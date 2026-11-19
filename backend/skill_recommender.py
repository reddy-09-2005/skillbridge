"""
skill_recommender.py
Recommends missing skills for ANY target job role by analyzing
real, live job postings. Each recommended skill comes with
learning resources and a step-by-step study flowchart with
depth info (what to do, and how long it usually takes).
"""

from collections import Counter

from linkedin import search_jobs
from nlp import extract_skills


RESOURCE_LINKS = {
    "python": {"docs": "https://docs.python.org/3/tutorial/", "course": "https://www.coursera.org/specializations/python"},
    "java": {"docs": "https://docs.oracle.com/javase/tutorial/", "course": "https://www.coursera.org/learn/java-programming"},
    "javascript": {"docs": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "course": "https://www.freecodecamp.org/"},
    "sql": {"docs": "https://www.w3schools.com/sql/", "course": "https://www.coursera.org/learn/sql-for-data-science"},
    "docker": {"docs": "https://docs.docker.com/get-started/", "course": "https://www.udemy.com/course/docker-mastery/"},
    "kubernetes": {"docs": "https://kubernetes.io/docs/tutorials/", "course": "https://www.udemy.com/course/certified-kubernetes-administrator-with-practice-tests/"},
    "aws": {"docs": "https://aws.amazon.com/getting-started/", "course": "https://aws.amazon.com/training/digital/"},
    "azure": {"docs": "https://learn.microsoft.com/en-us/training/azure/", "course": "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/"},
    "gcp": {"docs": "https://cloud.google.com/docs/get-started", "course": "https://cloud.google.com/learn/training"},
    "terraform": {"docs": "https://developer.hashicorp.com/terraform/tutorials", "course": "https://developer.hashicorp.com/terraform/tutorials"},
    "git": {"docs": "https://docs.github.com/en/get-started", "course": "https://www.freecodecamp.org/news/git-and-github-crash-course/"},
    "react": {"docs": "https://react.dev/learn", "course": "https://react.dev/learn"},
    "rest api": {"docs": "https://restfulapi.net/", "course": "https://restfulapi.net/"},
    "linux": {"docs": "https://linuxjourney.com/", "course": "https://linuxjourney.com/"},
    "machine learning": {"docs": "https://scikit-learn.org/stable/tutorial/index.html", "course": "https://www.coursera.org/learn/machine-learning-introduction"},
    "networking": {"docs": "https://www.cloudflare.com/learning/network-layer/what-is-networking/", "course": "https://www.cloudflare.com/learning/network-layer/what-is-networking/"},
    "cloudformation": {"docs": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html", "course": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html"},
    "ansible": {"docs": "https://docs.ansible.com/ansible/latest/getting_started/index.html", "course": "https://docs.ansible.com/ansible/latest/getting_started/index.html"},
}

def _youtube_link(skill: str) -> str:
    return f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial+for+beginners"


def _search_link(skill: str) -> str:
    return f"https://www.google.com/search?q=learn+{skill.replace(' ', '+')}+tutorial"


def _resources_for(skill: str) -> dict:
    key = skill.lower().strip()
    curated = RESOURCE_LINKS.get(key, {})

    return {
        "docs": curated.get("docs", _search_link(skill)),
        "course": curated.get("course", _search_link(skill)),
        "youtube": _youtube_link(skill),
    }


def _learning_steps(skill: str) -> list:
    """
    A step-by-step study flowchart for this skill, with depth info
    (what to actually do at each stage, and a rough time estimate).
    """
    return [
        {
            "title": "Learn the basics",
            "detail": f"Read the official docs or a short intro course for {skill}. Focus on core vocabulary and the 'why', not memorizing everything.",
            "duration": "2-4 days"
        },
        {
            "title": "Watch a tutorial",
            "detail": f"Watch one full beginner {skill} tutorial video and actually type the code/steps along with it instead of just watching.",
            "duration": "1-2 days"
        },
        {
            "title": "Practice hands-on",
            "detail": f"Do small, focused exercises in {skill} — a sandbox, katas, or a free-tier account. Aim for daily short sessions over one long one.",
            "duration": "1-2 weeks"
        },
        {
            "title": "Build a mini-project",
            "detail": f"Build one small real project using {skill} end-to-end. This is where it actually sticks — pick something you'll finish in a few days.",
            "duration": "1 week"
        },
        {
            "title": "Showcase the skill",
            "detail": f"Add {skill} to your resume with the specific project you built, and prepare 1-2 talking points for interviews about it.",
            "duration": "1-2 days"
        },
    ]


def recommend_skills(user_skills: list, target_role: str, postings_limit: int = 30, top_n: int = 15) -> dict:

    target_role = (target_role or "").strip()

    if not target_role:
        return {"error": "target_role is required"}

    jobs = search_jobs(target_role, limit=postings_limit)

    if not jobs:
        return {
            "error": f"No job postings found for '{target_role}'. Try a different job title."
        }

    skill_counter = Counter()

    for job in jobs:
        description = job.get("description") or job.get("title") or ""
        job_skills = extract_skills(description)
        skill_counter.update(s.lower().strip() for s in job_skills)

    required = [skill for skill, _count in skill_counter.most_common(top_n)]

    if not required:
        return {
            "error": f"Could not detect required skills for '{target_role}' from current postings."
        }

    user_skills_lower = {s.lower().strip() for s in user_skills}

    matched = [s for s in required if s in user_skills_lower]

    missing = [
        {
            "skill": s,
            "resources": _resources_for(s),
            "steps": _learning_steps(s),
        }
        for s in required
        if s not in user_skills_lower
    ]

    return {
        "role": target_role,
        "based_on_postings": len(jobs),
        "matched_skills": matched,
        "recommended_skills": missing,
        "match_percentage": round(len(matched) / len(required) * 100, 1) if required else 0
    }