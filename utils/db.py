import sqlite3
import os

DB_PATH = os.path.join("database", "resume_screening.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def get_all_jobs():
    conn = get_connection()
    jobs = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()
    return [dict(job) for job in jobs]


def insert_resume(candidate_name, file_path, raw_text, user_id=None):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO resumes (candidate_name, file_path, raw_text, user_id) VALUES (?, ?, ?, ?)",
        (candidate_name, file_path, raw_text, user_id)
    )
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    return resume_id


def insert_match(resume_id, job_id, similarity_score, ats_score):
    conn = get_connection()
    conn.execute(
        "INSERT INTO matches (resume_id, job_id, similarity_score, ats_score) VALUES (?, ?, ?, ?)",
        (resume_id, job_id, similarity_score, ats_score)
    )
    conn.commit()
    conn.close()
def create_user(full_name, email, password_hash):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            (full_name, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None  # email already exists
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_resumes_for_user(user_id):
    conn = get_connection()
    resumes = conn.execute(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY upload_date DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in resumes]


# =====================================================================
# SaaS upgrade functions (added on top of the original functions above).
# Nothing above this line was changed.
# =====================================================================

# ---------- Analyses (one row per /analyze run — powers dashboard + history) ----------

def insert_analysis(user_id, resume_id, search_query, location,
                     jobs_found, avg_ats_score, best_ats_score, avg_similarity_score):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO analyses
           (user_id, resume_id, search_query, location, jobs_found,
            avg_ats_score, best_ats_score, avg_similarity_score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, resume_id, search_query, location,
         jobs_found, avg_ats_score, best_ats_score, avg_similarity_score)
    )
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id


def get_analyses_for_user(user_id, limit=None):
    conn = get_connection()
    query = """SELECT analyses.*, resumes.candidate_name, resumes.file_path
               FROM analyses
               JOIN resumes ON resumes.id = analyses.resume_id
               WHERE analyses.user_id = ?
               ORDER BY analyses.created_at DESC"""
    params = [user_id]
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_analysis_by_id(analysis_id, user_id):
    """Fetch one analysis, scoped to user_id so a user can't access another user's report."""
    conn = get_connection()
    row = conn.execute(
        """SELECT analyses.*, resumes.candidate_name, resumes.file_path, resumes.raw_text
           FROM analyses
           JOIN resumes ON resumes.id = analyses.resume_id
           WHERE analyses.id = ? AND analyses.user_id = ?""",
        (analysis_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_matches_for_resume(resume_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM matches WHERE resume_id = ? ORDER BY ats_score DESC", (resume_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_analysis(analysis_id, user_id):
    """Delete an analysis (and its per-job matches), scoped to user_id."""
    conn = get_connection()
    analysis = conn.execute(
        "SELECT resume_id FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id)
    ).fetchone()
    if not analysis:
        conn.close()
        return False
    conn.execute("DELETE FROM matches WHERE resume_id = ?", (analysis["resume_id"],))
    conn.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id))
    conn.commit()
    conn.close()
    return True


def get_dashboard_stats(user_id):
    conn = get_connection()

    total_analyses = conn.execute(
        "SELECT COUNT(*) AS c FROM analyses WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]

    avg_ats_score = conn.execute(
        "SELECT AVG(avg_ats_score) AS a FROM analyses WHERE user_id = ?", (user_id,)
    ).fetchone()["a"] or 0

    saved_jobs_count = conn.execute(
        "SELECT COUNT(*) AS c FROM saved_jobs WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]

    resumes_count = conn.execute(
        "SELECT COUNT(*) AS c FROM resumes WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]

    # last 6 analyses, oldest -> newest, for a trend chart
    trend_rows = conn.execute(
        """SELECT avg_ats_score, created_at FROM analyses
           WHERE user_id = ? ORDER BY created_at DESC LIMIT 6""",
        (user_id,)
    ).fetchall()

    conn.close()

    return {
        "total_analyses": total_analyses,
        "avg_ats_score": round(avg_ats_score, 2),
        "saved_jobs_count": saved_jobs_count,
        "resumes_count": resumes_count,
        "score_trend": [dict(r) for r in reversed(trend_rows)],
    }


# ---------- Saved jobs ("Apply later") ----------

def save_job(user_id, job_key, job_title, job_company, job_location,
             apply_url, source, similarity_score, ats_score):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO saved_jobs
               (user_id, job_key, job_title, job_company, job_location,
                apply_url, source, similarity_score, ats_score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, job_key, job_title, job_company, job_location,
             apply_url, source, similarity_score, ats_score)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # already saved
    finally:
        conn.close()


def unsave_job(user_id, job_key):
    conn = get_connection()
    conn.execute(
        "DELETE FROM saved_jobs WHERE user_id = ? AND job_key = ?", (user_id, job_key)
    )
    conn.commit()
    conn.close()


def get_saved_jobs(user_id, search=None):
    conn = get_connection()
    if search:
        rows = conn.execute(
            """SELECT * FROM saved_jobs
               WHERE user_id = ? AND (job_title LIKE ? OR job_company LIKE ?)
               ORDER BY saved_at DESC""",
            (user_id, f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM saved_jobs WHERE user_id = ? ORDER BY saved_at DESC", (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_saved_job_keys(user_id):
    """Just the keys, for quickly flagging 'already saved' on job cards."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT job_key FROM saved_jobs WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {r["job_key"] for r in rows}


# ---------- Job reactions (like / dislike / hide) ----------

def set_reaction(user_id, job_key, reaction):
    """Upsert — reacting again on the same job overwrites the previous reaction."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO job_reactions (user_id, job_key, reaction)
           VALUES (?, ?, ?)
           ON CONFLICT(user_id, job_key)
           DO UPDATE SET reaction = excluded.reaction, created_at = CURRENT_TIMESTAMP""",
        (user_id, job_key, reaction)
    )
    conn.commit()
    conn.close()


def remove_reaction(user_id, job_key):
    conn = get_connection()
    conn.execute(
        "DELETE FROM job_reactions WHERE user_id = ? AND job_key = ?", (user_id, job_key)
    )
    conn.commit()
    conn.close()


def get_reactions_for_user(user_id):
    """Returns {job_key: 'like'|'dislike'|'hide'} for fast lookups when rendering job cards."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT job_key, reaction FROM job_reactions WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {r["job_key"]: r["reaction"] for r in rows}


# ---------- Profile ----------

def get_profile(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_profile(user_id, avatar_path=None, headline=None,
                    github_url=None, linkedin_url=None, portfolio_url=None):
    """
    Update whichever fields are provided; leave the rest as they were.
    Creates the profile row on first save.
    """
    conn = get_connection()
    existing = conn.execute(
        "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
    ).fetchone()

    if existing:
        fields = {
            "avatar_path": avatar_path if avatar_path is not None else existing["avatar_path"],
            "headline": headline if headline is not None else existing["headline"],
            "github_url": github_url if github_url is not None else existing["github_url"],
            "linkedin_url": linkedin_url if linkedin_url is not None else existing["linkedin_url"],
            "portfolio_url": portfolio_url if portfolio_url is not None else existing["portfolio_url"],
        }
        conn.execute(
            """UPDATE profiles SET avatar_path = ?, headline = ?, github_url = ?,
               linkedin_url = ?, portfolio_url = ?, updated_at = CURRENT_TIMESTAMP
               WHERE user_id = ?""",
            (fields["avatar_path"], fields["headline"], fields["github_url"],
             fields["linkedin_url"], fields["portfolio_url"], user_id)
        )
    else:
        conn.execute(
            """INSERT INTO profiles
               (user_id, avatar_path, headline, github_url, linkedin_url, portfolio_url)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, avatar_path, headline, github_url, linkedin_url, portfolio_url)
        )

    conn.commit()
    conn.close()


# ---------- Notifications ----------

def create_notification(user_id, title, message="", notif_type="info", link_url=None):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO notifications (user_id, title, message, type, link_url)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, title, message, notif_type, link_url)
    )
    conn.commit()
    notification_id = cursor.lastrowid
    conn.close()
    return notification_id


def get_notifications(user_id, unread_only=False, limit=20):
    conn = get_connection()
    query = "SELECT * FROM notifications WHERE user_id = ?"
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC LIMIT ?"
    rows = conn.execute(query, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unread_notification_count(user_id):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,)
    ).fetchone()["c"]
    conn.close()
    return count


def mark_notification_read(notification_id, user_id):
    conn = get_connection()
    conn.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
        (notification_id, user_id)
    )
    conn.commit()
    conn.close()


def mark_all_notifications_read(user_id):
    conn = get_connection()
    conn.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,)
    )
    conn.commit()
    conn.close()