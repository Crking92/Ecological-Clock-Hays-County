#!/usr/bin/env python3
"""Request a formal GBIF occurrence download using environment credentials.
This creates a GBIF download job and prints the download key. It does not store credentials.
Set: GBIF_USER, GBIF_EMAIL, GBIF_PWD.
Note: GBIF formal downloads may be asynchronous; GBIF will provide a download link/DOI after processing.
"""
import base64, json, os, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/live/gbif"
OUT_DIR.mkdir(parents=True, exist_ok=True)
user = os.environ.get("GBIF_USER")
email = os.environ.get("GBIF_EMAIL")
pwd = os.environ.get("GBIF_PWD")
if not all([user, email, pwd]):
    raise SystemExit("Set GBIF_USER, GBIF_EMAIL, and GBIF_PWD as environment variables first.")
# Starter predicate: Texas plant occurrences from 2015-present. Narrow/expand after testing.
payload = {
    "creator": user,
    "notificationAddresses": [email],
    "sendNotification": True,
    "format": "SIMPLE_CSV",
    "predicate": {
        "type": "and",
        "predicates": [
            {"type": "equals", "key": "COUNTRY", "value": "US"},
            {"type": "equals", "key": "STATE_PROVINCE", "value": "Texas"},
            {"type": "greaterThanOrEquals", "key": "YEAR", "value": "2015"},
            {"type": "equals", "key": "TAXON_KEY", "value": "6"}
        ]
    }
}
body = json.dumps(payload).encode("utf-8")
creds = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("ascii")
req = urllib.request.Request(
    "https://api.gbif.org/v1/occurrence/download/request",
    data=body,
    method="POST",
    headers={"Content-Type": "application/json", "Authorization": f"Basic {creds}"},
)
with urllib.request.urlopen(req, timeout=120) as resp:
    download_key = resp.read().decode("utf-8").strip().strip('"')
print(f"GBIF download requested. Download key: {download_key}")
print(f"Status URL: https://www.gbif.org/occurrence/download/{download_key}")
(ROOT / "data/live/gbif/last_gbif_download_key.txt").write_text(download_key + "\n", encoding="utf-8")
