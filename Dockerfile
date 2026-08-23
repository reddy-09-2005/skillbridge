# ========================================================
# SkillBridge AI - Production Multi-platform Dockerfile
# ========================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    SERVE_FRONTEND=true

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Pre-download spaCy NLP model to avoid cold-start download in container
RUN python -m spacy download en_core_web_sm

# Copy frontend and backend source code
COPY frontend /app/frontend
COPY backend /app/backend
COPY schema.sql /app/schema.sql

WORKDIR /app/backend

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p uploads && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Start gunicorn with production workers and threads
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120 'app:create_app()'"]
