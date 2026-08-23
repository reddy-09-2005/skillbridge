import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "SkillBridgeJWT@2026")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    LINKEDIN_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    JOB_SEARCH_LOCATION_DEFAULT = os.getenv("JOB_SEARCH_LOCATION_DEFAULT", "India")

    # CORS configuration
    _cors_env = os.getenv("CORS_ORIGINS", "*")
    if _cors_env.strip() == "*":
        CORS_ORIGINS = "*"
    else:
        CORS_ORIGINS = [orig.strip() for orig in _cors_env.split(",") if orig.strip()]

    # Database configuration (support DATABASE_URL / MYSQL_URL / MYSQL_PUBLIC_URL or separate params)
    database_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or os.getenv("MYSQL_PUBLIC_URL")
    if database_url:
        parsed = urlparse(database_url)
        MYSQL_HOST = parsed.hostname or "localhost"
        MYSQL_PORT = parsed.port or 3306
        MYSQL_USER = parsed.username or "root"
        MYSQL_PASSWORD = parsed.password or ""
        MYSQL_DATABASE = parsed.path.lstrip("/") or "skillbridge"
    else:
        MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
        MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
        MYSQL_USER = os.getenv("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "skillbridge")

    # Static frontend serving
    SERVE_FRONTEND = os.getenv("SERVE_FRONTEND", "true").lower() in ("true", "1", "yes")
    FRONTEND_DIR = os.getenv(
        "FRONTEND_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    )
