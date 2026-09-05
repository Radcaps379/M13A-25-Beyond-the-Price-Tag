> # HISTORICAL DEVELOPMENT DOCUMENT — NOT THE FINAL PROJECT METHODOLOGY
>
> This records the **initial project plan**, written before any analysis was run.
> Several things in it were subsequently changed by evidence and do not describe
> the submitted project:
>
> - It names XGBoost/LightGBM. The final estimator is scikit-learn's
>   **HistGradientBoosting**, imported directly with no fallback.
> - It describes a greedy/knapsack fallback for the optimizer. The final
>   optimizer **requires PuLP** and treats the greedy heuristic as a comparison.
> - It frames the objective as identifying **undervalued** players. That
>   hypothesis was tested out-of-sample and **was not supported**; the system was
>   rebuilt around exit risk.
>
> The final methodology is in `report/final/` and the current source pipeline.

---

# Beyond the Price Tag — Full Project Guide
### Explainable AI decision-support for football player valuation & transfer-budget allocation
### MBA · Working-with-AI (WAI) component

This is your working document for the whole term. It is built specifically around the **`davidcariboo/player-scores`** dataset (the maintained Transfermarkt export) as the single safe backbone, and around the four differentiators that separate this from a plain "rank players and regress" project: **explainability (SHAP)**, a **budget-constrained optimizer**, **generative-AI recruitment briefs**, and a **back-test**.

Your professor has invited you to explore beyond the syllabus, so the guide now also includes two **optional stretch layers** that push past a standard MBA analytics curriculum without touching your core scope or data: a behavioral **anchoring-bias analysis** and a **transfer-market network analysis** (see Part C2). Both reuse tables you're already pulling — no new datasets, no new joins — and both are explicitly sequenced *after* the core four differentiators, so they add ambition without adding risk.

**The one architectural rule everything obeys:** the core pipeline runs on `davidcariboo/player-scores` alone, and **every join is an integer-ID merge** (`player_id`, `club_id`). There is no step anywhere that matches players by name. Enrichment datasets are optional and never load-bearing. This is the whole reason we chose football over IPL — it keeps data work in the *write-it-once, it-just-runs* category, not the *ongoing-judgment-call* category.

---

## Part A — What we're building, in one picture

A player flows through four layers, and each layer is a graded deliverable:

1. **Valuation model** — from a player's performance, age, position and trajectory, predict a *fair* market value.
2. **Mispricing signal** — compare fair value against (a) their current Transfermarkt valuation and (b) the fee actually paid → flag *undervalued* and *overvalued* profiles.
3. **Optimizer** — given a budget (say €50M) and positional needs, output the *portfolio* of undervalued signings that maximizes performance-per-euro.
4. **Generative-AI briefs + back-test** — auto-write a board-ready one-pager per target, and prove the model works by checking whether players it flagged as undervalued later appreciated or outperformed.

The whole thing is framed as **capital allocation under constraint** — a decision-support tool for a club's recruitment and finance teams, not a data-science demo.

**Two optional layers sit on top of this, once the four core differentiators are solid:** a test for whether the market *anchors* on past fees rather than pricing performance, and a network view of *which clubs* systematically over- or under-pay. Neither is required to pass or to hit distinction — they exist purely to use the "explore outside the syllabus" permission you were given. Full detail in Part C2.

---

## Part B — The data, and exactly who does what

This section is the one that matters most for you, so it's explicit about the division of labour.

### The backbone: `davidcariboo/player-scores`
It's a set of linked CSVs. The ones we use:

| File | What it gives us | Role in project |
|---|---|---|
| `players.csv` | player_id, name, DOB, position, foot, height, current club | Identity + static predictors |
| `player_valuations.csv` | player_id, date, market_value_in_eur | **Target variable** + career-trajectory history + back-test |
| `appearances.csv` | player_id, game_id, minutes, goals, assists, cards | **Performance predictors** (aggregated per season) |
| `transfers.csv` | player_id, transfer fee, from/to club, date | **Fee-paid comparison** (the "vs. actual price" half) |
| `clubs.csv` / `competitions.csv` | club_id, league, country | League/level context + filtering |

Every one of these joins on `player_id` (and `club_id` where relevant). No fuzzy matching, ever.

### Enrichment (optional, never required)
- **`atakanakn`** (pre-joined Transfermarkt + WhoScored) → advanced stats (xG, key passes) for a robustness check. Someone already did the join, so you inherit zero matching work. The core model must run fine without it.
- **`kberkek00`** → backup backbone if davidcariboo has a coverage gap for a league/season you want.

### Reproducibility tip
davidcariboo **refreshes weekly**. Download it once, save the CSVs to a local `/data/raw/` folder, and work off that frozen copy all term so results don't shift week to week.

### Who does what — the honest split
| Task type | Who | How it works |
|---|---|---|
| Writing loader/cleaning/merge scripts | **Me** | Top-to-bottom runnable, plain-English comments |
| Filtering choices (which leagues, treat loans/free transfers/missing fees how) | **Me proposes, you accept/nudge** | I pick a sensible default and flag it; you say yes or tweak |
| Running the scripts | **You** | Copy, run, paste me any output |
| Fixing errors | **You paste the message → I fix** | You never debug alone |
| Modelling, Excel, dashboard, report, deck, demo | **Me writes / You run & own the narrative** | Same pattern throughout |

The one thing I can't promise is a *literally* frictionless dataset — every real dataset has missing values and filtering calls. Football keeps that friction **deterministic and one-time** (decide the rule once, script it) instead of the endless case-by-case name-matching IPL would have forced.

---

## Part C — The 13-phase roadmap

For each phase: **objectives · tasks · tools · effort · outputs · common mistakes · who does what**.

### Phase 1 — Problem definition
- **Objectives:** Lock the managerial decision, the fair-value definition, and the success metric (back-test: do flagged-undervalued players appreciate/outperform?).
- **Tasks:** One-page problem statement; define "fair value" as model-predicted value from performance+age+position+trajectory; fix scope (leagues, seasons); write the three research questions.
- **Tools:** This guide; a doc.
- **Effort:** 3–4 hrs.
- **Outputs:** Scoping note.
- **Common mistake:** Starting from the model instead of the decision.
- **Who:** You draft from this guide; I review and tighten.

### Phase 2 — Data acquisition
- **Objectives:** Get davidcariboo locally and frozen, reproducibly.
- **Tasks:** Download the CSVs; save to `/data/raw/`; a small script that loads each file and prints shape + columns so we confirm what we have.
- **Tools:** Kaggle (download), Python `pandas`.
- **Effort:** 2–3 hrs.
- **Outputs:** Frozen raw data + a "data inventory" printout.
- **Common mistake:** Working off the live/weekly version and getting shifting numbers.
- **Who:** I write the loader; you run it and paste the output.

### Phase 3 — Data cleaning & assembly (the important one)
- **Objectives:** ONE clean analysis table at **player-season** grain, built purely by ID merges.
- **Tasks:** Aggregate `appearances` to player-season (sum minutes/goals/assists/cards, count games); attach static fields from `players`; compute age at season; attach league/level from `clubs`; attach the market value as of each season from `player_valuations`; attach transfer fees from `transfers` where they exist. Apply the filtering rules (below) and report how many rows each rule drops.
- **Filtering choices I'll default (you accept/nudge):** keep top-5 European leagues + optionally top 2 more; players with ≥ ~500–900 league minutes in a season (drop tiny samples); drop loan moves and free/€0 transfers from the *fee* analysis (keep them for valuation); cap absurd outliers.
- **Tools:** `pandas`.
- **Effort:** you: minimal (run + review); me: the real work.
- **Outputs:** `player_season.csv` (analysis-ready) + a short data-quality report (rows kept/dropped, missingness).
- **Common mistake:** Leaking the future — e.g., using end-of-season value to predict that same season. We align features to *before* the value we predict.
- **Who:** I write it all; every judgment call is flagged in comments for your yes/no.

### Phase 4 — Exploratory analysis
- **Objectives:** Understand value/performance distributions; get an early look at where mispricing lives.
- **Tasks:** Value by age, position, league; performance vs. value correlations; distribution of transfer fees vs. valuations; spot obvious under/over-valued cases as a sanity check.
- **Tools:** `pandas`, `matplotlib`/`seaborn`, `plotly`.
- **Effort:** 6–8 hrs.
- **Outputs:** EDA notebook + 5–6 "story" charts you'll reuse in the deck.
- **Common mistake:** Pretty charts with no link to the decision. Every chart earns its place by informing valuation or mispricing.
- **Who:** I write the notebook; you run it and pick which charts speak to you.

### Phase 5 — Feature engineering
- **Objectives:** Build the signals that define fair value, including the **career-trajectory** edge.
- **Tasks:** Per-90 metrics (goals/90, assists/90, contributions/90); age and age² (value peaks then declines); position encoding; minutes/availability; **trajectory features** — value growth over prior seasons, form trend, "young-and-rising" flag; league-strength adjustment.
- **Tools:** `pandas`, `numpy`, `scikit-learn`.
- **Effort:** 8–12 hrs.
- **Outputs:** Feature table + a plain-English feature dictionary.
- **Common mistake:** Target leakage (any feature that secretly encodes the value we predict). I'll audit for it.
- **Who:** I write; you review the feature dictionary so you can explain each one in the report.

### Phase 6 — Model building
- **Objectives:** Fair-value model + the budget optimizer.
- **Tasks:** Baseline linear regression first (interpretable, sets the bar); then gradient boosting (XGBoost/LightGBM); predict log-value (values are skewed). Then the optimizer: given budget + positional slots, select the set of undervalued players maximizing predicted performance-per-euro — a knapsack/greedy version first (always works, easy to explain), ILP via `PuLP` if time allows.
- **Tools:** `scikit-learn`, `xgboost`/`lightgbm`, `PuLP`.
- **Effort:** 14–18 hrs.
- **Outputs:** Trained valuation model + working optimizer.
- **Common mistake:** Jumping to the fancy model before a clean baseline; predicting raw (not log) skewed values.
- **Who:** I write; you run and we read results together.

### Phase 7 — Model evaluation
- **Objectives:** Prove it works and is honest; produce the **killer result**.
- **Tasks:** Time-based validation (train past seasons → test a later one, never random split); error by position/age/league; **back-test** — take players the model flagged undervalued in season *t*, check whether their value/output rose in *t+1*; robustness with the enrichment stats.
- **Tools:** `scikit-learn`, custom back-test.
- **Effort:** 10–12 hrs.
- **Outputs:** Evaluation section + one memorable back-test number.
- **Common mistake:** Random splits that leak the future; reporting only average error with no segment breakdown.
- **Who:** I write the back-test; you own interpreting the story.

### Phase 8 — Generative-AI integration
- **Objectives:** Turn numbers into board-ready language.
- **Tasks:** Feed structured model + SHAP output to an LLM (Claude/GPT API) to draft a one-page recruitment brief per shortlisted target (why undervalued, key strengths, risks, positional fit); guardrail it to use *only* the provided numbers; generate a short transfer-window summary memo.
- **Tools:** Anthropic/OpenAI API, structured JSON prompting.
- **Effort:** 8–10 hrs.
- **Outputs:** Brief generator + sample briefs.
- **Common mistake:** Letting the LLM invent stats. It gets fed data and is constrained; you spot-check every brief.
- **Who:** I write the prompt/pipeline; you review sample briefs for tone.

### Phase 9 — Dashboard development
- **Objectives:** Make it usable and demo-able.
- **Tasks:** Interactive app — search a player → see fair value vs. market value vs. fee, the SHAP explanation, the mispricing flag; a budget slider that runs the optimizer and shows the recommended shortlist; a button that shows the generated brief.
- **Tools:** **Streamlit** (fastest script-to-app) or Plotly Dash; a claude.ai artifact is an option for the demo.
- **Effort:** 12–16 hrs.
- **Outputs:** Working dashboard.
- **Common mistake:** Over-building the UI at the expense of the analysis.
- **Who:** I write it; you run and drive it in the demo.

### Phase 10 — Managerial insights
- **Objectives:** Convert results into recommendations a club could act on.
- **Tasks:** Where the market systematically misprices (which positions/ages/leagues); the value-for-money case; sensitivity to budget size and assumptions; a concrete "here's a €50M shortlist" example.
- **Tools:** Doc/deck.
- **Effort:** 6–8 hrs.
- **Outputs:** Insights + recommendations section.
- **Common mistake:** Stopping at model metrics with no business translation.
- **Who:** We do this together — it's the MBA core; I structure, you sharpen the judgment.

### Phase 11 — Report
- **Objectives:** A polished postgraduate write-up.
- **Tasks:** Intro/problem, literature (the interpretable-ML valuation lineage — your ScienceDirect paper anchors this), data, method, results, back-test, ethics/robustness, recommendations, limitations.
- **Tools:** Word/Markdown/LaTeX.
- **Effort:** 12–16 hrs.
- **Outputs:** Final report.
- **Common mistake:** Method-heavy, decision-light narrative.
- **Who:** I draft sections; you own voice and the managerial argument.

### Phase 12 — Presentation
- **Objectives:** Tell the story in ~10–12 slides.
- **Tasks:** Decision → approach → one killer result (the back-test) → dashboard screenshot → the €50M shortlist → recommendation.
- **Tools:** PowerPoint/Slides.
- **Effort:** 6–8 hrs.
- **Outputs:** Deck.
- **Common mistake:** Slides of code and metric tables instead of a narrative.
- **Who:** I build the skeleton; you present it.

### Phase 13 — Recorded demonstration
- **Objectives:** Show the tool making a recruitment decision end-to-end.
- **Tasks:** Script a 4–6 min walkthrough: set a budget → see undervalued targets, explanations, and a generated brief → state the recommendation.
- **Tools:** OBS/Loom.
- **Effort:** 3–4 hrs.
- **Outputs:** Demo video.
- **Common mistake:** Unscripted rambling; demo the *decision*, not the codebase.
- **Who:** I write the script; you record.

---

## Part C2 — Beyond-syllabus stretch layers (optional)

These two exist for one reason: your professor said you could explore outside the syllabus, and a standard MBA analytics course doesn't go here. Both are **strictly optional** — the four core differentiators (SHAP, optimizer, GenAI briefs, back-test) already deliver a distinction-level project on their own. Attempt these only once Phase 7 (evaluation) and ideally Phase 9 (dashboard) are solid. If either core milestone slips, skip both without penalty.

Both share one property that makes them low-risk to attempt: **they use tables already sitting in your core pipeline** (`transfers.csv`, `player_valuations.csv`, `clubs.csv`) — no new dataset, no new download, no new join risk.

### Stretch A — Anchoring-bias analysis (behavioral economics)
- **Objectives:** Test whether a player's market valuation stays inflated *after* a big transfer fee, independent of how they actually perform — the classic "anchoring heuristic" from behavioral finance, applied to the transfer market.
- **Tasks:** For each transfer in `transfers.csv`, pull the player's valuation trajectory before and after the move from `player_valuations.csv` (e.g. value at t−1yr, at the transfer, at t+1yr, t+2yr) alongside their performance over the same windows (goals/assists/90 from `appearances.csv`). Run a simple event-study-style regression: does the fee paid still predict the player's post-transfer valuation *after* controlling for their actual performance change? A significant, persistent fee effect is evidence of anchoring. Segment by fee size (marquee vs. modest moves) and league to see where the effect is strongest. Pick 2–3 well-known expensive transfers as illustrative "expected vs. actual valuation trajectory" case-study charts for the deck.
- **Tools:** `pandas`, `statsmodels` (the standard library for this kind of regression/event-study), `matplotlib`.
- **Effort:** 6–8 hrs.
- **Outputs:** One regression table + 2–3 trajectory charts + a one-paragraph finding, written up as its own short section.
- **Common mistake:** Overclaiming causality. There's no clean control group here, so frame this as *suggestive evidence* of a market inefficiency, not proof — and watch for reverse causality (a high fee might partly reflect private information about future performance, not just anchoring).
- **Who:** I write the event-study script and run the regression; you interpret the result and frame it as a market-inefficiency insight for the report and deck.
- **Where it plugs in:** Feeds directly into Phase 10 (managerial insights) as a "why the market misprices" finding — pairs naturally with your existing mispricing-signal layer. Best attempted in **Week 9–10**, right after the back-test, since it reuses the same before/after valuation logic.

### Stretch B — Transfer-market network analysis (market structure)
- **Objectives:** Move from player-level mispricing to a market-structure view: which clubs sit at the center of overpaying or underpaying patterns, and are there identifiable "trading circles"?
- **Tasks:** Build a directed graph — nodes are clubs (`clubs.csv`), edges are transfers (`transfers.csv`), edge weight is the fee paid or, better, the mispricing residual (fee minus your model's predicted fair value). Compute centrality measures (degree, weighted degree, betweenness) to find hub clubs. Color-code the graph by average over/under-payment per club. Optionally run community detection (e.g. Louvain) to surface clusters of clubs that trade heavily with each other. Filter to the top-N clubs by transfer volume before visualizing, or the graph turns into an unreadable "hairball."
- **Tools:** `networkx` (graph construction + centrality — the standard Python graph library), `pyvis` or `plotly` for an interactive visual, `pandas`.
- **Effort:** 10–12 hrs (higher than Stretch A — new library, new visualization type).
- **Outputs:** A network graph figure + a short "market structure" write-up (e.g. "these five clubs are the most consistent overpayers as buyers").
- **Common mistake:** Reading centrality as causal — big, resource-rich clubs simply transact more, which inflates their centrality regardless of pricing skill. Note this as a confound, don't ignore it.
- **Who:** I write the graph-construction and centrality script; you decide which clubs or clusters make the most interesting story for the narrative.
- **Where it plugs in:** A genuinely separate, visually strong add-on — not required for the thin slice or back-test. Best attempted in **Week 11**, after the dashboard (Phase 9) is working and only if you have runway, explicitly framed in the report as the "beyond syllabus" flex your professor invited.

---

## Part D — Technology stack (with justification)

- **Language / IDE:** Python in **VS Code** (+ Jupyter for exploration) — dominant in analytics, best library support, clean to show in a demo.
- **Data wrangling:** `pandas`, `numpy` — the standard; because every join here is ID-based, `merge()` does all the assembly with no matching libraries needed.
- **ML:** `scikit-learn` (baseline + pipelines) + **`XGBoost`/`LightGBM`** — best-in-class for tabular data like this; strong accuracy while staying interpretable via SHAP.
- **Optimization:** **`PuLP`** for the budget-constrained shortlist (clean, well-documented ILP), with a greedy/knapsack fallback that's guaranteed to run and easy to explain.
- **Explainability:** **`SHAP`** — the standard for justifying model outputs to non-technical decision-makers; this is what makes it *decision-support*, not a black box.
- **Generative AI:** Anthropic Claude API (or OpenAI) with **structured JSON prompting** — drafts recruitment briefs from model output; pick one, constrain it to provided numbers, document your prompts in the report.
- **Excel:** for the shortlist deliverable and any figures the finance-team framing wants as a spreadsheet — I'll generate clean, formula-driven sheets.
- **Visualization:** `plotly`/`matplotlib`/`seaborn` for charts; **Streamlit** for the interactive app.
- **Version control / docs:** **GitHub** with a clear README, a reproducible pipeline, a data-provenance note, and the feature dictionary — expected at PG level and strong for recruiting.
- **Stretch A (anchoring bias):** **`statsmodels`** — the standard Python library for regression/event-study analysis; lets us test whether fee paid still predicts post-transfer valuation after controlling for performance.
- **Stretch B (network analysis):** **`networkx`** — the standard Python graph library, for building the club-transfer graph and computing centrality; **`pyvis`** or `plotly` for an interactive network visual if it's worth embedding in the dashboard.

---

## Part E — Engineering a >90% grade

- **One killer result:** the **back-test** number — "players flagged undervalued in 2023 rose ~X% in value the next season vs. ~Y% for the rest." One memorable, business-language figure.
- **Sensitivity analysis:** vary the budget, the minutes threshold, and the fair-value definition; show recommendations are stable (or explain where they aren't).
- **Explainability front-and-centre:** SHAP as *the* trust mechanism, not an appendix.
- **Robustness checks:** time-based validation, error by position/age/league, behaviour on low-minutes players, a cross-check using the enrichment stats.
- **Ethics section:** check whether the model systematically discounts by age or league in ways that could be unfair; state outputs are decision *support*, not verdicts; use only public professional performance data.
- **Two product artifacts:** the interactive dashboard + the generated briefs — they make it feel real.
- **Storytelling:** every deliverable as *decision → evidence → recommendation*, never *data → model → metric*.
- **Differentiation note:** explicitly position against the plain "rank-and-regress" approach — your optimizer, explainability, briefs, and back-test are the tier-up.
- **Beyond-syllabus flex (optional, if time allows):** the anchoring-bias event-study and the transfer-market network analysis (Part C2) — signal that you took the "explore outside the syllabus" instruction seriously, on top of an already-complete core project.

---

## Part F — 12-week milestone plan

Each week: **finish · deliverable · checkpoint · quality bar.** The one non-negotiable is a **working thin end-to-end slice by Week 6**.

| Week | Finish | Deliverable | Checkpoint | Quality bar |
|---|---|---|---|---|
| 1 | Scope locked; title/abstract/data submitted | Scoping note | Decision & metric are unambiguous | A club person would recognise the decision |
| 2 | davidcariboo downloaded & frozen | Raw data + inventory printout | All 5 core files load | Working off a frozen copy |
| 3 | Clean player-season table built | `player_season.csv` + DQ report | Table is all ID-merges, no name matching | Rows kept/dropped documented |
| 4 | EDA | EDA notebook + story charts | Early mispricing signal visible | Every chart tied to the decision |
| 5 | Features incl. trajectory | Feature table + dictionary | No target leakage | Each feature explainable in one line |
| 6 | **Thin slice: baseline value → flag undervalued** | End-to-end v0 | Runs start to finish | A gradable project already exists |
| 7 | Strong model + tuning | Trained model | Beats baseline on time-split | Error analysis by segment done |
| 8 | Budget optimizer | Working optimizer | Respects budget + positional needs | Greedy and/or ILP, explained |
| 9 | Evaluation + **back-test** | Killer number | The back-test result exists | Time-based validation, robustness |
| 10 | SHAP + GenAI briefs | Explainability + brief generator | Briefs use only real numbers | Every brief spot-checked |
| 11 | Dashboard + insights | Streamlit app + recommendations | A non-technical user can drive it | Decision-first, clean |
| 12 | Report + deck + demo | Final report, deck, video | Full narrative arc | Distinction-level polish (Part E) |

### Stretch layer timing (optional — only if ahead of schedule)

| When | What | Condition |
|---|---|---|
| Week 9–10 | Stretch A: anchoring-bias event-study | Only after the back-test (Week 9 core) is done — reuses the same valuation-trajectory logic |
| Week 11 | Stretch B: transfer-market network analysis | Only after the dashboard (Week 11 core) is working, and only if there's runway left |

**If either core milestone slips, drop both stretch layers without penalty.** The four core differentiators alone already exceed a standard-syllabus project — these two exist to use your professor's "explore" permission, not to replace the core scope.

---

## Submission fields (final)

**Title**
> Beyond the Price Tag: An Explainable AI Decision-Support System for Identifying Undervalued Talent and Optimizing Football Transfer Budgets

**Abstract**
> Football clubs commit hundreds of millions to the transfer market each year, yet fees remain anchored to reputation, age, and recent hype as much as to a player's underlying contribution — leaving budgets exposed to systematic overpayment while genuinely undervalued talent hides in plain sight. This project reframes recruitment as a capital-allocation problem and builds an explainable AI decision-support system that estimates a player's fair market value from performance, age, position, and career trajectory, then measures each player against both their current valuation and the fee actually paid to expose where the market is mispriced. Rather than stopping at a ranked list, it uses explainable AI (SHAP) to make every valuation transparent and defensible to recruitment and finance stakeholders, and a budget-constrained optimizer to recommend the portfolio of signings that maximizes performance-per-euro within a club's spending limit and positional needs. A generative-AI layer converts each shortlisted target into a board-ready recruitment brief, and the model is validated by back-testing whether the players it flags as undervalued subsequently appreciate in value or outperform — turning a predictive exercise into an auditable tool a club could defensibly act on. The result is a decision-support system for the recruitment and finance teams who must convert a finite transfer budget into competitive advantage under real constraints.

**Dataset(s)**
> 1. Football Data from Transfermarkt (`davidcariboo/player-scores`) — https://www.kaggle.com/datasets/davidcariboo/player-scores — primary backbone: market values, transfer fees, appearances, valuation history, joined by player/club IDs.
> 2. Football Player Dataset – Transfermarkt + WhoScored (`atakanakn`) — https://www.kaggle.com/datasets/atakanakn/football-player-dataset-transfermarkt-whoscored — pre-joined advanced performance stats for enrichment and robustness checks.
> 3. Transfermarkt Football Database (`kberkek00`) — https://www.kaggle.com/datasets/kberkek00/transfermarkt-datas — recent (2026) alternative backbone for coverage.

**Note:** these fields are already submitted and don't need to change. Both stretch layers in Part C2 run on the same three datasets — no new data source, no resubmission required.
