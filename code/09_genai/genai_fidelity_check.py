"""
==============================================================================
PHASE 11b - GENERATIVE-AI FIDELITY CHECK
Project: Beyond the Price Tag
==============================================================================

WHY THIS EXISTS
---------------
A report that says "we used an LLM to write summaries" has demonstrated nothing.
This makes the GenAI layer MEASURABLE by auditing every generated brief against
the structured facts it was given.

SIX CHECKS
----------
  1. NUMERICAL FIDELITY     every number in the brief traces to the input JSON
  2. NO UNSUPPORTED CLAIMS  no invented injury, contract, personality, tactical
                            or scouting assertions
  3. NO SPECULATION         no hedged causal claim about an unobservable
  4. STRUCTURAL COMPLETENESS all seven required sections present
  5. DECISION CONSISTENCY   the brief recommends investigation, never a signing
  6. UNCERTAINTY DISCLOSURE the brief states what the system cannot observe

A brief failing any check is rejected. The pass rate is reported in Section 4.9
as an empirical property of the pipeline, not an assurance.
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
import re
import sys
from pathlib import Path
import pandas as pd


facts = json.load(open(find("genai_input_facts.json")))
briefs = json.load(open(find("genai_briefs.json")))

print("=" * 78)
print("PHASE 11b - GENAI FIDELITY CHECK")
print("=" * 78)


# =============================================================================
# CHECK 1 - NUMERICAL FIDELITY
# =============================================================================
def allowed_numbers(f):
    """Every numeric value the brief is permitted to state."""
    a = set()

    def add(x):
        try:
            v = float(x)
        except (TypeError, ValueError):
            return
        a.add(round(v, 3))
        a.add(round(v, 1))
        a.add(round(v))
        if abs(v) >= 1e6:                     # euro values in millions
            a.add(round(v / 1e6, 1)); a.add(round(v / 1e6))
        if 0 < abs(v) < 1:                    # scores also written as percent
            a.add(round(v * 100, 1)); a.add(round(v * 100))

    for k, v in f.items():
        if isinstance(v, (int, float)):
            add(v)
    for d in f["shap_positive_drivers"] + f["shap_negative_drivers"]:
        for m in re.findall(r"[-+]?\d*\.?\d+", d):
            add(m)
    mc = f["model_context"]
    for v in mc.values():
        if isinstance(v, (int, float)):
            add(v)
        elif isinstance(v, str):
            for m in re.findall(r"[-+]?\d*\.?\d+", v):
                add(m)
    # structural constants stated in the optimizer brief
    for v in [50, 1, 900, 3, 2, 4, 5, 0, 100, 2024, 2025, 21, 28]:
        add(v)
    add(f["market_value_eur"] / 1e6)
    add(f["model_implied_value_eur"] / 1e6)
    return a


def check_numbers(text, f):
    allowed = allowed_numbers(f)
    # Strip markdown ordered-list markers first: "6." at the start of a line is
    # a list bullet, not a numeric claim. Leaving them in produced a false
    # positive on every brief with a numbered due-diligence list.
    scrubbed = re.sub(r"(?m)^\s*\d+\.\s", "", text)
    found = re.findall(r"[-+]?\d[\d,]*\.?\d*", scrubbed)
    bad = []
    for raw in found:
        clean = raw.replace(",", "")
        try:
            v = float(clean)
        except ValueError:
            continue
        if not any(abs(v - a) < 0.051 for a in allowed):
            bad.append(raw)
    return bad


# =============================================================================
# CHECK 2 - UNSUPPORTED CLAIMS
# =============================================================================
# Terms that assert knowledge the system does not have. Matched only when the
# brief ASSERTS them, not when it disclaims them.
FORBIDDEN = {
    "injury": r"\b(injur\w+|fitness record|medical history|knock|strain)\b",
    "contract": r"\b(contract (?:expires|length|situation|until)|release clause|free agent)\b",
    "personality": r"\b(mentality|attitude|character|temperament|leadership|professionalism)\b",
    "tactical": r"\b(tactical fit|suits? the system|formation|press\w*|playing style|link-up)\b",
    "scouting": r"\b(scouts? (?:report|rate)|our analysts believe|reportedly|rumou?r)\b",
    "transaction": r"\b(we (?:should|must) sign|recommend signing|proceed with (?:a|the) bid|make an offer)\b",
}

# Sentences that legitimately MENTION these terms while disclaiming knowledge.
DISCLAIM = r"(no information|does not (?:know|observe|have)|cannot (?:observe|establish|know)|" \
           r"has no|not available|unavailable|blind spot|verify|obtain|commission|" \
           r"establish|due diligence|recommended human|no data)"


# Two sections exist precisely to NAME what the system cannot observe and what a
# human must verify. Bullets there ("- injury history and current fitness") are
# disclaimers, not assertions. Scanning them as claims produced false positives
# on the first run, so the checker tracks which section each line sits in.
EXEMPT_SECTIONS = ["what the model does not know",
                   "recommended human due diligence"]


def check_claims(text):
    hits = []
    current_section = ""
    for line in text.split("\n"):
        if line.strip().startswith("#"):
            current_section = line.strip("# ").strip().lower()
            continue
        if any(e in current_section for e in EXEMPT_SECTIONS):
            continue                       # disclaimer territory
        for sent in re.split(r"(?<=[.!?])\s+", line):
            if not sent.strip():
                continue
            if re.search(DISCLAIM, sent, re.I):
                continue                   # disclaiming, not asserting
            for label, pat in FORBIDDEN.items():
                if re.search(pat, sent, re.I):
                    hits.append({"category": label,
                                 "section": current_section,
                                 "sentence": sent.strip()[:130]})
    return hits


# =============================================================================
# CHECKS 3 AND 4
# =============================================================================
REQUIRED_SECTIONS = [
    "Recommendation", "Why the player merits consideration",
    "Performance and valuation evidence", "Why the optimizer selected him",
    "Key risks and uncertainties", "What the model does not know",
    "Recommended human due diligence",
]


# =============================================================================
# CHECK 5 - SPECULATIVE CAUSAL INFERENCE
# =============================================================================
# The most likely LLM failure mode is not outright fabrication but HEDGED
# speculation: "his limited minutes may indicate injury problems". A hedge does
# not make an unsupported causal claim acceptable - the data shows what
# happened, never why. This check looks for a hedging word appearing in the
# same sentence as a causal connective plus an unobservable subject.

HEDGE = r"\b(may|might|possibly|perhaps|likely|could|suggests?|appears? to|" \
        r"seems? to|presumably|probably|indicat\w+)\b"
CAUSAL = r"\b(because|due to|owing to|reflect\w*|result\w* from|attributable to|" \
         r"explain\w*|caused? by|stems? from|driven by|on account of)\b"
UNOBSERVABLE = r"\b(injur\w+|fitness|contract|form|confidence|motivation|" \
               r"unsettled|homesick|manager|rotation policy|fall\w* out|" \
               r"disciplin\w+|personal (?:issues|reasons)|adaptation)\b"


def check_speculation(text):
    hits = []
    current_section = ""
    for line in text.split("\n"):
        if line.strip().startswith("#"):
            current_section = line.strip("# ").strip().lower()
            continue
        if any(e in current_section for e in EXEMPT_SECTIONS):
            continue
        for sent in re.split(r"(?<=[.!?])\s+", line):
            if not sent.strip():
                continue
            if re.search(DISCLAIM, sent, re.I):
                continue
            has_hedge = bool(re.search(HEDGE, sent, re.I))
            has_causal = bool(re.search(CAUSAL, sent, re.I))
            has_unobs = bool(re.search(UNOBSERVABLE, sent, re.I))
            # a hedged causal claim about something the system cannot see
            if has_unobs and (has_hedge or has_causal):
                hits.append({"section": current_section,
                             "sentence": sent.strip()[:130]})
    return hits


def check_structure(text):
    return [s for s in REQUIRED_SECTIONS if s.lower() not in text.lower()]


def check_decision(text):
    investigate = bool(re.search(
        r"(investigat\w+|further (?:review|enquiry)|due diligence|not for an immediate)",
        text, re.I))
    transacts = bool(re.search(
        r"\b(we (?:should|must) sign|recommend signing|proceed with (?:a|the) bid)\b",
        text, re.I))
    return investigate, transacts


def check_uncertainty(text):
    return all([
        bool(re.search(r"exit|below 900|leave", text, re.I)),
        bool(re.search(r"(does not know|cannot observe|has no information|no data)", text, re.I)),
        bool(re.search(r"(uncertain|error|risk)", text, re.I)),
    ])


def run_all():
    # =============================================================================
    # RUN
    # =============================================================================
    rows = []
    for f in facts:
        name = f["player"]
        text = briefs[name]

        bad_nums = check_numbers(text, f)
        claims = check_claims(text)
        spec = check_speculation(text)
        missing = check_structure(text)
        investigate, transacts = check_decision(text)
        unc = check_uncertainty(text)

        passed = (not bad_nums and not claims and not spec and not missing
                  and investigate and not transacts and unc)

        rows.append({
            "player": name,
            "words": len(text.split()),
            "numerical_fidelity": "PASS" if not bad_nums else f"FAIL ({len(bad_nums)})",
            "unsupported_claims": "PASS" if not claims else f"FAIL ({len(claims)})",
            "no_speculation": "PASS" if not spec else f"FAIL ({len(spec)})",
            "all_sections_present": "PASS" if not missing else f"FAIL ({len(missing)} missing)",
            "decision_consistency": "PASS" if (investigate and not transacts) else "FAIL",
            "uncertainty_disclosed": "PASS" if unc else "FAIL",
            "OVERALL": "PASS" if passed else "FAIL",
        })

        if bad_nums:
            print(f"\n[{name}] unverifiable numbers: {bad_nums[:8]}")
        for c in claims:
            print(f"\n[{name}] unsupported {c['category']}: \"{c['sentence']}\"")
        for c in spec:
            print(f"\n[{name}] speculative causal claim: \"{c['sentence']}\"")
        if missing:
            print(f"\n[{name}] missing sections: {missing}")

    res = pd.DataFrame(rows)
    print("\n" + "=" * 78)
    print("FIDELITY RESULTS")
    print("=" * 78)
    print(res.to_string(index=False))

    n_pass = (res.OVERALL == "PASS").sum()
    print(f"\nOverall pass rate: {n_pass}/{len(res)} ({100*n_pass/len(res):.0f}%)")
    res.to_csv(STAGE_OUT / "genai_fidelity_results.csv", index=False)


    # =============================================================================
    # NEGATIVE CONTROL - prove the checker actually catches violations
    # =============================================================================
    print("\n" + "=" * 78)
    print("NEGATIVE CONTROL")
    print("=" * 78)
    print("A checker that passes everything proves nothing. We feed it a brief with")
    print("four deliberately planted violations and confirm each is caught.\n")

    f0 = facts[0]
    sabotaged = briefs[f0["player"]] + """

    ## Scouting assessment
    He has an excellent injury record and his contract expires in 2029.
    His limited minutes may indicate underlying fitness problems.
    Scouts rate his mentality highly and he suits a high-pressing system.
    We recommend signing him for EUR 44.7m before the window closes.
    """

    bad_nums = check_numbers(sabotaged, f0)
    claims = check_claims(sabotaged)
    investigate, transacts = check_decision(sabotaged)

    print(f"planted fabricated figure (44.7)  -> caught: "
          f"{'YES' if any('44.7' in b for b in bad_nums) else 'NO'}")
    cats = {c['category'] for c in claims}
    for lbl, cat in [("planted injury claim", "injury"),
                     ("planted contract claim", "contract"),
                     ("planted personality claim", "personality"),
                     ("planted tactical claim", "tactical")]:
        print(f"{lbl:<34} -> caught: {'YES' if cat in cats else 'NO'}")
    print(f"planted signing recommendation    -> caught: {'YES' if transacts else 'NO'}")
    spec_hits = check_speculation(sabotaged)
    print(f"planted hedged speculation        -> caught: "
          f"{'YES' if spec_hits else 'NO'}")
    if spec_hits:
        print(f"     caught: \"{spec_hits[0]['sentence']}\"")

    print("\n" + "=" * 78)
    print("FIDELITY CHECK COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    run_all()
