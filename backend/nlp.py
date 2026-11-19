"""
nlp.py
Skill and keyword extraction from raw resume / job description text.
Uses a curated skill bank + spaCy for general keyword extraction.
"""

import re
import spacy

try:
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if the model hasn't been downloaded yet
    # (run: python -m spacy download en_core_web_sm)
    _nlp = spacy.blank("en")

SKILL_BANK = {
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go",
    "rust", "kotlin", "swift", "php", "ruby", "scala", "r",

    # Web / frameworks
    "react", "angular", "vue", "node.js", "express", "flask", "django",
    "fastapi", "next.js", "spring boot", "html", "css", "sass", "webpack",
    "rest api", "graphql", "microservices",

    # Databases
    "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "oracle",
    "database design", "indexing", "replication", "sqlite",

    # Cloud / DevOps / infra
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "ci/cd", "git", "github actions", "gitlab ci", "linux",
    "bash scripting", "networking", "iam", "vpc", "load balancing",
    "monitoring", "grafana", "prometheus", "cloudformation", "helm",

    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "data analysis", "pandas",
    "numpy", "tensorflow", "pytorch", "scikit-learn", "keras", "mlops",
    "data engineering", "etl", "airflow", "spark", "kafka", "hadoop",
    "data warehousing", "statistics", "data visualization", "tableau",
    "power bi", "excel", "big data", "computer vision",

    # Security
    "network security", "penetration testing", "siem", "firewalls",
    "incident response", "risk assessment", "cryptography", "vulnerability assessment",
    "vpn", "tcp/ip", "cybersecurity", "iso 27001", "owasp",

    # Systems / networking
    "windows server", "active directory", "virtualization", "vmware",
    "routing", "switching", "cisco", "dns", "backup management",

    # Mobile
    "flutter", "react native", "android", "ios development", "firebase",

    # QA / testing
    "selenium", "manual testing", "automation testing", "test cases",
    "api testing", "regression testing", "bug tracking", "cypress",
    "test frameworks", "junit", "pytest",

    # Design / product
    "figma", "wireframing", "prototyping", "user research", "adobe xd",
    "usability testing", "responsive design", "ui design", "ux design",

    # Project / business
    "agile", "scrum", "kanban", "jira", "product roadmap", "stakeholder management",
    "requirements gathering", "process mapping", "risk management",
    "budgeting", "market research", "user stories", "documentation",

    # Blockchain / other specialties
    "solidity", "smart contracts", "ethereum", "web3.js", "unity", "unreal engine",
    "3d modeling", "embedded systems", "rtos", "microcontrollers", "firmware",
    "salesforce", "apex", "sap", "erp implementation",

    # Soft skills
    "communication", "leadership", "problem solving", "project management",
    "team collaboration", "critical thinking", "time management",
}


def extract_skills(text):
    """Return a sorted list of known skills found in the given text."""
    text_lower = text.lower()
    found = set()
    for skill in SKILL_BANK:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    return sorted(found)


def extract_keywords(text, top_n=20):
    """General-purpose keyword extraction (nouns/lemmas by frequency)."""
    doc = _nlp(text)
    freq = {}
    for token in doc:
        if token.is_alpha and not token.is_stop and len(token.text) > 2:
            key = token.lemma_.lower()
            freq[key] = freq.get(key, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:top_n]