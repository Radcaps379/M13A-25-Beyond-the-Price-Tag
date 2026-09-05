# Section 4.8 — Explainability, Bias and Decision Transparency
### *Beyond the Price Tag* · to be inserted into Section 4, Results and Discussion

---

## 4.8.1 What drives model-implied valuation

SHAP values computed on the held-out 2024/25 season (n = 1,508) decompose Model 1's behaviour. The fifteen strongest individual drivers are led by a single dominant feature:

| Rank | Feature | Mean \|SHAP\| | Share |
|---|---|---|---|
| 1 | Age | 0.4726 | 21.10% |
| 2 | Goal contributions per 90 | 0.2156 | 9.63% |
| 3 | League minutes played | 0.2020 | 9.02% |
| 4 | League: Ligue 1 | 0.1433 | 6.40% |
| 5 | League: Bundesliga | 0.1212 | 5.41% |
| 6 | Seasons of top-5 history | 0.1092 | 4.88% |
| 7 | Minutes last season | 0.0896 | 4.00% |
| 8 | League: Serie A | 0.0884 | 3.95% |
| 9 | Minutes per appearance | 0.0861 | 3.84% |
| 10 | Three-season average minutes | 0.0843 | 3.76% |

Aggregated into the families defined in the feature dictionary, the explanation is well distributed rather than concentrated:

| Feature family | Mean \|SHAP\| | Share |
|---|---|---|
| Current-season performance | 0.6261 | 28.0% |
| Performance trajectory | 0.4886 | 21.8% |
| Age | 0.4726 | 21.1% |
| League context | 0.4240 | 18.9% |
| Position | 0.0896 | 4.0% |
| Club context | 0.0748 | 3.3% |
| Physical (height) | 0.0593 | 2.6% |
| Preferred foot | 0.0046 | 0.2% |

Three observations follow.

**No single feature dominates the model.** Age is the largest individual contributor at 21.1%, but current-season performance collectively contributes more (28.0%), and no family exceeds three-tenths of the explanation. A valuation model in which one variable overwhelmed the rest would be difficult to defend as a fundamentals-based system.

**Performance trajectory earns its place.** At 21.8%, trajectory features contribute more than the league context and almost as much as age. This vindicates the methodological decision in Section 3.4 to define career trajectory as *performance* history rather than *valuation* history. Had prior market value been admitted, it would have absorbed much of this explanatory mass while rendering the residual uninterpretable.

**League context is substantial at 18.9%.** Nearly a fifth of the model's behaviour reflects which competition a player appears in rather than what he does in it. This is consistent with the 3.3× league median differences in Section 4.1, and it is a finding a recruitment committee should register: the model prices the shirt as well as the performance.

*Figures: `q12_shap_global.png` (global and family importance), `q13_shap_beeswarm.png` (direction and magnitude).*

## 4.8.2 Player-level explanation for the recommended portfolio

Each recommended player carries both a prediction explanation and a selection explanation.

### Lucas Stassin — Attack, Ligue 1, age 20.1
Market value €18.0M · model-implied €31.1M

**Prediction explanation.** Raised by goal contributions per 90 (+1.028), age (+0.740), goals per 90 (+0.104), assists per 90 (+0.073) and minutes played (+0.042). Lowered by playing in Ligue 1 (−0.372), minutes last season (−0.091), minutes per appearance (−0.045), prior-season contributions (−0.040) and three-season average minutes (−0.031).

**Selection explanation.** Quality percentile 90, potential 0.762, value efficiency 0.818, risk component 0.117.

**What the model does not know.** Validated exit probability 13.5%. No contract, injury, scouting or off-field information.

Stassin is the clearest case in the portfolio: output is the dominant positive driver, and the principal drag is the league discount rather than anything about the player.

### Diego Coppola — Defender, Serie A, age 21.0
Market value €10.0M · model-implied €27.1M

**Prediction explanation.** Raised by age (+0.955), league minutes played (+0.336), height (+0.138), minutes per appearance (+0.114) and league context (+0.081). Lowered by goal contributions per 90 (−0.179), playing in Serie A (−0.155), club squad size and rotation (−0.140), three-season average minutes (−0.053) and assists per 90 (−0.026).

**Selection explanation.** Quality percentile 89, potential 0.691, value efficiency 0.931, risk component 0.327.

**What the model does not know.** Validated exit probability 12.9%.

Coppola illustrates why position-appropriate reasoning matters. Goal contributions *reduce* his implied value — appropriate for a defender, whose value the model derives from availability and minutes rather than attacking output, consistent with the correlation of 0.069 between contributions and value for non-attacking roles reported in Section 4.1.

### Facundo Buonanotte — Midfield, Premier League, age 20.0
Market value €20.0M · model-implied €20.3M

**Prediction explanation.** Raised by age (+0.764), goal contributions per 90 (+0.137) and league context (+0.344 across the omitted league indicators, representing the Premier League premium). Lowered by league minutes played (−0.143), minutes per appearance (−0.099), club squad size and rotation (−0.082), disciplinary record (−0.055) and three-season average minutes (−0.051).

**Selection explanation.** Quality percentile 86, potential 0.767, value efficiency 0.567, risk component 0.240.

**What the model does not know.** Validated exit probability 24.9% — the highest in the portfolio.

Buonanotte is instructive precisely because his model-implied value (€20.3M) sits almost exactly at his market value (€20.0M). He was **not** selected because of a valuation gap; value efficiency is his weakest component at 0.567. He was selected on quality and development potential. This is the clearest demonstration in the project that the system is no longer a bargain-finder.

*Figures: `q14_shap_lucas_stassin.png`, `q14_shap_diego_coppola.png`, `q14_shap_facundo_buonanotte.png`.*

## 4.8.3 Systematic residual heterogeneity

SHAP explains what drives the model. A separate audit of mean signed residuals on the held-out season reveals where the model systematically misses — and the pattern is not random.

| Dimension | Segment | n | Mean residual | Direction |
|---|---|---|---|---|
| **Age** | ≤21 | 98 | **+0.553** | Model under-values |
| | 22–24 | 329 | +0.164 | Model under-values |
| | 25–27 | 417 | +0.116 | Model under-values |
| | 28–30 | 345 | −0.100 | Model over-values |
| | 31+ | 319 | −0.144 | Model over-values |
| **League** | England | 315 | **+0.304** | Model under-values |
| | Italy | 326 | +0.047 | No material pattern |
| | France | 267 | +0.047 | No material pattern |
| | Germany | 271 | −0.045 | No material pattern |
| | Spain | 329 | −0.107 | Model over-values |
| **Position** | Midfield | 446 | +0.090 | Model under-values |
| | Defender | 569 | +0.047 | No material pattern |
| | Goalkeeper | 114 | +0.030 | No material pattern |
| | Attack | 379 | +0.016 | No material pattern |

Three patterns emerge, in descending order of importance.

**The age gradient is monotonic and large.** The mean residual falls steadily from +0.553 at age ≤21 to −0.144 at 31+, crossing zero between 27 and 28. The model systematically under-values young players and over-values old ones. The ≤21 magnitude should be read directionally rather than precisely: n = 98, and that segment also records the project's weakest predictive performance (R² = 0.104, Section 4.2).

**The Premier League is systematically under-valued** (+0.304), while LaLiga is modestly over-valued (−0.107) — a spread of roughly 0.41 log units between the two.

**Position effects are comparatively small.** Only midfield (+0.090) shows a material directional pattern; the remaining three positions sit within the immaterial band.

## 4.8.4 Robustness: does the gradient replicate?

A pattern observed in a single held-out season could be season-specific noise rather than a property of the model. A pre-specified replication check was therefore run on the two validation seasons, using the identical frozen Model 1, the identical five age bands, and the identical ±0.05 materiality threshold. No band was redrawn and no threshold was tuned after seeing results.

**Mean signed residual by age band and season:**

| Age band | 2022/23 | 2023/24 | 2024/25 *(test)* |
|---|---|---|---|
| ≤21 | +0.191 | +0.314 | +0.553 |
| 22–24 | +0.092 | +0.114 | +0.164 |
| 25–27 | +0.012 | +0.074 | +0.116 |
| 28–30 | −0.074 | −0.119 | −0.100 |
| 31+ | −0.094 | −0.085 | −0.144 |

*(n per band ranges from 92 to 444; the ≤21 band holds 92–103 observations per season.)*

**The pattern replicates in every season examined.** In all three, the youngest band carries a materially positive residual and the oldest a materially negative one. The decline is strictly monotonic in 2022/23 and 2024/25; in 2023/24 it breaks only at the final step, where the 31+ band (−0.085) sits marginally above 28–30 (−0.119) — a departure well inside sampling variation and one that does not affect the direction of the gradient.

The **magnitude widens over time**: the spread between youngest and oldest bands rises from 0.285 (2022/23) to 0.400 (2023/24) to 0.697 (2024/25). The direction is a stable model property; the size is not, and should not be quoted as a fixed quantity.

**League effects replicate less symmetrically.** England carries a materially positive residual in all three seasons (+0.249, +0.204, +0.304). Spain is directionally negative in all three (−0.032, −0.058, −0.107) but crosses the materiality threshold in only two — the 2022/23 figure sits inside the immaterial band. The under-valuation of Premier League players is therefore the better-supported league finding; the over-valuation of LaLiga players is directionally consistent but weaker.

*Figure: `q15_robustness_gradient.png`.*

This check materially strengthens the argument that follows. The age gradient is not an artefact of the test season but a persistent characteristic of the model across three consecutive seasons.

## 4.8.5 Why this connects directly to the failure of the mispricing hypothesis

The residual audit is not an incidental limitation. It supplies a mechanism for the central negative result of Section 4.4.

If the model systematically over-values players aged 28 and above, then those players will exhibit large *negative* residuals — observed value below model-implied value — and will be flagged as undervalued. But their market price is not wrong; the model is. This is precisely the population the raw signal selected: median flagged age 28.8, median flagged value €2.0M, with 39.7% subsequently departing top-5 football.

The residual/value correlation of +0.667 reported in Section 4.4 and the monotonic age gradient reported here are two views of the same defect.

> **The residual cannot be safely interpreted as market inefficiency, because the residual is itself systematically structured by age and league. A discrepancy between model and market is at least as likely to locate a weakness in the model as an error in the market.**

This is the point at which explainability stops being a presentational layer and becomes a substantive result. Had the project reported SHAP importance alone — age matters most, performance matters second — it would have produced a plausible-looking explanation of a model whose residuals were not fit for the purpose originally intended for them. The audit is what exposes that, and it is the reason the system was redesigned around validated exit risk rather than assumed mispricing.

Managerial implications are developed in Section 5.7.
