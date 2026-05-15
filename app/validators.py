"""Validadores customizados WTForms para a aplicação Mesa Certa."""

import re

from wtforms.validators import ValidationError


class UniqueEmail:
    """Valida que o e-mail não está cadastrado para outro usuário."""

    def __init__(
        self,
        exclude_id: int | None = None,
        message: str = "Este e-mail já está cadastrado.",
    ) -> None:
        self.exclude_id = exclude_id
        self.message = message

    def __call__(self, form, field) -> None:  # noqa: ANN001
        from app.models import Usuario

        query = Usuario.query.filter(Usuario.email == field.data.strip().lower())
        if self.exclude_id is not None:
            query = query.filter(Usuario.id != self.exclude_id)
        if query.first():
            raise ValidationError(self.message)


class UniqueNomeRestaurante:
    """Valida que o nome do restaurante ainda não foi cadastrado."""

    def __init__(
        self,
        exclude_id: int | None = None,
        message: str = "Já existe um restaurante com este nome.",
    ) -> None:
        self.exclude_id = exclude_id
        self.message = message

    def __call__(self, form, field) -> None:  # noqa: ANN001
        from app.models import Restaurante

        query = Restaurante.query.filter(Restaurante.nome.ilike(field.data.strip()))
        if self.exclude_id is not None:
            query = query.filter(Restaurante.id != self.exclude_id)
        if query.first():
            raise ValidationError(self.message)


class SenhaForte:
    """Valida que a senha tem no mínimo 8 caracteres e contém letras e números."""

    def __call__(self, form, field) -> None:  # noqa: ANN001
        v = field.data or ""
        if not v:
            return
        if len(v) < 8:
            raise ValidationError("A senha deve ter no mínimo 8 caracteres.")
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValidationError("A senha deve conter letras e números.")
