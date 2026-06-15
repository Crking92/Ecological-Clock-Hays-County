#!/usr/bin/env python3
"""USA-NPN starter script scaffold for Hays County Ecological Clock.
USA-NPN does not require an API key for the basic starter workflow.
This script writes the planned request configuration and a species list ready for a USA-NPN taxon matching step.
Next implementation choice: use the USA-NPN API directly or run an R `rnpn` workflow.
"""
import csv, json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/live/usanpn"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SPECIES = ROOT / "data/processed/species_master_hays.csv"
REQUEST_SOURCE = "Hays County Ecological Clock"
PHENOPHASES = ["Leaves", "Open flowers", "Fruits", "Ripe fruits", "Recent fruit or seed drop"]
START_YEAR = 2015
species_out = OUT_DIR / "usanpn_species_to_match.csv"
with SPECIES.open("r", encoding="utf-8", newline="") as f, species_out.open("w", encoding="utf-8", newline="") as out:
    reader = csv.DictReader(f)
    sci_col = "scientific_name" if "scientific_name" in reader.fieldnames else reader.fieldnames[0]
    w = csv.DictWriter(out, fieldnames=["scientific_name"])
    w.writeheader()
    seen = set()
    for row in reader:
        name = (row.get(sci_col) or "").strip()
        if name and name not in seen:
            seen.add(name); w.writerow({"scientific_name": name})
plan = {
    "request_source": REQUEST_SOURCE,
    "start_year": START_YEAR,
    "phenophases": PHENOPHASES,
    "species_to_match_csv": str(species_out.relative_to(ROOT)),
    "target_output": "data/live/usanpn/usanpn_hays_phenology_records.csv",
    "note": "Match plant names to USA-NPN species IDs, then request phenology records for target phenophases."
}
(OUT_DIR / f"usanpn_pull_plan_{date.today().isoformat()}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
print(f"Wrote USA-NPN species matching list: {species_out}")
