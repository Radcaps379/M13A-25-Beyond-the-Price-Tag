# Source Manifest

Key analytical and evidentiary artifacts in this repository, their provenance, and their role in the final project. Source code, figures and deliverables are listed separately below rather than enumerated row by row. Checksums are SHA-256, truncated to twelve characters.


## Analytical outputs

| Artifact | Produced by | In final result | Size | SHA-256 |
|---|---|---|---|---|
| `data/processed/club_context_audit.csv` | `feature_engineering.py` | Yes | 0 KB | `ddacc753c4b2` |
| `data/processed/data_quality_log.csv` | `build_player_season.py` | Yes | 1 KB | `7f585b67a70e` |
| `data/processed/feature_dictionary.csv` | `feature_engineering.py` | Yes | 5 KB | `f108b086fc8c` |
| `data/processed/feature_sets.txt` | `feature_engineering.py` | Yes | 1 KB | `f0ffc82f36b3` |
| `data/processed/model_matrix.csv` | `feature_engineering.py` | Yes | 7.0 MB | `a58ec27c7ba9` |
| `data/processed/player_season.csv` | `build_player_season.py` | Yes | 4.5 MB | `4cd791cd6da6` |
| `outputs/valuation/predictions_test.csv` | `modelling.py` | Yes | 847 KB | `855e5f1d0026` |
| `outputs/eda/eda_correlations.csv` | `eda_phase4.py` | Yes | 0 KB | `bd9550b7cbd1` |
| `outputs/eda/eda_findings.csv` | `eda_phase4.py` | Yes | 3 KB | `9bce10dfd028` |
| `outputs/valuation/model_results.csv` | `modelling.py` | Yes | 1 KB | `0a4fd1136a11` |
| `outputs/valuation/segment_stability.csv` | `modelling.py` | Yes | 1 KB | `309f7cd4b802` |
| `outputs/backtest/backtest_audit.csv` | `backtest_v2.py` | Yes | 0 KB | `48735e7f4741` |
| `outputs/backtest/backtest_full_2024_25.csv` | `backtest_v2.py` | Yes | 1.1 MB | `1b5b2226ce4f` |
| `outputs/backtest/backtest_outcome_performance.csv` | `backtest_v2.py` | Yes | 0 KB | `e09a4d6cc1ce` |
| `outputs/backtest/backtest_outcome_value.csv` | `backtest_v2.py` | Yes | 0 KB | `70e1c0dca942` |
| `outputs/backtest/backtest_portfolio.csv` | `backtest_v2.py` | Yes | 0 KB | `0eaeae8bf6fd` |
| `outputs/backtest/backtest_threshold_selection.csv` | `backtest_v2.py` | Yes | 0 KB | `e6847404e4b8` |
| `outputs/backtest/backtest_v2_full.csv` | `backtest_v2.py` | Yes | 1.2 MB | `634178819cab` |
| `outputs/backtest/backtest_validation_frame.csv` | `backtest_v2.py` | Yes | 1.1 MB | `68f8864bc679` |
| `outputs/backtest/candidates_2024_25.csv` | `backtest_v2.py` | Yes | 28 KB | `8a4222f188c9` |
| `outputs/backtest/candidates_v2_2024_25.csv` | `backtest_v2.py` | Yes | 32 KB | `2a4884648b7d` |
| `outputs/backtest/v2_backtest_audit.csv` | `backtest_v2.py` | Yes | 0 KB | `0e40e872826e` |
| `outputs/backtest/v2_backtest_outcome.csv` | `backtest_v2.py` | Yes | 0 KB | `658a5f7f849a` |
| `outputs/backtest/v2_signal_comparison.csv` | `backtest_v2.py` | Yes | 0 KB | `523b36c20cbe` |
| `outputs/backtest/v2_threshold_selection.csv` | `backtest_v2.py` | Yes | 0 KB | `e20bef42f00c` |
| `outputs/exit_risk/exit_risk_calibration.csv` | `exit_risk_model.py` | Yes | 0 KB | `4f2dceb592e1` |
| `outputs/exit_risk/exit_risk_performance.csv` | `exit_risk_model.py` | Yes | 0 KB | `e4e7731fcbe6` |
| `outputs/exit_risk/optimizer_input_2024_25.csv` | `exit_risk_model.py` | Yes | 361 KB | `bd47285e0c97` |
| `outputs/exit_risk/pretest_constants.csv` | `exit_risk_model.py` | Yes | 0 KB | `72217fa04f82` |
| `outputs/exit_risk/pretest_segment_uncertainty.csv` | `exit_risk_model.py` | Yes | 1 KB | `56ee2c094a39` |
| `outputs/optimizer/optimizer_baseline_comparison.csv` | `optimizer.py` | Yes | 0 KB | `beb48f6d20db` |
| `outputs/optimizer/optimizer_budget_sensitivity.csv` | `optimizer.py` | Yes | 0 KB | `b6eee8b5df1e` |
| `outputs/optimizer/optimizer_sensitivity.csv` | `optimizer.py` | Yes | 0 KB | `cb73f5f463ee` |
| `outputs/optimizer/optimizer_specification.md` | `optimizer.py` | Yes | 8 KB | `3618e1b459aa` |
| `outputs/optimizer/recommended_portfolio.csv` | `optimizer.py` | Yes | 1 KB | `c80d5451367a` |
| `outputs/optimizer/recruitment_shortlist_top50.csv` | `optimizer.py` | Yes | 14 KB | `2ba49117572c` |
| `outputs/shap/robustness_age_gradient.csv` | `robustness_check.py` | Yes | 0 KB | `4e78b7abcf99` |
| `outputs/shap/robustness_league.csv` | `robustness_check.py` | Yes | 0 KB | `bf639390868f` |
| `outputs/shap/robustness_verdict.csv` | `robustness_check.py` | Yes | 0 KB | `adaa6fa1dd10` |
| `outputs/shap/shap_all_players.csv` | `precompute_shap.py` | Yes | 418 KB | `3be3d0e86a91` |
| `outputs/shap/shap_bias_audit.csv` | `shap_analysis.py` | Yes | 1 KB | `61c35153f82d` |
| `outputs/shap/shap_family_importance.csv` | `shap_analysis.py` | Yes | 0 KB | `e7fdf86f59b6` |
| `outputs/shap/shap_global_importance.csv` | `shap_analysis.py` | Yes | 2 KB | `0f3926d0b32e` |
| `outputs/shap/shap_shortlist_explanations.csv` | `shap_analysis.py` | Yes | 1 KB | `59beec9b6069` |
| `outputs/genai/genai_armB_results.csv` | `cross-model evaluation record` | Yes | 0 KB | `2dba50a8970f` |
| `outputs/genai/genai_armC_results.csv` | `genai_fidelity_check.py (frozen validator, GPT artifacts)` | Yes | 0 KB | `eba78fda5481` |
| `outputs/genai/genai_arm_history.csv` | `cross-model evaluation record` | Yes | 1 KB | `dee134040410` |
| `outputs/genai/genai_briefs.json` | `-` | Yes | 9 KB | `6cd0f35213ce` |
| `outputs/genai/genai_controls.csv` | `cross-model evaluation record` | Yes | 0 KB | `c4bebfbd6bc9` |
| `outputs/genai/genai_fidelity_results.csv` | `genai_fidelity_check.py` | Yes | 0 KB | `e19570a7a52c` |
| `outputs/genai/genai_input_facts.json` | `genai_briefs.py` | Yes | 6 KB | `07bc59b96a89` |
| `outputs/audit/audit_results.csv` | `final_audit.py` | Yes | 6 KB | `07d8ddeea496` |
| `outputs/audit/canonical_figures.csv` | `final_audit.py` | Yes | 2 KB | `da2d68c5ac7a` |

## Deliverables

| Artifact | Role |
|---|---|
| `report/final/M13A-25_Beyond_the_Price_Tag_Report.docx` | Submitted report |
| `report/final/Beyond_the_Price_Tag_REPORT.md` | Assembled source the report was built from |
| `report/prompt_logbook/` | Working-with-AI record |
| `presentation/` | Submitted deck |
| `workbook/` | Recruitment committee decision workbook |

## Historical and superseded

These are retained deliberately. They document the development history and are **not** part of the final evidence chain.

| Artifact | Status |
|---|---|
| `code/05_backtest/backtest.py` | Superseded by `backtest_v2.py`. Retained because it implements the first pre-registered signal, whose null result is reported in the report. |
| `briefs/template/` | Deterministic control condition, Arm A. Not language-model output. |
| `code/11_reporting/build_deck.js` | Superseded. Produced the first deck design; the submitted presentation is built by `build_deck_v2.js` with `deck_core.js`. Retained as development history and marked in its header. |
| `code/09_genai/genai_ab_comparison.py` | Scripted API harness, written but **never executed**. Evaluation ran through conversational invocation instead. Retained because the report describes this path and its non-use. |
| `provenance/archive/GPT_ArmC_Briefs_For_Frozen_Validation.zip` | The exact Arm C handoff archive, preserved as received. |
| `docs/Football-Valuation-Project-Guide.md` | Early planning document. Superseded by the report; retained as development history. |

## Deliberately excluded from this repository

| Excluded | Reason |
|---|---|
| A duplicate copy of the workbook | Byte-identical to the retained file |
| An earlier unnumbered build of the deck | Superseded by the roll-number-named submission copy |
| An earlier generic front-matter draft | Superseded by the submission version |
| A GPT-generated transcript file | Contained passages authored by Claude but labelled as GPT output. Excluded on provenance grounds; the incident is documented in the prompt logbook. |

## Note on intermediate artifacts

Some scripts write intermediate working files consumed immediately by the next stage. Where such a file forms part of the evidence chain it is retained under `outputs/`. Where it existed only to pass data between two stages in a single run, it is not retained, and no placeholder has been fabricated in its place.
