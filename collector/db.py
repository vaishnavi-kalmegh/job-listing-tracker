"""SQLite schema and idempotent observation persistence."""
from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from discovery.roles import classify_role

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS companies (
  platform TEXT NOT NULL, token TEXT NOT NULL, name TEXT NOT NULL,
  PRIMARY KEY (platform, token)
);
CREATE TABLE IF NOT EXISTS jobs (
  platform TEXT NOT NULL, token TEXT NOT NULL, job_id TEXT NOT NULL,
  title TEXT NOT NULL, department TEXT NOT NULL DEFAULT '', team TEXT NOT NULL DEFAULT '',
  role_category TEXT NOT NULL DEFAULT 'Unclassified', is_tech INTEGER,
  entry_level INTEGER NOT NULL DEFAULT 0,
  location_raw TEXT NOT NULL, city_bucket TEXT NOT NULL,
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

ENTRY_INCLUDE = re.compile(r"\b(fresher|junior|associate|graduate|intern(ship)?|entry[- ]level|trainee|0\s*[-–to]+\s*2\s+years?)\b", re.I)
ENTRY_EXCLUDE = re.compile(r"\b(senior|sr\\.?|lead|principal|manager|director|head of|staff engineer)\b", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(description: str) -> str:
    return hashlib.sha256(description.encode("utf-8")).hexdigest()


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    # Forward-only migration for DBs created by the earlier Phase 2 scaffold.
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(jobs)")}
    migrations = {
        "department": "TEXT NOT NULL DEFAULT ''",
        "team": "TEXT NOT NULL DEFAULT ''",
        "role_category": "TEXT NOT NULL DEFAULT 'Unclassified'",
        "is_tech": "INTEGER",
        "entry_level": "INTEGER NOT NULL DEFAULT 0",
    }
    for name, sql_type in migrations.items():
        if name not in columns:
            connection.execute(f"ALTER TABLE jobs ADD COLUMN {name} {sql_type}")
    # Recompute labels for existing rows from title only; descriptions are never passed.
    for row in connection.execute("SELECT platform,token,job_id,title,department,team FROM jobs").fetchall():
        category, is_tech = classify_role(row["title"], row["department"], row["team"])
        connection.execute(
            "UPDATE jobs SET role_category=?,is_tech=?,entry_level=? WHERE platform=? AND token=? AND job_id=?",
            (category, None if is_tech is None else int(is_tech),
             int(bool(ENTRY_INCLUDE.search(row["title"])) and not bool(ENTRY_EXCLUDE.search(row["title"]))),
             row["platform"], row["token"], row["job_id"]),
        )
    connection.commit()
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
        title = str(item["title"])
        department = str(item.get("department", "") or "")
        team = str(item.get("team", "") or "")
        # Classification intentionally excludes description_text.
        category, is_tech = classify_role(title, department, team)
        entry_level = int(bool(ENTRY_INCLUDE.search(title)) and not bool(ENTRY_EXCLUDE.search(title)))
        description = str(item.get("description_text", ""))
        digest = content_hash(description)
        existing = connection.execute(
            "SELECT content_hash FROM jobs WHERE platform=? AND token=? AND job_id=?",
            (platform, token, job_id),
        ).fetchone()
        if existing is None:
            connection.execute(
                """INSERT INTO jobs(platform,token,job_id,title,department,team,role_category,is_tech,entry_level,
                   location_raw,city_bucket,url,description_text,content_hash,first_seen,last_seen,is_active)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                (platform, token, job_id, title, department, team, category,
                 None if is_tech is None else int(is_tech), entry_level,
                 item["location_raw"], item["city_bucket"], item.get("url", ""), description,
                 digest, now, now),
            )
            new_count += 1
        else:
            if existing["content_hash"] != digest:
                changed_count += 1
            connection.execute(
                """UPDATE jobs SET title=?,department=?,team=?,role_category=?,is_tech=?,entry_level=?,
                   location_raw=?,city_bucket=?,url=?,description_text=?,content_hash=?,last_seen=?,is_active=1
                   WHERE platform=? AND token=? AND job_id=?""",
                (title, department, team, category, None if is_tech is None else int(is_tech),
                 entry_level, item["location_raw"], item["city_bucket"], item.get("url", ""),
                 description, digest, now, platform, token, job_id),
            )
        connection.execute(
            "INSERT OR IGNORE INTO observations(platform,token,job_id,observed_at,content_hash) VALUES(?,?,?,?,?)",
            (platform, token, job_id, now, digest),
        )
    if seen_ids:
        placeholders = ",".join("?" for _ in seen_ids)
        cursor = connection.execute(
            f"UPDATE jobs SET is_active=0 WHERE platform=? AND token=? AND is_active=1 AND job_id NOT IN ({placeholders})",
            [platform, token, *seen_ids],
        )
    else:
        cursor = connection.execute(
            "UPDATE jobs SET is_active=0 WHERE platform=? AND token=? AND is_active=1",
            (platform, token),
        )
    vanished = cursor.rowcount
    connection.commit()
    return {"new": new_count, "changed": changed_count, "vanished": vanished, "seen": len(seen_ids)}
