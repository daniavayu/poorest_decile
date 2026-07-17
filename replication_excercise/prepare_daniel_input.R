source_rda <- file.path("..", "code_daniel", "comparable_blog 2.Rda")
output_csv <- file.path("prepared_daniel_input.csv")
cran_mirror <- "https://cloud.r-project.org"

required_packages <- c("dplyr", "pipr")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]

if (length(missing_packages) > 0) {
  options(repos = c(CRAN = cran_mirror))
  install.packages(missing_packages, repos = cran_mirror)
}

still_missing <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]

if (length(still_missing) > 0) {
  stop(
    sprintf(
      "Missing required R packages after install attempt: %s",
      paste(still_missing, collapse = ", ")
    )
  )
}

load(source_rda)

if (!exists("comparable_blog")) {
  stop("The Rda file does not contain an object named 'comparable_blog'.")
}

required_columns <- c("code", "year", "quantile", "welf_b")
missing_columns <- setdiff(required_columns, names(comparable_blog))

if (length(missing_columns) > 0) {
  stop(
    sprintf(
      "The comparable_blog object is missing required columns: %s",
      paste(missing_columns, collapse = ", ")
    )
  )
}

pop <- pipr::get_aux("pop") |>
  dplyr::mutate(year = as.numeric(year) + 1976) |>
  dplyr::filter(data_level == "national") |>
  dplyr::select(country_code, year, value) |>
  dplyr::rename(code = country_code, pop_total = value)

prepared <- comparable_blog |>
  dplyr::left_join(pop, by = c("code", "year")) |>
  dplyr::group_by(code, year) |>
  dplyr::mutate(bin_count = dplyr::n()) |>
  dplyr::ungroup()

missing_pop_rows <- prepared |>
  dplyr::filter(is.na(pop_total))

if (nrow(missing_pop_rows) > 0) {
  missing_keys <- missing_pop_rows |>
    dplyr::distinct(code, year)

  preview <- utils::capture.output(print(utils::head(missing_keys, 10)))
  stop(
    paste(
      sprintf("Missing population matches for %d country-year pairs.", nrow(missing_keys)),
      "First unmatched pairs:",
      paste(preview, collapse = "\n"),
      sep = "\n"
    )
  )
}

prepared <- prepared |>
  dplyr::mutate(pop = pop_total / bin_count) |>
  dplyr::transmute(
    year = as.integer(year),
    welf = as.numeric(welf_b),
    pop = as.numeric(pop)
  )

utils::write.csv(prepared, output_csv, row.names = FALSE)

cat(sprintf("Prepared rows: %d\n", nrow(prepared)))
cat(sprintf("Prepared columns: %d\n", ncol(prepared)))
cat(sprintf("Saved to: %s\n", normalizePath(output_csv, winslash = "/", mustWork = FALSE)))