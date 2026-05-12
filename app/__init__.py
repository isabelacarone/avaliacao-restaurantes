"""Pacote principal da aplicação Mesa Certa."""

from flask import Flask, flash, redirect, request, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import RequestEntityTooLarge

from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(test_config: dict | None = None) -> Flask:
    """Cria e configura a instância da aplicação Flask (Application Factory).

    Args:
        test_config: Dicionário de configurações que sobrescrevem Config antes de
            init_app(). Usado pela suite de testes para injetar banco temporário
            antes que Flask-SQLAlchemy crie a engine em init_app().

    Returns:
        Instância configurada da aplicação Flask.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    from app.auth import auth_bp
    from app.avaliacoes import avaliacoes_bp
    from app.restaurantes import restaurantes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(restaurantes_bp)
    app.register_blueprint(avaliacoes_bp)

    from app.models import user_loader_callback

    login_manager.user_loader(user_loader_callback)

    @app.errorhandler(RequestEntityTooLarge)
    def arquivo_muito_grande(e: RequestEntityTooLarge) -> tuple:
        """Trata upload de arquivo acima do limite de 2 MB.

        Args:
            e: Exceção de entidade muito grande levantada pelo Werkzeug.

        Returns:
            Redirecionamento para a página anterior com mensagem de erro.
        """
        flash("A foto deve ter no máximo 2 MB.", "danger")
        destino = request.referrer or url_for("restaurantes.listar")
        return redirect(destino), 302

    return app
