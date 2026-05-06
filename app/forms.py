"""Formulários WTForms da aplicação Mesa Certa."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    EmailField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length

CATEGORIAS: list[tuple[str, str]] = [
    ("brasileira", "Brasileira"),
    ("italiana", "Italiana"),
    ("japonesa", "Japonesa"),
    ("mexicana", "Mexicana"),
    ("americana", "Americana"),
    ("francesa", "Francesa"),
    ("árabe", "Árabe"),
    ("vegana", "Vegana"),
    ("frutos_do_mar", "Frutos do Mar"),
    ("outra", "Outra"),
]

FAIXAS_PRECO: list[tuple[str, str]] = [
    ("economico", "Econômico (até R$30)"),
    ("moderado", "Moderado (R$30 a R$80)"),
    ("sofisticado", "Sofisticado (acima de R$80)"),
]

NOTAS: list[tuple[str, str]] = [
    ("1", "1 — Péssimo"),
    ("2", "2 — Ruim"),
    ("3", "3 — Regular"),
    ("4", "4 — Bom"),
    ("5", "5 — Excelente"),
]

EXTENSOES_PERMITIDAS: list[str] = ["png", "jpg", "jpeg", "gif"]


class LoginForm(FlaskForm):
    """Formulário de autenticação do usuário."""

    email = EmailField(
        "E-mail",
        validators=[
            DataRequired(message="O e-mail é obrigatório."),
            Email(message="Informe um e-mail válido."),
        ],
    )
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(message="A senha é obrigatória.")],
    )


class CadastroForm(FlaskForm):
    """Formulário de cadastro de novo usuário."""

    nome = StringField(
        "Nome completo",
        validators=[
            DataRequired(message="O nome é obrigatório."),
            Length(min=3, max=120, message="O nome deve ter entre 3 e 120 caracteres."),
        ],
    )
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired(message="O e-mail é obrigatório."),
            Email(message="Informe um e-mail válido."),
        ],
    )
    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired(message="A senha é obrigatória."),
            Length(min=6, message="A senha deve ter no mínimo 6 caracteres."),
        ],
    )
    confirmar_senha = PasswordField(
        "Confirmar senha",
        validators=[
            DataRequired(message="A confirmação de senha é obrigatória."),
            EqualTo("senha", message="As senhas não coincidem."),
        ],
    )


class RestauranteForm(FlaskForm):
    """Formulário de cadastro de restaurante."""

    nome = StringField(
        "Nome do restaurante",
        validators=[
            DataRequired(message="O nome é obrigatório."),
            Length(max=120, message="O nome deve ter no máximo 120 caracteres."),
        ],
    )
    categoria = SelectField(
        "Categoria",
        choices=CATEGORIAS,
        validators=[DataRequired(message="Selecione uma categoria.")],
    )
    faixa_preco = SelectField(
        "Faixa de preço",
        choices=FAIXAS_PRECO,
        validators=[DataRequired(message="Selecione a faixa de preço.")],
    )
    endereco = StringField(
        "Endereço",
        validators=[
            DataRequired(message="O endereço é obrigatório."),
            Length(max=200, message="O endereço deve ter no máximo 200 caracteres."),
        ],
    )
    descricao = TextAreaField(
        "Descrição",
        validators=[
            Length(max=500, message="A descrição deve ter no máximo 500 caracteres.")
        ],
    )


class AvaliacaoForm(FlaskForm):
    """Formulário de avaliação de restaurante."""

    nota_atendimento = SelectField(
        "Atendimento",
        choices=NOTAS,
        validators=[DataRequired(message="Avalie o atendimento.")],
    )
    nota_ambiente = SelectField(
        "Ambiente",
        choices=NOTAS,
        validators=[DataRequired(message="Avalie o ambiente.")],
    )
    nota_prato = SelectField(
        "Qualidade do prato",
        choices=NOTAS,
        validators=[DataRequired(message="Avalie o prato.")],
    )
    nota_preco = SelectField(
        "Relação preço/qualidade",
        choices=NOTAS,
        validators=[DataRequired(message="Avalie o preço.")],
    )
    comentario = TextAreaField(
        "Comentário",
        validators=[
            Length(max=1000, message="O comentário deve ter no máximo 1000 caracteres.")
        ],
    )
    foto = FileField(
        "Foto do prato (opcional)",
        validators=[
            FileAllowed(EXTENSOES_PERMITIDAS, "Apenas imagens são permitidas.")
        ],
    )
