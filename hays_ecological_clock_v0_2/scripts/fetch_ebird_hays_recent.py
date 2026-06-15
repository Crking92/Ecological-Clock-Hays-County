#!/usr/bin/env python3
"""Fetch recent eBird observations for Hays County, Texas.
Set EBIRD_API_KEY in your environment. Do not hard-code the key.
Output: data/live/ebird/ebird_recent_hays_<date>.csv
"""
import csv, json, os, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/live/ebird"
OUT_DIR.mkdir(parents=True, exist_ok=True)
API_KEY = os.environ.get("EBIRD_API_KEY")
if not API_KEY:
    raise SystemExit("Set EBIRD_API_KEY first, e.g. export EBIRD_API_KEY=...")
REGION = "US-TX-209"
BACK_DAYS = 30
url = f"https://api.ebird.org/v2/data/obs/{REGION}/recent?back={BACK_DAYS}&includeProvisional=true"
req = urllib.request.Request(url, headers={"x-ebirdapitoken": API_KEY})
with urllib.request.urlopen(req, timeout=90) as resp:
    data = json.loads(resp.read().decode("utf-8"))
fields = sorted({k for row in data for k in row.keys()}) if data else []
out = OUT_DIR / f"ebird_recent_hays_{date.today().isoformat()}.csv"
with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    if fields:
        w.writeheader(); w.writerows(data)
print(f"Wrote {len(data)} rows to {out}")
