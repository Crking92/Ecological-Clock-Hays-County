# Suggested run order for v0.2 live pulls

1. Commit the v0.2 package to GitHub.
2. Keep secrets out of files. Export credentials only when needed.
3. Run PRISM first because climate signals drive the weekly clock:
   - `Rscript scripts/fetch_prism_hays_R_template.R`
4. Run iNaturalist public observations:
   - `python scripts/fetch_inaturalist_hays.py`
5. Run eBird recent observations after setting `EBIRD_API_KEY`:
   - `python scripts/fetch_ebird_hays_recent.py`
6. Run GBIF small public sample:
   - `python scripts/fetch_gbif_hays_public_api.py`
7. Use formal GBIF download later only when ready for a citable DOI-backed archive:
   - set `GBIF_USER`, `GBIF_EMAIL`, `GBIF_PWD`
   - `python scripts/request_gbif_hays_formal_download.py`
8. Run the USA-NPN species matching scaffold:
   - `python scripts/fetch_usanpn_hays_template.py`
9. Summarize new live outputs:
   - `python scripts/summarize_live_pulls.py`
