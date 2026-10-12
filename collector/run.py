"""Run one complete collection pass and write aggregate-only public summaries."""
from __future__ import annotations

import csv
import json
import logging
import os
import sqlite3
from collections import Counter
from pathlib import Path

from collector.client import CollectorClient, normalize_job
from collector.db import connect, save_complete_snapshot, utc_now
from discovery.discover import HostStopped, ProbeError
from discovery.locations import normalize_location
from discovery.roles import classify_role

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ROOT / "data" / "boards.csv"
DB_PATH = Path(os.environ.get("JOB_TRACKER_DB", str(ROOT / "data" / "private" / "jobs.db")))
SUMMARY_JSON = ROOT / "reports" / "daily_run_summary.json"
SUMMARY_MD = ROOT / "reports" / "daily_run_summary.md"
FEASIBILITY = ROOT / "reports" / "feasibility.md"
LOG = logging.getLogger("collector")
CITY_BUCKETS = ("Pune", "Hyderabad", "Bengaluru", "Delhi NCR", "Mumbai")
EXTRA_BUCKETS = ("India - Remote/Other", "Outside India", "Unparsed")
CATEGORIES = (
    "Software Engineering", "Data/ML/AI", "DevOps/Cloud/SRE/Infra", "QA/Test",
    "Security", "IT Support/Systems", "Product/Design (tech-adjacent)", "Non-Tech", "Unclassified",
)


def load_boards() -> list[dict[str, str]]:
    with BOARDS.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [r for r in rows if r.get("platform") in {"greenhouse", "lever"} and r.get("token")]


def collect_complete_board(connection, client: CollectorClient, board: dict[str, str]) -> dict[str, int]:
    """Persist a board only after the API and every record normalize successfully."""
    platform, token = board["platform"], board["token"]
    raw_jobs, complete, status = client.fetch(platform, token)
    if not complete:
        raise ProbeError(f"incomplete_fetch:{status}")
    normalized = [normalize_job(platform, raw) for raw in raw_jobs]
    return save_complete_snapshot(connection, platform, token, board.get("company_name", token), normalized)


def preview_location_rebucket_moves(db_path: Path) -> dict:
    """Count active legacy non-city rows that new rules move into target cities."""
    result = {
        "all_jobs": 0, "tech_jobs": 0,
        "by_city": {city: {"all_jobs": 0, "tech_jobs": 0} for city in CITY_BUCKETS},
    }
    if not db_path.exists():
        return result
    connection = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """SELECT city_bucket,location_raw,title,department,team
               FROM jobs WHERE is_active=1"""
        ).fetchall()
    except sqlite3.Error:
        connection.close()
        return result
    connection.close()
    for row in rows:
        old_bucket = row["city_bucket"]
        new_bucket = normalize_location(row["location_raw"])
        if old_bucket == new_bucket or new_bucket not in CITY_BUCKETS or old_bucket in CITY_BUCKETS:
            continue
        result["all_jobs"] += 1
        result["by_city"][new_bucket]["all_jobs"] += 1
        _, is_tech = classify_role(row["title"], row["department"], row["team"])
        if is_tech is True:
            result["tech_jobs"] += 1
            result["by_city"][new_bucket]["tech_jobs"] += 1
    return result


def write_feasibility_section(summary: dict) -> None:
    existing = FEASIBILITY.read_text(encoding="utf-8") if FEASIBILITY.exists() else "# Phase 1 feasibility report\n"
    start_marker = "<!-- TECH_FEASIBILITY_START -->"
    end_marker = "<!-- TECH_FEASIBILITY_END -->"
    moves = summary.get("location_rebucket_moves", {})
    section = [
        start_marker, "## Tech-only feasibility (latest successful collector history)", "",
        f"- Active jobs across the five cities: **{summary['five_city_all_jobs']}**.",
        f"- Active tech jobs across the five cities: **{summary['five_city_tech_jobs']}**.",
        f"- Tech-only volume clears approximately 300 jobs: **{'YES' if summary['five_city_tech_jobs'] >= 300 else 'NO'}**.",
        f"- Existing active listings moved from non-city buckets into the five cities by the updated location rules: **{moves.get('all_jobs', 0)}**, including **{moves.get('tech_jobs', 0)} tech jobs**.",
        "- Counts below are active records in the private collection database; all roles are collected, and filtering is applied only for analysis.", "",
        "| City | All active jobs | Tech-only jobs | Product/Design tag |", "|---|---:|---:|---:|",
    ]
    for city in CITY_BUCKETS:
        row = summary["city_counts"].get(city, {})
        section.append(f"| {city} | {row.get('all_jobs', 0)} | {row.get('tech_jobs', 0)} | {row.get('product_design_jobs', 0)} |")
    section += [
        "", "### All active jobs by location bucket and is_tech", "",
        "The is_tech field is true for technical roles and Product/Design (tech-adjacent), false for Non-Tech, and null for Unclassified roles. Product/Design remains separately counted and can be included or excluded downstream. Outside India means the location explicitly names a non-India country or a recognized non-India city; Unparsed means the location could not be determined conservatively.", "",
        "| Location bucket | All active jobs | is_tech = true | is_tech = false | is_tech = null | Product/Design |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for bucket in (*CITY_BUCKETS, *EXTRA_BUCKETS):
        row = summary["city_counts"].get(bucket, {})
        section.append(f"| {bucket} | {row.get('all_jobs', 0)} | {row.get('is_tech_true', 0)} | {row.get('is_tech_false', 0)} | {row.get('is_tech_null', 0)} | {row.get('product_design_jobs', 0)} |")
    section += [
        "", "### Excluded from analysis", "",
        "These records remain in collection history and are excluded from tech-only analysis.", "",
        "| Location bucket | Non-Tech | Unclassified role |", "|---|---:|---:|",
    ]
    for city in (*CITY_BUCKETS, *EXTRA_BUCKETS):
        row = summary["city_counts"].get(city, {})
        section.append(f"| {city} | {row.get('non_tech_jobs', 0)} | {row.get('unclassified_jobs', 0)} |")
    section.append(end_marker)
    block = "\n".join(section)
    if start_marker in existing and end_marker in existing:
        before = existing.split(start_marker, 1)[0].rstrip()
        after = existing.split(end_marker, 1)[1].lstrip()
        updated = before + "\n\n" + block + ("\n\n" + after if after else "") + "\n"
    else:
        updated = existing.rstrip() + "\n\n" + block + "\n"
    FEASIBILITY.write_text(updated, encoding="utf-8")


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
        f"- Active tech jobs in the five cities: {summary['five_city_tech_jobs']}",
        f"- Existing active listings rebucketed into the five cities: {summary['location_rebucket_moves']['all_jobs']}",
        f"- Tech jobs among those rebucketed listings: {summary['location_rebucket_moves']['tech_jobs']}",
        "", "## Counts by role category (active jobs in private history)", "",
        "| Role category | Count |", "|---|---:|",
    ]
    for category in CATEGORIES:
        lines.append(f"| {category} | {summary['active_counts_by_role_category'].get(category, 0)} |")
    lines += [
        "", "## Excluded from analysis", "",
        "Non-Tech and Unclassified roles remain in collection history but are excluded from tech-only analysis.",
        "", "| Role category | Count |", "|---|---:|",
        f"| Non-Tech | {summary['active_counts_by_role_category'].get('Non-Tech', 0)} |",
        f"| Unclassified | {summary['active_counts_by_role_category'].get('Unclassified', 0)} |",
        "", "This public summary contains aggregate counts only; no job titles, descriptions, URLs, company-level errors, or raw snapshots.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    location_rebucket_moves = preview_location_rebucket_moves(DB_PATH)
    client = CollectorClient()
    connection = connect(DB_PATH)
    totals = {
        "run_at": utc_now(), "boards_attempted": 0, "boards_fetched": 0, "errors": 0,
        "new_jobs": 0, "changed_jobs": 0, "vanished_jobs": 0, "jobs_seen_this_run": 0,
        "location_rebucket_moves": location_rebucket_moves,
    }
    for board in load_boards():
        totals["boards_attempted"] += 1
        platform, token = board["platform"], board["token"]
        started = utc_now()
        try:
            result = collect_complete_board(connection, client, board)
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
    city_counts = {}
    for row in connection.execute(
        """SELECT city_bucket, COUNT(*) AS all_jobs,
           SUM(CASE WHEN is_tech=1 THEN 1 ELSE 0 END) AS tech_jobs,
           SUM(CASE WHEN is_tech=1 THEN 1 ELSE 0 END) AS is_tech_true,
           SUM(CASE WHEN is_tech=0 THEN 1 ELSE 0 END) AS is_tech_false,
           SUM(CASE WHEN is_tech IS NULL THEN 1 ELSE 0 END) AS is_tech_null,
           SUM(CASE WHEN role_category='Product/Design (tech-adjacent)' THEN 1 ELSE 0 END) AS product_design_jobs,
           SUM(CASE WHEN role_category='Non-Tech' THEN 1 ELSE 0 END) AS non_tech_jobs,
           SUM(CASE WHEN role_category='Unclassified' THEN 1 ELSE 0 END) AS unclassified_jobs
           FROM jobs WHERE is_active=1 GROUP BY city_bucket"""
    ):
        city_counts[row["city_bucket"]] = {key: int(row[key] or 0) for key in (
            "all_jobs", "tech_jobs", "is_tech_true", "is_tech_false", "is_tech_null",
            "product_design_jobs", "non_tech_jobs", "unclassified_jobs"
        )}
    totals["city_counts"] = city_counts
    totals["five_city_all_jobs"] = sum(city_counts.get(city, {}).get("all_jobs", 0) for city in CITY_BUCKETS)
    totals["five_city_tech_jobs"] = sum(city_counts.get(city, {}).get("tech_jobs", 0) for city in CITY_BUCKETS)
    totals["boards_not_fetched"] = totals["errors"]
    connection.close()
    write_summary(totals)
    write_feasibility_section(totals)
    LOG.info("Aggregate run summary written; raw DB remains at configured private path.")
    return totals


if __name__ == "__main__":
    run()
