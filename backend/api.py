"""
api.py
Flask blueprint exposing SkillBridge AI's REST endpoints.
"""

import os
import uuid

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from db import conn, cursor

from resume import allowed_file, extract_text
from nlp import extract_skills
from linkedin import search_jobs
from modules import match_skills_to_jobs


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


# =========================================================
# UPLOAD RESUME
# =========================================================

@api_bp.route("/upload-resume", methods=["POST"])
@jwt_required()
def upload_resume():

    user_email = get_jwt_identity()

    if "resume" not in request.files:
        return jsonify({
            "error": "No file part named 'resume'"
        }), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    if not allowed_file(
        file.filename,
        current_app.config["ALLOWED_EXTENSIONS"]
    ):
        return jsonify({
            "error": "Unsupported file type"
        }), 400

    os.makedirs(
        current_app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    filename = (
        f"{uuid.uuid4().hex}_"
        f"{secure_filename(file.filename)}"
    )

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    try:

        text = extract_text(filepath)

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        if os.path.exists(filepath):
            os.remove(filepath)

    # Extract skills from resume
    skills = extract_skills(text)

    # =====================================================
    # SAVE RESUME TO MYSQL
    # =====================================================

    cursor.execute(
        """
        INSERT INTO resumes
        (user_email, resume_text, skills)
        VALUES (%s, %s, %s)
        """,
        (
            user_email,
            text,
            ",".join(skills)
        )
    )

    conn.commit()

    return jsonify({
        "resume_text": text,
        "skills": skills
    }), 200


# =========================================================
# RESUME HISTORY
# =========================================================

@api_bp.route("/resumes", methods=["GET"])
@jwt_required()
def get_resumes():

    user_email = get_jwt_identity()

    cursor.execute(
        """
        SELECT
            id,
            resume_text,
            skills,
            created_at
        FROM resumes
        WHERE user_email = %s
        ORDER BY id DESC
        """,
        (user_email,)
    )

    rows = cursor.fetchall()

    resumes = []

    for row in rows:

        resumes.append({
            "id": row["id"],
            "resume_text": row["resume_text"],
            "skills": (
                row["skills"].split(",")
                if row["skills"]
                else []
            ),
            "created_at": str(row["created_at"])
        })

    return jsonify({
        "resumes": resumes,
        "count": len(resumes)
    }), 200


# =========================================================
# JOB SEARCH
# =========================================================

@api_bp.route("/jobs/search", methods=["GET"])
def jobs_search():

    keywords = request.args.get(
        "keywords",
        ""
    )

    location = request.args.get(
        "location"
    )

    limit = int(
        request.args.get(
            "limit",
            25
        )
    )

    if not keywords:

        return jsonify({
            "error": "keywords query param is required"
        }), 400

    jobs = search_jobs(
        keywords,
        location=location,
        limit=limit
    )

    return jsonify({
        "jobs": jobs,
        "count": len(jobs)
    }), 200


# =========================================================
# JOB RECOMMENDATIONS
# =========================================================

@api_bp.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json(
        silent=True
    ) or {}

    resume_text = data.get(
        "resume_text",
        ""
    )

    keywords = data.get(
        "keywords",
        ""
    )

    location = data.get(
        "location"
    )

    top_n = int(
        data.get(
            "top_n",
            10
        )
    )

    if not resume_text:

        return jsonify({
            "error": "resume_text is required"
        }), 400

    # If keywords were not entered,
    # extract skills from resume
    if not keywords:

        extracted_skills = extract_skills(
            resume_text
        )

        keywords = (
            " ".join(
                extracted_skills[:5]
            )
            or "software engineer"
        )

    # Search jobs
    jobs = search_jobs(
        keywords,
        location=location,
        limit=max(
            top_n * 3,
            25
        )
    )

    # Match resume against jobs
    result = match_skills_to_jobs(
        resume_text,
        jobs,
        top_n=top_n
    )

    return jsonify(result), 200

    # ==============================
# ALL USERS + ALL RESUMES
# ==============================

@api_bp.route("/admin/all-data", methods=["GET"])
@jwt_required()
def get_all_data():

    # Get all registered users
    cursor.execute(
        """
        SELECT id, email, created_at
        FROM users
        ORDER BY id DESC
        """
    )

    users = cursor.fetchall()

    # Get all uploaded resumes
    cursor.execute(
        """
        SELECT id, user_email, resume_text, skills, created_at
        FROM resumes
        ORDER BY id DESC
        """
    )

    resumes = cursor.fetchall()

    return jsonify({
        "total_members": len(users),
        "total_resumes": len(resumes),

        "users": [
            {
                "id": row["id"],
                "email": row["email"],
                "created_at": str(row["created_at"])
            }
            for row in users
        ],

        "resumes": [
            {
                "id": row["id"],
                "user_email": row["user_email"],
                "resume_text": row["resume_text"],
                "skills": row["skills"].split(",") if row["skills"] else [],
                "created_at": str(row["created_at"])
            }
            for row in resumes
        ]
    }), 200