"""Report precision for tech and non-tech predictions after human review."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "reports" / "role_review.csv"


def normalized(value: str) -> str:
    value = (value or "").strip().casefold().replace("_", "-")
    if value in {"tech", "technical", "true", "yes", "1"}:
        return "tech"
    if value in {"non-tech", "nontech", "non technical", "false", "no", "0"}:
        return "non-tech"
    if value in {"unclassified", "uncertain", "unknown"}:
        return "unclassified"
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"Review file not found: {args.input}. Download the private role_review.csv or run python -m discovery.sample_role_review first.")
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    labelled = [r for r in rows if normalized(r.get("review_label", ""))]
    print(f"Human-labelled rows: {len(labelled)} / {len(rows)}")
    for group, expected in (("tech", "tech"), ("non-tech", "non-tech")):
        subset = [r for r in labelled if r.get("predicted_group") == group]
        correct = sum(normalized(r.get("review_label", "")) == expected for r in subset)
        precision = correct / len(subset) if subset else None
        print(f"{group} precision: " + (f"{precision:.3f} ({correct}/{len(subset)})" if precision is not None else "undefined (no labelled predictions in this group)"))
    if len(labelled) < len(rows):
        print("Unlabelled rows are excluded. No precision estimate is reported for an empty group.")
    print("These are review-sample precision estimates, not population estimates; sampling and reviewer labels may introduce bias.")


if __name__ == "__main__":
    main()
