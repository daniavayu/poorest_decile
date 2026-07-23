# Work: replication exercise

Python replication that combines Daniel's data prep with Nishant's population-weighted
decile methodology, plus extra plots comparing the poorest decile to the middle and top
of the distribution over time.

## Pipeline

1. **`prepare_daniel_input.R`** — loads `../daniel_analysis/comparable_blog 2.Rda`, merges
   in PIP population data, and writes `prepared_daniel_input.csv` (columns `year`, `welf`,
   `pop`) in this folder.
2. **`bottom10percent_from_daniel.py`** — reads `prepared_daniel_input.csv`, assigns
   population-weighted deciles per year (replicating Nishant's Stata
   `egen decile = xtile(welf), weight(pop) by(year) n(10)`), and writes
   `daniel_decile_shares.csv` and `evolution_shares.png`.
3. **`plot_left_behind.py`** — reads `daniel_decile_shares.csv` and produces
   `left_behind_plot.png` (income growth index and welfare share for the poorest, middle
   and top deciles) and `left_behind_gap_plot.png` (ratio of middle/top decile welfare to
   the poorest decile's).
4. **`distribucion.py`** — reads `prepared_daniel_input.csv` and builds
   Our-World-in-Data-style income density plots (`distribution_density_2000/2015/2026.png`
   and `distribution_density_combined.png`) from 1,000 population-weighted quantiles,
   plus `distribution_quantile_table.csv`.

## Data

`prepared_daniel_input.csv` is not tracked in this repo (large, generated file — see
`.gitignore`). Generate it by running `prepare_daniel_input.R` first, which requires
`../daniel_analysis/comparable_blog 2.Rda` and network access to PIP for population data.

## Usage

```bash
Rscript prepare_daniel_input.R
python bottom10percent_from_daniel.py
python plot_left_behind.py
python distribucion.py
```
