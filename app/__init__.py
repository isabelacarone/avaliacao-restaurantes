"""Pacote principal da aplicação Mesa Certa."""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from werkzeug.exceptions import RequestEntityTooLarge

from app.config import get_config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day"])

_CSP = {
    "default-src": "'self'",
    "style-src": ["'self'", "cdn.jsdelivr.net", "'unsafe-inline'"],
    "script-src": ["'self'", "cdn.jsdelivr.net", "'unsafe-inline'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'", "cdn.jsdelivr.net"],
}


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    if not app.debug and not app.testing:
        Talisman(app, force_https=False, content_security_policy=_CSP)
        _configurar_logging(app)

    from app.auth import auth_bp
    from app.avaliacoes import avaliacoes_bp
    from app.favoritos import favoritos_bp
    from app.restaurantes import restaurantes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(restaurantes_bp)
    app.register_blueprint(avaliacoes_bp)
    app.register_blueprint(favoritos_bp)

    from app.models import user_loader_callback

    login_manager.user_loader(user_loader_callback)

    with app.app_context():
        _seed_inicial()

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return {"status": "ok", "db": "connected"}, 200
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}, 500

    @app.errorhandler(RequestEntityTooLarge)
    def arquivo_muito_grande(e: RequestEntityTooLarge) -> tuple:
        app.logger.warning("Upload rejeitado (>2 MB): %s", request.path)
        flash("A foto deve ter no máximo 2 MB.", "danger")
        destino = request.referrer or url_for("restaurantes.listar")
        return redirect(destino), 302

    @app.errorhandler(404)
    def pagina_nao_encontrada(e):
        return render_template("erros/404.html"), 404

    @app.errorhandler(403)
    def acesso_negado(e):
        return render_template("erros/403.html"), 403

    @app.errorhandler(500)
    def erro_interno(e):
        import traceback
        app.logger.error("Erro interno: %s\n%s", e, traceback.format_exc())
        return render_template("erros/500.html"), 500

    return app


def _seed_inicial() -> None:
    """Popula o banco com dados iniciais se estiver vazio."""
    from app.models import Restaurante
    try:
        if Restaurante.query.first() is not None:
            return
        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location(
            "seed", pathlib.Path(__file__).parent.parent / "seed.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.seed()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Seed ignorado: %s", exc)


def _configurar_logging(app: Flask) -> None:
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler(
        "logs/mesa_certa.log", maxBytes=1_000_000, backupCount=3
    )
    handler.setLevel(logging.WARNING)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
