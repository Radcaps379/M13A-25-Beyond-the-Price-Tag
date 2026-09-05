# Recruitment Committee Brief — Facundo Buonanotte

**Midfield · Leicester City · England - Premier League · age 20.0**

## Recommendation
Facundo Buonanotte is put forward for further investigation, not for an immediate approach. The analytical system identifies him as a candidate on quality and development grounds; it cannot establish that a transaction would represent value, and its own back-test found no reliable link between model-implied valuation gaps and subsequent returns.

## Why the player merits consideration
He sits in the 86th percentile for performance among players in his position, with a development-potential score of 0.77. At age 20.0 he retains substantial resale runway under the club's recruitment horizon.

## Performance and valuation evidence
Current market value is EUR 20.0m against a model-implied value of EUR 20.3m, a difference of +1.5%. He recorded 1,514 league minutes at 0.416 goal contributions per 90.

Factors raising the model's valuation:
- age (+0.764)
- goal contributions per 90 (+0.137)
- plays in Spain - LaLiga (+0.120)
- plays in France - Ligue 1 (+0.116)

Factors lowering it:
- league minutes played (-0.143)
- minutes per appearance (-0.099)
- club squad size / rotation (-0.082)
- disciplinary record (-0.055)

## Why the optimizer selected him
Selected under a EUR 50m budget with one defender, one midfielder and one attacker required. Scored on quality 86th percentile, development potential 0.77, value efficiency 0.57, against a risk component of 0.24.

## Key risks and uncertainties
Predicted probability of falling below 900 top-5 league minutes next season is 24.9%, from a model with a held-out AUC of 0.732. Model uncertainty for his segment scores 0.219. The valuation model carries a median error of 43.9% on held-out data.

A known limitation applies directly here: The model systematically under-values players aged 21 and under and over-values players aged 28 and over. This gradient replicates across three consecutive seasons.

## What the model does not know
The system observes match statistics, age, position, league and valuation history. It has no information on:
- contract length and expiry
- injury history and current fitness
- scouting and tactical assessment
- off-field circumstances and player willingness
- agent and release-clause situation

The back-test finding is material: The hypothesis that model residuals identify exploitable undervaluation was tested out-of-sample and NOT supported (p = 0.307). Players flagged by residual left top-5 football at 3.7x the benchmark rate (30.1% vs 8.2%, p = 2.6e-11).

## Recommended human due diligence
1. Verify contract length, expiry and any release clause.
2. Obtain injury and fitness history from medical staff.
3. Commission live scouting on tactical fit and playing style.
4. Establish the selling club's position and the player's willingness.
5. Treat the valuation gap as a question to investigate, not evidence of value.
