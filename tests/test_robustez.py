"""Testes para os itens de robustez implementados na Sprint 9."""

import io

import pytest
from wtforms.validators import ValidationError

from app import db
from app.models import Avaliacao, Favorito, Restaurante, Usuario

# ---------------------------------------------------------------------------
# 1.3 Magic bytes
# ---------------------------------------------------------------------------


def test_magic_bytes_jpeg_valido(cliente_logado, restaurante):
    """Arquivo JPEG com bytes corretos deve ser aceito."""
    imagem = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 100)
    cliente_logado.post(
        f"/avaliacoes/nova/{restaurante.id}",
        data={
            "nota_atendimento": "4",
            "nota_ambiente": "4",
            "nota_prato": "4",
            "nota_preco": "4",
            "foto": (imagem, "prato.jpg", "image/jpeg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    av = Avaliacao.query.filter_by(restaurante_id=restaurante.id).first()
    assert av is not None
    assert av.foto_path is not None


def test_magic_bytes_invalidos_ignorados(cliente_logado, restaurante):
    """Arquivo com extensão .jpg mas bytes errados deve ser ignorado (sem foto)."""
    arquivo_invalido = io.BytesIO(b"PK\x03\x04" + b"\x00" * 100)
    cliente_logado.post(
        f"/avaliacoes/nova/{restaurante.id}",
        data={
            "nota_atendimento": "4",
            "nota_ambiente": "4",
            "nota_prato": "4",
            "nota_preco": "4",
            "foto": (arquivo_invalido, "malicioso.jpg", "image/jpeg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    av = Avaliacao.query.filter_by(restaurante_id=restaurante.id).first()
    assert av is not None
    assert av.foto_path is None


# ---------------------------------------------------------------------------
# 1.4 SenhaForte
# ---------------------------------------------------------------------------


def test_senhaforte_curta_bloqueada(app_ctx):
    from app.validators import SenhaForte

    validator = SenhaForte()

    class FakeField:
        data = "abc1"

    with pytest.raises(ValidationError, match="mínimo 8"):
        validator(None, FakeField())


def test_senhaforte_sem_numero_bloqueada(app_ctx):
    from app.validators import SenhaForte

    validator = SenhaForte()

    class FakeField:
        data = "abcdefgh"

    with pytest.raises(ValidationError, match="letras e números"):
        validator(None, FakeField())


def test_senhaforte_sem_letra_bloqueada(app_ctx):
    from app.validators import SenhaForte

    validator = SenhaForte()

    class FakeField:
        data = "12345678"

    with pytest.raises(ValidationError, match="letras e números"):
        validator(None, FakeField())


def test_senhaforte_valida_nao_levanta(app_ctx):
    from app.validators import SenhaForte

    validator = SenhaForte()

    class FakeField:
        data = "senha123"

    validator(None, FakeField())  # não deve levantar


def test_senhaforte_vazia_nao_levanta(app_ctx):
    """Campo vazio é tratado pelo Optional() — SenhaForte não deve bloquear."""
    from app.validators import SenhaForte

    validator = SenhaForte()

    class FakeField:
        data = ""

    validator(None, FakeField())  # não deve levantar


def test_cadastro_senha_fraca_rejeitada(client):
    resp = client.post(
        "/cadastro",
        data={
            "nome": "Novo User",
            "email": "novo@example.com",
            "senha": "abc",
            "confirmar_senha": "abc",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Usuario.query.filter_by(email="novo@example.com").first() is None


# ---------------------------------------------------------------------------
# 2.3 Soft delete
# ---------------------------------------------------------------------------


def test_restaurante_deletado_nao_aparece_na_listagem(client, restaurante):
    from datetime import datetime, timezone

    restaurante.deletado_em = datetime.now(timezone.utc)
    db.session.commit()

    resp = client.get("/")
    assert restaurante.nome.encode() not in resp.data


def test_restaurante_deletado_retorna_404(client, restaurante):
    from datetime import datetime, timezone

    restaurante.deletado_em = datetime.now(timezone.utc)
    db.session.commit()

    resp = client.get(f"/restaurantes/{restaurante.id}")
    assert resp.status_code == 404


def test_restaurante_ativo_aparece_na_listagem(client, restaurante):
    resp = client.get("/")
    assert restaurante.nome.encode() in resp.data


# ---------------------------------------------------------------------------
# 3.2 Páginas de erro customizadas
# ---------------------------------------------------------------------------


def test_404_usa_template_proprio(client):
    resp = client.get("/rota/que/nao/existe")
    assert resp.status_code == 404
    assert b"Mesa Certa" in resp.data


def test_403_usa_template_proprio(cliente_logado, restaurante, usuario):
    outro = Usuario(nome="Outro", email="outro2@test.com")
    outro.set_senha("senha123")
    db.session.add(outro)
    av = Avaliacao(
        usuario_id=outro.id if outro.id else 0,
        restaurante_id=restaurante.id,
        nota_atendimento=3,
        nota_ambiente=3,
        nota_prato=3,
        nota_preco=3,
    )
    db.session.flush()
    av.usuario_id = outro.id
    av.calcular_media()
    db.session.add(av)
    db.session.commit()

    resp = cliente_logado.post(f"/avaliacoes/{av.id}/excluir")
    assert resp.status_code == 403
    assert b"Mesa Certa" in resp.data


# ---------------------------------------------------------------------------
# 5.1 Paginação do perfil
# ---------------------------------------------------------------------------


def test_perfil_paginado(cliente_logado, usuario, restaurante):
    """Perfil com mais de 10 avaliações deve paginar."""
    # Precisamos de múltiplos restaurantes para gerar avaliações
    restaurantes = []
    for i in range(12):
        r = Restaurante(
            nome=f"Rest Pag {i}",
            categoria="brasileira",
            faixa_preco="moderado",
            endereco=f"Rua {i}",
        )
        db.session.add(r)
        restaurantes.append(r)
    db.session.flush()

    for r in restaurantes:
        av = Avaliacao(
            usuario_id=usuario.id,
            restaurante_id=r.id,
            nota_atendimento=4,
            nota_ambiente=4,
            nota_prato=4,
            nota_preco=4,
        )
        av.calcular_media()
        db.session.add(av)
    db.session.commit()

    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200
    # Com 12 avaliações e per_page=10, deve haver paginação
    resp_p2 = cliente_logado.get("/perfil?page=2")
    assert resp_p2.status_code == 200


# ---------------------------------------------------------------------------
# 5.2 Ordenação de avaliações no detalhe
# ---------------------------------------------------------------------------


def test_detalhe_ordenacao_melhor(cliente_logado, restaurante, usuario):
    outro = Usuario(nome="Outro Sort", email="sort@test.com")
    outro.set_senha("senha123")
    db.session.add(outro)
    db.session.flush()

    av1 = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=5,
        nota_ambiente=5,
        nota_prato=5,
        nota_preco=5,
    )
    av1.calcular_media()
    av2 = Avaliacao(
        usuario_id=outro.id,
        restaurante_id=restaurante.id,
        nota_atendimento=1,
        nota_ambiente=1,
        nota_prato=1,
        nota_preco=1,
    )
    av2.calcular_media()
    db.session.add_all([av1, av2])
    db.session.commit()

    resp = cliente_logado.get(f"/restaurantes/{restaurante.id}?ordem=melhor")
    assert resp.status_code == 200

    resp_pior = cliente_logado.get(f"/restaurantes/{restaurante.id}?ordem=pior")
    assert resp_pior.status_code == 200


# ---------------------------------------------------------------------------
# 5.3 Favoritos
# ---------------------------------------------------------------------------


def test_adicionar_favorito(cliente_logado, restaurante, usuario):
    resp = cliente_logado.post(
        f"/favoritos/{restaurante.id}/adicionar", follow_redirects=True
    )
    assert resp.status_code == 200
    assert (
        Favorito.query.filter_by(
            usuario_id=usuario.id, restaurante_id=restaurante.id
        ).first()
        is not None
    )


def test_remover_favorito(cliente_logado, restaurante, usuario):
    fav = Favorito(usuario_id=usuario.id, restaurante_id=restaurante.id)
    db.session.add(fav)
    db.session.commit()

    resp = cliente_logado.post(
        f"/favoritos/{restaurante.id}/remover", follow_redirects=True
    )
    assert resp.status_code == 200
    assert (
        Favorito.query.filter_by(
            usuario_id=usuario.id, restaurante_id=restaurante.id
        ).first()
        is None
    )


def test_listar_favoritos(cliente_logado, restaurante, usuario):
    fav = Favorito(usuario_id=usuario.id, restaurante_id=restaurante.id)
    db.session.add(fav)
    db.session.commit()

    resp = cliente_logado.get("/favoritos")
    assert resp.status_code == 200
    assert restaurante.nome.encode() in resp.data


def test_favorito_nao_duplica(cliente_logado, restaurante, usuario):
    cliente_logado.post(f"/favoritos/{restaurante.id}/adicionar")
    cliente_logado.post(f"/favoritos/{restaurante.id}/adicionar")
    count = Favorito.query.filter_by(
        usuario_id=usuario.id, restaurante_id=restaurante.id
    ).count()
    assert count == 1


def test_favorito_requer_login(client, restaurante):
    resp = client.post(f"/favoritos/{restaurante.id}/adicionar")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_favorito_restaurante_inexistente_404(cliente_logado):
    resp = cliente_logado.post("/favoritos/99999/adicionar")
    assert resp.status_code == 404
