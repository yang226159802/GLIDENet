#!/usr/bin/env python3
"""Lightweight metadata checks for dataset intake pull requests."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"


REQUIRED_FIELDS = [
    "schema_version",
    "id",
    "requested_track",
    "title",
    "description",
    "status",
    "keywords",
    "hosting_platform",
    "access_link",
    "metadata_link",
    "contributors",
    "contact",
    "grid",
    "field_location",
    "case_count",
    "format",
    "file_format",
    "doi",
    "license",
    "preview",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def check_catalogue_record(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        record = json.load(handle)

    for field in REQUIRED_FIELDS:
        if not record.get(field):
            errors.append(f"{path}: missing or empty required field '{field}'")

    access_link = (record.get("access_link") or "").strip()
    links = [s.strip() for s in access_link.split(";") if s.strip()]
    if not links:
        errors.append(f"{path}: access_link needs at least one public URL")

    case_count = 1
    try:
        case_count = int(record.get("case_count") or 1)
    except (TypeError, ValueError):
        errors.append(f"{path}: case_count must be an integer")

    if case_count < 1:
        errors.append(f"{path}: case_count must be a positive integer")
    elif case_count > 1 and len(links) < case_count:
        errors.append(
            f"{path}: case_count={case_count} but only {len(links)} access link(s) provided"
        )

    return errors


def main() -> int:
    if not DATASETS.exists():
        fail("datasets/ directory is missing")

    json_files = sorted(DATASETS.glob("*.json"))
    if not json_files:
        print("No dataset catalogue records found in datasets/; skipping")
        return 0

    errors: list[str] = []
    for path in json_files:
        try:
            errors.extend(check_catalogue_record(path))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON at line {exc.lineno}: {exc.msg}")

    if errors:
        print("Dataset metadata precheck failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Dataset metadata precheck passed for {len(json_files)} record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
