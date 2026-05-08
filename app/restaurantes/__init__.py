"""Blueprint de restaurantes da aplicação Mesa Certa."""

from flask import Blueprint

restaurantes_bp = Blueprint("restaurantes", __name__)

from app.restaurantes import routes  # noqa: E402, F401
