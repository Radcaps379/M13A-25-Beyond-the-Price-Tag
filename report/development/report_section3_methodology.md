# Section 3 — Design and Methodology
### *Beyond the Price Tag* · IIM Ranchi · Sports Analytics (WAI)

## 3.1 Decision context and information set

The system supports one decision, made by one identifiable group of people:

> Given a fixed transfer budget and a set of positional requirements, which players should a club's recruitment and finance functions investigate as acquisition targets?

Fixing the moment at which that decision is taken governs every methodological choice that follows. The decision point is **the end of the 2024/25 season**. Everything the system uses — performance, age, position, league, valuation, trajectory — is observable at that moment. Everything used to *evaluate* the system belongs to 2025/26 and is withheld from every fitting, tuning and threshold decision.

This is a stricter standard than a train/test split. It applies to feature selection, hyperparameter choice, threshold selection, normalisation constants and eligibility screens alike. Three separate leakage defects were identified and corrected during development under this rule, each documented at the relevant subsection below.

The system is therefore an **end-of-season transfer-window valuation tool**, not a mid-season scouting model. Features are drawn from a completed season and the valuation being modelled is recorded after that season concludes.

## 3.2 Dataset and player-season construction

The analysis is built on `davidcariboo/player-scores`, a maintained export of Transfermarkt covering players, clubs, competitions, appearances, historical valuations and transfers. The dataset was downloaded once and frozen locally; because the public version refreshes weekly, working from a frozen copy is necessary for reproducibility.

**The architectural constraint governing all data assembly is that every join uses an integer identifier** (`player_id`, `club_id`). No step at any point matches players by name. This eliminates entity-resolution error as a source of silent corruption.

Two further public datasets were evaluated and **excluded on data-integrity grounds**. A pre-joined Transfermarkt + WhoScored dataset (`atakanakn`, 1,533 players × 32 variables) offers advanced metrics such as expected goals and key passes, but its only join key is player name; incorporating it would have required exactly the fuzzy matching the architecture is designed to avoid. A second Transfermarkt compilation (`kberkek00`) was retained as a contingency source but never entered the pipeline. Excluding both is a deliberate methodological choice, not an oversight.

### Construction and scope

The analysis table is at **player-season** grain, built by aggregating match-level appearances and attaching player, club and valuation attributes by ID. The frozen scope is:

| Parameter | Value |
|---|---|
| Leagues | England, Spain, Germany, Italy, France |
| Seasons | 2015/16 – 2024/25 |
| Playing-time floor | ≥ 900 league minutes per player-season |
| Information cutoff | 26 August 2026 |

### Data-quality accounting

Every filter is logged; nothing is dropped silently. The material steps:

| Step | Rule | Before | After | Dropped |
|---|---|---|---|---|
| 1b | Top-5 European leagues only | 1,894,350 | 726,823 | 1,167,527 |
| 1c | Seasons 2015/16 – 2024/25 | 726,823 | 523,349 | 203,474 |
| 1d | ≥ 900 league minutes | 26,493 | 16,045 | 10,448 |
| 2b–2c | Plausible age; known position | 16,045 | 16,035 | 10 |
| 4a | Post-season market value exists | 16,035 | 15,927 | 108 |
| 4b | Valuation strictly after last match | 15,927 | 15,925 | 2 |

**Final analysis table: 15,925 player-seasons covering 4,961 unique players.**

A separate note concerns 492 transfer records dated after the information cutoff, extending to 2030. Inspection showed these are not corrupt: they are largely pre-announced scheduled returns, a substantial block relating to a club whose players' return dates are known years in advance. They are correctly characterised as **observations outside the project's information set** and are excluded and logged, not deleted as errors.

### The transfer-fee limitation

Of 174,673 in-scope transfer records, only **10.0% carry a positive fee** (35.1% are missing, 54.9% record €0 for free transfers, loans and youth moves). Within the analysis table, 2,487 of 15,925 player-seasons (15.6%) have an observed positive fee.

This materially shapes the design. **Market value, not fee, is the primary acquisition-cost benchmark**, with observed fees used only as a secondary check. The positive-fee subset is a selective, non-representative sample of player movement and is reported as such.

An early exploratory finding reinforces the caution: across observed fees, the **median fee is 0.86× the listed market value, and only 36% of transfers exceed the valuation**. Transfermarkt valuations are therefore not a floor over which clubs bid — they sit above typical realised prices. Any definition of "overpayment" must be relative to a model benchmark, not to the listed valuation.

## 3.3 Target definition and market-level normalisation

The modelling target is the **logarithm of market value**. Exploratory analysis found raw values heavily right-skewed (skew 3.90) against an approximately symmetric log distribution (skew 0.06), with a median of €7.0M against a mean of €13.3M.

Extreme values were **deliberately not winsorised**. Inspection confirmed the highest observations are recognisable elite players, and €200M is a genuine price in the modern market. Capping would remove precisely the cases a valuation model must handle; the log transform addresses the scale.

### Target timing

The target is the first valuation recorded **strictly after the player's final match of the season**, within a 240-day window.

An earlier specification anchored the target to a fixed 1 July date. This proved to be an artefact-generating choice: Transfermarkt's bulk refreshes occur at irregular times, and the June 2017 refresh fell immediately before the window opened, collapsing 2016/17 coverage to 46% against roughly 95% elsewhere. Anchoring instead to each player's own last match raises coverage to **99.3%, stable across every season**, with a median lag of 22 days.

### Market-level normalisation

Season cannot enter the model as a dummy variable. The test season never appears in training, so every test observation silently defaults to the baseline season — against a market that inflated approximately 2.6× across the study period. This produces a severe and invisible downward bias.

Two alternatives were evaluated. A log-linear market trend fitted on training seasons **overshot the true 2024/25 level by roughly 46%**, because training-period growth was rapid early and then plateaued. The adopted approach demeans each training season by its own median and **carries the final training season's level forward** to validation and test. No realised post-training outcome enters the calibration.

Two claims are consequently reported separately:

- **R²_relative** (primary) — level-invariant: how well the model values players relative to peers within a season. The market-level constant cancels exactly.
- **R² and euro-denominated error** (deployable) — performance under the carried-forward level, representing genuine out-of-sample forecasting.

Critically, **the mispricing residual is invariant to this choice**, being a within-season quantity from which the level term cancels.

## 3.4 Feature engineering

Features fall into five groups, each documented in a feature dictionary classifying all 48 entries by leakage status (34 ALLOWED, 3 ROBUSTNESS, 7 EXCLUDED, 2 ALLOWED-but-unused, 2 TARGET).

**Player characteristics** — age, age², position, height, preferred foot. Age² is included on empirical grounds: median value peaks at 21 among ages with adequate sample and declines to roughly €1M by 34.

**Current-season performance** — minutes, appearances, goals per 90, assists per 90, combined contributions per 90, cards per 90, minutes per appearance, availability.

**Performance trajectory** — prior-season levels and changes in minutes and output, three-season rolling means and volatilities, and a `young_and_improving` indicator. Career trajectory is deliberately defined as **performance trajectory, not valuation trajectory**: a model given the market's own prior valuation largely reproduces the market's persistence rather than challenging it, which would render the residual uninterpretable as mispricing.

**Market context** — league and season. Justified empirically: league medians differ 3.3× (Premier League €15M against Ligue 1 €4.5M) and season medians shift 2.6× across the period.

**Club context** — squad size in that season, derived from appearances.

Two decisions in this group required correction during development:

*Anachronistic club variables.* The `squad_size`, `average_age` and `stadium_seats` fields in `clubs.csv` describe each club as of the 2026 export, not as of the observed season. Attaching them to a 2015/16 row injects information from a decade later. All three are formally excluded; season-specific equivalents were derived from appearances instead.

*Target-informed selection.* Club variables were initially chosen by correlating them against a full-sample residual from the target — a subtle form of outcome-influenced feature selection. Club squad size is now **pre-specified on managerial grounds** (a proxy for squad depth and rotation environment), with a training-period-only diagnostic reported for transparency but not used to select.

### Missing trajectory history

4,961 player-seasons (31.2%) are a player's first observed season and have no prior history. These are **retained**, with trajectory features zero-filled and four explicit indicator flags carried so the model can learn "no history available" as a state. Dropping them would have cost 31% of the sample and biased it toward established players — removing precisely the young talent the system exists to surface.

## 3.5 Valuation models

Three nested specifications are estimated as a research experiment rather than an algorithm contest.

| Model | Raw variables | Encoded columns | Question |
|---|---|---|---|
| **Model 0** — context benchmark | 4 | 18 | How much does age, position and league alone explain? |
| **Model 1** — fundamental valuation *(primary)* | 33 | 47 | What does observable performance and trajectory add? |
| **Model 2** — market-informed benchmark | 35 | 49 | How much easier is it when the model sees prior market value? |

Model 1 is the primary specification. Model 2 exists to quantify the difference between explaining value from fundamentals and predicting the market from its own history; its residual is not economically interpretable as mispricing.

Two algorithms are reported: **Ridge regression** as the interpretable baseline, and **scikit-learn's `HistGradientBoostingRegressor`** as the primary non-linear model. This is a histogram-based gradient-boosting implementation in the same family as LightGBM and XGBoost; it was used throughout, and all reported results derive from it. Several features are mechanically related (contributions per 90 is the sum of goals and assists per 90; minutes, appearances and minutes-per-appearance are algebraically linked), so Ridge guards against multicollinearity distorting the linear conclusion. The ridge penalty is chosen by cross-validation within the training period only.

## 3.6 Time-based validation

| Split | Seasons | n |
|---|---|---|
| Train | 2015/16 – 2021/22 | 11,173 |
| Validation | 2022/23 – 2023/24 | 3,244 |
| Test | 2024/25 | 1,508 |

All three models are scored on identical test observations. Categorical encodings and scaling are fitted on training data alone. The test season is examined once, after all specification decisions are fixed.

## 3.7 Mispricing hypothesis and back-test

The mispricing hypothesis is treated as a **falsifiable claim subjected to out-of-sample test**, not an assumed property of the system.

The residual is defined as observed log market value minus model-implied log value; a negative residual indicates the market values a player below what fundamentals imply. The back-test asks whether players flagged undervalued using only end-of-2024/25 information subsequently showed evidence of value in 2025/26.

### Sequencing discipline

1. The selection criterion was **declared in writing before any computation**: candidate thresholds of bottom 10%, 15% and 20%; selection by largest median relative-appreciation differential in the validation window; minimum 50 candidates; tie-break toward the larger threshold.
2. The threshold was chosen using validation seasons only (flag 2022/23 → outcome 2023/24).
3. The threshold was applied **once** to 2024/25 and the candidate list frozen.
4. Only then were 2025/26 outcomes examined.

### Outcome definitions, fixed in advance

**Market-value outcome** — change in log valuation, measured **relative to a position × league peer benchmark** so that market-wide inflation and positional differences are controlled. A Ligue 1 midfielder and a Premier League forward are not comparable in raw terms.

**Performance outcome** — position-appropriate metrics, requiring ≥900 minutes in 2025/26. Goal contributions are used for attackers and midfielders; availability and minutes for defenders and goalkeepers, since exploratory analysis found goal contributions correlate 0.540 with value for attackers but only 0.069 for goalkeepers.

**Candidate accounting** — every flagged player is accounted for as outcome-available, outcome-unavailable, or without top-5 minutes. No candidate is silently dropped.

## 3.8 Exit-risk model

The back-test result (Section 4.4) redirected the project toward a second modelling task: predicting whether a player records **fewer than 900 top-5 league minutes in the following season**.

This threshold is recruitment-relevant — a signing managing 200 minutes delivers no more than one who departs. The base rate is 33.5%. This definition is deliberately broader than the stricter "no top-5 minutes at all" measure used in the back-test diagnostic, and the two must not be conflated.

The specification uses player characteristics, current performance, trajectory, market value and **the calibrated mispricing residual**. Including the residual here is not recycling a failed signal: it uses the one relationship the back-test actually validated, namely that unexplained valuation gaps predict exit rather than appreciation.

Both a **logistic regression** and a boosted classifier were estimated under the same time-based split. The logistic model is the **production model**, on evidence rather than preference — it marginally outperformed the boosted challenger out of sample, so no transparency-for-accuracy trade-off was required. The boosted model is retained as a challenger.

## 3.9 Risk-aware portfolio optimisation

### Withdrawal of the original objective

The optimizer was originally specified to maximise performance-per-euro, later revised to maximise model-implied value minus acquisition cost. **The back-test rejected that objective empirically.** Maximising the residual maximises model error, and demonstrably loads the portfolio with exit risk. The objective was replaced before any optimizer was built.

### Objective function

For each eligible player *i*, with all components normalised to [0,1] **within position**:

```
RecruitmentScore_i = w₁·Quality_i + w₂·Potential_i + w₃·ValueEfficiency_i − w₄·Risk_i
```

maximising `Σ RecruitmentScore_i · x_i` over binary selection variables.

| Component | Definition |
|---|---|
| Quality | Position-appropriate performance percentile (output for attackers and midfielders; availability for defenders and goalkeepers) |
| Potential | Remaining development runway, declining linearly to zero at age 30 — three years beyond the hard recruitment ceiling of 27, so a 26-year-old retains some runway rather than scoring zero |
| ValueEfficiency | Model-implied value ÷ market value, capped at the 90th percentile of the **pre-test** distribution |
| Risk | Validated exit probability combined with segment-level model uncertainty |

**Declared weights: Quality 0.35, Potential 0.25, ValueEfficiency 0.20, Risk penalty 0.20.** These are managerial assumptions fixed in a written specification before execution, not fitted parameters. Value efficiency is deliberately not dominant, and the risk penalty is sized to match it — encoding the project's central finding that a valuation gap and its attendant risk approximately offset.

### Constraints

| Constraint | Default | Managerial meaning |
|---|---|---|
| Budget | €50M | Acquisition cost cannot exceed the transfer budget |
| Positional requirements | 1 defender, 1 midfielder, 1 attacker | The squad has specific holes |
| Performance floor | 40th percentile within position | Prevents buying cheap players merely because they are cheap |
| Exit-risk ceiling | 0.40 | Excludes players likely to leave top-5 football |
| Age ceiling | 27 | Recruitment horizon requires resale runway |
| Minimum market value | €1M | Below this is not a strategic capital decision |
| Uncertainty ceiling | 80th percentile of segment error | Prevents treating noisy estimates as confident ones |

Solved as an integer linear program via PuLP, with a greedy heuristic reported alongside so that the value added by exact optimisation is visible rather than assumed.

### Leakage correction

An initial implementation derived segment uncertainty and the value-efficiency cap from the 2024/25 sample — both requiring the realised 2024/25 valuations a club cannot observe at the decision point. Both are now **fitted on training and validation seasons only** and passed to the optimizer as fixed constants.

### Guards against arbitrary scoring

Weights declared in advance with written justification; mandatory sensitivity analysis across weight and budget grids; naive baseline portfolios reported alongside; greedy solution reported alongside the ILP; and every recommendation carrying its exit probability and confidence. All optimizer artifacts are regenerated in a single verified execution, with cross-file consistency checked before any figure is quoted.

---

## 3.10 Explainable AI

*Supplied by `report_section3_10_explainability.md`; inserted here at assembly.*

## 3.11 Generative-AI recruitment briefs

*Supplied by `report_section6_11_genai.md`; inserted here at assembly.*

## 3.12 Ethical, data and modelling safeguards

See Section 5.7 for the managerial treatment of model risk and systematic residual heterogeneity, and Appendix F for the statement on the use of artificial intelligence.
