"""Fixtures compartilhadas para os testes do Mesa Certa.

Estratégia de isolamento:
- `app` é session-scoped (cria a Flask app uma vez) mas NÃO empurra app context,
  evitando que flask.g (app-context-scoped no Flask 2.2+) vaze entre testes.
- `app_ctx` é function-scoped: empurra/pop o contexto por teste.
- `limpar_banco` limpa todos os dados antes de cada teste.
- O test client cria seu próprio request context por request (padrão Flask).
"""

import os
import tempfile

import pytest

from app import create_app, db
from app.models import Avaliacao, Favorito, Restaurante, Usuario


@pytest.fixture(scope="session")
def app():
    """Cria a aplicação Flask uma única vez — sem empurrar app context."""
    db_fd, db_path = tempfile.mkstemp(suffix="_test.db")
    os.close(db_fd)

    # Config.SQLALCHEMY_DATABASE_URI é avaliada em import-time (quando conftest
    # é carregado pelo pytest). Flask-SQLAlchemy 3.x cria a engine em init_app(),
    # não de forma lazy. Por isso, a config de teste deve ser injetada via
    # test_config ANTES de init_app() — padrão recomendado pelo Flask.
    application = create_app(
        test_config={
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
            "RATELIMIT_ENABLED": False,
        }
    )

    with application.app_context():
        db.create_all()

    yield application

    os.unlink(db_path)


@pytest.fixture()
def app_ctx(app):
    """Empurra e pop um app context fresco a cada teste."""
    ctx = app.app_context()
    ctx.push()
    yield ctx
    db.session.remove()
    ctx.pop()


@pytest.fixture(autouse=True)
def limpar_banco(app_ctx):
    """Remove todos os dados antes de cada teste."""
    db.session.query(Avaliacao).delete()
    db.session.query(Favorito).delete()
    db.session.query(Restaurante).delete()
    db.session.query(Usuario).delete()
    db.session.commit()


@pytest.fixture()
def client(app):
    """Retorna um cliente de teste Flask fresco por teste."""
    return app.test_client()


@pytest.fixture()
def usuario(app_ctx):
    """Cria e retorna um usuário de teste."""
    u = Usuario(nome="Test User", email="test@example.com")
    u.set_senha("senha123")
    db.session.add(u)
    db.session.commit()
    return db.session.get(Usuario, u.id)


@pytest.fixture()
def restaurante(app_ctx):
    """Cria e retorna um restaurante de teste."""
    r = Restaurante(
        nome="Restaurante Teste",
        categoria="brasileira",
        faixa_preco="moderado",
        endereco="Rua Teste, 1",
    )
    db.session.add(r)
    db.session.commit()
    return db.session.get(Restaurante, r.id)


@pytest.fixture()
def cliente_logado(client, usuario):
    """Retorna cliente com sessão de login ativa."""
    client.post(
        "/login",
        data={"email": "test@example.com", "senha": "senha123"},
        follow_redirects=True,
    )
    return client


@pytest.fixture()
def avaliacao(app_ctx, usuario, restaurante):
    """Cria e retorna uma avaliação de teste."""
    av = Avaliacao(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        nota_atendimento=4,
        nota_ambiente=4,
        nota_prato=5,
        nota_preco=4,
        comentario="Ótimo restaurante!",
    )
    av.calcular_media()
    db.session.add(av)
    db.session.commit()
    return db.session.get(Avaliacao, av.id)
