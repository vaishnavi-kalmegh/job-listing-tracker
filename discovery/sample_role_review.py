"""Sample 30 predicted-tech and 30 predicted-non-tech titles for human review."""
from __future__ import annotations

import argparse
import csv
import os
import random
from pathlib import Path

from collector.db import connect

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("JOB_TRACKER_DB", str(ROOT / "data" / "private" / "jobs.db")))
OUTPUT = ROOT / "reports" / "role_review.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20261012)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.sample_size < 1:
        parser.error("--sample-size must be positive")
    if not DB_PATH.exists():
        raise SystemExit(f"Private database not found: {DB_PATH}. Run the collector first.")
    db = connect(DB_PATH)
    tech = [dict(row) for row in db.execute(
        "SELECT platform,token,job_id,title,role_category,is_tech FROM jobs WHERE is_active=1 AND is_tech=1"
    )]
    nontech = [dict(row) for row in db.execute(
        "SELECT platform,token,job_id,title,role_category,is_tech FROM jobs WHERE is_active=1 AND is_tech=0"
    )]
    db.close()
    rng = random.Random(args.seed)
    selected = []
    for group, rows in (("tech", tech), ("non-tech", nontech)):
        chosen = rng.sample(rows, min(args.sample_size, len(rows)))
        for row in chosen:
            selected.append({
                "platform": row["platform"], "company_token": row["token"], "job_id": row["job_id"],
                "title": row["title"], "predicted_group": group,
                "role_category": row["role_category"], "review_label": "",
            })
    rng.shuffle(selected)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "platform", "company_token", "job_id", "title", "predicted_group", "role_category", "review_label"
        ])
        writer.writeheader()
        writer.writerows(selected)
    print(f"Exported {min(args.sample_size, len(tech))} tech and {min(args.sample_size, len(nontech))} non-tech titles.")
    print("Fill review_label with tech or non-tech (or unclassified if neither); do not label by description.")
    if len(tech) < args.sample_size or len(nontech) < args.sample_size:
        print("WARNING: not enough active rows in one group to reach the requested sample size.")


if __name__ == "__main__":
    main()
