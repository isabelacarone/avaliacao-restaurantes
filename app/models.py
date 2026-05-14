"""Modelos de dados da aplicação Mesa Certa."""

from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id: int = db.Column(db.Integer, primary_key=True)
    nome: str = db.Column(db.String(120), nullable=False)
    email: str = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash: str = db.Column(db.String(256), nullable=False)
    criado_em: datetime = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    avaliacoes = db.relationship(
        "Avaliacao", backref="autor", cascade="all, delete-orphan", lazy="dynamic"
    )
    favoritos = db.relationship(
        "Favorito", backref="usuario", cascade="all, delete-orphan", lazy="dynamic"
    )

    def set_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self) -> str:
        return f"<Usuario {self.nome} ({self.email})>"


class Restaurante(db.Model):
    __tablename__ = "restaurante"

    id: int = db.Column(db.Integer, primary_key=True)
    nome: str = db.Column(db.String(120), nullable=False, index=True)
    categoria: str = db.Column(db.String(80), nullable=False, index=True)
    faixa_preco: str = db.Column(db.String(30), nullable=False, index=True)
    endereco: str = db.Column(db.String(200), nullable=False)
    descricao: str = db.Column(db.Text, nullable=True)
    deletado_em: datetime | None = db.Column(db.DateTime, nullable=True)
    criado_em: datetime = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    avaliacoes = db.relationship("Avaliacao", backref="restaurante", lazy="dynamic")
    favoritado_por = db.relationship("Favorito", backref="restaurante", lazy="dynamic")

    @property
    def media_geral(self) -> float | None:
        notas = [av.media_calculada for av in self.avaliacoes if av.media_calculada]
        if not notas:
            return None
        return round(sum(notas) / len(notas), 1)

    @property
    def total_avaliacoes(self) -> int:
        return self.avaliacoes.count()

    def __repr__(self) -> str:
        return f"<Restaurante {self.nome} ({self.categoria})>"


class Avaliacao(db.Model):
    __tablename__ = "avaliacao"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "restaurante_id", name="uq_avaliacao_usuario_rest"
        ),
        CheckConstraint("nota_atendimento BETWEEN 1 AND 5", name="ck_nota_atendimento"),
        CheckConstraint("nota_ambiente BETWEEN 1 AND 5", name="ck_nota_ambiente"),
        CheckConstraint("nota_prato BETWEEN 1 AND 5", name="ck_nota_prato"),
        CheckConstraint("nota_preco BETWEEN 1 AND 5", name="ck_nota_preco"),
    )

    id: int = db.Column(db.Integer, primary_key=True)
    usuario_id: int = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    restaurante_id: int = db.Column(
        db.Integer, db.ForeignKey("restaurante.id"), nullable=False
    )
    nota_atendimento: int = db.Column(db.Integer, nullable=False)
    nota_ambiente: int = db.Column(db.Integer, nullable=False)
    nota_prato: int = db.Column(db.Integer, nullable=False)
    nota_preco: int = db.Column(db.Integer, nullable=False)
    media_calculada: float = db.Column(db.Float, nullable=True)
    comentario: str = db.Column(db.Text, nullable=True)
    foto_path: str = db.Column(db.String(256), nullable=True)
    criado_em: datetime = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def calcular_media(self) -> None:
        notas = [
            self.nota_atendimento,
            self.nota_ambiente,
            self.nota_prato,
            self.nota_preco,
        ]
        self.media_calculada = round(sum(notas) / len(notas), 2)

    def __repr__(self) -> str:
        return (
            f"<Avaliacao restaurante_id={self.restaurante_id} "
            f"usuario_id={self.usuario_id} media={self.media_calculada}>"
        )


class Favorito(db.Model):
    """Restaurante salvo por um usuário."""

    __tablename__ = "favorito"
    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "restaurante_id", name="uq_favorito_usuario_rest"
        ),
    )

    id: int = db.Column(db.Integer, primary_key=True)
    usuario_id: int = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    restaurante_id: int = db.Column(
        db.Integer, db.ForeignKey("restaurante.id"), nullable=False
    )
    criado_em: datetime = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return (
            f"<Favorito usuario_id={self.usuario_id}"
            f" restaurante_id={self.restaurante_id}>"
        )


def user_loader_callback(user_id: str) -> Usuario | None:
    return db.session.get(Usuario, int(user_id))
