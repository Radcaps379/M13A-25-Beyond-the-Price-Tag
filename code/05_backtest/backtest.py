"""
==============================================================================
PHASE 7 - MISPRICING SIGNAL AND BACK-TEST
Project: Beyond the Price Tag
==============================================================================

THE QUESTION THIS ANSWERS
-------------------------
Not "did the model predict market value accurately?" (Phase 6 answered that)
but:

    When the model said a player was undervalued using ONLY information
    available at the end of 2024/25, did that player subsequently show
    evidence of value in 2025/26?

SEQUENCING DISCIPLINE (this is the whole point)
-----------------------------------------------
  1. Declare the selection criterion IN WRITING before computing anything.
  2. Choose the undervaluation threshold using VALIDATION seasons only
     (flag in 2022/23 -> outcome in 2023/24). Test-period data is untouched.
  3. Apply the chosen threshold ONCE to 2024/25. Freeze the candidate list.
  4. Only then look at 2025/26 outcomes.

Step 2 never sees 2024/25 or 2025/26. Step 4 happens after the list is frozen.
This prevents unconsciously tuning "undervalued" to whatever produces the
prettiest back-test.

WHAT WE MEASURE
---------------
  A. Market-value outcome  - relative appreciation vs a position x league peer
                             benchmark (controls for market-wide inflation)
  B. Performance outcome   - position-appropriate metrics, since the EDA showed
                             goal contributions are meaningless for goalkeepers

WHAT WE WILL NOT CLAIM
----------------------
No realized financial return. No causality. The finding is an association:
flagged players subsequently experienced higher relative appreciation than a
matched benchmark.
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
STAGE_OUT = stage_dir("backtest")


import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

plt.rcParams.update({"figure.dpi": 130, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25})

TRAIN_END, VAL_END = 2021, 2023
INFO_CUTOFF = pd.Timestamp("2026-08-26")
TOP5 = ["GB1", "ES1", "L1", "IT1", "FR1"]
MIN_MINUTES = 900

# =============================================================================
# PRE-DECLARED SELECTION CRITERION  (written before any number is computed)
# =============================================================================
CRITERION = """
PRE-DECLARED THRESHOLD SELECTION CRITERION
------------------------------------------
Candidate thresholds  : bottom 10%, 15%, 20% of the Model 1 mispricing residual
Selection rule        : choose the threshold with the LARGEST median relative
                        market-value appreciation differential versus the
                        position x league peer benchmark, measured in the
                        VALIDATION window (flag 2022/23 -> outcome 2023/24),
                        subject to a minimum of 50 candidates for usability.
Tie-break             : prefer the LARGER threshold (more candidates, more
                        robust to noise).
Data visible at this step : validation seasons only. 2024/25 and 2025/26 are
                        not read until the threshold is fixed.
"""
print("=" * 78)
print("PHASE 7 - MISPRICING SIGNAL AND BACK-TEST")
print("=" * 78)
print(CRITERION)

# =============================================================================
# REBUILD THE FROZEN MODEL 1 (identical spec to Phase 6)
# =============================================================================
mm = pd.read_csv(find("model_matrix.csv"))

M1 = ["age", "age2", "position", "league",
      "height_in_cm", "foot",
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
later = mm[mm.season > TRAIN_END].copy()

train_levels = train.groupby("season")["log_market_value"].median()
carry_level = float(train_levels.loc[TRAIN_END])
train["market_level"] = train["season"].map(train_levels)
later["market_level"] = carry_level
train["y_adj"] = train.log_market_value - train.market_level
later["y_adj"] = later.log_market_value - later.market_level


def design(fit_df, *others):
    def prep(d):
        x = d[M1].copy()
        for c in CAT:
            x[c] = x[c].fillna("unknown").astype(str)
        return x
    B = pd.get_dummies(prep(fit_df), columns=CAT, drop_first=True)
    out = [B]
    for o in others:
        D = pd.get_dummies(prep(o), columns=CAT, drop_first=True)
        out.append(D.reindex(columns=B.columns, fill_value=0))
    return [x.astype(float).fillna(0).values for x in out]


Xtr, Xla = design(train, later)
sc = StandardScaler().fit(Xtr)
# ESTIMATOR IS FIXED, NOT DISCOVERED.
# An earlier version tried to import lightgbm and fell back to scikit-learn.
# That made the estimator depend on what happened to be installed: a machine
# with lightgbm produced different numbers from the ones in the report. Every
# result in this repository was produced by HistGradientBoosting, so the choice
# is now explicit and the repository reproduces the report on any machine.
from sklearn.ensemble import HistGradientBoostingRegressor
mdl = HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05,
                                    random_state=42)
mdl.fit(sc.transform(Xtr), train.y_adj.values)

later["pred_adj"] = mdl.predict(sc.transform(Xla))
later["pred_log"] = later.pred_adj + later.market_level
later["pred_eur"] = np.exp(later.pred_log)

# MISPRICING RESIDUAL: observed minus model-implied, in log space.
# Negative => market values the player BELOW what fundamentals imply => undervalued.
later["residual"] = later.log_market_value - later.pred_log
later["mispricing_ratio"] = later.pred_eur / later.market_value_eur

print(f"Model 1 refitted on {len(train):,} training rows; scored "
      f"{len(later):,} rows in {sorted(later.season.unique())}")

# =============================================================================
# OUTCOME DATA: subsequent-season valuations and performance
# =============================================================================
print("\nBuilding subsequent-season outcomes (valuation + performance)")

val_raw = pd.read_csv(RAW / "player_valuations.csv", low_memory=False)
val_raw["date"] = pd.to_datetime(val_raw["date"], errors="coerce")
val_raw = val_raw[val_raw.date <= INFO_CUTOFF][
    ["player_id", "date", "market_value_in_eur"]].dropna().sort_values("date")

app = pd.read_csv(RAW / "appearances.csv", low_memory=False)
app["date"] = pd.to_datetime(app["date"], errors="coerce")
app = app[(app.date <= INFO_CUTOFF) & (app.competition_id.isin(TOP5))]
app["season"] = np.where(app.date.dt.month >= 7, app.date.dt.year, app.date.dt.year - 1)

perf_next = (app.groupby(["player_id", "season"])
             .agg(next_minutes=("minutes_played", "sum"),
                  next_games=("game_id", "nunique"),
                  next_goals=("goals", "sum"),
                  next_assists=("assists", "sum"),
                  next_last_match=("date", "max"))
             .reset_index())
perf_next["next_gc90"] = ((perf_next.next_goals + perf_next.next_assists) /
                          (perf_next.next_minutes / 90.0))


def attach_outcomes(df, flag_season):
    """Attach season t+1 valuation and performance for players flagged in t."""
    d = df[df.season == flag_season].copy()
    nxt = perf_next[perf_next.season == flag_season + 1].drop(columns="season")
    d = d.merge(nxt, on="player_id", how="left")

    # subsequent valuation: first recorded after the t+1 season's last match
    anchor = perf_next.loc[perf_next.season == flag_season + 1, "next_last_match"].max()
    d["outcome_anchor"] = d["next_last_match"].fillna(anchor)
    a = d[["player_id", "outcome_anchor"]].sort_values("outcome_anchor")
    m = pd.merge_asof(a, val_raw.rename(columns={"date": "next_val_date",
                                                 "market_value_in_eur": "next_value_eur"}),
                      left_on="outcome_anchor", right_on="next_val_date",
                      by="player_id", direction="forward",
                      tolerance=pd.Timedelta(days=240))
    d = d.merge(m[["player_id", "next_value_eur"]], on="player_id", how="left")
    d["d_log_value"] = np.log(d.next_value_eur) - np.log(d.market_value_eur)
    return d


def add_peer_benchmark(d):
    """
    Peer benchmark = median subsequent appreciation among players in the same
    position x league. Controls for market-wide inflation and for the fact that
    a Ligue 1 midfielder and a Premier League forward are not comparable.
    """
    peer = (d[d.d_log_value.notna()]
            .groupby(["position", "league"])["d_log_value"]
            .median().rename("peer_d_log_value").reset_index())
    d = d.merge(peer, on=["position", "league"], how="left")
    d["rel_appreciation"] = d.d_log_value - d.peer_d_log_value
    return d


# =============================================================================
# STEP 2 - THRESHOLD SELECTION ON VALIDATION ONLY (flag 2022/23 -> outcome 2023/24)
# =============================================================================
print("\n" + "=" * 78)
print("STEP 2: THRESHOLD SELECTION - VALIDATION WINDOW ONLY")
print("        flag season 2022/23  ->  outcome season 2023/24")
print("        (2024/25 and 2025/26 are NOT read in this step)")
print("=" * 78)

v = attach_outcomes(later, 2022)
v = add_peer_benchmark(v)
print(f"validation flag pool: {len(v):,} players with a 2022/23 valuation; "
      f"{v.d_log_value.notna().sum():,} have a 2023/24 outcome")

rows = []
for pct in [10, 15, 20]:
    cut = np.percentile(v.residual.dropna(), pct)
    flagged = v[v.residual <= cut]
    bench = v[v.residual > cut]
    f_med = flagged.rel_appreciation.median()
    b_med = bench.rel_appreciation.median()
    rows.append({"threshold": f"bottom {pct}%",
                 "residual_cut": round(cut, 4),
                 "n_candidates": len(flagged),
                 "median_rel_appreciation_flagged": round(f_med, 4),
                 "median_rel_appreciation_benchmark": round(b_med, 4),
                 "differential": round(f_med - b_med, 4),
                 "meets_min_50": len(flagged) >= 50})
thr = pd.DataFrame(rows)
print("\n" + thr.to_string(index=False))

elig = thr[thr.meets_min_50]
best = elig.differential.max()
chosen = elig[elig.differential == best].iloc[-1]      # tie-break: larger threshold
CHOSEN_PCT = int(chosen.threshold.split()[1].strip("%"))
thr["selected"] = thr.threshold == chosen.threshold
thr.to_csv(STAGE_OUT / "backtest_threshold_selection.csv", index=False)
v.to_csv(STAGE_OUT / "backtest_validation_frame.csv", index=False)   # reused by 7b

print(f"\n>>> SELECTED (validation only): {chosen.threshold} "
      f"(differential {chosen.differential:+.4f})")
print(">>> This threshold is now FROZEN and applied once to 2024/25.")

# =============================================================================
# STEP 3 - APPLY ONCE TO 2024/25, FREEZE THE CANDIDATE LIST
# =============================================================================
print("\n" + "=" * 78)
print(f"STEP 3: APPLYING bottom {CHOSEN_PCT}% TO 2024/25 - LIST FROZEN")
print("=" * 78)

t = attach_outcomes(later, 2024)

# Uncertainty screen: segment-level typical error, measured on VALIDATION only.
seg_err = (v.assign(abs_err=(v.residual).abs())
           .groupby(["position", "league"])["abs_err"].median()
           .rename("segment_uncertainty").reset_index())
t = t.merge(seg_err, on=["position", "league"], how="left")
t["segment_uncertainty"] = t.segment_uncertainty.fillna(t.segment_uncertainty.median())

cut_2024 = np.percentile(t.residual.dropna(), CHOSEN_PCT)
t["flag_undervalued"] = t.residual <= cut_2024

cand = t[t.flag_undervalued].copy()
print(f"candidates flagged in 2024/25: {len(cand):,} of {len(t):,}")

cand_out = cand[["player_id", "name", "position", "league", "club_name", "age",
                 "minutes", "goal_contributions_per90",
                 "market_value_eur", "pred_eur", "mispricing_ratio",
                 "residual", "segment_uncertainty"]].sort_values("residual")
cand_out.to_csv(STAGE_OUT / "candidates_2024_25.csv", index=False)

print("\nTop 15 candidates by mispricing signal:")
show = cand_out.head(15).copy()
show["market_value_eur"] = (show.market_value_eur / 1e6).round(1)
show["pred_eur"] = (show.pred_eur / 1e6).round(1)
show["mispricing_ratio"] = show.mispricing_ratio.round(2)
show["age"] = show.age.round(1)
print(show[["name", "position", "league", "age", "market_value_eur",
            "pred_eur", "mispricing_ratio"]].to_string(index=False))

# =============================================================================
# STEP 4 - BACK-TEST ON 2025/26  (first look at outcomes)
# =============================================================================
print("\n" + "=" * 78)
print("STEP 4: BACK-TEST - 2025/26 OUTCOMES (candidate list already frozen)")
print("=" * 78)

t = add_peer_benchmark(t)

# --- auditability: account for every flagged candidate ----------------------
audit = {
    "flagged_candidates": int(t.flag_undervalued.sum()),
    "value_outcome_available": int(t[t.flag_undervalued].d_log_value.notna().sum()),
    "value_outcome_unavailable": int(t[t.flag_undervalued].d_log_value.isna().sum()),
    "performance_outcome_available_ge900min": int(
        (t[t.flag_undervalued].next_minutes >= MIN_MINUTES).sum()),
    "played_but_under_900min": int(
        ((t[t.flag_undervalued].next_minutes > 0) &
         (t[t.flag_undervalued].next_minutes < MIN_MINUTES)).sum()),
    "no_top5_minutes_2025_26": int(t[t.flag_undervalued].next_minutes.isna().sum()),
}
print("\nCandidate accounting (no silent drops):")
for k, val_ in audit.items():
    print(f"   {k:<40} {val_:>6}")
pd.Series(audit).to_frame("count").to_csv(STAGE_OUT / "backtest_audit.csv")

# --- OUTCOME A: relative market-value appreciation ---------------------------
fl = t[t.flag_undervalued & t.rel_appreciation.notna()]
bm = t[~t.flag_undervalued & t.rel_appreciation.notna()]


def boot_ci(x, n=5000, seed=42):
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    s = rng.choice(x, (n, len(x)), replace=True)
    m = np.median(s, axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


lo_f, hi_f = boot_ci(fl.rel_appreciation)
lo_b, hi_b = boot_ci(bm.rel_appreciation)

from scipy.stats import mannwhitneyu
u, pval = mannwhitneyu(fl.rel_appreciation, bm.rel_appreciation, alternative="greater")

resA = pd.DataFrame([
    {"group": "Flagged undervalued", "n": len(fl),
     "median_rel_appreciation": round(fl.rel_appreciation.median(), 4),
     "ci95_low": round(lo_f, 4), "ci95_high": round(hi_f, 4),
     "pct_positive_relative": round(100 * (fl.rel_appreciation > 0).mean(), 1)},
    {"group": "Benchmark (not flagged)", "n": len(bm),
     "median_rel_appreciation": round(bm.rel_appreciation.median(), 4),
     "ci95_low": round(lo_b, 4), "ci95_high": round(hi_b, 4),
     "pct_positive_relative": round(100 * (bm.rel_appreciation > 0).mean(), 1)},
])
resA.loc[len(resA)] = {
    "group": "Difference", "n": np.nan,
    "median_rel_appreciation": round(fl.rel_appreciation.median() -
                                     bm.rel_appreciation.median(), 4),
    "ci95_low": np.nan, "ci95_high": np.nan,
    "pct_positive_relative": round(100 * (fl.rel_appreciation > 0).mean() -
                                   100 * (bm.rel_appreciation > 0).mean(), 1)}

print("\n--- OUTCOME A: relative market-value appreciation (vs position x league peers) ---")
print(resA.to_string(index=False))
print(f"\nMann-Whitney U (one-sided, flagged > benchmark): p = {pval:.4g}")
print(f"Median ratio in value terms: flagged {np.exp(fl.rel_appreciation.median()):.3f}x "
      f"vs benchmark {np.exp(bm.rel_appreciation.median()):.3f}x relative to peers")

# --- OUTCOME B: position-appropriate performance -----------------------------
print("\n--- OUTCOME B: performance change, position-appropriate metrics ---")
print("    (goal contributions are meaningless for goalkeepers, so keepers and")
print("     defenders are assessed on availability/minutes instead)")

pb = t[t.next_minutes >= MIN_MINUTES].copy()
pb["d_gc90"] = pb.next_gc90 - pb.goal_contributions_per90
pb["d_minutes"] = pb.next_minutes - pb.minutes

perf_rows = []
for pos, metric, label in [("Attack", "d_gc90", "goal contributions/90"),
                           ("Midfield", "d_gc90", "goal contributions/90"),
                           ("Defender", "d_minutes", "minutes (availability)"),
                           ("Goalkeeper", "d_minutes", "minutes (availability)")]:
    sub = pb[pb.position == pos]
    f = sub[sub.flag_undervalued][metric].dropna()
    b = sub[~sub.flag_undervalued][metric].dropna()
    if len(f) >= 5:
        perf_rows.append({"position": pos, "metric": label,
                          "n_flagged": len(f), "n_benchmark": len(b),
                          "median_flagged": round(float(f.median()), 3),
                          "median_benchmark": round(float(b.median()), 3),
                          "difference": round(float(f.median() - b.median()), 3)})
perfdf = pd.DataFrame(perf_rows)
print(perfdf.to_string(index=False))

# =============================================================================
# PORTFOLIO-LEVEL VIEW
# =============================================================================
print("\n--- PORTFOLIO VIEW: the 2024/25 undervalued portfolio ---")
port = {
    "candidates": len(fl),
    "combined_market_value_eur_m": round(fl.market_value_eur.sum() / 1e6, 1),
    "combined_model_implied_eur_m": round(fl.pred_eur.sum() / 1e6, 1),
    "combined_value_one_year_later_eur_m": round(fl.next_value_eur.sum() / 1e6, 1),
    "portfolio_growth_pct": round(100 * (fl.next_value_eur.sum() /
                                         fl.market_value_eur.sum() - 1), 1),
    "benchmark_growth_pct": round(100 * (bm.next_value_eur.sum() /
                                         bm.market_value_eur.sum() - 1), 1),
}
for k, val_ in port.items():
    print(f"   {k:<38} {val_:>10}")
pd.Series(port).to_frame("value").to_csv(STAGE_OUT / "backtest_portfolio.csv")

resA.to_csv(STAGE_OUT / "backtest_outcome_value.csv", index=False)
perfdf.to_csv(STAGE_OUT / "backtest_outcome_performance.csv", index=False)
t.to_csv(STAGE_OUT / "backtest_full_2024_25.csv", index=False)

# =============================================================================
# FIGURE
# =============================================================================
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
ax[0].hist(bm.rel_appreciation, bins=45, alpha=.6, label=f"benchmark (n={len(bm)})",
           color="#a0aec0", density=True)
ax[0].hist(fl.rel_appreciation, bins=30, alpha=.7, label=f"flagged (n={len(fl)})",
           color="#2b6cb0", density=True)
ax[0].axvline(bm.rel_appreciation.median(), color="#4a5568", ls="--", lw=1.5)
ax[0].axvline(fl.rel_appreciation.median(), color="#2b6cb0", ls="--", lw=1.5)
ax[0].set_xlim(-1.5, 1.5)
ax[0].set_xlabel("relative appreciation vs position × league peers (log)")
ax[0].set_ylabel("density"); ax[0].legend(frameon=False, fontsize=8)
ax[0].set_title("2025/26 outcome distribution")

groups = ["Flagged\nundervalued", "Benchmark"]
meds = [fl.rel_appreciation.median(), bm.rel_appreciation.median()]
errs = [[meds[0] - lo_f, meds[1] - lo_b], [hi_f - meds[0], hi_b - meds[1]]]
ax[1].bar(groups, meds, yerr=errs, capsize=6, color=["#2b6cb0", "#a0aec0"])
ax[1].axhline(0, color="#4a5568", lw=1)
ax[1].set_ylabel("median relative appreciation (log)")
ax[1].set_title("Median outcome with 95% bootstrap CI")
fig.suptitle("Phase 7 back-test: flagged in 2024/25, measured in 2025/26", y=1.02)
fig.tight_layout(); fig.savefig(FIG / "q9_backtest.png", bbox_inches="tight")
plt.close(fig)

print("\n" + "=" * 78)
print("PHASE 7 COMPLETE")
print("=" * 78)
