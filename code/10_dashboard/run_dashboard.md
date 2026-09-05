# Running the dashboard

## Setup

```bash
pip install -r requirements.txt
```

## Run

From the repository root:

```bash
streamlit run code/10_dashboard/dashboard.py
```

It opens at http://localhost:8501

## Required artifacts

All are committed to the repository and resolved automatically by
`code/repo_paths.py`, so no path configuration is needed:

| Artifact | Location |
|---|---|
| `optimizer_input_2024_25.csv` | `outputs/exit_risk/` |
| `shap_all_players.csv` | `outputs/shap/` |
| `recommended_portfolio.csv` | `outputs/optimizer/` |
| `pretest_segment_uncertainty.csv` | `outputs/exit_risk/` |
| `pretest_constants.csv` | `outputs/exit_risk/` |
| Generated briefs | `briefs/claude/`, `briefs/gpt/`, `briefs/template/` |

## The five views

1. **Executive transfer window** — set a budget, positional needs and risk tolerance; the integer program solves live
2. **Player explorer** — any of the 1,508 held-out players, with the gap-versus-risk quadrant
3. **Why this player?** — prediction explanation and selection explanation, kept separate
4. **Committee brief** — the generated document, labelled by which arm produced it
5. **How to read this system** — what the system does, and what it deliberately does not claim

## Notes

- The Executive view re-solves the optimisation live and reproduces the frozen
  €50M portfolio exactly: Stassin, Coppola, Buonanotte, €48.0M committed.
- No player is ever labelled "undervalued". The interface says *potential
  valuation discrepancy, investigate*, and where a large gap coincides with high
  exit risk it says *treat as a warning*.
