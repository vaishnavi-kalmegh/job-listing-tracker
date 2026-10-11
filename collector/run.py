"""Run one complete collection pass and write aggregate-only public summaries."""
from __future__ import annotations

import csv
import json
import logging
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from collector.client import CollectorClient, normalize_job
from collector.db import connect, save_complete_snapshot, utc_now
from discovery.discover import HostStopped, ProbeError

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ROOT / "data" / "boards.csv"
DB_PATH = Path(os.environ.get("JOB_TRACKER_DB", str(ROOT / "data" / "private" / "jobs.db")))
SUMMARY_JSON = ROOT / "reports" / "daily_run_summary.json"
SUMMARY_MD = ROOT / "reports" / "daily_run_summary.md"
LOG = logging.getLogger("collector")
CATEGORIES = (
    "Software Engineering", "Data/ML/AI", "DevOps/Cloud/SRE/Infra", "QA/Test",
    "Security", "IT Support/Systems", "Product/Design (tech-adjacent)", "Non-Tech", "Unclassified",
)


def load_boards() -> list[dict[str, str]]:
    with BOARDS.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [r for r in rows if r.get("platform") in {"greenhouse", "lever"} and r.get("token")]


def write_summary(summary: dict) -> None:
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Daily collection summary", "",
        f"- Run time (UTC): {summary['run_at']}",
        f"- Boards attempted: {summary['boards_attempted']}",
        f"- Boards fetched completely: {summary['boards_fetched']}",
        f"- Errors/incomplete boards: {summary['errors']}",
        f"- New jobs: {summary['new_jobs']}",
        f"- Changed jobs: {summary['changed_jobs']}",
        f"- Vanished jobs (confirmed only by complete snapshots): {summary['vanished_jobs']}",
        f"- Active jobs in private history after run: {summary['active_jobs_after_run']}",
        "", "## Counts by role category (active jobs in private history)", "",
        "| Role category | Count |", "|---|---:|",
    ]
    for category in CATEGORIES:
        lines.append(f"| {category} | {summary['active_counts_by_role_category'].get(category, 0)} |")
    lines += [
        "", "## Excluded from analysis", "",
        "Non-Tech and Unclassified jobs remain in collection history but are excluded from tech-only analysis.",
        "", "| Category | Count |", "|---|---:|",
        f"| Non-Tech | {summary['active_counts_by_role_category'].get('Non-Tech', 0)} |",
        f"| Unclassified | {summary['active_counts_by_role_category'].get('Unclassified', 0)} |",
        "", "This public summary contains aggregate counts only; no job titles, descriptions, URLs, company-level errors, or raw snapshots.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    client = CollectorClient()
    connection = connect(DB_PATH)
    totals = {
        "run_at": utc_now(), "boards_attempted": 0, "boards_fetched": 0, "errors": 0,
        "new_jobs": 0, "changed_jobs": 0, "vanished_jobs": 0, "jobs_seen_this_run": 0,
    }
    for board in load_boards():
        totals["boards_attempted"] += 1
        platform, token = board["platform"], board["token"]
        started = utc_now()
        try:
            raw_jobs, complete, status = client.fetch(platform, token)
            if not complete:
                raise ProbeError(f"incomplete_fetch:{status}")
            normalized = []
            for raw in raw_jobs:
                # A malformed record makes the snapshot incomplete: do not infer disappearance.
                normalized.append(normalize_job(platform, raw))
            result = save_complete_snapshot(connection, platform, token, board.get("company_name", token), normalized)
            totals["boards_fetched"] += 1
            totals["new_jobs"] += result["new"]
            totals["changed_jobs"] += result["changed"]
            totals["vanished_jobs"] += result["vanished"]
            totals["jobs_seen_this_run"] += result["seen"]
            connection.execute(
                "INSERT INTO collection_runs(started_at,finished_at,platform,token,status,jobs_seen) VALUES(?,?,?,?,?,?)",
                (started, utc_now(), platform, token, "success_complete", result["seen"]),
            )
            connection.commit()
            LOG.info("Complete board snapshot: %s/%s jobs=%d new=%d vanished=%d", platform, token, result["seen"], result["new"], result["vanished"])
        except (ProbeError, HostStopped, ValueError, TypeError, AttributeError) as exc:
            totals["errors"] += 1
            connection.execute(
                "INSERT INTO collection_runs(started_at,finished_at,platform,token,status,error_type,jobs_seen) VALUES(?,?,?,?,?,?,0)",
                (started, utc_now(), platform, token, "failed_or_incomplete", f"{type(exc).__name__}:{str(exc)[:350]}"),
            )
            connection.commit()
            LOG.error("Board fetch incomplete; no listings marked inactive: %s", type(exc).__name__)

    counts = Counter()
    for row in connection.execute("SELECT role_category,COUNT(*) AS n FROM jobs WHERE is_active=1 GROUP BY role_category"):
        counts[row["role_category"]] = row["n"]
    totals["active_counts_by_role_category"] = {category: int(counts.get(category, 0)) for category in CATEGORIES}
    totals["active_jobs_after_run"] = sum(totals["active_counts_by_role_category"].values())
    totals["boards_not_fetched"] = totals["errors"]
    connection.close()
    write_summary(totals)
    LOG.info("Aggregate run summary written; raw DB remains at configured private path.")
    return totals


if __name__ == "__main__":
    run()
