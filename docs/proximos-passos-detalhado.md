# Mesa Certa — Resumo Técnico

## Visão Geral

Plataforma web de avaliação de restaurantes construída com **Flask 3**, seguindo o padrão **MVC com Blueprints**. Desenvolvida em 6 sprints iterativas, partindo de um backend básico até uma aplicação completa com testes automatizados, validação client/server-side e documentação técnica.

---

## Stack e Ferramentas

| Camada | Tecnologia |
|---|---|
| Framework web | Flask 3.x (Application Factory) |
| ORM | Flask-SQLAlchemy 3.x |
| Migrações | Flask-Migrate (Alembic) |
| Autenticação | Flask-Login |
| Formulários | Flask-WTF + WTForms |
| Frontend | Bootstrap 5 + Jinja2 |
| Banco de dados | SQLite (dev) |
| Hashing de senhas | Werkzeug PBKDF2 |
| Testes | pytest + pytest-flask + pytest-cov |
| Linter | ruff |
| Gerenciador de pacotes | uv 0.11.13 |

---

## Histórico de Sprints

### Sprint 2 — Funcionalidades Base
- **RF09**: Página de perfil (`GET /perfil`) com avatar por iniciais, contagem de avaliações e histórico
- **Paginação** na listagem de restaurantes (12 por página, parâmetro `?page=N`)
- **Bloqueio de avaliação duplicada**: verifica `(usuario_id, restaurante_id)` antes de exibir o formulário
- **Flask-Migrate**: substituiu `db.create_all()` pelo workflow Alembic; migration inicial gerada

### Sprint 3 — Upload e CRUD de Avaliações
- **Preview de imagem** antes do upload via `FileReader` JavaScript
- **Edição e exclusão** de avaliações próprias (`GET/POST /avaliacoes/<id>/editar`, `POST /avaliacoes/<id>/excluir`)
  - 403 para tentativas por não-autores
  - Exclusão remove arquivo de foto do disco
  - Edição preserva foto atual se nenhuma nova for enviada
- **Ordenação da listagem**: parâmetro `?order=recentes|nota|avaliacoes`, preservado na paginação e filtros
- **Handler 413**: flash `danger` + redirect para página anterior quando upload excede 2 MB
- **`.gitignore`** corrigido (bug: `docs/` estava sendo ignorada); **`.env.example`** criado

### Sprint 4 — Detalhe do Restaurante e Testes
- **Paginação de avaliações** no detalhe do restaurante (8 por página)
  - Métricas calculadas sobre `avaliacoes_todas` (todas), não apenas a página atual
- **Botões editar/excluir** no detalhe, condicionados a `current_user.id == av.usuario_id`
  - CSRF gerenciado via `form_csrf = FlaskForm()` passado pela rota
- **Testes automatizados**: 21 testes cobrindo `auth`, `restaurantes` e `avaliacoes`
- **Seed do banco**: `seed.py` idempotente com 4 usuários, 10 restaurantes, 23 avaliações

### Sprint 5 — Qualidade e Isolamento de Testes
- **Correção de `datetime.utcnow()`**: substituído por `lambda: datetime.now(timezone.utc)` nos três modelos (PEP 615 / Python 3.12)
- **`create_app(test_config)`**: injeção de configuração antes de `db.init_app(app)`, resolvendo o vazamento para o banco real
- **`.gitignore`**: adicionados `.pytest_cache/` e `*_test.db`
- README atualizado com `uv sync`, `uv add`, `uv lock --upgrade`

### Sprint 6 — Validação e UX de Exclusão
- **`app/validators.py`**: validadores WTForms customizados
  - `UniqueEmail`: e-mail já cadastrado; suporta `exclude_id` para edição futura
  - `UniqueNomeRestaurante`: nome duplicado (case-insensitive); suporta `exclude_id`
  - Import lazy (`from app.models import ...` dentro de `__call__`) evita circular imports
- **`app/static/js/validacao.js`**: módulo IIFE `Validacao` com sistema declarativo `data-v`
  - Atributos: `data-v="required"`, `data-v="email"`, `data-v="confirm"`, `data-v-min`, `data-v-max`, `data-v-label`
  - Valida no `submit` (bloqueia), no `blur` (feedback imediato), limpa no `input`
- **Modal de confirmação de exclusão** (`confirmarExclusao(formId, nomeItem, tipo)`)
  - Bootstrap 5 reutilizável em `base.html`
  - Exibe nome do item a ser excluído; substituiu `confirm()` nativo nos três templates
- **25 testes passando; cobertura 88%**

---

## Decisões Técnicas Relevantes

### Isolamento de Testes (problema mais complexo)

Três comportamentos do Python/Flask interagem de forma não-óbvia:

1. **`Config.SQLALCHEMY_DATABASE_URI` é avaliado em import-time** — alterar variável de ambiente antes de `create_app()` não tem efeito porque `conftest.py` importa `create_app` durante a coleta de testes, quando a classe `Config` já foi definida.

2. **Flask-SQLAlchemy 3.x cria engines em `init_app()`**, não de forma lazy — alterar `app.config["SQLALCHEMY_DATABASE_URI"]` após `create_app()` não afeta a engine já criada.

3. **Flask 2.2+ moveu `flask.g` para o app-context** — um contexto ativo durante toda a sessão de testes faz `current_user` do Flask-Login vazar entre testes.

**Solução final**: padrão `create_app(test_config=dict)` — injeta a config ANTES de `db.init_app(app)`. Combinado com:
- Fixture `app_ctx` de escopo `function` (push/pop de contexto por teste)
- Fixture `limpar_banco` com `autouse=True` (DELETE em todas as tabelas antes de cada teste)
- SQLite em arquivo temporário (`tempfile.mkstemp`) em vez de `:memory:` (permite múltiplas conexões)

### CSRF em Templates de Teste

`csrf_token()` Jinja global requer `CSRFProtect`, não apenas `WTF_CSRF_ENABLED`. Solução: rotas passam `form_csrf=FlaskForm()` e templates usam `{{ form_csrf.hidden_tag() }}`.

### Import Lazy em Validators

`app/validators.py` importa modelos dentro de `__call__()` para evitar circular imports (`app/models.py` → `app/forms.py` → `app/validators.py` → `app/models.py`).

---

## Estado Atual

```
Testes:    25/25 passando
Cobertura: 88%
Ruff:      ✓ sem erros
uv:        0.11.13
Seed:      5 usuários · 10 restaurantes · 23 avaliações
```

### Cobertura por módulo (aproximada)

| Módulo | Cobertura |
|---|---|
| `app/auth/routes.py` | ~95% |
| `app/restaurantes/routes.py` | ~90% |
| `app/avaliacoes/routes.py` | ~72% |
| `app/models.py` | ~85% |
| `app/validators.py` | ~100% |

---

## Próximos Passos

### Ampliar cobertura de testes (88% → 95%+)

Linhas não cobertas prioritárias:

- `app/avaliacoes/routes.py` — helpers `_salvar_foto` e `_excluir_foto`, fluxo de edição com nova foto
- `app/models.py` — propriedades `media_geral` e `total_avaliacoes`

```bash
uv run pytest tests/ --cov=app --cov-report=term-missing
```

### Preparação para produção

```bash
# Gerar SECRET_KEY segura
python -c "import secrets; print(secrets.token_hex(32))"

# Copiar template de ambiente
cp .env.example .env
```

- Trocar `DATABASE_URL` de SQLite para PostgreSQL
- Configurar `client_max_body_size 2m;` no Nginx (além do `MAX_CONTENT_LENGTH` do Flask)
- Variável `FLASK_ENV=production` desativa o modo debug

### Funcionalidades futuras (não priorizadas)

| Item | Complexidade |
|---|---|
| Edição do perfil do usuário (nome, senha) | Baixa |
| Upload de foto de perfil / avatar real | Média |
| Avaliação de restaurante pelo dono | Média |
| Ordenação de avaliações no detalhe | Baixa |
| Sistema de favoritos | Média |
| Deploy com Docker + Gunicorn + Nginx | Alta |

---

## Comandos de Referência Rápida

```bash
# Rodar a aplicação
uv run python run.py

# Aplicar migrações
FLASK_APP=run.py uv run flask db upgrade

# Após alterar models.py
FLASK_APP=run.py uv run flask db migrate -m "descrição"
FLASK_APP=run.py uv run flask db upgrade

# Popular banco de desenvolvimento
uv run python seed.py

# Testes
uv run pytest tests/ -v
uv run pytest tests/ --cov=app --cov-report=term-missing

# Linter
uv run ruff check app/ run.py
uv run ruff check --fix app/ run.py
```
