cran_mirror <- "https://cloud.r-project.org"

required_packages <- c("dplyr", "joyn", "ggplot2", "pipr", "scales")

missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]

if (length(missing_packages) > 0) {
  options(repos = c(CRAN = cran_mirror))
  install.packages(missing_packages, repos = cran_mirror)
}

library(dplyr)
library(joyn)
library(ggplot2)
library(pipr)
library(scales)

load("comparable_blog 2.Rda")

#--------------------------------------------------
# Population data from PIP
#--------------------------------------------------

pop <- pipr::get_aux("pop") |>
  mutate(year = as.numeric(year) + 1976) |>
  filter(data_level == "national") |>
  select(-data_level) |>
  rename(
    pop = value,
    code = country_code
  ) |>
  filter(year >= 1981, year <= 2026)

#--------------------------------------------------
# Merge population onto binned distribution
#--------------------------------------------------

comparable_blog <- comparable_blog |>
  joyn::joyn(
    pop,
    match_type = "m:1",
    by = c("code", "year"),
    reportvar = FALSE,
    keep = "left",
    verbose = FALSE
  )

#--------------------------------------------------
# Construct global population deciles
# (same logic as Stata xtile, weighted by population)
#--------------------------------------------------

decile_shares <- comparable_blog |>
  select(-c(code, quantile)) |>
  group_by(year) |>
  arrange(welf_b, .by_group = TRUE) |>
  mutate(
    
    # cumulative population
    cum_pop = cumsum(pop),
    
    # assign deciles (10 equal-sized population groups)
    decile = pmin(
      10L,
      ceiling(cum_pop / (sum(pop) / 10))
    )
    
  ) |>
  group_by(year, decile) |>
  summarize(
    
    # population-weighted mean welfare
    mean_welf = weighted.mean(
      welf_b,
      w = pop,
      na.rm = TRUE
    ),
    
    .groups = "drop"
    
  ) |>
  group_by(year) |>
  mutate(
    
    # share of total welfare
    welfare_share = 100 * mean_welf / sum(mean_welf)
    
  ) |>
  ungroup()

#--------------------------------------------------
# Plot
#--------------------------------------------------

decile_panel_plot_corrected_2 <- decile_shares |>
  mutate(
    decile = factor(
      decile,
      levels = 1:10,
      labels = paste("Decile", 1:10)
    )
  ) |>
  ggplot(aes(year, welfare_share)) +
  geom_line(linewidth = 0.8) +
  facet_wrap(~decile, ncol = 5, scales = "free_y") +
  labs(
    title = "Income Share by Global Decile Option 2 Corrected",
    x = NULL,
    y = "Income Share (%)"
  ) +
  scale_y_continuous(
    labels = scales::label_number(
      accuracy = 0.1,
      suffix = "%"
    )
  ) +
  theme_minimal()

print(decile_panel_plot_corrected_2)
