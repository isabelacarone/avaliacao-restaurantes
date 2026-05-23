"""Testes da feature de perfil expandido: foto, idade e favoritos."""

import io

import pytest

from app import db
from app.models import Favorito, Usuario


# ---------------------------------------------------------------------------
# 5.1 Modelo
# ---------------------------------------------------------------------------


def test_usuario_aceita_foto_e_idade(app_ctx):
    u = Usuario(nome="Foto", email="foto@test.com", foto_perfil_path="perfil_1.jpg", idade=25)
    u.set_senha("Senha123")
    db.session.add(u)
    db.session.commit()
    recarregado = db.session.get(Usuario, u.id)
    assert recarregado.foto_perfil_path == "perfil_1.jpg"
    assert recarregado.idade == 25


def test_usuario_campos_opcionais_nulos(app_ctx):
    u = Usuario(nome="Sem foto", email="semfoto@test.com")
    u.set_senha("Senha123")
    db.session.add(u)
    db.session.commit()
    recarregado = db.session.get(Usuario, u.id)
    assert recarregado.foto_perfil_path is None
    assert recarregado.idade is None


# ---------------------------------------------------------------------------
# 5.2 Validação de idade
# ---------------------------------------------------------------------------


def test_editar_perfil_idade_valida(cliente_logado):
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "idade": "30",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.idade == 30


def test_editar_perfil_idade_minima_aceita(cliente_logado):
    """Exatamente 18 anos deve ser aceito."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "idade": "18",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.idade == 18


def test_editar_perfil_idade_abaixo_do_minimo(cliente_logado):
    """Idade menor que 18 deve ser rejeitada."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "idade": "17",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.idade != 17


def test_editar_perfil_idade_acima_do_maximo(cliente_logado):
    """Idade maior que 120 deve ser rejeitada."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "idade": "121",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.idade != 121


def test_editar_perfil_idade_vazia_aceita(cliente_logado):
    """Campo idade vazio (opcional) não deve causar erro."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "idade": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 5.3 Upload de foto de perfil
# ---------------------------------------------------------------------------


def test_editar_perfil_upload_foto(cliente_logado):
    """Upload de PNG válido deve salvar foto_perfil_path no usuário."""
    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "foto_perfil": (io.BytesIO(fake_png), "foto.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.foto_perfil_path is not None
    assert u.foto_perfil_path.endswith(".png")


def test_editar_perfil_upload_jpg(cliente_logado):
    """Upload de JPEG válido deve ser aceito."""
    fake_jpg = b"\xff\xd8\xff" + b"\x00" * 100
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "foto_perfil": (io.BytesIO(fake_jpg), "foto.jpg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.foto_perfil_path is not None
    assert u.foto_perfil_path.endswith(".jpg")


def test_editar_perfil_gif_rejeitado(cliente_logado):
    """GIF não é permitido em foto de perfil."""
    fake_gif = b"GIF8" + b"\x00" * 100
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "foto_perfil": (io.BytesIO(fake_gif), "animacao.gif"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.foto_perfil_path is None


def test_editar_perfil_foto_extensao_invalida(cliente_logado):
    """Extensão não permitida deve ser rejeitada sem alterar foto_perfil_path."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
            "foto_perfil": (io.BytesIO(b"dados"), "malware.exe"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.foto_perfil_path is None


def test_editar_perfil_sem_foto_nao_apaga_existente(cliente_logado, app_ctx):
    """Salvar sem enviar nova foto não deve apagar a foto já cadastrada."""
    u = Usuario.query.filter_by(email="test@example.com").first()
    u.foto_perfil_path = "perfil_existente.png"
    db.session.commit()

    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = db.session.get(Usuario, u.id)
    assert u.foto_perfil_path == "perfil_existente.png"


# ---------------------------------------------------------------------------
# 5.4 Favoritos exibidos no perfil
# ---------------------------------------------------------------------------


def test_perfil_exibe_favoritos(cliente_logado, restaurante, app_ctx):
    """Página /perfil deve listar os favoritos do usuário."""
    u = Usuario.query.filter_by(email="test@example.com").first()
    fav = Favorito(usuario_id=u.id, restaurante_id=restaurante.id)
    db.session.add(fav)
    db.session.commit()

    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200
    assert restaurante.nome.encode() in resp.data


def test_perfil_sem_favoritos_nao_quebra(cliente_logado):
    """Perfil sem favoritos deve renderizar normalmente."""
    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 5.5 Exibição dos novos campos no perfil
# ---------------------------------------------------------------------------


def test_perfil_exibe_idade_quando_preenchida(cliente_logado, app_ctx):
    """Página /perfil deve exibir a idade se ela estiver definida."""
    u = Usuario.query.filter_by(email="test@example.com").first()
    u.idade = 28
    db.session.commit()

    resp = cliente_logado.get("/perfil")
    assert b"28" in resp.data


def test_perfil_nao_exibe_idade_quando_nula(cliente_logado):
    """Perfil com idade None deve renderizar sem erro."""
    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Senha — novo comportamento: só exigida ao trocar senha
# ---------------------------------------------------------------------------


def test_editar_perfil_sem_senha_atual_muda_nome(cliente_logado):
    """Alterar nome sem informar senha atual deve funcionar."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Nome Novo Sem Senha",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "",
            "confirmar_nova_senha": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.nome == "Nome Novo Sem Senha"


def test_editar_perfil_troca_senha_exige_senha_atual(cliente_logado):
    """Tentar trocar a senha sem informar a senha atual deve ser rejeitado."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "",
            "nova_senha": "NovaSenha99",
            "confirmar_nova_senha": "NovaSenha99",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert not u.check_senha("NovaSenha99")


def test_editar_perfil_troca_senha_senha_atual_errada(cliente_logado):
    """Senha atual errada deve impedir a troca de senha."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "errada",
            "nova_senha": "NovaSenha99",
            "confirmar_nova_senha": "NovaSenha99",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert not u.check_senha("NovaSenha99")
