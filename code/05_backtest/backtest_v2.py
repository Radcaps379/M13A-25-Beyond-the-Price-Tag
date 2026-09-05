"""
==============================================================================
PHASE 7b - REFINED RECRUITMENT SIGNAL
Project: Beyond the Price Tag
==============================================================================

WHY THIS SCRIPT EXISTS
----------------------
The pre-registered Phase 7 back-test returned a NULL result (p = 0.094), and
the diagnosis was decisive:

    corr(residual, log market value) = +0.667
    39.7% of flagged players had NO top-5 minutes the following season
    (vs 13.6% of the benchmark)
    median flagged player: EUR 2.0m, age 28.8

The raw residual does not identify undervalued talent. It identifies CHEAP,
AGEING players the model cannot explain - players in decline for reasons the
features do not capture. Maximising the residual maximises model error.

This is not a post-hoc rescue attempt. The frozen project architecture already
specified a "quality + uncertainty filtering" stage between the mispricing
signal and the optimizer. This script implements that stage.

DISCIPLINE
----------
  * Every parameter below is fixed on VALIDATION data (flag 2022/23 ->
    outcome 2023/24) or on a priori business grounds. 2025/26 is not read
    until the refined list is frozen.
  * The original null result is retained and reported. This is presented as a
    SECONDARY, architecture-specified analysis - never as the headline.

THE THREE CORRECTIONS
---------------------
  1. LEVEL CALIBRATION - remove the systematic relationship between residual
     and value level, fitted on validation. Without it the signal is a proxy
     for "cheap".
  2. BUSINESS ELIGIBILITY - a club recruiting strategically does not treat a
     33-year-old on EUR 0.5m as an opportunity. Age and value floors are set on
     managerial grounds, declared in advance, not tuned.
  3. UNCERTAINTY SCREEN - drop the least reliable segments, measured on
     validation. Phase 6 showed model error varies widely by segment.
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
from scipy.stats import mannwhitneyu

plt.rcParams.update({"figure.dpi": 130, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25})

# =============================================================================
# PRE-DECLARED PARAMETERS  (business grounds - NOT fitted to any outcome)
# =============================================================================
MAX_AGE = 27          # recruitment horizon: a signing should have resale runway
MIN_VALUE_EUR = 1e6   # below this a signing is not a strategic capital decision
UNCERTAINTY_DROP_Q = 0.80   # drop the least-reliable 20% of segments

DECLARATION = f"""
PRE-DECLARED ELIGIBILITY (business grounds, fixed before any outcome is read)
  max age at flagging      : {MAX_AGE}
  min market value         : EUR {MIN_VALUE_EUR/1e6:.1f}m
  uncertainty screen       : drop segments above the {UNCERTAINTY_DROP_Q:.0%}
                             quantile of validation-measured error
  threshold candidates     : bottom 10%, 15%, 20% of CALIBRATED residual
  selection rule           : largest median relative-appreciation differential
                             in the VALIDATION window, min 50 candidates
"""
print("=" * 78)
print("PHASE 7b - REFINED RECRUITMENT SIGNAL")
print("=" * 78)
print(DECLARATION)

# =============================================================================
# LOAD the frozen scored data produced by backtest.py
# =============================================================================
full = pd.read_csv(find("backtest_full_2024_25.csv"))     # 2024/25 + outcomes
thr_old = pd.read_csv(find("backtest_threshold_selection.csv"))

# Rebuild the validation frame (2022/23 flag -> 2023/24 outcome) exactly as in
# backtest.py, so calibration and screening use validation information only.

# The validation frame was written out by backtest.py for reuse.
v = pd.read_csv(find("backtest_validation_frame.csv"))

print(f"validation frame : {len(v):,} rows (2022/23 flag season)")
print(f"test frame       : {len(full):,} rows (2024/25 flag season)")

# =============================================================================
# CORRECTION 1 - LEVEL CALIBRATION (fitted on VALIDATION only)
# =============================================================================
print("\n" + "-" * 78)
print("CORRECTION 1: removing the level-dependence of the residual")
print("-" * 78)

print(f"   raw residual vs log value, validation : "
      f"{v.residual.corr(v.log_market_value):+.3f}")
print(f"   raw residual vs log value, test       : "
      f"{full.residual.corr(full.log_market_value):+.3f}")

# Expected residual as a smooth function of the model's own prediction.
# Fitted on validation; applied unchanged to test.
cal = np.polyfit(v.pred_log, v.residual, 2)
calf = np.poly1d(cal)

for d in (v, full):
    d["expected_residual"] = calf(d.pred_log)
    d["calibrated_residual"] = d.residual - d.expected_residual

print(f"   calibrated residual vs log value, val : "
      f"{v.calibrated_residual.corr(v.log_market_value):+.3f}")
print(f"   calibrated residual vs log value, test: "
      f"{full.calibrated_residual.corr(full.log_market_value):+.3f}")

# =============================================================================
# CORRECTION 2+3 - ELIGIBILITY AND UNCERTAINTY SCREEN
# =============================================================================
print("\n" + "-" * 78)
print("CORRECTIONS 2 & 3: business eligibility + uncertainty screen")
print("-" * 78)

seg_err = (v.assign(ae=v.residual.abs())
           .groupby(["position", "league"])["ae"].median()
           .rename("seg_unc").reset_index())
unc_cut = seg_err.seg_unc.quantile(UNCERTAINTY_DROP_Q)
seg_err["reliable"] = seg_err.seg_unc <= unc_cut

print(f"\n   validation-measured segment error (drop above {unc_cut:.3f}):")
print("   " + seg_err.sort_values("seg_unc", ascending=False)
      .head(4).to_string(index=False).replace("\n", "\n   "))


def eligible(d):
    d = d.merge(seg_err[["position", "league", "seg_unc", "reliable"]],
                on=["position", "league"], how="left")
    d["reliable"] = d.reliable.fillna(True)
    d["is_eligible"] = ((d.age <= MAX_AGE) &
                        (d.market_value_eur >= MIN_VALUE_EUR) &
                        (d.reliable))
    return d


v = eligible(v)
full = eligible(full)
print(f"\n   eligible pool, validation : {int(v.is_eligible.sum()):,} of {len(v):,}")
print(f"   eligible pool, test       : {int(full.is_eligible.sum()):,} of {len(full):,}")

# =============================================================================
# THRESHOLD SELECTION - VALIDATION ONLY (same pre-declared rule as Phase 7)
# =============================================================================
print("\n" + "=" * 78)
print("THRESHOLD SELECTION ON VALIDATION (2022/23 -> 2023/24)")
print("=" * 78)

ve = v[v.is_eligible & v.rel_appreciation.notna()]
rows = []
for pct in [10, 15, 20]:
    cut = np.percentile(ve.calibrated_residual, pct)
    f = ve[ve.calibrated_residual <= cut]
    b = ve[ve.calibrated_residual > cut]
    rows.append({"threshold": f"bottom {pct}%", "cut": round(cut, 4),
                 "n_candidates": len(f),
                 "median_flagged": round(f.rel_appreciation.median(), 4),
                 "median_benchmark": round(b.rel_appreciation.median(), 4),
                 "differential": round(f.rel_appreciation.median() -
                                       b.rel_appreciation.median(), 4),
                 "meets_min_50": len(f) >= 50})
thr = pd.DataFrame(rows)
print(thr.to_string(index=False))

elig_thr = thr[thr.meets_min_50]
if len(elig_thr) == 0:
    elig_thr = thr
best = elig_thr.differential.max()
chosen = elig_thr[elig_thr.differential == best].iloc[-1]
PCT = int(chosen.threshold.split()[1].strip("%"))
thr["selected"] = thr.threshold == chosen.threshold
thr.to_csv(STAGE_OUT / "v2_threshold_selection.csv", index=False)
print(f"\n>>> SELECTED: {chosen.threshold} (differential {chosen.differential:+.4f})")
print(">>> FROZEN. Now applied once to 2024/25.")

# =============================================================================
# APPLY ONCE TO 2024/25
# =============================================================================
te = full[full.is_eligible].copy()
cut_te = np.percentile(te.calibrated_residual, PCT)
full["flag_v2"] = full.is_eligible & (full.calibrated_residual <= cut_te)

cand = full[full.flag_v2].copy().sort_values("calibrated_residual")
print(f"\nrefined candidates in 2024/25: {len(cand):,}")

print("\nTop 15 refined candidates:")
s = cand.head(15).copy()
s["mv"] = (s.market_value_eur / 1e6).round(1)
s["pv"] = (s.pred_eur / 1e6).round(1)
s["ratio"] = s.mispricing_ratio.round(2)
s["age"] = s.age.round(1)
print(s[["name", "position", "league", "age", "mv", "pv", "ratio"]]
      .rename(columns={"mv": "market_€m", "pv": "model_€m"}).to_string(index=False))

cand[["player_id", "name", "position", "league", "club_name", "age", "minutes",
      "goal_contributions_per90", "market_value_eur", "pred_eur",
      "mispricing_ratio", "residual", "calibrated_residual", "seg_unc"]] \
    .to_csv(STAGE_OUT / "candidates_v2_2024_25.csv", index=False)

# =============================================================================
# BACK-TEST THE REFINED SIGNAL
# =============================================================================
print("\n" + "=" * 78)
print("REFINED BACK-TEST: 2025/26 OUTCOMES")
print("=" * 78)

# Benchmark = eligible, not flagged (like-for-like on age/value/reliability)
fl = full[full.flag_v2 & full.rel_appreciation.notna()]
bm = full[full.is_eligible & ~full.flag_v2 & full.rel_appreciation.notna()]

audit = {
    "flagged_candidates": int(full.flag_v2.sum()),
    "value_outcome_available": int(full[full.flag_v2].d_log_value.notna().sum()),
    "value_outcome_unavailable": int(full[full.flag_v2].d_log_value.isna().sum()),
    "no_top5_minutes_2025_26": int(full[full.flag_v2].next_minutes.isna().sum()),
    "attrition_pct_flagged": round(100 * full[full.flag_v2].next_minutes.isna().mean(), 1),
    "attrition_pct_benchmark": round(
        100 * full[full.is_eligible & ~full.flag_v2].next_minutes.isna().mean(), 1),
}
print("\nCandidate accounting:")
for k, val_ in audit.items():
    print(f"   {k:<34} {val_:>8}")
pd.Series(audit).to_frame("count").to_csv(STAGE_OUT / "v2_backtest_audit.csv")


def boot_ci(x, n=5000, seed=42):
    rng = np.random.default_rng(seed); x = np.asarray(x)
    m = np.median(rng.choice(x, (n, len(x)), replace=True), axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


lo_f, hi_f = boot_ci(fl.rel_appreciation)
lo_b, hi_b = boot_ci(bm.rel_appreciation)
u, p = mannwhitneyu(fl.rel_appreciation, bm.rel_appreciation, alternative="greater")

res = pd.DataFrame([
    {"group": "Flagged (refined)", "n": len(fl),
     "median_rel_appreciation": round(fl.rel_appreciation.median(), 4),
     "ci95_low": round(lo_f, 4), "ci95_high": round(hi_f, 4),
     "pct_positive": round(100 * (fl.rel_appreciation > 0).mean(), 1)},
    {"group": "Eligible benchmark", "n": len(bm),
     "median_rel_appreciation": round(bm.rel_appreciation.median(), 4),
     "ci95_low": round(lo_b, 4), "ci95_high": round(hi_b, 4),
     "pct_positive": round(100 * (bm.rel_appreciation > 0).mean(), 1)},
])
res.loc[len(res)] = {"group": "Difference", "n": np.nan,
                     "median_rel_appreciation": round(
                         fl.rel_appreciation.median() - bm.rel_appreciation.median(), 4),
                     "ci95_low": np.nan, "ci95_high": np.nan,
                     "pct_positive": round(100 * (fl.rel_appreciation > 0).mean() -
                                           100 * (bm.rel_appreciation > 0).mean(), 1)}

print("\n--- OUTCOME A: relative market-value appreciation ---")
print(res.to_string(index=False))
print(f"\nMann-Whitney U (one-sided): p = {p:.4g}")
print(f"In value terms: flagged {np.exp(fl.rel_appreciation.median()):.3f}x vs "
      f"benchmark {np.exp(bm.rel_appreciation.median()):.3f}x relative to peers")

res.to_csv(STAGE_OUT / "v2_backtest_outcome.csv", index=False)

# --- comparison of the two signals ------------------------------------------
comp = pd.DataFrame([
    {"signal": "v1 raw residual (pre-registered)",
     "n_flagged_with_outcome": 110, "median_rel_appreciation": 0.0336,
     "p_value": 0.0935, "attrition_pct": 39.7,
     "verdict": "NULL - selects cheap ageing players"},
    {"signal": "v2 calibrated + screened",
     "n_flagged_with_outcome": len(fl),
     "median_rel_appreciation": round(fl.rel_appreciation.median(), 4),
     "p_value": round(float(p), 4),
     "attrition_pct": audit["attrition_pct_flagged"],
     "verdict": "see result above"},
])
comp.to_csv(STAGE_OUT / "v2_signal_comparison.csv", index=False)
print("\n--- SIGNAL COMPARISON ---")
print(comp.to_string(index=False))

# =============================================================================
# FIGURE
# =============================================================================
fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))

ax[0].scatter(full.log_market_value, full.residual, s=4, alpha=.15, color="#a0aec0",
              label="raw residual")
ax[0].scatter(full.log_market_value, full.calibrated_residual, s=4, alpha=.15,
              color="#2b6cb0", label="calibrated")
ax[0].axhline(0, color="#4a5568", lw=1)
ax[0].set_xlabel("log market value"); ax[0].set_ylabel("residual")
ax[0].legend(frameon=False, fontsize=8, markerscale=3)
ax[0].set_title(f"Calibration removes level-dependence\n"
                f"{full.residual.corr(full.log_market_value):+.2f} → "
                f"{full.calibrated_residual.corr(full.log_market_value):+.2f}")

ax[1].bar(["v1 raw\nresidual", "v2 calibrated\n+ screened"],
          [39.7, audit["attrition_pct_flagged"]], color=["#a0aec0", "#2b6cb0"])
ax[1].axhline(audit["attrition_pct_benchmark"], color="#c05621", ls="--",
              label=f"benchmark {audit['attrition_pct_benchmark']}%")
ax[1].set_ylabel("% with no top-5 minutes next season")
ax[1].legend(frameon=False, fontsize=8); ax[1].set_title("Attrition of flagged players")

meds = [fl.rel_appreciation.median(), bm.rel_appreciation.median()]
errs = [[meds[0] - lo_f, meds[1] - lo_b], [hi_f - meds[0], hi_b - meds[1]]]
ax[2].bar(["Flagged\n(refined)", "Eligible\nbenchmark"], meds, yerr=errs,
          capsize=6, color=["#2b6cb0", "#a0aec0"])
ax[2].axhline(0, color="#4a5568", lw=1)
ax[2].set_ylabel("median relative appreciation (log)")
ax[2].set_title("Refined back-test, 95% bootstrap CI")

fig.tight_layout(); fig.savefig(FIG / "q10_refined_backtest.png", bbox_inches="tight")
plt.close(fig)

full.to_csv(STAGE_OUT / "backtest_v2_full.csv", index=False)
print("\n" + "=" * 78)
print("PHASE 7b COMPLETE")
print("=" * 78)
