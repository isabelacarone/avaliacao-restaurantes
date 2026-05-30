"""Configurações da aplicação Mesa Certa."""

import os

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "app", "static", "uploads")
UPLOAD_FOLDER_PERFIL: str = os.path.join(BASE_DIR, "app", "static", "uploads", "perfil")
MAX_CONTENT_LENGTH: int = 2 * 1024 * 1024
ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "gif"}
ALLOWED_EXTENSIONS_PERFIL: set[str] = {"png", "jpg", "jpeg"}


class Config:
    """Configurações base — herdada por todas as outras."""

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    UPLOAD_FOLDER: str = UPLOAD_FOLDER
    UPLOAD_FOLDER_PERFIL: str = UPLOAD_FOLDER_PERFIL
    MAX_CONTENT_LENGTH: int = MAX_CONTENT_LENGTH
    ALLOWED_EXTENSIONS: set[str] = ALLOWED_EXTENSIONS
    ALLOWED_EXTENSIONS_PERFIL: set[str] = ALLOWED_EXTENSIONS_PERFIL

    @classmethod
    def init(cls) -> None:
        """Lê variáveis de ambiente em tempo de uso, não de importação."""
        cls.SECRET_KEY = os.environ.get(
            "SECRET_KEY", "dev-secret-key-troque-em-producao"
        )
        cls.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mesa_certa.db")


class DevelopmentConfig(Config):
    DEBUG: bool = True

    @classmethod
    def init(cls) -> None:
        cls.SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insegura")
        cls.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mesa_certa.db")


class TestingConfig(Config):
    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = False
    SECRET_KEY: str = "test-secret"
    RATELIMIT_ENABLED: bool = False

    @classmethod
    def init(cls) -> None:
        cls.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mesa_certa.db")


class ProductionConfig(Config):
    @classmethod
    def init(cls) -> None:
        secret = os.environ.get("SECRET_KEY")
        if not secret:
            raise RuntimeError(
                "SECRET_KEY é obrigatória em produção. "
                "Defina a variável de ambiente antes de iniciar a aplicação."
            )
        cls.SECRET_KEY = secret
        cls.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mesa_certa.db")


_CONFIG_MAP: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config() -> type[Config]:
    """Retorna a classe de configuração baseada em FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development")
    cfg = _CONFIG_MAP.get(env, DevelopmentConfig)
    cfg.init()
    return cfg
