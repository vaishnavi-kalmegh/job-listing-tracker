"""Conservative normalization into project-defined Indian city buckets."""
from __future__ import annotations

import re

CITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "Pune": (r"\bpune\b",),
    "Hyderabad": (r"\bhyderabad\b", r"\bsecunderabad\b"),
    "Bengaluru": (r"\bbengaluru\b", r"\bbangalore\b"),
    "Delhi NCR": (
        r"\bdelhi\b", r"\bnew delhi\b", r"\bgurgaon\b",
        r"\bgurugram\b", r"\bnoida\b", r"\bgreater noida\b",
        r"\bfaridabad\b", r"\bghaziabad\b",
    ),
    "Mumbai": (r"\bmumbai\b", r"\bnavi mumbai\b", r"\bthane\b"),
}
REMOTE_PATTERNS = (r"\bindia\s*[-:]?\s*remote\b", r"\bremote\s*[-:]?\s*india\b", r"\banywhere in india\b")
REMOTE_WORDS = (r"\bremote\b", r"\bwork from anywhere\b")


def normalize_location(location: str | None) -> str:
    """Return a city bucket, India remote/other, or Unclassified.

    City evidence takes precedence over generic 'remote' wording so a
    location such as 'Remote, Mumbai' remains attributable to Mumbai.
    """
    if not location or not location.strip():
        return "Unclassified"
    value = re.sub(r"[,/|]+", " ", location.casefold())
    for bucket, patterns in CITY_PATTERNS.items():
        if any(re.search(pattern, value) for pattern in patterns):
            return bucket
    if any(re.search(pattern, value) for pattern in REMOTE_PATTERNS):
        return "India - Remote/Other"
    if any(re.search(pattern, value) for pattern in REMOTE_WORDS):
        return "India - Remote/Other"
    if re.search(r"\bindia\b", value):
        return "India - Remote/Other"
    return "Unclassified"
