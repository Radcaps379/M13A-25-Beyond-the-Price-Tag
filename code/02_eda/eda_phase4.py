"""
==============================================================================
PHASE 4 - EXPLORATORY DATA ANALYSIS / PRE-FEATURE VALIDATION
Project: Beyond the Price Tag
==============================================================================

PURPOSE
-------
This is NOT "make some charts". Every output below exists to settle a decision
we must make before writing the feature matrix:

  Q1  How is market value distributed?      -> do we model log value?
  Q2  How does value vary with age?         -> do we need age squared?
  Q3  How does value vary by position?      -> do we need position controls?
  Q4  Is there real performance signal?     -> are our predictors worth anything?
  Q5  Do leagues and seasons differ?        -> do we need league/season controls?
  Q6  Where does obvious mispricing sit?    -> first managerial story

  Q7  Are the extreme values real players or data errors?
      (We deliberately do NOT blindly winsorize. We look first.)

OUTPUTS
-------
  figures/*.png        report-ready charts
  eda_findings.csv     the numbers behind each decision
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
STAGE_OUT = stage_dir("eda")


import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import inspect as _inspect
# matplotlib renamed boxplot's 'labels' argument to 'tick_labels' in 3.11.
_MPL_TICKLABELS = "tick_labels" in _inspect.signature(plt.Axes.boxplot).parameters
from pathlib import Path


plt.rcParams.update({
    "figure.dpi": 130, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})
COL = "#2b6cb0"; COL2 = "#c05621"

ps = pd.read_csv(find("player_season.csv"))
findings = []


def note(question, finding, implication):
    findings.append({"question": question, "finding": finding,
                     "implication_for_modelling": implication})
    print(f"\n  Q: {question}")
    print(f"  FINDING     : {finding}")
    print(f"  IMPLICATION : {implication}")


print("=" * 78)
print(f"PHASE 4 EDA  |  {len(ps):,} player-seasons  |  {ps.player_id.nunique():,} players")
print("=" * 78)

# =============================================================================
# Q1 - DISTRIBUTION OF MARKET VALUE
# =============================================================================
print("\n" + "-" * 78); print("Q1: HOW IS MARKET VALUE DISTRIBUTED?"); print("-" * 78)

mv = ps["market_value_eur"]
skew_raw = mv.skew()
skew_log = np.log(mv).skew()

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(mv / 1e6, bins=60, color=COL, edgecolor="white", linewidth=.4)
ax[0].set_title(f"Market value (raw)\nskew = {skew_raw:.2f}")
ax[0].set_xlabel("€ million"); ax[0].set_ylabel("player-seasons")
ax[1].hist(np.log(mv), bins=60, color=COL2, edgecolor="white", linewidth=.4)
ax[1].set_title(f"Market value (log)\nskew = {skew_log:.2f}")
ax[1].set_xlabel("log(€)")
fig.suptitle("Q1  Market value is heavily right-skewed; log transform fixes it", y=1.02)
fig.tight_layout(); fig.savefig(FIG / "q1_value_distribution.png", bbox_inches="tight"); plt.close(fig)

note("Q1 Distribution of market value",
     f"raw skew {skew_raw:.2f} vs log skew {skew_log:.2f}; "
     f"median €{mv.median():,.0f}, mean €{mv.mean():,.0f}",
     "Model log(value). Mean >> median confirms a long right tail that would "
     "otherwise dominate squared-error loss.")

# =============================================================================
# Q7 - ARE THE EXTREMES REAL? (deliberately before any capping decision)
# =============================================================================
print("\n" + "-" * 78); print("Q7: ARE EXTREME VALUES REAL PLAYERS OR DATA ERRORS?"); print("-" * 78)

top = ps.nlargest(15, "market_value_eur")[
    ["name", "season", "league", "age", "position", "goals", "assists", "market_value_eur"]]
print(top.to_string(index=False))

bottom = ps.nsmallest(10, "market_value_eur")[
    ["name", "season", "league", "age", "position", "minutes", "market_value_eur"]]
print("\nLowest-valued player-seasons:")
print(bottom.to_string(index=False))

p999 = mv.quantile(0.999)
n_above = (mv > p999).sum()
note("Q7 Extreme values",
     f"top 15 are recognisable elite players (Mbappé, Yamal, Messi, Haaland...); "
     f"{n_above} rows above the 99.9th percentile (€{p999/1e6:.0f}m)",
     "DO NOT winsorize. These are genuine heavy tails, not anomalies. The log "
     "transform already handles the scale. Capping would delete exactly the "
     "elite cases a valuation model must get right.")

# =============================================================================
# Q2 - AGE
# =============================================================================
print("\n" + "-" * 78); print("Q2: HOW DOES VALUE VARY WITH AGE?"); print("-" * 78)

ps["age_int"] = ps["age"].astype(int)
band = ps[ps.age_int.between(17, 38)]
by_age = band.groupby("age_int").agg(
    median_value=("market_value_eur", "median"),
    mean_log=("log_market_value", "mean"),
    n=("player_id", "size")).reset_index()

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(by_age.age_int, by_age.median_value / 1e6, "o-", color=COL, lw=2)
ax[0].set_title("Median market value by age"); ax[0].set_xlabel("age"); ax[0].set_ylabel("€ million")
ax[1].plot(by_age.age_int, by_age.mean_log, "o-", color=COL2, lw=2)
ax[1].set_title("Mean log value by age"); ax[1].set_xlabel("age"); ax[1].set_ylabel("mean log(€)")
fig.suptitle("Q2  Value declines steeply with age — the relationship is non-linear", y=1.02)
fig.tight_layout(); fig.savefig(FIG / "q2_age_curve.png", bbox_inches="tight"); plt.close(fig)

# Only look for the peak where the sample is large enough to trust. Ages 17-18
# have 22 and 90 rows respectively - a handful of exceptional teenagers who are
# the only players that young getting 900+ top-5 minutes. Treating that as "the
# peak" would be a survivorship artifact, not a market fact.
reliable = by_age[by_age.n >= 250]
peak = reliable.loc[reliable.median_value.idxmax()]
lin = np.corrcoef(band.age, band.log_market_value)[0, 1]
note("Q2 Age",
     f"among ages with n>=250, median value peaks at {int(peak.age_int)} (€{peak.median_value/1e6:.1f}m, "
     f"n={int(peak.n)}) and falls to €{by_age[by_age.age_int==34].median_value.iloc[0]/1e6:.1f}m by 34; "
     f"linear corr(age, log value) = {lin:.2f}. Ages 17-18 show higher medians on only "
     f"{int(by_age[by_age.age_int==17].n.iloc[0])} and {int(by_age[by_age.age_int==18].n.iloc[0])} rows - "
     f"survivorship, not a real second peak",
     "Include age AND age². Note the peak sits younger than the classic 25-27 "
     "'peak performance' age because market value prices FUTURE resale potential, "
     "not just current output — a point worth making in the report.")

# =============================================================================
# Q3 - POSITION
# =============================================================================
print("\n" + "-" * 78); print("Q3: HOW DOES VALUE VARY BY POSITION?"); print("-" * 78)

by_pos = ps.groupby("position").agg(
    n=("player_id", "size"),
    median_value=("market_value_eur", "median"),
    mean_log=("log_market_value", "mean")).sort_values("median_value", ascending=False)
print(by_pos.assign(median_value=lambda d: d.median_value.map("{:,.0f}".format)).to_string())

fig, ax = plt.subplots(figsize=(7, 4))
order = by_pos.index.tolist()
ax.boxplot([np.log(ps.loc[ps.position == p, "market_value_eur"]) for p in order],
           **({"tick_labels": order} if _MPL_TICKLABELS else {"labels": order}), showfliers=False, patch_artist=True,
           boxprops=dict(facecolor="#bee3f8", edgecolor=COL),
           medianprops=dict(color=COL2, lw=2))
ax.set_ylabel("log market value (€)")
ax.set_title("Q3  Value differs systematically by position")
fig.tight_layout(); fig.savefig(FIG / "q3_position.png", bbox_inches="tight"); plt.close(fig)

spread = by_pos.median_value.max() / by_pos.median_value.min()
note("Q3 Position",
     f"median value ranges {spread:.1f}x across positions "
     f"(highest {by_pos.index[0]} €{by_pos.median_value.iloc[0]/1e6:.1f}m, "
     f"lowest {by_pos.index[-1]} €{by_pos.median_value.iloc[-1]/1e6:.1f}m)",
     "Position controls are required. Goalkeepers especially cannot share a "
     "goals-based value function with attackers.")

# =============================================================================
# Q4 - PERFORMANCE SIGNAL (and the position-confound warning)
# =============================================================================
print("\n" + "-" * 78); print("Q4: IS THERE REAL PERFORMANCE SIGNAL?"); print("-" * 78)

perf = ["minutes", "games", "goals_per90", "assists_per90",
        "goal_contributions_per90", "cards_per90", "minutes_per_game"]

print("\nCorrelation with log market value:")
rows = []
overall = {c: ps[c].corr(ps.log_market_value) for c in perf}
for c in perf:
    r = {"metric": c, "ALL": overall[c]}
    for p in ["Attack", "Midfield", "Defender", "Goalkeeper"]:
        sub = ps[ps.position == p]
        r[p] = sub[c].corr(sub.log_market_value)
    rows.append(r)
corr_tab = pd.DataFrame(rows).set_index("metric").round(3)
print(corr_tab.to_string())

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].scatter(ps.goal_contributions_per90, ps.log_market_value, s=3, alpha=.12, color=COL)
ax[0].set_xlim(0, 1.5); ax[0].set_xlabel("goals + assists per 90")
ax[0].set_ylabel("log market value"); ax[0].set_title("Output vs value (all positions)")
for p, c in zip(["Attack", "Midfield", "Defender", "Goalkeeper"],
                ["#c05621", "#2b6cb0", "#2f855a", "#805ad5"]):
    s = ps[ps.position == p]
    ax[1].scatter(s.minutes, s.log_market_value, s=3, alpha=.15, color=c, label=p)
ax[1].set_xlabel("league minutes played"); ax[1].set_title("Minutes vs value, by position")
ax[1].legend(markerscale=4, fontsize=8, frameon=False)
fig.suptitle("Q4  Predictors carry signal, but it is position-dependent", y=1.02)
fig.tight_layout(); fig.savefig(FIG / "q4_performance_signal.png", bbox_inches="tight"); plt.close(fig)

note("Q4 Performance signal",
     f"minutes r={overall['minutes']:.2f}, contributions/90 r={overall['goal_contributions_per90']:.2f} "
     f"overall; but contributions/90 is r={corr_tab.loc['goal_contributions_per90','Goalkeeper']:.2f} "
     f"for goalkeepers vs r={corr_tab.loc['goal_contributions_per90','Attack']:.2f} for attackers",
     "Predictors do contain signal. Correlations are modest, which is expected "
     "and healthy — if performance explained value almost perfectly there would "
     "be no mispricing to find. Position-specific behaviour confirms we need "
     "position interactions or a tree model that finds them automatically.")

# =============================================================================
# Q5 - LEAGUE AND SEASON
# =============================================================================
print("\n" + "-" * 78); print("Q5: DO LEAGUES AND SEASONS DIFFER?"); print("-" * 78)

by_lg = ps.groupby("league").agg(n=("player_id", "size"),
                                 median_value=("market_value_eur", "median")
                                 ).sort_values("median_value", ascending=False)
print(by_lg.assign(median_value=lambda d: d.median_value.map("{:,.0f}".format)).to_string())

by_se = ps.groupby("season").agg(median_value=("market_value_eur", "median"),
                                 mean_log=("log_market_value", "mean")).reset_index()
print("\nBy season:")
print(by_se.assign(median_value=lambda d: d.median_value.map("{:,.0f}".format)).to_string(index=False))

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].barh(by_lg.index, by_lg.median_value / 1e6, color=COL)
ax[0].set_xlabel("median € million"); ax[0].set_title("Median value by league")
ax[1].plot(by_se.season, by_se.median_value / 1e6, "o-", color=COL2, lw=2)
ax[1].set_xlabel("season (start year)"); ax[1].set_ylabel("median € million")
ax[1].set_title("Median value by season")
fig.suptitle("Q5  League and season both shift the value scale", y=1.02)
fig.tight_layout(); fig.savefig(FIG / "q5_league_season.png", bbox_inches="tight"); plt.close(fig)

lg_ratio = by_lg.median_value.max() / by_lg.median_value.min()
covid_dip = by_se.set_index("season").median_value
note("Q5 League & season",
     f"league medians differ {lg_ratio:.1f}x (PL €{by_lg.median_value.iloc[0]/1e6:.1f}m vs "
     f"{by_lg.index[-1]} €{by_lg.median_value.iloc[-1]/1e6:.1f}m); season median moves from "
     f"€{covid_dip.loc[2015]/1e6:.1f}m (2015/16) to €{covid_dip.loc[2024]/1e6:.1f}m (2024/25)",
     "Both league and season must be controls. Season also captures transfer-market "
     "inflation and the COVID valuation shock — a €20m player in 2016 is not a "
     "€20m player in 2024, so time-based validation must respect this.")

# =============================================================================
# Q6 - FIRST LOOK AT MISPRICING (naive, pre-model)
# =============================================================================
print("\n" + "-" * 78); print("Q6: WHERE DOES CANDIDATE MISPRICING SIT?"); print("-" * 78)

# Naive peer benchmark: median log value of same position x season x age band.
ps["age_band"] = pd.cut(ps.age, [15, 21, 24, 27, 30, 46],
                        labels=["<=21", "22-24", "25-27", "28-30", "31+"])
ps["peer_median_log"] = ps.groupby(
    ["position", "season", "age_band"], observed=True)["log_market_value"].transform("median")
ps["naive_gap"] = ps["log_market_value"] - ps["peer_median_log"]

# Among high-output players, who sits below their peer benchmark?
hi = ps[(ps.goal_contributions_per90 > ps.goal_contributions_per90.quantile(.80)) &
        (ps.minutes >= 1500)]
cands = hi.nsmallest(12, "naive_gap")[
    ["name", "season", "league", "age", "position", "minutes",
     "goal_contributions_per90", "market_value_eur", "naive_gap"]]
mean_gap = cands["naive_gap"].mean()
print("High output but valued below positional/age/season peers:")
print(cands.drop(columns=["naive_gap"]).assign(market_value_eur=lambda d: d.market_value_eur.map("{:,.0f}".format),
                   goal_contributions_per90=lambda d: d.goal_contributions_per90.round(2),
                   age=lambda d: d.age.round(1)).to_string(index=False))

fee = ps[ps.transfer_fee_eur.notna()].copy()
fee["fee_to_value"] = fee.transfer_fee_eur / fee.market_value_eur
note("Q6 Candidate mispricing",
     f"a naive peer benchmark isolates high-output players sitting {abs(mean_gap):.2f} log points "
     f"(~{100*(1-np.exp(mean_gap)):.0f}%) below their position/age/season peers; "
     f"{len(fee):,} rows carry an observed fee, median fee/value ratio {fee.fee_to_value.median():.2f}, "
     f"with {100*(fee.fee_to_value>1).mean():.0f}% of fees exceeding the listed valuation",
     "Signal exists even before modelling. NOTE the fee finding runs opposite to the "
     "common assumption: the median fee is BELOW the listed market value (0.86x), not "
     "above it — only 36% of transfers exceed the valuation. Transfermarkt valuations "
     "are therefore not a floor that clubs bid over; they sit above typical realised "
     "prices. This materially affects how we frame 'overpayment' in the report.")

# =============================================================================
# SAVE
# =============================================================================
pd.DataFrame(findings).to_csv(STAGE_OUT / "eda_findings.csv", index=False)
corr_tab.to_csv(STAGE_OUT / "eda_correlations.csv")

print("\n" + "=" * 78)
print("EDA COMPLETE")
print("=" * 78)
print(f"figures written to {FIG}/  (5 charts)")
print(f"findings written to {PROC/'eda_findings.csv'}")
