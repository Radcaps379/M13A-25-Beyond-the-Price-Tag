"""
==============================================================================
PHASE 9 - RISK-AWARE RECRUITMENT PORTFOLIO OPTIMIZER
Project: Beyond the Price Tag
==============================================================================
Implements optimizer_specification.md exactly. Read that document first - every
weight and constraint here is declared there, with justification, before this
script was written.

  Objective : maximise  w1*Quality + w2*Potential + w3*ValueEfficiency
                        - w4*Risk
  Subject to: budget, positional needs, performance floor, exit-risk ceiling,
              age ceiling, minimum value, uncertainty ceiling, binary selection

WHY NOT "MAXIMISE THE VALUATION GAP"
------------------------------------
Phase 7 tested that objective and rejected it: no subsequent relative
appreciation (p = 0.307) and 3.7x the benchmark exit rate (OR 4.82). Optimising the gap would
optimise an unvalidated quantity and load the portfolio with risk.
==============================================================================
"""

# --- repository paths -------------------------------------------------------
# Resolved from this file's location so the script runs from a clean clone,
# from any working directory. See code/repo_paths.py.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from repo_paths import ROOT, RAW, PROC, OUTPUTS, FIGURES, BRIEFS, find, stage_dir, ensure_dirs
ensure_dirs()
FIG = FIGURES
STAGE_OUT = stage_dir("optimizer")


import pandas as pd
import numpy as np
from pathlib import Path
import itertools


# =============================================================================
# DECLARED PARAMETERS (from optimizer_specification.md - not fitted)
# =============================================================================
W_QUALITY, W_POTENTIAL, W_VALUE, W_RISK = 0.35, 0.25, 0.20, 0.20

BUDGET_EUR = 50e6
POSITION_NEEDS = {"Defender": 1, "Midfield": 1, "Attack": 1}
MIN_QUALITY_PCTL = 0.40
MAX_EXIT_RISK = 0.40
MAX_AGE = 27
MIN_VALUE_EUR = 1e6
MAX_UNCERTAINTY_Q = 0.80

print("=" * 78)
print("PHASE 9 - RISK-AWARE RECRUITMENT OPTIMIZER")
print("=" * 78)
print(f"weights   quality {W_QUALITY} | potential {W_POTENTIAL} | "
      f"value {W_VALUE} | risk -{W_RISK}")
print(f"budget    EUR {BUDGET_EUR/1e6:.0f}m")
print(f"needs     {POSITION_NEEDS}")

df = pd.read_csv(find("optimizer_input_2024_25.csv"))
print(f"exit model: LOGISTIC (production) | uncertainty + value cap: pre-test only")
print(f"\nplayer pool: {len(df):,} (2024/25, each with validated exit probability)")

# Pre-test calibration constants, fitted on seasons <= 2023 in Phase 8.
# Loaded here so that every transformation below uses them.
seg_unc = pd.read_csv(find("pretest_segment_uncertainty.csv"))[
    ["position", "league", "seg_unc"]]
consts = pd.read_csv(find("pretest_constants.csv"), index_col=0)["value"]
print(f"pre-test constants loaded: value cap {float(consts['value_efficiency_cap_p90']):.3f}, "
      f"global uncertainty {float(consts['global_uncertainty']):.3f}")

# =============================================================================
# COMPONENT CONSTRUCTION - all normalised WITHIN position
# =============================================================================
print("\nBuilding score components (normalised within position)")


def pct_within(s, by):
    return s.groupby(by).rank(pct=True)


# --- QUALITY: position-appropriate, because Phase 4 showed goal contributions
#     mean almost nothing for goalkeepers (r=0.07) but a lot for attackers (0.54)
df["quality_raw"] = np.where(
    df.position.isin(["Attack", "Midfield"]),
    df.goal_contributions_per90,
    df.minutes / df.minutes.max(),        # availability proxy for DEF/GK
)
df["quality"] = pct_within(df.quality_raw, df.position)

# --- POTENTIAL: remaining development / resale runway.
# Declines linearly to zero at age 30 (a three-year horizon beyond the hard
# recruitment ceiling of 27). The ceiling and the runway are deliberately
# different: the club will not SIGN a player over 27, but a 26-year-old still
# carries some resale runway and should not score zero.
POTENTIAL_ZERO_AGE = 30
df["potential"] = np.clip((POTENTIAL_ZERO_AGE - df.age) /
                          (POTENTIAL_ZERO_AGE - 17), 0, 1)

# --- VALUE EFFICIENCY: capped, because Phase 7 showed extreme ratios are model
#     error rather than opportunity
# cap fitted on training+validation seasons, never on the 2024/25 pool
cap = float(consts["value_efficiency_cap_p90"])
df["value_eff_raw"] = df.mispricing_ratio.clip(upper=cap)
df["value_efficiency"] = pct_within(df.value_eff_raw, df.position)

# --- RISK: validated exit probability + segment uncertainty
# Segment uncertainty is READ IN from pretest_segment_uncertainty.csv, which was
# fitted on training+validation seasons only. It is NOT recomputed here: doing so
# from the 2024/25 sample would require the realized 2024/25 valuations, which a
# club cannot observe at the decision point.
df = df.merge(seg_unc, on=["position", "league"], how="left")
df["seg_unc"] = df.seg_unc.fillna(float(consts["global_uncertainty"]))
df["uncertainty"] = df.seg_unc.rank(pct=True)
df["risk"] = 0.7 * df.exit_prob + 0.3 * df.uncertainty

df["score"] = (W_QUALITY * df.quality + W_POTENTIAL * df.potential
               + W_VALUE * df.value_efficiency - W_RISK * df.risk)

# =============================================================================
# ELIGIBILITY
# =============================================================================
unc_cut = df.uncertainty.quantile(MAX_UNCERTAINTY_Q)
df["eligible"] = (
    (df.age <= MAX_AGE) &
    (df.market_value_eur >= MIN_VALUE_EUR) &
    (df.quality >= MIN_QUALITY_PCTL) &
    (df.exit_prob <= MAX_EXIT_RISK) &
    (df.uncertainty <= unc_cut) &
    (df.position.isin(POSITION_NEEDS))
)
elig = df[df.eligible].copy()
print(f"eligible after all constraints: {len(elig):,}")
print(elig.groupby("position").size().to_string())

# =============================================================================
# SOLVE - ILP via PuLP. The greedy heuristic is a COMPARISON, not a fallback.
# =============================================================================
# THE OFFICIAL SOLUTION IS THE INTEGER PROGRAM, NOT THE HEURISTIC.
# An earlier version returned None when PuLP was absent, so the script silently
# fell back to the greedy heuristic and produced a DIFFERENT portfolio without
# saying so. A missing dependency must fail loudly, never change the answer.
try:
    import pulp
except ImportError:
    raise SystemExit(
        "\nPuLP is required for the official ILP solution.\n"
        "Without it this script would fall back to a greedy heuristic and\n"
        "produce a different portfolio from the one reported.\n\n"
        "Install the declared dependencies:\n"
        "    pip install -r requirements.txt\n")


def solve_ilp(pool, budget, needs):
    prob = pulp.LpProblem("recruitment", pulp.LpMaximize)
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in pool.index}
    prob += pulp.lpSum(pool.loc[i, "score"] * x[i] for i in pool.index)
    prob += pulp.lpSum(pool.loc[i, "market_value_eur"] * x[i]
                       for i in pool.index) <= budget
    for pos, n in needs.items():
        idx = pool.index[pool.position == pos]
        prob += pulp.lpSum(x[i] for i in idx) == n
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[prob.status] != "Optimal":
        return None
    chosen = [i for i in pool.index if x[i].value() and x[i].value() > 0.5]
    return pool.loc[chosen]


def solve_greedy(pool, budget, needs):
    """
    Greedy heuristic: best score per position, then fill the remaining budget.

    Computed alongside the ILP so the value added by exact optimisation is
    visible rather than assumed. It is NEVER substituted for the ILP. If PuLP is
    unavailable the script exits at import time, because a missing solver must
    not silently change the recommended portfolio.
    """
    picks, spend = [], 0.0
    for pos, n in needs.items():
        sub = pool[pool.position == pos].sort_values("score", ascending=False)
        for _, r in sub.iterrows():
            if len([p for p in picks if p.position == pos]) >= n:
                break
            if spend + r.market_value_eur <= budget:
                picks.append(r); spend += r.market_value_eur
    return pd.DataFrame(picks)


ilp = solve_ilp(elig, BUDGET_EUR, POSITION_NEEDS)
greedy = solve_greedy(elig, BUDGET_EUR, POSITION_NEEDS)

# A missing solver already fails at import. This covers the other route to a
# different answer: PuLP present but the solve returning non-optimal, which
# previously fell through to the greedy heuristic without saying so.
if ilp is None:
    raise SystemExit(
        "\nThe ILP did not return an optimal solution.\n"
        "The greedy heuristic is a comparison only and is never substituted\n"
        "for the official portfolio. Investigate the solver before proceeding.\n")
port = ilp
method = "ILP (PuLP)"
print(f"\nsolved with: {method}")
if ilp is not None:
    print(f"greedy total score {greedy.score.sum():.4f} vs "
          f"ILP {ilp.score.sum():.4f}  "
          f"({'ILP better' if ilp.score.sum() > greedy.score.sum() + 1e-9 else 'identical - greedy suffices'})")


def show(p, title):
    print(f"\n{'-'*78}\n{title}\n{'-'*78}")
    v = p.copy()
    v["market_€m"] = (v.market_value_eur / 1e6).round(1)
    v["model_€m"] = (v.pred_eur / 1e6).round(1)
    v["gap_%"] = (100 * (v.pred_eur / v.market_value_eur - 1)).round(0)
    v["quality_pctl"] = (100 * v.quality).round(0)
    v["exit_risk_%"] = (100 * v.exit_prob).round(0)
    v["age"] = v.age.round(1)
    print(v[["name", "position", "league", "age", "market_€m", "model_€m",
             "gap_%", "quality_pctl", "exit_risk_%"]].to_string(index=False))
    print(f"\n   spend EUR {p.market_value_eur.sum()/1e6:.1f}m of "
          f"{BUDGET_EUR/1e6:.0f}m   remaining EUR "
          f"{(BUDGET_EUR-p.market_value_eur.sum())/1e6:.1f}m")
    print(f"   mean exit risk {100*p.exit_prob.mean():.1f}%   "
          f"mean quality percentile {100*p.quality.mean():.0f}")


show(port, "RECOMMENDED PORTFOLIO (risk-aware)")

# =============================================================================
# BASELINE COMPARISONS - does the complexity earn its place?
# =============================================================================
print("\n" + "=" * 78)
print("BASELINE COMPARISON")
print("=" * 78)

pool_all = df[df.position.isin(POSITION_NEEDS) & (df.market_value_eur >= MIN_VALUE_EUR)]

# Baseline A: largest valuation gap (the REJECTED Phase 7 objective)
gap_pick = []
for pos, n in POSITION_NEEDS.items():
    s = pool_all[pool_all.position == pos].nlargest(n, "mispricing_ratio")
    gap_pick.append(s)
gapp = pd.concat(gap_pick)

# Baseline B: cheapest players meeting positional needs
cheap_pick = []
for pos, n in POSITION_NEEDS.items():
    s = pool_all[pool_all.position == pos].nsmallest(n, "market_value_eur")
    cheap_pick.append(s)
cheapp = pd.concat(cheap_pick)

comp = pd.DataFrame([
    {"portfolio": "Risk-aware (recommended)", "n": len(port),
     "spend_eur_m": round(port.market_value_eur.sum() / 1e6, 1),
     "mean_exit_risk_pct": round(100 * port.exit_prob.mean(), 1),
     "mean_quality_pctl": round(100 * port.quality.mean(), 0),
     "mean_age": round(port.age.mean(), 1),
     "actually_exited_pct": round(100 * port.exit.mean(), 1)},
    {"portfolio": "Largest valuation gap (rejected objective)", "n": len(gapp),
     "spend_eur_m": round(gapp.market_value_eur.sum() / 1e6, 1),
     "mean_exit_risk_pct": round(100 * gapp.exit_prob.mean(), 1),
     "mean_quality_pctl": round(100 * gapp.quality.mean(), 0),
     "mean_age": round(gapp.age.mean(), 1),
     "actually_exited_pct": round(100 * gapp.exit.mean(), 1)},
    {"portfolio": "Cheapest meeting needs", "n": len(cheapp),
     "spend_eur_m": round(cheapp.market_value_eur.sum() / 1e6, 1),
     "mean_exit_risk_pct": round(100 * cheapp.exit_prob.mean(), 1),
     "mean_quality_pctl": round(100 * cheapp.quality.mean(), 0),
     "mean_age": round(cheapp.age.mean(), 1),
     "actually_exited_pct": round(100 * cheapp.exit.mean(), 1)},
])
print(comp.to_string(index=False))
print("\n   'actually_exited_pct' is the REALISED 2025/26 outcome. It is shown")
print("   for evaluation only and was not available to the optimizer.")
comp.to_csv(STAGE_OUT / "optimizer_baseline_comparison.csv", index=False)

# =============================================================================
# SENSITIVITY - is the shortlist stable, or an artefact of the weights?
# =============================================================================
print("\n" + "=" * 78)
print("SENSITIVITY ANALYSIS")
print("=" * 78)

sens, appear = [], {}
grid = [(0.35, 0.25, 0.20, 0.20), (0.50, 0.20, 0.15, 0.15),
        (0.25, 0.35, 0.20, 0.20), (0.30, 0.20, 0.35, 0.15),
        (0.30, 0.20, 0.15, 0.35), (0.25, 0.25, 0.25, 0.25)]
for (a, b, c, dd) in grid:
    tmp = elig.copy()
    tmp["score"] = a * tmp.quality + b * tmp.potential + c * tmp.value_efficiency - dd * tmp.risk
    p = solve_ilp(tmp, BUDGET_EUR, POSITION_NEEDS)
    if p is None:
        raise SystemExit("ILP non-optimal during sensitivity analysis; refusing to substitute greedy.")
    for nm in p.name:
        appear[nm] = appear.get(nm, 0) + 1
    sens.append({"w_quality": a, "w_potential": b, "w_value": c, "w_risk": dd,
                 "players": ", ".join(p.name.tolist()),
                 "spend_eur_m": round(p.market_value_eur.sum() / 1e6, 1)})
sensdf = pd.DataFrame(sens)
print(sensdf.to_string(index=False))

stab = pd.Series(appear).sort_values(ascending=False)
print(f"\nSelection stability across {len(grid)} weightings:")
print(stab.head(10).to_string())
core = (stab >= len(grid) * 0.5).sum()
print(f"\n   {core} players appear in >=50% of weightings -> the core "
      f"recommendation is {'STABLE' if core >= 2 else 'UNSTABLE - report as such'}")

sensdf.to_csv(STAGE_OUT / "optimizer_sensitivity.csv", index=False)

# budget sensitivity
budg = []
for B in [20e6, 35e6, 50e6, 75e6, 100e6]:
    p = solve_ilp(elig, B, POSITION_NEEDS)
    if p is None:
        raise SystemExit("ILP non-optimal during sensitivity analysis; refusing to substitute greedy.")
    budg.append({"budget_eur_m": B / 1e6, "spend_eur_m": round(p.market_value_eur.sum() / 1e6, 1),
                 "mean_quality_pctl": round(100 * p.quality.mean(), 0),
                 "mean_exit_risk_pct": round(100 * p.exit_prob.mean(), 1),
                 "players": ", ".join(p.name.tolist())})
budgdf = pd.DataFrame(budg)
print("\nBudget sensitivity:")
print(budgdf.to_string(index=False))
budgdf.to_csv(STAGE_OUT / "optimizer_budget_sensitivity.csv", index=False)

# =============================================================================
# SAVE
# =============================================================================
outcols = ["player_id", "name", "position", "league", "club_name", "age",
           "minutes", "goal_contributions_per90", "market_value_eur", "pred_eur",
           "mispricing_ratio", "quality", "potential", "value_efficiency",
           "exit_prob", "uncertainty", "risk", "score"]
port[outcols].to_csv(STAGE_OUT / "recommended_portfolio.csv", index=False)
elig.sort_values("score", ascending=False).head(50)[outcols].to_csv(STAGE_OUT / "recruitment_shortlist_top50.csv", index=False)

print("\n" + "=" * 78)
print("PHASE 9 COMPLETE")
print("=" * 78)
