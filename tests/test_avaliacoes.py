"""Testes das rotas de avaliações."""

from app import db
from app.models import Avaliacao, Usuario


def _dados_avaliacao() -> dict:
    return {
        "nota_atendimento": "4",
        "nota_ambiente": "4",
        "nota_prato": "5",
        "nota_preco": "3",
        "comentario": "Muito bom!",
    }


def test_nova_avaliacao_requer_login(client, restaurante):
    resp = client.get(
        f"/avaliacoes/nova/{restaurante.id}", follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"login" in resp.data.lower()


def test_nova_avaliacao_cria_registro(cliente_logado, restaurante):
    resp = cliente_logado.post(
        f"/avaliacoes/nova/{restaurante.id}",
        data=_dados_avaliacao(),
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Avaliacao.query.filter_by(restaurante_id=restaurante.id).count() == 1


def test_avaliacao_duplicada_bloqueada(cliente_logado, restaurante, avaliacao):
    resp = cliente_logado.get(
        f"/avaliacoes/nova/{restaurante.id}", follow_redirects=True
    )
    assert resp.status_code == 200
    assert "já avaliou" in resp.data.decode("utf-8")


def test_editar_avaliacao_propria(cliente_logado, restaurante, avaliacao):
    resp = cliente_logado.post(
        f"/avaliacoes/{avaliacao.id}/editar",
        data={**_dados_avaliacao(), "comentario": "Atualizado!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    av = db.session.get(Avaliacao, avaliacao.id)
    assert av.comentario == "Atualizado!"


def test_excluir_avaliacao_propria(cliente_logado, restaurante, avaliacao):
    av_id = avaliacao.id
    resp = cliente_logado.post(
        f"/avaliacoes/{av_id}/excluir", follow_redirects=True
    )
    assert resp.status_code == 200
    assert db.session.get(Avaliacao, av_id) is None


def test_editar_avaliacao_alheia_retorna_403(cliente_logado, restaurante, usuario):
    """Usuário logado não pode editar avaliação de outra pessoa."""
    outro = Usuario(nome="Outro", email="outro@example.com")
    outro.set_senha("senha456")
    db.session.add(outro)
    db.session.flush()
    av = Avaliacao(
        usuario_id=outro.id,
        restaurante_id=restaurante.id,
        nota_atendimento=3,
        nota_ambiente=3,
        nota_prato=3,
        nota_preco=3,
    )
    av.calcular_media()
    db.session.add(av)
    db.session.commit()
    av_id = av.id

    resp = cliente_logado.post(f"/avaliacoes/{av_id}/editar", data=_dados_avaliacao())
    assert resp.status_code == 403


def test_avaliacao_restaurante_inexistente(cliente_logado):
    resp = cliente_logado.get("/avaliacoes/nova/9999")
    assert resp.status_code == 404
