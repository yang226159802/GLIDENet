#!/usr/bin/env python3
"""Notify dataset reviewers about new submissions.

The script intentionally has no third-party dependencies. If SMTP secrets are
not configured, it writes a GitHub Actions summary and exits successfully.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import smtplib
from email.message import EmailMessage


ROOT = Path(__file__).resolve().parents[1]
REVIEWERS_FILE = ROOT / ".github" / "reviewers.yml"


def load_reviewer_emails() -> list[str]:
    emails: list[str] = []
    if not REVIEWERS_FILE.exists():
        return emails

    for line in REVIEWERS_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("email:"):
            email = stripped.split(":", 1)[1].strip().strip("'\"")
            if email and not email.endswith("@example.com"):
                emails.append(email)
    return emails


def load_event() -> dict:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return {}
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def build_message(event: dict) -> tuple[str, str]:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")

    if "issue" in event:
        item = event["issue"]
        kind = "Dataset submission issue"
        url = item.get("html_url", "")
    elif "pull_request" in event:
        item = event["pull_request"]
        kind = "Dataset pull request"
        url = item.get("html_url", "")
    else:
        item = {}
        kind = "Dataset intake event"
        url = f"{server}/{repo}"

    title = item.get("title", "Untitled dataset submission")
    user = item.get("user", {}).get("login", "unknown")

    subject = f"[GLIDENet] Review needed: {title}"
    body = "\n".join(
        [
            f"{kind} needs maintainer review.",
            "",
            f"Repository: {repo}",
            f"Title: {title}",
            f"Submitted by: {user}",
            f"Link: {url}",
            "",
            "Automated checks are preliminary. Please verify metadata completeness, data access, license, citation, and file readability before accepting the record.",
        ]
    )
    return subject, body


def write_summary(subject: str, body: str, recipients: list[str], reason: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    text = "\n".join(
        [
            "## Reviewer notification",
            "",
            f"Status: {reason}",
            f"Subject: {subject}",
            f"Recipients: {', '.join(recipients) if recipients else 'none configured'}",
            "",
            "```text",
            body,
            "```",
        ]
    )
    if summary_path:
        Path(summary_path).write_text(text, encoding="utf-8")
    else:
        print(text)


def main() -> int:
    event = load_event()
    subject, body = build_message(event)
    recipients = load_reviewer_emails()

    smtp_host = os.environ.get("SMTP_HOST")
    mail_from = os.environ.get("MAIL_FROM") or os.environ.get("SMTP_USERNAME")
    if not smtp_host or not mail_from or not recipients:
        write_summary(subject, body, recipients, "SMTP or recipient list not configured; email skipped")
        return 0

    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = mail_from
    message["To"] = ", ".join(recipients)
    message.set_content(body)
    try:
        with smtplib.SMTP(smtp_host, port, timeout=30) as smtp:
            smtp.starttls()
            if username and password:
                smtp.login(username, password)
            smtp.send_message(message)
        write_summary(subject, body, recipients, "email sent")
    except Exception as exc:
        write_summary(subject, body, recipients, f"SMTP failed: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
