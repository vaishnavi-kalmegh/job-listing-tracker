"""Build a reproducible feasibility report from a local discovery run."""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_LOG = ROOT / "reports" / "discovery_run.json"
OUTPUT = ROOT / "reports" / "feasibility.md"
CITIES = ("Pune", "Hyderabad", "Bengaluru", "Delhi NCR", "Mumbai")


def main() -> None:
    if not RUN_LOG.exists():
        raise SystemExit("No local discovery_run.json found. Run python -m discovery.discover first.")
    run = json.loads(RUN_LOG.read_text(encoding="utf-8"))
    verified = [r for r in run.get("results", []) if r.get("verified") and r.get("complete")]
    totals: Counter[str] = Counter()
    entry: Counter[str] = Counter()
    remote = unclassified = 0
    for board in verified:
        try:
            city_counts = json.loads(board.get("jobs_per_city") or "{}")
            entry_counts = json.loads(board.get("entry_level_jobs") or "{}")
        except (ValueError, TypeError):
            continue
        for city in CITIES:
            totals[city] += int(city_counts.get(city, 0))
            entry[city] += int(entry_counts.get(city, 0))
    # Board verification currently counts only target-city jobs in public CSV.
    # Remote and unclassified counts are intentionally not estimated unless
    # the source run explicitly contains them.
    city_total = sum(totals.values())
    entry_total = sum(entry.values())
    failures = [r for r in run.get("results", []) if not r.get("verified")]
    skewed = any(totals[c] == 0 or entry[c] == 0 for c in CITIES)
    enough = city_total >= 300 and not skewed
    decision = "Enough data to continue to Phase 2" if enough else "Feasibility concern: do not proceed automatically; review source strategy and coverage."
    lines = [
        "# Phase 1 feasibility report", "",
        f"Generated from local discovery run at {run.get('run_at', 'unknown')}.",
        "All counts below are derived from verified, complete API responses in this run.", "",
        f"- **Verified boards:** {len(verified)} (valid zero-job boards count as verified).",
        f"- **Jobs in the five target cities:** {city_total}.",
        f"- **Entry-level jobs across the five cities:** {entry_total}.",
        f"- **API probes attempted:** {run.get('probes_attempted', 0)}.",
        f"- **Failed, blocked, invalid, or incomplete probes:** {len(failures)}.",
        f"- **Feasibility decision:** {decision}", "",
        "| City | Jobs | Entry-level estimate |",
        "|---|---:|---:|",
    ]
    for city in CITIES:
        lines.append(f"| {city} | {totals[city]} | {entry[city]} |")
    lines += ["", "## Interpretation", "",
              "Entry-level counts are heuristic estimates based on titles and descriptions; they are not a verified seniority field.",
              "A board probe that fails, is blocked, returns invalid JSON, or cannot be completely paginated is not treated as a verified zero-job board.",
              "This report uses target-city counts only. India - Remote/Other and Unclassified are kept separate and are not counted toward the five-city threshold.",
              "If volume is below approximately 300 jobs or any city has no observed entry-level roles, expand evidence-backed candidate sources and manually inspect more public board URLs. Do not brute-force tokens.", "",
              "## Probe outcomes", "",
              "| Platform | Company | Token | Verified | Status | HTTP |",
              "|---|---|---|---|---|---:|"]
    for result in run.get("results", []):
        lines.append(f"| {result.get('platform','')} | {result.get('company_name','')} | {result.get('token','')} | {result.get('verified', False)} | {result.get('status','')} | {result.get('http_status','')} |")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(verified)} verified boards, {city_total} target-city jobs, {entry_total} entry-level estimates.")


if __name__ == "__main__":
    main()
