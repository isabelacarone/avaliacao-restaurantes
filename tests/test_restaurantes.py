"""Testes das rotas de restaurantes."""

from app.models import Restaurante


def test_listagem_publica(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_detalhe_existente(client, restaurante):
    resp = client.get(f"/restaurantes/{restaurante.id}")
    assert resp.status_code == 200
    assert b"Restaurante Teste" in resp.data


def test_detalhe_inexistente(client):
    resp = client.get("/restaurantes/9999")
    assert resp.status_code == 404


def test_novo_restaurante_requer_login(client):
    resp = client.get("/restaurantes/novo", follow_redirects=True)
    assert resp.status_code == 200
    assert b"login" in resp.data.lower()


def test_novo_restaurante_autenticado(cliente_logado):
    resp = cliente_logado.post(
        "/restaurantes/novo",
        data={
            "nome": "Pizzaria Bella",
            "categoria": "italiana",
            "faixa_preco": "moderado",
            "endereco": "Rua da Paz, 10",
            "descricao": "Pizza no forno a lenha",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Restaurante.query.filter_by(nome="Pizzaria Bella").first() is not None


def test_listagem_filtro_categoria(client, restaurante):
    resp = client.get("/?categoria=brasileira")
    assert resp.status_code == 200
    assert b"Restaurante Teste" in resp.data


def test_listagem_filtro_sem_resultado(client, restaurante):
    resp = client.get("/?q=xyzinexistente")
    assert resp.status_code == 200
    assert b"Restaurante Teste" not in resp.data
