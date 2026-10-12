"""Export 40 random distinct Unparsed location strings for private review only."""
from __future__ import annotations

import argparse
import csv
import random
import sqlite3
from pathlib import Path

from discovery.locations import normalize_location

ROOT = Path(__file__).resolve().parents[1]
DB_DEFAULT = ROOT / "data" / "private" / "jobs.db"
OUTPUT_DEFAULT = ROOT / "reports" / "unparsed_location_review.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DB_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--sample-size", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20261012)
    args = parser.parse_args()
    if args.sample_size < 1:
        parser.error("--sample-size must be positive")
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")

    connection = sqlite3.connect(f"file:{args.db.resolve()}?mode=ro", uri=True)
    try:
        rows = connection.execute(
            """SELECT DISTINCT location_raw FROM jobs
               WHERE is_active=1 AND location_raw IS NOT NULL AND TRIM(location_raw) != ''
               ORDER BY location_raw"""
        ).fetchall()
    finally:
        connection.close()

    candidates = [row[0] for row in rows if normalize_location(row[0]) == "Unparsed"]
    rng = random.Random(args.seed)
    sample = rng.sample(candidates, min(args.sample_size, len(candidates)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["location_raw", "review_label", "review_notes"])
        writer.writeheader()
        for location in sample:
            writer.writerow({"location_raw": location, "review_label": "", "review_notes": ""})

    print(f"Exported {len(sample)} of {len(candidates)} distinct Unparsed location strings to {args.output}.")
    print("This file contains raw location strings; keep it in the private data repository only.")


if __name__ == "__main__":
    main()
