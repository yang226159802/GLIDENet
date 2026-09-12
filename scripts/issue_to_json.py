#!/usr/bin/env python3
"""Generate a dataset JSON and image files from a GitHub issue.

The GitHub issue form fields are parsed from the issue body markdown. A flat
JSON record is written to datasets/<id>.json, images are downloaded into
website/assets/<id>/, and the generated id is written to stdout plus a marker
file so the workflow can open a pull request afterwards.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ROOT / "datasets"
ASSETS_DIR = ROOT / "website" / "assets"
ID_FILE = ROOT / "generated_id.txt"

LABEL_TO_FIELD = {
    "Requested review track": "requested_track",
    "Dataset title": "title",
    "Subtitle": "subtitle",
    "Description": "description",
    "Dataset status": "status",
    "Keywords": "keywords",
    "Hosting platform": "hosting_platform",
    "Dataset link": "access_link",
    "info.json link": "metadata_link",
    "Physics and numerical method": "physics",
    "Variables": "variables",
    "Grid dimensions": "grid",
    "Field location": "field_location",
    "Number of samples / snapshots": "samples",
    "Data format": "format",
    "File format and loading instructions": "file_format",
    "Dataset size": "size",
    "Number of cases": "case_count",
    "Case conditions": "case_condition",
    "Contributors": "contributors",
    "Contact": "contact",
    "DOI or preferred citation": "doi",
    "License": "license",
    "Preview image": "preview",
    "Detail page images": "detail_images",
    "Automated precheck notes": "automation_notes",
}


def parse_issue_body(body: str) -> dict[str, str]:
   """Split an issue-form body into a label -> value mapping."""
   result: dict[str, str] = {}
   current_label: str | None = None
   current_lines: list[str] = []

   for line in body.splitlines():
       if line.startswith("### "):
           if current_label is not None:
               result[current_label] = "\n".join(current_lines).strip()
           current_label = line[4:].strip()
           current_lines = []
       elif current_label is not None:
           current_lines.append(line)

   if current_label is not None:
       result[current_label] = "\n".join(current_lines).strip()

   return result


def slugify(text: str) -> str:
   text = text.lower().strip()
   text = re.sub(r"[^a-z0-9]+", "-", text)
   return text.strip("-") or "dataset"


def extract_urls(value: str) -> list[str]:
   """Extract URLs from a value that may contain markdown image links."""
   urls: list[str] = []
   # markdown image/links: ![...](url) or [...](url)
   for match in re.finditer(r"!?\[[^\]]*\]\((https?://[^)\s]+)\)", value):
       urls.append(match.group(1).rstrip('"\'.,;'))
   # bare URLs
   for match in re.finditer(r"https?://[^\s)\]]+", value):
       url = match.group(0).rstrip('"\'.,;')
       if url not in urls:
           urls.append(url)
   return urls


def download(url: str, destination: Path) -> str:
   destination.parent.mkdir(parents=True, exist_ok=True)
   try:
       with urllib.request.urlopen(url, timeout=60) as response:
           content = response.read()
       destination.write_bytes(content)
       return str(destination.relative_to(ROOT / "website"))
   except Exception as exc:  # noqa: BLE001
       print(f"Warning: could not download {url}: {exc}")
       return url


def file_extension(url: str) -> str:
   path = url.split("?", 1)[0]
   ext = os.path.splitext(path)[1]
   return ext if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"} else ".png"


def main() -> int:
   event_path = os.environ.get("GITHUB_EVENT_PATH")
   if not event_path:
       print("GITHUB_EVENT_PATH is not set")
       return 1

   event = json.loads(Path(event_path).read_text(encoding="utf-8"))
   issue = event.get("issue", {})
   body = issue.get("body", "") or ""
   issue_number = issue.get("number", 0)

   parsed = parse_issue_body(body)
   record: dict[str, object] = {"schema_version": "0.1.0"}
   for label, field in LABEL_TO_FIELD.items():
       value = parsed.get(label, "").strip()
       if value and value != "_No response_":
           record[field] = value

   title = str(record.get("title", "")).strip()
   timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
   dataset_id = f"{slugify(title)}-{timestamp}" if title else f"issue-{issue_number}-{timestamp}"
   record["id"] = dataset_id

   image_dir = ASSETS_DIR / dataset_id
   image_dir.mkdir(parents=True, exist_ok=True)

   preview_urls = extract_urls(str(record.get("preview", "")))
   if preview_urls:
       record["preview"] = download(preview_urls[0], image_dir / f"cover{file_extension(preview_urls[0])}")
   else:
       record.pop("preview", None)

   detail_urls = extract_urls(str(record.get("detail_images", "")))
   if detail_urls:
       saved: list[str] = []
       for i, url in enumerate(detail_urls, start=1):
           saved.append(download(url, image_dir / f"detail-{i}{file_extension(url)}"))
       record["detail_images"] = saved
   else:
       record.pop("detail_images", None)

   DATASETS_DIR.mkdir(parents=True, exist_ok=True)
   output_path = DATASETS_DIR / f"{dataset_id}.json"
   output_path.write_text(
       json.dumps(record, indent=2, ensure_ascii=False) + "\n",
       encoding="utf-8",
   )

   ID_FILE.write_text(dataset_id, encoding="utf-8")
   print(f"Generated {output_path} with id {dataset_id}")
   print(dataset_id)
   return 0


if __name__ == "__main__":
   raise SystemExit(main())
