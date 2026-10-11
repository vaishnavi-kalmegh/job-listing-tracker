"""SQLite schema and idempotent observation persistence."""
from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS companies (
  platform TEXT NOT NULL, token TEXT NOT NULL, name TEXT NOT NULL,
  PRIMARY KEY (platform, token)
);
CREATE TABLE IF NOT EXISTS jobs (
  platform TEXT NOT NULL, token TEXT NOT NULL, job_id TEXT NOT NULL,
  title TEXT NOT NULL, location_raw TEXT NOT NULL, city_bucket TEXT NOT NULL,
  url TEXT NOT NULL, description_text TEXT NOT NULL, content_hash TEXT NOT NULL,
  first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, is_active INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (platform, token, job_id)
);
CREATE TABLE IF NOT EXISTS observations (
  platform TEXT NOT NULL, token TEXT NOT NULL, job_id TEXT NOT NULL,
  observed_at TEXT NOT NULL, content_hash TEXT NOT NULL,
  PRIMARY KEY (platform, token, job_id, observed_at),
  FOREIGN KEY (platform, token, job_id) REFERENCES jobs(platform, token, job_id)
);
CREATE TABLE IF NOT EXISTS collection_runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL, finished_at TEXT,
  platform TEXT NOT NULL, token TEXT NOT NULL,
  status TEXT NOT NULL, error_type TEXT, jobs_seen INTEGER NOT NULL DEFAULT 0
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(description: str) -> str:
    return hashlib.sha256(description.encode("utf-8")).hexdigest()


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def save_complete_snapshot(
    connection: sqlite3.Connection,
    platform: str,
    token: str,
    company_name: str,
    jobs: list[dict[str, Any]],
    observed_at: str | None = None,
) -> dict[str, int]:
    """Persist only a successful, complete snapshot; safely handles return after absence."""
    now = observed_at or utc_now()
    seen_ids: set[str] = set()
    new_count = changed_count = 0
    connection.execute(
        "INSERT INTO companies(platform,token,name) VALUES(?,?,?) "
        "ON CONFLICT(platform,token) DO UPDATE SET name=excluded.name",
        (platform, token, company_name),
    )
    for item in jobs:
        job_id = str(item["job_id"])
        seen_ids.add(job_id)
        digest = content_hash(str(item.get("description_text", "")))
        existing = connection.execute(
            "SELECT content_hash FROM jobs WHERE platform=? AND token=? AND job_id=?",
            (platform, token, job_id),
        ).fetchone()
        if existing is None:
            connection.execute(
                """INSERT INTO jobs(platform,token,job_id,title,location_raw,city_bucket,url,
                   description_text,content_hash,first_seen,last_seen,is_active)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,1)""",
                (platform, token, job_id, item["title"], item["location_raw"], item["city_bucket"],
                 item.get("url", ""), item.get("description_text", ""), digest, now, now),
            )
            new_count += 1
        else:
            if existing["content_hash"] != digest:
                changed_count += 1
            connection.execute(
                """UPDATE jobs SET title=?,location_raw=?,city_bucket=?,url=?,description_text=?,
                   content_hash=?,last_seen=?,is_active=1
                   WHERE platform=? AND token=? AND job_id=?""",
                (item["title"], item["location_raw"], item["city_bucket"], item.get("url", ""),
                 item.get("description_text", ""), digest, now, platform, token, job_id),
            )
        connection.execute(
            "INSERT OR IGNORE INTO observations(platform,token,job_id,observed_at,content_hash) VALUES(?,?,?,?,?)",
            (platform, token, job_id, now, digest),
        )
    vanished = 0
    if seen_ids:
        placeholders = ",".join("?" for _ in seen_ids)
        params = [platform, token, *seen_ids]
        cursor = connection.execute(
            f"UPDATE jobs SET is_active=0 WHERE platform=? AND token=? AND is_active=1 AND job_id NOT IN ({placeholders})",
            params,
        )
        vanished = cursor.rowcount
    else:
        # A successful, complete zero-job snapshot is valid and means all prior
        # jobs for this board are absent. Callers must never invoke this method
        # for a failed, partial, or schema-invalid fetch.
        cursor = connection.execute(
            "UPDATE jobs SET is_active=0 WHERE platform=? AND token=? AND is_active=1",
            (platform, token),
        )
        vanished = cursor.rowcount
    connection.commit()
    return {"new": new_count, "changed": changed_count, "vanished": vanished, "seen": len(seen_ids)}
