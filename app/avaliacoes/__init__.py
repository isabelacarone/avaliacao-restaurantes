"""Blueprint de avaliações da aplicação Mesa Certa."""

from flask import Blueprint

avaliacoes_bp = Blueprint("avaliacoes", __name__)

from app.avaliacoes import routes  # noqa: E402, F401
