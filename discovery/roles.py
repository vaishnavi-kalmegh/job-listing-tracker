"""Deterministic role labels from title and optional department/team metadata only."""
from __future__ import annotations

import re

CATEGORIES = (
    "Software Engineering",
    "Data/ML/AI",
    "DevOps/Cloud/SRE/Infra",
    "QA/Test",
    "Security",
    "IT Support/Systems",
    "Product/Design (tech-adjacent)",
    "Non-Tech",
    "Unclassified",
)
TECH_CATEGORIES = frozenset(CATEGORIES[:7])

# Narrow, explicit non-tech terms. Do not treat generic "operations" in a
# technical title such as Security Operations Engineer as automatically non-tech.
NON_TECH = re.compile(
    r"\b(sales|account executive|account manager|business development|marketing|recruit(?:er|ing)|"
    r"human resources|\bhr\b|finance|accountant|accounting|legal|lawyer|"
    r"business operations|sales operations|revenue operations|people operations|"
    r"operations analyst|operations manager|operations coordinator|operations specialist|operations associate|"
    r"customer success|customer support representative|relationship manager|"
    r"talent acquisition|payroll|procurement|office manager|administrative assistant|"
    r"content writer|copywriter)\b", re.I
)
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Security", re.compile(r"\b(security engineer|security operations|application security|appsec|cyber ?security|infosec|soc analyst|security analyst|penetration test|pentest|vulnerability|iam engineer|identity and access management|grc analyst|security architect)\b", re.I)),
    ("QA/Test", re.compile(r"\b(qa engineer|qa analyst|quality assurance|quality analyst|software tester|test engineer|test analyst|test automation|automation tester|sdet|manual tester|performance tester|validation engineer)\b", re.I)),
    ("DevOps/Cloud/SRE/Infra", re.compile(r"\b(devops|site reliability|\bsre\b|cloud engineer|cloud architect|platform engineer|infrastructure engineer|systems engineer|kubernetes|network engineer|database administrator|\bdba\b|release engineer|build engineer|production engineer)\\b", re.I)),
    ("Data/ML/AI", re.compile(r"\b(data scientist|data engineer|data analyst|analytics engineer|machine learning|\bml engineer|\bai engineer|artificial intelligence|deep learning|nlp engineer|computer vision|research scientist|bi engineer|business intelligence developer|statistician)\\b", re.I)),
    ("Product/Design (tech-adjacent)", re.compile(r"\b(product manager|technical product manager|product owner|ux designer|ui designer|product designer|ux researcher|user experience|user interface|interaction designer|design systems|technical writer|solutions architect|solutions engineer)\\b", re.I)),
    ("IT Support/Systems", re.compile(r"\b(it support|help ?desk|desktop support|service desk|system administrator|sysadmin|it administrator|it analyst|technical support engineer|support engineer|endpoint administrator|it operations technician)\\b", re.I)),
    ("Software Engineering", re.compile(r"\b(software engineer|software developer|frontend|front-end|backend|back-end|full.?stack|web developer|mobile developer|android developer|ios developer|application developer|programmer|firmware engineer|embedded engineer|systems programmer|engineering manager|technical lead|staff engineer|principal engineer)\\b", re.I)),
)


def _classify_text(value: str) -> tuple[str, bool | None]:
    if not value.strip():
        return "Unclassified", None
    if NON_TECH.search(value):
        return "Non-Tech", False
    for category, pattern in RULES:
        if pattern.search(value):
            return category, True
    return "Unclassified", None


def classify_role(title: str, department: str = "", team: str = "") -> tuple[str, bool | None]:
    """Return (role_category, is_tech); never reads a description/body field.

    Title evidence has precedence so a generic department label cannot override
    a clear engineering title. Department/team metadata resolves ambiguous titles.
    """
    title_text = str(title or "").strip()
    category, is_tech = _classify_text(title_text)
    if category != "Unclassified":
        return category, is_tech

    metadata = " ".join(str(v or "") for v in (department, team)).strip()
    if not metadata:
        return "Unclassified", None

    category, is_tech = _classify_text(metadata)
    if category != "Unclassified":
        return category, is_tech

    # Resolve common ambiguous titles only when the department/team explicitly
    # names a specialized technical function. Generic "Engineering" is insufficient.
    metadata_rules = (
        ("Security", re.compile(r"\b(information security|security engineering|application security)\b", re.I)),
        ("QA/Test", re.compile(r"\b(quality engineering|quality assurance|test engineering)\b", re.I)),
        ("DevOps/Cloud/SRE/Infra", re.compile(r"\b(platform engineering|cloud engineering|infrastructure|site reliability)\b", re.I)),
        ("Data/ML/AI", re.compile(r"\b(data science|data engineering|machine learning|artificial intelligence|analytics engineering)\b", re.I)),
        ("IT Support/Systems", re.compile(r"\b(it support|it systems|help ?desk|service desk)\b", re.I)),
        ("Software Engineering", re.compile(r"\b(software engineering|application engineering)\b", re.I)),
        ("Product/Design (tech-adjacent)", re.compile(r"\b(product design|user experience|ux design|ui design)\b", re.I)),
    )
    for category, pattern in metadata_rules:
        if pattern.search(metadata):
            return category, True
    return "Unclassified", None
