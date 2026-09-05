# Section 3.10 — Explainable AI
### *Beyond the Price Tag* · to be inserted into Section 3, Design and Methodology

---

## 3.10.1 Purpose and scope

The valuation model is a histogram-based gradient-boosted ensemble (`HistGradientBoostingRegressor`), which is not directly readable. For a system whose stated purpose is to support recruitment and finance decisions, an unreadable model is not merely inelegant — it is unusable, because a committee cannot act on a number it cannot interrogate.

SHAP (SHapley Additive exPlanations) is applied to Model 1 for two distinct purposes:

1. **Model explainability** — establishing what generally drives model-implied valuation, and why a specific player receives a specific figure.
2. **Recruitment decision support** — presenting each shortlisted player's positive drivers, negative drivers, and, critically, **what the model does not know**.

The second purpose exists because of the Phase 7 result. A model explanation that persuasively accounts for a high implied value could easily be mistaken for evidence that a player is underpriced. Section 4.4 established that this inference is unsafe. The explainability layer is therefore designed to constrain interpretation, not merely to justify predictions.

## 3.10.2 Method

SHAP values are computed with a tree-path-dependent explainer on the **held-out 2024/25 season** (n = 1,508), using the frozen Model 1 refitted on training seasons only. Values are expressed in the deflated log-valuation units in which the model is estimated, and are additive: each player's prediction equals the base value plus the sum of that player's SHAP contributions.

Two levels of aggregation are reported. **Global importance** is the mean absolute SHAP value per encoded feature, which measures how much a feature moves predictions overall irrespective of direction. **Family importance** sums those values across the feature groups defined in the feature dictionary, giving a reading at the level a manager can actually reason about.

## 3.10.3 Two kinds of explanation, deliberately separated

The system answers two different questions, and conflating them would misrepresent how a recommendation was produced.

| | Question answered | Mechanism | Example |
|---|---|---|---|
| **Prediction explanation** | *Why did the model value this player at this figure?* | SHAP decomposition of Model 1 | Age and minutes raise Coppola's implied value; Serie A and squad rotation lower it |
| **Selection explanation** | *Why did the system recommend this player for the portfolio?* | Optimizer score components and binding constraints | Coppola was selected on quality percentile 89, potential 0.691, value efficiency 0.931, against risk 0.327 |

SHAP explains a *number*. The optimizer explains a *choice*. A player may have a fully explicable valuation and still not be selected, because the portfolio is constrained by budget, positional requirements, exit risk and model uncertainty. Both explanations are reported for every shortlisted player, and the dashboard presents them as separate panels.

## 3.10.4 Reading league contributions under baseline encoding

One presentational caveat requires explicit statement, since the raw output is otherwise easy to misread.

Categorical variables are one-hot encoded with the first level dropped, so England (Premier League) is the omitted baseline. For a Premier League player, every other league indicator takes the value zero — and SHAP correctly assigns a contribution to those zeros. The output therefore shows entries such as *"plays in Spain – LaLiga: +0.120"* for a player who plays in England.

**These are to be read as the contribution of *not* playing in that league.** For a Premier League player, the combined positive contributions across the omitted league indicators represent the Premier League valuation premium identified in Section 4.1, where league medians differ 3.3×. In the dashboard and in generated briefs, these terms are consolidated into a single readable "league context" line rather than presented as separate indicators, to avoid the misreading.

## 3.10.5 Residual-bias audit

SHAP describes what drives the model. It does not reveal where the model is systematically *wrong*. These are different questions, and the second is more consequential for this project.

A separate audit therefore examines the **mean signed residual** (observed minus model-implied log value) by position, league and age band on the held-out season. A mean residual materially above zero indicates the model systematically under-values that group; materially below zero, that it over-values them. A threshold of ±0.05 log units is used to distinguish material from immaterial patterns.

This audit is reported in Section 4.8 and its managerial implications in Section 5.7. It is described throughout as **systematic residual heterogeneity**, not as "fairness bias," since no formal fairness criterion is defined in this project and the groups examined are competitive rather than protected characteristics.

## 3.10.6 What the explainability layer must not be used to claim

Three constraints are imposed on how SHAP output may be interpreted, each traceable to an earlier finding:

1. **A SHAP explanation of a high implied value is not evidence of undervaluation.** Section 4.4 found no relationship between valuation residuals and subsequent relative appreciation.
2. **Feature importance is not causal.** SHAP attributes a model's behaviour, not the world's. Age dominating the explanation means the model relies on age, not that age causes market value.
3. **Explanations cannot cover omitted information.** The model observes no contract length, injury history, disciplinary record beyond cards, scouting assessment or off-field circumstance. Section 4.5 established that unexplained valuation gaps predict exit rather than appreciation, which is consistent with these omissions carrying real information. Every shortlist explanation therefore carries an explicit "what the model does not know" statement alongside the player's validated exit probability.
