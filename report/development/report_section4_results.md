# Section 4 — Results and Discussion
### *Beyond the Price Tag* · IIM Ranchi · Sports Analytics (WAI)

## 4.1 Result 1 — Football market valuation is highly structured

Before any model was fitted, exploratory analysis established that market value varies systematically along four dimensions. Each finding determined a specific modelling decision rather than merely describing the data.

**Distribution.** Raw market value is heavily right-skewed (skew 3.90); the log transform is approximately symmetric (skew 0.06). Median €7.0M against mean €13.3M confirms a long right tail that would otherwise dominate squared-error loss. *Decision: model log value.*

**Age.** Median value peaks at 21 (€12.0M, n=798) and declines to approximately €1.0M by 34. The relationship is markedly non-linear. *Decision: include age².*

An instructive detail: an initial reading placed the peak at 17. That figure rested on 22 observations — the only players young enough and good enough to accumulate 900 top-5 minutes. Restricting attention to ages with adequate sample corrects the peak to 21. The episode illustrates why sample size must be inspected alongside any summary statistic.

The peak nonetheless sits younger than the conventional 25–27 performance peak. This is not an error but a substantive finding: **market value prices future resale potential, not only current output.**

**Position.** Median values differ 1.8× across positions. *Decision: position controls are mandatory.*

**League and season.** League medians differ 3.3× (Premier League €15.0M against Ligue 1 €4.5M); season medians shift 2.6× across the period. *Decision: both are mandatory controls, and validation must be strictly time-based.*

## 4.2 Result 2 — Observable fundamentals explain a substantial share of valuation

| Model | Raw variables | R²_relative | R² (deployable) | Median % error | MAE |
|---|---|---|---|---|---|
| Model 0 — context benchmark | 4 | 0.383 | 0.375 | 57.5% | €10.72M |
| **Model 1 — fundamental (HistGradientBoosting)** | **33** | **0.678** | **0.677** | **43.9%** | **€7.60M** |
| Model 1 — fundamental (Ridge) | 33 | 0.672 | 0.671 | 44.2% | €7.64M |

*Held-out 2024/25 season, n = 1,508, identical observations across all models.*

Adding observable performance and trajectory raises explanatory power from 0.383 to 0.678 — the project's substantive positive finding. **Observable football information carries real valuation signal.**

The correct formulation is: *on the held-out 2024/25 sample, Model 1 achieves R² = 0.678 in the season-normalised valuation framework.* The stronger claim that the model "explains 67.8% of player value" is not supported, since Transfermarkt market value is itself an estimate rather than an objective price.

Ridge and OLS agree to three decimal places, confirming that the mechanical relationships among per-90 and minutes-based features do not materially alter the linear conclusion.

### Error is not uniformly distributed

| Dimension | Segment | n | Median % error | R² |
|---|---|---|---|---|
| Position | Attack | 379 | 37.3% | 0.768 |
| | Goalkeeper | 114 | 40.5% | 0.588 |
| League | England | 315 | 35.1% | 0.637 |
| | Spain | 329 | 55.9% | 0.615 |
| Age | ≤21 | 98 | 52.3% | **0.104** |
| | 25–27 | 417 | 40.4% | 0.621 |

Two segments deserve emphasis. Spanish valuations are markedly harder to model than English ones. More consequentially, **the model performs worst on players aged 21 and under (R² = 0.104)** — the segment in which the system therefore provides the least reliable valuation signal. This heterogeneity is the direct justification for the uncertainty constraint in the optimizer, and it is reported rather than concealed.

## 4.3 Result 3 — Prior market beliefs explain considerably more

| Model | R²_relative | Median % error | MAE |
|---|---|---|---|
| Model 1 — fundamentals only | 0.678 | 43.9% | €7.60M |
| **Model 2 — plus prior market value** | **0.884** | **23.7%** | **€4.47M** |

Adding a single market-derived variable — the player's own prior valuation — raises R² by 0.206. Twenty-nine performance and trajectory features contributed 0.295; two market-derived features contribute more than two-thirds of that. Prior log market value correlates 0.835 with the target, nearly double the strongest legitimate fundamental feature (age², 0.451).

The interpretation is the project's first major insight:

> **Predicting the market is substantially easier than explaining it.** Transfermarkt valuations are highly persistent, and a model permitted to observe prior valuations largely reproduces that persistence.

This is why Model 1 remains the primary specification despite lower accuracy. Model 2's residual measures deviation from Transfermarkt's own trend, which carries no economic interpretation as mispricing. **Accuracy and economic usefulness are different objectives**, and a project optimising the former would have selected the wrong model.

## 4.4 Result 4 — The mispricing hypothesis fails out of sample

This is a core research finding and is reported as such rather than minimised.

| Signal | Candidates with outcome | Median relative appreciation | Difference vs benchmark | p (one-sided) |
|---|---|---|---|---|
| Raw residual (pre-registered) | 110 | +0.034 | +0.034 | 0.094 |
| Calibrated + screened | 128 | +0.154 | **0.000** | 0.307 |
| Eligible benchmark | 591 | +0.154 | — | — |

Neither specification produced a statistically significant subsequent appreciation advantage. The validation window had shown a small positive differential (+0.042) that **did not replicate** on the test season — the characteristic signature of a signal that was noise.

> **The out-of-sample evidence does not support the hypothesis that the model residual identifies systematically exploitable transfer-market mispricing.**

Deliberately, no third signal was constructed. Iterating specifications until one reached significance would have invalidated the entire testing procedure; the discipline that makes a negative result meaningful is the willingness to accept it.

### Why the raw signal failed

Diagnosis was unambiguous. The residual correlates **+0.667 with log market value**: it is substantially a function of how cheap a player already is. Because the model regresses toward the mean in log space, it over-predicts low-valued players, who are then flagged as "undervalued."

| | Flagged | Benchmark |
|---|---|---|
| Median market value | €2.0M | €11.0M |
| Median age | 28.8 | 26.0 |
| No top-5 minutes following season | **39.7%** | 13.6% |

The raw signal identified **cheap, ageing players departing top-flight football** — players who are inexpensive for reasons the model cannot observe.

## 4.5 Result 5 — The residual instead carries recruitment-risk information

The same diagnostic that invalidated the appreciation hypothesis revealed a far stronger relationship in the opposite direction.

Players flagged by the refined signal left top-5 football entirely at **3.7× the rate** of the eligible benchmark the following season — 30.1% against 8.2% (Fisher exact, odds ratio 4.82, **p = 2.6 × 10⁻¹¹**). This relationship provides substantially stronger statistical evidence than either appreciation test, and it survived both signal specifications.

The managerial interpretation:

> When a player's observed valuation sits substantially below what observable performance fundamentals imply, the discrepancy more often reflects information the market holds and public match statistics do not, than an exploitable error.

Contract situation, injury history, role change, off-field circumstances and impending movement below top-flight level are **plausible hypotheses**, not findings from this data, and are labelled accordingly.

The practical consequence reframes the entire system:

> **A large unexplained valuation gap should trigger investigation, not an automatic bid.**

### An exploratory conditional observation

Among flagged players who remained in top-5 football with ≥900 minutes, the flagged group did appreciate more strongly than the benchmark (+0.242 against +0.182, p = 0.048).

This is reported as **exploratory only**. Conditioning on survival is post-outcome selection: a club cannot know at the decision point which players will still be playing a year later. It is not evidence of an investable strategy and does not enter the optimizer.

## 4.6 Result 6 — Exit risk is itself predictable

The negative result becomes a validated decision-support component.

| Model | Split | n | AUC | Brier |
|---|---|---|---|---|
| **Logistic (production)** | Validation | 3,244 | 0.7362 | 0.1932 |
| **Logistic (production)** | **Test** | **1,508** | **0.7323** | **0.1861** |
| HistGradientBoosting (challenger) | Test | 1,508 | 0.7283 | 0.1864 |

The interpretable model marginally **outperformed** the non-linear challenger out of sample, so the project faced no transparency-versus-accuracy trade-off in this task — a point worth stating explicitly, since such trade-offs are usually assumed.

Calibration is strong across the risk distribution:

| Risk decile | Predicted exit | Actual exit |
|---|---|---|
| 0 (lowest) | 5.2% | 7.3% |
| 4 | 23.0% | 30.5% |
| 9 (highest) | 69.6% | 69.5% |

A **9.5× spread** between lowest and highest decile, with predicted and actual converging closely at the extremes. The model both discriminates and is calibrated well enough for its outputs to be used as probabilities in a decision rule.

## 4.7 Result 7 — Risk-aware allocation changes the recommendation

Applying the optimizer under a €50M budget with one defender, one midfielder and one attacker required:

| Player | Position | League | Age | Market | Model-implied | Exit risk |
|---|---|---|---|---|---|---|
| Lucas Stassin | Attack | Ligue 1 | 20.1 | €18M | €31.1M | 14% |
| Diego Coppola | Defender | Serie A | 21.0 | €10M | €27.1M | 13% |
| Facundo Buonanotte | Midfield | Premier League | 20.0 | €20M | €20.3M | 25% |

**€48M of €50M · mean quality percentile 88 · mean predicted exit risk 17.1%**

### Comparison against naive strategies

| Portfolio | Spend | Mean quality percentile | Predicted exit risk | Mean age |
|---|---|---|---|---|
| **Risk-aware (recommended)** | €48M | 88 | 17.1% | 20.4 |
| Largest valuation gap *(rejected objective)* | €7M | 69 | 49.3% | 26.5 |
| Cheapest meeting positional needs | €3M | 70 | 66.4% | 35.5 |

The contrast is instructive. The cheapest feasible portfolio has a mean age of **35.5** and a predicted exit risk of 66.4% — it is not a recruitment strategy but a demonstration of what naive value-hunting selects. The rejected valuation-gap objective performs better but still carries nearly three times the exit risk of the risk-aware portfolio at materially lower quality.

### What this comparison does and does not establish

The illustration must not be overstated. Realised 2025/26 outcomes for these three-player portfolios involve two players versus one and **cannot establish effectiveness at n = 3**.

> **The exit-risk model is validated at the population level (AUC 0.732, n = 1,508). The portfolio is an illustrative application of that validated model, not an out-of-sample validation sample for the optimizer.**

### Sensitivity

Across six weight configurations, **Lucas Stassin appears in all six**, Diego Coppola in four, and Facundo Buonanotte in three. The honest characterisation is **meaningful stability rather than complete invariance**: the core recommendation persists while the remainder of the portfolio shifts with the relative emphasis placed on quality, potential, affordability and risk.

Budget sensitivity reveals a further property. Recommended spend plateaus at approximately €52M, with identical portfolios returned at €75M and €100M:

> Under the model's eligibility constraints, increasing the nominal budget beyond roughly €75M does not translate into a larger or higher-scoring recommended portfolio.

This is a property of the model and its eligibility universe — not evidence that real clubs face a €52M optimal ceiling.

## 4.8 Synthesis

The evidence chain runs:

1. Market valuation is highly structured along age, position, league and time.
2. Observable fundamentals explain a substantial share of it (R² = 0.678).
3. Prior market beliefs explain considerably more (R² = 0.884) — the market is highly persistent.
4. **The unexplained residual does not identify exploitable mispricing.**
5. It does identify **elevated exit risk** (30.1% vs 8.2% exit, odds ratio 4.82, p = 2.6 × 10⁻¹¹).
6. Exit risk is independently predictable (AUC 0.732) and well calibrated.
7. A risk-aware optimizer built on that validated component produces materially different — and more defensible — recommendations than naive value-hunting.

The project therefore concludes something more useful than its original hypothesis. A high-accuracy valuation model does **not** license the inference that its residual represents market error. In this market, over this period, the residual was better understood as a signal of information the model lacked. The appropriate managerial response is not to abandon quantitative recruitment support, but to redesign it: **from a bargain-finder into a system that tells a recruitment committee where to look, how confident to be, and what to investigate before committing capital.**
