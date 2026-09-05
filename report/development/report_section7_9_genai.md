# Section 7.9 — Generative-AI Results and Fidelity Evaluation
### *Beyond the Price Tag* · to be inserted into Section 7, Results and Discussion

---

## 7.9.1 Headline result

| Arm | Generator | Result | Interpretation |
|---|---|---|---|
| **A** | Deterministic template | 3/3 | Control — the validator does not falsely reject compliant output |
| **B** | Claude, conversational | **1/3 → 3/3** | A real generation failure, detected and corrected |
| **C** | GPT, conversational | **3/3** | Cross-model arm; partial validator independence |

The result of interest is **Arm B's initial failure**, not any of the pass rates.

In summary: the evaluation demonstrated that **fluency alone was insufficient to guarantee factual fidelity**. The initial Claude generation contained three plausible numerical fabrications that were detected by the frozen validator, after which the corrected Claude and GPT generations passed all prescribed checks. This demonstrates the utility of the generation-and-validation architecture; it does not establish general language-model reliability, nor superiority of one model family over another.

## 7.9.2 The generation failure

The first conversational generation produced one passing brief of three. The Stassin brief contained three numerical claims inconsistent with the supplied payload:

| Stated in the brief | Value in the payload |
|---|---|
| 2,079 league minutes | **1,868** |
| 0.606 goal contributions per 90 | **0.819** |
| 0.560 model uncertainty | **0.074** |

The validator detected all three.

Two features of this failure matter more than its existence. First, the brief was otherwise **professionally written and structurally complete** — it passed the claim, speculation, structure, decision-consistency and uncertainty checks. Nothing in its prose signalled that three of its figures were wrong. Second, the fabrications were **plausible**: 2,079 minutes is a credible season for a regular starter, and 0.606 goal contributions per 90 is a credible attacking return. A reader without the source data beside them would have no basis for suspicion.

The failure arose from the model drawing figures from surrounding context rather than reading them from the payload. After the figures were re-taken verbatim from the payload, all three briefs passed.

This is the project's principal generative-AI finding:

> **A fluent, well-structured and apparently authoritative recruitment brief contained three fabricated quantitative claims. Fluency carried no information about factual accuracy, and only automated verification against the source payload exposed the discrepancy.**

## 7.9.3 Cross-model arm

The GPT conversational arm achieved **3/3 under the frozen validator**, passing all six recorded dimensions for each of Lucas Stassin, Diego Coppola and Facundo Buonanotte on first generation, without correction.

Two additional checks establish that this pass is substantive rather than an artefact of the evaluation.

**Numerical density.** A brief can pass a numerical-fidelity check trivially by making few numerical claims. The GPT briefs recorded **74.3 numeric claims per 1,000 words**, higher than the initial Claude arm at 69.9 and comparable to the deterministic template at 91.1. The arm passed by stating figures correctly, not by avoiding them.

**Negative control on the generated text itself.** Six violations were planted directly into a GPT-authored brief — a fabricated euro figure, invented injury, contract and tactical claims, an explicit signing recommendation, and a hedged causal claim. The validator detected **6/6**. It was therefore actively evaluating that text rather than passing it because it was structurally complete.

| Control | Result |
|---|---|
| Synthetic negative control (planted into template text) | 7/7 detected |
| Negative control planted into GPT-authored text | 6/6 detected |
| Arm C payload vs canonical payload | byte-identical |
| Validator checksum vs delivered copy | unchanged |

## 7.9.4 Content fidelity: which framework did the briefs communicate?

The six automated checks test whether a brief states the supplied facts correctly. They cannot test whether it communicates the *right analytical framework* — a brief could be numerically flawless while reverting to the bargain-finding framing this study rejected.

Manual inspection of the nine generated briefs across both conversational arms found that framework fidelity held in every case, and the three players happen to constitute a useful test:

**Stassin** carries a substantial model-market gap (+72.6%). The briefs present it as a discrepancy warranting investigation and pair it with the back-test result, rather than as evidence of underpricing.

**Coppola** carries the largest gap in the portfolio (+171.4%) together with the highest model uncertainty (0.788). The briefs disclose both, and treat the size of the gap as a reason for closer scrutiny rather than greater confidence.

**Buonanotte** is the decisive case. His model-implied value (€20.3M) is within 1.5% of his market value, and his value efficiency (0.567) is the weakest in the portfolio. Under the project's original objective he would never have been surfaced. The briefs state explicitly that no valuation discrepancy supports the recommendation and that the case rests on quality and development potential.

That last result matters because it could not have been produced by a system still optimising for apparent bargains. The generative layer is faithfully communicating the framework the evidence produced, not the one the project began with.

This is reported as manual inspection rather than as an automated check, and it is not claimed as a validated property. It is an observation about nine documents.

## 7.9.5 What these results do not establish

Three claims are **not** supported and are not made anywhere in this report.

**This is not evidence that GPT is more reliable than Claude.** Each arm contains three briefs. The design was not constructed or powered for model comparison, and a single failed generation in one arm cannot support an inference about relative reliability.

**This is not a claim of factual reliability.** The corrected Claude result and the GPT result are both 3/3, but the first Claude generation was not. The system's demonstrated property is that fabrication *can be detected*, not that it does not occur.

**Arm C is not a fully independent validation.** The generating model had visibility of the validator design through the project interaction. The independence is partial, and Section 6.11.6 records it as such.

The defensible conclusion is narrower than any of these:

> The constrained generation-and-validation architecture detected fabricated content in an initial language-model generation and produced compliant output after factual grounding and correction. It was applied without modification across two model families.

## 7.9.6 Managerial implication

The finding has a direct consequence for how a committee should treat a generated document.

A recruitment brief produced by this system is a **verified translation of analytical evidence, not an additional source of football intelligence**. It contains no information the analytical layer did not supply, and the fidelity check confirms that it contains nothing more.

That framing carries practical weight because the failure mode observed here is not detectable by reading. The three fabricated figures in the Stassin brief were caught by comparison against a source file, not by review of the prose. A committee that treated fluency as evidence of accuracy would have accepted them.

Every brief therefore closes with two sections that exist for this reason: an explicit statement of what the model cannot observe — contract, medical, scouting and willingness-to-move considerations — and a list of due-diligence questions directed back to human judgement. The generative layer reduces the burden of translating multiple quantitative outputs into a consistent decision document. It does not reduce the burden of verification, and the architecture is designed so that verification happens automatically before the document reaches a decision-maker rather than depending on a reader noticing.
