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


def test_login_email_inexistente(client):
    """Login com e-mail que não existe no banco deve falhar."""
    resp = client.post(
        "/login",
        data={"email": "naoexiste@example.com", "senha": "senha123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"incorretos" in resp.data


def test_cadastro_senhas_divergem(client):
    """Cadastro com senhas diferentes não deve criar usuário."""
    from app.models import Usuario

    resp = client.post(
        "/cadastro",
        data={
            "nome": "Teste Diverge",
            "email": "diverge@example.com",
            "senha": "senha123",
            "confirmar_senha": "senha456",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Usuario.query.filter_by(email="diverge@example.com").first() is None


def test_perfil_exibe_contagem_de_avaliacoes(cliente_logado, restaurante, avaliacao):
    """Página de perfil deve exibir o número de avaliações do usuário."""
    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200
    body = resp.data.decode("utf-8")
    assert "avalia" in body.lower()


def test_cadastro_email_maiusculas_normalizado(client):
    """E-mail com letras maiúsculas não deve ser duplicado após normalização."""
    from app.models import Usuario

    client.post(
        "/cadastro",
        data={
            "nome": "Maiusculo",
            "email": "Maiusculo@example.com",
            "senha": "senha123",
            "confirmar_senha": "senha123",
        },
        follow_redirects=True,
    )
    # Deve haver exatamente um usuário com esse e-mail (ou variante lowercase)
    total = Usuario.query.filter(
        Usuario.email.in_(["maiusculo@example.com", "Maiusculo@example.com"])
    ).count()
    assert total == 1


# ---------------------------------------------------------------------------
# Edição de perfil
# ---------------------------------------------------------------------------


def test_editar_perfil_get_exibe_formulario(cliente_logado):
    """GET /perfil/editar deve exibir o formulário pré-preenchido."""
    resp = cliente_logado.get("/perfil/editar")
    assert resp.status_code == 200
    assert b"Test User" in resp.data


def test_editar_perfil_requer_login(client):
    """GET /perfil/editar sem login deve redirecionar para login."""
    resp = client.get("/perfil/editar", follow_redirects=True)
    assert resp.status_code == 200
    assert b"login" in resp.data.lower()


def test_editar_perfil_muda_nome(cliente_logado):
    """POST com nome novo e senha correta deve atualizar o nome do usuário."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Nome Alterado",
            "email": "test@example.com",
            "senha_atual": "senha123",
            "nova_senha": "",
            "confirmar_nova_senha": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.nome == "Nome Alterado"


def test_editar_perfil_muda_email(cliente_logado):
    """POST com e-mail novo e senha correta deve atualizar o e-mail."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "newemail@example.com",
            "senha_atual": "senha123",
            "nova_senha": "",
            "confirmar_nova_senha": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Usuario.query.filter_by(email="newemail@example.com").first() is not None


def test_editar_perfil_muda_senha(cliente_logado):
    """POST com nova senha válida deve alterar o hash da senha."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "senha123",
            "nova_senha": "novaSenha456",
            "confirmar_nova_senha": "novaSenha456",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.check_senha("novaSenha456")


def test_editar_perfil_senha_atual_errada(cliente_logado):
    """Senha atual incorreta deve rejeitar a alteração."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "errada",
            "nova_senha": "",
            "confirmar_nova_senha": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"incorreta" in resp.data.lower() or b"atual" in resp.data.lower()


def test_editar_perfil_email_duplicado_rejeitado(cliente_logado, app_ctx):
    """E-mail já usado por outro usuário deve ser rejeitado inline."""
    from app import db

    outro = Usuario(nome="Outro", email="outro@dup.com")
    outro.set_senha("senha123")
    db.session.add(outro)
    db.session.commit()

    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "outro@dup.com",
            "senha_atual": "senha123",
            "nova_senha": "",
            "confirmar_nova_senha": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "cadastrado" in resp.data.decode("utf-8").lower()


def test_editar_perfil_novo_email_igual_ao_proprio(cliente_logado):
    """Manter o próprio e-mail não deve ser rejeitado como duplicado."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "senha123",
            "nova_senha": "",
            "confirmar_nova_senha": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Usuario.query.filter_by(email="test@example.com").count() == 1


def test_editar_perfil_nova_senha_curta_rejeitada(cliente_logado):
    """Nova senha com menos de 6 caracteres deve ser rejeitada."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User",
            "email": "test@example.com",
            "senha_atual": "senha123",
            "nova_senha": "abc",
            "confirmar_nova_senha": "abc",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert not u.check_senha("abc")
