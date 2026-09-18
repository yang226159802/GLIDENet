#!/usr/bin/env python3
"""Generate website/dataset-{id}.html pages from datasets/*.json records.

Records use the flat issue-field structure written by issue_to_json.py. The
detail page keeps the original display fields while reading shared page
partials from templates/site.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ROOT / "datasets"
PAGES_DIR = ROOT / "website"
TEMPLATE_DIR = ROOT / "templates" / "site"
DETAIL_TEMPLATE = TEMPLATE_DIR / "dataset-detail.html"
NAV_TEMPLATE = TEMPLATE_DIR / "nav.html"
FOOTER_TEMPLATE = TEMPLATE_DIR / "footer.html"


def _short_status(status: str) -> str:
    for suffix in ("_dataset", " dataset"):
        if status.endswith(suffix):
            return status[: -len(suffix)]
    return status


def _text(value: object) -> str:
    return html.escape(str(value or "").strip())


def _href(value: object) -> str:
    return html.escape(str(value or "").strip(), quote=True)


def _asset_path(value: object) -> str:
    path = str(value or "").strip()
    if path.startswith("website/"):
        path = path[len("website/"):]
    return path


def _render(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{ " + key + " }}", value)
    return template


def _split_links(value: object) -> list[str]:
    return [s.strip() for s in str(value or "").split(";") if s.strip()]


def build_page(record: dict, template: str, nav: str, footer: str) -> str | None:
    dataset_id = record.get("id", "")
    if not dataset_id:
        print("Skipping record without id")
        return None

    title = _text(record.get("title") or "Untitled")
    subtitle = _text(record.get("subtitle"))
    description = _text(record.get("description"))
    status = _short_status(str(record.get("status", "seed"))).capitalize()

    access_links = _split_links(record.get("access_link"))
    metadata_links = _split_links(record.get("metadata_link"))

    try:
        case_count = int(record.get("case_count") or 1)
    except (TypeError, ValueError):
        case_count = 1
    if case_count < 1:
        case_count = 1

    if case_count <= 1 and access_links:
        host = _text(record.get("hosting_platform") or "dataset host")
        open_button = (
            f'<p><a class="button" href="{_href(access_links[0])}">Open on {host}</a></p>'
        )
    else:
        open_button = ""

    cases_section = ""
    cases_nav = ""
    if case_count > 1:
        cases_nav = '<a href="#cases">Cases</a>'
        rows: list[str] = []
        total = max(len(access_links), len(metadata_links))
        for i in range(total):
            acc = access_links[i] if i < len(access_links) else ""
            meta = metadata_links[i] if i < len(metadata_links) else ""
            acc_td = f'<a href="{_href(acc)}">{_text(acc)}</a>' if acc else "-"
            meta_td = f'<a href="{_href(meta)}">info.json</a>' if meta else "-"
            rows.append(f"<tr><td>{acc_td}</td><td>{meta_td}</td></tr>")
        cases_section = (
            '<section class="section">'
            '<h2 id="cases">Cases</h2>'
            '<table class="data-table"><thead><tr>'
            "<th>Dataset link</th><th>info.json</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></section>"
        )

    detail_images = record.get("detail_images", [])
    if isinstance(detail_images, str):
        detail_images = [detail_images]
    detail_imgs = []
    for d_img in detail_images:
        path = _asset_path(d_img)
        if path:
            detail_imgs.append(f'<img src="{_href(path)}" alt="{title}" />')
    detail_images_inline = (
        '<div class="detail-gallery">' + "".join(detail_imgs) + "</div>"
        if detail_imgs
        else '<div class="placeholder-media" aria-label="Dataset image placeholder"></div>'
    )

    items: list[str] = [f"<li>Status: {status} dataset</li>"]
    if case_count <= 1:
        if access_links:
            items.append(f'<li><a href="{_href(access_links[0])}">Dataset link</a></li>')
        if metadata_links:
            items.append(f'<li><a href="{_href(metadata_links[0])}">info.json</a></li>')

    field_map = [
        ("Contributors", "contributors"),
        ("Contact", "contact"),
        ("License", "license"),
        ("Dimension", "dimension"),
        ("Grid", "grid"),
        ("Field location", "field_location"),
        ("Samples / snapshots", "samples"),
        ("Format", "format"),
        ("Size", "size"),
        ("Case conditions", "case_condition"),
        ("Loading instructions", "file_format"),
    ]
    doi = _text(record.get("doi"))
    if doi:
        paper_title = _text(record.get("paper_title"))
        paper_label = f"Paper: {paper_title} " if paper_title else "Paper: "
        items.append(f'<li>{paper_label}<a href="https://doi.org/{_href(record.get("doi"))}">{doi}</a></li>')
    for label, key in field_map:
        value = _text(record.get(key))
        if value:
            items.append(f"<li>{label}: {value}</li>")

    return _render(
        template,
        {
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "detail_images": detail_images_inline,
            "open_button": open_button,
            "cases_section": cases_section,
            "cases_nav": cases_nav,
            "quick_info_items": "\n".join(items),
            "nav": nav,
            "footer": footer,
        },
    )


def main() -> int:
    if not DATASETS_DIR.exists():
        print("datasets/ directory not found")
        return 1

    template = DETAIL_TEMPLATE.read_text(encoding="utf-8")
    nav = NAV_TEMPLATE.read_text(encoding="utf-8")
    footer = FOOTER_TEMPLATE.read_text(encoding="utf-8")

    json_files = sorted(DATASETS_DIR.glob("*.json"))
    if not json_files:
        print("No dataset JSON files found; cleaning orphan pages")

    generated = 0
    records = []
    for path in json_files:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"Skipping {path.name}: invalid JSON ({exc})")
            continue

        page = build_page(record, template, nav, footer)
        if page is None:
            continue

        records.append(record)
        dataset_id = record.get("id", "")
        output_path = PAGES_DIR / f"dataset-{dataset_id}.html"
        output_path.write_text(page, encoding="utf-8")
        print(f"Generated {output_path.name}")
        generated += 1

    existing_pages = set(PAGES_DIR.glob("dataset-*.html"))
    expected_ids = {r.get("id", "") for r in records}
    for page_path in sorted(existing_pages):
        page_id = page_path.stem.replace("dataset-", "")
        if page_id not in expected_ids:
            page_path.unlink()
            print(f"Removed orphan page: {page_path.name}")

    print(f"Generated {generated} dataset detail page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
