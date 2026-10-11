"""Polite API client with completeness-aware Greenhouse and Lever pagination."""
from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import requests

from discovery.discover import USER_AGENT, HostStopped, ProbeError
from discovery.locations import normalize_location


class CollectorClient:
    def __init__(self, timeout: float = 25.0) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
        self.timeout = timeout
        self.last_request = 0.0
        self.stopped_hosts: set[str] = set()

    def get_json(self, url: str) -> Any:
        host = urlparse(url).netloc.lower()
        if host in self.stopped_hosts:
            raise HostStopped(f"host paused: {host}")
        wait = 1.0 - (time.monotonic() - self.last_request)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(3):
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as exc:
                if attempt == 2:
                    raise ProbeError(f"network_or_timeout: {exc}") from exc
                time.sleep(2 ** attempt)
                continue
            if response.status_code in (403, 429):
                self.stopped_hosts.add(host)
                raise HostStopped(f"http_{response.status_code}; host paused for run")
            if response.status_code in (500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            if not response.ok:
                raise ProbeError(f"http_error:{response.status_code}")
            try:
                return response.json()
            except ValueError as exc:
                raise ProbeError("invalid_json") from exc
        raise ProbeError("retry_exhausted")

    def fetch(self, platform: str, token: str) -> tuple[list[dict[str, Any]], bool, str]:
        jobs: list[dict[str, Any]] = []
        if platform == "greenhouse":
            page = 1
            while page <= 50:
                payload = self.get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true&per_page=100&page={page}")
                if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list) or any(not isinstance(j, dict) for j in payload["jobs"]):
                    return jobs, False, "schema_error"
                page_jobs = payload["jobs"]
                jobs.extend(page_jobs)
                if len(page_jobs) < 100:
                    return jobs, True, "ok"
                page += 1
            return jobs, False, "pagination_cap_reached"
        if platform == "lever":
            skip = 0
            while skip < 5000:
                payload = self.get_json(f"https://api.lever.co/v0/postings/{token}?mode=json&limit=100&skip={skip}")
                if not isinstance(payload, list) or any(not isinstance(j, dict) for j in payload):
                    return jobs, False, "schema_error"
                jobs.extend(payload)
                if len(payload) < 100:
                    return jobs, True, "ok"
                skip += 100
            return jobs, False, "pagination_cap_reached"
        return [], False, "unsupported_platform"


def normalize_job(platform: str, raw: dict[str, Any]) -> dict[str, str]:
    if platform == "greenhouse":
        loc = raw.get("location")
        location = str(loc.get("name") or "") if isinstance(loc, dict) else ""
        job_id = str(raw.get("id") or "")
        title = str(raw.get("title") or "")
        url = str(raw.get("absolute_url") or "")
        description = str(raw.get("content") or "")
    else:
        categories = raw.get("categories")
        location = str(categories.get("location") or "") if isinstance(categories, dict) else ""
        job_id = str(raw.get("id") or "")
        title = str(raw.get("text") or raw.get("title") or "")
        url = str(raw.get("hostedUrl") or "")
        description = str(raw.get("descriptionPlain") or raw.get("description") or "")
    if not job_id or not title:
        raise ValueError("job_missing_required_id_or_title")
    # Store only allowed target-city, India remote/other, and Unclassified jobs.
    bucket = normalize_location(location)
    return {
        "job_id": job_id, "title": title, "location_raw": location,
        "city_bucket": bucket, "url": url, "description_text": description,
    }
