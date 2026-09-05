"""
==============================================================================
PHASE 3 - BUILD THE PLAYER-SEASON ANALYSIS TABLE
Project: Beyond the Price Tag
==============================================================================

WHAT THIS SCRIPT DOES, IN PLAIN ENGLISH
---------------------------------------
It takes the raw Transfermarkt CSVs and produces ONE clean table where each row
is "one player, in one season". That single table is what every later stage of
the project (model, mispricing, optimizer, SHAP, back-test) will read.

Every join below uses an INTEGER ID (player_id / club_id). There is no step
anywhere that matches players by name. That is deliberate and non-negotiable.

FROZEN SCOPE (agreed before writing this)
-----------------------------------------
  Leagues        : England, Spain, Germany, Italy, France (top 5)
  Seasons        : 2015/16 through 2024/25
  Minimum time   : >= 900 league minutes in the season
  Info cutoff    : 26 August 2026 - nothing dated after this is used
  Target         : model-implied market value (Transfermarkt value after season)
  Cost proxy     : Transfermarkt market value
  Actual fees    : secondary check, only where a positive fee exists

HOW TO READ THE OUTPUT
----------------------
The script prints a numbered STEP for each stage and writes a data-quality log
showing how many rows each rule removed. Nothing is deleted silently.

OUTPUTS
-------
  player_season.csv        the analysis table
  data_quality_log.csv     every filter, and how many rows it dropped
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

# -----------------------------------------------------------------------------
# CONFIGURATION - every judgement call is here, in one place, easy to change
# -----------------------------------------------------------------------------


# The five leagues. These are Transfermarkt's competition codes.
TOP5 = {
    "GB1": "England - Premier League",
    "ES1": "Spain - LaLiga",
    "L1":  "Germany - Bundesliga",
    "IT1": "Italy - Serie A",
    "FR1": "France - Ligue 1",
}

# Season 2015 means the 2015/16 season. We model 2015/16 .. 2024/25 inclusive.
SEASON_MIN, SEASON_MAX = 2015, 2024

MIN_MINUTES = 900          # a player must play at least this much to be included
INFO_CUTOFF = pd.Timestamp("2026-08-26")   # our information cutoff

# How long after a player's LAST MATCH we allow the target valuation to be taken.
#
# WHY ANCHOR ON THE LAST MATCH RATHER THAN A FIXED CALENDAR DATE:
# Transfermarkt runs its bulk valuation refreshes at irregular times - some
# years in June, some in July, some in December. An earlier version of this
# script anchored on 1 July, which happened to sit just AFTER the June 2017
# refresh, so the 2016/17 season lost half its rows for no real-world reason
# (coverage fell to 46% that season vs ~95% elsewhere). Anchoring on each
# player's own last match removes that artifact: coverage is now 99%+ and
# stable in every season.
#
# Time-awareness is preserved: the valuation is always taken strictly AFTER
# the last match of the season we draw performance from.
TARGET_WINDOW_DAYS = 240

quality_log = []   # collects (step, rule, rows_before, rows_after, dropped)


def log(step, rule, before, after):
    """Record what a filter did so nothing is dropped silently."""
    quality_log.append({
        "step": step,
        "rule": rule,
        "rows_before": before,
        "rows_after": after,
        "rows_dropped": before - after,
        "pct_dropped": round(100 * (before - after) / before, 2) if before else 0,
    })
    print(f"   [{step}] {rule}")
    print(f"        {before:,} -> {after:,}  (dropped {before-after:,})")


def season_of(dates):
    """
    Turn a match date into a season label.
    Football seasons run Aug-May, so anything from July onward belongs to the
    season that STARTS that calendar year. July 2015 - June 2016 => season 2015.
    """
    return np.where(dates.dt.month >= 7, dates.dt.year, dates.dt.year - 1)


print("=" * 78)
print("PHASE 3 - BUILDING PLAYER-SEASON TABLE")
print("=" * 78)

# =============================================================================
# STEP 1 - APPEARANCES -> per-season performance totals
# =============================================================================
print("\nSTEP 1: Aggregating match appearances into season totals")

app = pd.read_csv(RAW / "appearances.csv", low_memory=False)
n0 = len(app)
print(f"   loaded appearances.csv: {n0:,} rows")

app["date"] = pd.to_datetime(app["date"], errors="coerce")

# Drop anything after our information cutoff.
before = len(app)
app = app[app["date"] <= INFO_CUTOFF]
log("1a", f"appearances on/before info cutoff {INFO_CUTOFF.date()}", before, len(app))

# Keep only the five leagues in scope.
before = len(app)
app = app[app["competition_id"].isin(TOP5.keys())]
log("1b", "keep top-5 European leagues only", before, len(app))

# Label each match with its season, then keep the seasons in scope.
app["season"] = season_of(app["date"])
before = len(app)
app = app[(app["season"] >= SEASON_MIN) & (app["season"] <= SEASON_MAX)]
log("1c", f"keep seasons {SEASON_MIN}/16 .. {SEASON_MAX}/25", before, len(app))

# Now collapse many matches into one row per player-season.
ps = (app.groupby(["player_id", "season"])
         .agg(games=("game_id", "nunique"),
              minutes=("minutes_played", "sum"),
              goals=("goals", "sum"),
              assists=("assists", "sum"),
              yellow_cards=("yellow_cards", "sum"),
              red_cards=("red_cards", "sum"),
              main_competition=("competition_id",
                                lambda s: s.value_counts().index[0]),
              main_club_id=("player_club_id",
                            lambda s: s.value_counts().index[0]),
              season_start=("date", "min"),
              season_end=("date", "max"))
         .reset_index())
print(f"   -> {len(ps):,} player-season rows created")

# Playing-time filter: too few minutes means the performance numbers are noise.
before = len(ps)
ps = ps[ps["minutes"] >= MIN_MINUTES]
log("1d", f"require >= {MIN_MINUTES} league minutes in the season", before, len(ps))

# =============================================================================
# STEP 2 - PLAYER ATTRIBUTES (joined on player_id)
# =============================================================================
print("\nSTEP 2: Attaching player attributes (age, position, foot, height)")

players = pd.read_csv(RAW / "players.csv", low_memory=False)
players["date_of_birth"] = pd.to_datetime(players["date_of_birth"], errors="coerce")

keep_cols = ["player_id", "date_of_birth", "position", "sub_position",
             "foot", "height_in_cm", "country_of_citizenship", "name"]

before = len(ps)
ps = ps.merge(players[keep_cols], on="player_id", how="left")   # <-- integer ID join
log("2a", "join players.csv on player_id", before, len(ps))

# Age measured at 1 January inside the season - a fixed, consistent reference.
ref = pd.to_datetime((ps["season"] + 1).astype(str) + "-01-01")
ps["age"] = (ref - ps["date_of_birth"]).dt.days / 365.25

before = len(ps)
ps = ps[ps["age"].between(15, 45)]     # removes rows with missing/absurd DOB
log("2b", "require a plausible age (15-45)", before, len(ps))

before = len(ps)
ps = ps[ps["position"].notna() & (ps["position"] != "Missing")]
log("2c", "require a known position", before, len(ps))

# =============================================================================
# STEP 3 - CLUB AND LEAGUE CONTEXT (joined on club_id)
# =============================================================================
print("\nSTEP 3: Attaching club context")

clubs = pd.read_csv(RAW / "clubs.csv", low_memory=False)
club_cols = clubs[["club_id", "name", "domestic_competition_id",
                   "squad_size", "average_age", "stadium_seats"]].copy()
club_cols = club_cols.rename(columns={"name": "club_name",
                                      "club_id": "main_club_id"})

before = len(ps)
ps = ps.merge(club_cols, on="main_club_id", how="left")          # <-- integer ID join
log("3a", "join clubs.csv on club_id", before, len(ps))

ps["league"] = ps["main_competition"].map(TOP5)

# =============================================================================
# STEP 4 - THE TARGET: market value measured AFTER the season finishes
# =============================================================================
print("\nSTEP 4: Attaching the target (post-season market value)")
print("   Time-awareness rule: performance comes from the season just played;")
print("   the value we predict is recorded AFTER that season ends. No overlap.")

val = pd.read_csv(RAW / "player_valuations.csv", low_memory=False)
val["date"] = pd.to_datetime(val["date"], errors="coerce")
val = val[val["date"] <= INFO_CUTOFF]
val = val[["player_id", "date", "market_value_in_eur"]].dropna()

# --- 4a. TARGET: first valuation recorded AFTER the player's last match -------
#
# IMPORTANT IMPLEMENTATION NOTE:
# merge_asof returns rows in left-frame order, so it is tempting to write the
# result back with `.values`. Do NOT do that here. season_end has thousands of
# tied dates, and pandas' default sort is not stable, so sorting twice can order
# those ties differently and silently attach each player's value to a DIFFERENT
# player's row. An earlier version of this script did exactly that and produced
# nonsense (squad players valued at EUR 200m, and a completely flat age curve).
# We therefore carry the join keys through and merge on keys, never on position.

v_sorted = val.sort_values("date", kind="mergesort")

asof_left = (ps[["player_id", "season", "season_end"]]
             .sort_values("season_end", kind="mergesort"))

tgt = pd.merge_asof(
    asof_left,
    v_sorted.rename(columns={"date": "target_value_date",
                             "market_value_in_eur": "market_value_eur"}),
    left_on="season_end", right_on="target_value_date",
    by="player_id", direction="forward",
    tolerance=pd.Timedelta(days=TARGET_WINDOW_DAYS),
)

# merge back on the (player_id, season) key - safe regardless of row order
ps = ps.merge(
    tgt[["player_id", "season", "target_value_date", "market_value_eur"]],
    on=["player_id", "season"], how="left",
)

# How long after the last match the valuation was recorded. Kept as a column so
# the gap is auditable and can be tightened later if a reviewer asks.
ps["target_lag_days"] = (ps["target_value_date"] - ps["season_end"]).dt.days

# --- 4b. PRIOR VALUE: last valuation BEFORE the season started ---------------
# NOTE: this is stored for reference and for the trajectory-variant model only.
# It is deliberately EXCLUDED from the primary mispricing model, because a model
# fed the market's own prior number largely re-predicts the market instead of
# challenging it.
ps["season_open"] = pd.to_datetime(ps["season"].astype(str) + "-07-01")

prior_left = (ps[["player_id", "season", "season_open"]]
              .sort_values("season_open", kind="mergesort"))

prior = pd.merge_asof(
    prior_left,
    v_sorted.rename(columns={"date": "prior_value_date",
                             "market_value_in_eur": "prior_market_value_eur"}),
    left_on="season_open", right_on="prior_value_date",
    by="player_id", direction="backward",
    tolerance=pd.Timedelta(days=365),
)

# again: merge on keys, never positionally
ps = ps.merge(
    prior[["player_id", "season", "prior_market_value_eur"]],
    on=["player_id", "season"], how="left",
)

before = len(ps)
ps = ps[ps["market_value_eur"].notna() & (ps["market_value_eur"] > 0)]
log("4a", "require a post-season market value (the target)", before, len(ps))

# The valuation must be dated STRICTLY AFTER the last match. If it falls on the
# same day we cannot tell whether it was recorded before or after that match, so
# time-awareness is ambiguous. Only a couple of rows, but it lets the report
# state the rule without a caveat.
before = len(ps)
ps = ps[ps["target_lag_days"] > 0]
log("4b", "target valuation strictly after last match (lag > 0 days)", before, len(ps))

# =============================================================================
# STEP 5 - ACTUAL TRANSFER FEES (secondary benchmark only)
# =============================================================================
print("\nSTEP 5: Attaching actual transfer fees where a positive fee exists")
print("   Reminder: only ~10% of transfer rows carry a positive fee, so this")
print("   is a SELECTIVE subset - a secondary check, never the main sample.")

tr = pd.read_csv(RAW / "transfers.csv", low_memory=False)
tr["transfer_date"] = pd.to_datetime(tr["transfer_date"], errors="coerce")

n_future = (tr["transfer_date"] > INFO_CUTOFF).sum()
print(f"   post-cutoff transfer rows excluded from analysis: {n_future:,}")
quality_log.append({
    "step": "5a", "rule": f"transfers dated after {INFO_CUTOFF.date()} excluded "
                          f"(outside information set, not corrupt)",
    "rows_before": len(tr), "rows_after": len(tr) - n_future,
    "rows_dropped": int(n_future),
    "pct_dropped": round(100 * n_future / len(tr), 2),
})

tr = tr[tr["transfer_date"] <= INFO_CUTOFF]
tr_fee = tr[tr["transfer_fee"].notna() & (tr["transfer_fee"] > 0)].copy()
print(f"   transfers with a positive fee: {len(tr_fee):,} of {len(tr):,} "
      f"({100*len(tr_fee)/len(tr):.1f}%)")

# A transfer belongs to the summer window following season S.
tr_fee["transfer_season"] = season_of(tr_fee["transfer_date"])
fee = (tr_fee.groupby(["player_id", "transfer_season"])
             .agg(transfer_fee_eur=("transfer_fee", "max"),
                  transfer_date=("transfer_date", "max"))
             .reset_index()
             .rename(columns={"transfer_season": "season"}))

before = len(ps)
ps = ps.merge(fee, on=["player_id", "season"], how="left")   # <-- integer ID join
log("5b", "left-join positive transfer fees (does not drop rows)", before, len(ps))
print(f"   player-seasons with an observed positive fee: "
      f"{ps['transfer_fee_eur'].notna().sum():,}")

# =============================================================================
# STEP 6 - BASIC DERIVED COLUMNS
# =============================================================================
print("\nSTEP 6: Adding per-90 rates and simple derived fields")

p90 = ps["minutes"] / 90.0
ps["goals_per90"] = ps["goals"] / p90
ps["assists_per90"] = ps["assists"] / p90
ps["goal_contributions_per90"] = (ps["goals"] + ps["assists"]) / p90
ps["cards_per90"] = (ps["yellow_cards"] + ps["red_cards"]) / p90
ps["minutes_per_game"] = ps["minutes"] / ps["games"]
ps["log_market_value"] = np.log(ps["market_value_eur"])

# =============================================================================
# STEP 7 - SAVE
# =============================================================================
print("\nSTEP 7: Writing outputs")

final_cols = [
    "player_id", "name", "season", "league", "main_competition",
    "main_club_id", "club_name",
    "age", "position", "sub_position", "foot", "height_in_cm",
    "country_of_citizenship",
    "games", "minutes", "minutes_per_game",
    "goals", "assists", "yellow_cards", "red_cards",
    "goals_per90", "assists_per90", "goal_contributions_per90", "cards_per90",
    "squad_size", "average_age", "stadium_seats",
    "market_value_eur", "log_market_value", "target_value_date", "target_lag_days",
    "prior_market_value_eur",
    "transfer_fee_eur", "transfer_date",
]
ps_out = ps[final_cols].sort_values(["season", "player_id"]).reset_index(drop=True)

ps_out.to_csv(STAGE_OUT / "player_season.csv", index=False)
pd.DataFrame(quality_log).to_csv(STAGE_OUT / "data_quality_log.csv", index=False)

print(f"   wrote {OUT/'player_season.csv'}   ({len(ps_out):,} rows)")
print(f"   wrote {OUT/'data_quality_log.csv'}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 78)
print("SUMMARY OF THE ANALYSIS TABLE")
print("=" * 78)
print(f"Rows (player-seasons) : {len(ps_out):,}")
print(f"Unique players        : {ps_out['player_id'].nunique():,}")
print(f"Seasons               : {ps_out['season'].min()}/16 .. {ps_out['season'].max()}/25")
print("\nRows per season:")
print(ps_out.groupby("season").size().to_string())
print("\nRows per league:")
print(ps_out.groupby("league").size().to_string())
print("\nRows per position:")
print(ps_out.groupby("position").size().to_string())
print("\nMarket value (EUR):")
print(ps_out["market_value_eur"].describe().apply(lambda x: f"{x:,.0f}").to_string())
print("\nMissingness in key columns (%):")
key = ["age", "position", "minutes", "market_value_eur",
       "prior_market_value_eur", "transfer_fee_eur", "height_in_cm", "foot"]
print((ps_out[key].isna().mean() * 100).round(1).to_string())
print("=" * 78)
