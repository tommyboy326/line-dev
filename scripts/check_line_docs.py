#!/usr/bin/env python3
"""Check LINE Developers docs for content drift vs the stored baseline.

- Fetches each URL in scripts/line-docs-urls.json
- Extracts the main content region, strips nav/script/style noise
- Hashes the normalized text with SHA-256
- Compares against .line-docs-baseline.json at repo root
- Writes /tmp/line-docs-changes.md summary + emits GITHUB_OUTPUT flags

Exits 0 on normal runs (including when changes are detected). Non-zero exit
is reserved for unrecoverable errors (e.g. URL list missing).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Comment

REPO_ROOT = Path(__file__).resolve().parent.parent
URL_LIST = REPO_ROOT / "scripts" / "line-docs-urls.json"
BASELINE = REPO_ROOT / ".line-docs-baseline.json"
SUMMARY = Path("/tmp/line-docs-changes.md")

HEADERS = {
    "User-Agent": (
        "line-dev-skill-docs-checker/1.0 "
        "(+https://github.com/tommyboy326/line-dev-skill)"
    ),
    "Accept-Language": "en",
}

STRIP_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "aside")
CONTENT_SELECTORS = (
    "main",
    "article",
    "[role=main]",
    ".content",
    "#content",
    ".document",
)
REQUEST_TIMEOUT = 30
INTER_REQUEST_SLEEP = 1.0


def extract_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(list(STRIP_TAGS)):
        tag.decompose()
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()

    main = None
    for sel in CONTENT_SELECTORS:
        found = soup.select_one(sel)
        if found is not None:
            main = found
            break
    if main is None:
        main = soup.body or soup

    text = main.get_text(separator="\n", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def fetch(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}", file=sys.stderr)
        return None


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def emit_output(**kwargs: str | int | bool) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a", encoding="utf-8") as f:
        for k, v in kwargs.items():
            if isinstance(v, bool):
                v = "true" if v else "false"
            f.write(f"{k}={v}\n")


def main() -> int:
    if not URL_LIST.exists():
        print(f"URL list missing: {URL_LIST}", file=sys.stderr)
        return 1

    urls = json.loads(URL_LIST.read_text(encoding="utf-8"))
    is_first_run = not BASELINE.exists()
    baseline: dict[str, dict] = (
        json.loads(BASELINE.read_text(encoding="utf-8")) if not is_first_run else {}
    )

    new_baseline: dict[str, dict] = {}
    errors: list[str] = []
    labels: dict[str, str] = {}

    for entry in urls:
        url = entry["url"]
        label = entry.get("label", url)
        labels[url] = label
        print(f"Checking {label} ...")
        html = fetch(url)
        if html is None:
            errors.append(url)
            if url in baseline:
                # keep prior hash so a transient fetch failure isn't flagged as a change
                new_baseline[url] = baseline[url]
            continue
        content = extract_content(html)
        new_baseline[url] = {
            "hash": sha256(content),
            "label": label,
            "skill": entry.get("skill", ""),
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        time.sleep(INTER_REQUEST_SLEEP)

    added = sorted(u for u in new_baseline if u not in baseline)
    removed = sorted(u for u in baseline if u not in new_baseline)
    changed = sorted(
        u for u in new_baseline
        if u in baseline and baseline[u].get("hash") != new_baseline[u].get("hash")
    )

    has_changes = bool(added or removed or changed)

    BASELINE.write_text(
        json.dumps(new_baseline, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines: list[str] = ["# LINE Docs Changes", ""]
    if is_first_run:
        lines.append(f"Initial baseline created for {len(new_baseline)} URLs.")
        lines.append("")
    if changed:
        lines.append(f"## Changed ({len(changed)})")
        lines.append("")
        for u in changed:
            lines.append(f"- [{labels.get(u, u)}]({u})")
        lines.append("")
    if added and not is_first_run:
        lines.append(f"## Newly tracked ({len(added)})")
        lines.append("")
        for u in added:
            lines.append(f"- [{labels.get(u, u)}]({u})")
        lines.append("")
    if removed:
        lines.append(f"## Removed ({len(removed)})")
        lines.append("")
        for u in removed:
            lines.append(f"- {baseline[u].get('label', u)} — {u}")
        lines.append("")
    if errors:
        lines.append(f"## Fetch errors ({len(errors)})")
        lines.append("")
        for u in errors:
            lines.append(f"- {u}")
        lines.append("")

    SUMMARY.write_text("\n".join(lines), encoding="utf-8")

    emit_output(
        has_changes=(has_changes and not is_first_run),
        is_first_run=is_first_run,
        changed_count=len(changed),
        added_count=len(added),
        removed_count=len(removed),
        error_count=len(errors),
    )

    print(
        f"\nResult: {len(changed)} changed, {len(added)} added, "
        f"{len(removed)} removed, {len(errors)} errors"
    )
    if is_first_run:
        print("(first run — baseline initialized)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
