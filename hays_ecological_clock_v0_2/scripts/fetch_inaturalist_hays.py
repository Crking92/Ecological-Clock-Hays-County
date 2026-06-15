#!/usr/bin/env python3
"""Fetch public iNaturalist observations for Hays County area.
No API key is required for this public-observation starter pull.
Uses the Hays County boundary bounding box unless INAT_PLACE_ID is set.
Outputs CSVs for plants and insects.
"""
import csv, json, os, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/live/inaturalist"
OUT_DIR.mkdir(parents=True, exist_ok=True)
BOUNDARY = ROOT / "data/boundaries/processed/hays_county_boundary.geojson"
START_DATE = "2015-01-01"
PER_PAGE = 200
MAX_PAGES = int(os.environ.get("INAT_MAX_PAGES", "10"))
PLACE_ID = os.environ.get("INAT_PLACE_ID")  # optional if you know the exact Hays County iNaturalist place id
TAXON_GROUPS = {
    "plants": {"iconic_taxa": "Plantae"},
    "insects": {"iconic_taxa": "Insecta"},
}

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

bbox = bbox_from_geojson(BOUNDARY)
base_url = "https://api.inaturalist.org/v1/observations"
for group, taxon_params in TAXON_GROUPS.items():
    rows = []
    for quality in ["research", "needs_id"]:
        for page in range(1, MAX_PAGES + 1):
            params = {
                "d1": START_DATE,
                "order_by": "observed_on",
                "order": "desc",
                "quality_grade": quality,
                "per_page": PER_PAGE,
                "page": page,
                **taxon_params,
            }
            if PLACE_ID:
                params["place_id"] = PLACE_ID
            else:
                west, south, east, north = bbox
                params.update({"swlng": west, "swlat": south, "nelng": east, "nelat": north})
            url = base_url + "?" + urllib.parse.urlencode(params)
            with urllib.request.urlopen(url, timeout=90) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            results = payload.get("results", [])
            for r in results:
                taxon = r.get("taxon") or {}
                rows.append({
                    "id": r.get("id"),
                    "observed_on": r.get("observed_on"),
                    "created_at": r.get("created_at"),
                    "quality_grade": r.get("quality_grade"),
                    "scientific_name": taxon.get("name"),
                    "common_name": taxon.get("preferred_common_name"),
                    "taxon_id": taxon.get("id"),
                    "iconic_taxon_name": taxon.get("iconic_taxon_name"),
                    "latitude": (r.get("geojson") or {}).get("coordinates", [None, None])[1],
                    "longitude": (r.get("geojson") or {}).get("coordinates", [None, None])[0],
                    "uri": r.get("uri"),
                })
            if len(results) < PER_PAGE:
                break
            time.sleep(1)
    out = OUT_DIR / f"inaturalist_hays_{group}_{date.today().isoformat()}.csv"
    fields = ["id","observed_on","created_at","quality_grade","scientific_name","common_name","taxon_id","iconic_taxon_name","latitude","longitude","uri"]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} {group} rows to {out}")
