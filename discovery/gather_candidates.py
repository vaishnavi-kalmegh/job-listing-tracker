"""Collect candidate company names from public lists without guessing job-board tokens.

This helper is deliberately separate from API probing. Public-list candidates
are written with their source URL and blank tokens; a human must find and
record an actual public Greenhouse/Lever board URL before they can be probed.
"""
from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "discovery" / "candidate_sources.csv"
REPO_URL = "https://github.com/vaishnavi-kalmegh/job-listing-tracker"
HEADERS = {"User-Agent": f"JobListingTrackerResearch/0.1 (+{REPO_URL})"}
SOURCES = (
    ("Wikipedia: List of companies of India", "https://en.wikipedia.org/wiki/List_of_companies_of_India"),
    ("Wikipedia: List of unicorn startup companies", "https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies"),
)


def fetch_candidate_names(url: str, timeout: int = 20) -> list[str]:
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    names: set[str] = set()
    for table in soup.select("table.wikitable"):
        for row in table.select("tr"):
            cells = row.find_all(["th", "td"], recursive=False)
            if not cells:
                continue
            text = cells[0].get_text(" ", strip=True)
            text = re.sub(r"\[[0-9]+\]", "", text).strip()
            if 2 <= len(text) <= 100 and not text.lower() in {"company", "name", "company name"}:
                if re.search(r"[A-Za-z]", text) and not text.startswith(("http://", "https://")):
                    names.add(text)
    return sorted(names, key=str.casefold)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for label, url in SOURCES:
        # Keep public-list requests polite too; no crawling of linked pages.
        time.sleep(1)
        try:
            names = fetch_candidate_names(url)
        except (requests.RequestException, ValueError) as exc:
            print(f"WARNING: could not read {url}: {type(exc).__name__}: {exc}")
            continue
        for name in names:
            rows[(name.casefold(), url)] = {
                "company_name": name, "source_name": label, "source_url": url,
                "greenhouse_token": "", "lever_token": "",
                "notes": "Candidate from public list only; board URL/token not yet verified.",
            }
        print(f"{label}: extracted {len(names)} candidate names")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "company_name", "source_name", "source_url", "greenhouse_token", "lever_token", "notes"
        ])
        writer.writeheader()
        writer.writerows(rows.values())
    print(f"Wrote {len(rows)} sourced candidates to {args.output}")


if __name__ == "__main__":
    main()
