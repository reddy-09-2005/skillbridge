# SkillBridge AI

An AI-powered resume analyzer and job matcher. Upload a resume once, and
SkillBridge AI extracts your skills and matches them against live job
postings — showing which roles fit best and which skills are missing for
the ones that don't yet.

## Features

- **Resume upload & parsing** — supports PDF, DOCX, and TXT resumes
- **Automatic skill extraction** — pulls relevant skills out of resume text
- **AI-matched job recommendations** — ranks job postings by fit against
  your resume, with a match score and skill-gap breakdown per role
- **Resume history** — every upload is saved to your account for later
  reference
- **User accounts** — signup/login with secure password hashing and
  JWT-based sessions

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | MySQL |
| Auth | Flask-JWT-Extended, Werkzeug password hashing |
| NLP / skill extraction | spaCy-based parsing |
| Semantic matching | Sentence-Transformers (PyTorch) |
| Frontend | HTML, CSS, JavaScript (no framework) |

## Project structure

```
skillbridge/
├── backend/
│   ├── app.py           # Flask app entry point
│   ├── auth.py          # signup/login routes
│   ├── api.py            # resume upload, job search, recommendations
│   ├── db.py             # MySQL connection
│   ├── config.py         # app configuration (reads from .env)
│   ├── nlp.py             # skill extraction
│   ├── resume.py          # resume file parsing
│   ├── linkedin.py        # job search integration
│   ├── modules.py         # skill-to-job matching logic
│   └── requirements.txt
└── frontend/
    ├── index.html          # landing page
    ├── login.html / signup.html
    ├── dashboard.html       # main app (upload, jobs, history, profile)
    ├── api.js / app.js      # API calls and shared state
    └── dashboard.js / joblist.js
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js (for serving the frontend)
- MySQL Server

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/` (not committed to git):

```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=skillbridge
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

Create the database and tables in MySQL (see `schema.sql` if present, or
set up `users` and `resumes` tables matching the columns used in
`auth.py` / `api.py`).

Run the backend:

```bash
flask run --port 5000
```

### Frontend

```bash
cd frontend
npx http-server -p 5500 -c-1
```

Then open `http://127.0.0.1:5500/index.html` in your browser.

## Environment variables

`.env` is excluded from git via `.gitignore` — never commit real
credentials. `config.py` reads all sensitive values from environment
variables with `os.getenv(...)`.

## License

Personal / educational project.