from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import User
from utils.db import create_user, get_user_by_email, get_user_by_id

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or not password:
            return render_template("signup.html", error="All fields are required.")

        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters.")

        password_hash = generate_password_hash(password)
        user_id = create_user(full_name, email, password_hash)

        if user_id is None:
            return render_template("signup.html", error="An account with this email already exists.")

        user_dict = get_user_by_id(user_id)
        login_user(User(user_dict))
        return redirect(url_for("resume.index"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user_dict = get_user_by_email(email)
        if user_dict and check_password_hash(user_dict["password_hash"], password):
            login_user(User(user_dict))
            return redirect(url_for("resume.index"))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
