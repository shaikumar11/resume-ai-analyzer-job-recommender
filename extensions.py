"""
Shared Flask extension instances.

Kept in their own module (rather than inside app.py) so blueprint files
can `from extensions import login_manager, User` without creating a
circular import with the app factory in app.py.
"""

from flask_login import LoginManager, UserMixin

login_manager = LoginManager()


class User(UserMixin):
    """Wraps a row from the `users` table so Flask-Login can work with it."""

    def __init__(self, user_dict):
        self.id = user_dict["id"]
        self.full_name = user_dict["full_name"]
        self.email = user_dict["email"]
