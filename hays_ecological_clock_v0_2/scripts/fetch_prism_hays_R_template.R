#!/usr/bin/env Rscript
# PRISM workflow template for Hays County Ecological Clock v0.2
# Install once if needed:
# install.packages(c("prism", "terra", "sf", "dplyr", "lubridate", "readr"))

library(prism)
library(terra)
library(sf)
library(dplyr)
library(lubridate)
library(readr)

root <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = TRUE)
out_dir <- file.path(root, "data", "live", "prism")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
boundary_path <- file.path(root, "data", "boundaries", "processed", "hays_county_boundary.geojson")
hays <- st_read(boundary_path, quiet = TRUE) |> st_transform(4326)
options(prism.path = file.path(out_dir, "raw_prism_cache"))
vars <- c("ppt", "tmin", "tmax", "tmean", "vpdmin", "vpdmax")
start_date <- as.Date("2020-01-01")
end_date <- Sys.Date() - 1
# For first test runs, set end_date <- start_date + 30

daily_rows <- list()
for (v in vars) {
  message("Downloading/extracting PRISM variable: ", v)
  get_prism_dailys(type = v, minDate = start_date, maxDate = end_date, keepZip = FALSE)
  files <- prism_archive_ls()[grepl(paste0("_", v, "_"), prism_archive_ls())]
  files <- files[grepl("bil$", files)]
  for (f in files) {
    r <- rast(f)
    rr <- crop(r, vect(hays)) |> mask(vect(hays))
    val <- global(rr, "mean", na.rm = TRUE)[1,1]
    d <- as.Date(gsub(".*_(\\d{8})_.*", "\\1", basename(f)), format = "%Y%m%d")
    daily_rows[[length(daily_rows) + 1]] <- data.frame(date = d, variable = v, county_mean = val)
  }
}
daily <- bind_rows(daily_rows)
write_csv(daily, file.path(out_dir, "prism_hays_daily_county_mean_long.csv"))

wide <- daily |> tidyr::pivot_wider(names_from = variable, values_from = county_mean) |> arrange(date)
weekly <- wide |>
  mutate(week_start = floor_date(date, "week")) |>
  group_by(week_start) |>
  summarize(
    ppt_7d = sum(ppt, na.rm = TRUE),
    tmin_avg = mean(tmin, na.rm = TRUE),
    tmax_avg = mean(tmax, na.rm = TRUE),
    tmean_avg = mean(tmean, na.rm = TRUE),
    vpdmax_avg = mean(vpdmax, na.rm = TRUE),
    vpdmin_avg = mean(vpdmin, na.rm = TRUE),
    .groups = "drop"
  ) |>
  mutate(
    freeze_flag = tmin_avg <= 32,
    heat_stress_flag = tmax_avg >= 95,
    vpd_stress_flag = vpdmax_avg >= 2.5,
    ecological_signal = case_when(
      freeze_flag ~ "freeze or false-spring risk",
      heat_stress_flag & vpd_stress_flag ~ "heat plus dry-air stress",
      ppt_7d >= 1 ~ "rain pulse",
      TRUE ~ "baseline seasonal monitoring"
    )
  )
write_csv(weekly, file.path(out_dir, "climate_clock_hays_weekly.csv"))
message("Wrote PRISM daily and weekly outputs to ", out_dir)
