# Hays County Ecological Clock v0.2

Public-facing data package for a Hays County ecological timing dashboard.

This version builds from v0.1 and adds the live-pull scaffolding, Hays County boundary, clipped Level IV ecoregion layer, and credential-safe configuration for PRISM, USA-NPN, iNaturalist, GBIF, and eBird.

## What this package already contains

- `data/processed/species_master_hays.csv` - merged USDA + Wildflower Center Hays plant master.
- `data/processed/plant_clock_hays.csv` - plant bloom/timing fields from the Wildflower Center file.
- `data/processed/interaction_hays.csv` - Central Texas GloBI interactions filtered to Hays-listed plants.
- `data/processed/interaction_summary_by_plant_type.csv` - interaction counts by Hays plant and interaction type.
- `data/processed/bird_clock_hays.csv` - Hays-detected eBird birds with simple food-guild and ecological-clock roles.
- `data/processed/lookout_rules_hays.csv` - starter rules for public “something seems off” notices.
- `data/reference/ecoregions_tx_level4_reference.csv` - EPA Level IV Texas ecoregion reference table.
- `data/reference/hays_level4_ecoregions_clipped.geojson` - Level IV ecoregions clipped to Hays County boundary.
- `data/reference/hays_level4_ecoregions_summary.csv` - clipped Level IV ecoregion summary.
- `data/boundaries/processed/hays_county_boundary.geojson` - Hays County boundary in WGS84.
- `data/soil/soil_interpretation_signals.csv` - SSURGO interpretation rows useful for wildlife, soil health, water, rangeland, and restoration context.
- `config/hays_ecological_clock_config.yml` - source and live-pull settings.

## Live-pull scripts added in v0.2

- `scripts/fetch_prism_hays_R_template.R` - PRISM daily climate extraction to Hays County weekly signals.
- `scripts/fetch_usanpn_hays_template.py` - USA-NPN setup/species matching scaffold for 2015-present phenology.
- `scripts/fetch_inaturalist_hays.py` - public iNaturalist plant and insect observation pulls.
- `scripts/fetch_gbif_hays_public_api.py` - small no-credential GBIF occurrence sample pull.
- `scripts/request_gbif_hays_formal_download.py` - credential-safe formal GBIF download request template.
- `scripts/fetch_ebird_hays_recent.py` - eBird recent Hays County observations using `EBIRD_API_KEY`.
- `scripts/summarize_live_pulls.py` - summaries of downloaded live CSV files.

## Current geography

- Boundary: Hays County, Texas
- Output CRS for web/dashboard mapping: EPSG:4326
- Approximate boundary area: 1757.6 sq km
- WGS84 bounding box: west -98.297540, south 29.752410, east -97.708710, north 30.356210
- eBird region code: `US-TX-209`

## Live-source choices

### PRISM

- Resolution: 4 km first
- Daily date range: 2020-present
- Baseline normals: 1991-2020
- Variables: `ppt`, `tmin`, `tmax`, `tmean`, `vpdmin`, `vpdmax`

### USA-NPN

- Request source: `Hays County Ecological Clock`
- Date range: 2015-present
- Species list: `data/processed/species_master_hays.csv`
- Target phenophases: Leaves, Open flowers, Fruits, Ripe fruits, Recent fruit or seed drop

### iNaturalist

- Hays County boundary bounding box by default
- Optional exact place filter: set `INAT_PLACE_ID` if desired
- Groups: plants and insects first
- Quality: research grade first, needs ID secondary

### GBIF

Two paths are staged:

1. Small public API pull without credentials.
2. Formal GBIF download request using environment variables only: `GBIF_USER`, `GBIF_EMAIL`, `GBIF_PWD`.

### eBird

- Region: `US-TX-209`
- API key must be set as `EBIRD_API_KEY`
- The key is not stored in this package.

## Source hierarchy

1. GitHub files are the project source of truth once committed.
2. Uploaded source files are the current staging sources.
3. APIs add recent/live signals after static tables are stable.
4. Old workbooks should only be used to recover missing row-level data.

## Important limitations

- The PRISM R script is a template/workflow script; it should be run locally or in a GitHub Action with R packages installed.
- The USA-NPN script currently stages species matching and pull configuration. Final API implementation should happen after matching names to USA-NPN species IDs.
- SSURGO `cinterp` was parsed as soil interpretation signals, not as a full soil map. To map soils, add SSURGO mapunit/component/spatial files.
- GBIF formal downloads should be requested only when you are ready to store the GBIF download key/DOI in the source inventory.

## Recommended next step

Commit this v0.2 package to GitHub, run the PRISM workflow first, then iNaturalist/eBird, then GBIF public API, then USA-NPN matching.
