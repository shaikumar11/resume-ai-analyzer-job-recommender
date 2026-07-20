import os
from flask import Blueprint, request, render_template, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from utils.resume_parser import extract_text
from utils.preprocess import clean_text
from utils.db import (
    insert_resume, insert_match, insert_analysis,
    get_analyses_for_user, get_analysis_by_id, get_matches_for_resume,
    delete_analysis, get_saved_job_keys, get_reactions_for_user,
)
from utils.jobs_api import fetch_live_jobs
from utils.skill_extractor import extract_keywords
from models.nlp_matcher import compute_similarities_batch
from models.ats_scorer import check_sections

resume_bp = Blueprint("resume", __name__)


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_RESUME_EXTENSIONS"]


def guess_search_query(cleaned_resume):
    role_hints = [
        "software developer", "data engineer", "backend developer",
        "machine learning engineer", "full stack developer", "data analyst",
    ]
    for hint in role_hints:
        if all(word in cleaned_resume for word in hint.split()):
            return hint
    if "python" in cleaned_resume:
        return "python developer"
    return "software developer"


# ---------- Main page ----------

@resume_bp.route("/")
@login_required
def index():
    return render_template("index.html", user=current_user)


# ---------- Analyze (same behavior as before, plus an analyses row for history/dashboard) ----------

@resume_bp.route("/analyze", methods=["POST"])
@login_required
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and DOCX files are supported"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    try:
        raw_text = extract_text(file_path)
    except Exception as e:
        current_app.logger.warning("Could not parse resume '%s': %s", filename, e)
        return jsonify({"error": f"Could not read file: {str(e)}"}), 400

    cleaned_resume = clean_text(raw_text)
    candidate_name = filename.rsplit(".", 1)[0].replace("_", " ")
    resume_id = insert_resume(candidate_name, file_path, raw_text, user_id=current_user.id)

    location = request.form.get("location", "").strip() or current_app.config["DEFAULT_LOCATION"]
    search_query = guess_search_query(cleaned_resume)

    try:
        live_jobs = fetch_live_jobs(query=search_query, location=location, results_count=8)
    except Exception as e:
        current_app.logger.error("Live job fetch failed for query='%s': %s", search_query, e)
        return jsonify({"error": f"Could not fetch live jobs: {str(e)}"}), 502

    if not live_jobs:
        # Still record the analysis run (0 jobs found) so history/dashboard stay accurate.
        insert_analysis(
            current_user.id, resume_id, search_query, location,
            jobs_found=0, avg_ats_score=0, best_ats_score=0, avg_similarity_score=0,
        )
        return jsonify({"candidate_name": candidate_name, "search_query": search_query, "jobs": []})

    sections = check_sections(raw_text)
    resume_skill_words = extract_keywords(cleaned_resume, top_n=60)

    # Clean every job description once, then score all of them against the
    # resume in a single batch TF-IDF fit (unchanged from before).
    cleaned_jobs = [clean_text(job["description"]) for job in live_jobs]
    similarities = compute_similarities_batch(cleaned_resume, cleaned_jobs)

    # So the frontend can show "Saved"/"Liked" state immediately on freshly
    # fetched jobs, without a second round-trip.
    saved_keys = get_saved_job_keys(current_user.id)
    reactions = get_reactions_for_user(current_user.id)

    job_results = []
    ats_scores = []
    for job, cleaned_job, similarity in zip(live_jobs, cleaned_jobs, similarities):
        job_skill_words = extract_keywords(cleaned_job, top_n=40)
        matched = sorted(job_skill_words & resume_skill_words)
        missing = sorted(job_skill_words - resume_skill_words)

        keyword_pct = round((len(matched) / len(job_skill_words)) * 100, 2) if job_skill_words else 0
        section_pct = (sum(sections.values()) / len(sections)) * 100
        ats_score = round((section_pct * 0.4) + (keyword_pct * 0.6), 2)
        ats_scores.append(ats_score)

        insert_match(resume_id, 0, similarity, ats_score)

        job_results.append({
            "job_id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "apply_url": job["redirect_url"],
            "contract_time": job.get("contract_time", ""),
            "category": job.get("category", ""),
            "posted": job.get("created", "")[:10] if job.get("created") else "",
            "source": job.get("source", ""),
            "similarity_score": round(similarity * 100, 2),
            "ats_score": ats_score,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "sections": sections,
            "saved": job["id"] in saved_keys,
            "reaction": reactions.get(job["id"]),
        })

    job_results.sort(key=lambda x: x["similarity_score"], reverse=True)

    insert_analysis(
        current_user.id, resume_id, search_query, location,
        jobs_found=len(job_results),
        avg_ats_score=round(sum(ats_scores) / len(ats_scores), 2),
        best_ats_score=max(ats_scores),
        avg_similarity_score=round(sum(similarities) / len(similarities), 4),
    )

    return jsonify({
        "candidate_name": candidate_name,
        "search_query": search_query,
        "jobs": job_results,
    })


# ---------- Resume History ----------

@resume_bp.route("/history")
@login_required
def history_page():
    # NOTE: templates/history.html doesn't exist yet — this route is wired
    # and ready, it'll render once the history.html template lands in the
    # frontend pass. The /api/history endpoints below already work today.
    return render_template("history.html", user=current_user)


@resume_bp.route("/api/history")
@login_required
def api_history():
    return jsonify(get_analyses_for_user(current_user.id))


@resume_bp.route("/api/history/<int:analysis_id>")
@login_required
def api_history_detail(analysis_id):
    analysis = get_analysis_by_id(analysis_id, current_user.id)
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404
    analysis["matches"] = get_matches_for_resume(analysis["resume_id"])
    return jsonify(analysis)


@resume_bp.route("/api/history/<int:analysis_id>", methods=["DELETE"])
@login_required
def api_history_delete(analysis_id):
    deleted = delete_analysis(analysis_id, current_user.id)
    if not deleted:
        return jsonify({"error": "Analysis not found"}), 404
    return jsonify({"success": True})
