# Live Pull Setup Notes - Hays County Ecological Clock v0.2

## Credential handling
Do not commit API keys, usernames, passwords, tokens, or generated private downloads to GitHub.
Use local environment variables or GitHub Secrets.

Required only when that source is run:

- `EBIRD_API_KEY` for eBird API pulls.
- `GBIF_USER`, `GBIF_EMAIL`, and `GBIF_PWD` for formal GBIF downloads.

PRISM, USA-NPN, and public iNaturalist pulls do not require private credentials for the starter workflow.

## USA-NPN phenophases
A phenophase is a life-stage event. For this dashboard, use:

- Leaves: plant is actively growing.
- Open flowers: nectar and pollen are available now.
- Fruits: fruit or seed structures are present.
- Ripe fruits: wildlife food or seed-collection timing is active.
- Recent fruit or seed drop: seed is falling or has recently fallen.

These are the living clock ticks used to compare plant timing with insects, birds, rain, heat, and drought.

## GBIF workflow
Start with `scripts/fetch_gbif_hays_public_api.py` for small occurrence support pulls.
Use `scripts/request_gbif_hays_formal_download.py` later when you want a citable GBIF download DOI or a large occurrence archive.

## PRISM workflow
Use the R script first if R is available because the `prism` and `terra` packages handle PRISM rasters cleanly.
Output should become `data/live/prism/climate_clock_hays_weekly.csv`.
