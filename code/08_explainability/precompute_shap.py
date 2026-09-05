"""
Precompute per-player SHAP drivers for all 2024/25 players so the dashboard can
explain any player instantly without loading the model or shap at runtime.
Writes: data/processed/shap_all_players.csv
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

import pandas as pd, numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import shap

TRAIN_END = 2021

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
test = mm[mm.season > 2023].copy().reset_index(drop=True)
lv = train.groupby("season").log_market_value.median()
carry = float(lv.loc[TRAIN_END])
train["y_adj"] = train.log_market_value - train.season.map(lv)


def prep(d):
    x = d[M1].copy()
    for c in CAT:
        x[c] = x[c].fillna("unknown").astype(str)
    return x


B = pd.get_dummies(prep(train), columns=CAT, drop_first=True)
FEAT = list(B.columns)
Xtr = B.astype(float).fillna(0).values
Xte = (pd.get_dummies(prep(test), columns=CAT, drop_first=True)
       .reindex(columns=FEAT, fill_value=0).astype(float).fillna(0).values)
sc = StandardScaler().fit(Xtr)

# scikit-learn's HistGradientBoostingRegressor - the same estimator used
# throughout the project. lightgbm is not installed in this environment and the
# frozen results were all produced with this fallback.
from sklearn.ensemble import HistGradientBoostingRegressor
mdl = HistGradientBoostingRegressor(max_iter=600, learning_rate=0.05,
                                    random_state=42)
mdl.fit(sc.transform(Xtr), train.y_adj.values)

sv = shap.TreeExplainer(mdl).shap_values(sc.transform(Xte))
svd = pd.DataFrame(sv, columns=FEAT)

READABLE = {
    "age": "age", "age2": "age (non-linear)", "minutes": "league minutes",
    "games": "appearances", "goals_per90": "goals per 90",
    "assists_per90": "assists per 90",
    "goal_contributions_per90": "goal contributions per 90",
    "cards_per90": "disciplinary record", "minutes_per_game": "minutes per appearance",
    "availability": "availability", "prev_minutes": "minutes last season",
    "delta_minutes": "change in minutes", "prev_goals_per90": "goals/90 last season",
    "delta_goals_per90": "change in goals/90",
    "prev_assists_per90": "assists/90 last season",
    "delta_assists_per90": "change in assists/90",
    "prev_goal_contributions_per90": "contributions/90 last season",
    "delta_goal_contributions_per90": "change in contributions/90",
    "roll3_mean_goal_contributions_per90": "3-season average output",
    "roll3_std_goal_contributions_per90": "output consistency",
    "roll3_mean_minutes": "3-season average minutes",
    "roll3_std_minutes": "minutes consistency",
    "seasons_observed": "seasons of top-5 history",
    "has_prior_season": "prior-season history",
    "has_3yr_history": "3+ seasons of history",
    "is_first_observed_season": "first observed season",
    "prior_gap_years": "gap since last season",
    "young_and_improving": "young and improving",
    "club_squad_size": "club squad rotation", "height_in_cm": "height",
}

# League dummies are consolidated: with drop_first encoding, a player's own
# league shows as an absent indicator, so raw dummy values read as nonsense
# ("plays in LaLiga" for a Premier League player). We sum them into one term.
league_cols = [c for c in FEAT if c.startswith("league_")]
other_cols = [c for c in FEAT if not c.startswith("league_")]

rows = []
for i in range(len(test)):
    r = svd.iloc[i]
    league_total = float(r[league_cols].sum())
    contrib = {READABLE.get(c, c.replace("position_", "position: ")
                            .replace("foot_", "foot: ")): float(r[c])
               for c in other_cols}
    contrib["league context"] = league_total
    s = pd.Series(contrib).sort_values(ascending=False)
    pos = s[s > 0.001].head(5)
    neg = s[s < -0.001].tail(5).sort_values()
    rows.append({
        "player_id": test.loc[i, "player_id"],
        "positive_drivers": "; ".join(f"{k} ({v:+.3f})" for k, v in pos.items()),
        "negative_drivers": "; ".join(f"{k} ({v:+.3f})" for k, v in neg.items()),
    })

pd.DataFrame(rows).to_csv(STAGE_OUT / "shap_all_players.csv", index=False)
print(f"wrote shap_all_players.csv for {len(rows):,} players")
