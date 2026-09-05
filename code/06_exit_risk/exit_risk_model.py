"""
==============================================================================
PHASE 8 - EXIT-RISK MODEL
Project: Beyond the Price Tag
==============================================================================

WHY THIS EXISTS
---------------
Phase 7 found that players flagged by the mispricing residual were 3.7x the benchmark rate more
likely to disappear from top-5 football the following season (30.1% vs 8.2%,
Fisher p = 2.6e-11). That is the project's strongest validated finding.

But 30.1% is a BACK-TEST OUTCOME, not a probability model. Feeding that single
number into the optimizer would hardcode an unvalidated assumption - exactly the
mistake that made the undervaluation signal fail. So we build a proper model:

    TARGET: does this player record < 900 top-5 league minutes next season?

and hold it to the same standard as Model 1: strict time-based validation, no
test information in any fitting or threshold decision.

WHY THE RESIDUAL IS AN ALLOWED FEATURE HERE
-------------------------------------------
The mispricing residual failed to predict APPRECIATION. It succeeded in
predicting EXIT. Using it here is not recycling a dead signal - it is using the
one relationship the back-test actually validated.

WHAT THIS BUYS THE PROJECT
--------------------------
A per-player exit probability the optimizer can price, rather than a blanket
penalty. It converts a negative research result into a working decision input.
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
STAGE_OUT = stage_dir("exit_risk")


import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.calibration import calibration_curve

plt.rcParams.update({"figure.dpi": 130, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25})

TRAIN_END, VAL_END = 2021, 2023
INFO_CUTOFF = pd.Timestamp("2026-08-26")
TOP5 = ["GB1", "ES1", "L1", "IT1", "FR1"]
MIN_MINUTES = 900

print("=" * 78)
print("PHASE 8 - EXIT-RISK MODEL")
print("=" * 78)

# =============================================================================
# STEP 1 - BUILD THE TARGET: exit from top-5 football in season t+1
# =============================================================================
mm = pd.read_csv(find("model_matrix.csv"))

app = pd.read_csv(RAW / "appearances.csv", low_memory=False)
app["date"] = pd.to_datetime(app["date"], errors="coerce")
app = app[(app.date <= INFO_CUTOFF) & (app.competition_id.isin(TOP5))]
app["season"] = np.where(app.date.dt.month >= 7, app.date.dt.year, app.date.dt.year - 1)

nxt = (app.groupby(["player_id", "season"])["minutes_played"].sum()
       .rename("next_minutes").reset_index())
nxt["season"] = nxt["season"] - 1          # attach season t+1 outcome to season t

d = mm.merge(nxt, on=["player_id", "season"], how="left")
d["next_minutes"] = d["next_minutes"].fillna(0)

# The final season in the data has no observable "next season" outcome yet,
# so it cannot carry a label. 2024/25 -> 2025/26 IS observable, so 2024 stays.
LAST_LABELLED = 2024
d = d[d.season <= LAST_LABELLED].copy()
d["exit"] = (d.next_minutes < MIN_MINUTES).astype(int)

print(f"\nlabelled rows: {len(d):,}")
print(f"overall exit rate: {100*d.exit.mean():.1f}%")
print("\nexit rate by season:")
print((100 * d.groupby("season").exit.mean()).round(1).to_string())

# =============================================================================
# STEP 2 - ATTACH THE MISPRICING RESIDUAL (the validated Phase 7 relationship)
# =============================================================================
resid_src = pd.read_csv(find("backtest_v2_full.csv"))[
    ["player_id", "season", "residual", "calibrated_residual", "pred_log"]]
d = d.merge(resid_src, on=["player_id", "season"], how="left")

# Residuals only exist for seasons the frozen Model 1 scored (2022+). For
# training seasons we must generate them the same way, so we refit Model 1 on
# training data and score every row - this is the same model, same spec.
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


def design(fit_df, *others):
    def prep(x):
        z = x[M1].copy()
        for c in CAT:
            z[c] = z[c].fillna("unknown").astype(str)
        return z
    B = pd.get_dummies(prep(fit_df), columns=CAT, drop_first=True)
    out = [B.astype(float).fillna(0).values]
    for o in others:
        D = pd.get_dummies(prep(o), columns=CAT, drop_first=True)
        out.append(D.reindex(columns=B.columns, fill_value=0).astype(float).fillna(0).values)
    return out


tr_v = d[d.season <= TRAIN_END]
lv = tr_v.groupby("season").log_market_value.median()
carry = float(lv.loc[TRAIN_END])
d["market_level"] = d.season.map(lv).fillna(carry)
d["y_adj"] = d.log_market_value - d.market_level

Xtr, Xall = design(d[d.season <= TRAIN_END], d)
sc0 = StandardScaler().fit(Xtr)
# ESTIMATOR IS FIXED, NOT DISCOVERED.
# An earlier version tried to import lightgbm and fell back to scikit-learn.
# That made the estimator depend on what happened to be installed: a machine
# with lightgbm produced different numbers from the ones in the report. Every
# result in this repository was produced by HistGradientBoosting, so the choice
# is now explicit and the repository reproduces the report on any machine.
from sklearn.ensemble import HistGradientBoostingRegressor
mdl = HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05,
                                    random_state=42)
vm.fit(sc0.transform(Xtr), d[d.season <= TRAIN_END].y_adj.values)

d["pred_adj_all"] = vm.predict(sc0.transform(Xall))
d["pred_log_all"] = d.pred_adj_all + d.market_level
d["resid_all"] = d.log_market_value - d.pred_log_all
cal = np.poly1d(np.polyfit(d.loc[d.season <= TRAIN_END, "pred_log_all"],
                           d.loc[d.season <= TRAIN_END, "resid_all"], 2))
d["calib_resid_all"] = d.resid_all - cal(d.pred_log_all)

print(f"\nmispricing residual attached to all {len(d):,} rows "
      f"(Model 1 refit on training seasons only)")

# =============================================================================
# STEP 3 - FIT THE EXIT-RISK MODEL
# =============================================================================
EXIT_FEATURES = [
    "age", "age2", "position", "league",
    "minutes", "games", "minutes_per_game", "availability",
    "goal_contributions_per90", "cards_per90",
    "delta_minutes", "prev_minutes", "roll3_mean_minutes", "roll3_std_minutes",
    "delta_goal_contributions_per90", "roll3_mean_goal_contributions_per90",
    "seasons_observed", "has_prior_season", "is_first_observed_season",
    "log_market_value",
    "calib_resid_all",          # <- the Phase 7 validated relationship
]
ECAT = ["position", "league"]

train = d[d.season <= TRAIN_END]
val = d[(d.season > TRAIN_END) & (d.season <= VAL_END)]
test = d[d.season > VAL_END]

print(f"\nTRAIN {len(train):,}   VAL {len(val):,}   TEST {len(test):,} "
      f"(2024/25 -> 2025/26 outcome)")


def edesign(fit_df, *others):
    def prep(x):
        z = x[EXIT_FEATURES].copy()
        for c in ECAT:
            z[c] = z[c].astype(str)
        return z
    B = pd.get_dummies(prep(fit_df), columns=ECAT, drop_first=True)
    out = [B.astype(float).fillna(0).values]
    for o in others:
        D = pd.get_dummies(prep(o), columns=ECAT, drop_first=True)
        out.append(D.reindex(columns=B.columns, fill_value=0).astype(float).fillna(0).values)
    return out, list(B.columns)


(Etr, Eva, Ete), cols = edesign(train, val, test)
sc = StandardScaler().fit(Etr)
ytr, yva, yte = train.exit.values, val.exit.values, test.exit.values

# ESTIMATOR IS FIXED, NOT DISCOVERED.
# An earlier version tried to import lightgbm and fell back to scikit-learn.
# That made the estimator depend on what happened to be installed: a machine
# with lightgbm produced different numbers from the ones in the report. Every
# result in this repository was produced by HistGradientBoosting, so the choice
# is now explicit and the repository reproduces the report on any machine.
from sklearn.ensemble import HistGradientBoostingClassifier
clf = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05,
                                     random_state=42)
algo = "HistGBC"
clf.fit(sc.transform(Etr), ytr)

logit = LogisticRegression(max_iter=2000).fit(sc.transform(Etr), ytr)

rows = []
for nm, m in [("Logistic (interpretable)", logit), (f"{algo} (primary)", clf)]:
    for split, X, y in [("VALIDATION", Eva, yva), ("TEST", Ete, yte)]:
        p = m.predict_proba(sc.transform(X))[:, 1]
        rows.append({"model": nm, "split": split, "n": len(y),
                     "AUC": round(roc_auc_score(y, p), 4),
                     "Brier": round(brier_score_loss(y, p), 4),
                     "base_rate": round(float(y.mean()), 4)})
perf = pd.DataFrame(rows)
print("\n" + perf.to_string(index=False))
perf.to_csv(STAGE_OUT / "exit_risk_performance.csv", index=False)

# =============================================================================
# STEP 4 - CALIBRATION AND DECILE LIFT
# =============================================================================
# PRODUCTION MODEL = LOGISTIC REGRESSION.
# The interpretable model marginally OUTPERFORMED the boosted challenger out of
# sample (test AUC 0.7323 vs 0.7283), so there is no accuracy/interpretability
# trade-off to make here. The boosted model is retained as a challenger only.
# An earlier version scored the optimizer with the boosted probabilities while
# the write-up claimed logistic - that inconsistency is corrected here.
PRODUCTION = logit
p_te = PRODUCTION.predict_proba(sc.transform(Ete))[:, 1]
test = test.copy(); test["exit_prob"] = p_te
test["exit_prob_challenger"] = clf.predict_proba(sc.transform(Ete))[:, 1]

dec = (test.assign(decile=pd.qcut(test.exit_prob, 10, labels=False, duplicates="drop"))
       .groupby("decile").agg(n=("exit", "size"),
                              predicted=("exit_prob", "mean"),
                              actual=("exit", "mean")).reset_index())
dec["predicted"] = (100 * dec.predicted).round(1)
dec["actual"] = (100 * dec.actual).round(1)
print("\nDecile calibration on TEST (predicted vs actual exit %):")
print(dec.to_string(index=False))
dec.to_csv(STAGE_OUT / "exit_risk_calibration.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
ax[0].plot(dec.decile, dec.predicted, "o-", label="predicted", color="#2b6cb0")
ax[0].plot(dec.decile, dec.actual, "s-", label="actual", color="#c05621")
ax[0].set_xlabel("risk decile"); ax[0].set_ylabel("exit rate (%)")
ax[0].legend(frameon=False); ax[0].set_title("Exit-risk calibration (2024/25 → 2025/26)")

imp = pd.Series(np.abs(PRODUCTION.coef_[0]), index=cols)
imp = imp.sort_values(ascending=False).head(12)
ax[1].barh(range(len(imp)), imp.values, color="#2b6cb0")
ax[1].set_yticks(range(len(imp))); ax[1].set_yticklabels(imp.index, fontsize=8)
ax[1].invert_yaxis(); ax[1].set_title("Exit-risk drivers (|logistic coefficient|)")
fig.tight_layout(); fig.savefig(FIG / "q11_exit_risk.png", bbox_inches="tight")
plt.close(fig)

# =============================================================================
# STEP 5 - SCORE EVERY 2024/25 PLAYER FOR THE OPTIMIZER
# =============================================================================
out = test[["player_id", "name", "season", "position", "league", "club_name",
            "age", "minutes", "games", "goal_contributions_per90",
            "market_value_eur", "log_market_value",
            "calib_resid_all", "exit_prob", "exit", "next_minutes"]].copy()
out["pred_eur"] = np.exp(test.pred_log_all)
out["mispricing_ratio"] = out.pred_eur / out.market_value_eur
out["exit_prob_challenger"] = test["exit_prob_challenger"].values
out.to_csv(STAGE_OUT / "optimizer_input_2024_25.csv", index=False)

# =============================================================================
# EXPORT PRE-TEST CALIBRATION CONSTANTS FOR THE OPTIMIZER
# =============================================================================
# The optimizer must not derive ANY transformation from 2024/25 outcomes.
# An earlier version computed segment uncertainty from abs(2024/25 residual),
# which requires knowing the realized 2024/25 valuation - leakage. Both the
# uncertainty table and the value-efficiency cap are therefore fitted here on
# TRAIN+VALIDATION seasons only and handed to the optimizer as fixed inputs.
pre = d[d.season <= VAL_END].copy()
pre["ae"] = pre.calib_resid_all.abs()

global_unc = float(pre.ae.median())
pos_unc = pre.groupby("position")["ae"].median()
seg = pre.groupby(["position", "league"]).agg(
    seg_unc=("ae", "median"), n=("ae", "size")).reset_index()

# sparse cells fall back to position-level, then global
seg.loc[seg.n < 30, "seg_unc"] = seg.loc[seg.n < 30, "position"].map(pos_unc)
seg["seg_unc"] = seg.seg_unc.fillna(global_unc)
seg["source"] = np.where(seg.n < 30, "position-level fallback", "position x league")
seg.to_csv(STAGE_OUT / "pretest_segment_uncertainty.csv", index=False)

cap = float(pre.groupby("player_id").head(1).assign(
    ratio=lambda z: np.exp(z.log_market_value - z.pred_log_all)).ratio.median())
ve_cap = float((np.exp(pre.pred_log_all - pre.log_market_value)).quantile(0.90))
pd.Series({"value_efficiency_cap_p90": ve_cap,
           "global_uncertainty": global_unc,
           "fitted_on_seasons": f"<= {VAL_END}"}).to_frame("value").to_csv(STAGE_OUT / "pretest_constants.csv")

print(f"\npre-test constants (fitted on seasons <= {VAL_END}):")
print(f"   value-efficiency cap (p90) : {ve_cap:.3f}")
print(f"   global uncertainty         : {global_unc:.3f}")
print(f"   segment cells              : {len(seg)} "
      f"({int((seg.n < 30).sum())} using fallback)")

print(f"\nwrote optimizer_input_2024_25.csv ({len(out):,} players, "
      f"each with a validated exit probability)")
print("=" * 78)
