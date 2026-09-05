# Project Control Rules
### *Beyond the Price Tag* · binding for all remaining work

These are not guidelines. Four numerical errors reached draft text before being caught, and each was found only because someone checked against a file rather than against a memory. The rules below make that check structural.

---

## Rule 1 — Artifact files are the single source of truth

Every number appearing in the report, deck, dashboard, README, brief or video script must be traceable to a file in `data/processed/`, `figures/` or `briefs/`.

**Never** cite a number from: conversational prose, an earlier draft, a console output that has scrolled past, or memory. If a figure cannot be pointed at in a file, it does not go in the document.

## Rule 2 — Pull before writing, audit after

Before drafting any section containing figures, re-read the source artifacts. After drafting, run a mechanical claim-by-claim comparison against those artifacts.

Section 5 was audited on 34 separate claims. That is the standard for every remaining section.

## Rule 3 — A script that runs is not a script that worked

Check exit codes. Check that expected output files exist and carry the expected timestamp. Cross-check dependent files against one another before quoting any of them.

*Origin:* the optimizer crashed inside budget sensitivity on a `DataFrame.__bool__` error, left stale files on disk, and the reported portfolio (€48M) disagreed with the file (€41M) for a full turn.

## Rule 4 — Sanity-check outputs for face validity

Statistical validity is not plausibility. After any modelling step, inspect the extremes and the shape.

*Origin:* a non-stable double sort silently attached valuations to the wrong players, producing a €200M journeyman and a flat age curve. The pipeline raised no error. Only the face-validity check caught it.

## Rule 5 — Name the artefact that was actually used

Library and estimator names in the report must match what executed.

*Origin:* `lightgbm` was never installed; every model ran on `HistGradientBoosting`. The artifacts recorded this correctly throughout while the prose said "LightGBM" for several days.

**Binding terminology:**
- Valuation model → **scikit-learn `HistGradientBoostingRegressor` (HistGBM)**
- Exit-risk production model → **`LogisticRegression`**
- Exit-risk challenger → **`HistGradientBoostingClassifier` (HistGBC)**
- Optimizer → **PuLP (CBC)**
- "LightGBM" and "XGBoost" must not appear in the report, deck, dashboard, README or video.

## Rule 6 — Claim only what was measured

No variable may be invoked that the data does not contain.

*Origin:* "the model is weakest where recruitment interest is highest" — recruitment interest was never measured. Corrected to "one of the strategically important segments for a youth-oriented recruitment strategy."

## Rule 7 — Nothing is written before its evidence exists

**Final state.** The generative-AI sections are complete and appear as 6.10 and 7.9 in the renumbered report. The evaluation ran through conversational model invocation rather than the scripted API harness, and the report says so; see `PROVENANCE_RECONCILIATION.md`. The dashboard labels each brief by the arm that produced it.

## Rule 8 — Distinguish validated from illustrative

| Component | Status | Permitted claim |
|---|---|---|
| Valuation model | Validated, n = 1,508 | R² = 0.678, season-normalised, held-out |
| Exit-risk model | Validated, n = 1,508 | AUC = 0.732, calibrated across deciles |
| Mispricing hypothesis | Tested and **rejected** | p = 0.307, no appreciation advantage |
| Residual bias gradient | Replicated, 3 seasons | Direction stable; magnitude varies |
| Three-player portfolio | **Illustrative only** | An application of a validated model — never validation |
| Survival-conditional result | **Exploratory only** | Post-outcome selection; never a headline |

The n = 3 caveat travels with every mention of the portfolio.

---

## Errors caught by these rules

| # | Error | Found by |
|---|---|---|
| 1 | Test set stated as 1,509; artifacts said 1,508 | Rule 1 |
| 2 | Portfolio quoted as €48M while file held €41M | Rule 3 |
| 3 | Coppola's age SHAP quoted +0.76; actual +0.955 | Rule 2 |
| 4 | "LightGBM" claimed throughout; never installed | Rule 5 |
| 5 | €200M journeyman valuation, flat age curve | Rule 4 |
| 6 | Season dummies silently defaulting test rows to 2015/16 baseline | Rule 4 |
| 7 | Uncertainty and value cap derived from test outcomes | Rule 8 |
| 8 | "Recruitment interest" invoked but never measured | Rule 6 |

Eight defects caught by these binding control rules, none of which produced an error message. Every one was found by checking output against a file or against reality.

*These eight are the control-rule defects only. The wider development record documents **39 defects and control failures** in total across the project; see the prompt logbook, Section 5.*
