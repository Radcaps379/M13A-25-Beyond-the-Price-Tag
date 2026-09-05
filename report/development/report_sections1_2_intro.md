# Section 1 — Introduction
### *Beyond the Price Tag* · IIM Ranchi · Sports Analytics (WAI)

---

## 1.1 Transfer spending as a capital-allocation decision

A football club's transfer budget is finite, committed under time pressure, and largely irreversible once spent. A signing that does not work out cannot be unwound at cost: the fee is sunk, the wage commitment persists for years, and the squad slot the player occupies is unavailable to anyone else. In this respect recruitment resembles capital budgeting more closely than it resembles shopping — a set of interdependent, constrained, long-horizon commitments made with incomplete information about their eventual return.

Clubs nonetheless approach the decision one player at a time. A target is identified, negotiated for, and signed; attention then moves to the next. The budget functions as a running balance rather than a portfolio to be allocated, and the question *"is this player worth the fee?"* is asked far more often than *"is this combination of players the best use of what we have?"*

## 1.2 Why conventional valuation is difficult

The natural response is to establish what a player is worth and compare it to the asking price. This turns out to be harder than it sounds, for three reasons.

First, **there is no observable price for most players.** A transfer fee exists only when a transfer occurs, and most players in any season do not move. In the dataset underlying this study, only a tenth of transfer records carry a positive fee at all. The remainder are free transfers, loans and youth movements. Any valuation framework covering a full player population must therefore work against an estimated valuation rather than a transacted price — and that estimate is itself a construct, not a fact.

Second, **valuation is heavily confounded by context.** The same performance commands materially different valuations depending on the player's age, position and competition. A striker's goal contribution and a goalkeeper's are not comparable quantities, and a season in one league is not priced like the same season in another.

Third, and most importantly, **much of what determines a player's price is not publicly observable.** Contract length, injury history, tactical role, relationship with the coaching staff, agent situation and willingness to move are all material to a valuation and none appears in public match data. Any model built on performance statistics is working with a partial view, and the gap between what it can see and what the market can see is precisely where its errors will live.

## 1.3 What observable performance data can offer

Public data has nonetheless improved substantially. Match-level records for Europe's major leagues now provide minutes, appearances, goals, assists and disciplinary records for tens of thousands of player-seasons, linked to valuation histories that extend over a decade. This supports a specific and useful question: **how much of a player's market valuation is explained by what is publicly observable about their football?**

That question is answerable, and its answer is informative in both directions. A high proportion suggests valuation is broadly grounded in performance. A large unexplained remainder is more ambiguous — it might indicate that the market is mispricing players, or that the model is missing information the market possesses. Distinguishing between those two interpretations is not a technical detail. It is the entire question on which a recruitment decision turns.

## 1.4 Why explainability is a requirement, not a feature

A recruitment committee cannot act on a number it cannot interrogate. If a system asserts that a player is worth substantially more than his price, the immediate and correct response is *why does it think so, and how confident should we be?*

This makes explainability a functional requirement of the system rather than a presentational addition. It also imposes a second obligation that is easier to overlook: a decision-support tool must be able to communicate **what it does not know**. A model that explains its reasoning persuasively while remaining silent about its blind spots is more dangerous than one that offers no explanation at all, because the explanation lends unearned confidence to an estimate built on partial information.

## 1.5 The research question

This project therefore treats market inefficiency as something to be **tested rather than assumed**. It does not begin from the position that clubs systematically misprice players and that a model can exploit this. It begins from a narrower and more answerable question:

> **Can observable football fundamentals support a useful valuation and recruitment-decision framework — without assuming that every unexplained valuation gap represents a market inefficiency?**

The distinction matters because the two most plausible explanations for a model-market disagreement have opposite managerial implications. If the market is wrong, the discrepancy is an opportunity. If the model is missing something, the same discrepancy is a warning. A system that cannot tell these apart, or that assumes the first by default, will systematically recommend the players a club should most carefully avoid.

Whether the framework built here can distinguish between them — and what happens when that capability is subjected to out-of-sample testing — is the subject of the remainder of this report.

---

# Section 2 — Problem Statement, Motivation and Novelty

---

## 2.1 Problem statement

A club must allocate finite transfer capital across players who differ in position, age, performance level, valuation uncertainty and the risk that they will not deliver the playing time expected of them — while satisfying specific positional requirements and working from information that is materially incomplete.

The decision has four properties that shape any system intended to support it:

**It is constrained, not open-ended.** A budget cannot be exceeded, positional gaps must actually be filled, and a portfolio of five wingers does not solve a defensive problem regardless of how favourably each is priced.

**It is made under partial observability.** The information available publicly is a strict subset of the information available to the market. Contract, medical, tactical and personal circumstances are absent.

**It is heterogeneous across the player population.** Performance means different things in different positions, valuations scale differently across leagues, and the reliability of any estimate varies systematically by segment.

**It is irreversible and long-horizon.** Consequences persist for years, which makes the cost of a confidently wrong recommendation considerably higher than the cost of a cautious one.

A useful system must therefore do more than rank players by apparent value. It must indicate how confident it is, what it cannot see, and how a given candidate fits alongside the others a club might sign.

## 2.2 Motivation

The project's founding hypothesis was straightforward and widely held: that a valuation model built from observable performance, age, position and career trajectory could identify players whose market valuations appear disconnected from their fundamentals, and that such players would represent recruitment opportunities.

The hypothesis is plausible. If performance drives value, then players whose performance exceeds what their valuation implies are, on the face of it, underpriced.

**This project treats that proposition as a hypothesis to be tested rather than a premise to be built upon.** That decision determined the structure of the entire study. The mispricing claim was formalised as a falsifiable statement, a testing procedure was specified in writing before any outcome was examined, thresholds were fixed on validation data and applied once to a held-out season, and the result — whatever it turned out to be — was accepted rather than iterated upon.

The motivation for this discipline is practical rather than academic. A recruitment system that recommends players on the basis of an untested assumption does not merely fail to add value; it directs scarce scouting resources and irreversible capital toward whichever players the model happens to misjudge most severely. The cost of an unvalidated recruitment signal is borne in real transfers.

## 2.3 Novelty

The novelty of this project does not lie in applying machine learning to football valuation, which is well-established, nor in any individual algorithm used. Gradient boosting, logistic regression, integer programming and SHAP are all standard tools.

**The contribution is the integrated decision framework and the managerial logic that governs it** — specifically, a framework whose design was determined by empirical evidence rather than by initial intent. Seven elements constitute that contribution:

**1. A fundamental valuation model with strict time-consistency.** Market value is modelled from performance, age, position, league and *performance* trajectory. Career trajectory is deliberately defined through performance history rather than valuation history, so that the model explains value from football rather than reproducing the market's own persistence.

**2. A formally tested — and unsupported — market-mispricing hypothesis.** The central claim was subjected to a pre-registered out-of-sample test with the selection rule fixed in advance. Two specifications were tested and the investigation stopped, rather than continuing until a specification reached significance. The negative result is a finding of the study, not a failure of it.

**3. Discovery of a strong exit-risk relationship within the residual.** The diagnostic that invalidated the mispricing interpretation revealed a substantially stronger relationship running the opposite way: unexplained valuation gaps predict subsequent departure from top-flight football rather than appreciation.

**4. An independently validated exit-risk model.** That relationship was converted from a back-test observation into a calibrated predictive component, validated under the same time-based discipline as the valuation model.

**5. A risk-aware constrained transfer-budget optimizer.** The original objective — maximise the valuation gap — was withdrawn on evidence and replaced with a formulation combining position-appropriate quality, development potential and value efficiency against validated exit risk and model uncertainty, under budget, positional, quality, age and confidence constraints. Weights and constraints were declared in a written specification before execution.

**6. Explainability separating prediction explanations from selection explanations.** Two distinct questions receive two distinct answers: SHAP accounts for why the model produced a given valuation, while the optimizer separately accounts for why a player was selected. Conflating them would allow a persuasive valuation explanation to substitute for a selection rationale.

**7. A guarded generative-AI layer for committee communication.** The language model receives only validated structured outputs and performs no analysis. Every brief is machine-audited for numerical fidelity, unsupported claims, speculative causal inference, decision consistency and uncertainty disclosure, with the auditor itself verified against deliberately planted violations.

Taken together, these describe a system that does something different from what the project set out to build. It does not identify undervalued players. It helps a recruitment committee distinguish candidates worth investigating from apparent bargains that more likely reflect model error or hidden risk — and, for each candidate, states which of those it cannot tell apart.

That is a narrower claim than the project began with, and it is the claim the evidence supports.
