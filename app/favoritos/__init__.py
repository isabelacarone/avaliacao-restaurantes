"""Blueprint de favoritos."""

from flask import Blueprint

favoritos_bp = Blueprint("favoritos", __name__)

from app.favoritos import routes  # noqa: E402, F401
