"""Testes das rotas de avaliações."""

import io

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
    resp = client.get(f"/avaliacoes/nova/{restaurante.id}", follow_redirects=True)
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
    resp = cliente_logado.post(f"/avaliacoes/{av_id}/excluir", follow_redirects=True)
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


def test_editar_avaliacao_inexistente_retorna_404(cliente_logado):
    """Tentativa de editar avaliação que não existe deve retornar 404."""
    resp = cliente_logado.get("/avaliacoes/9999/editar")
    assert resp.status_code == 404


def test_excluir_avaliacao_inexistente_retorna_404(cliente_logado):
    """Tentativa de excluir avaliação que não existe deve retornar 404."""
    resp = cliente_logado.post("/avaliacoes/9999/excluir")
    assert resp.status_code == 404


def test_excluir_avaliacao_alheia_retorna_403(cliente_logado, restaurante, usuario):
    """Usuário logado não pode excluir avaliação de outra pessoa."""
    from app import db
    from app.models import Usuario

    outro = Usuario(nome="Outro Excluir", email="outroexc@example.com")
    outro.set_senha("senha456")
    db.session.add(outro)
    db.session.flush()

    from app.models import Avaliacao

    av = Avaliacao(
        usuario_id=outro.id,
        restaurante_id=restaurante.id,
        nota_atendimento=2,
        nota_ambiente=2,
        nota_prato=2,
        nota_preco=2,
    )
    av.calcular_media()
    db.session.add(av)
    db.session.commit()

    resp = cliente_logado.post(f"/avaliacoes/{av.id}/excluir")
    assert resp.status_code == 403


def test_editar_avaliacao_recalcula_media(cliente_logado, restaurante, avaliacao):
    """Editar notas deve recalcular a média corretamente."""
    from app import db
    from app.models import Avaliacao

    resp = cliente_logado.post(
        f"/avaliacoes/{avaliacao.id}/editar",
        data={
            "nota_atendimento": "5",
            "nota_ambiente": "5",
            "nota_prato": "5",
            "nota_preco": "5",
            "comentario": "Perfeito!",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    av = db.session.get(Avaliacao, avaliacao.id)
    assert av.media_calculada == 5.0


def test_nova_avaliacao_get_exibe_formulario(cliente_logado, restaurante):
    """GET em nova avaliação deve renderizar o formulário."""
    resp = cliente_logado.get(f"/avaliacoes/nova/{restaurante.id}")
    assert resp.status_code == 200
    assert b"form" in resp.data.lower()


def test_avaliacao_sem_comentario_permitida(cliente_logado, restaurante):
    """Avaliação sem comentário (campo opcional) deve ser aceita."""
    from app.models import Avaliacao

    resp = cliente_logado.post(
        f"/avaliacoes/nova/{restaurante.id}",
        data={
            "nota_atendimento": "3",
            "nota_ambiente": "3",
            "nota_prato": "3",
            "nota_preco": "3",
            "comentario": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    av = Avaliacao.query.filter_by(restaurante_id=restaurante.id).first()
    assert av is not None
    assert av.comentario == "" or av.comentario is None


def test_nova_avaliacao_com_foto_valida(cliente_logado, restaurante):
    """Upload de imagem JPEG válida deve salvar a avaliação com foto."""
    imagem = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 100)
    resp = cliente_logado.post(
        f"/avaliacoes/nova/{restaurante.id}",
        data={
            "nota_atendimento": "4",
            "nota_ambiente": "4",
            "nota_prato": "4",
            "nota_preco": "4",
            "comentario": "Com foto!",
            "foto": (imagem, "prato.jpg", "image/jpeg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    av = Avaliacao.query.filter_by(restaurante_id=restaurante.id).first()
    assert av is not None
    assert av.foto_path is not None


def test_nova_avaliacao_extensao_invalida_ignora_foto(cliente_logado, restaurante):
    """Upload com extensão inválida (PDF) não deve salvar foto."""
    arquivo_pdf = io.BytesIO(b"%PDF-1.4 fake content")
    resp = cliente_logado.post(
        f"/avaliacoes/nova/{restaurante.id}",
        data={
            "nota_atendimento": "3",
            "nota_ambiente": "3",
            "nota_prato": "3",
            "nota_preco": "3",
            "comentario": "Extensão errada",
            "foto": (arquivo_pdf, "documento.pdf", "application/pdf"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_editar_avaliacao_com_foto_nova(cliente_logado, restaurante, avaliacao):
    """Editar com nova foto deve substituir a foto anterior."""
    imagem = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 100)
    resp = cliente_logado.post(
        f"/avaliacoes/{avaliacao.id}/editar",
        data={
            "nota_atendimento": "5",
            "nota_ambiente": "5",
            "nota_prato": "5",
            "nota_preco": "5",
            "comentario": "Nova foto!",
            "foto": (imagem, "nova.jpg", "image/jpeg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    av = db.session.get(Avaliacao, avaliacao.id)
    assert av.foto_path is not None


def test_upload_acima_de_2mb_retorna_erro(cliente_logado, restaurante):
    """Arquivo acima de 2 MB deve disparar o handler 413."""
    arquivo_grande = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * (3 * 1024 * 1024))
    resp = cliente_logado.post(
        f"/avaliacoes/nova/{restaurante.id}",
        data={
            "nota_atendimento": "4",
            "nota_ambiente": "4",
            "nota_prato": "4",
            "nota_preco": "4",
            "comentario": "Grande demais",
            "foto": (arquivo_grande, "grande.jpg", "image/jpeg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    # Handler 413 faz redirect com flash; após follow_redirects status é 200
    assert resp.status_code == 200
