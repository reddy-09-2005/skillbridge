
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
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "nosql",
    "mongodb", "postgresql", "mysql", "react", "angular", "vue", "node.js",
    "express", "flask", "django", "fastapi", "aws", "azure", "gcp", "docker",
    "kubernetes", "git", "ci/cd", "machine learning", "deep learning", "nlp",
    "data analysis", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn",
    "tableau", "power bi", "excel", "rest api", "graphql", "html", "css",
    "linux", "agile", "scrum", "project management", "communication",
    "leadership", "problem solving",
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