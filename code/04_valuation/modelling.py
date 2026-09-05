"""
==============================================================================
PHASE 6 - MODELLING: THE THREE-MODEL EXPERIMENT
Project: Beyond the Price Tag
==============================================================================

THE RESEARCH DESIGN
-------------------
  MODEL 0  Context-only benchmark
           Can age, position, league and market-wide time trends alone explain
           player valuation?

  MODEL 1  Fundamental valuation model            <-- PRIMARY SPECIFICATION
           How much additional explanatory power comes from observable
           performance and performance trajectory?

  MODEL 2  Market-informed benchmark              <-- ROBUSTNESS ONLY
           How much does accuracy improve when the model is allowed to see the
           player's PREVIOUS market valuation?

Model 2 is expected to win on accuracy. That is the point, not an embarrassment:
predicting the market is easier than challenging it. Model 1 remains primary
because its residual is an economically meaningful mispricing signal, whereas
Model 2's residual is largely "deviation from Transfermarkt's own persistence".

TIME DISCIPLINE (applies to EVERYTHING, not just the split)
-----------------------------------------------------------
  TRAIN       2015/16 - 2021/22
  VALIDATION  2022/23 - 2023/24   (tuning, threshold choice)
  TEST        2024/25             (touched once, at the very end)

No feature selection, no hyperparameter choice and no threshold is ever made
using validation or test information.

ALL THREE MODELS ARE SCORED ON EXACTLY THE SAME TEST ROWS.

OUTPUTS
-------
  model_results.csv        headline comparison table
  segment_stability.csv    error by position / age band / league
  predictions_test.csv     row-level test predictions for the mispricing layer
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
STAGE_OUT = stage_dir("valuation")


import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

plt.rcParams.update({"figure.dpi": 130, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25})

TRAIN_END, VAL_END = 2021, 2023   # test = 2024

mm = pd.read_csv(find("model_matrix.csv"))
print("=" * 78)
print(f"PHASE 6 - MODELLING   |   {len(mm):,} player-seasons")
print("=" * 78)

# -----------------------------------------------------------------------------
# Feature sets (read back from the frozen definition file)
# -----------------------------------------------------------------------------
CAT = ["position", "league", "season"]

M0 = ["age", "age2", "position", "league", "season"]
M1 = M0 + [
    "height_in_cm", "foot",
    "minutes", "games", "goals_per90", "assists_per90",
    "goal_contributions_per90", "cards_per90", "minutes_per_game", "availability",
    "prev_minutes", "delta_minutes",
    "prev_goals_per90", "delta_goals_per90",
    "prev_assists_per90", "delta_assists_per90",
    "prev_goal_contributions_per90", "delta_goal_contributions_per90",
    "roll3_mean_goal_contributions_per90", "roll3_std_goal_contributions_per90",
    "roll3_mean_minutes", "roll3_std_minutes",
    "seasons_observed", "has_prior_season", "has_3yr_history",
    "is_first_observed_season", "prior_gap_years", "young_and_improving",
    "club_squad_size",
]
M2 = M1 + ["log_prior_market_value", "has_prior_value"]

SETS = {"Model 0": M0, "Model 1": M1, "Model 2": M2}

# -----------------------------------------------------------------------------
# Time-based split
# -----------------------------------------------------------------------------
train = mm[mm.season <= TRAIN_END].copy()
val = mm[(mm.season > TRAIN_END) & (mm.season <= VAL_END)].copy()
test = mm[mm.season > VAL_END].copy()

print(f"\nTRAIN  {train.season.min()}/16-{train.season.max()}/22   n={len(train):,}")
print(f"VALID  {val.season.min()}/23-{val.season.max()}/24   n={len(val):,}")
print(f"TEST   {test.season.min()}/25              n={len(test):,}   <- touched once")
print("\nAll three models are scored on these identical test rows.")

# =============================================================================
# MARKET-LEVEL DEFLATION  (why season cannot be a dummy variable)
# =============================================================================
print("\n" + "-" * 78)
print("MARKET-LEVEL ADJUSTMENT")
print("-" * 78)
print("A season DUMMY cannot extrapolate: the test season never appears in")
print("training, so every test row silently falls back to the baseline season.")
print("With ~2.6x market inflation across the period that deflates every test")
print("prediction by roughly a decade of growth - a severe, invisible bias.")
print()
print("We therefore demean each TRAINING season by its own median, and carry the")
print("last training level forward to validation and test. Two claims are then")
print("reported separately:")
print("  R2_relative  <- PRIMARY. Level-invariant: how well are players valued")
print("                  relative to peers within a season? Market level cancels.")
print("  R2 / euro    <- Deployable forecast using the carried-forward level.")
print("                  No realized validation or test outcome is used.")

# --- MARKET LEVEL: estimated WITHOUT any test-season outcome ------------------
# An earlier version computed each season's level from that season's own median
# valuation - including the test season. That used realized 2024/25 targets to
# re-inflate 2024/25 predictions, which contaminates the euro-denominated test
# metrics. Aggregate or not, it is information that does not exist at the moment
# the prediction is made.
#
# We now separate two distinct claims:
#
#   (A) DEPLOYABLE FORECAST - fully out-of-sample.
#       Training seasons are demeaned by their own median (in-sample, legitimate).
#       Validation and test seasons carry forward the LAST TRAINING season's
#       level. No post-training outcome is used anywhere. Euro metrics reported
#       under this scheme are honest out-of-sample performance.
#
#   (B) WITHIN-SEASON RELATIVE VALUATION - the project's primary claim.
#       Evaluated after removing a single per-season constant from both actual
#       and predicted values, so the market level cancels exactly. This measures
#       how well the model values players RELATIVE to each other in a season,
#       which is what a recruitment decision actually needs. The constant is
#       calibrated on the evaluation season and is therefore reported as a
#       calibration layer, never as evidence of level-forecasting accuracy.
#
# The mispricing signal is unaffected by either choice: it is a within-season
# residual, so the level term cancels out entirely.

train_levels = train.groupby("season")["log_market_value"].median()
carry_level = float(train_levels.loc[TRAIN_END])   # last training season

train["market_level"] = train["season"].map(train_levels)
for df in (val, test):
    df["market_level"] = carry_level              # carried forward, no leakage

for df in (train, val, test):
    df["y_adj"] = df["log_market_value"] - df["market_level"]

print("\n   training-season levels (median log value):")
print("   " + ", ".join(f"{s}:{v:.2f}" for s, v in train_levels.items()))
print(f"   carried forward to VALID and TEST: {carry_level:.2f} "
      f"(last training season, {TRAIN_END}/{str(TRAIN_END+1)[-2:]})")
print("   -> no realized validation or test outcome enters the calibration")

CAT = ["position", "league"]
M0 = [c for c in M0 if c != "season"]
M1 = [c for c in M1 if c != "season"]
M2 = [c for c in M2 if c != "season"]
SETS = {"Model 0": M0, "Model 1": M1, "Model 2": M2}
print("   'season' removed from all feature sets (absorbed by the market level)")


def design(cols, fit_frame, *frames):
    """
    Build aligned design matrices. Categories are learned from the TRAINING
    frame only, so no test-period category can influence encoding.
    """
    def prep(df):
        d = df[cols].copy()
        for c in CAT:
            if c in d.columns:
                d[c] = d[c].astype(str)
        if "foot" in d.columns:
            d["foot"] = d["foot"].fillna("unknown").astype(str)
        return d

    base = prep(fit_frame)
    dumcols = [c for c in CAT + ["foot"] if c in base.columns]
    B = pd.get_dummies(base, columns=dumcols, drop_first=True)
    out = [B]
    for f in frames:
        D = pd.get_dummies(prep(f), columns=dumcols, drop_first=True)
        D = D.reindex(columns=B.columns, fill_value=0)   # align to train columns
        out.append(D)
    return [x.astype(float).fillna(0.0).values for x in out]


def evaluate_relative(y_true_log, y_pred_log):
    """
    Level-invariant evaluation. Removes one constant from actual and one from
    predicted, so any error in the market-level estimate cancels. This is the
    project's PRIMARY metric: how well are players valued relative to peers
    within the same season?
    """
    a = y_true_log - np.mean(y_true_log)
    p = y_pred_log - np.mean(y_pred_log)
    return {"R2_relative": round(float(r2_score(a, p)), 4),
            "MAE_log_relative": round(float(mean_absolute_error(a, p)), 4)}


def evaluate(name, y_true_log, y_pred_log):
    """Metrics in log space AND in euros, since the business output is euros."""
    rmse_log = float(np.sqrt(mean_squared_error(y_true_log, y_pred_log)))
    mae_log = float(mean_absolute_error(y_true_log, y_pred_log))
    r2 = float(r2_score(y_true_log, y_pred_log))
    true_eur = np.exp(y_true_log)
    pred_eur = np.exp(y_pred_log)
    pct_err = np.abs(pred_eur - true_eur) / true_eur
    return {"model": name, "RMSE_log": round(rmse_log, 4), "MAE_log": round(mae_log, 4),
            "R2": round(r2, 4),
            "median_pct_error": round(float(np.median(pct_err)) * 100, 1),
            "MAE_eur_millions": round(float(np.mean(np.abs(pred_eur - true_eur))) / 1e6, 2)}


# =============================================================================
# FIT AND EVALUATE
# =============================================================================
results, preds, models = [], {}, {}

for name, cols in SETS.items():
    print("\n" + "-" * 78)
    print(f"{name}   ({len(cols)} raw variables)")
    print("-" * 78)

    Xtr, Xva, Xte = design(cols, train, val, test)
    # train on the DEFLATED target; re-inflate before scoring so all metrics
    # remain in true log-euro units and are comparable across models
    ytr = train.y_adj.values
    yva_true = val.log_market_value.values
    yte_true = test.log_market_value.values

    sc = StandardScaler().fit(Xtr)          # fitted on TRAIN only
    Xtr_s, Xva_s, Xte_s = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)

    # --- (a) OLS baseline ---------------------------------------------------
    ols = LinearRegression().fit(Xtr_s, ytr)

    # --- (b) Ridge: several of our features are mechanically related --------
    #     (goals/90 + assists/90 = contributions/90; minutes/games/mins-per-game)
    #     so the linear model is exposed to multicollinearity. Alpha is chosen
    #     by CV INSIDE THE TRAINING PERIOD ONLY.
    ridge = RidgeCV(alphas=np.logspace(-3, 3, 25)).fit(Xtr_s, ytr)

    # --- (c) Gradient boosting ---------------------------------------------
    # ESTIMATOR IS FIXED, NOT DISCOVERED.
    # An earlier version tried to import lightgbm and fell back to scikit-learn.
    # That made the estimator depend on what happened to be installed: a machine
    # with lightgbm produced different numbers from those in the report. Every
    # result in this repository was produced by HistGradientBoosting, so the
    # choice is explicit and the repository reproduces the report anywhere.
    from sklearn.ensemble import HistGradientBoostingRegressor
    gbm = HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05,
                                        random_state=42)
    gbm.fit(Xtr_s, ytr)
    gbm_name = "HistGBM"

    for algo, mdl in [("OLS", ols), ("Ridge", ridge), (gbm_name, gbm)]:
        p_va = mdl.predict(Xva_s) + val.market_level.values      # re-inflate
        p_te = mdl.predict(Xte_s) + test.market_level.values     # re-inflate
        r_va = evaluate(f"{name} / {algo}", yva_true, p_va)
        r_te = evaluate(f"{name} / {algo}", yte_true, p_te)
        r_va.update(evaluate_relative(yva_true, p_va))
        r_te.update(evaluate_relative(yte_true, p_te))
        r_te["split"] = "TEST"; r_va["split"] = "VALIDATION"
        r_te["raw_vars"] = len(cols); r_va["raw_vars"] = len(cols)
        results.extend([r_va, r_te])
        print(f"   {algo:<10} TEST R2_relative={r_te['R2_relative']:.3f}  "
              f"(deployable-level R2={r_te['R2']:.3f}, median%err={r_te['median_pct_error']:.1f}%)")

    # keep the boosted model's test predictions for the mispricing layer
    preds[name] = mdl.predict(Xte_s) + test.market_level.values
    models[name] = (mdl, sc, cols, gbm_name)

res = pd.DataFrame(results)[
    ["model", "split", "raw_vars", "R2_relative", "MAE_log_relative",
     "R2", "RMSE_log", "MAE_log", "median_pct_error", "MAE_eur_millions"]]
res.to_csv(STAGE_OUT / "model_results.csv", index=False)

print("\n" + "=" * 78)
print("HEADLINE COMPARISON  (TEST = 2024/25, identical rows for all models)")
print("=" * 78)
print(res[res.split == "TEST"].to_string(index=False))

# =============================================================================
# SEGMENT STABILITY - error must not hide in one group
# =============================================================================
print("\n" + "=" * 78)
print("SEGMENT STABILITY (Model 1, test set)")
print("=" * 78)

test = test.reset_index(drop=True)
test["pred_log_m1"] = preds["Model 1"]
test["pred_eur_m1"] = np.exp(test.pred_log_m1)
test["abs_pct_err"] = (test.pred_eur_m1 - test.market_value_eur).abs() / test.market_value_eur
test["age_band"] = pd.cut(test.age, [15, 21, 24, 27, 30, 46],
                          labels=["<=21", "22-24", "25-27", "28-30", "31+"])

seg = []
for dim in ["position", "league", "age_band"]:
    for k, grp in test.groupby(dim, observed=True):
        seg.append({"dimension": dim, "segment": str(k), "n": len(grp),
                    "median_pct_error": round(100 * grp.abs_pct_err.median(), 1),
                    "R2": round(r2_score(grp.log_market_value, grp.pred_log_m1), 3)
                    if len(grp) > 30 else np.nan})
segdf = pd.DataFrame(seg)
segdf.to_csv(STAGE_OUT / "segment_stability.csv", index=False)
print(segdf.to_string(index=False))

# =============================================================================
# FIGURES
# =============================================================================
te = res[res.split == "TEST"]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))

lbl = te.model.tolist()
ax[0].barh(range(len(te)), te.R2, color=["#90cdf4"] * 3 + ["#2b6cb0"] * 3 + ["#c05621"] * 3)
ax[0].set_yticks(range(len(te))); ax[0].set_yticklabels(lbl, fontsize=8)
ax[0].set_xlabel("Test R² (2024/25)"); ax[0].invert_yaxis()
ax[0].set_title("Accuracy rises when the model may see prior market value")

ax[1].scatter(test.market_value_eur / 1e6, test.pred_eur_m1 / 1e6, s=6, alpha=.3,
              color="#2b6cb0")
lim = [0, test.market_value_eur.max() / 1e6 * 1.05]
ax[1].plot(lim, lim, "--", color="#c05621", lw=1.5, label="perfect prediction")
ax[1].set_xlabel("actual market value (€m)"); ax[1].set_ylabel("Model 1 predicted (€m)")
ax[1].set_title("Model 1 fit on held-out 2024/25"); ax[1].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(FIG / "q8_model_comparison.png", bbox_inches="tight")
plt.close(fig)

test.to_csv(STAGE_OUT / "predictions_test.csv", index=False)

print("\n" + "=" * 78)
print("written: model_results.csv, segment_stability.csv, predictions_test.csv")
print("=" * 78)
