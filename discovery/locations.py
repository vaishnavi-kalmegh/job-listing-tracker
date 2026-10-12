"""Conservative normalization into project-defined Indian city buckets."""
from __future__ import annotations

import re

CITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "Pune": (
        r"\bpune\b", r"\bhinjewadi\b", r"\bhinjawadi\b", r"\bkharadi\b",
    ),
    "Hyderabad": (
        r"\bhyderabad\b", r"\bsecunderabad\b", r"\bgachibowli\b",
        r"\bhitec\s+city\b", r"\bhitech\s+city\b",
    ),
    "Bengaluru": (
        r"\bbengaluru\b", r"\bbangalore\b", r"\bbangalore\s+urban\b",
        r"\bwhitefield\b",
    ),
    "Delhi NCR": (
        r"\bdelhi\b", r"\bnew delhi\b", r"\bgurgaon\b",
        r"\bgurugram\b", r"\bnoida\b", r"\bgreater noida\b",
        r"\bfaridabad\b", r"\bghaziabad\b",
    ),
    "Mumbai": (
        r"\bmumbai\b", r"\bnavi mumbai\b", r"\bthane\b",
        r"\bandheri\b", r"\bpowai\b", r"\bbkc\b",
        r"\bbandra kurla complex\b",
    ),
}

REMOTE_PATTERNS = (
    r"\bindia\s*[-:]?\s*remote\b",
    r"\bremote\s*[-:]?\s*india\b",
    r"\banywhere in india\b",
)
REMOTE_WORDS = (r"\bremote\b", r"\bwork from anywhere\b")

# These signals are deliberately explicit. A vague or unknown place stays Unparsed;
# do not guess a country from abbreviations that can also be ordinary words.
OUTSIDE_INDIA_COUNTRIES = (
    r"\b(united states|united states of america|usa|u\.s\.a\.|u\.s\.|us)\b",
    r"\b(united kingdom|uk|u\.k\.|england|scotland|wales|northern ireland)\b",
    r"\b(canada|mexico|brazil|argentina|chile|colombia|peru)\b",
    r"\b(australia|new zealand|singapore|malaysia|indonesia|philippines|thailand|vietnam)\b",
    r"\b(germany|france|netherlands|the netherlands|ireland|spain|italy|portugal|switzerland)\b",
    r"\b(sweden|norway|denmark|finland|poland|czech republic|czechia|romania|hungary|ukraine)\b",
    r"\b(united arab emirates|uae|saudi arabia|qatar|kuwait|israel|jordan|turkey|türkiye)\b",
    r"\b(japan|china|hong kong|taiwan|south korea|korea|pakistan|bangladesh|sri lanka|nepal)\b",
    r"\b(south africa|kenya|nigeria|egypt|ghana|morocco|ethiopia|rwanda)\b",
)

OUTSIDE_INDIA_CITIES = (
    r"\blondon\b", r"\bdublin\b", r"\bmanchester\b", r"\bedinburgh\b",
    r"\bnew york\b", r"\bsan francisco\b", r"\blos angeles\b",
    r"\bseattle\b", r"\baustin\b", r"\bboston\b", r"\bchicago\b",
    r"\bdenver\b", r"\bdallas\b", r"\bhouston\b", r"\batlanta\b",
    r"\btoronto\b", r"\bvancouver\b", r"\bmontreal\b", r"\bottawa\b",
    r"\bsydney\b", r"\bmelbourne\b", r"\bbrisbane\b", r"\bperth\b",
    r"\bauckland\b", r"\bwellington\b", r"\bsingapore\b",
    r"\bberlin\b", r"\bmunich\b", r"\bfrankfurt\b", r"\bamsterdam\b",
    r"\bparis\b", r"\bmadrid\b", r"\bbarcelona\b", r"\brome\b",
    r"\bmilan\b", r"\bzurich\b", r"\bstockholm\b", r"\bcopenhagen\b",
    r"\boslo\b", r"\bhelsinki\b", r"\bprague\b", r"\bwarsaw\b",
    r"\bdubai\b", r"\babu dhabi\b", r"\briyadh\b", r"\bdoha\b",
    r"\btokyo\b", r"\bosaka\b", r"\bseoul\b", r"\bbeijing\b",
    r"\bshanghai\b", r"\btaipei\b", r"\btel aviv\b",
    r"\bcape town\b", r"\bjohannesburg\b", r"\bnairobi\b", r"\blagos\b",
)


def normalize_location(location: str | None) -> str:
    """Return an Indian city, India remote/other, Outside India, or Unparsed.

    Known Indian city/suburb evidence takes precedence over generic remote wording.
    A clearly named non-India country/city is Outside India. Unknown/ambiguous
    strings stay Unparsed rather than being assigned a guessed geography.
    """
    if not location or not location.strip():
        return "Unparsed"
    value = re.sub(r"[,/|]+", " ", location.casefold())

    for bucket, patterns in CITY_PATTERNS.items():
        if any(re.search(pattern, value) for pattern in patterns):
            return bucket

    # Explicit India remote/India location remains distinct from Outside India.
    if any(re.search(pattern, value) for pattern in REMOTE_PATTERNS):
        return "India - Remote/Other"
    if re.search(r"\bindia\b", value):
        return "India - Remote/Other"

    if any(re.search(pattern, value) for pattern in OUTSIDE_INDIA_COUNTRIES):
        return "Outside India"
    if any(re.search(pattern, value) for pattern in OUTSIDE_INDIA_CITIES):
        return "Outside India"

    if any(re.search(pattern, value) for pattern in REMOTE_WORDS):
        return "India - Remote/Other"
    return "Unparsed"
