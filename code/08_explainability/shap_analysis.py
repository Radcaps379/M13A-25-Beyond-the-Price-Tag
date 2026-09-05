"""
==============================================================================
PHASE 10 - EXPLAINABLE AI (SHAP)
Project: Beyond the Price Tag
==============================================================================

TWO JOBS, DELIBERATELY SEPARATED
--------------------------------
JOB 1  Model explainability
       Global : what drives model-implied valuation in general?
       Local  : why did the model value THIS player at this figure?

JOB 2  Recruitment decision support
       For each shortlisted player: positive drivers, negative drivers, and -
       critically - WHAT THE MODEL DOES NOT KNOW.

THE DISTINCTION THAT MATTERS
----------------------------
    PREDICTION EXPLANATION (SHAP)   : why did the model produce this valuation?
    DECISION EXPLANATION (optimizer): why did the system select this player?

These are different questions and the report must not conflate them. SHAP
explains a number. The optimizer explains a choice.

THE CAVEAT SHAP MUST CARRY
--------------------------
Phase 7 established that a large unexplained valuation gap does NOT imply an
exploitable opportunity - it is associated with elevated exit risk
p = 2.6e-11). So a SHAP explanation of a high model-implied value must never be
presented as proof that a player is undervalued. It explains the prediction; it
does not validate the business case.
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
STAGE_OUT = stage_dir("shap")


import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.preprocessing import StandardScaler

plt.rcParams.update({"figure.dpi": 130, "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25})

TRAIN_END = 2021

print("=" * 78)
print("PHASE 10 - SHAP EXPLAINABILITY")
print("=" * 78)

# =============================================================================
# REBUILD MODEL 1 EXACTLY AS FROZEN
# =============================================================================
mm = pd.read_csv(find("model_matrix.csv"))

M1 = ["age", "age2", "position", "league", "height_in_cm", "foot",
      "minutes", "games", "goals_per90", "assists_per90",
      "goal_contributions_per90", "cards_per90", "minutes_per_game", "availability",
      "prev_minutes", "delta_minutes", "prev_goals_per90", "delta_goals_per90",
      "prev_assists_per90", "delta_assists_per90",
      "prev_goal_contributions_per90", "delta_goal_contributions_per90",
      "roll3_mean_goal_contributions_per90", "roll3_std_goal_contributions_per90",
      "roll3_mean_minutes", "roll3_std_minutes",
      "seasons_observed", "has_prior_season", "has_3yr_history",
      "is_first_observed_season", "prior_gap_years", "young_and_improving",
      "club_squad_size"]
CAT = ["position", "league", "foot"]

train = mm[mm.season <= TRAIN_END].copy()
test = mm[mm.season > 2023].copy()

lv = train.groupby("season").log_market_value.median()
carry = float(lv.loc[TRAIN_END])
train["market_level"] = train.season.map(lv)
test["market_level"] = carry
train["y_adj"] = train.log_market_value - train.market_level


def prep(d):
    x = d[M1].copy()
    for c in CAT:
        x[c] = x[c].fillna("unknown").astype(str)
    return x


B = pd.get_dummies(prep(train), columns=CAT, drop_first=True)
FEATNAMES = list(B.columns)
Xtr = B.astype(float).fillna(0).values
Xte = (pd.get_dummies(prep(test), columns=CAT, drop_first=True)
       .reindex(columns=FEATNAMES, fill_value=0).astype(float).fillna(0).values)

sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

# ESTIMATOR IS FIXED, NOT DISCOVERED.
# An earlier version tried to import lightgbm and fell back to scikit-learn.
# That made the estimator depend on what happened to be installed: a machine
# with lightgbm produced different numbers from the ones in the report. Every
# result in this repository was produced by HistGradientBoosting, so the choice
# is now explicit and the repository reproduces the report on any machine.
from sklearn.ensemble import HistGradientBoostingRegressor
mdl = HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05,
                                    random_state=42)
mdl.fit(Xtr_s, train.y_adj.values)
print(f"Model 1 refitted: {len(train):,} train rows, {len(FEATNAMES)} encoded features")

# =============================================================================
# SHAP VALUES
# =============================================================================
import shap

print("\ncomputing SHAP values on the held-out 2024/25 season...")
explainer = shap.TreeExplainer(mdl)
sv = explainer.shap_values(Xte_s)
base_value = float(explainer.expected_value if np.isscalar(explainer.expected_value)
                   else explainer.expected_value[0])
print(f"   SHAP matrix {sv.shape}, base value {base_value:+.4f} (log units, deflated)")

# -----------------------------------------------------------------------------
# JOB 1a - GLOBAL: what drives model-implied valuation?
# -----------------------------------------------------------------------------
print("\n" + "-" * 78)
print("JOB 1a - GLOBAL EXPLANATION")
print("-" * 78)

glob = (pd.DataFrame({"feature": FEATNAMES,
                      "mean_abs_shap": np.abs(sv).mean(axis=0)})
        .sort_values("mean_abs_shap", ascending=False).reset_index(drop=True))
glob["share_pct"] = (100 * glob.mean_abs_shap / glob.mean_abs_shap.sum()).round(2)
glob.to_csv(STAGE_OUT / "shap_global_importance.csv", index=False)

print("Top 15 drivers of model-implied valuation:")
print(glob.head(15).to_string(index=False))

# group into the families used in the feature dictionary
def family(f):
    if f.startswith("league_"): return "league context"
    if f.startswith("position_"): return "position"
    if f.startswith("foot_"): return "foot"
    if f in ("age", "age2"): return "age"
    if f.startswith(("prev_", "delta_", "roll3_")) or f in (
            "seasons_observed", "has_prior_season", "has_3yr_history",
            "is_first_observed_season", "prior_gap_years", "young_and_improving"):
        return "performance trajectory"
    if f == "club_squad_size": return "club context"
    if f == "height_in_cm": return "physical"
    return "current-season performance"


glob["family"] = glob.feature.map(family)
fam = (glob.groupby("family").mean_abs_shap.sum()
       .sort_values(ascending=False).reset_index())
fam["share_pct"] = (100 * fam.mean_abs_shap / fam.mean_abs_shap.sum()).round(1)
fam.to_csv(STAGE_OUT / "shap_family_importance.csv", index=False)
print("\nBy feature family:")
print(fam.to_string(index=False))

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
top = glob.head(15).iloc[::-1]
ax[0].barh(range(len(top)), top.mean_abs_shap, color="#2b6cb0")
ax[0].set_yticks(range(len(top))); ax[0].set_yticklabels(top.feature, fontsize=8)
ax[0].set_xlabel("mean |SHAP| (log units)")
ax[0].set_title("Global drivers of model-implied valuation")
ax[1].barh(range(len(fam)), fam.mean_abs_shap.iloc[::-1], color="#c05621")
ax[1].set_yticks(range(len(fam))); ax[1].set_yticklabels(fam.family.iloc[::-1], fontsize=8)
ax[1].set_xlabel("summed mean |SHAP|"); ax[1].set_title("By feature family")
fig.tight_layout(); fig.savefig(FIG / "q12_shap_global.png", bbox_inches="tight")
plt.close(fig)

# beeswarm - direction as well as magnitude
try:
    fig = plt.figure(figsize=(9, 6))
    shap.summary_plot(sv, pd.DataFrame(Xte_s, columns=FEATNAMES),
                      max_display=15, show=False)
    plt.title("SHAP summary — direction and magnitude", fontsize=11)
    plt.tight_layout(); plt.savefig(FIG / "q13_shap_beeswarm.png", bbox_inches="tight")
    plt.close()
    print("\n   beeswarm written")
except Exception as e:
    print(f"   beeswarm skipped: {e}")

# =============================================================================
# JOB 1b + JOB 2 - LOCAL EXPLANATIONS FOR THE SHORTLIST
# =============================================================================
print("\n" + "-" * 78)
print("JOB 1b / JOB 2 - LOCAL EXPLANATIONS FOR RECOMMENDED PLAYERS")
print("-" * 78)

port = pd.read_csv(find("recommended_portfolio.csv"))
opt_in = pd.read_csv(find("optimizer_input_2024_25.csv"))

test = test.reset_index(drop=True)
test["pred_adj"] = mdl.predict(Xte_s)
test["pred_log"] = test.pred_adj + test.market_level
test["pred_eur"] = np.exp(test.pred_log)

sv_df = pd.DataFrame(sv, columns=FEATNAMES)

READABLE = {
    "age": "age", "age2": "age (non-linear effect)",
    "minutes": "league minutes played", "games": "appearances",
    "goals_per90": "goals per 90", "assists_per90": "assists per 90",
    "goal_contributions_per90": "goal contributions per 90",
    "cards_per90": "disciplinary record", "minutes_per_game": "minutes per appearance",
    "availability": "availability when selected",
    "prev_minutes": "minutes last season", "delta_minutes": "change in minutes",
    "prev_goals_per90": "goals per 90 last season",
    "delta_goals_per90": "change in goals per 90",
    "prev_assists_per90": "assists per 90 last season",
    "delta_assists_per90": "change in assists per 90",
    "prev_goal_contributions_per90": "contributions per 90 last season",
    "delta_goal_contributions_per90": "change in contributions per 90",
    "roll3_mean_goal_contributions_per90": "3-season average output",
    "roll3_std_goal_contributions_per90": "output consistency",
    "roll3_mean_minutes": "3-season average minutes",
    "roll3_std_minutes": "minutes consistency",
    "seasons_observed": "seasons of top-5 history",
    "has_prior_season": "prior-season history available",
    "has_3yr_history": "3+ seasons of history",
    "is_first_observed_season": "first observed season",
    "prior_gap_years": "gap since last observed season",
    "young_and_improving": "young and improving profile",
    "club_squad_size": "club squad size / rotation",
    "height_in_cm": "height",
}


def readable(f):
    if f in READABLE: return READABLE[f]
    if f.startswith("league_"): return f"plays in {f.replace('league_','')}"
    if f.startswith("position_"): return f"position: {f.replace('position_','')}"
    if f.startswith("foot_"): return f"preferred foot: {f.replace('foot_','')}"
    return f


explanations = []
for _, p in port.iterrows():
    m = test.player_id == p.player_id
    if not m.any():
        continue
    i = int(np.flatnonzero(m.values)[0])
    row = sv_df.iloc[i]
    oi = opt_in[opt_in.player_id == p.player_id].iloc[0]

    pos_d = row.sort_values(ascending=False).head(5)
    neg_d = row.sort_values().head(5)

    print(f"\n{'='*70}\n{p['name']}  ({p.position}, {p.league}, age {p.age:.1f})")
    print(f"  market value  EUR {p.market_value_eur/1e6:.1f}m")
    print(f"  model-implied EUR {test.loc[i,'pred_eur']/1e6:.1f}m")
    print(f"{'='*70}")
    print("  PREDICTION EXPLANATION (SHAP) - why the model produced this value")
    print("    raises the valuation:")
    for f, v in pos_d.items():
        if v > 0.001:
            print(f"      + {readable(f):<42} {v:+.3f}")
    print("    lowers the valuation:")
    for f, v in neg_d.items():
        if v < -0.001:
            print(f"      - {readable(f):<42} {v:+.3f}")

    print("\n  DECISION EXPLANATION (optimizer) - why the system selected him")
    print(f"      quality percentile      {100*p.quality:.0f}")
    print(f"      development potential   {p.potential:.2f}")
    print(f"      value efficiency        {p.value_efficiency:.2f}")
    print(f"      risk component          {p.risk:.2f}")

    print("\n  WHAT THE MODEL DOES NOT KNOW")
    print(f"      exit probability (validated model)  {100*oi.exit_prob:.0f}%")
    print("      no contract length, injury history, scouting assessment or")
    print("      off-field information is available to this model. Phase 7 found")
    print("      that unexplained valuation gaps predict EXIT, not appreciation.")

    explanations.append({
        "player_id": p.player_id, "name": p["name"], "position": p.position,
        "league": p.league, "age": round(p.age, 1),
        "market_value_eur": p.market_value_eur,
        "model_implied_eur": round(float(test.loc[i, "pred_eur"]), 0),
        "top_positive_drivers": "; ".join(
            f"{readable(f)} ({v:+.3f})" for f, v in pos_d.items() if v > 0.001),
        "top_negative_drivers": "; ".join(
            f"{readable(f)} ({v:+.3f})" for f, v in neg_d.items() if v < -0.001),
        "quality_pctl": round(100 * p.quality, 0),
        "potential": round(p.potential, 3),
        "value_efficiency": round(p.value_efficiency, 3),
        "risk_component": round(p.risk, 3),
        "exit_probability": round(float(oi.exit_prob), 4),
    })

pd.DataFrame(explanations).to_csv(STAGE_OUT / "shap_shortlist_explanations.csv", index=False)

# waterfall figures for the portfolio
for _, p in port.iterrows():
    m = test.player_id == p.player_id
    if not m.any():
        continue
    i = int(np.flatnonzero(m.values)[0])
    try:
        fig = plt.figure(figsize=(8, 5))
        shap.plots._waterfall.waterfall_legacy(
            base_value, sv[i], feature_names=[readable(f) for f in FEATNAMES],
            max_display=12, show=False)
        plt.title(f"{p['name']} — why the model implies "
                  f"€{test.loc[i,'pred_eur']/1e6:.1f}m", fontsize=10)
        plt.tight_layout()
        fname = p["name"].lower().replace(" ", "_").replace("'", "")
        plt.savefig(FIG / f"q14_shap_{fname}.png", bbox_inches="tight")
        plt.close()
    except Exception as e:
        print(f"   waterfall skipped for {p['name']}: {e}")

# =============================================================================
# FAIRNESS / BIAS AUDIT - required for the ethics section
# =============================================================================
print("\n" + "-" * 78)
print("BIAS AUDIT - does the model systematically discount by group?")
print("-" * 78)

test["resid"] = test.log_market_value - test.pred_log
bias = []
for dim in ["position", "league"]:
    for k, g in test.groupby(dim):
        bias.append({"dimension": dim, "segment": str(k), "n": len(g),
                     "mean_residual": round(float(g.resid.mean()), 4),
                     "interpretation": "model UNDER-values group" if g.resid.mean() > 0.05
                     else ("model OVER-values group" if g.resid.mean() < -0.05
                           else "no material systematic bias")})
test["age_band"] = pd.cut(test.age, [15, 21, 24, 27, 30, 46],
                          labels=["<=21", "22-24", "25-27", "28-30", "31+"])
for k, g in test.groupby("age_band", observed=True):
    bias.append({"dimension": "age_band", "segment": str(k), "n": len(g),
                 "mean_residual": round(float(g.resid.mean()), 4),
                 "interpretation": "model UNDER-values group" if g.resid.mean() > 0.05
                 else ("model OVER-values group" if g.resid.mean() < -0.05
                       else "no material systematic bias")})
biasdf = pd.DataFrame(bias)
print(biasdf.to_string(index=False))
biasdf.to_csv(STAGE_OUT / "shap_bias_audit.csv", index=False)

print("\n" + "=" * 78)
print("PHASE 10 COMPLETE")
print("=" * 78)
