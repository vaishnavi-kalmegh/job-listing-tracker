"""Export random title samples for human review of the entry-level heuristic.

This script does not claim precision until a reviewer supplies gold labels.
Use --sample-size 30 for 30 predicted-positive and 30 predicted-negative titles.
Descriptions are read locally from a discovery run file only; exports contain
titles and predicted labels, not full descriptions.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_LOG = ROOT / "reports" / "discovery_run.json"
OUTPUT = ROOT / "reports" / "entry_level_review.csv"
CITIES = ("Pune", "Hyderabad", "Bengaluru", "Delhi NCR", "Mumbai")


def is_entry_level(title: str, description: str) -> bool:
    import re
    include = re.compile(r"\b(fresher|junior|associate|graduate|intern(ship)?|entry[- ]level|0\s*[-–to]+\s*2\s+years?)\b", re.I)
    exclude = re.compile(r"\b(senior|sr\.?|lead|principal|manager|director|head of|staff engineer)\b", re.I)
    return bool(include.search(f"{title} {description}")) and not bool(exclude.search(title))


def extract_title_records(run: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for result in run.get("results", []):
        if not result.get("verified") or not result.get("complete"):
            continue
        platform = result.get("platform", "")
        for job in result.get("jobs_for_review", []):
            title = str(job.get("title") or job.get("text") or "").strip()
            description = str(job.get("description") or job.get("content") or job.get("descriptionPlain") or "")
            if not title:
                continue
            records.append({
                "platform": platform,
                "company_name": str(result.get("company_name", "")),
                "title": title,
                "predicted_entry_level": str(is_entry_level(title, description)).lower(),
                "review_label": "",
            })
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20261012)
    parser.add_argument("--run-log", type=Path, default=RUN_LOG)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.sample_size < 1:
        parser.error("--sample-size must be positive")
    if not args.run_log.exists():
        raise SystemExit("No local run log found. Run discovery first. This script requires a local review dataset.")
    run = json.loads(args.run_log.read_text(encoding="utf-8"))
    records = extract_title_records(run)
    positives = [r for r in records if r["predicted_entry_level"] == "true"]
    negatives = [r for r in records if r["predicted_entry_level"] == "false"]
    rng = random.Random(args.seed)
    sample = rng.sample(positives, min(args.sample_size, len(positives))) + rng.sample(negatives, min(args.sample_size, len(negatives)))
    rng.shuffle(sample)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["platform", "company_name", "title", "predicted_entry_level", "review_label"])
        writer.writeheader()
        writer.writerows(sample)
    print(f"Eligible titles: {len(records)}; flagged: {len(positives)}; not flagged: {len(negatives)}")
    print(f"Exported {sum(r['predicted_entry_level']=='true' for r in sample)} flagged and {sum(r['predicted_entry_level']=='false' for r in sample)} unflagged titles to {args.output}")
    print("Fill review_label with true/false after human review, then run: python -m discovery.score_entry_level_review")
    if len(positives) < args.sample_size or len(negatives) < args.sample_size:
        print("WARNING: fewer records than requested in at least one class; the requested sample size was not available.")


if __name__ == "__main__":
    main()
