"""
auth.py
Flask blueprint exposing SkillBridge AI's authentication endpoints.
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from db import conn, cursor

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"error": "an account with this email already exists"}), 409

    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
        (email, password_hash),
    )
    conn.commit()

    user_id = cursor.lastrowid
    token = create_access_token(identity=email)
    return jsonify({"token": token, "email": email}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE email = %s", (email,)
    )
    row = cursor.fetchone()

    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "invalid email or password"}), 401

    token = create_access_token(identity=email)
    return jsonify({"token": token, "email": email}), 200