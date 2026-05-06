"""Configurações da aplicação Mesa Certa."""

import os

UPLOAD_FOLDER: str = os.path.join("app", "static", "uploads")
MAX_CONTENT_LENGTH: int = 2 * 1024 * 1024
ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "gif"}


class Config:
    """Configurações base da aplicação.

    Attributes:
        SECRET_KEY: Chave secreta para sessões e CSRF. Deve ser trocada em produção.
        SQLALCHEMY_DATABASE_URI: URI de conexão com o banco de dados SQLite.
        SQLALCHEMY_TRACK_MODIFICATIONS: Desabilita rastreamento de modificações.
        UPLOAD_FOLDER: Caminho para salvar arquivos enviados pelos usuários.
        MAX_CONTENT_LENGTH: Tamanho máximo permitido para upload (2 MB).
        ALLOWED_EXTENSIONS: Extensões de imagem permitidas para upload.
    """

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-troque-em-producao")
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///mesa_certa.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    UPLOAD_FOLDER: str = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH: int = MAX_CONTENT_LENGTH
    ALLOWED_EXTENSIONS: set[str] = ALLOWED_EXTENSIONS
