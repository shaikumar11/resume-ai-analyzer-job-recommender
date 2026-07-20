-- ResumeIQ Database Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    candidate_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    raw_text TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT,
    description TEXT NOT NULL,
    required_skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    job_id INTEGER,
    job_title TEXT,
    job_company TEXT,
    similarity_score REAL,
    ats_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

-- =====================================================================
-- SaaS upgrade tables (added on top of the original schema above).
-- Nothing above this line was changed — existing data stays intact.
-- =====================================================================

-- One row per user, holding the extra profile info the Profile page
-- needs (avatar, headline, social/portfolio links). 1:1 with users.
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    avatar_path TEXT,
    headline TEXT,
    github_url TEXT,
    linkedin_url TEXT,
    portfolio_url TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- One row per /analyze call (one resume upload = one analysis run).
-- This is what powers the dashboard stats and the Resume History page.
-- "matches" above still stores the per-job detail; this table stores
-- the roll-up numbers for that whole run so we don't have to
-- re-aggregate "matches" every time the dashboard loads.
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resume_id INTEGER NOT NULL,
    search_query TEXT,
    location TEXT,
    jobs_found INTEGER DEFAULT 0,
    avg_ats_score REAL DEFAULT 0,
    best_ats_score REAL DEFAULT 0,
    avg_similarity_score REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

-- Jobs a user explicitly saved ("Apply later"). job_key mirrors the
-- frontend's jobKey() (job_id, or apply_url, or title+company) so a
-- job saved from any source can be looked up/removed consistently.
CREATE TABLE IF NOT EXISTS saved_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_key TEXT NOT NULL,
    job_title TEXT NOT NULL,
    job_company TEXT,
    job_location TEXT,
    apply_url TEXT,
    source TEXT,
    similarity_score REAL,
    ats_score REAL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, job_key)
);

-- Replaces the current localStorage-only like/dislike/hide state with
-- something that persists server-side per user. One row per user+job;
-- reacting again just overwrites the previous reaction for that job.
CREATE TABLE IF NOT EXISTS job_reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_key TEXT NOT NULL,
    reaction TEXT NOT NULL CHECK(reaction IN ('like', 'dislike', 'hide')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, job_key)
);

-- Backing store for the notification bell (e.g. "Your resume scored
-- 82% against 6 new roles").
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT,
    type TEXT DEFAULT 'info',
    link_url TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for the queries the dashboard/history/saved-jobs pages will
-- run often (lookups filtered by user_id, ordered by recency).
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_matches_resume_id ON matches(resume_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_id ON saved_jobs(user_id, saved_at);
CREATE INDEX IF NOT EXISTS idx_job_reactions_user_id ON job_reactions(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id, is_read);