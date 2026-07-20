<div align="center">

# 🧠 Resume AI Analyzer & Job Recommend System

**Upload a resume. Get scored against live job openings. Instantly.**

AI-powered ATS scoring, keyword gap analysis, and real-time job matching — built with Flask, TF-IDF/NLP, and live job market APIs.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit--learn](https://img.shields.io/badge/scikit--learn-TF--IDF-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-07405E?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#license)

[Features](#-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [API Reference](#-api-reference) • [Project Structure](#-project-structure)

</div>

---

## 📋 Overview

**Resume AI Analyzer & Job Recommend System** parses a candidate's resume (PDF or DOCX), extracts skills and structure, and scores it against **live job postings** pulled in real time from Adzuna and Jooble. Instead of comparing your resume to a static, hand-picked list of "sample jobs," every match is against a role that's actually hiring right now.

Under the hood, matching is powered by **TF-IDF vectorization + cosine similarity** (the same core technique real ATS platforms use) rather than a hardcoded keyword whitelist — so it adapts to whatever domain the resume and job description are actually in.

---

## ✨ Features

### 🔍 Resume Analysis
- Drag-and-drop upload — **PDF & DOCX** supported
- ATS readability score (0–100), weighted from section-completeness + keyword match
- Section detection — contact, skills, experience, education, projects
- Matched vs. missing keywords, per job
- Dynamic keyword extraction (TF-IDF-ranked, not a fixed whitelist)

### 💼 Live Job Matching
- Real-time postings from **Adzuna** and **Jooble**, fetched in parallel and de-duplicated
- Cosine-similarity match score per job, batch-computed for speed
- Location-aware search

### 📊 Dashboard & History
- Total analyses, average ATS score, saved jobs, resumes uploaded — at a glance
- ATS score trend chart over time
- Full resume history with per-job breakdown, delete, and printable report

### ⭐ Saved Jobs
- Bookmark roles to apply to later
- Search your saved list
- One click to the original posting

### 👤 Profile
- Editable headline, avatar, GitHub/LinkedIn/portfolio links

### 🎨 Interface
- Light/dark mode with persistence
- Responsive layout
- Toast notifications, animated stat cards, empty states throughout

### 🔐 Accounts
- Secure signup/login (hashed passwords, Flask-Login sessions)
- Per-user data isolation — every query is scoped to the logged-in user

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Flask 3.1, Flask-Login, Blueprint-based architecture |
| **Matching engine** | scikit-learn (TF-IDF + cosine similarity) |
| **Text processing** | NLTK (tokenizing, lemmatizing, stopword removal) |
| **Resume parsing** | PyPDF2, python-docx |
| **Job data** | Adzuna API, Jooble API (fetched concurrently via `ThreadPoolExecutor`) |
| **Database** | SQLite (raw SQL, no ORM) |
| **Frontend** | HTML5, vanilla JavaScript (Fetch API), Chart.js |
| **Auth** | Werkzeug password hashing, Flask-Login sessions |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Free API keys from [Adzuna](https://developer.adzuna.com/) and/or [Jooble](https://jooble.org/api/about)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/shaikumar11/resume-ai-analyzer-job-recommender.git
cd resume-ai-analyzer-job-recommender

# 2. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Create a .env file in the project root (see .env.example)
```

Create a `.env` file:
```env
SECRET_KEY=replace-with-a-random-secret-key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
JOOBLE_API_KEY=your_jooble_api_key
```

```bash
# 5. Initialize the database
python init_db.py

# 6. Run the app
python app.py
```

Visit **http://127.0.0.1:5000** — sign up, upload a resume, and see it scored against live openings.

---

## 📁 Project Structure

```
resume-ai-analyzer-job-recommender/
├── app.py                   # Application factory, blueprint registration
├── config.py                 # Central config, loads .env
├── extensions.py              # Shared Flask-Login user class
├── init_db.py                 # Creates/migrates the SQLite schema
├── requirements.txt
│
├── blueprints/                # Route handlers, grouped by domain
│   ├── auth.py                  # Signup / login / logout
│   ├── resume.py                # Upload, analyze, history
│   ├── jobs.py                  # Save / unsave / like / dislike jobs
│   ├── dashboard.py              # Stats + notifications API
│   └── profile.py                # Profile view/edit, avatar upload
│
├── models/
│   ├── nlp_matcher.py            # TF-IDF + cosine similarity engine
│   └── ats_scorer.py              # Section detection, ATS scoring
│
├── utils/
│   ├── db.py                     # All SQL queries
│   ├── jobs_api.py                # Adzuna + Jooble fetching, de-dupe
│   ├── resume_parser.py           # PDF/DOCX text extraction
│   ├── preprocess.py              # Cleaning, tokenizing, lemmatizing
│   └── skill_extractor.py         # Dynamic TF-IDF keyword extraction
│
├── database/
│   ├── schema.sql                 # Full table definitions
│   └── seed_jobs.py
│
└── templates/
    ├── index.html                  # Main resume-upload + job-match screen
    ├── dashboard.html
    ├── history.html
    ├── saved_jobs.html
    ├── profile.html
    ├── login.html
    └── signup.html
```

---

## 📡 API Reference

All endpoints below require an authenticated session (`@login_required`) unless noted.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Create an account |
| `POST` | `/login` | Authenticate |
| `GET` | `/logout` | End session |
| `POST` | `/analyze` | Upload + analyze a resume, returns matched jobs |
| `GET` | `/api/history` | List all past analyses for the current user |
| `GET` | `/api/history/<id>` | Detail view of one analysis |
| `DELETE` | `/api/history/<id>` | Delete an analysis |
| `POST` | `/api/jobs/save` | Save a job |
| `DELETE` | `/api/jobs/save/<job_key>` | Remove a saved job |
| `GET` | `/api/jobs/saved` | List saved jobs (supports `?q=` search) |
| `POST` | `/api/jobs/react` | Like / dislike / hide a job |
| `GET` | `/api/dashboard/stats` | Aggregate stats for the dashboard |
| `GET` / `POST` | `/api/profile` | View / update profile |
| `GET` | `/api/notifications` | List notifications |

---

## 🗺 Roadmap

- [ ] Additional job sources — Greenhouse, Lever, RemoteOK, Remotive
- [ ] Server-generated PDF reports (currently uses browser print-to-PDF)
- [ ] Automated notifications (e.g. "Your resume scored X% on a new match")
- [ ] Skill-gap recommendations tied to specific learning resources

---

## 🤝 Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">

Built with Flask, scikit-learn, and a genuine dislike of resumes that vanish into ATS black holes.

</div>
