# Data Sources

The original raw datasets are not stored in this repository. They are public
Kaggle datasets, and redistributing third-party data is neither necessary nor
appropriate here. This document records exactly what was used, so the analysis
can be traced to its source.

## 1. Primary source

**Football Data from Transfermarkt** — `davidcariboo/player-scores`
https://www.kaggle.com/datasets/davidcariboo/player-scores

Downloaded once and frozen. The public version refreshes weekly; working from a
frozen copy is what makes these results reproducible.

| File | Rows | Role |
|---|---|---|
| `players.csv` | 50,149 | Identity, date of birth, position |
| `player_valuations.csv` | 656,301 | Target variable and valuation history |
| `appearances.csv` | 1,894,350 | Performance, aggregated to player-season |
| `transfers.csv` | 175,165 | Fee comparison, secondary analysis only |
| `clubs.csv` | 796 | Club and league context |
| `competitions.csv` | 65 | League filtering |

Every join uses `player_id` or `club_id`. No step matches players by name.

**Verifying the copy used.** SHA-256 of the frozen archive:
`cd8bbacdb80e5c87cf4e9ee3e6bca2e6ab56baa0c3edbc05b12eedfdf1f9b4e8`

## 2. Evaluated and deliberately excluded

**Transfermarkt + WhoScored compilation** — `atakanakn`
https://www.kaggle.com/datasets/atakanakn/football-player-dataset-transfermarkt-whoscored

1,533 players with advanced metrics including expected goals and key passes.

*Excluded from the pipeline.* Its only join key is player name. Incorporating it
would have required fuzzy entity resolution, the single risk this architecture
was designed to eliminate. Recorded here because the exclusion is a documented
methodological decision, not an oversight.

**Transfermarkt Football Database** — `kberkek00`
https://www.kaggle.com/datasets/kberkek00/transfermarkt-datas

Retained as a contingency backbone. Never entered the analytical pipeline.

## 3. What this repository contains instead

The derived artifacts are committed in full, so the analysis can be inspected
and most of it re-executed without downloading anything:

| Location | Contents |
|---|---|
| `data/processed/` | The analysis table (15,925 player-seasons) and feature matrix |
| `outputs/` | Every frozen result, by pipeline stage |
| `figures/` | Every figure used in the report |

## 4. Reproducing the stages that need raw data

Stages 01 (player-season construction), 03 (feature engineering) and 06
(exit-risk model) read the raw CSVs. To run them:

1. Download `davidcariboo/player-scores` from the link above
2. Unpack the CSVs into `data/raw/`
3. Follow the pipeline order in the main README

Every other stage runs from the committed artifacts. The scope of what is and
is not re-executable is stated in the README.

## 5. A note on the transfer-fee field

Of 174,673 in-scope transfer records, only **10.0%** carry a positive fee: 35.1%
are missing and 54.9% record €0 for free transfers, loans and youth moves. This
is why market value, not fee, is the primary acquisition-cost benchmark.
