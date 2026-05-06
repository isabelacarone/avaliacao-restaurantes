"""Modelos de dados da aplicação Mesa Certa."""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Usuario(UserMixin, db.Model):
    """Modelo de usuário da plataforma.

    Attributes:
        id: Identificador único do usuário.
        nome: Nome completo do usuário.
        email: Endereço de e-mail único.
        senha_hash: Hash da senha armazenada com segurança.
        criado_em: Data e hora de criação do cadastro.
        avaliacoes: Relacionamento com as avaliações feitas pelo usuário.
    """

    __tablename__ = "usuario"

    id: int = db.Column(db.Integer, primary_key=True)
    nome: str = db.Column(db.String(120), nullable=False)
    email: str = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash: str = db.Column(db.String(256), nullable=False)
    criado_em: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    avaliacoes = db.relationship(
        "Avaliacao", backref="autor", cascade="all, delete-orphan", lazy="dynamic"
    )

    def set_senha(self, senha: str) -> None:
        """Define a senha do usuário armazenando seu hash.

        Args:
            senha: Senha em texto plano a ser criptografada.
        """
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado.

        Args:
            senha: Senha em texto plano a ser verificada.

        Returns:
            True se a senha estiver correta, False caso contrário.
        """
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self) -> str:
        """Representação textual do usuário."""
        return f"<Usuario {self.nome} ({self.email})>"


class Restaurante(db.Model):
    """Modelo de restaurante cadastrado na plataforma.

    Attributes:
        id: Identificador único do restaurante.
        nome: Nome do restaurante.
        categoria: Categoria culinária (ex.: italiana, japonesa).
        faixa_preco: Faixa de preço (economico, moderado, sofisticado).
        endereco: Endereço completo do estabelecimento.
        descricao: Descrição opcional do restaurante.
        criado_em: Data e hora de criação do cadastro.
        avaliacoes: Relacionamento com as avaliações recebidas.
    """

    __tablename__ = "restaurante"

    id: int = db.Column(db.Integer, primary_key=True)
    nome: str = db.Column(db.String(120), nullable=False)
    categoria: str = db.Column(db.String(80), nullable=False)
    faixa_preco: str = db.Column(db.String(30), nullable=False)
    endereco: str = db.Column(db.String(200), nullable=False)
    descricao: str = db.Column(db.Text, nullable=True)
    criado_em: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    avaliacoes = db.relationship("Avaliacao", backref="restaurante", lazy="dynamic")

    @property
    def media_geral(self) -> float | None:
        """Calcula a média geral do restaurante com base em todas as avaliações.

        Returns:
            Média aritmética das médias calculadas ou None se não houver avaliações.
        """
        notas = [av.media_calculada for av in self.avaliacoes if av.media_calculada]
        if not notas:
            return None
        return round(sum(notas) / len(notas), 1)

    @property
    def total_avaliacoes(self) -> int:
        """Retorna o total de avaliações recebidas pelo restaurante.

        Returns:
            Número inteiro de avaliações cadastradas.
        """
        return self.avaliacoes.count()

    def __repr__(self) -> str:
        """Representação textual do restaurante."""
        return f"<Restaurante {self.nome} ({self.categoria})>"


class Avaliacao(db.Model):
    """Modelo de avaliação de restaurante feita por um usuário.

    Attributes:
        id: Identificador único da avaliação.
        usuario_id: Chave estrangeira do usuário avaliador.
        restaurante_id: Chave estrangeira do restaurante avaliado.
        nota_atendimento: Nota de 1 a 5 para o atendimento.
        nota_ambiente: Nota de 1 a 5 para o ambiente.
        nota_prato: Nota de 1 a 5 para a qualidade do prato.
        nota_preco: Nota de 1 a 5 para a relação custo-benefício.
        media_calculada: Média aritmética dos quatro critérios.
        comentario: Comentário textual opcional.
        foto_path: Caminho relativo da foto enviada pelo usuário.
        criado_em: Data e hora da avaliação.
    """

    __tablename__ = "avaliacao"

    id: int = db.Column(db.Integer, primary_key=True)
    usuario_id: int = db.Column(
        db.Integer, db.ForeignKey("usuario.id"), nullable=False
    )
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
    criado_em: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def calcular_media(self) -> None:
        """Calcula e armazena a média aritmética dos quatro critérios de avaliação."""
        notas = [
            self.nota_atendimento,
            self.nota_ambiente,
            self.nota_prato,
            self.nota_preco,
        ]
        self.media_calculada = round(sum(notas) / len(notas), 2)

    def __repr__(self) -> str:
        """Representação textual da avaliação."""
        return (
            f"<Avaliacao restaurante_id={self.restaurante_id} "
            f"usuario_id={self.usuario_id} media={self.media_calculada}>"
        )


def user_loader_callback(user_id: str) -> Usuario | None:
    """Carrega o usuário pelo ID para o Flask-Login.

    Args:
        user_id: ID do usuário como string.

    Returns:
        Instância de Usuario ou None se não encontrado.
    """
    return db.session.get(Usuario, int(user_id))
