## Este script genera el gráfico de panel de deciles de ingresos globales 
## utilizando los datos de Daniel y corrigiendo el peso por población.

load("comparable_blog 2.Rda")
library(dplyr)
install.packages("joyn")
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

write.csv(
  comparable_blog,
  "comparable_blog_with_pop.csv",
  row.names = FALSE
)

decile_shares <- comparable_blog |>
  select(-c(code, quantile)) |>
  group_by(year) |>
  arrange(welf_b, .by_group = TRUE) |>
  mutate(
    cum_pop = cumsum(pop),
    decile = pmin(10L, ceiling(cum_pop / (sum(pop) / 10)))
  ) |>
  group_by(year, decile) |>
  summarize(
    mean_welf = weighted.mean(welf_b, w = pop, na.rm = TRUE),
    .groups = "drop"
  ) |>
  group_by(year) |>
  mutate(
    welfare_share = mean_welf / sum(mean_welf) * 100
  ) |>
  ungroup()

(decile_panel_plot_corrected <- decile_shares |>
    mutate(
      decile = factor(decile,
                      levels = 1:10,
                      labels = paste("Decile", 1:10))
    ) |>
    ggplot(aes(x = year, y = welfare_share)) +
    geom_line(linewidth = 0.8) +
    facet_wrap(~decile, ncol = 5, scales = "free_y") +
    labs(
      title = "Income Share by Global Decile (Daniel Corrected)",
      x = NULL,
      y = "Income share (%)"
    ) +
    scale_y_continuous(labels = scales::label_number(accuracy = 0.1, suffix = "%")) +
    theme_minimal())

print(decile_panel_plot_corrected)
