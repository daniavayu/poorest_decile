cran_mirror <- "https://cloud.r-project.org"
required_packages <- c("dplyr", "joyn", "ggplot2", "pipr", "scales")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]

if (length(missing_packages) > 0) {
  options(repos = c(CRAN = cran_mirror))
  install.packages(missing_packages, repos = cran_mirror)
}

load("comparable_blog 2.Rda")
library(dplyr)
library(joyn)
library(ggplot2)

# Get country population data from PIP
pop <- pipr::get_aux("pop") |>
       mutate(year=as.numeric(year)+1976) |>
       filter(data_level=="national") |>
       select(-data_level) |>
       rename("pop" = "value","code"="country_code") |>
       filter(year<=2026) |>
       filter(year>=1981)

# Merge to the comparable binned vectors
comparable_blog <- comparable_blog |>
  joyn::joyn(pop,match_type="m:1",by=c("code","year"),reportvar=FALSE,keep="left",verbose=FALSE)  

decile_shares <- comparable_blog |>
  select(-c("code", "quantile")) |>
  group_by(year) |>
  arrange(welf_b) |>
  mutate(
    cum_pop_share = cumsum(pop) / sum(pop),
    decile = pmin(10L, ceiling(cum_pop_share * 10))
  ) |>
  ungroup() |>
  group_by(year,decile) |>
  summarize(welfare_mass = sum(welf_b, na.rm = TRUE)  ) |>
  ungroup() |>
  group_by(year) |>
  mutate(welfare_share = welfare_mass / sum(welfare_mass)*100) |>
  ungroup()

(decile_panel_plot <- decile_shares |>
  mutate(
    decile = factor(decile, levels = 1:10, labels = paste("Decile", 1:10))) |>
  ggplot(aes(x = year, y = welfare_share)) +
  geom_line(linewidth = 0.8) +
  facet_wrap(~ decile, ncol = 5, scales = "free_y") +
  labs(
    title = "Welfare Share by Decile Over Time",
    x = NULL,
    y = "Welfare share (%)",
    color = "Method" ) +
  scale_y_continuous(labels = scales::label_number(accuracy = 0.1, suffix = "%")) +
  theme_minimal())