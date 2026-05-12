"""Testes unitários dos modelos de dados."""

import pytest

from app import db
from app.models import Avaliacao, Restaurante, Usuario


# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------


def test_set_senha_gera_hash(app_ctx):
    u = Usuario(nome="Teste", email="t@t.com")
    u.set_senha("segura123")
    assert u.senha_hash != "segura123"
    assert u.senha_hash is not None


def test_check_senha_correta(app_ctx):
    u = Usuario(nome="Teste", email="t@t.com")
    u.set_senha("segura123")
    assert u.check_senha("segura123") is True


def test_check_senha_errada(app_ctx):
    u = Usuario(nome="Teste", email="t@t.com")
    u.set_senha("segura123")
    assert u.check_senha("outra") is False


def test_usuario_repr(app_ctx):
    u = Usuario(nome="Ana", email="ana@example.com")
    assert "Ana" in repr(u)
    assert "ana@example.com" in repr(u)


# ---------------------------------------------------------------------------
# Restaurante — media_geral e total_avaliacoes
# ---------------------------------------------------------------------------


def test_media_geral_sem_avaliacoes(app_ctx):
    r = Restaurante(
        nome="Sem Avaliação", categoria="italiana", faixa_preco="moderado", endereco="Rua A, 1"
    )
    db.session.add(r)
    db.session.commit()
    assert r.media_geral is None


def test_media_geral_com_uma_avaliacao(app_ctx, usuario, restaurante):
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=4,
        nota_ambiente=4,
        nota_prato=4,
        nota_preco=4,
    )
    av.calcular_media()
    db.session.add(av)
    db.session.commit()
    assert restaurante.media_geral == 4.0


def test_media_geral_com_multiplas_avaliacoes(app_ctx, restaurante):
    outro_usuario = Usuario(nome="Outro", email="outro@example.com")
    outro_usuario.set_senha("senha123")
    db.session.add(outro_usuario)

    u2 = Usuario(nome="Mais um", email="masum@example.com")
    u2.set_senha("senha123")
    db.session.add(u2)
    db.session.flush()

    av1 = Avaliacao(
        usuario_id=outro_usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=5,
        nota_ambiente=5,
        nota_prato=5,
        nota_preco=5,
    )
    av1.calcular_media()

    av2 = Avaliacao(
        usuario_id=u2.id,
        restaurante_id=restaurante.id,
        nota_atendimento=3,
        nota_ambiente=3,
        nota_prato=3,
        nota_preco=3,
    )
    av2.calcular_media()

    db.session.add_all([av1, av2])
    db.session.commit()

    # media_geral = (5.0 + 3.0) / 2
    assert restaurante.media_geral == 4.0


def test_total_avaliacoes_zero(app_ctx, restaurante):
    assert restaurante.total_avaliacoes == 0


def test_total_avaliacoes_incrementa(app_ctx, usuario, restaurante):
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=3,
        nota_ambiente=3,
        nota_prato=3,
        nota_preco=3,
    )
    av.calcular_media()
    db.session.add(av)
    db.session.commit()
    assert restaurante.total_avaliacoes == 1


def test_restaurante_repr(app_ctx):
    r = Restaurante(
        nome="Cantina Bela",
        categoria="italiana",
        faixa_preco="moderado",
        endereco="Rua B, 2",
    )
    assert "Cantina Bela" in repr(r)
    assert "italiana" in repr(r)


# ---------------------------------------------------------------------------
# Avaliacao — calcular_media
# ---------------------------------------------------------------------------


def test_calcular_media_valores_iguais(app_ctx, usuario, restaurante):
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=4,
        nota_ambiente=4,
        nota_prato=4,
        nota_preco=4,
    )
    av.calcular_media()
    assert av.media_calculada == 4.0


def test_calcular_media_valores_mistos(app_ctx, usuario, restaurante):
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=5,
        nota_ambiente=3,
        nota_prato=4,
        nota_preco=4,
    )
    av.calcular_media()
    assert av.media_calculada == 4.0


def test_calcular_media_notas_extremas(app_ctx, usuario, restaurante):
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=1,
        nota_ambiente=1,
        nota_prato=5,
        nota_preco=5,
    )
    av.calcular_media()
    assert av.media_calculada == 3.0


def test_avaliacao_repr(app_ctx, usuario, restaurante):
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=4,
        nota_ambiente=4,
        nota_prato=4,
        nota_preco=4,
    )
    av.calcular_media()
    r = repr(av)
    assert "restaurante_id" in r
    assert "media" in r


# ---------------------------------------------------------------------------
# Integridade referencial
# ---------------------------------------------------------------------------


def test_cascade_delete_usuario_remove_avaliacoes(app_ctx, usuario, restaurante):
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=5,
        nota_ambiente=5,
        nota_prato=5,
        nota_preco=5,
    )
    av.calcular_media()
    db.session.add(av)
    db.session.commit()
    av_id = av.id

    db.session.delete(usuario)
    db.session.commit()

    assert db.session.get(Avaliacao, av_id) is None


def test_criado_em_preenchido_automaticamente(app_ctx):
    u = Usuario(nome="Auto Data", email="auto@example.com")
    u.set_senha("senha123")
    db.session.add(u)
    db.session.commit()
    assert u.criado_em is not None


# ---------------------------------------------------------------------------
# Validators — branch exclude_id
# ---------------------------------------------------------------------------


def test_unique_email_permite_proprio_email_com_exclude_id(app_ctx, usuario):
    """UniqueEmail com exclude_id deve permitir o e-mail do próprio usuário."""
    from app.validators import UniqueEmail

    validator = UniqueEmail(exclude_id=usuario.id)

    class FakeField:
        data = "test@example.com"

    validator(None, FakeField())  # deve passar sem levantar ValidationError


def test_unique_email_bloqueia_email_de_outro_usuario(app_ctx, usuario):
    """UniqueEmail com exclude_id de outro usuário deve bloquear e-mail duplicado."""
    import pytest
    from wtforms.validators import ValidationError

    from app.validators import UniqueEmail

    outro = Usuario(nome="Outro", email="outro@val.com")
    outro.set_senha("senha123")
    db.session.add(outro)
    db.session.commit()

    validator = UniqueEmail(exclude_id=outro.id)

    class FakeField:
        data = "test@example.com"

    with pytest.raises(ValidationError):
        validator(None, FakeField())


def test_unique_nome_restaurante_permite_proprio_nome_com_exclude_id(app_ctx, restaurante):
    """UniqueNomeRestaurante com exclude_id deve permitir o nome do próprio restaurante."""
    from app.validators import UniqueNomeRestaurante

    validator = UniqueNomeRestaurante(exclude_id=restaurante.id)

    class FakeField:
        data = "Restaurante Teste"

    validator(None, FakeField())  # deve passar sem levantar ValidationError


def test_unique_nome_restaurante_bloqueia_nome_de_outro(app_ctx, restaurante):
    """UniqueNomeRestaurante com exclude_id de outro deve bloquear nome duplicado."""
    import pytest
    from wtforms.validators import ValidationError

    from app.validators import UniqueNomeRestaurante

    outro = Restaurante(
        nome="Outro Restaurante",
        categoria="italiana",
        faixa_preco="moderado",
        endereco="Rua X, 1",
    )
    db.session.add(outro)
    db.session.commit()

    validator = UniqueNomeRestaurante(exclude_id=outro.id)

    class FakeField:
        data = "Restaurante Teste"

    with pytest.raises(ValidationError):
        validator(None, FakeField())
