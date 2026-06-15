#!/usr/bin/env python3
"""Summarize live-pull CSV outputs into dashboard-ready counts.
Run after any PRISM/USA-NPN/iNaturalist/GBIF/eBird pulls.
"""
import csv, json
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "data/live"
summary = {"generated_on": date.today().isoformat(), "live_files": []}
for path in sorted(LIVE.rglob("*.csv")):
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            row_count = sum(1 for _ in f) - 1
    except Exception:
        row_count = None
    summary["live_files"].append({"path": str(path.relative_to(ROOT)), "rows": row_count})
out = ROOT / "data/live/live_pull_summary.json"
out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(f"Wrote {out}")
