# Nishant's methodology (Stata + Python)

Builds a population-weighted global decile panel from a binned global income distribution, and plots how each decile's income share evolves over time.

## Methodology

For each year, the global income distribution is built from bins where each observation
has an average income level (`welf`) and a corresponding population (`pop`). Bins are
ranked from lowest to highest income, and population weights are used to split the global
population into ten equally sized groups (deciles) — so each decile represents ~10% of
the world's *population*, not 10% of the bins. The average income of each decile is then
computed as a population-weighted mean, and each decile's share of total income is its
average income divided by the sum of average incomes across all ten deciles.

## Files

- **`bottom10percent.do`** — original Stata script. Expects a PIP `GlobalDist*.dta` file
  (~1,000 bins per country-year, columns `year`, `welf`, `pop`) and produces the
  connected-line plot of income shares for deciles 1, 2, 5 and 10.
- **`bottom10percent.py`** — direct Python translation of the Stata script. Looks for
  `globdist.dta` / `.csv` / `.parquet` / `.feather` or a `GlobalDist*.dta` file in this
  folder (or pass `--input`), and writes `nishant_decile_shares.csv` and
  `nishant_decile_shares_plot.png`.

The Our-World-in-Data-style income density plots (`distribucion.py`) live in
[../work/](../work/README.md) since they build on the replication pipeline's prepared
input rather than the raw `GlobalDist` file used here.

## Data

`GlobalDist*.dta/.csv` and other generated CSVs are not tracked in this repo (see
`.gitignore`). Download the global distribution file from the World Bank
[Poverty and Inequality Platform (PIP)](https://pip.worldbank.org/) and place it in this
folder to run `bottom10percent.py`.

## Usage

```bash
python bottom10percent.py --input GlobalDist1000bins_....dta
```
