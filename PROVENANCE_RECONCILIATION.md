# Provenance Reconciliation

An adversarial review of package v2 reported that the frozen model output contradicted the report: that `model_results.csv` contained `Model 1 / LightGBM` with R² = 0.6754, while the report claims HistGradientBoosting and R² = 0.678.

This document records what was checked, what was found, and what changed.

## Finding: the packaged artifacts were correct

| Check | Result |
|---|---|
| Is `lightgbm` installed in the build environment? | **No.** It was never successfully installed. |
| Estimators in the packaged `model_results.csv` | `HistGBM`, `Ridge`, `OLS`. No LightGBM entry. |
| Packaged Model 1 R²_relative | **0.6783**, matching the report's 0.678 |
| `data/processed/predictions_test.csv` vs `outputs/valuation/predictions_test.csv` | **Byte-identical** (same MD5) |

The reported contradiction did not exist in the package. It arose because the reviewing environment **did** have lightgbm installed. Running the packaged `modelling.py` there took the lightgbm branch, overwrote the outputs with different numbers, and the review then read its own regenerated file.

## But the review exposed a real defect

The scripts selected their estimator by *attempting an import*:

```python
try:
    from lightgbm import LGBMRegressor
    ...
except ImportError:
    from sklearn.ensemble import HistGradientBoostingRegressor
```

**The estimator therefore depended on what happened to be installed.** A machine with lightgbm produced R² = 0.6754; a machine without it produced 0.678. The repository could not reproduce the report on an arbitrary machine, which is precisely what a reproducibility archive must do.

This is a genuine reproducibility defect, and more consequential than the one reported. It was not visible in the artifacts, only in the code path.

## What changed

The estimator is now **fixed, not discovered**. Every script imports `HistGradientBoosting` directly, with the reasoning recorded in a comment at each site. Files changed: `modelling.py`, `backtest.py`, `exit_risk_model.py`, `robustness_check.py`, `shap_analysis.py`, `precompute_shap.py`.

**No result, figure, weight, specification or conclusion was altered.** Rerunning `modelling.py` after the change reproduces `Model 1 / HistGBM`, R²_relative = **0.6783**, unchanged.

Nothing was renamed and no CSV was edited. Doing either would have falsified provenance rather than establishing it.

## Duplicate artifact removed

`predictions_test.csv` existed in both `data/processed/` and `outputs/valuation/`. The copies were identical, but the resolver searched `data/processed/` first, so a future divergence could have caused a script to silently read a stale file.

The duplicate is removed, and `find()` now searches **stage outputs first**, so a file in `data/processed/` can never shadow a current stage artifact.

## Also corrected

- `__pycache__` removed from the package
- `package-lock.json` generated (27 packages), so the Node dependency tree is frozen
- `genai_ab_comparison.py` given an unmissable header: **HISTORICAL ARTIFACT, NOT EXECUTED FOR THE FINAL RESULTS**
- Stale "four of five" GenAI wording corrected in the README and prompt logbook; the validator has six checks
- `clean_clone_test.sh` renamed `repository_reproducibility_test.sh`, since it verifies a fresh checkout rather than performing a git clone. Clone and `git lfs pull` are tested after pushing, per `SETUP_GITHUB.md` step 9.

## Raw archives

The three dataset archives are not in this package, by design: at 219 MB the primary archive would make it undownloadable. `.gitattributes` is configured to track them with Git LFS, `data/raw/README.md` carries their SHA-256 checksums, and `PLACE_ARCHIVES_HERE.txt` gives the instructions.

**LFS is not verified until after the push.** The ZIP export proves nothing about LFS configuration; the real test is a clone followed by `git lfs pull`, which is step 9 of the setup guide.

## Verification after these changes

```
bash code/12_audit/repository_reproducibility_test.sh
```

From a fresh copy, without lightgbm installed:

- Path resolution: all artifacts located
- `modelling.py` reproduces Model 1 / HistGBM, R² = 0.6783
- `backtest_v2.py`, `optimizer.py`, `robustness_check.py`: all run
- Portfolio unchanged: Stassin, Coppola, Buonanotte, €48.0M
- Fidelity validator: runs
- Submission audit: **AUDIT PASSED**, exit 0


---

## v4: a second environment-dependent defect, found the same way

The same review environment lacked **PuLP**. Running the packaged optimizer there produced a different portfolio (Coppola, Nebel, Diop, €44.0M) because `solve_ilp` returned `None` when the import failed and the script silently used its greedy heuristic instead.

The pristine package was again correct: it contained Stassin, Coppola and Buonanotte at €48.0M. But the defect underneath was real and identical in kind to the lightgbm one. **A missing dependency was changing the answer instead of stopping.**

### What changed

`optimizer.py` now raises at import time if PuLP is absent:

```
PuLP is required for the official ILP solution.
Without it this script would fall back to a greedy heuristic and
produce a different portfolio from the one reported.
```

The greedy heuristic remains, but only as a reported comparison against the ILP result, never as an automatic substitute. Verified by simulating PuLP's absence: the script exits with the message rather than producing a plausible wrong portfolio.

`repository_reproducibility_test.sh` now checks all declared dependencies before running anything and stops if any are missing. It also notes, without failing, when lightgbm is present, since the estimator is now fixed and unaffected.

### The pattern across both incidents

Twice, a review environment differed from the build environment, and twice the code responded by **quietly taking a different path** rather than failing. Both times the artifacts were correct and the code was wrong. Both are now fixed so that an incomplete environment produces an error, not a different answer.


---

## v5: a third way the gate could report a false PASS

Review found that the deck checks shelled out to `markitdown`, an external tool. When it was absent the audit printed *"deck text extraction skipped"* and continued to **AUDIT PASSED**, having performed none of the deck-specific numerical checks.

This is the same failure mode as the previous two, in a third location: **a missing dependency changed behaviour instead of stopping.** In this case the consequence was worse, because the thing that silently stopped working was the control itself.

### What changed

Deck text is now extracted with `python-pptx`, a declared dependency, covering text frames, tables and chart data. Extraction failure is **fatal**: if the presentation cannot be read, or `python-pptx` is not installed, the audit reports the reason and exits non-zero.

Verified by simulating the absence of `python-pptx`: the audit exits 1 with an explanatory message instead of passing. With the dependency present it extracts 12 slides and runs 10 canonical checks plus the slide-7 and slide-10 content checks, all passing.

## v5: other corrections

**Stale "five checks" wording.** The report and its source section still described the validator as applying five checks; it applies six. Corrected at source, in the assembled markdown, and in the Word document, which was patched in place so the author's table of contents and edits survive.

**Optimizer documentation.** Comments still described the greedy heuristic as a fallback "that always runs". Since PuLP is now a hard requirement, that language contradicted the code. The heuristic is now documented as a comparison that is never substituted for the ILP, in both the script and the frozen specification.

## The recurring pattern, stated plainly

Three defects, all the same shape:

| Missing | Old behaviour | Consequence |
|---|---|---|
| lightgbm present unexpectedly | Different estimator selected | R² 0.6754 instead of 0.678 |
| PuLP absent | Greedy heuristic substituted | A different portfolio, reported as the result |
| markitdown absent | Deck checks skipped | AUDIT PASSED without checking the deck |

In each case the program ran successfully and produced a plausible result. None raised an error. All three are now fixed so that an incomplete or unexpected environment produces a loud failure rather than a quiet substitution.


---

## v6: last-mile documentation accuracy

**Check count.** Three further statements still described the validator as applying five checks: one in the prompt logbook and two in the report, one of which neither review had previously caught. All corrected to six, at source and in both Word documents, which were patched in place so the author's table of contents and edits survive.

**Precision of the historical result.** The logbook said the fabricated brief "passed four of the five automated checks". The accurate statement is that it **failed the numerical-fidelity check while passing the other five**. This is the stronger formulation: it explains exactly why the failure was hard to notice, since only one of six dimensions detected it and nothing in the prose signalled a problem.

**Historical defect values marked as historical.** The logbook recorded the 7.82 odds ratio and 6.90 skew without making clear they were temporary corruptions. It now states plainly that both were corrected at source, that the corrupted values appear nowhere in the submitted work, and that the correct figures are 4.82 and 3.90 throughout. `PROVENANCE_RECONCILIATION.md` retains the historical detail; the submitted logbook now cannot be misread as reporting current values.

No analytical result, figure, weight or conclusion changed. The audit passes and the repository reproducibility test passes.


---

## v7: why the same phrase evaded three sweeps

A statement implying the validator had fewer than six checks was corrected three times and reappeared each time, because it existed in three different wordings:

| Wording | Location | Caught in |
|---|---|---|
| "four of five automated checks" | README, logbook | v3 |
| "four of the five automated checks" | logbook | v6 |
| "The five automated checks test whether" | report, twice | v6 |
| "passed the other four checks" | logbook | **v7** |

Each fix targeted the exact string found, so the next variant survived. Two structural causes:

**The phrase was searched for, not counted.** A grep for `"four of five"` cannot find `"the other four checks"`. The gate now applies a **count check** instead: any construction implying four or five checks is flagged regardless of phrasing, with `"the other five"` correctly exempt, since five passing out of six is the accurate statement.

**The prompt logbook was never in the scanned set.** It is a submitted artifact, but `SUBMISSION_REQUIRED` did not list it, so the placeholder and stale-content gate had never examined it. That is why three sweeps of the report and README left the logbook untouched. It is now scanned.

Verified by negative control: reintroducing `"passed the other four checks"` into the logbook makes the audit exit 1 and name the file and phrase; restoring the correct wording returns exit 0.

This is the fourth instance of the project's recurring lesson. The first three were missing dependencies changing behaviour silently. This one was a control that appeared to be working while not examining one of the files it was meant to cover.


---

## v10: a regression introduced by the deck redesign

The presentation was rebuilt with a new design system (`deck_core.js`, `build_deck_v2.js`). Copying those two files into the repository reintroduced a defect the v2 hardening pass had eliminated everywhere else: **`build_deck_v2.js` wrote to an absolute build-machine path.** New code entering a hardened repository has to meet the same standard as the code already in it, and it did not.

Fixed: the builder now derives the repository root from its own location and writes to `presentation/`. Verified that no absolute path remains anywhere under `code/`.

`build_deck.js`, which produced the earlier design, is retained as development history and now carries a header marking it **SUPERSEDED**, warning that running it would overwrite the submitted deck.

A `__pycache__` directory also appeared during verification. It was created by running the audit inside the extracted copy, not shipped: the ZIP contains zero `.pyc` files. No action needed, but worth recording so the next reviewer does not report it as a packaging defect.

### Verification of the current documents

All four submitted documents in the package were confirmed byte-identical to the delivered versions. From a fresh extraction the audit passes at exit 0, with the deck checks reading the redesigned presentation: 12 slides extracted, slide 7 at 8/8 and slide 10 at 7/7. The visual rebuild did not disturb any figure the gate verifies.


---

## v12: three claims that overstated what the evidence supports

None of these were caught by numerical checks, because every figure involved was correct. What was wrong was the sentence built around it.

**"Ridge and OLS agree to four decimal places."** They agree to three. `model_results.csv` gives OLS 0.3830 against Ridge 0.3831, OLS 0.6719 against 0.6720, OLS 0.8552 against 0.8551, so the fourth decimal differs in all three specifications. A figure-presence audit cannot catch this: both numbers are present and both are correct, and only the claim about their relationship is wrong.

**"Orders of magnitude stronger than anything found on the appreciation side."** This compared p = 2.6 × 10⁻¹¹ against p = 0.094 and p = 0.307. A p-value measures strength of evidence, not size of effect, so it cannot support a claim about how much stronger a relationship is. Replaced with "provides substantially stronger statistical evidence than either appreciation test", which is what the p-values actually license. The effect size is reported separately and properly: 30.1% against 8.2%, a risk ratio of 3.7, and an independently validated AUC of 0.7323.

**"Precisely the group a value-driven recruitment strategy most wants to identify."** An unmeasured normative claim about what a recruitment strategy wants, attached to a measured fact about model performance. Replaced with "the segment in which the system therefore provides the least reliable valuation signal", which states only what R² = 0.104 and a 52.3% median error support. This is the same defect class the author caught earlier in "recruitment interest", and it had reappeared.

All three corrected at source across four files and patched into the Word document in place, so the author's table of contents and edits survive. A whole-document extraction of the report and logbook afterwards confirms none remain, alongside fourteen other checks for previously corrected defects.


---

## v13: a control that had been blind, and three artifacts the gate never read

**The causality detector had never worked.** Its pattern was written as `causes?\x08` — a literal backspace character, not the word-boundary `\b`. A string-manipulation pass during an earlier edit had converted the escape. The detector therefore matched nothing, and "the residual causes exit" would have passed.

The negative control did not reveal this, because its planted sentence ("This proves that contracts explain the residual") happened to match a *different* pattern in the same claim class. **A control class with several patterns needs a plant per pattern, not per class.** A second plant, "The residual causes subsequent player exit", is now in the suite: 6/6 detected.

**Three submitted artifacts were never text-scanned.** The stale-content gate read markdown only. It never read `dashboard.py`, the report DOCX, or the logbook DOCX — so the gate could report PASS while a submitted artifact contained superseded wording. It did: the dashboard still said *five* fidelity rules, *4.8x odds*, and *3.7× more likely to disappear*, all of which had been corrected everywhere else months earlier. All three now scanned.

**The report carried one more unmeasured normative claim.** "The model is weakest in one of the strategically important segments for a youth-oriented recruitment strategy" asserts what is strategically important, which nothing measures. Now: "The model is weakest for players aged 21 and under", followed by the R² and median-error figures that are measured.

**The prompt logbook DOCX was a malformed OOXML package.** `ImageRun` could not infer the image type and wrote the part as `.undefined` with no content-type declaration. LibreOffice and Word tolerate it; `python-docx` cannot open the file at all. Declaring `type: "png"` fixes the package: the part is now `.png`, and python-docx, LibreOffice and the OOXML validator all accept it.

**Also:** the workbook in the repository replaced with the exact delivered copy; the historical project guide given a prominent header stating it is not the final methodology, since it still names XGBoost, a greedy fallback and an "undervalued" objective, none of which describe the submitted project.

### The pattern, once more

Four of the five findings in this pass were **controls that appeared to work while not covering their scope**: a regex that matched nothing, a negative control that tested one pattern of six, a text scan that read three of six artifact types, and a document validator that passed a package another tool could not open. The analytical results were correct throughout.


---

## v14: the last batch, and what it says about "AUDIT PASSED"

Eight defects, found while the gate was reporting PASS. That is the point worth recording: **a passing audit means every check that exists succeeded, not that the submission is fully checked.**

**The optimizer could still substitute greedy.** A missing PuLP already failed at import, but PuLP *present and the solve returning non-optimal* left `solve_ilp()` returning `None`, and the script then used the greedy heuristic without saying so. The same route existed inside the sensitivity and budget loops. All three now raise. The portfolio is unchanged: ILP (PuLP), €48.0M.

**`python-pptx` was never declared.** The audit's deck checks import it, and the README instructs `pip install -r requirements.txt` followed by running the audit. A genuinely clean environment would have failed. Every previous "clean" run succeeded only because the environment already had it. Added to `requirements.txt` and to the reproducibility dependency gate.

**Section 7.9 had no parent heading.** Six subsections, 7.9.1 through 7.9.6, sat directly under 7.8 with nothing above them. Structural, not cosmetic. Added at source and inserted into the Word document at the correct heading level.

**The report displayed internal figure filenames.** Three paragraphs reading `Figures: q14_shap_lucas_stassin.png, ...` were assembly metadata that reached the submitted document. Removed.

**A table showed bare commas where "not applicable" belonged.** The eligible-benchmark row rendered as `, ` in two cells, an em-dash converted during the typography pass and then left as punctuation. Now `N/A`.

**The report source and the report DOCX had diverged.** The submitted document had zero em-dashes; its markdown source still had 134. Since `build_docx.js` regenerates the document from that source, a rebuild would have reintroduced the typography that was deliberately removed. Source corrected with the same context-aware rules.

**Submitted source code still carried superseded statistics.** `exit_risk_model.py` and `optimizer.py` had `4.8x` in their docstrings, contradicting the corrected terminology everywhere else. Also softened "valuation gaps predict EXIT" to "are strongly associated with EXIT", reserving predictive language for the dedicated exit-risk model.

**The workbook in the repository was replaced** with the exact delivered copy.


---

## v15: a correction that was silently reverted by a rebuild

The prompt logbook's leakage sentence was corrected, and then reappeared in the submitted document. The cause is worth recording precisely.

Two copies of the logbook's markdown existed: one in the repository at `report/prompt_logbook/`, and one in the delivery directory. The correction was applied to the repository copy. `build_logbook.js` reads the **delivery** copy. When the document was later rebuilt to fix a malformed image part, it regenerated from the uncorrected source, **silently reverting the fix**.

Nothing failed. The rebuild reported success, the document validated, and the audit passed, because no check compared a document against the source it was built from.

### What changed

The sentence is corrected at the source the builder actually reads, and both copies now carry identical wording:

> three separate forms of test-set leakage; a distinct target-informed feature-selection defect drawn from the full sample rather than the training period

This is also the better formulation. It demonstrates that the categories are understood rather than merely renumbering them: three defects leaked test-set information, and a fourth used the full sample where it should have used the training period.

### The control added

A **source / document agreement check**. For each Word document with a markdown source, the gate now confirms both agree on the tracked phrases, and fails if they diverge. Verified by negative control: reverting the sentence in the markdown makes the audit exit 1 and name the disagreement; restoring it returns exit 0.

This closes the last route by which a corrected artifact could quietly become uncorrected: not by editing it, but by rebuilding it from something older.


---

## v16: independent reconstruction, and two packaging defects it exposed

An independent reviewer extracted this package into a fresh directory and executed it, rather than reading its claims. Two findings are worth recording separately.

### The strongest evidence the project has

The reviewer's environment lacked PuLP and had no network access, so the official optimizer could not run. Instead they **reconstructed the optimization problem from the package's own inputs and specification** and solved it with SciPy's MILP implementation: the quality, potential, capped value-efficiency and uncertainty calculations, the eligibility filters, the declared weights, the budget and the positional constraints.

The independent solve returned **Lucas Stassin, Diego Coppola and Facundo Buonanotte at €48.0M** — the frozen portfolio exactly. All six weight-sensitivity scenarios and all five budget-sensitivity rows matched as well.

That is materially stronger than trusting the stored CSV. The optimizer is not producing a stale file that happens to look right; the mathematics reproduces under a different solver.

The reviewer also independently re-executed the valuation models, the refined back-test and the robustness replication, reproducing every reported figure including the three-decimal Ridge/OLS agreement and the U21 R² of 0.104.

### Two packaging defects the audit did not catch

**Four of the 53 manifest checksums were stale.** `SOURCE_MANIFEST.md` records a SHA-256 per artifact, but nothing verified them, so when artifacts were regenerated the manifest silently fell behind: three hashes drifted and one entry pointed at a path the file no longer occupied. All 53 regenerated from the actual files, and the gate now verifies them. Negative-control tested: appending a byte to a manifested file makes the audit exit 1 and name the file.

**The logbook's markdown referenced an image absent from the package.** `figures/logbook_defects.png` was embedded in the delivered Word document but never copied into the repository, so the markdown source was not self-contained and `build_logbook.js` would have failed on a fresh clone. Image added, and the gate now resolves every markdown image reference. Negative-control tested.

### Wording corrected

"Fully reproducible from the ZIP" was too strong and has been replaced with a precise statement of what is verified from the package, what is verifiable only against frozen outputs because the raw archives are excluded, and what remains pending until the post-push clone test.


---

## v17: what executing everything found that inspecting it did not

Previous passes inspected scripts. This pass **ran every one of them** from a fresh extraction. Four defects surfaced that no amount of reading would have caught.

**The deck builder could not run.** `build_deck_v2.js` used `path.join` without importing `path`. An earlier hardening edit had anchored its insertion on a line that file does not contain, so the fix silently did nothing and was never noticed because nobody executed the script. The submitted deck could not be regenerated from its own stated source.

**`package.json` pointed at the superseded builder.** `build:deck` ran `build_deck.js`, the earlier design marked SUPERSEDED in its own header. Anyone following the repository's instructions would have regenerated the wrong presentation.

**`assemble_report.py` could not find its own sources.** The path resolver searched `data/` and `outputs/` but never `report/`, where the section markdown lives. Fixed by adding the report directories to the search path.

**The build scripts destroy the submitted documents.** Running any of the three regenerates a deliverable in place, discarding the author's updated table of contents and manual edits. This was discovered by running them: three documents were overwritten and had to be restored. All three now refuse to run without `ALLOW_OVERWRITE_SUBMITTED=1`, so following the README cannot silently destroy a submission.

**One check was scoped too widely.** After `npm install`, the markdown asset check began scanning `node_modules` and reported 43 unresolved references from third-party READMEs. Now scoped to project sources, with remote URLs excluded.

### Full executable verification, from a fresh extraction

| | |
|---|---|
| `node --check`, all reporting scripts | 5/5 |
| `compileall`, all Python | pass |
| Every Python script executed | 17/17 behave correctly: 12 run, 4 stop for absent raw archives, 1 guarded exit |
| Every npm script executed | 3/3 build |
| Overwrite guard | blocks without opt-in |
| Manifest checksums | 53/53 |
| Markdown image references | all resolve |
| `final_audit.py` | PASSED, exit 0 |
| `repository_reproducibility_test.sh` | PASSED |
| Rebuilt deck | 12 slides, all tracked values present |

The lesson is the project's own, applied once more: a script that has never been executed has not been verified, however carefully it has been read.


---

## v18: the repository contradicted its own report on a clean machine

A fresh audit installed exactly what `requirements.txt` declared into an empty virtualenv and ran the pipeline. The dependency file used `>=` constraints, so pip resolved to newer libraries than the ones that produced the submitted work, including **scikit-learn 1.9.0**.

Under those versions the analysis did not reproduce:

| Figure | Reported | Clean install |
|---|---|---|
| Model 1 R² | 0.678 | **0.6803** |
| Model 1 median % error | 43.9% | 44.0% |
| Under-21 R² | 0.104 | **0.119** |
| Under-21 median % error | 52.3% | 51.4% |
| Under-21 residual, 2024 | +0.553 | +0.545 |

`HistGradientBoostingRegressor` fits differently between scikit-learn 1.8 and 1.9. Anyone cloning the repository and following the README would have obtained figures that contradict the report, with no indication that anything was wrong.

The portfolio, the back-test p-values and the exit-rate comparison all reproduced exactly, because they do not depend on the boosted model's internals. Only the model-fit figures moved.

**Every version is now pinned with `==` to the exact set that produced the submitted figures**, recorded in the file with the reason. The reproducibility test additionally checks the installed versions against those pins and stops with an explanatory message if they drift, so the mismatch cannot recur silently.

A second defect surfaced in the same run: `eda_phase4.py` called `boxplot(labels=...)`, removed in matplotlib 3.11, so the script crashed on a clean install. It now detects the supported spelling and works on either version.

### Why nothing caught this earlier

Every previous verification ran in the environment that built the project, where the correct versions were already installed. The audit compared artifacts to each other and to the documents; it never asked whether the code would produce those artifacts again elsewhere. A dependency file is not verified by reading it, only by installing from it into an empty environment.


---

## v19: the repository would have failed on a Windows clone

`.gitattributes` declared `*.csv text`, `*.md text` and `*.py text`. Those tell Git to normalise line endings on checkout. On any Windows clone, every CSV arrives with CRLF, its bytes differ from what `SOURCE_MANIFEST.md` hashed, and the audit fails.

Verified by cloning the repository with `core.autocrlf=true`:

```
manifest after CRLF checkout:   0 of 53 correct
audit:                          FAILED
```

A reader on Windows would have cloned a correct repository, run the documented command, and been told all 53 checksums were wrong. Nothing in the package was actually broken; the transport was rewriting the evidence.

### What changed

Analytical artifacts are now declared `-text`, so Git never rewrites them: `*.csv`, `*.json`, `*.txt`, plus explicit `binary` for the documents and images. Source and prose are `text eol=lf`, checked out as LF on every platform so scripts behave identically.

Verified across three configurations:

| `core.autocrlf` | Platform | Manifest | Audit |
|---|---|---|---|
| `false` | Linux, macOS | 53/53 | PASSED |
| `true` | **Windows** | 53/53 | PASSED |
| `input` | mixed | 53/53 | PASSED |

### Why nothing caught this

Every previous verification extracted a ZIP. A ZIP preserves bytes exactly; Git does not. The defect existed only in the transport, and could only appear once the files had actually passed through a Git clone. Testing the artifact is not the same as testing its delivery.
