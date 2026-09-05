# Beyond the Price Tag

**An Explainable AI Decision-Support System for Identifying Undervalued Talent and Optimizing Football Transfer Budgets**

Gudladona Venkata Rahul · M13A-25 · MBA (Marketing) · Indian Institute of Management Ranchi
Sports Analytics · Working with AI · Prof. Yelleti Vivek · September 2026

---

## What this project investigates

This project investigates whether observable football fundamentals can identify exploitable valuation discrepancies in the transfer market, and develops a risk-aware recruitment decision-support framework when the evidence does not support that interpretation.

The central claim was treated as a **hypothesis to be tested rather than a premise to build on**. That decision shaped everything that follows.

## Key findings

| Finding | Evidence |
|---|---|
| Observable fundamentals explain a substantial share of market valuation | R² = 0.678 on a held-out season, against 0.383 for a context-only benchmark |
| Prior market beliefs explain considerably more | R² = 0.884 when the model may see the player's previous valuation |
| **The mispricing hypothesis was not supported** | Two pre-registered signals, p = 0.094 and p = 0.307 |
| The residual instead predicts departure from top-flight football | Flagged players left at 3.7× the benchmark rate, 30.1% against 8.2%, Fisher p = 2.6 × 10⁻¹¹ |
| Exit risk is independently predictable | Held-out AUC = 0.732, calibrated from 7.3% to 69.5% across risk deciles |

The project therefore concludes something more useful than its founding hypothesis: **a model's disagreement with the market is a question to investigate, not an opportunity to exploit.** The system is positioned as a screening and investigation tool, never an autonomous decision-maker.

## Analytical pipeline

Scripts run in the order their folder numbers indicate.

| Stage | Script | Produces |
|---|---|---|
| 01 | `build_player_season.py` | `player_season.csv`, `data_quality_log.csv` |
| 02 | `eda_phase4.py` | EDA findings, figures q1–q5 |
| 03 | `feature_engineering.py` | `model_matrix.csv`, `feature_dictionary.csv` |
| 04 | `modelling.py` | `model_results.csv`, `predictions_test.csv` |
| 05 | `backtest_v2.py` | Back-test outcomes and threshold selection |
| 06 | `exit_risk_model.py` | `exit_risk_performance.csv`, pre-test constants |
| 07 | `optimizer.py` | `recommended_portfolio.csv`, sensitivity analyses |
| 08 | `shap_analysis.py`, `robustness_check.py` | SHAP decompositions, bias audit, replication |
| 09 | `genai_briefs.py`, `genai_fidelity_check.py` | Committee briefs and fidelity results |
| 10 | `dashboard.py` | Interactive Streamlit application |
| 11 | `assemble_report.py`, `build_docx.js` | Assembled report and Word document |
| 12 | `final_audit.py` | Submission gate |

## Dataset

**Primary:** `davidcariboo/player-scores`, a maintained Transfermarkt export, downloaded once and frozen. The raw CSVs are public Kaggle data and are **not redistributed in this repository**. Source links, file inventory, the frozen archive checksum and re-run instructions are in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) so results do not shift between runs. Every join uses an integer identifier (`player_id`, `club_id`); no step matches players by name.

**Scope:** England, Spain, Germany, Italy and France; seasons 2015/16 through 2024/25; players with at least 900 league minutes in a season; information cutoff 26 August 2026. This yields **15,925 player-seasons covering 4,961 players**, of which 1,508 form the held-out 2024/25 test set.

**Evaluated and excluded.** Two further datasets were assessed and deliberately left out of the pipeline. Both are retained under `data/raw/reference/` with the reason recorded, because the exclusion is a methodological decision rather than an omission.

## Repository structure

```
report/          final report, prompt logbook, section drafts
presentation/    submission deck
workbook/        recruitment committee decision workbook
code/            pipeline scripts, numbered in execution order
data/            frozen raw archives and the analysis table
outputs/         frozen results by stage
briefs/          generative-AI recruitment briefs, all three arms
figures/         figures used in the report
provenance/      audit trail and handoff archives
docs/            project development guide
```

## Reproducing the analysis

```bash
pip install -r requirements.txt          # Python pipeline
npm install                             # document generation (optional)
# stages 01, 03, 06 need the raw CSVs: see docs/DATA_SOURCES.md
python code/01_data/build_player_season.py
python code/03_features/feature_engineering.py
python code/04_valuation/modelling.py
python code/05_backtest/backtest_v2.py
python code/06_exit_risk/exit_risk_model.py
python code/07_optimizer/optimizer.py
python code/12_audit/final_audit.py
```

Every frozen output is committed, so results can be inspected without rerunning the 1.9-million-row pipeline. Stages 01, 03 and 06 additionally require the raw archives unpacked in `data/raw/`; the remaining stages run from the committed artifacts.

## Running the dashboard

```bash
pip install streamlit
streamlit run code/10_dashboard/dashboard.py
```

Five views: **Executive transfer window**, **Player explorer**, **Why this player?** (prediction versus selection explanation), **Committee brief**, and **How to read this system**. The interactive optimizer reproduces the frozen portfolio exactly.

## Generative-AI evaluation

> The reported evaluation was conducted through **conversational model invocation**. `code/09_genai/genai_ab_comparison.py` is a scripted API harness that was written but **never executed**; it is retained for provenance and is not required to reproduce the Arm B or Arm C results.

The generative layer converts validated analytical outputs into committee briefs and performs no analysis. Every brief passes a frozen **six-check** validator: numerical fidelity, unsupported claims, speculative causation, structural completeness, decision consistency and uncertainty disclosure.

| Arm | Generator | Independence from validator authorship | Result |
|---|---|---|---|
| A | Deterministic template | Full | 3/3 |
| B | Claude, conversational | None, same family authored the validator | **1/3**, then 3/3 after correction |
| C | GPT, conversational | Partial, different family | 3/3 |

**The result of interest is Arm B's initial failure.** A fluent, structurally complete brief contained three fabricated figures and was detected by the validator while the other five dimensions passed. Only comparison against the source payload exposed it.

## Verification

> **Verification status, stated precisely.**
>
> **Verified from this package:** the valuation models, the refined back-test, the robustness replication, the optimizer objective and its portfolio, all weight and budget sensitivities, the generative-AI validator and its negative controls, the audit itself, and the structural validity of all four submitted documents. An independent reviewer reconstructed the optimization problem with a different solver and obtained the identical portfolio and every sensitivity result.
>
 That covers the player-season construction, feature engineering and exit-risk model training. Those stages are verifiable against their frozen outputs, not re-executable from the ZIP.
>
> **Pending:** verification from the pushed GitHub repository, which requires a clone test after the repository is created** described in `SETUP_GITHUB.md`, step 8. A ZIP export cannot demonstrate that a clone works; only a real clone can.

```bash
pip install -r requirements.txt
bash code/12_audit/repository_reproducibility_test.sh
```

The test checks declared dependencies first and stops if any are missing. This matters: without PuLP the optimizer would fall back to a heuristic and return a different portfolio, and without the dependency check that substitution would be silent.

When the raw archives are not unpacked locally, the audit reads the positive-fee record share from the frozen canonical table rather than deriving it from `transfers.csv`. With the archives present it derives the figure directly. `final_audit.py` is the submission gate. It builds a canonical figure table directly from the artifacts, then checks every deliverable against it: 62 textual figure checks, banned-term and claim-class scans, a fact-payload audit, slide-level checks on the deck, a staleness sweep, a completeness gate, and a self-audit that inspects its own code for hardcoded values. It exits non-zero if any check fails.

**39 defects were documented across development.** None produced a runtime error. Every one surfaced through comparison against a file, a rendered page, a validation result, or the underlying data. See `code/12_audit/PROJECT_CONTROL_RULES.md`.

## Limitations

- Transfermarkt market value is a community-informed estimate, not a transacted price
- Only 10.0% of transfer records carry a positive fee, so fee analysis rests on a selective subset
- One held-out season and one market cycle
- The recommended portfolio is an illustration of a validated method, **not a validation sample**; three players cannot establish effectiveness
- Model error varies by segment, from 35.1% median error in England to 55.9% in Spain, and R² of only 0.104 for players aged 21 and under
- Contract, injury, tactical and scouting information are unobserved, and the evidence suggests that absence is doing real work

## AI use and disclosure

Artificial intelligence was used substantially: for code authorship across the pipeline, figure and artifact generation, and drafting. It also participated in methodological discussion. The author retained decision authority throughout, and the division of responsibility is documented in full in `report/prompt_logbook/` and in Appendix F of the report.

Outputs from one AI system were audited by a second under a process the author designed and adjudicated. That cross-model workflow is described in the prompt logbook.

## Licence

Academic coursework. Underlying data remains subject to its original terms.
