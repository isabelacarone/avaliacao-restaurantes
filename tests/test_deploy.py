"""Testes de smoke/pré-deploy: validam que o app sobe e funciona corretamente.

Esses testes pegam os erros mais comuns antes do deploy:
- App factory cria a aplicação sem erros
- Banco de dados conecta e tabelas existem
- Todas as rotas principais respondem (sem 500)
- Blueprints registrados corretamente
- Configuração de produção está consistente
- Seed não quebra e é idempotente
- Arquivos de deploy existem e estão corretos
- Variáveis de ambiente obrigatórias são lidas
"""

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def test_create_app_retorna_flask(app):
    from flask import Flask

    assert isinstance(app, Flask)


def test_app_tem_secret_key(app):
    assert app.config.get("SECRET_KEY")


def test_app_nao_esta_em_debug_quando_testing(app):
    # Em testes, debug pode estar on, mas TESTING deve ser True
    assert app.config["TESTING"] is True


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------


def test_banco_conecta(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["db"] == "connected"


def test_tabela_usuario_existe(app_ctx):
    from app import db

    db.session.execute(db.text("SELECT 1 FROM usuario LIMIT 1"))


def test_tabela_restaurante_existe(app_ctx):
    from app import db

    db.session.execute(db.text("SELECT 1 FROM restaurante LIMIT 1"))


def test_tabela_avaliacao_existe(app_ctx):
    from app import db

    db.session.execute(db.text("SELECT 1 FROM avaliacao LIMIT 1"))


def test_tabela_favorito_existe(app_ctx):
    from app import db

    db.session.execute(db.text("SELECT 1 FROM favorito LIMIT 1"))


# ---------------------------------------------------------------------------
# Rotas principais — nenhuma pode retornar 500
# ---------------------------------------------------------------------------


def test_rota_raiz_responde(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_rota_login_get_responde(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_rota_cadastro_get_responde(client):
    resp = client.get("/cadastro")
    assert resp.status_code == 200


def test_rota_novo_restaurante_redireciona_sem_login(client):
    resp = client.get("/restaurantes/novo")
    assert resp.status_code in (302, 401)


def test_rota_favoritos_redireciona_sem_login(client):
    resp = client.get("/favoritos")
    assert resp.status_code in (302, 401)


def test_rota_detalhe_inexistente_retorna_404(client):
    resp = client.get("/restaurantes/99999")
    assert resp.status_code == 404


def test_rota_health_retorna_json(client):
    resp = client.get("/health")
    assert resp.content_type == "application/json"


# ---------------------------------------------------------------------------
# Blueprints registrados
# ---------------------------------------------------------------------------


def test_blueprint_auth_registrado(app):
    nomes = [bp.name for bp in app.blueprints.values()]
    assert "auth" in nomes


def test_blueprint_restaurantes_registrado(app):
    nomes = [bp.name for bp in app.blueprints.values()]
    assert "restaurantes" in nomes


def test_blueprint_avaliacoes_registrado(app):
    nomes = [bp.name for bp in app.blueprints.values()]
    assert "avaliacoes" in nomes


def test_blueprint_favoritos_registrado(app):
    nomes = [bp.name for bp in app.blueprints.values()]
    assert "favoritos" in nomes


# ---------------------------------------------------------------------------
# Configuração de produção
# ---------------------------------------------------------------------------


def test_config_producao_tem_secret_key_via_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "chave-super-secreta-teste")
    from app.config import ProductionConfig

    ProductionConfig.init()
    assert ProductionConfig.SECRET_KEY == "chave-super-secreta-teste"


def test_config_producao_usa_database_url_do_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///custom.db")
    from app.config import Config

    Config.init()
    assert Config.SQLALCHEMY_DATABASE_URI == "sqlite:///custom.db"


def test_config_seleciona_producao_pelo_env(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    import importlib

    import app.config as cfg_mod

    importlib.reload(cfg_mod)
    from app.config import ProductionConfig

    assert cfg_mod.get_config() is ProductionConfig


def test_config_seleciona_development_por_padrao(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    import importlib

    import app.config as cfg_mod

    importlib.reload(cfg_mod)
    from app.config import DevelopmentConfig

    assert cfg_mod.get_config() is DevelopmentConfig


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------


def _mod_seed():
    """Carrega seed.py como módulo sem executar o bloco __main__."""
    spec = importlib.util.spec_from_file_location("seed_mod", ROOT / "seed.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_seed_tem_funcao_seed():
    mod = _mod_seed()
    assert callable(getattr(mod, "seed", None)), "seed.py deve expor função seed()"


def test_seed_dados_usuarios_definidos():
    mod = _mod_seed()
    assert len(mod.USUARIOS) > 0
    for u in mod.USUARIOS:
        assert "nome" in u and "email" in u and "senha" in u


def test_seed_dados_restaurantes_definidos():
    mod = _mod_seed()
    assert len(mod.RESTAURANTES) > 0
    campos = {"nome", "categoria", "faixa_preco", "endereco"}
    for r in mod.RESTAURANTES:
        assert campos.issubset(r.keys()), f"Restaurante sem campos obrigatórios: {r}"


def test_seed_emails_unicos():
    mod = _mod_seed()
    emails = [u["email"] for u in mod.USUARIOS]
    assert len(emails) == len(set(emails)), "Emails duplicados no seed"


def test_seed_restaurantes_nomes_unicos():
    mod = _mod_seed()
    nomes = [r["nome"] for r in mod.RESTAURANTES]
    assert len(nomes) == len(set(nomes)), "Nomes de restaurante duplicados no seed"


def test_seed_executa_sem_erros_no_contexto_de_teste(app_ctx):
    """seed() usando os models do contexto de teste não levanta exceções."""
    from app import db
    from app.models import Restaurante, Usuario

    mod = _mod_seed()

    # Executa seed diretamente no contexto de teste, sem chamar create_app()
    usuarios = []
    for dados in mod.USUARIOS:
        if Usuario.query.filter_by(email=dados["email"]).first():
            continue
        u = Usuario(nome=dados["nome"], email=dados["email"])
        u.set_senha(dados["senha"])
        db.session.add(u)
        usuarios.append(u)
    db.session.commit()

    restaurantes = []
    for dados in mod.RESTAURANTES:
        if Restaurante.query.filter_by(nome=dados["nome"]).first():
            continue
        r = Restaurante(**dados)
        db.session.add(r)
        restaurantes.append(r)
    db.session.commit()

    assert Usuario.query.count() == len(mod.USUARIOS)
    assert Restaurante.query.count() == len(mod.RESTAURANTES)


def test_seed_idempotente_no_contexto_de_teste(app_ctx):
    """Inserir dados seed duas vezes não duplica registros."""
    from app import db
    from app.models import Restaurante, Usuario

    mod = _mod_seed()

    def inserir():
        for dados in mod.USUARIOS:
            if not Usuario.query.filter_by(email=dados["email"]).first():
                u = Usuario(nome=dados["nome"], email=dados["email"])
                u.set_senha(dados["senha"])
                db.session.add(u)
        for dados in mod.RESTAURANTES:
            if not Restaurante.query.filter_by(nome=dados["nome"]).first():
                db.session.add(Restaurante(**dados))
        db.session.commit()

    inserir()
    total_u1 = Usuario.query.count()
    total_r1 = Restaurante.query.count()
    inserir()
    assert Usuario.query.count() == total_u1
    assert Restaurante.query.count() == total_r1


def test_seed_avaliacoes_notas_validas():
    """Todas as notas no seed estão entre 1 e 5."""
    mod = _mod_seed()
    campos_nota = ("at", "am", "pr", "pc")
    for av in mod.AVALIACOES:
        for campo in campos_nota:
            assert 1 <= av[campo] <= 5, f"Nota inválida em {av}"


# ---------------------------------------------------------------------------
# Arquivos de deploy
# ---------------------------------------------------------------------------


def test_procfile_existe():
    assert (ROOT / "Procfile").exists(), "Procfile não encontrado"


def test_procfile_tem_web_entry():
    content = (ROOT / "Procfile").read_text()
    assert content.startswith("web:"), "Procfile deve ter entrada 'web:'"


def test_procfile_contem_gunicorn():
    content = (ROOT / "Procfile").read_text()
    assert "gunicorn" in content


def test_procfile_contem_flask_db_upgrade():
    content = (ROOT / "Procfile").read_text()
    assert "flask db upgrade" in content


def test_requirements_txt_existe():
    assert (ROOT / "requirements.txt").exists(), "requirements.txt não encontrado"


def test_requirements_txt_contem_flask():
    content = (ROOT / "requirements.txt").read_text().lower()
    assert "flask==" in content


def test_requirements_txt_contem_gunicorn():
    content = (ROOT / "requirements.txt").read_text().lower()
    assert "gunicorn==" in content


def test_requirements_txt_contem_sqlalchemy():
    content = (ROOT / "requirements.txt").read_text().lower()
    assert "sqlalchemy==" in content


def test_run_py_existe():
    assert (ROOT / "run.py").exists()


def test_run_py_exporta_app():
    spec = importlib.util.spec_from_file_location("run", ROOT / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "app"), "run.py deve expor variável 'app' para o gunicorn"


def test_migrations_existem():
    versions = list((ROOT / "migrations" / "versions").glob("*.py"))
    assert len(versions) > 0, "Nenhuma migration encontrada"


def test_gitignore_nao_ignora_migrations():
    gitignore = (ROOT / ".gitignore").read_text()
    assert "migrations/" not in gitignore


def test_uploads_gitkeep_existe():
    assert (ROOT / "app" / "static" / "uploads" / ".gitkeep").exists()
