"""
==============================================================================
PHASE 11 - GENERATIVE-AI RECRUITMENT BRIEF GENERATOR
Project: Beyond the Price Tag
==============================================================================

DESIGN PRINCIPLE
----------------
The LLM is an INFORMATION-TRANSLATION LAYER, not an analytical layer. It
receives structured numeric facts already validated by Phases 6-10 and converts
them into committee-readable prose. It performs no analysis, adds no data, and
is given no narrative it could embellish.

    structured facts  ->  LLM  ->  fixed-section brief  ->  fidelity check

WHAT THE BRIEF MUST NOT SAY
---------------------------
It must never recommend signing a player. Phase 7 established that the system
cannot identify exploitable mispricing. The brief's job is to say: here is why
the analytics suggest investigation, and here is what a human must verify.

USAGE
-----
    python genai_briefs.py --offline    # deterministic template, no API key
    python genai_briefs.py              # calls the Anthropic API (needs key)

The offline mode exists so the pipeline and the fidelity checker are fully
demonstrable without credentials. It is NOT the deliverable - it is the control
condition against which LLM output is compared.
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


import pandas as pd
import numpy as np
import json
import os
import sys
import re
from pathlib import Path


OFFLINE = "--offline" in sys.argv

# =============================================================================
# STEP 1 - BUILD THE STRUCTURED INPUT CONTRACT
# =============================================================================
# Every field the LLM may reference. Nothing outside this dictionary is
# permitted to appear as a factual claim in the brief.

print("=" * 78)
print("PHASE 11 - GENERATIVE-AI RECRUITMENT BRIEFS")
print("=" * 78)

port = pd.read_csv(find("recommended_portfolio.csv"))
shap_exp = pd.read_csv(find("shap_shortlist_explanations.csv"))
opt_in = pd.read_csv(find("optimizer_input_2024_25.csv"))

MODEL_CONTEXT = {
    "valuation_model_test_r2": 0.678,
    "valuation_model_median_pct_error": 43.9,
    "exit_model_test_auc": 0.732,
    "mispricing_backtest_result": (
        "The hypothesis that model residuals identify exploitable undervaluation "
        "was tested out-of-sample and NOT supported (p = 0.307). Players flagged "
        "by residual left top-5 football at 3.7x the benchmark rate "
        "(30.1% vs 8.2%, p = 2.6e-11)."
    ),
    "known_model_bias": (
        "The model systematically under-values players aged 21 and under and "
        "over-values players aged 28 and over. This gradient replicates across "
        "three consecutive seasons."
    ),
    "model_blind_spots": [
        "contract length and expiry",
        "injury history and current fitness",
        "scouting and tactical assessment",
        "off-field circumstances and player willingness",
        "agent and release-clause situation",
    ],
}


def build_facts(row):
    """Assemble the complete, closed set of facts for one player."""
    s = shap_exp[shap_exp.player_id == row.player_id].iloc[0]
    o = opt_in[opt_in.player_id == row.player_id].iloc[0]

    def drivers(txt):
        if not isinstance(txt, str) or not txt.strip():
            return []
        return [d.strip() for d in txt.split(";") if d.strip()]

    return {
        "player": row["name"],
        "position": row.position,
        "league": row.league,
        "club": row.club_name,
        "age": round(float(row.age), 1),
        "market_value_eur": int(row.market_value_eur),
        "model_implied_value_eur": int(s.model_implied_eur),
        "valuation_gap_pct": round(
            100 * (s.model_implied_eur / row.market_value_eur - 1), 1),
        "minutes_played": int(row.minutes),
        "goal_contributions_per90": round(float(row.goal_contributions_per90), 3),
        "quality_percentile": int(s.quality_pctl),
        "development_potential_score": round(float(row.potential), 3),
        "value_efficiency_score": round(float(row.value_efficiency), 3),
        "predicted_exit_risk_pct": round(100 * float(o.exit_prob), 1),
        "model_uncertainty_score": round(float(row.uncertainty), 3),
        "shap_positive_drivers": drivers(s.top_positive_drivers),
        "shap_negative_drivers": drivers(s.top_negative_drivers),
        "optimizer_selection_reason": (
            f"Selected under a EUR 50m budget with one defender, one midfielder "
            f"and one attacker required. Scored on quality {int(s.quality_pctl)}th "
            f"percentile, development potential {float(row.potential):.2f}, value "
            f"efficiency {float(row.value_efficiency):.2f}, against a risk "
            f"component of {float(row.risk):.2f}."
        ),
        "model_context": MODEL_CONTEXT,
    }


facts = [build_facts(r) for _, r in port.iterrows()]
with open(STAGE_OUT / "genai_input_facts.json", "w") as f:
    json.dump(facts, f, indent=2)
print(f"\nstructured input built for {len(facts)} players "
      f"-> genai_input_facts.json")

# =============================================================================
# STEP 2 - THE PROMPT
# =============================================================================
SYSTEM_PROMPT = """You are drafting a Recruitment Committee Brief for a football club's \
recruitment and finance staff.

ABSOLUTE CONSTRAINTS - violating any of these makes the brief unusable:

1. Use ONLY the numbers and facts in the supplied JSON. Do not introduce any \
statistic, figure, date, or fact that is not present in it.
2. Do NOT invent or infer anything about injuries, contracts, personality, \
tactical fit, playing style, transfer rumours, agents, or the player's \
willingness to move. The analytical system has no data on any of these.
3. Do NOT speculate about CAUSES of anything you observe, even hedged or \
probabilistically. The data shows what happened, never why.
   WRONG: "His limited minutes may indicate injury problems or a loss of form."
   WRONG: "The low valuation possibly reflects contract uncertainty."
   RIGHT: "He recorded 1,204 league minutes. The reason for this minutes total \
is not observable in the supplied data."
   Hedging words - may, might, possibly, likely, suggests, could indicate, \
perhaps - do not make an unsupported causal claim acceptable. State the \
observation, then state that the cause is unknown.
4. Do NOT recommend signing the player. The system's own back-test found that \
model-implied valuation gaps do NOT identify exploitable opportunities. Your \
brief recommends INVESTIGATION, never a transaction.
5. Do not describe the player as "undervalued" as a matter of fact. You may say \
the model implies a higher value than the market, which is a different claim.
6. Round figures as supplied. Do not recompute or embellish.

Write these seven sections, using these exact headings:

## Recommendation
## Why the player merits consideration
## Performance and valuation evidence
## Why the optimizer selected him
## Key risks and uncertainties
## What the model does not know
## Recommended human due diligence

Tone: sober, professional, suitable for a board paper. No marketing language. \
No hype. Approximately 400-500 words."""


def call_llm(fact):
    """Call the Anthropic API. Requires ANTHROPIC_API_KEY in the environment."""
    import urllib.request
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user",
                      "content": "Draft the brief from this data:\n\n"
                                 + json.dumps(fact, indent=2)}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={"content-type": "application/json",
                 "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = json.loads(r.read())
    return "".join(b.get("text", "") for b in body.get("content", []))


def template_brief(f):
    """
    Deterministic control-condition brief. Identical structure, every number
    drawn directly from the fact dictionary. Used when no API key is available
    and as the baseline against which LLM fidelity is measured.
    """
    mv, iv = f["market_value_eur"] / 1e6, f["model_implied_value_eur"] / 1e6
    pos_d = "\n".join(f"- {d}" for d in f["shap_positive_drivers"][:4])
    neg_d = "\n".join(f"- {d}" for d in f["shap_negative_drivers"][:4])
    blind = "\n".join(f"- {b}" for b in f["model_context"]["model_blind_spots"])
    return f"""# Recruitment Committee Brief — {f['player']}

**{f['position']} · {f['club']} · {f['league']} · age {f['age']}**

## Recommendation
{f['player']} is put forward for further investigation, not for an immediate \
approach. The analytical system identifies him as a candidate on quality and \
development grounds; it cannot establish that a transaction would represent \
value, and its own back-test found no reliable link between model-implied \
valuation gaps and subsequent returns.

## Why the player merits consideration
He sits in the {f['quality_percentile']}th percentile for performance among \
players in his position, with a development-potential score of \
{f['development_potential_score']:.2f}. At age {f['age']} he retains \
substantial resale runway under the club's recruitment horizon.

## Performance and valuation evidence
Current market value is EUR {mv:.1f}m against a model-implied value of \
EUR {iv:.1f}m, a difference of {f['valuation_gap_pct']:+.1f}%. He recorded \
{f['minutes_played']:,} league minutes at {f['goal_contributions_per90']:.3f} \
goal contributions per 90.

Factors raising the model's valuation:
{pos_d}

Factors lowering it:
{neg_d}

## Why the optimizer selected him
{f['optimizer_selection_reason']}

## Key risks and uncertainties
Predicted probability of falling below 900 top-5 league minutes next season is \
{f['predicted_exit_risk_pct']:.1f}%, from a model with a held-out AUC of \
{f['model_context']['exit_model_test_auc']}. Model uncertainty for his segment \
scores {f['model_uncertainty_score']:.3f}. The valuation model carries a median \
error of {f['model_context']['valuation_model_median_pct_error']:.1f}% on \
held-out data.

A known limitation applies directly here: {f['model_context']['known_model_bias']}

## What the model does not know
The system observes match statistics, age, position, league and valuation \
history. It has no information on:
{blind}

The back-test finding is material: {f['model_context']['mispricing_backtest_result']}

## Recommended human due diligence
1. Verify contract length, expiry and any release clause.
2. Obtain injury and fitness history from medical staff.
3. Commission live scouting on tactical fit and playing style.
4. Establish the selling club's position and the player's willingness.
5. Treat the valuation gap as a question to investigate, not evidence of value.
"""


# =============================================================================
# STEP 3 - GENERATE
# =============================================================================
# Wrapped in main() so the A/B harness can import template_brief, call_llm and
# facts without triggering generation as an import side effect.


def main():
    mode = "TEMPLATE (offline control)" if OFFLINE else "ANTHROPIC API"
    print(f"\ngeneration mode: {mode}")

    briefs = {}
    for f in facts:
        name = f["player"]
        if OFFLINE:
            text = template_brief(f)
        else:
            try:
                text = call_llm(f)
            except Exception as e:
                print(f"   API call failed for {name}: {e}")
                print("   falling back to template control")
                text = template_brief(f)
        briefs[name] = text
        fn = BRIEFS / f"brief_{name.lower().replace(' ', '_')}.md"
        fn.write_text(text)
        print(f"   wrote {fn}  ({len(text.split())} words)")

    with open(STAGE_OUT / "genai_briefs.json", "w") as fh:
        json.dump(briefs, fh, indent=2)

    print("\n" + "=" * 78)
    print("BRIEFS GENERATED - run genai_fidelity_check.py to validate")
    print("=" * 78)


if __name__ == "__main__":
    main()
