# SkillBridge AI — Cloud Deployment Guide

This guide walks you through deploying **SkillBridge AI** (Python Flask + NLP/AI Engine + MySQL + Modern Frontend) to live cloud hosting platforms.

---

## Architecture Overview

SkillBridge AI can be deployed in two modes:

```
┌─────────────────────────────────────────────────────────────┐
│ Option A: Unified Full-Stack (Easiest - Single Container)   │
│                                                             │
│  Browser ──► [ Flask Web Service (Port 5000) ]              │
│               ├── / (Frontend HTML/CSS/JS)                  │
│               ├── /api/* (REST API & NLP Matcher)           │
│               └── ──► [ MySQL Database ]                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Option B: Decoupled Multi-Host (CDN Edge Frontend)          │
│                                                             │
│  Browser ──► [ Vercel / Netlify (Static CDN Frontend) ]     │
│       │                                                     │
│       └────► [ Render / Railway Flask Backend API ]         │
│                      └── ──► [ Cloud MySQL Database ]       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Option 1: Render.com (Recommended Free / Low-Cost)

### Step 1: Push Code to GitHub
Ensure your code is pushed to a private or public GitHub repository.

### Step 2: Set up a Free MySQL Database
You can use a free MySQL database from:
- [Aiven.io](https://aiven.io/mysql) (Free 5GB MySQL)
- [Railway.app](https://railway.app) (Free tier MySQL)
- [Clever Cloud](https://www.clever-cloud.com/) (Free MySQL addon)

Import `schema.sql` into your database or let the application automatically initialize the tables on first startup.

### Step 3: Deploy Web Service on Render
1. Log in to [Render.com Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Fill in the settings:
   - **Name**: `skillbridge-ai`
   - **Environment**: `Python 3`
   - **Region**: Closest to your users (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**:
     ```bash
     cd backend && gunicorn --workers 2 --threads 4 --timeout 120 "app:create_app()"
     ```

5. Under **Environment Variables**, add:
   | Key | Value / Example |
   |---|---|
   | `PYTHON_VERSION` | `3.11.9` |
   | `SERVE_FRONTEND` | `true` |
   | `CORS_ORIGINS` | `*` |
   | `SECRET_KEY` | `(Generate random secret)` |
   | `JWT_SECRET_KEY` | `(Generate random secret)` |
   | `MYSQL_HOST` | `your-mysql-host.com` |
   | `MYSQL_PORT` | `3306` |
   | `MYSQL_USER` | `your-db-user` |
   | `MYSQL_PASSWORD` | `your-db-password` |
   | `MYSQL_DATABASE` | `skillbridge` |

6. Click **Deploy Web Service**. Render will build the service, pre-download the spaCy NLP model, and launch the application.

---

## ⚡ Option 2: Railway.app (1-Click with Built-in MySQL)

Railway allows deploying both Flask and MySQL together in the same project:

1. Log in to [Railway.app](https://railway.app/).
2. Click **New Project** -> **Provision MySQL**.
3. Click **New** -> **GitHub Repo** -> select your `skillbridge` repository.
4. In the Web Service settings:
   - Railway will automatically detect the `Dockerfile` in the root!
   - In **Variables**, add a reference to the MySQL database:
     ```
     DATABASE_URL = ${{MySQL.DATABASE_URL}}
     ```
5. Click **Deploy**. Railway will launch MySQL, build the Docker container, and serve your app.

---

## 🌐 Option 3: Vercel (Frontend) + Render/Railway (Backend API)

If you prefer hosting the frontend on Vercel's global edge network:

### Step 1: Deploy Backend
Deploy the backend to Render or Railway as described above. Note down your backend URL (e.g., `https://skillbridge-api.onrender.com`).

### Step 2: Configure Frontend API Base URL
In `frontend/api.js` (or before loading scripts in HTML), specify your backend API URL:
```javascript
window.API_BASE_URL = "https://skillbridge-api.onrender.com/api";
```

### Step 3: Deploy to Vercel
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. Set **Root Directory** to `frontend`.
5. Click **Deploy**.

---

## 🐳 Option 4: Docker & Docker Compose (Self-Hosted / VPS)

Deploy to any Linux VPS (Ubuntu, Debian, AWS EC2, DigitalOcean Droplet, Linode) or run locally with Docker:

```bash
# Clone repository
git clone <your-repo-url>
cd skillbridge

# Launch full stack (MySQL + Flask Backend + Static Frontend)
docker compose up -d --build
```

- Web App: `http://localhost:5000` (or `http://your-server-ip:5000`)
- Health check: `http://localhost:5000/health`
- Check logs: `docker compose logs -f web`

---

## 🛠️ Testing Deployment Locally Before Push

You can test the production Gunicorn server locally on Windows / Linux:

```powershell
cd "C:\Users\vishw\OneDrive\Desktop\skillbridge\backend"

# Activate venv
.\venv\Scripts\activate

# Run with python app.py
python app.py
```
Open `http://localhost:5000` to verify the frontend and API work seamlessly together.

---

## 🔒 Security Best Practices for Production

1. **Environment Variables**: Never commit real database passwords or JWT secret keys to GitHub. Always use cloud environment variables.
2. **CORS**: Set `CORS_ORIGINS` to your production domain (e.g., `https://skillbridge.vercel.app`) if hosting frontend and backend on separate domains.
3. **SSL/HTTPS**: Render, Railway, and Vercel automatically provision free TLS/SSL certificates for all custom domains.
