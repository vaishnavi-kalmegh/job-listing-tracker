"""Deterministic role labels from title and optional department/team metadata only."""
from __future__ import annotations

import re

CATEGORIES = (
    "Software Engineering", "Data/ML/AI", "DevOps/Cloud/SRE/Infra", "QA/Test",
    "Security", "IT Support/Systems", "Product/Design (tech-adjacent)", "Non-Tech", "Unclassified",
)
TECH_CATEGORIES = frozenset(CATEGORIES[:7])

# Technical patterns precede generic non-tech terms to avoid false negatives
# such as "Security Operations Analyst" matching "operations analyst".
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Security", re.compile(r"\b(security engineer|security operations|application security|appsec|cyber ?security|infosec|soc analyst|security analyst|penetration test|pentest|vulnerability|iam engineer|identity and access management|grc analyst|security architect|information security|threat intelligence|incident response analyst|security consultant)\b", re.I)),
    ("QA/Test", re.compile(r"\b(qa engineer|qa analyst|quality assurance|quality analyst|software tester|test engineer|test analyst|test automation|automation tester|sdet|manual tester|performance tester|validation engineer|quality engineering|test architect|quality automation|test lead)\b", re.I)),
    ("DevOps/Cloud/SRE/Infra", re.compile(r"\b(devops|site reliability|\bsre\b|cloud engineer|cloud architect|cloud operations|platform engineer|infrastructure engineer|systems engineer|kubernetes|network engineer|database administrator|\bdba\b|release engineer|build engineer|production engineer|production support engineer|noc engineer|network operations engineer|systems administrator|linux administrator|windows administrator|infra engineer|infrastructure operations|platform operations|technical operations engineer)\b", re.I)),
    ("Data/ML/AI", re.compile(r"\b(data scientist|data engineer|data analyst|analytics engineer|machine learning|\bml engineer|\bai engineer|artificial intelligence|deep learning|nlp engineer|computer vision|research scientist|bi engineer|business intelligence developer|bi analyst|data quality analyst|data governance|data operations|etl developer|etl engineer|reporting analyst|analytics consultant|statistician|decision scientist|applied scientist|generative ai|llm engineer|ai researcher|machine learning researcher)\b", re.I)),
    ("Product/Design (tech-adjacent)", re.compile(r"\b(product manager|technical product manager|product owner|ux designer|ui designer|product designer|ux researcher|user experience|user interface|interaction designer|design systems|technical writer|solutions architect|solutions engineer|technical program manager|product operations manager|service designer|experience designer|design researcher|product analyst)\b", re.I)),
    ("IT Support/Systems", re.compile(r"\b(it support|help ?desk|desktop support|service desk|system administrator|sysadmin|it administrator|it analyst|technical support engineer|technical support specialist|support engineer|support analyst|application support|product support|endpoint administrator|it operations technician|it service management|application administrator|application support analyst|customer support engineer|technical services engineer)\b", re.I)),
    ("Software Engineering", re.compile(r"\b(software engineer|software developer|frontend|front-end|backend|back-end|full.?stack|web developer|mobile developer|android developer|ios developer|application developer|application engineer|programmer|firmware engineer|embedded engineer|systems programmer|engineering manager|technical lead|staff engineer|principal engineer|api engineer|integration engineer|integration developer|technology analyst|software architect|solutions developer|developer|programmer analyst|web engineer|mobile engineer|java developer|python developer|\.net developer|javascript developer|salesforce developer|technical consultant - software)\b", re.I)),
)

NON_TECH = re.compile(
    r"\b(sales|account executive|account manager|business development|marketing|recruit(?:er|ing)|"
    r"human resources|\bhr\b|finance|accountant|accounting|legal|lawyer|business operations|"
    r"sales operations|revenue operations|people operations|operations analyst|operations manager|"
    r"operations coordinator|operations specialist|operations associate|customer success|"
    r"customer support representative|relationship manager|talent acquisition|payroll|procurement|"
    r"office manager|administrative assistant|content writer|copywriter|product marketing|"
    r"field marketing|demand generation|accounting operations|financial analyst|investment banking|"
    r"corporate counsel|public relations|communications manager|recruitment coordinator)\b", re.I
)

# Metadata is consulted only if the title itself does not decide the label.
METADATA_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Security", re.compile(r"\b(security|infosec|cyber ?security|application security|soc|identity and access management)\b", re.I)),
    ("QA/Test", re.compile(r"\b(quality assurance|quality engineering|qa\b|testing|test engineering|software validation)\b", re.I)),
    ("DevOps/Cloud/SRE/Infra", re.compile(r"\b(devops|site reliability|sre|cloud engineering|cloud infrastructure|infrastructure engineering|platform engineering|network operations|systems engineering|it infrastructure)\b", re.I)),
    ("Data/ML/AI", re.compile(r"\b(data science|data engineering|data analytics|analytics engineering|business intelligence|machine learning|artificial intelligence|ai research|data platform|data operations)\b", re.I)),
    ("IT Support/Systems", re.compile(r"\b(it support|it systems|help ?desk|service desk|technical support|application support|desktop support|end user computing)\b", re.I)),
    ("Software Engineering", re.compile(r"\b(software engineering|software development|application development|engineering - software|engineering - technology|technology engineering|product engineering|r&d software|research and development - software)\b", re.I)),
    ("Product/Design (tech-adjacent)", re.compile(r"\b(product management|product design|user experience|ux design|ui design|design systems|product experience)\b", re.I)),
)
NON_TECH_METADATA = re.compile(
    r"\b(sales|marketing|human resources|talent acquisition|recruiting|finance|accounting|legal|"
    r"customer success|business operations|people operations|payroll|procurement|communications|"
    r"public relations|corporate affairs|administration|facilities|supply chain|business development)\b", re.I
)


def _classify_text(value: str) -> tuple[str, bool | None]:
    text = str(value or "").strip()
    if not text:
        return "Unclassified", None
    for category, pattern in RULES:
        if pattern.search(text):
            return category, True
    if NON_TECH.search(text):
        return "Non-Tech", False
    return "Unclassified", None


def classify_role(title: str, department: str = "", team: str = "") -> tuple[str, bool | None]:
    """Return (role_category, is_tech) using title and API department/team only."""
    category, is_tech = _classify_text(title)
    if category != "Unclassified":
        return category, is_tech
    metadata = " ".join(str(v or "") for v in (department, team)).strip()
    if not metadata:
        return "Unclassified", None
    for category, pattern in METADATA_RULES:
        if pattern.search(metadata):
            return category, True
    if NON_TECH_METADATA.search(metadata):
        return "Non-Tech", False
    return "Unclassified", None
