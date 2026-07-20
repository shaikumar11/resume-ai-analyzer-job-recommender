import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Central app configuration. Values come from environment variables
    (see .env) where present, with safe local-dev fallbacks.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this-later")

    # Same upload folder/size limit as the original app.py.
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    ALLOWED_RESUME_EXTENSIONS = {"pdf", "docx"}
    ALLOWED_AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Read here too (in addition to utils/jobs_api.py's own os.getenv calls)
    # so app.py can fail fast / log a warning if nothing is configured.
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
    JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")

    DEFAULT_LOCATION = "India"
