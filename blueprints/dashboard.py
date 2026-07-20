from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user

from utils.db import (
    get_dashboard_stats, get_analyses_for_user,
    get_notifications, get_unread_notification_count,
    mark_notification_read, mark_all_notifications_read,
)

dashboard_bp = Blueprint("dashboard", __name__)


# ---------- Dashboard page ----------

@dashboard_bp.route("/dashboard")
@login_required
def dashboard_page():
    # NOTE: templates/dashboard.html doesn't exist yet — route + API are
    # ready now, template lands in the frontend pass.
    return render_template("dashboard.html", user=current_user)


@dashboard_bp.route("/api/dashboard/stats")
@login_required
def api_dashboard_stats():
    stats = get_dashboard_stats(current_user.id)
    stats["recent_activity"] = get_analyses_for_user(current_user.id, limit=5)
    return jsonify(stats)


# ---------- Notifications API ----------

@dashboard_bp.route("/api/notifications")
@login_required
def api_notifications():
    unread_only = request.args.get("unread_only") == "true"
    return jsonify({
        "notifications": get_notifications(current_user.id, unread_only=unread_only),
        "unread_count": get_unread_notification_count(current_user.id),
    })


@dashboard_bp.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def api_mark_notification_read(notification_id):
    mark_notification_read(notification_id, current_user.id)
    return jsonify({"success": True})


@dashboard_bp.route("/api/notifications/read-all", methods=["POST"])
@login_required
def api_mark_all_read():
    mark_all_notifications_read(current_user.id)
    return jsonify({"success": True})
