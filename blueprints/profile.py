import os
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from utils.db import get_profile, upsert_profile

profile_bp = Blueprint("profile", __name__)


def allowed_avatar(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_AVATAR_EXTENSIONS"]


def avatar_url_for(avatar_filename):
    if not avatar_filename:
        return None
    return url_for("profile.serve_avatar", filename=avatar_filename)


# ---------- Avatar file serving ----------

@profile_bp.route("/uploads/avatars/<path:filename>")
@login_required
def serve_avatar(filename):
    avatar_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
    return send_from_directory(avatar_dir, filename)


# ---------- Profile page ----------

@profile_bp.route("/profile")
@login_required
def profile_page():
    user_profile = get_profile(current_user.id) or {}
    return render_template("profile.html", user=current_user, profile=user_profile,
                            avatar_url=avatar_url_for(user_profile.get("avatar_path")))


# ---------- Profile API ----------

@profile_bp.route("/api/profile", methods=["GET"])
@login_required
def api_get_profile():
    user_profile = get_profile(current_user.id) or {}
    return jsonify({
        "full_name": current_user.full_name,
        "email": current_user.email,
        "avatar_url": avatar_url_for(user_profile.get("avatar_path")),
        "headline": user_profile.get("headline"),
        "github_url": user_profile.get("github_url"),
        "linkedin_url": user_profile.get("linkedin_url"),
        "portfolio_url": user_profile.get("portfolio_url"),
    })


@profile_bp.route("/api/profile", methods=["POST"])
@login_required
def api_update_profile():
    headline = request.form.get("headline")
    github_url = request.form.get("github_url")
    linkedin_url = request.form.get("linkedin_url")
    portfolio_url = request.form.get("portfolio_url")

    avatar_filename = None
    avatar_file = request.files.get("avatar")
    if avatar_file and avatar_file.filename:
        if not allowed_avatar(avatar_file.filename):
            return jsonify({"error": "Avatar must be a PNG, JPG, or WEBP image"}), 400
        avatar_filename = secure_filename(f"user{current_user.id}_{avatar_file.filename}")
        avatar_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_file.save(os.path.join(avatar_dir, avatar_filename))

    upsert_profile(
        current_user.id,
        avatar_path=avatar_filename,
        headline=headline,
        github_url=github_url,
        linkedin_url=linkedin_url,
        portfolio_url=portfolio_url,
    )

    user_profile = get_profile(current_user.id) or {}
    return jsonify({"success": True, "avatar_url": avatar_url_for(user_profile.get("avatar_path"))})
