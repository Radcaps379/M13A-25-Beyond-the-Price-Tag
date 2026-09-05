# Report Skeleton — FROZEN
### *Beyond the Price Tag* · IIM Ranchi · Sports Analytics (WAI) · Due 5 September 2026

This is the authoritative structure. No section moves after this point. Every section lists the **source artifact** for its numbers, so no figure is ever copied from conversational prose.

**Status key:** ✅ drafted · 🔨 build required · ✍️ write when dependencies land


> **RENUMBERING APPLIED.** Dataset Description & Details is now a genuine top-level section (5), matching the IIM template's contents page. Design and Methodology becomes 6, Results & Discussion 7, Analysis 8, Conclusion 9, Limitations and Future Work 10. Sub-section numbers inside the drafted files (3.1, 4.2, etc.) must be renumbered during final assembly: 3.x → 6.x, 4.x → 7.x, 5.x → 8.x, 6.x → 9.x.

---

## FRONT MATTER

| Item | Status | Notes |
|---|---|---|
| Title page | ✍️ | Replace `<TITLE OF THE PROJECT>` with the submitted title. Specialization, Name + **Registration ID**, guide **Prof. Yelleti Vivek**, Area of Information Systems and Business Analytics. **Change the date from "May 2026" to September 2026.** |
| Declaration | ✍️ | **Critical:** the template still carries a different project's title, *"Flow-Graph-Driven Multi Agent Framework Using LLM's"*. Replace with our title. Retain the institute's AI-use paragraph verbatim — it is directly satisfied by how this project was run. Supervisor named as Dr. Vivek Yelleti. Fill Place and Date. |
| Certificate | ✍️ | Per template. |
| Abstract | ✍️ | **Do not reuse the submitted abstract unchanged.** It states the model is "validated by back-testing whether the players it flags as undervalued subsequently appreciate" — true as a description of the test performed, but the report abstract must state the test's outcome. Write last, after Section 6. |
| Table of Contents | ✍️ | Generate last. |
| List of Figures / Tables | ✍️ | Generate last. |

---

## 1. INTRODUCTION ✍️
*Short. Roughly 1.5 pages.*

- Football transfers as a large-scale capital-allocation decision under constraint
- Imperfect information in transfer valuation
- Why purely performance-based scouting is insufficient
- Why explainable AI suits managerial decision support rather than autonomous decision-making

**Closing proposition:**
> Can observable football fundamentals support a useful valuation and recruitment-decision framework *without assuming that every unexplained valuation gap represents a market inefficiency?*

---

## 2. PROBLEM STATEMENT ✍️
*Source: `report_sections1_2_intro.md` §2.1*

A club must allocate finite transfer capital across players differing in position, age, performance, valuation uncertainty and exit risk, while satisfying positional requirements under materially incomplete information. Four properties shape any supporting system: the decision is constrained, partially observable, heterogeneous across the player population, and irreversible.

---

## 3. MOTIVATION ✍️
*Source: `report_sections1_2_intro.md` §2.2*

The founding hypothesis — that observable performance can identify players whose valuations are disconnected from fundamentals — is stated, together with the decision to **test it rather than assume it**, and the practical reason that discipline matters: an unvalidated recruitment signal directs scouting capacity and irreversible capital toward whichever players the model misjudges most.

---

## 4. NOVELTY OF THE PROJECT ✍️
*Source: `report_sections1_2_intro.md` §2.3*

Novelty is located in the integrated decision framework and the evidence that shaped it, not in any individual algorithm. Seven contributions:

1. Fundamental valuation model with strict time-consistency
2. Formally tested — and unsupported — market-mispricing hypothesis
3. Discovery of a strong exit-risk relationship within the residual
4. Independently validated exit-risk model
5. Risk-aware constrained portfolio optimizer
6. Explainability separating prediction from selection explanations
7. Guarded generative-AI layer for committee communication

---

## 5. DATASET DESCRIPTION & DETAILS ✅
*Promoted to a top-level section to match the template's contents page. Source: `report_section3_methodology.md` §3.2. Leave a cross-reference at the head of Design and Methodology.*

| Content | Source artifacts |
|---|---|
| Backbone dataset, frozen-copy rationale, integer-ID architecture | `build_player_season.py` |
| Datasets evaluated and excluded on integrity grounds | — |
| Scope, construction, data-quality accounting | `data_quality_log.csv`, `player_season.csv` |
| The transfer-fee limitation (10.0% positive fees) | `player_season.csv` |

---

## 6. DESIGN AND METHODOLOGY

| § | Section | Status | Source artifacts |
|---|---|---|---|
| 3.1 | Decision Context and Information Set | ✅ | — |
| 3.2 | Dataset and Player-Season Construction | ✅ | `data_quality_log.csv`, `player_season.csv`, `build_player_season.py` |
| 3.3 | Target Definition and Market-Level Normalisation | ✅ | `build_player_season.py`, `modelling.py` |
| 3.4 | Feature Engineering | ✅ | `feature_dictionary.csv`, `feature_sets.txt`, `pretest_segment_uncertainty.csv` |
| 3.5 | Valuation Models | ✅ | `modelling.py` |
| 3.6 | Time-Based Validation | ✅ | `modelling.py` |
| 3.7 | Mispricing Hypothesis and Back-Test | ✅ | `backtest.py`, `backtest_v2.py`, `v2_threshold_selection.csv` |
| 3.8 | Exit-Risk Model | ✅ | `exit_risk_model.py`, `exit_risk_performance.csv` |
| 3.9 | Risk-Aware Portfolio Optimisation | ✅ | `optimizer_specification.md`, `optimizer.py` |
| 3.10 | Explainable AI | 🔨 | *SHAP build* |
| 3.11 | Generative-AI Recruitment Briefs | 🔨 | *brief generator build* |
| 3.12 | Data, Modelling and AI Safeguards | ✍️ | Ethics, fairness checks, AI-use disclosure |

**Required addition to 3.10** — distinguish two kinds of explanation, which the dashboard will also need:
- **Prediction explanation (SHAP):** *why did the model value this player at €31.1M?*
- **Decision explanation (optimizer):** *why did the system select this player for the portfolio?*

These are different questions. SHAP explains a number; the optimizer explains a choice.

---

## 7. RESULTS AND DISCUSSION

| § | Result | Status | Source artifacts |
|---|---|---|---|
| 4.1 | Market valuation is structured | ✅ | `eda_findings.csv`, `eda_correlations.csv`, figs q1–q5 |
| 4.2 | Fundamentals meaningfully explain valuation | ✅ | `model_results.csv`, `segment_stability.csv` |
| 4.3 | Prior market beliefs explain substantially more | ✅ | `model_results.csv` |
| 4.4 | The undervaluation hypothesis does not survive testing | ✅ | `backtest_outcome_value.csv`, `v2_backtest_outcome.csv`, `v2_signal_comparison.csv` |
| 4.5 | The residual contains a strong exit-risk signal | ✅ | `v2_backtest_audit.csv` |
| 4.6 | Exit risk can itself be predicted | ✅ | `exit_risk_performance.csv`, `exit_risk_calibration.csv` |
| 4.7 | Risk-aware portfolio optimisation | ✅ | `recommended_portfolio.csv`, `optimizer_baseline_comparison.csv`, `optimizer_sensitivity.csv`, `optimizer_budget_sensitivity.csv` |
| 4.8 | Explainability results | 🔨 | *SHAP build* |
| 4.9 | Generative-AI recruitment outputs | 🔨 | *brief generator build* |

**Editorial note on 4.1** — the age-17 correction is reduced to one sentence:
> An initial descriptive peak at age 17 was traced to the very small number of qualifying observations at that age; applying a minimum-count condition shifted the observed median-value peak to age 21.

---

## 8. ANALYSIS ✍️
*The managerial interpretation section. Kept deliberately separate from Results, per the template. This is where the MBA contribution lives.*

**5.1 What the model can and cannot tell a recruiter**
**5.2 Why apparent bargains may be risk signals** — the central inversion of the project
**5.3 Implications for transfer-budget allocation** — including the ~€52M plateau under model constraints
**5.4 Implications for recruitment and finance teams** — who uses which output
**5.5 How the tool should be used in practice** — screening and investigation, not autonomous decision
**5.6 Sensitivity and robustness** — weight and budget sensitivity, segment heterogeneity
**5.7 Ethical and managerial considerations** — age/league bias, decision support vs verdict, public data only

**The sentence that should appear prominently:**
> The output is a shortlist for investigation, not a bid list.

---

## 9. CONCLUSION ✍️

**9.0** — What we asked · what we found · what a club should do differently
**10. Limitations and Future Work** *(promoted to top level per the template contents)*

Limitations to state plainly:
- Market value is an editorial estimate, not an observed price
- Only 15.6% of player-seasons carry an observed transfer fee
- The optimizer portfolio is an illustration, **not validated at n = 3**
- Single test season; one market cycle
- Model weakest for players aged ≤ 21 (R² = 0.104) — the segment of greatest recruitment interest
- No contract, injury or scouting data — the most likely content of the unexplained residual

---

## APPENDICES ✍️
A. Feature dictionary · B. Data-quality log · C. Optimizer specification · D. Model results tables · E. Code listing / repository · F. AI-use statement

---

## STANDING RULES

1. **Every number is pulled from the artifact that generated it.** Never from earlier prose. Three transcription errors have already been caught this way.
2. **No claim is written before its artifact exists.** Sections 6.10, 6.11, 7.8, 7.9 stay empty until SHAP and the brief generator are built and checked.
3. **Corrections stay inside the methodology**, framed as decisions with reasons — not as an errata list.
4. **The n = 3 caveat travels with every mention of the portfolio.**

---

## PROJECT STATUS — 27 August 2026

*The analytical structure above is frozen. This block is status metadata and is refreshed as work completes. The original build order it replaced is superseded.*

| Component | Status |
|---|---|
| Research design · data · EDA · features | Frozen |
| Valuation model (Models 0/1/2) | Frozen |
| Mispricing hypothesis test | Frozen — **not supported** |
| Exit-risk model | Frozen — validated, AUC 0.732 |
| Risk-aware optimizer | Frozen |
| SHAP explainability + bias audit + replication | Frozen |
| Dashboard | Frozen, reproduces the batch portfolio |
| Excel decision workbook | Frozen |
| Sections 1–2, 5, 6 (now 1–4, 8, 9–10) | Frozen |
| Sections 3.10 / 4.8 → 6.10 / 7.8 (explainability) | Frozen |
| Deck (12 slides) | Frozen |
| Demo script | Frozen |
| Front matter | Submission-ready |
| Cross-artifact audit | Built and passing |
| GenAI evaluation (3 arms, conversational) | Complete — Arm A 3/3, Arm B 1/3→3/3, Arm C 3/3 |
| Sections 6.11 / 7.9 (GenAI) | Drafted and audited |
| Final report assembly | Complete — 16,576 words, 10 sections |
| Final audit re-run | After assembly |

### Finalisation discipline

The project is no longer in a build phase. From this point:

**No new analytical ideas. No new signals. No new models. No new scope.**

Only completion, integration, formatting and verification. The single exception is the live generative-AI A/B experiment, which was part of the frozen methodology and remains incomplete.

### Remaining path

All analytical and drafting work is complete. What remains requires the author:

1. Fill the five personal fields in the front matter (name, registration ID, specialization, place, date)
2. Paste the assembled report into the IIM `.docx`, apply institute formatting, generate contents and figure/table numbering
3. Export to PDF and visually inspect every page
4. Rehearse the dashboard and record the demonstration
5. Rename files to roll number
6. Re-run `final_audit.py` as the final gate — it will not pass while any `[[ ]]` field is unfilled
