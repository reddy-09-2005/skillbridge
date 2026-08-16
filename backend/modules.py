"""
modules.py
Ties nlp.py (skill extraction) and embeddings.py (semantic ranking) together
into a single resume -> ranked, skill-annotated job list pipeline.
"""

from nlp import extract_skills
from embeddings import rank_jobs


def match_skills_to_jobs(resume_text, jobs, top_n=10):
    resume_skills = extract_skills(resume_text)
    ranked = rank_jobs(resume_text, jobs, top_n=top_n)

    for job in ranked:
        job_text = f"{job.get('title', '')} {job.get('description', '')}"
        job_skills = extract_skills(job_text)
        matched = sorted(set(resume_skills) & set(job_skills))
        missing = sorted(set(job_skills) - set(resume_skills))
        job["matched_skills"] = matched
        job["missing_skills"] = missing

    return {"resume_skills": resume_skills, "jobs": ranked}