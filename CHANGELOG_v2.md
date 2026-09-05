# Changes from v1 to v2

A reproducibility hardening pass. **No analytical logic, result, figure, model specification, optimizer weight or report conclusion was changed.** Verified by rerunning the pipeline from a clean copy: the recommended portfolio is unchanged (Stassin, Coppola, Buonanotte, €48.0M) and Model 1 still reports R² = 0.6783.

## Blockers fixed

**1. Scripts were coupled to the build machine.** Sixteen Python scripts and three Node scripts referenced `/mnt/user-data/outputs` or assumed a flat `data/processed/` working directory. A clean clone could not run them.

Added `code/repo_paths.py`, which derives every path from its own file location. Each script now resolves artifacts by name across `data/processed/` and every `outputs/<stage>/` directory, and writes to its own stage directory. No absolute build-machine path remains anywhere in the repository.

**2. The audit could not run from a clean clone.** `final_audit.py` searched a flat delivery directory that does not exist in a repository. It now locates deliverables across `report/`, `presentation/`, `workbook/` and `code/`. It also degrades gracefully when the raw archives are not unpacked, reading the affected figure from the frozen canonical table rather than failing or hardcoding it.

**3. Stage-to-stage paths did not match the packaged structure.** `exit_risk_model.py`, `optimizer.py`, `shap_analysis.py`, `genai_briefs.py` and `dashboard.py` each read files that the package stores under `outputs/<stage>/`. All resolve correctly now.

**4. The staleness sweep was removed.** It compared delivered copies against working copies; a repository holds one copy of each artifact, so the check no longer applies. Removing it inadvertently deleted the placeholder gate as well, which has been restored and scoped to submitted documents, since planning documents legitimately contain `[[ ]]` template markers.

## Documentation corrected

| Was | Now |
|---|---|
| Validator described as four checks in the script header, five in the README | **Six**, listed consistently: numerical fidelity, unsupported claims, speculation, structural completeness, decision consistency, uncertainty disclosure |
| README claimed four dashboard views | **Five**, named as they appear in the interface |
| `run_dashboard.md` gave `streamlit run dashboard.py` and a wrong file list | Correct command and the actual artifact locations |
| Manifest claimed to list every artifact | Describes itself accurately as key analytical and evidentiary artifacts |
| `requirements.txt` claimed to cover all dependencies | Notes that Node dependencies are in `package.json` |
| No warning against running the unexecuted API harness | README states plainly that it was never executed and is not needed |

## Added

- `code/repo_paths.py` — repository-relative path resolution
- `package.json` — Node dependencies (`docx`, `pptxgenjs`) with build scripts
- `code/12_audit/clean_clone_test.sh` — end-to-end verification from a fresh checkout
- `docs/demo_video_script.md` — required by the audit's completeness gate
- `CHANGELOG_v2.md`

## One defect introduced and removed during this pass

While making the raw-data dependency optional I briefly hardcoded a value into the audit's canonical table, which violates the project's own rule that no empirical value may be hardcoded there. The AST self-audit was re-run and the figure is now read from the frozen canonical table instead.

## Verification

```
bash code/12_audit/repository_reproducibility_test.sh
```

From a fresh copy at a different filesystem location, and from a different working directory:

- Path resolution: all artifacts located
- `modelling.py`, `backtest_v2.py`, `optimizer.py`, `robustness_check.py`: all run
- Fidelity validator: runs
- Submission audit: **AUDIT PASSED**, exit code 0

62 figure checks, 0 banned terms, 0 claim-class violations, 11/11 fact-payload checks, all required artifacts present, 10/10 deck checks, slide 7 8/8, slide 10 7/7, 5/5 planted over-claims caught, 0 hardcoded literals.

Stages 01, 03 and 06 additionally require the raw archives unpacked in `data/raw/`.
