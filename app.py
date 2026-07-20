import os
import logging

from flask import Flask, request, jsonify

from config import Config
from extensions import login_manager, User
from utils.db import get_user_by_id
from init_db import init_db


@login_manager.user_loader
def load_user(user_id):
    user_dict = get_user_by_id(user_id)
    return User(user_dict) if user_dict else None


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    configure_logging(app)

    # Safe to call on every startup — schema.sql is all "CREATE TABLE IF
    # NOT EXISTS", so this never touches existing data. It just makes sure
    # any new tables (added as the app evolves) exist before routes hit them.
    init_db()

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    register_blueprints(app)
    register_error_handlers(app)

    return app


def configure_logging(app):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app.logger.setLevel(logging.INFO)


def register_blueprints(app):
    from blueprints.auth import auth_bp
    from blueprints.resume import resume_bp
    from blueprints.jobs import jobs_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)


def register_error_handlers(app):
    def wants_json():
        return request.path.startswith("/api/") or \
            request.accept_mimetypes.best == "application/json"

    @app.errorhandler(404)
    def not_found(error):
        if wants_json():
            return jsonify({"error": "Not found"}), 404
        return "Page not found", 404

    @app.errorhandler(413)
    def file_too_large(error):
        if wants_json():
            return jsonify({"error": "File too large. Max size is 10MB."}), 413
        return "File too large. Max size is 10MB.", 413

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Unhandled server error")
        if wants_json():
            return jsonify({"error": "Internal server error"}), 500
        return "Something went wrong on our end.", 500


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
