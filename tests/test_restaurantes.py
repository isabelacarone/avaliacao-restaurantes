"""Testes das rotas de restaurantes e validador de nome único."""

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


def test_novo_restaurante_nome_duplicado_exibe_erro(cliente_logado, restaurante):
    """UniqueNomeRestaurante deve impedir criação de restaurante duplicado."""
    resp = cliente_logado.post(
        "/restaurantes/novo",
        data={
            "nome": "Restaurante Teste",
            "categoria": "brasileira",
            "faixa_preco": "moderado",
            "endereco": "Outra rua, 99",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Restaurante.query.filter_by(nome="Restaurante Teste").count() == 1


def test_novo_restaurante_campo_vazio_rejeitado(cliente_logado):
    """Campos obrigatórios vazios devem impedir criação de restaurante."""
    resp = cliente_logado.post(
        "/restaurantes/novo",
        data={
            "nome": "",
            "categoria": "italiana",
            "faixa_preco": "moderado",
            "endereco": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Restaurante.query.count() == 0


def test_listagem_filtro_categoria(client, restaurante):
    resp = client.get("/?categoria=brasileira")
    assert resp.status_code == 200
    assert b"Restaurante Teste" in resp.data


def test_listagem_filtro_sem_resultado(client, restaurante):
    resp = client.get("/?q=xyzinexistente")
    assert resp.status_code == 200
    assert b"Restaurante Teste" not in resp.data


def test_listagem_ordenacao_nota(client, restaurante):
    """Parâmetro order=nota deve retornar 200."""
    resp = client.get("/?order=nota")
    assert resp.status_code == 200


def test_listagem_ordenacao_avaliacoes(client, restaurante):
    """Parâmetro order=avaliacoes deve retornar 200."""
    resp = client.get("/?order=avaliacoes")
    assert resp.status_code == 200


def test_listagem_ordenacao_recentes(client, restaurante):
    """Parâmetro order=recentes (padrão) deve retornar 200."""
    resp = client.get("/?order=recentes")
    assert resp.status_code == 200


def test_listagem_filtro_faixa_preco(client, restaurante):
    """Filtro por faixa_preco deve retornar restaurante com preço moderado."""
    resp = client.get("/?faixa_preco=moderado")
    assert resp.status_code == 200
    assert b"Restaurante Teste" in resp.data


def test_listagem_filtro_faixa_preco_sem_resultado(client, restaurante):
    """Filtro por faixa_preco=sofisticado não deve retornar restaurante moderado."""
    resp = client.get("/?faixa_preco=sofisticado")
    assert resp.status_code == 200
    assert b"Restaurante Teste" not in resp.data


def test_listagem_filtro_combinado_categoria_e_faixa(client, restaurante):
    """Filtro combinado categoria + faixa_preco deve retornar o restaurante correto."""
    resp = client.get("/?categoria=brasileira&faixa_preco=moderado")
    assert resp.status_code == 200
    assert b"Restaurante Teste" in resp.data


def test_listagem_filtro_combinado_sem_resultado(client, restaurante):
    """Combinação inválida não deve retornar resultados."""
    resp = client.get("/?categoria=japonesa&faixa_preco=economico")
    assert resp.status_code == 200
    assert b"Restaurante Teste" not in resp.data


def test_detalhe_exibe_avaliacao(client, restaurante, avaliacao):
    """Página de detalhe deve exibir avaliação existente."""
    resp = client.get(f"/restaurantes/{restaurante.id}")
    assert resp.status_code == 200
    body = resp.data.decode("utf-8")
    assert "timo restaurante" in body


def test_detalhe_exibe_nota_media(client, restaurante, avaliacao):
    """Página de detalhe deve exibir a nota média calculada."""
    resp = client.get(f"/restaurantes/{restaurante.id}")
    assert resp.status_code == 200
    assert b"4" in resp.data


def test_novo_restaurante_sem_endereco_rejeitado(cliente_logado):
    """Envio sem endereço não deve criar restaurante."""
    resp = cliente_logado.post(
        "/restaurantes/novo",
        data={
            "nome": "Sem Endereco",
            "categoria": "italiana",
            "faixa_preco": "moderado",
            "endereco": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Restaurante.query.filter_by(nome="Sem Endereco").first() is None


def test_listagem_filtro_nota_min_encontra(client, restaurante, avaliacao):
    """Filtro nota_min=4 deve retornar restaurante com média 4.25."""
    resp = client.get("/?nota_min=4")
    assert resp.status_code == 200
    assert b"Restaurante Teste" in resp.data


def test_listagem_filtro_nota_min_exclui(client, restaurante, avaliacao):
    """Filtro nota_min=5 não deve retornar restaurante com média 4.25."""
    resp = client.get("/?nota_min=5")
    assert resp.status_code == 200
    assert b"Restaurante Teste" not in resp.data


def test_listagem_filtro_nota_min_sem_avaliacoes(client, restaurante):
    """Restaurante sem avaliações não deve aparecer quando nota_min está ativo."""
    resp = client.get("/?nota_min=1")
    assert resp.status_code == 200
    assert b"Restaurante Teste" not in resp.data


def test_listagem_filtro_nota_min_combinado_categoria(client, restaurante, avaliacao):
    """nota_min combinado com categoria deve filtrar corretamente."""
    resp = client.get("/?nota_min=4&categoria=brasileira")
    assert resp.status_code == 200
    assert b"Restaurante Teste" in resp.data
