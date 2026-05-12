"""Validadores customizados WTForms para a aplicação Mesa Certa.

Implementa checagens de unicidade (e-mail, nome de restaurante) que
exigem acesso ao banco de dados e não são cobertas pelos validadores
padrão do WTForms.
"""

from wtforms.validators import ValidationError


class UniqueEmail:
    """Valida que o e-mail não está cadastrado para outro usuário.

    Args:
        exclude_id: ID do usuário a ignorar (uso em edição de perfil).
        message: Mensagem de erro personalizada.
    """

    def __init__(
        self,
        exclude_id: int | None = None,
        message: str = "Este e-mail já está cadastrado.",
    ) -> None:
        self.exclude_id = exclude_id
        self.message = message

    def __call__(self, form, field) -> None:  # noqa: ANN001
        """Executa a validação consultando o banco de dados.

        Args:
            form: Instância do formulário WTForms.
            field: Campo que está sendo validado.

        Raises:
            ValidationError: Se o e-mail já existir para outro usuário.
        """
        from app.models import Usuario

        query = Usuario.query.filter(
            Usuario.email == field.data.strip().lower()
        )
        if self.exclude_id is not None:
            query = query.filter(Usuario.id != self.exclude_id)
        if query.first():
            raise ValidationError(self.message)


class UniqueNomeRestaurante:
    """Valida que o nome do restaurante ainda não foi cadastrado.

    Args:
        exclude_id: ID do restaurante a ignorar (uso em edição futura).
        message: Mensagem de erro personalizada.
    """

    def __init__(
        self,
        exclude_id: int | None = None,
        message: str = "Já existe um restaurante com este nome.",
    ) -> None:
        self.exclude_id = exclude_id
        self.message = message

    def __call__(self, form, field) -> None:  # noqa: ANN001
        """Executa a validação consultando o banco de dados.

        Args:
            form: Instância do formulário WTForms.
            field: Campo que está sendo validado.

        Raises:
            ValidationError: Se o nome já existir para outro restaurante.
        """
        from app.models import Restaurante

        query = Restaurante.query.filter(
            Restaurante.nome.ilike(field.data.strip())
        )
        if self.exclude_id is not None:
            query = query.filter(Restaurante.id != self.exclude_id)
        if query.first():
            raise ValidationError(self.message)
