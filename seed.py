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
    {"nome": "Elena Costa", "email": "elena@example.com", "senha": "senha123"},
    {"nome": "Fábio Rocha", "email": "fabio@example.com", "senha": "senha123"},
    {"nome": "Gabriela Nunes", "email": "gabriela@example.com", "senha": "senha123"},
    {"nome": "Henrique Alves", "email": "henrique@example.com", "senha": "senha123"},
]

RESTAURANTES: list[dict] = [
    # 0
    {
        "nome": "Cantina da Nonna",
        "categoria": "italiana",
        "faixa_preco": "moderado",
        "endereco": "Rua das Flores, 142 — Centro",
        "descricao": "Massas artesanais e molhos feitos no dia. Ambiente aconchegante com decoração italiana.",
    },
    # 1
    {
        "nome": "Sakura Sushi Bar",
        "categoria": "japonesa",
        "faixa_preco": "sofisticado",
        "endereco": "Av. Paulista, 890, Bela Vista",
        "descricao": "Culinária japonesa contemporânea com peixes frescos importados diretamente.",
    },
    # 2
    {
        "nome": "Churrascaria do Gaúcho",
        "categoria": "brasileira",
        "faixa_preco": "moderado",
        "endereco": "Estrada Velha, 33, Jardim América",
        "descricao": "Rodízio de carnes nobres com cortes gaúchos e buffet de saladas.",
    },
    # 3
    {
        "nome": "El Mariachi",
        "categoria": "mexicana",
        "faixa_preco": "economico",
        "endereco": "Rua XV de Novembro, 55, Bairro Alto",
        "descricao": "Tacos, burritos e nachos com ingredientes frescos. Ambiente descontraído.",
    },
    # 4
    {
        "nome": "The Brooklyn Burger",
        "categoria": "americana",
        "faixa_preco": "economico",
        "endereco": "Rua das Palmeiras, 210, Pinheiros",
        "descricao": "Hambúrgueres artesanais com pão brioche. Batata frita crocante inclusa.",
    },
    # 5
    {
        "nome": "Bistrô Provence",
        "categoria": "francesa",
        "faixa_preco": "sofisticado",
        "endereco": "Alameda Santos, 1200, Jardins",
        "descricao": "Alta gastronomia francesa com carta de vinhos selecionados e menu degustação.",
    },
    # 6
    {
        "nome": "Verdura & Cia",
        "categoria": "vegana",
        "faixa_preco": "moderado",
        "endereco": "Rua Augusta, 480, Consolação",
        "descricao": "Cardápio 100% vegano com pratos criativos e ingredientes orgânicos certificados.",
    },
    # 7
    {
        "nome": "Mar Aberto",
        "categoria": "frutos_do_mar",
        "faixa_preco": "sofisticado",
        "endereco": "Rua da Praia, 77, Itaim Bibi",
        "descricao": "Frutos do mar frescos e moquecas tradicionais. Vista para o jardim.",
    },
    # 8
    {
        "nome": "Kebab do Oriente",
        "categoria": "árabe",
        "faixa_preco": "economico",
        "endereco": "Rua 25 de Março, 340, Liberdade",
        "descricao": "Kebabs, falafel e homus artesanal. Ambiente familiar com música ao vivo às sextas.",
    },
    # 9
    {
        "nome": "Fogão de Minas",
        "categoria": "brasileira",
        "faixa_preco": "economico",
        "endereco": "Rua Joaquim Nabuco, 12, Vila Madalena",
        "descricao": "Comida mineira autêntica: feijão tropeiro, frango com quiabo e pão de queijo na hora.",
    },
    # 10
    {
        "nome": "Trattoria Bella Napoli",
        "categoria": "italiana",
        "faixa_preco": "sofisticado",
        "endereco": "Rua Oscar Freire, 345, Cerqueira César",
        "descricao": "Pizzas napolitanas no forno a lenha importado da Itália. Farinha tipo 00.",
    },
    # 11
    {
        "nome": "Ramen do Mestre",
        "categoria": "japonesa",
        "faixa_preco": "moderado",
        "endereco": "Rua Galvão Bueno, 230, Liberdade",
        "descricao": "Ramen tonkotsu com caldo fervido por 18 horas. Gyoza artesanal.",
    },
    # 12
    {
        "nome": "Taco Loco",
        "categoria": "mexicana",
        "faixa_preco": "moderado",
        "endereco": "Av. Rebouças, 512, Pinheiros",
        "descricao": "Tacos gourmet com tortilha artesanal. Ingredientes importados do México.",
    },
    # 13
    {
        "nome": "Texas BBQ House",
        "categoria": "americana",
        "faixa_preco": "moderado",
        "endereco": "Rua dos Pinheiros, 88, Pinheiros",
        "descricao": "Costela defumada por 12 horas em estilo texano. Molho barbecue artesanal.",
    },
    # 14
    {
        "nome": "Brasserie Du Soleil",
        "categoria": "francesa",
        "faixa_preco": "moderado",
        "endereco": "Rua Haddock Lobo, 980, Cerqueira César",
        "descricao": "Clássicos franceses em ambiente descontraído. Crepe suzette e onion soup.",
    },
    # 15
    {
        "nome": "Green Kitchen",
        "categoria": "vegana",
        "faixa_preco": "economico",
        "endereco": "Rua Bela Cintra, 720, Consolação",
        "descricao": "Fast food vegano com hambúrgueres de grão-de-bico e bowls coloridos.",
    },
    # 16
    {
        "nome": "Osteria Porto Fino",
        "categoria": "frutos_do_mar",
        "faixa_preco": "moderado",
        "endereco": "Rua Mourato Coelho, 60, Vila Madalena",
        "descricao": "Frutos do mar grelhados e risoto de lulas. Vinho branco gelado na taça.",
    },
    # 17
    {
        "nome": "Al Fanar",
        "categoria": "árabe",
        "faixa_preco": "moderado",
        "endereco": "Rua Antônio de Barros, 540, Tatuapé",
        "descricao": "Culinária árabe completa: quibe assado, esfiha e charuto de uva.",
    },
    # 18
    {
        "nome": "Boteco do Zé",
        "categoria": "brasileira",
        "faixa_preco": "economico",
        "endereco": "Rua Harmonia, 22, Vila Madalena",
        "descricao": "Petiscos brasileiros clássicos: coxinha, pastel e polenta frita. Chopp gelado.",
    },
    # 19
    {
        "nome": "Empório da Massa",
        "categoria": "italiana",
        "faixa_preco": "economico",
        "endereco": "Rua dos Três Irmãos, 108, Saúde",
        "descricao": "Massas frescas por quilo e pratos do dia. Rápido, gostoso e barato.",
    },
]

AVALIACOES: list[dict] = [
    # Cantina da Nonna (0)
    {
        "rest": 0,
        "user": 0,
        "at": 5,
        "am": 5,
        "pr": 5,
        "pc": 4,
        "c": "Melhor carbonara da cidade! O ambiente é super aconchegante.",
    },
    {
        "rest": 0,
        "user": 1,
        "at": 4,
        "am": 5,
        "pr": 4,
        "pc": 3,
        "c": "Massa fresca deliciosa. Um pouco caro mas vale a pena.",
    },
    {
        "rest": 0,
        "user": 2,
        "at": 5,
        "am": 4,
        "pr": 5,
        "pc": 4,
        "c": "Fui no aniversário e adorei. Atendimento impecável.",
    },
    {
        "rest": 0,
        "user": 4,
        "at": 4,
        "am": 4,
        "pr": 4,
        "pc": 3,
        "c": "Boa comida, ambiente agradável. Voltaria sim.",
    },
    # Sakura (1)
    {
        "rest": 1,
        "user": 0,
        "at": 5,
        "am": 5,
        "pr": 5,
        "pc": 3,
        "c": "O omakase é uma experiência única. Peixe fresquíssimo.",
    },
    {
        "rest": 1,
        "user": 2,
        "at": 4,
        "am": 5,
        "pr": 5,
        "pc": 3,
        "c": "Apresentação linda, sabor incrível. Preço elevado mas justificado.",
    },
    {
        "rest": 1,
        "user": 3,
        "at": 3,
        "am": 4,
        "pr": 4,
        "pc": 2,
        "c": "Bom sushi mas para o preço esperava mais criatividade.",
    },
    {
        "rest": 1,
        "user": 5,
        "at": 5,
        "am": 5,
        "pr": 5,
        "pc": 4,
        "c": "O melhor restaurante japonês que fui em anos. Imperdível.",
    },
    # Churrascaria (2)
    {
        "rest": 2,
        "user": 1,
        "at": 4,
        "am": 3,
        "pr": 5,
        "pc": 5,
        "c": "Carne excelente, picanha no ponto certo. Ótimo custo-benefício.",
    },
    {
        "rest": 2,
        "user": 3,
        "at": 3,
        "am": 3,
        "pr": 4,
        "pc": 4,
        "c": "Rodízio farto. Barulhento nos fins de semana.",
    },
    {
        "rest": 2,
        "user": 6,
        "at": 4,
        "am": 4,
        "pr": 5,
        "pc": 5,
        "c": "Perfeito para almoço em família. Saladas frescas e variedade de cortes.",
    },
    # El Mariachi (3)
    {
        "rest": 3,
        "user": 0,
        "at": 4,
        "am": 4,
        "pr": 4,
        "pc": 5,
        "c": "Tacos incríveis pelo preço. Guacamole fresco e saboroso.",
    },
    {
        "rest": 3,
        "user": 2,
        "at": 5,
        "am": 3,
        "pr": 4,
        "pc": 5,
        "c": "Comida boa e barata! Atendimento simpático. Voltarei.",
    },
    {
        "rest": 3,
        "user": 7,
        "at": 3,
        "am": 3,
        "pr": 3,
        "pc": 4,
        "c": "Razoável. Não é o mais autêntico mas serve bem.",
    },
    # Brooklyn Burger (4)
    {
        "rest": 4,
        "user": 1,
        "at": 4,
        "am": 3,
        "pr": 5,
        "pc": 5,
        "c": "O smash burger é absurdamente bom. Batata frita crocante perfeita.",
    },
    {
        "rest": 4,
        "user": 3,
        "at": 3,
        "am": 3,
        "pr": 4,
        "pc": 4,
        "c": "Hambúrguer gostoso. Espera um pouco longa no sábado.",
    },
    {
        "rest": 4,
        "user": 5,
        "at": 4,
        "am": 3,
        "pr": 5,
        "pc": 4,
        "c": "O double smash é viciante. Preço justo para a qualidade.",
    },
    # Bistrô Provence (5)
    {
        "rest": 5,
        "user": 0,
        "at": 5,
        "am": 5,
        "pr": 5,
        "pc": 3,
        "c": "Jantar romântico perfeito. O magret de canard estava divino.",
    },
    {
        "rest": 5,
        "user": 2,
        "at": 5,
        "am": 5,
        "pr": 4,
        "pc": 2,
        "c": "Ambiente sofisticado e comida excelente. Caro, mas especial.",
    },
    {
        "rest": 5,
        "user": 4,
        "at": 5,
        "am": 5,
        "pr": 5,
        "pc": 3,
        "c": "Menu degustação memorável. A sommelier foi excelente na escolha dos vinhos.",
    },
    # Verdura & Cia (6)
    {
        "rest": 6,
        "user": 1,
        "at": 5,
        "am": 4,
        "pr": 4,
        "pc": 4,
        "c": "Surpreendente! Não sinto falta da carne. Strogonoff de cogumelos incrível.",
    },
    {
        "rest": 6,
        "user": 3,
        "at": 4,
        "am": 4,
        "pr": 3,
        "pc": 4,
        "c": "Opções interessantes. Nem tudo agradou mas vale experimentar.",
    },
    {
        "rest": 6,
        "user": 7,
        "at": 4,
        "am": 3,
        "pr": 4,
        "pc": 5,
        "c": "Melhor fast food vegano da região. O burger de lentilha é surpreendente.",
    },
    # Mar Aberto (7)
    {
        "rest": 7,
        "user": 0,
        "at": 4,
        "am": 5,
        "pr": 5,
        "pc": 3,
        "c": "A moqueca de camarão é espetacular. Recomendo fortemente.",
    },
    {
        "rest": 7,
        "user": 2,
        "at": 5,
        "am": 4,
        "pr": 5,
        "pc": 3,
        "c": "Frutos do mar fresquíssimos. O peixe grelhado estava perfeito.",
    },
    {
        "rest": 7,
        "user": 6,
        "at": 5,
        "am": 5,
        "pr": 5,
        "pc": 4,
        "c": "Polvo grelhado simplesmente incrível. Vinho branco harmonizou perfeitamente.",
    },
    # Kebab (8)
    {
        "rest": 8,
        "user": 1,
        "at": 4,
        "am": 3,
        "pr": 4,
        "pc": 5,
        "c": "Kebab enorme pelo preço. Falafel crocante e homus cremoso.",
    },
    {
        "rest": 8,
        "user": 3,
        "at": 3,
        "am": 2,
        "pr": 4,
        "pc": 5,
        "c": "Comida gostosa e baratinha. Ambiente simples mas honesto.",
    },
    {
        "rest": 8,
        "user": 5,
        "at": 4,
        "am": 3,
        "pr": 5,
        "pc": 5,
        "c": "Melhor falafel que comi. A música ao vivo na sexta é um charme.",
    },
    # Fogão de Minas (9)
    {
        "rest": 9,
        "user": 0,
        "at": 5,
        "am": 4,
        "pr": 5,
        "pc": 5,
        "c": "Pão de queijo saindo do forno! Feijão tropeiro idêntico ao da vó.",
    },
    {
        "rest": 9,
        "user": 1,
        "at": 4,
        "am": 4,
        "pr": 5,
        "pc": 5,
        "c": "Comida de alma. Porção enorme, saí satisfeito e gastei pouco.",
    },
    {
        "rest": 9,
        "user": 2,
        "at": 5,
        "am": 4,
        "pr": 4,
        "pc": 5,
        "c": "Melhor frango ao molho pardo que comi. Voltarei toda semana.",
    },
    {
        "rest": 9,
        "user": 7,
        "at": 4,
        "am": 3,
        "pr": 5,
        "pc": 5,
        "c": "Tutu de feijão e costelinha incrível. Preço honestíssimo.",
    },
    # Trattoria Bella Napoli (10)
    {
        "rest": 10,
        "user": 3,
        "at": 5,
        "am": 5,
        "pr": 5,
        "pc": 3,
        "c": "Pizza napolitana autêntica, borda fofinha e molho san marzano perfeito.",
    },
    {
        "rest": 10,
        "user": 4,
        "at": 4,
        "am": 5,
        "pr": 5,
        "pc": 3,
        "c": "Margherita simples e sensacional. Vale cada centavo.",
    },
    {
        "rest": 10,
        "user": 6,
        "at": 5,
        "am": 4,
        "pr": 5,
        "pc": 2,
        "c": "Caro mas único na cidade. A pizza Diavola queimou de boa forma.",
    },
    # Ramen do Mestre (11)
    {
        "rest": 11,
        "user": 0,
        "at": 4,
        "am": 4,
        "pr": 5,
        "pc": 4,
        "c": "Caldo tonkotsu profundo e encorpado. O ovo marinado é perfeito.",
    },
    {
        "rest": 11,
        "user": 4,
        "at": 5,
        "am": 4,
        "pr": 5,
        "pc": 4,
        "c": "Melhor ramen da cidade. O gyoza tem casca fininha e recheio suculento.",
    },
    {
        "rest": 11,
        "user": 7,
        "at": 3,
        "am": 3,
        "pr": 4,
        "pc": 3,
        "c": "Bom ramen mas espera de 40 minutos. Vai nos dias de semana.",
    },
    # Taco Loco (12)
    {
        "rest": 12,
        "user": 1,
        "at": 4,
        "am": 4,
        "pr": 4,
        "pc": 4,
        "c": "Taco de carnitas muito saboroso. Diferente dos tacos comuns por aqui.",
    },
    {
        "rest": 12,
        "user": 5,
        "at": 5,
        "am": 4,
        "pr": 4,
        "pc": 3,
        "c": "Tortilha artesanal faz toda a diferença. Mezcal sour incrível.",
    },
    # Texas BBQ (13)
    {
        "rest": 13,
        "user": 2,
        "at": 4,
        "am": 3,
        "pr": 5,
        "pc": 4,
        "c": "Costela desfiando e soltando do osso. O smoke ring é real!",
    },
    {
        "rest": 13,
        "user": 6,
        "at": 3,
        "am": 3,
        "pr": 5,
        "pc": 4,
        "c": "Brisket excelente, ambiente simples. O coleslaw equilibra bem.",
    },
    # Brasserie Du Soleil (14)
    {
        "rest": 14,
        "user": 1,
        "at": 5,
        "am": 5,
        "pr": 4,
        "pc": 4,
        "c": "Onion soup autêntica e crepe suzette flamejado na mesa. Encantador.",
    },
    {
        "rest": 14,
        "user": 4,
        "at": 4,
        "am": 5,
        "pr": 4,
        "pc": 4,
        "c": "Boa relação qualidade-preço para culinária francesa. Confit de canard impecável.",
    },
    # Green Kitchen (15)
    {
        "rest": 15,
        "user": 3,
        "at": 4,
        "am": 3,
        "pr": 4,
        "pc": 5,
        "c": "Bowl de proteína vegetal por R$25. Impossível achar mais barato e gostoso.",
    },
    {
        "rest": 15,
        "user": 7,
        "at": 4,
        "am": 3,
        "pr": 3,
        "pc": 5,
        "c": "Bom custo-benefício. O hamburguer de grão-de-bico ressecou um pouco.",
    },
    # Osteria Porto Fino (16)
    {
        "rest": 16,
        "user": 0,
        "at": 5,
        "am": 4,
        "pr": 5,
        "pc": 4,
        "c": "Risoto de lulas al dente e cremoso. Vinho branco gelado na taça harmonizou.",
    },
    {
        "rest": 16,
        "user": 5,
        "at": 4,
        "am": 4,
        "pr": 4,
        "pc": 3,
        "c": "Polvo bem grelhado. Caro mas ambiente agradável e com boa vista.",
    },
    # Al Fanar (17)
    {
        "rest": 17,
        "user": 2,
        "at": 5,
        "am": 4,
        "pr": 5,
        "pc": 4,
        "c": "Quibe assado irresistível e esfiha de ricota fechada a milanesa. Top.",
    },
    {
        "rest": 17,
        "user": 6,
        "at": 4,
        "am": 4,
        "pr": 4,
        "pc": 4,
        "c": "Charuto de folha de uva recheado com arroz e carne moída. Delicioso.",
    },
    # Boteco do Zé (18)
    {
        "rest": 18,
        "user": 1,
        "at": 4,
        "am": 4,
        "pr": 4,
        "pc": 5,
        "c": "Coxinha crocante e bolinho de bacalhau irresistíveis. Chopp bem tirado.",
    },
    {
        "rest": 18,
        "user": 3,
        "at": 3,
        "am": 4,
        "pr": 3,
        "pc": 5,
        "c": "Bom petisco, bar animado. Polenta frita a melhor da região.",
    },
    {
        "rest": 18,
        "user": 7,
        "at": 4,
        "am": 5,
        "pr": 4,
        "pc": 5,
        "c": "Vila Madalena tem muitos botecos mas esse tem o melhor ambiente e preço.",
    },
    # Empório da Massa (19)
    {
        "rest": 19,
        "user": 4,
        "at": 4,
        "am": 3,
        "pr": 4,
        "pc": 5,
        "c": "Massa fresca por quilo é ótima pedida no almoço. Rápido e saboroso.",
    },
    {
        "rest": 19,
        "user": 5,
        "at": 3,
        "am": 2,
        "pr": 4,
        "pc": 5,
        "c": "Bom para o dia a dia. Ambiente sem pretensão mas comida honesta.",
    },
    {
        "rest": 19,
        "user": 6,
        "at": 4,
        "am": 3,
        "pr": 5,
        "pc": 5,
        "c": "Ravioli de ricota e espinafre fresquíssimo. Melhor custo da região.",
    },
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
                comentario=av_dados.get("c"),
            )
            av.calcular_media()
            db.session.add(av)

        db.session.commit()

        u_total = Usuario.query.count()
        r_total = Restaurante.query.count()
        av_total = Avaliacao.query.count()
        print(
            f"\nBanco populado: {u_total} usuários · {r_total} restaurantes · {av_total} avaliações"
        )
        print("\nContas de teste (senha: senha123):")
        for u in USUARIOS:
            print(f"  {u['email']}")


if __name__ == "__main__":
    seed()
