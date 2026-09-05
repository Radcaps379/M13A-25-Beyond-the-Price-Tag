"""
==============================================================================
PHASE 5 - FEATURE ENGINEERING
Project: Beyond the Price Tag
==============================================================================

WHAT THIS SCRIPT DOES
---------------------
Turns player_season.csv into a modelling matrix, and builds the three nested
feature sets we agreed to compare:

  MODEL 0  market context only     age, age2, position, league, season
           -> "how much is explained by context alone?"
  MODEL 1  + performance & trajectory                    <-- PRIMARY MODEL
           -> "how much of valuation does observable football explain?"
  MODEL 2  + prior market value                          <-- ROBUSTNESS ONLY
           -> "how much do we gain by letting the model listen to the market?"

The residual from MODEL 1 is the mispricing signal. MODEL 2 exists to show what
happens when we let the model re-predict Transfermarkt instead of challenging it.

LEAKAGE DISCIPLINE
------------------
Every feature is classified in the feature dictionary as one of:
  ALLOWED        known before the target valuation date - safe
  ROBUSTNESS     legitimate but market-derived - Model 2 only
  EXCLUDED       leaks the target or post-decision information

TRAJECTORY AND MISSING HISTORY
------------------------------
Players in their first observed season have no prior-season history. We do NOT
drop them - that would bias the sample toward long-tenured players. Instead we
fill trajectory features with 0 and carry explicit indicator flags so the model
can learn "no history available" as its own state.

OUTPUTS
-------
  model_matrix.csv        the modelling table
  feature_dictionary.csv  every feature, its meaning, and its leakage class
  club_context_audit.csv  evidence for/against including club variables
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
STAGE_OUT = PROC


import pandas as pd
import numpy as np
from pathlib import Path


INFO_CUTOFF = pd.Timestamp("2026-08-26")
TOP5 = ["GB1", "ES1", "L1", "IT1", "FR1"]

feature_dict = []


def declare(name, group, description, leakage_class, model_sets):
    feature_dict.append({
        "feature": name, "group": group, "description": description,
        "leakage_class": leakage_class, "used_in": model_sets,
    })


print("=" * 78)
print("PHASE 5 - FEATURE ENGINEERING")
print("=" * 78)

ps = pd.read_csv(find("player_season.csv"))
print(f"loaded player_season.csv: {len(ps):,} rows")

# =============================================================================
# STEP 1 - SEASON-SPECIFIC CLUB CONTEXT (replaces the present-day snapshot)
# =============================================================================
print("\nSTEP 1: Deriving club context AS IT WAS in each season")
print("   clubs.csv squad_size/average_age/stadium_seats describe each club as")
print("   of the 2026 export, NOT as of 2015/16. Attaching those to historical")
print("   rows would inject information from years after the observation, so we")
print("   rebuild club context from that season's actual appearances instead.")

app = pd.read_csv(RAW / "appearances.csv", low_memory=False)
app["date"] = pd.to_datetime(app["date"], errors="coerce")
app = app[(app["date"] <= INFO_CUTOFF) & (app["competition_id"].isin(TOP5))]
app["season"] = np.where(app["date"].dt.month >= 7,
                         app["date"].dt.year, app["date"].dt.year - 1)

players = pd.read_csv(RAW / "players.csv", low_memory=False)
players["date_of_birth"] = pd.to_datetime(players["date_of_birth"], errors="coerce")
app = app.merge(players[["player_id", "date_of_birth"]], on="player_id", how="left")
ref = pd.to_datetime((app["season"] + 1).astype(str) + "-01-01")
app["age_at_season"] = (ref - app["date_of_birth"]).dt.days / 365.25

club_ctx = (app.groupby(["player_club_id", "season"])
              .agg(club_squad_size=("player_id", "nunique"),
                   club_mean_age=("age_at_season", "mean"),
                   club_total_minutes=("minutes_played", "sum"))
              .reset_index()
              .rename(columns={"player_club_id": "main_club_id"}))

ps = ps.merge(club_ctx, on=["main_club_id", "season"], how="left")
print(f"   attached season-specific club context "
      f"({ps['club_squad_size'].notna().mean()*100:.1f}% matched)")

# =============================================================================
# STEP 2 - PLAYER CHARACTERISTICS
# =============================================================================
print("\nSTEP 2: Player characteristics")

ps["age2"] = ps["age"] ** 2
declare("age", "player", "Age in years at 1 Jan of the season", "ALLOWED", "0,1,2")
declare("age2", "player", "Age squared - captures the non-linear value curve "
        "(EDA showed a peak near 21 then steep decline)", "ALLOWED", "0,1,2")
declare("position", "player", "Broad position (Attack/Midfield/Defender/Goalkeeper)",
        "ALLOWED", "0,1,2")
declare("height_in_cm", "player", "Height in cm", "ALLOWED", "1,2")
declare("foot", "player", "Preferred foot", "ALLOWED", "1,2")

# =============================================================================
# STEP 3 - CURRENT-SEASON PERFORMANCE
# =============================================================================
print("STEP 3: Current-season performance")

ps["availability"] = ps["minutes"] / (ps["games"] * 90.0)
ps["starts_proxy"] = (ps["minutes_per_game"] >= 60).astype(int)

for c, d in [
    ("minutes", "Total league minutes in the season"),
    ("games", "League appearances in the season"),
    ("goals_per90", "Goals per 90 minutes"),
    ("assists_per90", "Assists per 90 minutes"),
    ("goal_contributions_per90", "Goals + assists per 90 minutes"),
    ("cards_per90", "Yellow + red cards per 90 minutes"),
    ("minutes_per_game", "Average minutes per appearance"),
    ("availability", "Share of available minutes played when appearing"),
]:
    declare(c, "performance_current", d, "ALLOWED", "1,2")

# =============================================================================
# STEP 4 - PERFORMANCE TRAJECTORY (prior seasons only)
# =============================================================================
print("STEP 4: Performance trajectory from PRIOR seasons only")

ps = ps.sort_values(["player_id", "season"]).reset_index(drop=True)
g = ps.groupby("player_id")

TRAJ = ["minutes", "goals_per90", "assists_per90", "goal_contributions_per90"]

# --- one-season lag --------------------------------------------------------
for c in TRAJ:
    ps[f"prev_{c}"] = g[c].shift(1)
    ps[f"delta_{c}"] = ps[c] - ps[f"prev_{c}"]

ps["prev_season"] = g["season"].shift(1)
ps["seasons_since_prev"] = ps["season"] - ps["prev_season"]

# --- multi-season history (3-season window, prior seasons only) ------------
for c in ["goal_contributions_per90", "minutes"]:
    ps[f"roll3_mean_{c}"] = (g[c].shift(1)
                             .groupby(ps["player_id"])
                             .rolling(3, min_periods=2).mean()
                             .reset_index(level=0, drop=True))
    ps[f"roll3_std_{c}"] = (g[c].shift(1)
                            .groupby(ps["player_id"])
                            .rolling(3, min_periods=2).std()
                            .reset_index(level=0, drop=True))

# --- history availability indicators (kept, never dropped) -----------------
ps["seasons_observed"] = g.cumcount()                       # 0 = first season
ps["has_prior_season"] = ps["prev_minutes"].notna().astype(int)
ps["has_3yr_history"] = (ps["seasons_observed"] >= 3).astype(int)
ps["is_first_observed_season"] = (ps["seasons_observed"] == 0).astype(int)
ps["prior_gap_years"] = ps["seasons_since_prev"].fillna(0)

# "young and improving" - the recruitment archetype the project is hunting
ps["young_and_improving"] = (
    (ps["age"] <= 23) &
    (ps["delta_goal_contributions_per90"] > 0) &
    (ps["delta_minutes"] > 0)
).astype(int)

traj_cols = ([f"prev_{c}" for c in TRAJ] + [f"delta_{c}" for c in TRAJ] +
             [f"roll3_mean_{c}" for c in ["goal_contributions_per90", "minutes"]] +
             [f"roll3_std_{c}" for c in ["goal_contributions_per90", "minutes"]])

# Fill trajectory gaps with 0, flagged by the indicators above. We do NOT drop
# first-season players: dropping them would bias the sample toward established
# players and remove exactly the young talent this project is meant to surface.
n_first = int(ps["is_first_observed_season"].sum())
ps[traj_cols] = ps[traj_cols].fillna(0)

print(f"   first observed seasons (no history): {n_first:,} "
      f"({100*n_first/len(ps):.1f}%) - retained with indicator flags, not dropped")
print(f"   rows with >=3 seasons of history   : {int(ps['has_3yr_history'].sum()):,}")

for c in TRAJ:
    declare(f"prev_{c}", "performance_trajectory",
            f"{c} in the previous observed season", "ALLOWED", "1,2")
    declare(f"delta_{c}", "performance_trajectory",
            f"Change in {c} vs previous observed season", "ALLOWED", "1,2")
for c in ["goal_contributions_per90", "minutes"]:
    declare(f"roll3_mean_{c}", "performance_trajectory",
            f"Mean {c} over up to 3 PRIOR seasons", "ALLOWED", "1,2")
    declare(f"roll3_std_{c}", "performance_trajectory",
            f"Volatility of {c} over up to 3 PRIOR seasons (consistency)",
            "ALLOWED", "1,2")
declare("seasons_observed", "performance_trajectory",
        "Number of prior top-5 seasons observed for this player", "ALLOWED", "1,2")
declare("has_prior_season", "performance_trajectory",
        "Indicator: prior-season history exists", "ALLOWED", "1,2")
declare("has_3yr_history", "performance_trajectory",
        "Indicator: at least 3 prior seasons observed", "ALLOWED", "1,2")
declare("is_first_observed_season", "performance_trajectory",
        "Indicator: first observed season (trajectory features are zero-filled)",
        "ALLOWED", "1,2")
declare("prior_gap_years", "performance_trajectory",
        "Seasons elapsed since previous observed season (gap detector)",
        "ALLOWED", "1,2")
declare("young_and_improving", "performance_trajectory",
        "Indicator: age<=23 with rising output and rising minutes", "ALLOWED", "1,2")

# =============================================================================
# STEP 5 - MARKET CONTEXT
# =============================================================================
print("STEP 5: Market context")
declare("league", "context", "Domestic league (EDA: 3.3x median value spread)",
        "ALLOWED", "0,1,2")
declare("season", "context",
        "Season start year - absorbs transfer-market inflation (EDA: 2.6x drift)",
        "ALLOWED", "0,1,2")

# =============================================================================
# STEP 6 - CLUB CONTEXT: PRE-SPECIFIED, NOT SELECTED FROM THE TARGET
# =============================================================================
print("\nSTEP 6: Club context - pre-specified on managerial grounds")
print("   METHODOLOGICAL NOTE:")
print("   An earlier version of this script chose club variables by correlating")
print("   them with a FULL-SAMPLE residual from the target. That is target-informed")
print("   feature selection: the outcome influenced which predictors entered the")
print("   model. The variable itself is fine; the route to choosing it was not.")
print("   We therefore PRE-SPECIFY club context on a priori grounds below, and")
print("   report a training-period-only diagnostic purely for transparency.")

# --- A PRIORI SPECIFICATION (decided before looking at any outcome) ----------
# club_squad_size = number of distinct players the club actually used in that
# season. Managerial rationale: it proxies squad depth and the rotation
# environment a player operates in, both of which plausibly shape how a player's
# minutes and output should be read. Known at season end, no target involved.
#
# club_mean_age and club_total_minutes are NOT included in the primary
# specification: neither has a distinct managerial rationale beyond what age and
# minutes already capture at player level, and neither showed useful standalone
# structure in Phase 4 EDA.
club_keep = ["club_squad_size"]
club_drop = ["club_mean_age", "club_total_minutes"]

print(f"\n   PRE-SPECIFIED for Model 1 : {club_keep}")
print(f"   Not in primary spec       : {club_drop}")

# --- TRAINING-PERIOD-ONLY DIAGNOSTIC (reported, NOT used for selection) ------
# Restricted to seasons <= TRAIN_END so that no test-period information can
# influence anything. This is descriptive evidence for the report, not a filter.
TRAIN_END = 2021
tr = ps[ps["season"] <= TRAIN_END]
print(f"\n   Diagnostic computed on training seasons only "
      f"(<= {TRAIN_END}/{str(TRAIN_END+1)[-2:]}, n={len(tr):,}):")

base = pd.get_dummies(tr[["age", "age2", "position", "league", "season"]],
                      columns=["position", "league", "season"], drop_first=True).astype(float)
y_tr = tr["log_market_value"].values
X_tr = np.column_stack([np.ones(len(base)), base.values])
beta, *_ = np.linalg.lstsq(X_tr, y_tr, rcond=None)
resid_tr = y_tr - X_tr @ beta

audit_rows = []
for c in club_keep + club_drop:
    ok = tr[c].notna()
    r = np.corrcoef(tr.loc[ok, c], resid_tr[ok.values])[0, 1]
    audit_rows.append({
        "variable": c,
        "in_primary_specification": c in club_keep,
        "selection_basis": "a priori managerial rationale",
        "train_period_partial_corr": round(r, 4),
        "note": "diagnostic only - NOT used to select features",
    })
audit = pd.DataFrame(audit_rows)
print(audit.to_string(index=False))

declare("club_squad_size", "club_context",
        "Distinct players used by the club that season. Pre-specified on "
        "managerial grounds as a squad-depth / rotation-environment proxy. "
        "NOT selected via target-derived residuals.", "ALLOWED", "1,2")
for c in club_drop:
    declare(c, "club_context",
            f"Season-specific {c}. Excluded from the primary specification: no "
            f"distinct managerial rationale beyond player-level age and minutes, "
            f"and limited standalone structure in EDA.", "ALLOWED (not used)", "none")

# The present-day snapshot columns are formally excluded as anachronistic.
for c in ["squad_size", "average_age", "stadium_seats"]:
    declare(c, "club_context_snapshot",
            f"{c} from clubs.csv - describes the club as of the 2026 export, "
            f"not as of the season. Anachronistic.", "EXCLUDED", "none")

# =============================================================================
# STEP 7 - EXPLICIT EXCLUSIONS
# =============================================================================
declare("prior_market_value_eur", "market_derived",
        "Transfermarkt valuation before the season. Legitimate and non-leaking, "
        "but market-derived: including it makes the model re-predict the market "
        "rather than challenge it.", "ROBUSTNESS", "2")
declare("transfer_fee_eur", "outcome",
        "Observed transfer fee - a post-decision outcome, and only present for "
        "15.6% of rows (selective subset)", "EXCLUDED", "none")
declare("transfer_date", "outcome", "Date of transfer - post-decision", "EXCLUDED", "none")
declare("market_value_eur", "target", "Target variable (euros)", "TARGET", "target")
declare("log_market_value", "target", "Target variable (log euros) - primary target",
        "TARGET", "target")
declare("target_value_date", "target", "Date the target valuation was recorded",
        "EXCLUDED", "none")
declare("target_lag_days", "target",
        "Days between last match and target valuation - audit column", "EXCLUDED", "none")

# =============================================================================
# STEP 8 - ASSEMBLE THE THREE FEATURE SETS
# =============================================================================
print("\nSTEP 8: Assembling the three nested feature sets")



M0 = ["age", "age2", "position", "league", "season"]
M1 = M0 + [
    "height_in_cm", "foot",
    "minutes", "games", "goals_per90", "assists_per90",
    "goal_contributions_per90", "cards_per90", "minutes_per_game", "availability",
] + traj_cols + [
    "seasons_observed", "has_prior_season", "has_3yr_history",
    "is_first_observed_season", "prior_gap_years", "young_and_improving",
] + club_keep
M2 = M1 + ["prior_market_value_eur"]

# Model 2 needs prior value present; keep a flag rather than dropping rows.
ps["has_prior_value"] = ps["prior_market_value_eur"].notna().astype(int)
ps["prior_market_value_eur"] = ps["prior_market_value_eur"].fillna(
    ps["prior_market_value_eur"].median())
ps["log_prior_market_value"] = np.log(ps["prior_market_value_eur"])
M2 = M1 + ["log_prior_market_value", "has_prior_value"]
declare("log_prior_market_value", "market_derived",
        "Log of prior market value (median-filled where absent)", "ROBUSTNESS", "2")
declare("has_prior_value", "market_derived",
        "Indicator: prior market value was observed", "ROBUSTNESS", "2")

keep = (["player_id", "name", "season", "league", "club_name", "main_club_id",
         "position", "sub_position", "market_value_eur", "log_market_value",
         "target_value_date", "target_lag_days",
         "prior_market_value_eur", "transfer_fee_eur"]
        + [c for c in dict.fromkeys(M2) if c not in
           ("position", "league", "season")])
keep = list(dict.fromkeys([c for c in keep if c in ps.columns]))
mm = ps[keep].copy()

mm.to_csv(STAGE_OUT / "model_matrix.csv", index=False)
pd.DataFrame(feature_dict).to_csv(STAGE_OUT / "feature_dictionary.csv", index=False)
audit.to_csv(STAGE_OUT / "club_context_audit.csv", index=False)

with open(STAGE_OUT / "feature_sets.txt", "w") as f:
    f.write("MODEL 0 (market context):\n  " + ", ".join(M0) + "\n\n")
    f.write("MODEL 1 (PRIMARY - context + performance + trajectory):\n  " + ", ".join(M1) + "\n\n")
    f.write("MODEL 2 (robustness - Model 1 + prior market value):\n  " + ", ".join(M2) + "\n")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 78)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 78)

# Raw model variables vs expanded design-matrix columns after encoding.
# These are different numbers and the report must not conflate them.
def encoded_width(cols):
    sub = ps[[c for c in cols if c in ps.columns]]
    return pd.get_dummies(sub, columns=[c for c in ["position", "league", "season"]
                                        if c in sub.columns], drop_first=True).shape[1]

print(f"model_matrix.csv       : {len(mm):,} rows x {mm.shape[1]} columns")
print(f"\n{'Model':<10}{'raw variables':>16}{'encoded columns':>18}")
for nm, s in [("Model 0", M0), ("Model 1", M1), ("Model 2", M2)]:
    print(f"{nm:<10}{len(s):>16}{encoded_width(s):>18}")
print("\n  ('raw variables' counts position/league/season once each;")
print("   'encoded columns' is the actual design-matrix width after dummies.)")

print("\nDECISION POINT (defines how the tool must be described):")
print("  Features come from a COMPLETED season; the target valuation is recorded")
print("  after the player's final match. This is therefore an END-OF-SEASON")
print("  transfer-window valuation tool, not a mid-season scouting model.")

print("\nFeature dictionary by leakage class:")
print(pd.DataFrame(feature_dict)["leakage_class"].value_counts().to_string())
print("\nTrajectory coverage:")
print(f"  first observed season : {n_first:,} ({100*n_first/len(ps):.1f}%)")
print(f"  has prior season      : {int(ps['has_prior_season'].sum()):,}")
print(f"  has 3+ yr history     : {int(ps['has_3yr_history'].sum()):,}")
print(f"  young_and_improving   : {int(ps['young_and_improving'].sum()):,}")
print("=" * 78)
