# Section 6.11 — Generative-AI Recruitment Brief Generation and Fidelity Control
### *Beyond the Price Tag* · to be inserted into Section 6, Design and Methodology

---

## 6.11.1 Role of the generative layer

The generative-AI component is a **downstream communication layer, not a source of analytical estimates**. The valuation model, exit-risk model, explainability analysis and portfolio optimizer provide the quantitative evidence used by the system; the language model converts those validated outputs into a recruitment-committee brief. This separation is architectural rather than stylistic: it prevents the language model from computing, adjusting or reinterpreting any analytical result.

The design responds directly to Section 7.4. Because the study found no support for exploitable mispricing, a brief that reads persuasively must not thereby lend confidence to a recommendation the evidence does not support. The generative layer is therefore constrained to translate, and constrained to disclose what the analytical system cannot see.

## 6.11.2 Input contract

Each brief is generated from a structured player-facts payload containing position, club, league, age, market value, model-implied value, valuation gap, minutes, goal contributions per 90, quality percentile, development potential, value efficiency, predicted exit risk, model uncertainty, SHAP positive and negative drivers, and the optimizer's selection rationale. A shared model-context block supplies the valuation model's held-out error, the exit model's AUC, the back-test result, the known age-related model bias, and the list of variables the system cannot observe.

Nothing outside this payload may appear as a factual claim. The payload is treated as a project artifact under the same control rules as the model outputs and is verified against the canonical figure table during the final audit — a control introduced after a superseded figure was found in a delivered copy of the payload, where it would have propagated into every subsequent generation as an *allowed* fact.

## 6.11.3 Output specification and prohibitions

The prompt requires a fixed seven-section structure: recommendation, why the player merits consideration, performance and valuation evidence, why the optimizer selected him, key risks and uncertainties, what the model does not know, and recommended human due diligence.

Four prohibitions apply:

1. **No unsupported numbers.** Only figures present in the payload may appear.
2. **No invented attributes.** Injuries, contracts, personality, tactical fit, scouting assessment and willingness to move are unobservable and may not be asserted.
3. **No transaction recommendation.** The brief recommends investigation. Section 7.4 established that valuation gaps do not identify exploitable opportunities.
4. **No speculative causation, hedged or otherwise.** *May, might, possibly, likely, suggests* do not make an unsupported causal claim acceptable. The permitted form states the observation and then states that the cause is unknown.

The fourth prohibition was added after review identified hedged inference — *"his limited minutes may indicate fitness problems"* — as a more probable failure mode than outright fabrication, because such phrasing reads as helpfulness rather than invention.

## 6.11.4 The fidelity validator

Generated briefs pass through a frozen validator applying six checks:

| Check | Tests |
|---|---|
| Numerical fidelity | Every number traces to the payload |
| Unsupported claims | No invented injury, contract, personality, tactical or scouting assertion |
| Speculation control | No hedged causal claim about an unobservable |
| Structural completeness | All seven sections present |
| Decision consistency + uncertainty disclosure | Recommends investigation, never a transaction; states exit risk and model limitations |

The validator is **negative-control tested**: a checker that passes every document demonstrates nothing. Deliberately fabricated numerical and qualitative claims are inserted into otherwise compliant briefs, and the validator must detect them. This testing exposed a genuine defect during development — markdown ordered-list markers were being parsed as numeric claims — which was corrected before evaluation.

## 6.11.5 Execution environment

The original implementation called the Anthropic API from a scripted harness. That path was not used. The evaluation was instead conducted through **conversational language-model invocation**, using the identical structured payload, the identical prompt specification and the identical frozen validator.

This is stated plainly because the distinction matters for reproducibility: the briefs were not produced by an authenticated API call, and the report makes no claim that they were. The provider is not the research object. The object is whether a constrained generative layer can translate validated analytical output without introducing unsupported content, and that question is unaffected by which interface performed the inference.

## 6.11.6 Three-arm evaluation design

| Arm | Generator | Independence from validator authorship |
|---|---|---|
| **A** | Deterministic template — no language model | Full |
| **B** | Claude, conversational | **None** — the same model family authored the validator |
| **C** | GPT, conversational | **Partial** — different model family, but with visibility of the validator design through the project interaction |

Arm A establishes that the validator does not falsely reject compliant structured output. Arm B is a live generation but carries no independence: a model evaluated against checks it designed demonstrates little. Arm C was added specifically to reduce that shared-origin limitation.

Arm C's independence is **partial, not full**, and the report does not describe it otherwise. The generating model had visibility of the check design through the project conversation, so procedural coupling remains.

Two provenance controls were applied before Arm C was evaluated, both prompted by earlier defects:

- **Payload provenance.** The payload used for Arm C was verified byte-identical to the canonical file. Had the generator amended the facts, the arms would not have been comparable.
- **Validator provenance.** The validator's checksum was verified unchanged against the delivered copy, establishing that no check was adjusted for this run.

A result reported by a generator is not evidence. Only the frozen validator's output on the delivered artifacts is treated as an Arm C result.
