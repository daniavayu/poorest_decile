# Daniel's data prep (R)

Builds a population-weighted global decile panel from Daniel's comparable binned welfare dataset, following the same weighting logic as [Nishant's methodology](../nishant_analysis/README.md).

## Data pipeline (see `notes.md`)

1. Daniel's data: one row per country/year/bin (1,000 bins), with columns `code`, `year`,
   `quantile`, `welf_b`, `pop`.
2. Country population by year (1981–2026) is pulled from PIP (`pipr::get_aux("pop")`).
3. The two datasets are merged on `code` and `year`.

## Files

- **`r_code.R`** — **original** script. Computes each decile's welfare as `sum(welf_b)`
  within population-weighted decile groups — this does **not** correctly replicate a
  population-weighted mean, so the resulting shares are biased.
- **`corrected_daniel.R`** — **corrected** script. Fixes the above by computing each
  decile's welfare as `weighted.mean(welf_b, w = pop)`. This is the script to use.
- **`notes.md`** — working notes on the data structure and Nishant's methodology.

## Data

`comparable_blog 2.Rda` and generated CSVs are not tracked in this repo (see
`.gitignore`, they're large). Place `comparable_blog 2.Rda` in this folder before running
either script; `pipr` will fetch population data from PIP over the network.

## Usage

```r
source("corrected_daniel.R")
```
