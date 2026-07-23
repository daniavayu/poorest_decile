# poorest_decile

What has happened in the last years with the poorest decile of the world's population?

This repository studies how the global income distribution has evolved since 1981, with a
focus on the poorest decile relative to the middle and top of the distribution.

## Repository structure

```
poorest_decile/
├── nishant_analysis/   # Original Stata methodology + its Python translation
├── daniel_analysis/     # R scripts that build the population-weighted global decile panel
├── work/                 # Python replication combining Daniel's data prep with Nishant's methodology
├── docs/                 # Brainstorming notes and project updates
└── README.md
```

### `nishant_analysis/`
Stata code (`bottom10percent.do`) that builds population-weighted global deciles from a
1,000-bin global distribution dataset (PIP `GlobalDist...` files) and its direct Python
translation (`bottom10percent.py`).
See [nishant_analysis/README.md](nishant_analysis/README.md).

### `daniel_analysis/`
R scripts that take Daniel's comparable binned welfare data (`comparable_blog 2.Rda`),
merge it with PIP population data, and build a population-weighted decile panel.
See [daniel_analysis/README.md](daniel_analysis/README.md).

### `work/`
Python scripts that reproduce Nishant's weighted-decile methodology using Daniel's
prepared input data, plus additional plots on how the poorest decile compares to the
middle and top deciles over time, including Our-World-in-Data-style income density plots
(`distribucion.py`). See [work/README.md](work/README.md).

### `docs/`
Brainstorming notes and progress updates written during the project.

## Data

Raw and intermediate data files (`.dta`, `.Rda`, `.csv`, etc.) are not tracked in this
repository (see `.gitignore`) because they are large and/or derived from restricted
sources. To reproduce the analysis you need to obtain, from the World Bank
[Poverty and Inequality Platform (PIP)](https://pip.worldbank.org/):

- A global distribution file binned by country/year (e.g. `GlobalDist*.dta`, ~1,000 bins
  per country-year) — used by `nishant_analysis/`.
- Country-level population data via `pipr::get_aux("pop")` — used by both
  `daniel_analysis/` and `work/` to weight bins by population.
- Daniel's comparable binned welfare dataset (`comparable_blog 2.Rda`) — place it in
  `daniel_analysis/` before running its scripts.

Each subfolder's README documents the exact input file(s) its scripts expect and the
scripts (e.g. `work/prepare_daniel_input.R`) that generate intermediate CSVs from
the raw data.
