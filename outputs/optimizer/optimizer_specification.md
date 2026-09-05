# Risk-Aware Recruitment Portfolio Optimizer — Specification
### Phase 9 · *Beyond the Price Tag*

This document fixes the optimizer's design **before** it is run, so that it cannot become an arbitrary scoring exercise tuned until it produces an attractive shortlist. Every weight, constraint and variable below is declared here first, with a managerial justification.

---

## 1. Why the original objective was withdrawn

The optimizer was originally specified to *maximise performance-per-euro*, later revised to *maximise (model-implied value − acquisition cost)*.

Phase 7 rejected that objective empirically. Players selected on the largest valuation residual showed **no subsequent relative appreciation** (median differential 0.0000, Mann-Whitney p = 0.307), and left top-5 football entirely at **3.7× the benchmark rate** (30.1% vs 8.2%, Fisher odds ratio 4.82, p = 2.6 × 10⁻¹¹).

Optimising residual surplus would therefore optimise a quantity our own back-test failed to validate — and would actively load the portfolio with exit risk. The objective is replaced.

---

## 2. The decision this optimizer supports

> Given a fixed transfer budget and a set of positional requirements, select the portfolio of players offering the best combination of football quality, development potential and affordability, while explicitly controlling recruitment risk and model uncertainty.

The output is a **shortlist for investigation**, not a bid list. This distinction is the central managerial lesson of the project.

---

## 3. Objective function

For each eligible player *i*, a Recruitment Score is formed from four components, each normalised to [0, 1] **within position** so that a goalkeeper competes against goalkeepers:

```
RecruitmentScore_i = w₁·Quality_i + w₂·Potential_i + w₃·ValueEfficiency_i − w₄·Risk_i
```

The optimizer maximises `Σ RecruitmentScore_i · x_i` where `x_i ∈ {0,1}`.

### Component definitions

| Component | Definition | Managerial meaning |
|---|---|---|
| **Quality** | Position-appropriate performance percentile. Attack/Midfield: goal contributions per 90. Defender/Goalkeeper: availability and minutes played. | Is this player actually good at the job the club is hiring for? Position-specific because Phase 4 showed goal contributions correlate 0.54 with value for attackers but 0.07 for goalkeepers. |
| **Potential** | Remaining development / resale runway, declining linearly to zero at **age 30** — deliberately three years beyond the hard recruitment ceiling of 27, so that a 26-year-old still carries some runway rather than scoring zero. | Will the asset appreciate, or is the club buying the tail of a career? |
| **ValueEfficiency** | Model-implied value ÷ market value, **capped at the 90th percentile of the pre-test (≤2023) distribution**. | Is the club paying less than fundamentals imply? Capped because Phase 7 proved extreme ratios signal model error, not opportunity. |
| **Risk** | Validated exit probability from the Phase 8 **logistic** model (test AUC 0.732), combined with segment-level model uncertainty. Both the uncertainty table and the value-efficiency cap are fitted on **training + validation seasons only** and passed to the optimizer as fixed constants — never recomputed from the 2024/25 pool, which would require the realised valuations a club cannot observe. | How confident can the club be that the apparent gap is opportunity rather than missing information? |

### Declared weights

| Weight | Value | Justification |
|---|---|---|
| w₁ Quality | **0.35** | Recruitment is primarily about capability. Highest weight. |
| w₂ Potential | **0.25** | Development upside is the core of a value-driven strategy. |
| w₃ ValueEfficiency | **0.20** | Affordability matters but is deliberately *not* dominant — Phase 7 showed value gaps alone are unreliable. |
| w₄ Risk penalty | **0.20** | Sized to match ValueEfficiency, encoding the project's key finding: a valuation gap and its attendant risk roughly offset. |

**These are managerial assumptions, not fitted parameters.** They were set from the evidence above and are not tuned to produce a preferred shortlist. Section 6 tests their stability.

---

## 4. Constraints, and what each means to a club

| Constraint | Default | Club-management meaning |
|---|---|---|
| **Budget** | €50M | Total acquisition cost cannot exceed the transfer budget. Cost proxy = current market value (only 15.6% of transfers carry an observed fee). |
| **Positional requirements** | e.g. 1 CB, 1 CM, 1 FW | The squad has specific holes. A portfolio of five wingers is not a solution. |
| **Minimum performance floor** | 40th percentile within position | Prevents the optimizer buying cheap players purely because they are cheap. |
| **Maximum exit risk** | 0.40 | Hard ceiling from the validated exit model. Excludes players likely to leave top-5 football regardless of their apparent bargain. |
| **Age ceiling** | 27 | Recruitment horizon: a signing needs resale runway. |
| **Minimum market value** | €1M | Below this a transfer is not a strategic capital-allocation decision. |
| **Maximum model uncertainty** | 80th percentile of segment error | Phase 6 showed error varies from 35.1% (England) to 55.9% (Spain) and R² of only 0.104 for players ≤21. The optimizer must not treat a noisy estimate as a confident one. |
| **No duplicate selection** | binary xᵢ | Structural. |

---

## 5. Allowed and forbidden variables

**Allowed** — all known at the decision point (end of 2024/25 season):
age · position · league · completed-season performance · performance trajectory · market value · model-implied value · calibrated mispricing residual · validated exit probability · segment uncertainty

**Forbidden** — post-decision or unavailable information:
2025/26 outcomes of any kind · observed subsequent transfer fees · next-season minutes or valuations · the survival-conditional appreciation result from Phase 7

The last exclusion is deliberate. The finding that flagged players who *stayed* appreciated more strongly (+0.242 vs +0.182, p = 0.048) is conditional on survival, which a club cannot observe when deciding. It stays in the report as exploratory and never enters the optimizer.

---

## 6. Guards against an arbitrary scoring exercise

Five commitments, made before running:

1. **Weights declared in advance** (Section 3) with written justification, not fitted.
2. **Sensitivity analysis is mandatory.** The optimizer is re-run across a grid of weights and budgets; if the shortlist is unstable, that instability is reported rather than concealed.
3. **A naive baseline is always reported alongside.** The risk-aware portfolio is compared to a "cheapest players meeting positional needs" portfolio and a "largest valuation gap" portfolio. If the risk-aware version is not visibly different, the added complexity is not justified.
4. **The greedy solution is reported alongside the ILP, as a comparison only.** If a simple greedy heuristic matches the optimizer, that is stated plainly — sophistication must earn its place.
5. **Every recommendation carries its uncertainty.** No player is presented without exit probability and confidence attached.
6. **All artifacts come from a single verified execution.** An earlier run crashed mid-script and left stale files on disk that disagreed with the reported portfolio. Every optimizer output is now regenerated in one run, with timestamps and cross-file consistency checked before any number is quoted.

---

## 7. What the optimizer outputs

For each recommended player: name, position, club, age, market value, model-implied value, valuation gap, quality percentile, exit probability, confidence band, and a plain-English risk flag.

For the portfolio: budget used, budget remaining, positional requirements satisfied, aggregate exit risk, and a comparison against both baseline portfolios.

---

## 8. The recommendation this system is designed to produce

Not *"these are the ten cheapest good players."* Instead:

> **These players show a valuation gap our model cannot explain. Here is how confident we are in each estimate, and here is the probability each leaves top-flight football within a year. Investigate the high-confidence, low-risk names first — and treat a large unexplained gap as a question, not an answer.**
