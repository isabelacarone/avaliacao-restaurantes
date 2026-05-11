"""Testes das rotas de autenticação e validadores de unicidade."""

from app.models import Usuario


def test_cadastro_cria_usuario(client):
    resp = client.post(
        "/cadastro",
        data={
            "nome": "Novo Usuario",
            "email": "novo@example.com",
            "senha": "senha123",
            "confirmar_senha": "senha123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Usuario.query.filter_by(email="novo@example.com").first() is not None


def test_cadastro_email_duplicado_exibe_erro_inline(client, usuario):
    """UniqueEmail deve devolver erro inline (200) em vez de redirecionar."""
    resp = client.post(
        "/cadastro",
        data={
            "nome": "Outro",
            "email": "test@example.com",
            "senha": "senha123",
            "confirmar_senha": "senha123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # O erro do UniqueEmail aparece inline no formulário
    assert "cadastrado" in resp.data.decode("utf-8").lower()
    assert Usuario.query.filter_by(email="test@example.com").count() == 1


def test_cadastro_email_invalido_exibe_erro(client):
    """Email com formato inválido deve ser rejeitado."""
    resp = client.post(
        "/cadastro",
        data={
            "nome": "Teste",
            "email": "email-invalido",
            "senha": "senha123",
            "confirmar_senha": "senha123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Usuario.query.filter_by(email="email-invalido").first() is None


def test_cadastro_campo_vazio_rejeitado(client):
    """Campos obrigatórios vazios devem impedir criação de usuário."""
    resp = client.post(
        "/cadastro",
        data={"nome": "", "email": "", "senha": "", "confirmar_senha": ""},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Usuario.query.count() == 0


def test_login_credenciais_corretas(client, usuario):
    resp = client.post(
        "/login",
        data={"email": "test@example.com", "senha": "senha123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Bem-vindo" in resp.data


def test_login_senha_errada(client, usuario):
    resp = client.post(
        "/login",
        data={"email": "test@example.com", "senha": "errada"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"incorretos" in resp.data


def test_perfil_requer_login(client):
    resp = client.get("/perfil", follow_redirects=True)
    assert resp.status_code == 200
    assert b"login" in resp.data.lower()


def test_perfil_usuario_autenticado(cliente_logado):
    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200
    assert b"Test User" in resp.data


def test_logout(cliente_logado):
    resp = cliente_logado.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    resp2 = cliente_logado.get("/perfil", follow_redirects=True)
    assert b"login" in resp2.data.lower()
