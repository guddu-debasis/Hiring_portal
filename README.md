# 🧠 NeuralNexus — AI Hiring Automation System

A full-stack AI-powered hiring platform that automates resume screening, candidate scoring, and recruiter workflows — built with FastAPI, React, and Groq (Llama 3.3).

---

## Problem It Solves

Manually reviewing resumes is slow, inconsistent, and biased. NeuralNexus automates the end-to-end hiring pipeline — from job posting to AI-ranked candidate shortlisting — so recruiters spend time deciding, not filtering.

---

## How It Solves It

- **Candidates** sign up, browse open roles, and submit their PDF resume.
- **AI engine** (Llama 3.3 via Groq) extracts text from the PDF and scores the candidate against job requirements (0–100%).
- **Resumes** are stored permanently on Cloudinary; no local disk dependency.
- **Recruiters** view a ranked shortlist for each job and can one-click **Hire** or **Pass** each candidate.
- **Status tracking** lets candidates check their application outcome by email.

---

## Features

### For Candidates
- Register and login with role `candidate`
- Browse all open job listings
- Apply by submitting name, email, and a PDF resume
- Track application status (Pending / Selected / Rejected) by email

### For Recruiters
- Register and login with role `recruiter`
- Post new job vacancies (title, description, requirements)
- View AI-ranked shortlist for each job
- Inline PDF resume viewer (Google Docs viewer embed)
- One-click **Hire** or **Pass** to update candidate status
- Delete a job and cascade-remove all its applications

### AI Pipeline
- PDF text extraction using **PyMuPDF (fitz)**
- Match scoring via **Llama 3.3-70b** (Groq API)
- Score evaluated on skill alignment, experience level, and project relevance
- Score bounded to 0–100 with deterministic `temperature=0`

### Frontend (React)
- Modern glassmorphism UI with dark/light theme toggle
- Built with React 19, React Router 7, Vite 8, and Lucide icons
- Auth state persisted in `localStorage`
- Deployed frontend points to live Render API

### Frontend (Streamlit — alternate UI)
- Full feature parity with the React frontend
- Dark/white theme toggle
- Accessible via `streamlit run streamlit_app.py`

---

## Project Structure

```
Candidate Shortlist/
├── app/
│   ├── main.py                    # FastAPI app, CORS, static files, router
│   ├── api/
│   │   └── v1/
│   │       └── endpoints.py       # All API routes (auth, jobs, candidates)
│   ├── models/
│   │   └── candidate.py           # SQLAlchemy: JobPost, Candidate, User
│   ├── schemas/
│   │   └── candidate.py           # Pydantic: JobCreate, JobResponse, CandidateResponse
│   ├── services/
│   │   └── ai_service.py          # PDF text extraction + Groq AI scoring
│   └── core/
│       ├── config.py              # Settings from .env (local + cloud-aware)
│       ├── database.py            # SQLAlchemy engine, session, SSL for TiDB
│       └── security.py            # bcrypt hashing, JWT creation/verify
├── frontend/                      # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx                # Main app: Auth, Recruiter, Candidate views
│   │   ├── App.css                # Glassmorphism styles
│   │   └── main.jsx               # React entry point
│   ├── package.json
│   └── vite.config.js
├── streamlit_app.py               # Alternate Streamlit UI
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (never commit)
├── .gitignore
└── .github/
    └── workflows/
        └── keep_alive.yml         # GitHub Action to keep Render service warm
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI |
| Database | MySQL / TiDB Cloud (via SQLAlchemy ORM) |
| AI Model | Llama 3.3-70b-versatile (Groq API) |
| PDF Parsing | PyMuPDF (fitz) |
| File Storage | Cloudinary (raw PDF upload) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Frontend | React 19, React Router 7, Vite 8 |
| Alternate UI | Streamlit |
| Server | Uvicorn |
| Deployment | Render (backend), Cloudinary (storage) |

---

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+ (local) **or** a TiDB Cloud / Aiven cluster

### 2. Create the Database (local MySQL)
```sql
CREATE DATABASE hiring_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Clone & Install Python Dependencies
```bash
git clone <your-repo-url>
cd "Candidate Shortlist"
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure `.env`

```env
# Local MySQL (used if DATABASE_URL is not set)
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=hiring_db

# Cloud DB (overrides all MYSQL_* vars if set)
DATABASE_URL=mysql+pymysql://user:pass@host:port/dbname

# JWT
SECRET_KEY=replace_with_a_long_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI
GROQ_API_KEY=your_groq_api_key

# Cloudinary (for resume storage)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

> **Security:** Never commit your `.env` file. It is already listed in `.gitignore`.

### 5. Run the Backend
```bash
python -m uvicorn app.main:app --reload
```

Tables are auto-created on startup via `Base.metadata.create_all()`.

Open the interactive API docs at:
```
http://localhost:8000/docs      ← Swagger UI
http://localhost:8000/redoc     ← ReDoc
```

### 6a. Run the React Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:5173`.

> The API base URL is currently hardcoded to the live Render deployment in `frontend/src/App.jsx`:
> ```javascript
> const API_BASE = 'https://hiring-portal-xl3g.onrender.com/api/v1';
> ```
> Change this to `http://localhost:8000/api/v1` for local backend development.

To build for production:
```bash
npm run build
# Output goes to: frontend/dist/
```

### 6b. Run the Streamlit Frontend (alternate)

```bash
streamlit run streamlit_app.py
```

To point Streamlit at your local backend, add this to `.streamlit/secrets.toml`:
```toml
BASE_URL = "http://localhost:8000/api/v1"
```

---

## API Reference

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/login?username=&password=` | Login — returns JWT token + role |
| POST | `/api/v1/signup?username=&password=&role=` | Register as `candidate` or `recruiter` |

### Jobs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/jobs/` | Create a job posting |
| GET | `/api/v1/jobs/` | List all job postings |
| DELETE | `/api/v1/jobs/{job_id}` | Delete a job (cascades to all applications) |

### Candidates

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/apply/` | Submit application with PDF resume (multipart/form-data) |
| GET | `/api/v1/jobs/{job_id}/shortlist` | Get AI-ranked candidates for a job |
| PUT | `/api/v1/candidates/{id}/status?status=` | Update status: `Selected` or `Rejected` |
| GET | `/api/v1/my-applications/{email}` | Track all applications by candidate email |

---

## Roles

| Role | Capabilities |
|---|---|
| `recruiter` | Post jobs, view AI-ranked shortlist, hire/pass candidates, delete jobs |
| `candidate` | Browse jobs, submit PDF applications, track status by email |

---

## AI Scoring Logic

When a candidate submits a resume:

1. The PDF bytes are uploaded to **Cloudinary** and a permanent URL is stored in the database.
2. **PyMuPDF** extracts raw text from the PDF bytes entirely in-memory (no disk I/O required).
3. The extracted text and the job's `requirements` field are sent to **Groq** (Llama 3.3-70b-versatile) with a structured HR recruiter prompt.
4. The model returns a numeric score (0–100) based on:
   - Skill alignment (technical stack match)
   - Experience level (years and depth)
   - Project relevance
5. The score is clamped to [0, 100] and stored with the candidate record.
6. The shortlist endpoint returns candidates ordered by score descending.

---

## Deployment (Render)

The backend is deployed on [Render](https://render.com). Set these environment variables in the Render dashboard:

```
DATABASE_URL
GROQ_API_KEY
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
SECRET_KEY
```

A GitHub Actions workflow (`.github/workflows/keep_alive.yml`) pings the Render service on a schedule to prevent cold starts on the free tier.
