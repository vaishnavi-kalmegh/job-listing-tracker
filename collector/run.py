"""Run one collector pass over the verified public board registry.

The collector stores full descriptions only in the local SQLite database. The
database is gitignored and must not be committed to the public repository.
"""
from __future__ import annotations

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from collector.client import CollectorClient, normalize_job
from collector.db import connect, save_complete_snapshot, utc_now
from discovery.discover import HostStopped, ProbeError
from discovery.locations import normalize_location

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ROOT / "data" / "boards.csv"
DB_PATH = ROOT / "data" / "private" / "jobs.db"
LOG = logging.getLogger("collector")


def load_boards() -> list[dict[str, str]]:
    with BOARDS.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [r for r in rows if r.get("platform") in {"greenhouse", "lever"} and r.get("token")]


def run() -> dict[str, int]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    client = CollectorClient()
    connection = connect(DB_PATH)
    totals = {"boards": 0, "successful": 0, "errors": 0, "new": 0, "changed": 0, "vanished": 0, "seen": 0}
    for board in load_boards():
        totals["boards"] += 1
        platform, token = board["platform"], board["token"]
        started = utc_now()
        try:
            raw_jobs, complete, status = client.fetch(platform, token)
            if not complete:
                raise ProbeError(f"incomplete_fetch:{status}")
            normalized = []
            parse_errors = 0
            for raw in raw_jobs:
                try:
                    item = normalize_job(platform, raw)
                    if item["city_bucket"] in {"Pune", "Hyderabad", "Bengaluru", "Delhi NCR", "Mumbai", "India - Remote/Other", "Unclassified"}:
                        normalized.append(item)
                except (ValueError, TypeError, AttributeError):
                    parse_errors += 1
                    LOG.exception("Could not normalize a record from %s/%s; snapshot will not be used to infer disappearance", platform, token)
            if parse_errors:
                # A malformed listing means absence cannot safely be inferred:
                # retain no deactivation inference for this board this run.
                raise ProbeError(f"parsing_incomplete:{parse_errors}_records")
            summary = save_complete_snapshot(connection, platform, token, board.get("company_name", token), normalized)
            totals["successful"] += 1
            for key in ("new", "changed", "vanished", "seen"):
                totals[key] += summary[key]
            connection.execute(
                "INSERT INTO collection_runs(started_at,finished_at,platform,token,status,jobs_seen) VALUES(?,?,?,?,?,?)",
                (started, utc_now(), platform, token, "success_complete", summary["seen"]),
            )
            connection.commit()
            LOG.info("%s/%s: complete jobs=%d new=%d changed=%d vanished=%d", platform, token, summary["seen"], summary["new"], summary["changed"], summary["vanished"])
        except (ProbeError, HostStopped) as exc:
            totals["errors"] += 1
            connection.execute(
                "INSERT INTO collection_runs(started_at,finished_at,platform,token,status,error_type,jobs_seen) VALUES(?,?,?,?,?,?,0)",
                (started, utc_now(), platform, token, "failed_or_incomplete", str(exc)[:500]),
            )
            connection.commit()
            LOG.error("%s/%s failed; no listings marked inactive: %s", platform, token, exc)
    connection.close()
    LOG.info("RUN SUMMARY: %s", totals)
    return totals


if __name__ == "__main__":
    run()
