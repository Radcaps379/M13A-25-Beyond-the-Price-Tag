"""
==============================================================================
ROBUSTNESS CHECK - DOES THE RESIDUAL GRADIENT REPLICATE?
Project: Beyond the Price Tag
==============================================================================

PRE-SPECIFIED QUESTION (fixed before running)
---------------------------------------------
    Does the qualitative signed-residual pattern observed in the held-out
    2024/25 season also appear in the 2022/23 and 2023/24 validation seasons?

Expected pattern from the test season:
    younger age bands -> positive mean residual (model under-values)
    older age bands   -> negative mean residual (model over-values)
    England positive, Spain negative

FIXED IN ADVANCE - NOT TO BE CHANGED AFTER SEEING RESULTS
---------------------------------------------------------
  * Age bands: <=21, 22-24, 25-27, 28-30, 31+   (identical to Section 4.8)
  * Model: frozen Model 1 specification, trained on seasons <= 2021 only
  * Metric: mean signed residual (observed - model-implied log value)
  * Materiality threshold: +/- 0.05 log units (identical to Section 4.8)
  * Leagues examined: England and Spain (the two strongest test-season effects)

This is a DESCRIPTIVE replication check. No new model is fitted, no band is
redrawn, no threshold is tuned, and validation and test data are never pooled.
If the pattern does not replicate, the test-season result is reported as
season-specific heterogeneity rather than a general model property.
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

plt.rcParams.update({"figure.dpi": 130, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25})

TRAIN_END = 2021
BANDS = [15, 21, 24, 27, 30, 46]
LABELS = ["<=21", "22-24", "25-27", "28-30", "31+"]
MATERIAL = 0.05

print("=" * 78)
print("ROBUSTNESS CHECK - RESIDUAL GRADIENT REPLICATION")
print("=" * 78)

# --- rebuild frozen Model 1 --------------------------------------------------
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
later = mm[mm.season > TRAIN_END].copy()

lv = train.groupby("season").log_market_value.median()
carry = float(lv.loc[TRAIN_END])
train["market_level"] = train.season.map(lv)
later["market_level"] = carry
train["y_adj"] = train.log_market_value - train.market_level


def prep(d):
    x = d[M1].copy()
    for c in CAT:
        x[c] = x[c].fillna("unknown").astype(str)
    return x


B = pd.get_dummies(prep(train), columns=CAT, drop_first=True)
Xtr = B.astype(float).fillna(0).values
Xla = (pd.get_dummies(prep(later), columns=CAT, drop_first=True)
       .reindex(columns=B.columns, fill_value=0).astype(float).fillna(0).values)
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

later["pred_log"] = mdl.predict(sc.transform(Xla)) + later.market_level
later["resid"] = later.log_market_value - later.pred_log
later["age_band"] = pd.cut(later.age, BANDS, labels=LABELS)

print(f"frozen Model 1 trained on {len(train):,} rows (seasons <= {TRAIN_END})")
print(f"scored {len(later):,} rows across seasons {sorted(later.season.unique())}")

# =============================================================================
# AGE GRADIENT BY SEASON
# =============================================================================
print("\n" + "-" * 78)
print("AGE GRADIENT - mean signed residual by band and season")
print("-" * 78)

rows = []
for s in sorted(later.season.unique()):
    sub = later[later.season == s]
    for lab in LABELS:
        g = sub[sub.age_band == lab]
        if len(g) == 0:
            continue
        rows.append({"season": s,
                     "split": "VALIDATION" if s <= 2023 else "TEST",
                     "age_band": lab, "n": len(g),
                     "mean_residual": round(float(g.resid.mean()), 4)})
age_tab = pd.DataFrame(rows)

pivot = age_tab.pivot(index="age_band", columns="season", values="mean_residual").reindex(LABELS)
npiv = age_tab.pivot(index="age_band", columns="season", values="n").reindex(LABELS)
print("\nmean residual:")
print(pivot.to_string())
print("\nsample size:")
print(npiv.to_string())

# --- replication verdict, using the pre-specified criterion -----------------
print("\n" + "-" * 78)
print("REPLICATION VERDICT")
print("-" * 78)

verdicts = []
for s in sorted(later.season.unique()):
    col = pivot[s].dropna()
    monotonic = bool(np.all(np.diff(col.values) < 0))
    young_pos = bool(col.loc["<=21"] > MATERIAL)
    old_neg = bool(col.loc["31+"] < -MATERIAL)
    spread = float(col.loc["<=21"] - col.loc["31+"])
    verdicts.append({"season": s, "split": "VALIDATION" if s <= 2023 else "TEST",
                     "monotonic_decline": monotonic,
                     "young_band_positive": young_pos,
                     "old_band_negative": old_neg,
                     "spread_young_minus_old": round(spread, 4),
                     "pattern_replicates": bool(young_pos and old_neg)})
vdf = pd.DataFrame(verdicts)
print(vdf.to_string(index=False))

val_rep = vdf[vdf.split == "VALIDATION"].pattern_replicates.all()
print(f"\n>>> Pattern replicates in ALL validation seasons: {val_rep}")

# =============================================================================
# LEAGUE CHECK - England vs Spain
# =============================================================================
print("\n" + "-" * 78)
print("LEAGUE CHECK - England vs Spain")
print("-" * 78)

lrows = []
for s in sorted(later.season.unique()):
    sub = later[later.season == s]
    for lg in ["England - Premier League", "Spain - LaLiga"]:
        g = sub[sub.league == lg]
        lrows.append({"season": s, "split": "VALIDATION" if s <= 2023 else "TEST",
                      "league": lg.split(" - ")[0], "n": len(g),
                      "mean_residual": round(float(g.resid.mean()), 4)})
lg_tab = pd.DataFrame(lrows)
print(lg_tab.pivot(index="league", columns="season", values="mean_residual").to_string())

eng_pos = all(lg_tab[(lg_tab.league == "England") & (lg_tab.split == "VALIDATION")]
              .mean_residual > MATERIAL)
esp_neg = all(lg_tab[(lg_tab.league == "Spain") & (lg_tab.split == "VALIDATION")]
              .mean_residual < -MATERIAL)
print(f"\n   England positive in all validation seasons: {eng_pos}")
print(f"   Spain negative in all validation seasons   : {esp_neg}")

# =============================================================================
# SAVE
# =============================================================================
age_tab.to_csv(STAGE_OUT / "robustness_age_gradient.csv", index=False)
vdf.to_csv(STAGE_OUT / "robustness_verdict.csv", index=False)
lg_tab.to_csv(STAGE_OUT / "robustness_league.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
for s in sorted(later.season.unique()):
    col = pivot[s].dropna()
    style = "o--" if s <= 2023 else "s-"
    lw = 1.6 if s <= 2023 else 2.6
    ax[0].plot(range(len(col)), col.values, style, lw=lw,
               label=f"{s}/{str(s+1)[-2:]}" + (" (test)" if s > 2023 else ""))
ax[0].axhline(0, color="#4a5568", lw=1)
ax[0].axhspan(-MATERIAL, MATERIAL, color="#e2e8f0", alpha=.6)
ax[0].set_xticks(range(len(LABELS))); ax[0].set_xticklabels(LABELS)
ax[0].set_xlabel("age band"); ax[0].set_ylabel("mean signed residual")
ax[0].legend(frameon=False, fontsize=8)
ax[0].set_title("Age gradient replicates across seasons")

lp = lg_tab.pivot(index="season", columns="league", values="mean_residual")
w = 0.35; xs = np.arange(len(lp))
ax[1].bar(xs - w/2, lp["England"], w, label="England", color="#2b6cb0")
ax[1].bar(xs + w/2, lp["Spain"], w, label="Spain", color="#c05621")
ax[1].axhline(0, color="#4a5568", lw=1)
ax[1].set_xticks(xs); ax[1].set_xticklabels([f"{s}/{str(s+1)[-2:]}" for s in lp.index])
ax[1].set_ylabel("mean signed residual"); ax[1].legend(frameon=False, fontsize=8)
ax[1].set_title("League effect by season")
fig.tight_layout(); fig.savefig(FIG / "q15_robustness_gradient.png", bbox_inches="tight")
plt.close(fig)

print("\n" + "=" * 78)
print("ROBUSTNESS CHECK COMPLETE")
print("=" * 78)
