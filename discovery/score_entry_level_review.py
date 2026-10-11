"""Compute heuristic precision from a human-labelled entry-level review CSV."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "reports" / "entry_level_review.csv"


def truth(value: str) -> bool | None:
    normalized = value.strip().casefold()
    if normalized in {"true", "yes", "1", "entry-level", "entry_level"}:
        return True
    if normalized in {"false", "no", "0", "not-entry-level", "not_entry_level"}:
        return False
    return None


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Review file not found: {INPUT}")
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    labelled = [(r, truth(r.get("review_label", ""))) for r in rows]
    labelled = [(r, y) for r, y in labelled if y is not None]
    predicted_positive = [(r, y) for r, y in labelled if truth(r.get("predicted_entry_level", "")) is True]
    tp = sum(y is True for _, y in predicted_positive)
    fp = sum(y is False for _, y in predicted_positive)
    precision = tp / (tp + fp) if tp + fp else None
    print(f"Human-labelled records: {len(labelled)}")
    print(f"Predicted-positive records with human labels: {len(predicted_positive)}")
    print(f"True positives: {tp}; false positives: {fp}")
    print("Heuristic precision on labelled predicted-positive sample: " + (f"{precision:.3f} ({tp}/{tp+fp})" if precision is not None else "undefined (no labelled predicted-positive rows)"))
    if len(predicted_positive) < 30:
        print("CAUTION: fewer than 30 predicted-positive rows are labelled; precision is preliminary.")
    print("This is sample precision only, not population precision. Review sampling and labels may introduce bias.")


if __name__ == "__main__":
    main()
