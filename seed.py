"""Popula o banco de dados com dados de teste para o Mesa Certa.

Uso:
    uv run python seed.py

O script é idempotente: verifica se os dados já existem antes de inserir.
"""

from app import create_app, db
from app.models import Avaliacao, Restaurante, Usuario

app = create_app()

USUARIOS: list[dict] = [
    {"nome": "Ana Souza", "email": "ana@example.com", "senha": "senha123"},
    {"nome": "Bruno Lima", "email": "bruno@example.com", "senha": "senha123"},
    {"nome": "Carla Mendes", "email": "carla@example.com", "senha": "senha123"},
    {"nome": "Diego Ferreira", "email": "diego@example.com", "senha": "senha123"},
]

RESTAURANTES: list[dict] = [
    {
        "nome": "Cantina da Nonna",
        "categoria": "italiana",
        "faixa_preco": "moderado",
        "endereco": "Rua das Flores, 142 — Centro",
        "descricao": "Massas artesanais e molhos feitos no dia. Ambiente aconchegante com decoração italiana.",
    },
    {
        "nome": "Sakura Sushi Bar",
        "categoria": "japonesa",
        "faixa_preco": "sofisticado",
        "endereco": "Av. Paulista, 890 — Bela Vista",
        "descricao": "Culinária japonesa contemporânea com peixes frescos importados diretamente.",
    },
    {
        "nome": "Churrascaria do Gaúcho",
        "categoria": "brasileira",
        "faixa_preco": "moderado",
        "endereco": "Estrada Velha, 33 — Jardim América",
        "descricao": "Rodízio de carnes nobres com cortes gaúchos e buffet de saladas.",
    },
    {
        "nome": "El Mariachi",
        "categoria": "mexicana",
        "faixa_preco": "economico",
        "endereco": "Rua XV de Novembro, 55 — Bairro Alto",
        "descricao": "Tacos, burritos e nachos com ingredientes frescos. Ambiente descontraído.",
    },
    {
        "nome": "The Brooklyn Burger",
        "categoria": "americana",
        "faixa_preco": "economico",
        "endereco": "Rua das Palmeiras, 210 — Pinheiros",
        "descricao": "Hambúrgueres artesanais com pão brioche. Batata frita crocante inclusa.",
    },
    {
        "nome": "Bistrô Provence",
        "categoria": "francesa",
        "faixa_preco": "sofisticado",
        "endereco": "Alameda Santos, 1200 — Jardins",
        "descricao": "Alta gastronomia francesa com carta de vinhos selecionados e menu degustação.",
    },
    {
        "nome": "Verdura & Cia",
        "categoria": "vegana",
        "faixa_preco": "moderado",
        "endereco": "Rua Augusta, 480 — Consolação",
        "descricao": "Cardápio 100% vegano com pratos criativos e ingredientes orgânicos certificados.",
    },
    {
        "nome": "Mar Aberto",
        "categoria": "frutos_do_mar",
        "faixa_preco": "sofisticado",
        "endereco": "Rua da Praia, 77 — Itaim Bibi",
        "descricao": "Frutos do mar frescos e moquecas tradicionais. Vista para o jardim.",
    },
    {
        "nome": "Kebab do Oriente",
        "categoria": "árabe",
        "faixa_preco": "economico",
        "endereco": "Rua 25 de Março, 340 — Liberdade",
        "descricao": "Kebabs, falafel e homus artesanal. Ambiente familiar com música ao vivo às sextas.",
    },
    {
        "nome": "Fogão de Minas",
        "categoria": "brasileira",
        "faixa_preco": "economico",
        "endereco": "Rua Joaquim Nabuco, 12 — Vila Madalena",
        "descricao": "Comida mineira autêntica: feijão tropeiro, frango com quiabo e pão de queijo na hora.",
    },
]

AVALIACOES: list[dict] = [
    # Cantina da Nonna (idx 0)
    {"rest": 0, "user": 0, "at": 5, "am": 5, "pr": 5, "pc": 4, "comentario": "Melhor carbonara da cidade! O ambiente é super aconchegante."},
    {"rest": 0, "user": 1, "at": 4, "am": 5, "pr": 4, "pc": 3, "comentario": "Massa fresca deliciosa. Um pouco caro mas vale a pena."},
    {"rest": 0, "user": 2, "at": 5, "am": 4, "pr": 5, "pc": 4, "comentario": "Fui no aniversário e adorei. Atendimento impecável."},
    # Sakura (idx 1)
    {"rest": 1, "user": 0, "at": 5, "am": 5, "pr": 5, "pc": 3, "comentario": "O omakase é uma experiência única. Peixe fresquíssimo."},
    {"rest": 1, "user": 2, "at": 4, "am": 5, "pr": 5, "pc": 3, "comentario": "Apresentação linda, sabor incrível. Preço elevado mas justificado."},
    {"rest": 1, "user": 3, "at": 3, "am": 4, "pr": 4, "pc": 2, "comentario": "Bom sushi mas para o preço esperava mais criatividade."},
    # Churrascaria (idx 2)
    {"rest": 2, "user": 1, "at": 4, "am": 3, "pr": 5, "pc": 5, "comentario": "Carne excelente, picanha no ponto certo. Ótimo custo-benefício."},
    {"rest": 2, "user": 3, "at": 3, "am": 3, "pr": 4, "pc": 4, "comentario": "Rodízio farto. Barulhento nos fins de semana."},
    # El Mariachi (idx 3)
    {"rest": 3, "user": 0, "at": 4, "am": 4, "pr": 4, "pc": 5, "comentario": "Tacos incríveis pelo preço. Guacamole fresco e saboroso."},
    {"rest": 3, "user": 2, "at": 5, "am": 3, "pr": 4, "pc": 5, "comentario": "Comida boa e barata! Atendimento simpático. Voltarei."},
    # Brooklyn Burger (idx 4)
    {"rest": 4, "user": 1, "at": 4, "am": 3, "pr": 5, "pc": 5, "comentario": "O smash burger é absurdamente bom. Batata frita crocante perfeita."},
    {"rest": 4, "user": 3, "at": 3, "am": 3, "pr": 4, "pc": 4, "comentario": "Hambúrguer gostoso. Espera um pouco longa no sábado."},
    # Bistrô Provence (idx 5)
    {"rest": 5, "user": 0, "at": 5, "am": 5, "pr": 5, "pc": 3, "comentario": "Jantar romântico perfeito. O magret de canard estava divino."},
    {"rest": 5, "user": 2, "at": 5, "am": 5, "pr": 4, "pc": 2, "comentario": "Ambiente sofisticado e comida excelente. Caro, mas especial."},
    # Verdura & Cia (idx 6)
    {"rest": 6, "user": 1, "at": 5, "am": 4, "pr": 4, "pc": 4, "comentario": "Surpreendente! Não sinto falta da carne. Strogonoff de cogumelos incrível."},
    {"rest": 6, "user": 3, "at": 4, "am": 4, "pr": 3, "pc": 4, "comentario": "Opções interessantes. Nem tudo agradou mas vale experimentar."},
    # Mar Aberto (idx 7)
    {"rest": 7, "user": 0, "at": 4, "am": 5, "pr": 5, "pc": 3, "comentario": "A moqueca de camarão é espetacular. Recomendo fortemente."},
    {"rest": 7, "user": 2, "at": 5, "am": 4, "pr": 5, "pc": 3, "comentario": "Frutos do mar fresquíssimos. O peixe grelhado estava perfeito."},
    # Kebab (idx 8)
    {"rest": 8, "user": 1, "at": 4, "am": 3, "pr": 4, "pc": 5, "comentario": "Kebab enorme pelo preço. Falafel crocante e homus cremoso."},
    {"rest": 8, "user": 3, "at": 3, "am": 2, "pr": 4, "pc": 5, "comentario": "Comida gostosa e baratinha. Ambiente simples mas honesto."},
    # Fogão de Minas (idx 9)
    {"rest": 9, "user": 0, "at": 5, "am": 4, "pr": 5, "pc": 5, "comentario": "Pão de queijo saindo do forno! Feijão tropeiro idêntico ao da vó."},
    {"rest": 9, "user": 1, "at": 4, "am": 4, "pr": 5, "pc": 5, "comentario": "Comida de alma. Porção enorme, saí satisfeito e gastei pouco."},
    {"rest": 9, "user": 2, "at": 5, "am": 4, "pr": 4, "pc": 5, "comentario": "Melhor frango ao molho pardo que comi. Voltarei toda semana."},
]


def seed() -> None:
    """Insere os dados de teste no banco de dados."""
    with app.app_context():
        db.create_all()  # garante tabelas caso flask db upgrade não tenha rodado
        usuarios_criados: list[Usuario] = []
        for dados in USUARIOS:
            existente = Usuario.query.filter_by(email=dados["email"]).first()
            if existente:
                usuarios_criados.append(existente)
                continue
            u = Usuario(nome=dados["nome"], email=dados["email"])
            u.set_senha(dados["senha"])
            db.session.add(u)
            db.session.flush()
            usuarios_criados.append(u)
            print(f"  Usuário criado: {u.nome} ({u.email})")

        restaurantes_criados: list[Restaurante] = []
        for dados in RESTAURANTES:
            existente = Restaurante.query.filter_by(nome=dados["nome"]).first()
            if existente:
                restaurantes_criados.append(existente)
                continue
            r = Restaurante(**dados)
            db.session.add(r)
            db.session.flush()
            restaurantes_criados.append(r)
            print(f"  Restaurante criado: {r.nome}")

        for av_dados in AVALIACOES:
            usuario = usuarios_criados[av_dados["user"]]
            restaurante = restaurantes_criados[av_dados["rest"]]
            ja_existe = Avaliacao.query.filter_by(
                usuario_id=usuario.id, restaurante_id=restaurante.id
            ).first()
            if ja_existe:
                continue
            av = Avaliacao(
                usuario_id=usuario.id,
                restaurante_id=restaurante.id,
                nota_atendimento=av_dados["at"],
                nota_ambiente=av_dados["am"],
                nota_prato=av_dados["pr"],
                nota_preco=av_dados["pc"],
                comentario=av_dados.get("comentario"),
            )
            av.calcular_media()
            db.session.add(av)

        db.session.commit()
        u_total = Usuario.query.count()
        r_total = Restaurante.query.count()
        av_total = Avaliacao.query.count()
        print(f"\nBanco populado: {u_total} usuários · {r_total} restaurantes · {av_total} avaliações")
        print("\nContas de teste (senha: senha123):")
        for u in USUARIOS:
            print(f"  {u['email']}")


if __name__ == "__main__":
    seed()
