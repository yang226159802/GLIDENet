#!/usr/bin/env python3
"""Generate website/js/datasets-data.js from datasets/*.json records.

Records use the flat issue-field structure written by issue_to_json.py. This
script intentionally emits data only; UI rendering lives in website/js.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ROOT / "datasets"
OUTPUT = ROOT / "website" / "js" / "datasets-data.js"


def _short_status(status: str) -> str:
    for suffix in ("_dataset", " dataset"):
        if status.endswith(suffix):
            return status[: -len(suffix)]
    return status


def build_entry(record: dict) -> dict:
    title = (record.get("title") or "").strip()
    subtitle = (record.get("subtitle") or "").strip()
    keywords = (record.get("keywords") or "").strip()
    tags = [k.strip() for k in keywords.split(",") if k.strip()]

    preview = (record.get("preview") or "").strip()
    if preview.startswith("website/"):
        preview = preview[len("website/"):]

    access_links = [
        s.strip() for s in (record.get("access_link") or "").split(";") if s.strip()
    ]
    data_url = access_links[0] if access_links else ""

    try:
        case_count = int(record.get("case_count") or 1)
    except (TypeError, ValueError):
        case_count = 1
    if case_count < 1:
        case_count = 1

    return {
        "id": record.get("id", ""),
        "title": title,
        "subtitle": subtitle,
        "status": _short_status(record.get("status", "seed")).lower(),
        "tags": tags,
        "samples": (record.get("samples") or "").strip(),
        "grid": (record.get("grid") or "").strip(),
        "fieldLocation": (record.get("field_location") or "").strip(),
        "format": (record.get("format") or "").strip(),
        "license": (record.get("license") or "").strip(),
        "size": (record.get("size") or "").strip(),
        "imageUrl": preview,
        "dataUrl": data_url,
        "detailUrl": f"dataset-{record.get('id', 'unknown')}.html",
        "caseCount": case_count,
        "hostingPlatform": (record.get("hosting_platform") or "").strip(),
        "categories": record.get("categories", []),
    }


def main() -> int:
    if not DATASETS_DIR.exists():
        print("datasets/ directory not found, skipping")
        return 1

    json_files = sorted(DATASETS_DIR.glob("*.json"))
    if not json_files:
        print("No dataset JSON files found; writing empty list")

    entries = []
    for path in json_files:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            entries.append(build_entry(record))
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"Warning: skipping {path.name}: {exc}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    header = "// Auto-generated from datasets/*.json -- do not edit manually.\n"
    data_block = f"window.DATASETS = {json.dumps(entries, indent=2, ensure_ascii=False)};\n"
    OUTPUT.write_text(header + data_block, encoding="utf-8")
    print(f"Generated {OUTPUT} with {len(entries)} dataset(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
