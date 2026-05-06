"""Pacote principal da aplicação Mesa Certa."""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app() -> Flask:
    """Cria e configura a instância da aplicação Flask (Application Factory).

    Returns:
        Instância configurada da aplicação Flask.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
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

    with app.app_context():
        db.create_all()

    return app
