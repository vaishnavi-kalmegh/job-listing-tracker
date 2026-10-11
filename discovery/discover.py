"""Evidence-backed discovery and verification for public Greenhouse/Lever boards."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from discovery.locations import normalize_location

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "discovery" / "seeds.csv"
BOARDS = ROOT / "data" / "boards.csv"
RUN_LOG = ROOT / "reports" / "discovery_run.json"
REPO_URL = "https://github.com/vaishnavi-kalmegh/job-listing-tracker"
USER_AGENT = f"JobListingTrackerResearch/0.1 (+{REPO_URL}; contact via repository issues)"
CITY_BUCKETS = ("Pune", "Hyderabad", "Bengaluru", "Delhi NCR", "Mumbai")
ENTRY_INCLUDE = re.compile(r"\b(fresher|junior|associate|graduate|intern(ship)?|entry[- ]level|0\s*[-–to]+\s*2\s+years?)\b", re.I)
ENTRY_EXCLUDE = re.compile(r"\b(senior|sr\.?|lead|principal|manager|director|head of|staff engineer)\b", re.I)
LOG = logging.getLogger("discovery")


class HostStopped(RuntimeError):
    pass


class ProbeError(RuntimeError):
    pass


class PoliteClient:
    """A shared one-request-per-second client with bounded retry/backoff."""

    def __init__(self, timeout: float = 20.0) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json, text/plain, */*"})
        self.timeout = timeout
        self.last_request = 0.0
        self.stopped_hosts: set[str] = set()
        self.robots: dict[str, dict[str, Any]] = {}

    def get(self, url: str, *, json_expected: bool = False) -> requests.Response:
        host = urlparse(url).netloc.lower()
        if host in self.stopped_hosts:
            raise HostStopped(f"Host paused after HTTP 403/429: {host}")
        delay = 1.0 - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)
        for attempt in range(3):
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as exc:
                if attempt == 2:
                    raise ProbeError(f"timeout_or_network_error: {type(exc).__name__}: {exc}") from exc
                time.sleep(2 ** attempt)
                continue
            if response.status_code in (403, 429):
                self.stopped_hosts.add(host)
                raise HostStopped(f"http_{response.status_code}; host paused for run: {host}")
            if response.status_code in (500, 502, 503, 504):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
            if not response.ok:
                raise ProbeError(f"http_error: status={response.status_code}")
            return response
        raise ProbeError("retry_exhausted")

    def check_robots(self, api_host: str) -> dict[str, Any]:
        if api_host in self.robots:
            return self.robots[api_host]
        robots_url = f"https://{api_host}/robots.txt"
        result: dict[str, Any] = {"url": robots_url, "status": "unresolved", "notes": ""}
        try:
            # robots.txt is fetched through the same politeness controls.
            response = self.get(robots_url)
            result.update(status=f"http_{response.status_code}", notes="Fetched; review relevant path rules before expanding collection.")
            text = response.text[:200_000]
            if "disallow:" in text.lower():
                result["disallow_lines"] = [
                    line.strip() for line in text.splitlines()
                    if line.strip().lower().startswith(("user-agent:", "disallow:", "allow:"))
                ][:100]
        except HostStopped as exc:
            result["status"] = "blocked"
            result["notes"] = str(exc)
        except ProbeError as exc:
            result["status"] = "unresolved"
            result["notes"] = str(exc)
        self.robots[api_host] = result
        return result


def load_seeds(path: Path = SEEDS) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle) if (row.get("company_name") or "").strip()]


def token_evidence_ok(platform: str, token: str, source_url: str) -> bool:
    """Require a source URL that visibly identifies the token on the platform."""
    if not token.strip() or not source_url.strip():
        return False
    parsed = urlparse(source_url)
    host = (parsed.hostname or "").lower()
    path_parts = [p for p in parsed.path.split("/") if p]
    if platform == "greenhouse":
        if host not in {"boards.greenhouse.io", "job-boards.greenhouse.io"}:
            return False
        if path_parts and path_parts[0].casefold() == token.casefold():
            return True
        # Greenhouse also publishes embedded board URLs using ?for=<board_token>.
        from urllib.parse import parse_qs
        return parse_qs(parsed.query).get("for", [""])[0].casefold() == token.casefold()
    if platform == "lever":
        return host in {"jobs.lever.co", "jobs.eu.lever.co"} and bool(path_parts) and path_parts[0].casefold() == token.casefold()
    return False


def entry_level(title: str, description: str) -> bool:
    text = f"{title} {description}"
    return bool(ENTRY_INCLUDE.search(text)) and not bool(ENTRY_EXCLUDE.search(title))


def extract_jobs(platform: str, payload: Any) -> tuple[list[dict[str, Any]], bool, str]:
    """Validate schema and retrieve pagination where the API exposes it.

    Returns (jobs, complete, status). A parse/schema failure is never treated
    as an empty successful board.
    """
    if platform == "greenhouse":
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            return [], False, "schema_error: expected object with jobs list"
        jobs = payload["jobs"]
        meta = payload.get("meta") or {}
        # Greenhouse board endpoint can be paginated with per_page/page. A
        # short page indicates completion; meta.total is checked when present.
        total = meta.get("total") if isinstance(meta, dict) else None
        complete = len(jobs) < 100 or (isinstance(total, int) and len(jobs) >= total)
        return [j for j in jobs if isinstance(j, dict)], complete, "ok" if complete else "pagination_incomplete"
    if platform == "lever":
        if not isinstance(payload, list) or any(not isinstance(j, dict) for j in payload):
            return [], False, "schema_error: expected list of posting objects"
        # Lever's unpaginated response is considered complete only when fewer
        # than the requested page size is returned by our fetcher.
        return payload, len(payload) < 100, "ok" if len(payload) < 100 else "pagination_incomplete"
    return [], False, "unknown_platform"


def fetch_board(client: PoliteClient, platform: str, token: str) -> tuple[list[dict[str, Any]], bool, str, int | None]:
    if platform == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true&per_page=100&page=1"
    elif platform == "lever":
        url = f"https://api.lever.co/v0/postings/{token}?mode=json&limit=100&skip=0"
    else:
        return [], False, "unknown_platform", None
    try:
        response = client.get(url, json_expected=True)
        try:
            payload = response.json()
        except ValueError:
            return [], False, "invalid_json", response.status_code
        jobs, complete, status = extract_jobs(platform, payload)
        # Avoid treating a full first page as complete. Additional pagination
        # is intentionally explicit and bounded to prevent runaway requests.
        if platform == "greenhouse" and not complete:
            page = 2
            while page <= 50:
                next_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true&per_page=100&page={page}"
                next_response = client.get(next_url)
                try:
                    next_payload = next_response.json()
                except ValueError:
                    return jobs, False, "invalid_json_on_page", next_response.status_code
                if not isinstance(next_payload, dict) or not isinstance(next_payload.get("jobs"), list):
                    return jobs, False, "schema_error_on_page", next_response.status_code
                page_jobs = next_payload["jobs"]
                if any(not isinstance(j, dict) for j in page_jobs):
                    return jobs, False, "schema_error_on_page", next_response.status_code
                jobs.extend(page_jobs)
                if len(page_jobs) < 100:
                    return jobs, True, "ok", response.status_code
                page += 1
            return jobs, False, "pagination_cap_reached", response.status_code
        if platform == "lever" and not complete:
            # Continue Lever skip/limit pagination; each request is throttled.
            skip = 100
            while skip < 5000:
                next_response = client.get(f"https://api.lever.co/v0/postings/{token}?mode=json&limit=100&skip={skip}")
                try:
                    page_jobs = next_response.json()
                except ValueError:
                    return jobs, False, "invalid_json_on_page", next_response.status_code
                if not isinstance(page_jobs, list) or any(not isinstance(j, dict) for j in page_jobs):
                    return jobs, False, "schema_error_on_page", next_response.status_code
                jobs.extend(page_jobs)
                if len(page_jobs) < 100:
                    return jobs, True, "ok", response.status_code
                skip += 100
            return jobs, False, "pagination_cap_reached", response.status_code
        return jobs, complete, status, response.status_code
    except HostStopped as exc:
        return [], False, f"host_stopped: {exc}", None
    except ProbeError as exc:
        return [], False, str(exc), None


def job_location(platform: str, job: dict[str, Any]) -> str:
    if platform == "greenhouse":
        location = job.get("location")
        if isinstance(location, dict):
            return str(location.get("name") or "")
        return ""
    categories = job.get("categories")
    if isinstance(categories, dict):
        return str(categories.get("location") or "")
    return ""


def job_title(job: dict[str, Any]) -> str:
    return str(job.get("title") or job.get("text") or "")


def job_description(job: dict[str, Any]) -> str:
    if isinstance(job.get("content"), str):
        return re.sub(r"<[^>]+>", " ", job["content"])
    if isinstance(job.get("descriptionPlain"), str):
        return job["descriptionPlain"]
    return ""


def verify_candidate(client: PoliteClient, seed: dict[str, str], platform: str, token: str) -> dict[str, Any]:
    endpoint_host = "boards-api.greenhouse.io" if platform == "greenhouse" else "api.lever.co"
    robots = client.check_robots(endpoint_host)
    jobs, complete, status, http_status = fetch_board(client, platform, token)
    verified = status == "ok" and complete
    city_counts: Counter[str] = Counter()
    entry_counts: Counter[str] = Counter()
    if verified:
        for job in jobs:
            bucket = normalize_location(job_location(platform, job))
            if bucket in CITY_BUCKETS:
                city_counts[bucket] += 1
                if entry_level(job_title(job), job_description(job)):
                    entry_counts[bucket] += 1
    return {
        "platform": platform, "token": token, "company_name": seed["company_name"].strip(),
        "source": seed.get("source_url", "").strip(), "status": status, "verified": verified,
        "complete": complete, "http_status": http_status, "total_jobs": len(jobs) if verified else "",
        "jobs_per_city": json.dumps({city: city_counts.get(city, 0) for city in CITY_BUCKETS}, sort_keys=True),
        "entry_level_jobs": json.dumps({city: entry_counts.get(city, 0) for city in CITY_BUCKETS}, sort_keys=True),
        "verified_at": datetime.now(timezone.utc).isoformat() if verified else "",
        "robots": robots,
        # Full descriptions remain only in the ignored local run log; this
        # field is never copied to data/boards.csv or any committed report.
        "jobs_for_review": [
            {"title": job_title(job), "description": job_description(job)}
            for job in jobs
        ] if verified else [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-probes", type=int, default=60, help="Hard cap on API board probes (maximum allowed: 300).")
    parser.add_argument("--seeds", type=Path, default=SEEDS)
    args = parser.parse_args()
    if not 1 <= args.max_probes <= 300:
        parser.error("--max-probes must be between 1 and 300")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    seeds = load_seeds(args.seeds)
    client = PoliteClient()
    results: list[dict[str, Any]] = []
    probe_count = 0
    candidates: list[tuple[dict[str, str], str, str]] = []
    for seed in seeds:
        for platform, key in (("greenhouse", "greenhouse_token"), ("lever", "lever_token")):
            token = (seed.get(key) or "").strip()
            if token and token_evidence_ok(platform, token, seed.get("source_url", "")):
                candidates.append((seed, platform, token))
            elif token:
                results.append({"platform": platform, "token": token, "company_name": seed["company_name"],
                                "source": seed.get("source_url", ""), "status": "rejected_token_evidence",
                                "verified": False, "complete": False, "http_status": "", "total_jobs": "",
                                "jobs_per_city": "", "entry_level_jobs": "", "verified_at": ""})
    seen: set[tuple[str, str]] = set()
    for seed, platform, token in candidates:
        key = (platform, token.casefold())
        if key in seen:
            continue
        seen.add(key)
        if probe_count >= args.max_probes:
            LOG.warning("Probe cap reached (%s); remaining candidates not attempted.", args.max_probes)
            break
        probe_count += 1
        LOG.info("Probe %s board token from evidence URL %s", platform, seed.get("source_url", ""))
        result = verify_candidate(client, seed, platform, token)
        results.append(result)
        if result["verified"]:
            LOG.info("Verified %s/%s: %s jobs", platform, token, result["total_jobs"])
        else:
            LOG.warning("Not verified %s/%s: %s", platform, token, result["status"])

    columns = ["platform", "token", "company_name", "source", "total_jobs", "jobs_per_city", "entry_level_jobs", "verified_at"]
    BOARDS.parent.mkdir(parents=True, exist_ok=True)
    with BOARDS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for result in results:
            if result.get("verified"):
                writer.writerow({key: result.get(key, "") for key in columns})
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    RUN_LOG.write_text(json.dumps({
        "run_at": datetime.now(timezone.utc).isoformat(), "probe_cap": args.max_probes,
        "probes_attempted": probe_count, "robots": client.robots, "results": results,
    }, indent=2), encoding="utf-8")
    LOG.info("Wrote %s verified boards to %s", sum(bool(r.get("verified")) for r in results), BOARDS)


if __name__ == "__main__":
    main()
