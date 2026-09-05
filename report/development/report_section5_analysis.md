# Section 5 — Analysis
### *Beyond the Price Tag* · IIM Ranchi · Sports Analytics (WAI)

> Section 7 reports what the analysis found. This section addresses what a football club should do about it.

---

## 5.1 From valuation to decision support

The project set out to build a system that identified undervalued players. It ended by building something different, and the reason is the single most important managerial lesson it produced.

The valuation model works. On the held-out 2024/25 season it achieves R² = 0.678 in the season-normalised framework, against 0.383 for a benchmark using age, position and league alone. Observable football performance genuinely explains a substantial share of what the market pays.

But a model that explains valuation well does **not** thereby identify where valuation is wrong. When the residual from that model was tested out-of-sample as a mispricing signal, it produced no subsequent relative appreciation advantage (median differential 0.0000, p = 0.307). The gap between model and market was not an exploitable error.

> **A valuation model can identify a discrepancy without establishing that the market is mistaken.**

This is why the system is positioned as a **screening and investigation tool**. It narrows 1,508 players to a handful worth a scout's time, attaches an explanation and a risk estimate to each, and states plainly what it cannot see. It does not decide, and the interface never labels a player "undervalued" because the evidence does not support that word.

## 5.2 Why the original "bargain" logic fails

The intuitive recruitment heuristic — pursue players whose model-implied value exceeds their market price — failed in a specific and instructive way.

The residual correlates **+0.667 with log market value**. Because the model regresses toward the mean in log space, it over-predicts cheap players, and those players are then flagged as bargains. The result was a candidate list with a median market value of €2.0M and a median age of 28.8, of whom **39.7% left top-5 football entirely** within a season, against 13.6% of the benchmark.

The refined signal, with level calibration and eligibility screening applied, produced a far more sensible candidate list — but still no appreciation advantage (p = 0.307) and still 30.1% attrition against 8.2%.

For a recruitment committee, the practical translation is:

> **A large unexplained valuation gap is more often a sign that the market knows something the model does not than an error waiting to be exploited.**

Contract situation, injury history, role change, attitude, and impending movement below top-flight level are plausible candidates for that missing information. None of them is observable in this data, and none is claimed as a finding.

## 5.3 The recruitment decision framework

The system's outputs sequence into six questions a committee can actually work through. This is the dashboard expressed as a process.

| Step | Question | Evidence used | Fails if |
|---|---|---|---|
| **1** | Is observable performance strong enough? | Position-appropriate quality percentile | Below the 40th percentile in position |
| **2** | Does the model imply meaningful valuation upside? | Model-implied value against market value | Gap within ±5% — model and market agree |
| **3** | How uncertain is that estimate? | Segment-level model error | Segment in the least reliable quintile |
| **4** | What is the predicted exit risk? | Validated exit model (AUC 0.732) | Above the club's risk tolerance |
| **5** | Does he fit positional and budget requirements? | Constrained optimizer | No feasible portfolio includes him |
| **6** | What human due diligence is required? | Generated brief | — always required |

Step 6 never resolves to "no further work needed." The system's own back-test is the reason.

Note the ordering. **Quality is asked before value.** A framework that asked about the valuation gap first would reproduce the failure documented in 5.2.

## 5.4 Implications for recruitment teams

Scouting capacity is the binding constraint in most recruitment operations, not analytical capacity. A club cannot send analysts to watch 1,508 players.

The system is therefore best understood as **a way of allocating scouting attention**. It supports:

- **Candidate screening** — reducing a league-wide pool to a reviewable shortlist
- **Shortlist construction** under explicit positional and budget requirements
- **Prioritising scouting resource** toward players where the model is confident and the risk is low
- **Flagging players who require deeper investigation** — a large gap paired with high exit risk is a question for a scout, not a recommendation
- **Balancing youth and upside against retention risk**, which the exit model now quantifies per player

It does not support autonomous signing decisions, and the briefs it generates are written to make that impossible to misread: each one states that the player is "put forward for further investigation, not for an immediate approach."

There is one specific caution for recruitment teams. The model is weakest for players aged 21 and under: for players aged 21 and under it achieves R² of only 0.104 with a median error of 52.3%. Its outputs for that group should therefore carry **more human scrutiny and less analytical confidence** than the headline accuracy figures imply.

## 5.5 Implications for finance and sporting directors

This is where the project's managerial contribution is strongest, because the optimizer changes the *shape* of the decision rather than merely informing it.

Recruitment is conventionally executed as a sequence of isolated player decisions: identify a target, negotiate, sign, move to the next. The optimizer reframes it as **portfolio allocation under constraint**. The question shifts from

> *Which player is cheapest relative to estimated value?*

to

> **Given €50M and three positional requirements, which combination delivers the strongest risk-adjusted recruitment profile?**

Under the declared weights, the recommended €50M portfolio commits €48.0M across three players at a mean quality percentile of 88 and a mean predicted exit risk of 17.1%. Set against two naive alternatives:

| Strategy | Spend | Mean quality pctl | Predicted exit risk | Mean age |
|---|---|---|---|---|
| **Risk-aware allocation** | €48.0M | 88 | 17.1% | 20.4 |
| Largest valuation gap | €7.0M | 69 | 49.3% | 26.5 |
| Cheapest meeting needs | €3.0M | 70 | 66.4% | 35.5 |

The cheapest feasible portfolio is not a recruitment strategy at all — a mean age of 35.5 and a two-in-three probability of the squad falling below meaningful minutes. It demonstrates what unconstrained value-hunting selects when nothing restrains it.

Two further findings matter at director level.

**Budget is not the binding constraint beyond a point.** Recommended spend plateaus at €52.0M: identical portfolios are returned at €75M and €100M. Under this model's eligibility rules, additional budget stops buying a better shortlist because the constraints — quality floor, age ceiling, exit-risk ceiling, uncertainty ceiling — bind before the money does. This is a property of the model's eligible universe, not evidence that clubs face a €52M optimal ceiling in reality. But it makes a real managerial point: **relaxing a constraint may be worth more than raising a budget.**

**Risk tolerance is a real lever, and it is expensive.** Moving from a €20M to a €35M budget raises mean quality from 88 to 92 while cutting mean exit risk from 30.9% to 19.2%. The marginal €15M buys risk reduction more than it buys quality.

## 5.6 Explainability and governance

For a system whose recommendations concern individual professionals and substantial capital, three governance properties matter.

**Explanations are separated by question.** SHAP explains why the model produced a valuation; the optimizer separately explains why a player was selected. Conflating them would let a persuasive valuation explanation stand in for a selection rationale. In the Coppola case, the valuation is driven by age (+0.955) and minutes (+0.336), while the selection is driven by quality percentile 89 and value efficiency 0.931 against a risk component of 0.327 — related but distinct accounts.

**Uncertainty travels with every recommendation.** No player appears without an exit probability and a confidence indication. The briefs state the model's 43.9% median error explicitly rather than presenting point estimates as precise.

**The generative layer is constrained by construction.** It receives structured, already-validated numbers and converts them to prose. It performs no analysis. Every brief is machine-checked for numerical fidelity, unsupported claims, speculative causal inference, decision consistency and uncertainty disclosure, and the checker is verified against deliberately planted violations. Generative AI here adds **communication efficiency, not analytical authority.**

**Public data has limits that governance cannot fix.** The model observes match statistics, age, position, league and valuation history. Contract, medical, tactical and personal information are absent — and Section 4.5 suggests that absence is doing real work in the residual.

## 5.7 Model risk and systematic residual heterogeneity

The model's errors are not random with respect to who a player is, and the pattern replicates.

| Age band | 2022/23 | 2023/24 | 2024/25 |
|---|---|---|---|
| ≤21 | +0.191 | +0.314 | +0.553 |
| 22–24 | +0.092 | +0.114 | +0.164 |
| 25–27 | +0.012 | +0.074 | +0.116 |
| 28–30 | −0.074 | −0.119 | −0.100 |
| 31+ | −0.094 | −0.085 | −0.144 |

The direction of the gradient replicated across all three examined seasons, although its magnitude varied materially over time. The model systematically under-values young players and over-values older ones. A parallel league pattern shows the Premier League under-valued in all three seasons (+0.249, +0.204, +0.304); LaLiga is directionally over-valued but crosses the materiality threshold in only two of three.

This is not an incidental limitation. It is the mechanism behind the failed mispricing hypothesis. If the model over-values players aged 28 and above, those players show negative residuals and get flagged as bargains — but their market price is not wrong; the model is. The residual/value correlation of +0.667 and this age gradient are two views of one defect.

> **A model's disagreement with the market cannot automatically be interpreted as evidence that the market is wrong. The disagreement may equally locate a weakness in the model.**

For a club, this converts into a concrete operating rule: **discrepancies concentrated in a segment where the model is known to be biased carry less weight than discrepancies elsewhere.** All else equal, a large gap on a 30-year-old in LaLiga deserves more scepticism than the same gap on a 24-year-old in Serie A, because the first sits where the model is known to err in that direction.

## 5.8 Sensitivity and robustness

The conclusions do not rest on a single modelling choice.

**Time-based validation throughout.** Train 2015/16–2021/22, validate 2022/23–2023/24, test 2024/25 once. No feature selection, threshold or normalisation constant was ever fitted using validation or test information. Three separate leakage defects were found and corrected under this rule.

**The nested model comparison is consistent across algorithms.** Model 0 → 1 → 2 R² runs 0.375 → 0.678 → 0.884 under gradient boosting, and 0.383 → 0.672 → 0.855 under Ridge. The ordering and the interpretation hold regardless of estimator. Ridge and OLS agree to three decimal places, confirming multicollinearity is not distorting the linear conclusion.

**The bias gradient replicates across three seasons** (5.7).

**The exit model is calibrated, not merely discriminating.** Predicted and actual exit rates converge closely at the extremes: 5.2% predicted against 7.3% actual in the lowest decile, 69.6% against 69.5% in the highest — a 9.5× spread. The interpretable logistic model marginally outperformed the boosted challenger out of sample (AUC 0.7323 against 0.7283), so no transparency-for-accuracy trade-off was required.

**The optimizer's recommendation is stable but not invariant.** Across six weight configurations, Lucas Stassin appears in all six, Diego Coppola in four and Facundo Buonanotte in three. The honest characterisation is meaningful stability rather than complete invariance: the core recommendation persists while the remainder shifts with the emphasis placed on quality, potential, affordability and risk.

**Budget sensitivity shows a plateau at €52.0M** (5.5).

**One robustness limit must be stated plainly.** The three-player portfolio is an illustration of a validated method, not a validation sample. Realised 2025/26 outcomes for three players cannot establish effectiveness. The exit-risk model is validated at the population level, n = 1,508; the portfolio is not.

## 5.9 A practical operating model

The system fits into an existing recruitment process at a specific point, and stops at a specific point.

```
   ANALYTICS SCREENING          model-implied value, quality percentile
            ↓                    across the eligible player universe
   MODEL EXPLANATION            SHAP drivers, prediction vs selection
            ↓                    rationale separated
   RISK ASSESSMENT              exit probability, segment uncertainty,
            ↓                    known model bias for that profile
   PORTFOLIO OPTIMISATION       budget, positional needs, risk tolerance
            ↓                    → shortlist for investigation
  ─────────────── analytics ends here ───────────────
            ↓
   HUMAN SCOUTING               live assessment, tactical fit, style
            ↓
   DUE DILIGENCE                medical, contract, agent, willingness
            ↓
   TRANSFER COMMITTEE           decision, with analytics as one input
```

The line matters as much as the steps. Everything above it is reproducible, auditable and explicitly uncertain. Everything below it requires information the system does not have and cannot acquire from public data.

The project's proposition is therefore not that artificial intelligence discovers undervalued footballers. It is that:

> **AI can help a recruitment committee distinguish between an apparent value opportunity and an apparent value opportunity that is more likely to be model error or recruitment risk — and can say, for each candidate, which of those it cannot tell apart.**

That is a narrower claim than the project began with. It is also one the evidence supports.
