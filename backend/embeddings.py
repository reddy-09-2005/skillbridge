"""
embeddings.py
Sentence-embedding based semantic similarity between a resume and job postings.
"""

from functools import lru_cache
from sentence_transformers import SentenceTransformer, util
from config import Config


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(Config.EMBEDDING_MODEL)


def similarity_score(resume_text, job_text):
    model = get_model()
    embeddings = model.encode([resume_text, job_text], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(score * 100, 2)


def rank_jobs(resume_text, jobs, top_n=10):
    """Rank a list of job dicts by semantic similarity to the resume text."""
    if not jobs:
        return []

    model = get_model()
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    job_texts = [f"{j.get('title', '')} {j.get('description', '')}" for j in jobs]
    job_embs = model.encode(job_texts, convert_to_tensor=True)
    scores = util.cos_sim(resume_emb, job_embs)[0]

    ranked = sorted(zip(jobs, scores.tolist()), key=lambda x: x[1], reverse=True)

    results = []
    for job, score in ranked[:top_n]:
        job_copy = dict(job)
        job_copy["match_score"] = round(score * 100, 2)
        results.append(job_copy)
    return results