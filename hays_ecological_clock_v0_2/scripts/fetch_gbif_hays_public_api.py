#!/usr/bin/env python3
"""Small public GBIF occurrence pull for Hays County species support.
No credentials required. This is for quick local evidence, not formal DOI downloads.
For citable/large downloads, use request_gbif_hays_formal_download.py.
"""
import csv, json, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/live/gbif"
OUT_DIR.mkdir(parents=True, exist_ok=True)
BOUNDARY = ROOT / "data/boundaries/processed/hays_county_boundary.geojson"
SPECIES = ROOT / "data/processed/species_master_hays.csv"
LIMIT_SPECIES = 100  # raise later after the workflow is tested
START_YEAR = 2015

def bbox_from_geojson(path):
    gj = json.loads(path.read_text(encoding="utf-8"))
    coords = []
    def walk(x):
        if isinstance(x, list) and len(x) == 2 and all(isinstance(v, (int, float)) for v in x):
            coords.append(x)
        elif isinstance(x, list):
            for y in x: walk(y)
    for feat in gj["features"]:
        walk(feat["geometry"]["coordinates"])
    xs = [c[0] for c in coords]; ys = [c[1] for c in coords]
    return min(xs), min(ys), max(xs), max(ys)

west, south, east, north = bbox_from_geojson(BOUNDARY)
with SPECIES.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    sci_col = "scientific_name" if "scientific_name" in reader.fieldnames else reader.fieldnames[0]
    names = []
    for row in reader:
        name = (row.get(sci_col) or "").strip()
        if name and name not in names:
            names.append(name)
        if len(names) >= LIMIT_SPECIES:
            break
rows = []
for name in names:
    params = {
        "scientificName": name,
        "country": "US",
        "stateProvince": "Texas",
        "year": f"{START_YEAR},*",
        "decimalLatitude": f"{south},{north}",
        "decimalLongitude": f"{west},{east}",
        "limit": 50,
    }
    url = "https://api.gbif.org/v1/occurrence/search?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=90) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"WARN {name}: {e}")
        continue
    for r in payload.get("results", []):
        rows.append({
            "query_name": name,
            "gbif_key": r.get("key"),
            "scientific_name": r.get("scientificName"),
            "accepted_scientific_name": r.get("acceptedScientificName"),
            "event_date": r.get("eventDate"),
            "basis_of_record": r.get("basisOfRecord"),
            "dataset_key": r.get("datasetKey"),
            "publishing_org_key": r.get("publishingOrgKey"),
            "latitude": r.get("decimalLatitude"),
            "longitude": r.get("decimalLongitude"),
            "coordinate_uncertainty_m": r.get("coordinateUncertaintyInMeters"),
            "locality": r.get("locality"),
            "county": r.get("county"),
            "state_province": r.get("stateProvince"),
            "country_code": r.get("countryCode"),
            "gbif_url": f"https://www.gbif.org/occurrence/{r.get('key')}" if r.get("key") else None,
        })
    time.sleep(0.25)
out = OUT_DIR / f"gbif_hays_public_api_sample_{date.today().isoformat()}.csv"
fields = ["query_name","gbif_key","scientific_name","accepted_scientific_name","event_date","basis_of_record","dataset_key","publishing_org_key","latitude","longitude","coordinate_uncertainty_m","locality","county","state_province","country_code","gbif_url"]
with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(rows)
print(f"Wrote {len(rows)} rows to {out}")
