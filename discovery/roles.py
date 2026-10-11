"""Title-only job role classification; descriptions are deliberately ignored."""
from __future__ import annotations

import re
from typing import Any

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

# Non-tech rules are explicit and run first to avoid false positives such as
# "Technical Account Manager" being treated as an engineering role.
NON_TECH = re.compile(
    r"\b(sales|account executive|business development|marketing|recruit(?:er|ing)|"
    r"human resources|\bhr\b|finance|accountant|accounting|legal|lawyer|"
    r"operations|customer success|customer support representative|"
    r"relationship manager|talent acquisition|payroll|procurement|"
    r"office manager|administrative assistant|content writer|copywriter)\b", re.I
)
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Security", re.compile(r"\b(security engineer|application security|appsec|cyber ?security|infosec|soc analyst|security analyst|penetration test|pentest|vulnerability|iam engineer|identity and access management|grc analyst|security architect)\b", re.I)),
    ("QA/Test", re.compile(r"\b(qa engineer|quality assurance|software tester|test engineer|test automation|automation tester|sdet|manual tester|performance tester|validation engineer)\b", re.I)),
    ("DevOps/Cloud/SRE/Infra", re.compile(r"\b(devops|site reliability|\bsre\b|cloud engineer|cloud architect|platform engineer|infrastructure engineer|systems engineer|kubernetes|network engineer|database administrator|\bdba\b|release engineer|build engineer|production engineer)\b", re.I)),
    ("Data/ML/AI", re.compile(r"\b(data scientist|data engineer|data analyst|analytics engineer|machine learning|\bml engineer|\bai engineer|artificial intelligence|deep learning|nlp engineer|computer vision|research scientist|bi engineer|business intelligence developer|statistician)\b", re.I)),
    ("Product/Design (tech-adjacent)", re.compile(r"\b(product manager|technical product manager|product owner|ux designer|ui designer|product designer|ux researcher|user experience|user interface|interaction designer|design systems|technical writer|solutions architect|solutions engineer)\b", re.I)),
    ("IT Support/Systems", re.compile(r"\b(it support|help ?desk|desktop support|service desk|system administrator|sysadmin|it administrator|it analyst|technical support engineer|support engineer|endpoint administrator|it operations technician)\b", re.I)),
    ("Software Engineering", re.compile(r"\b(software engineer|software developer|frontend|front-end|backend|back-end|full.?stack|web developer|mobile developer|android developer|ios developer|application developer|programmer|firmware engineer|embedded engineer|systems programmer|engineering manager|technical lead|staff engineer|principal engineer)\b", re.I)),
)


def classify_role(title: str, department: str = "", team: str = "") -> tuple[str, bool | None]:
    """Return (role_category, is_tech); never reads description/body fields."""
    evidence = " ".join(str(v or "") for v in (title, department, team)).strip()
    if not evidence:
        return "Unclassified", None
    if NON_TECH.search(evidence):
        return "Non-Tech", False
    for category, pattern in RULES:
        if pattern.search(evidence):
            return category, True
    # A clearly technical department/team can resolve an ambiguous title, but
    # only with specific engineering/IT naming; generic "Technology" is not enough.
    if re.search(r"\b(software engineering|engineering - platform|data science|machine learning|information security|quality engineering|infrastructure|cloud engineering|it systems)\b", " ".join((str(department or ""), str(team or ""))), re.I):
        for category, pattern in RULES:
            if pattern.search(str(department or "") + " " + str(team or "")):
                return category, True
    return "Unclassified", None
