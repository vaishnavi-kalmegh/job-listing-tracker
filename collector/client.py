"""Polite public API client with robots.txt and completeness-aware pagination."""
from __future__ import annotations

import time
import urllib.robotparser
from typing import Any
from urllib.parse import urlparse

import requests

from discovery.discover import USER_AGENT, HostStopped, ProbeError
from discovery.locations import normalize_location

API_HOSTS = {"greenhouse": "boards-api.greenhouse.io", "lever": "api.lever.co"}


class CollectorClient:
    def __init__(self, timeout: float = 25.0) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
        self.timeout = timeout
        self.last_request = 0.0
        self.stopped_hosts: set[str] = set()
        self.robots: dict[str, tuple[str, urllib.robotparser.RobotFileParser | None]] = {}

    def _request(self, url: str) -> requests.Response:
        host = urlparse(url).netloc.lower()
        if host in self.stopped_hosts:
            raise HostStopped(f"host paused: {host}")
        for attempt in range(3):
            wait = 1.0 - (time.monotonic() - self.last_request)
            if wait > 0:
                time.sleep(wait)
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as exc:
                if attempt == 2:
                    raise ProbeError(f"network_or_timeout:{type(exc).__name__}") from exc
                time.sleep(2 ** attempt)
                continue
            if response.status_code in (403, 429):
                self.stopped_hosts.add(host)
                raise HostStopped(f"http_{response.status_code}; host paused for remainder of run")
            if response.status_code in (500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return response
        raise ProbeError("retry_exhausted")

    def _check_robots(self, url: str) -> None:
        host = urlparse(url).netloc.lower()
        if host in self.robots:
            status, parser = self.robots[host]
        else:
            robots_url = f"https://{host}/robots.txt"
            response = self._request(robots_url)
            if response.status_code == 404:
                status, parser = "not_found", None
            elif not response.ok:
                # Do not proceed when a robots policy cannot be retrieved reliably.
                raise ProbeError(f"robots_unresolved:http_{response.status_code}")
            else:
                parser = urllib.robotparser.RobotFileParser()
                parser.set_url(robots_url)
                parser.parse(response.text.splitlines())
                status = "loaded"
            self.robots[host] = (status, parser)
        if parser is not None and not parser.can_fetch(USER_AGENT, url):
            raise ProbeError(f"robots_disallow:{urlparse(url).path}")
        # A missing robots.txt has no machine-readable rules; platform terms
        # remain a separate compliance requirement documented in docs/compliance.md.

    def get_json(self, url: str) -> Any:
        self._check_robots(url)
        response = self._request(url)
        if not response.ok:
            raise ProbeError(f"http_error:{response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise ProbeError("invalid_json") from exc

    def fetch(self, platform: str, token: str) -> tuple[list[dict[str, Any]], bool, str]:
        jobs: list[dict[str, Any]] = []
        if platform == "greenhouse":
            page = 1
            while page <= 50:
                payload = self.get_json(
                    f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true&per_page=100&page={page}"
                )
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


def _names(value: Any) -> str:
    if isinstance(value, list):
        names = []
        for item in value:
            if isinstance(item, dict):
                name = item.get("name")
                if name:
                    names.append(str(name))
            elif isinstance(item, str):
                names.append(item)
        return " / ".join(names)
    if isinstance(value, dict):
        return str(value.get("name") or "")
    return str(value or "")


def normalize_job(platform: str, raw: dict[str, Any]) -> dict[str, str]:
    if platform == "greenhouse":
        location = _names(raw.get("location"))
        job_id = str(raw.get("id") or "")
        title = str(raw.get("title") or "")
        url = str(raw.get("absolute_url") or "")
        description = str(raw.get("content") or "")
        department = _names(raw.get("departments"))
        team = _names(raw.get("teams"))
        if not team:
            team = department
    else:
        categories = raw.get("categories")
        categories = categories if isinstance(categories, dict) else {}
        location = str(categories.get("location") or "")
        job_id = str(raw.get("id") or "")
        title = str(raw.get("text") or raw.get("title") or "")
        url = str(raw.get("hostedUrl") or "")
        description = str(raw.get("descriptionPlain") or raw.get("description") or "")
        department = str(categories.get("department") or "")
        team = str(categories.get("team") or "")
    if not job_id or not title:
        raise ValueError("job_missing_required_id_or_title")
    return {
        "job_id": job_id, "title": title, "department": department, "team": team,
        "location_raw": location, "city_bucket": normalize_location(location),
        "url": url, "description_text": description,
    }
