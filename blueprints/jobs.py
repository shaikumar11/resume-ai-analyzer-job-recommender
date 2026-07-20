from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

from utils.db import (
    save_job, unsave_job, get_saved_jobs,
    set_reaction, remove_reaction, get_reactions_for_user,
)

jobs_bp = Blueprint("jobs", __name__)


# ---------- Saved Jobs page ----------

@jobs_bp.route("/saved-jobs")
@login_required
def saved_jobs_page():
    # NOTE: templates/saved_jobs.html doesn't exist yet — same situation as
    # /history, route + API are ready now, template lands in the frontend pass.
    return render_template("saved_jobs.html", user=current_user)


# ---------- Saved Jobs API ----------

@jobs_bp.route("/api/jobs/save", methods=["POST"])
@login_required
def api_save_job():
    data = request.get_json(silent=True) or {}
    job_key = data.get("job_id")
    if not job_key:
        return jsonify({"error": "job_id is required"}), 400

    newly_saved = save_job(
        current_user.id, job_key,
        job_title=data.get("title", "Untitled Role"),
        job_company=data.get("company", ""),
        job_location=data.get("location", ""),
        apply_url=data.get("apply_url", "#"),
        source=data.get("source", ""),
        similarity_score=data.get("similarity_score"),
        ats_score=data.get("ats_score"),
    )
    return jsonify({"success": True, "already_saved": not newly_saved})


@jobs_bp.route("/api/jobs/save/<path:job_key>", methods=["DELETE"])
@login_required
def api_unsave_job(job_key):
    unsave_job(current_user.id, job_key)
    return jsonify({"success": True})


@jobs_bp.route("/api/jobs/saved", methods=["GET"])
@login_required
def api_get_saved_jobs():
    search = request.args.get("q", "").strip() or None
    return jsonify(get_saved_jobs(current_user.id, search=search))


# ---------- Reactions API (like / dislike / hide) ----------

@jobs_bp.route("/api/jobs/react", methods=["POST"])
@login_required
def api_react():
    data = request.get_json(silent=True) or {}
    job_key = data.get("job_id")
    reaction = data.get("reaction")
    if not job_key or reaction not in ("like", "dislike", "hide"):
        return jsonify({"error": "job_id and a valid reaction ('like'/'dislike'/'hide') are required"}), 400
    set_reaction(current_user.id, job_key, reaction)
    return jsonify({"success": True})


@jobs_bp.route("/api/jobs/react/<path:job_key>", methods=["DELETE"])
@login_required
def api_remove_reaction(job_key):
    remove_reaction(current_user.id, job_key)
    return jsonify({"success": True})


@jobs_bp.route("/api/jobs/reactions", methods=["GET"])
@login_required
def api_get_reactions():
    return jsonify(get_reactions_for_user(current_user.id))
