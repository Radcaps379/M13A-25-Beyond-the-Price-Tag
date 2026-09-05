"""
==============================================================================
HISTORICAL ARTIFACT - NOT EXECUTED FOR THE FINAL RESULTS
==============================================================================

This scripted Anthropic API harness was written but NEVER RUN. The final
generative-AI evaluation was conducted through conversational model invocation,
as the report states. The script is retained for provenance only; it is not
required to reproduce the reported Arm B or Arm C results, and running it would
not reproduce them.

The frozen validator it references now applies SIX checks, not five: numerical
fidelity, unsupported claims, speculation, structural completeness, decision
consistency and uncertainty disclosure.

==============================================================================
PHASE 11c - TEMPLATE CONTROL vs LIVE LLM COMPARISON
Project: Beyond the Price Tag
==============================================================================

WHAT THIS DOES
--------------
Generates BOTH brief types for the same three players and runs both through the
identical six fidelity checks, so Section 4.9 can report a real comparison
rather than an assertion.

    A. Template control  - deterministic, no LLM
    B. Live LLM          - Anthropic API

THE RESULT IS NOT PRE-ASSUMED
-----------------------------
If the LLM produces violations, that is reported, the prompt is tightened, and
the rerun is documented. An LLM that never errs is less credible than one whose
failures were caught by a working guardrail.

HOW TO RUN
----------
    export ANTHROPIC_API_KEY="sk-ant-..."
    python genai_ab_comparison.py

Without a key the script stops and explains what to do. It will not silently
substitute template output and call it LLM output.
==============================================================================
"""

# --- repository paths -------------------------------------------------------
# Resolved from this file's location so the script runs from a clean clone,
# from any working directory. See code/repo_paths.py.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from repo_paths import ROOT, RAW, PROC, OUTPUTS, FIGURES, BRIEFS, find, stage_dir, ensure_dirs
ensure_dirs()
FIG = FIGURES
STAGE_OUT = stage_dir("genai")


import json
import os
import sys
from pathlib import Path
import pandas as pd


sys.path.insert(0, str(Path(__file__).parent))
from genai_briefs import template_brief, call_llm, facts          # noqa: E402
import genai_fidelity_check as fc                                  # noqa: E402

print("=" * 78)
print("PHASE 11c - TEMPLATE CONTROL vs LIVE LLM")
print("=" * 78)

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("""
No ANTHROPIC_API_KEY found in the environment.

This script deliberately does NOT fall back to template output, because
labelling template text as LLM output would misrepresent the experiment.

To run the live comparison:

    export ANTHROPIC_API_KEY="sk-ant-..."      # macOS / Linux
    set ANTHROPIC_API_KEY=sk-ant-...           # Windows cmd
    $env:ANTHROPIC_API_KEY="sk-ant-..."        # Windows PowerShell

    python genai_ab_comparison.py

A key can be created at https://console.anthropic.com/settings/keys
Three briefs cost well under one US cent.
""")
    sys.exit(1)


def audit(text, f):
    """Run all five fidelity checks and return a result row."""
    bad_nums = fc.check_numbers(text, f)
    claims = fc.check_claims(text)
    spec = fc.check_speculation(text)
    missing = fc.check_structure(text)
    investigate, transacts = fc.check_decision(text)
    unc = fc.check_uncertainty(text)
    ok = (not bad_nums and not claims and not spec and not missing
          and investigate and not transacts and unc)
    return {
        "numerical_fidelity": not bad_nums,
        "unsupported_claims": not claims,
        "no_speculation": not spec,
        "all_sections": not missing,
        "decision_consistency": investigate and not transacts,
        "uncertainty_disclosed": unc,
        "PASS": ok,
        "_detail": {"numbers": bad_nums[:5], "claims": claims[:3],
                    "speculation": spec[:3], "missing": missing},
    }


rows, texts = [], {}
for f in facts:
    name = f["player"]
    print(f"\n--- {name} ---")

    ctrl = template_brief(f)
    a = audit(ctrl, f)
    print(f"   template control : {'PASS' if a['PASS'] else 'FAIL'} "
          f"({len(ctrl.split())} words)")

    try:
        llm = call_llm(f)
    except Exception as e:
        print(f"   LLM call FAILED: {e}")
        print("   stopping - partial results would misrepresent the comparison")
        sys.exit(1)

    b = audit(llm, f)
    print(f"   live LLM         : {'PASS' if b['PASS'] else 'FAIL'} "
          f"({len(llm.split())} words)")
    if not b["PASS"]:
        for k, v in b["_detail"].items():
            if v:
                print(f"      {k}: {v}")

    fn = OUT / f"llm_brief_{name.lower().replace(' ', '_')}.md"
    fn.write_text(llm)
    texts[name] = {"template": ctrl, "llm": llm}

    for label, r in [("Template control", a), ("Live LLM", b)]:
        rows.append({"player": name, "brief_type": label,
                     **{k: ("PASS" if v else "FAIL")
                        for k, v in r.items() if k != "_detail"}})

res = pd.DataFrame(rows)
res.to_csv(STAGE_OUT / "genai_ab_results.csv", index=False)

print("\n" + "=" * 78)
print("COMPARISON RESULTS")
print("=" * 78)
print(res.to_string(index=False))

summary = (res.assign(p=(res.PASS == "PASS").astype(int))
           .groupby("brief_type")
           .agg(briefs=("player", "size"), passed=("p", "sum")).reset_index())
summary["pass_rate"] = (summary.passed.astype(str) + "/" + summary.briefs.astype(str))
print("\n" + summary[["brief_type", "pass_rate"]].to_string(index=False))
summary.to_csv(STAGE_OUT / "genai_ab_summary.csv", index=False)

with open(STAGE_OUT / "genai_ab_texts.json", "w") as fh:
    json.dump(texts, fh, indent=2)

print("\nwritten: genai_ab_results.csv, genai_ab_summary.csv, "
      "genai_ab_texts.json, briefs/llm_brief_*.md")
print("=" * 78)
