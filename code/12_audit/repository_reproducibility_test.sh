#!/usr/bin/env bash
# Repository reproducibility test.
#
# Verifies the repository works from a fresh checkout at any filesystem
# location. It does NOT perform a git clone or git lfs pull; those are tested
# separately after pushing, per SETUP_GITHUB.md step 9.
#
# Verifies that the repository works from a fresh checkout: that paths resolve,
# artifacts are found, the pipeline runs, and the audit passes. Run from the
# repository root.
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
echo "Repository: $ROOT"
echo
echo "0. Declared dependencies"
python3 - <<'PYCHECK'
import importlib.util, sys
required = ["pandas", "numpy", "sklearn", "scipy", "matplotlib", "shap",
            "pulp", "openpyxl", "pptx"]
missing = [m for m in required if importlib.util.find_spec(m) is None]

# Version drift changes the numbers. scikit-learn 1.9 fits
# HistGradientBoosting differently and produced Model 1 R2 = 0.6803 against the
# reported 0.678. Pinned versions are checked, not assumed.
PINNED = {"sklearn": "1.8.0", "pandas": "3.0.2", "numpy": "2.4.4",
          "scipy": "1.17.1", "matplotlib": "3.10.8"}
drift = []
if not missing:
    for mod, want in PINNED.items():
        try:
            got = importlib.import_module(mod).__version__
            if got != want:
                drift.append(f"{mod} {got} (pinned {want})")
        except Exception:
            pass
    if drift:
        print("   VERSION DRIFT:", "; ".join(drift))
        print("   The reported figures were produced with the pinned versions.")
        print("   Install them exactly:  pip install -r requirements.txt")
        sys.exit(1)
if missing:
    print("   MISSING:", ", ".join(missing))
    print("   Install them before running this test:")
    print("       pip install -r requirements.txt")
    print()
    print("   Proceeding without them would not reproduce the reported results.")
    print("   PuLP in particular: without it the optimizer would use a greedy")
    print("   heuristic and return a different portfolio.")
    sys.exit(1)
print("   all declared dependencies present")
if importlib.util.find_spec("lightgbm") is not None:
    print("   note: lightgbm is installed. It is not used; the estimator is")
    print("   fixed to HistGradientBoosting and results are unaffected.")
PYCHECK
echo
echo "1. Path resolution"
python3 -c "
import sys; sys.path.insert(0,'code')
from repo_paths import find, ROOT
for f in ['player_season.csv','model_results.csv','recommended_portfolio.csv',
          'exit_risk_performance.csv','genai_armC_results.csv']:
    print('   ', f, '->', find(f).relative_to(ROOT))
"
echo
echo "2. Analytical pipeline (stages that need no raw data)"
for s in code/04_valuation/modelling.py code/05_backtest/backtest_v2.py \
         code/07_optimizer/optimizer.py code/08_explainability/robustness_check.py; do
  printf "   %-46s " "$(basename $s)"
  python3 "$s" > /dev/null 2>&1 && echo OK || { echo FAIL; exit 1; }
done
echo
echo "3. Generative-AI fidelity validator"
python3 code/09_genai/genai_fidelity_check.py > /dev/null 2>&1 && echo "   OK" || { echo "   FAIL"; exit 1; }
echo
echo "4. Submission audit"
python3 code/12_audit/final_audit.py > /dev/null 2>&1 && echo "   AUDIT PASSED" || { echo "   AUDIT FAILED"; exit 1; }
echo
echo "Repository reproducibility test complete."
echo "Stages 01, 03 and 06 additionally require the raw archives unpacked in data/raw/."
