"""Export a reproducible random sample of currently Unclassified titles for private review.

This script deliberately opens SQLite directly rather than calling collector.db.connect(),
because connect() reclassifies historical rows using the current rules. In the workflow,
run this before the next collection so the sample reflects the pre-rule-update Unclassified
population. Never write this file to the public repository.
"""
from __future__ import annotations

import argparse
import csv
import random
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_DEFAULT = ROOT / "data" / "private" / "jobs.db"
OUTPUT_DEFAULT = ROOT / "reports" / "unclassified_review.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DB_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20261012)
    args = parser.parse_args()
    if args.sample_size < 1:
        parser.error("--sample-size must be positive")
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")
    connection = sqlite3.connect(f"file:{args.db.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        """SELECT platform,token AS company_token,job_id,title,department,team,
                  location_raw,city_bucket,role_category,is_tech
           FROM jobs WHERE is_active=1 AND role_category='Unclassified'
           ORDER BY platform,token,job_id"""
    ).fetchall()
    connection.close()
    rng = random.Random(args.seed)
    sample = rng.sample(rows, min(args.sample_size, len(rows)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "platform", "company_token", "job_id", "title", "department", "team",
        "location_raw", "city_bucket", "current_role_category", "current_is_tech",
        "review_label", "review_notes",
    ]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sample:
            writer.writerow({
                "platform": row["platform"], "company_token": row["company_token"],
                "job_id": row["job_id"], "title": row["title"],
                "department": row["department"], "team": row["team"],
                "location_raw": row["location_raw"], "city_bucket": row["city_bucket"],
                "current_role_category": row["role_category"], "current_is_tech": row["is_tech"],
                "review_label": "", "review_notes": "",
            })
    print(f"Exported {len(sample)} of {len(rows)} active Unclassified listings to {args.output}.")
    print("Contains titles and metadata; keep it in the private data repository only.")


if __name__ == "__main__":
    main()
