# Recorded Demonstration — Script
### *Beyond the Price Tag* · slides only, no live software · target 6:30

**Setup.** Presenter view so the speaker notes are visible. Screen at 1920×1080. Nothing else needs to be open: the deck carries the whole demonstration.

**Two numbers to say exactly as written.**
- *"3.7 times the benchmark exit rate, 30.1% against 8.2%"* — the **risk ratio**. The odds ratio is 4.82. Never say "4.8 times more likely."
- *"9.5× observed decile spread, 7.3% at the lowest and 69.5% at the highest"* — the **actual** spread. The predicted spread is 13.4×.

---

## SEGMENT I — Can we estimate what a player should be worth? (0:00–2:00)

### Slide 1 · Title — 0:00
> "Football clubs don't simply buy players. They allocate scarce capital across players, positions and risks.
>
> This project asks: when the transfer budget is finite, who should a recruitment committee investigate? We began by treating that as a player-valuation problem."

### Slide 2 · The managerial problem — 0:20
> "The decision is hard for four reasons. A transfer is largely irreversible. Budgets and squad slots are constrained. Important information, contracts and medical status, is private. And performance means different things across positions, leagues and ages."

*Point to the closing line.*
> "So this is closer to capital budgeting than to shopping."

### Slide 3 · The original hypothesis — 0:40
*Trace the chain left to right.*
> "Performance, age, position and trajectory produce a model-implied valuation. Compare that with the market, and the gap looks like an opportunity."

*Pause on the amber box.*
> "But is the gap actually an opportunity? If the market is wrong, it is. If the model is missing something, the same gap is a warning. Those point in opposite directions, so we treated it as a hypothesis to test, not a premise."

### Slide 4 · Data and design — 1:00
> "15,925 player-seasons, ten seasons, five major European leagues. 2024/25 held out completely: 1,508 players for the final test. Every join is on an integer player ID, no name matching anywhere. Train, then validate, then test once."

### Slide 5 · How the system was built — 1:20
*Don't read twelve boxes. Gesture across them.*
> "Twelve stages, run in order. The point isn't the number. Every stage writes a frozen artifact, so every figure you're about to see traces back to the file that produced it. That property is what made the verification possible later."

### Slide 6 · What explains market value — 1:40
> "The fundamental model reaches an R-squared of 0.678 on the held-out season, against 0.383 for a context-only benchmark. Observable football carries real valuation signal.
>
> But let the model see the player's prior market value and it jumps to 0.884. Two market-derived variables add more than twenty-nine performance features contributed."

*Point to the closing line.*
> "Predicting the market is easier than explaining it. That's why Model 2 isn't our recruitment model: its residual is just deviation from Transfermarkt's own trend."

---

## SEGMENT II — Does a valuation gap mean opportunity? (2:00–3:10)

### Slide 7 · The hypothesis test — 2:00
*Slow down. The slide goes dark; let it register.*
> "Then we tested the actual investment hypothesis. If the gap represents genuine opportunity, the players it flags should subsequently outperform comparable players."

*Pause. A full beat.*
> "They didn't.
>
> The pre-registered signal wasn't significant. We refined it, calibrated the residual, screened for quality and confidence, and it still wasn't significant."

*Point to the right-hand panel.*
> "Two specifications. Then we stopped. We did not keep changing the threshold until significance appeared, because that would have turned a hypothesis test into a search."

### Slide 8 · The discovery — 2:35
> "But the failed hypothesis led somewhere more useful. The same discrepancy was strongly associated with players leaving top-five football altogether.
>
> Flagged players left at 3.7 times the benchmark rate, 30.1% against 8.2%, Fisher exact p of 2.6 times ten to the minus eleven.
>
> So we built a separate exit-risk model. Held-out AUC of 0.732, and calibrated: 7.3% actual exit in the lowest decile, 69.5% in the highest."

*Point to the right-hand card.*
> "Where a model disagrees with the market, the market is usually right. The residual is a warning signal, not an arbitrage signal."

---

## SEGMENT III — How should a committee use this? (3:10–6:30)

### Slide 9 · Explainability — 3:10
> "So we rebuilt the system around that evidence. Two different questions get two different answers.
>
> Take Buonanotte. Market value €20.0 million. Model-implied €20.3 million. There is essentially no valuation gap. Under the original hypothesis he would never have surfaced."

*Pause.*
> "But the optimizer selected him anyway, on quality at the 86th percentile and development potential of 0.77. His value efficiency is the weakest in the portfolio.
>
> So the system is no longer asking who is cheap. It is asking who is worth investigating."

### Slide 10 · The central inversion — 3:45
*The hero slide. Take your time.*
> "This is the central inversion of the project."

*Point top-right.*
> "A large valuation gap combined with high exit risk is not a bargain. It is a warning, and it is exactly the profile a naive bargain-finder would rank first."

*Point top-left.*
> "A large gap with lower risk becomes a candidate for investigation."

*Then, deliberately:*
> "The system never says 'undervalued'. It says: potential valuation discrepancy, investigate."

### Slide 11 · The committee scenario — 4:15
> "So: fifty million euros, one defender, one midfielder, one attacker.
>
> The system selects Lucas Stassin, Diego Coppola and Facundo Buonanotte. €48 million committed, mean quality percentile 88.3, mean predicted exit risk 17.1%."

*Look at the amber box and say it plainly.*
> "I want to be precise about what this shows. It demonstrates how the framework allocates a budget. It does not validate the optimizer. Three players cannot establish effectiveness. The exit-risk model is validated at population level on 1,508 players; the portfolio is an illustration of that validated component."

### Slide 12 · Robustness — 4:50
> "Across six weight configurations, Stassin appears in all six, Coppola in four, Buonanotte in three. The recommendation shows meaningful stability, but it is not invariant, and we report it that way.
>
> And under the tested constraints, budget beyond about €75 million buys nothing. The quality, age and risk constraints bind before the money does. For a sporting director that's a real insight: relaxing a constraint may be worth more than raising the budget."

### Slide 13 · Generative AI — 5:20
> "The system also writes a one-page brief for each shortlisted player. That layer is a subject of the research, not just a feature.
>
> Every brief passes a frozen six-check validator. We ran three arms: a deterministic template, and two different conversational language models.
>
> The interesting result is the failure. One model's brief contained three fabricated figures: it reported 2,079 minutes when the real number was 1,868, and 0.606 goal contributions per 90 when the real number was 0.819."

*Pause.*
> "That brief was fluent, structurally complete, and passed the other five checks. Nothing in the prose signalled a problem. Fluency carried no information about accuracy. Only comparison against the source data exposed it."

### Slide 14 · The interface — 5:50
> "All of this is delivered through an interactive dashboard with five views: set a budget and the optimizer solves live; explore any of the 1,508 players; see why the model valued someone and separately why the optimizer selected them; read the generated brief; and a view explaining what the system does not claim.
>
> It runs from the same frozen artifacts as this deck, and the interactive optimizer reproduces the €48 million portfolio exactly. That last point is the check that matters: the interface is not a separate calculation."

### Slide 15 · How the work was verified — 6:05
> "One more thing, because it's the Working-with-AI contribution.
>
> I used two AI systems and audited them against each other. One built; the second reviewed the delivered files, never the first one's description of them. I adjudicated, and overruled both at different points.
>
> Thirty-nine defects were found. None produced an error message. Every one surfaced by comparing an artifact against the thing that produced it. At one point a portfolio was reported as €48 million while the delivered file contained €41 million. Only artifact-level review could have caught that."

### Slide 16 · The takeaway — 6:20
*Walk down the four steps.*
> "So this is where analytics ends. The system narrows the universe, explains its valuations, quantifies a risk the original approach ignored entirely, and allocates the budget under real constraints."

*Point to the amber rule.*
> "Below this line we need information the model does not have: scouting, medical, contracts, tactical fit. The system says so on every recommendation."

*Final beat. Look at the camera, not the slide.*
> "AI does not replace the recruitment committee. It helps the committee investigate the right players for the right reasons."

---

## Recording notes

**Do**
- Rehearse Segment II alone. The pause after *"They didn't"* is the most important second in the video.
- Say the n = 3 caveat on slide 11 at full volume. Under-claiming reads as confidence.
- Say the three fabricated numbers on slide 13 aloud. They are all plausible, which is the point.

**Don't**
- Say "undervalued" except when quoting the original hypothesis.
- Say "LightGBM" — the valuation model is scikit-learn's HistGradientBoostingRegressor.
- Say "4.8 times more likely" — that is an odds ratio, not a risk ratio.
- Apologise for the negative result. It is the finding.

**If you run long,** compress slide 5 to one sentence and trim slide 12's budget discussion. Do not cut the pause in Segment II or the caveat on slide 11.

**Timing.** Roughly 6:30 at an unhurried pace. Anywhere from 5:30 to 7:30 is fine. There is no benefit in stretching it.
