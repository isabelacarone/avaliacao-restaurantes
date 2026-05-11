# Implementações — Mesa Certa

Registro das funcionalidades adicionadas após a entrega inicial do backend.

---

## Sprint 2

### 1. Página de Perfil do Usuário (RF09)

**Arquivos modificados:**

| Arquivo | Alteração |
|---|---|
| `app/auth/routes.py` | Nova rota `GET /perfil` com `@login_required` |
| `app/templates/auth/perfil.html` | Template criado do zero |
| `app/templates/base.html` | Link "Meu perfil" na navbar e no dropdown |

**Comportamento:**
- Rota protegida: redireciona para `/login` se não autenticado
- Exibe avatar com iniciais, e-mail, data de cadastro e contagem de avaliações
- Lista avaliações ordenadas da mais recente para a mais antiga, com notas por critério
- Estado vazio com CTA para explorar restaurantes

---

### 2. Paginação na Listagem de Restaurantes

**Arquivos modificados:**

| Arquivo | Alteração |
|---|---|
| `app/restaurantes/routes.py` | `query.paginate(page, per_page=12)` substituindo `.all()` |
| `app/templates/restaurantes/listar.html` | Controles de navegação com `iter_pages()` |

**Parâmetro adicionado a `GET /`:**

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `page` | integer | `1` | Número da página atual |

---

### 3. Bloqueio de Avaliação Duplicada

**Arquivo modificado:** `app/avaliacoes/routes.py`

Antes de renderizar o formulário, verifica se `Avaliacao` com `(usuario_id, restaurante_id)` já existe. Se existir: flash `warning` + redirect para o detalhe do restaurante.

---

### 4. Flask-Migrate — Migrações de Banco de Dados

**Arquivos modificados:**

| Arquivo | Alteração |
|---|---|
| `pyproject.toml` | `flask-migrate>=4.0.0` adicionado |
| `app/__init__.py` | `Migrate` inicializado; `db.create_all()` removido |
| `migrations/` | Pasta criada pelo `flask db init` |
| `migrations/versions/b5a7b14cbacf_initial_schema.py` | Migration inicial gerada |

**Comandos executados:**
```bash
uv add flask-migrate
FLASK_APP=run.py uv run flask db init
FLASK_APP=run.py uv run flask db migrate -m "initial schema"
FLASK_APP=run.py uv run flask db upgrade
```

---

## Sprint 3

### 5. Preview de Imagem no Upload

**Arquivo modificado:** `app/templates/avaliacoes/nova.html`

Adicionado elemento `<img id="foto-preview">` e listener JavaScript que lê o arquivo com `FileReader` e atualiza o preview antes do envio. Mesmo padrão replicado em `avaliacoes/editar.html`.

---

### 6. Edição e Exclusão de Avaliações

**Arquivos modificados/criados:**

| Arquivo | Alteração |
|---|---|
| `app/avaliacoes/routes.py` | Novas rotas `editar` e `excluir`; helpers `_salvar_foto` e `_excluir_foto` extraídos |
| `app/templates/avaliacoes/editar.html` | Template criado |
| `app/templates/auth/perfil.html` | Botões "Editar" e "Excluir" adicionados em cada card |

**Rotas adicionadas:**

| Método | URL | Função | Restrição |
|---|---|---|---|
| GET/POST | `/avaliacoes/<id>/editar` | `avaliacoes.editar` | Autor da avaliação |
| POST | `/avaliacoes/<id>/excluir` | `avaliacoes.excluir` | Autor da avaliação |

**Comportamento:**
- Tentativa de editar/excluir avaliação alheia retorna `403`
- Exclusão remove o arquivo de foto do disco (se houver)
- Edição preserva a foto atual se nenhuma nova for enviada
- Exclusão via `POST` (formulário com token CSRF) — impede exclusão acidental por GET

---

### 7. Ordenação da Listagem

**Arquivos modificados:**

| Arquivo | Alteração |
|---|---|
| `app/restaurantes/routes.py` | Parâmetro `order` + função `_ordem_clause()` |
| `app/templates/restaurantes/listar.html` | Botões de ordenação na barra de filtros |

**Parâmetro adicionado a `GET /`:**

| Parâmetro | Valores | Padrão | Descrição |
|---|---|---|---|
| `order` | `recentes`, `nota`, `avaliacoes` | `recentes` | Critério de ordenação |

A ordenação é preservada ao navegar entre páginas e ao aplicar filtros.

---

### 8. Tratamento de Erro 413 (Upload Muito Grande)

**Arquivo modificado:** `app/__init__.py`

Adicionado `@app.errorhandler(RequestEntityTooLarge)` que exibe flash `danger` e redireciona para a página anterior quando o arquivo enviado excede 2 MB.

---

### 9. Gitignore e .env.example

**Arquivos modificados/criados:**

| Arquivo | Alteração |
|---|---|
| `.gitignore` | Corrigido: removido `docs/` (deve ser versionado); `instance/` substitui `*.db`; `**/__pycache__/` recursivo; removido padrão duplicado `mesa_certa.egg-info/` |
| `.env.example` | Criado — template documentando as variáveis de ambiente necessárias |

**Problemas corrigidos no .gitignore anterior:**
- `docs/` estava ignorada — toda a documentação ficava fora do repositório
- `*.db` ignorava arquivos de banco em qualquer pasta; substituído por `instance/`
- `__pycache__/` não pegava subpastas; corrigido para `**/__pycache__/`
- `migrations/` não estava listada como ignorada (correto — deve ser versionada)

---

## Sprint 4

### 10. Paginação de Avaliações no Detalhe do Restaurante

**Arquivos modificados:**

| Arquivo | Alteração |
|---|---|
| `app/restaurantes/routes.py` | Detalhe agora pagina as avaliações (8 por página); métricas globais calculadas sobre `todas` (não apenas a página) |
| `app/templates/restaurantes/detalhe.html` | Usa `avaliacoes_todas` para barras de critério; controles de paginação adicionados |

---

### 11. Botões Editar/Excluir no Detalhe do Restaurante

**Arquivo modificado:** `app/templates/restaurantes/detalhe.html`

Cada card de avaliação exibe botões "Editar" e "Excluir" condicionados a `current_user.id == av.usuario_id`. O CSRF é gerenciado via `form_csrf = FlaskForm()` passado pela rota.

---

### 12. Testes Automatizados

**Arquivos criados:**

| Arquivo | Descrição |
|---|---|
| `tests/conftest.py` | Fixtures com isolamento total por teste via `app_ctx` function-scoped |
| `tests/test_auth.py` | 7 testes: cadastro, e-mail duplicado, login correto/errado, perfil com/sem login, logout |
| `tests/test_restaurantes.py` | 7 testes: listagem pública, detalhe, 404, novo sem login, novo autenticado, filtros |
| `tests/test_avaliacoes.py` | 7 testes: nova sem login, criação, duplicata, edição, exclusão, 403 para não-autor, 404 |

**Total:** 21 testes, todos passando.

**Detalhe técnico — isolamento de `flask.g` e engine:**

1. **`flask.g` é app-context-scoped (Flask 2.2+):** se o `app` fixture mantivesse o contexto ativo entre testes, `flask.g` seria compartilhado e o `current_user` cacheado pelo Flask-Login vazaria de um teste para o próximo. A fixture `app_ctx` (function-scoped) empurra e pop um contexto limpo por teste.

2. **Flask-SQLAlchemy 3.x cria a engine em `init_app()`**, não de forma lazy. Por isso, alterar `app.config["SQLALCHEMY_DATABASE_URI"]` após `create_app()` não tem efeito. A solução adotada é o padrão Flask: `create_app(test_config={...})` injeta a config ANTES de `db.init_app(app)`.

3. **`Config.SQLALCHEMY_DATABASE_URI` é avaliada em import-time:** como `conftest.py` importa `from app import create_app, db` durante a coleta de testes (antes que qualquer fixture rode), a classe `Config` já foi definida com o URI padrão do banco real. Por isso a injeção via `test_config` dentro de `create_app()` é a única abordagem que funciona.

**Executar:**
```bash
uv run pytest tests/ -v
```

---

### 13. Seed do Banco de Dados

**Arquivo criado:** `seed.py`

Script idempotente que popula o banco com dados realistas para desenvolvimento e testes manuais.

**Dados inseridos:**
- 4 usuários (senha: `senha123`)
- 10 restaurantes em categorias variadas (italiana, japonesa, brasileira, mexicana, americana, francesa, vegana, frutos do mar, árabe)
- 23 avaliações com comentários e notas diversas

**Executar:**
```bash
# 1. Garantir que o banco está criado
FLASK_APP=run.py uv run flask db upgrade

# 2. Popular
uv run python seed.py
```

---

### 14. Atualização de uv e pyproject.toml

| Item | Antes | Depois |
|---|---|---|
| uv | 0.11.9 | 0.11.12 |
| `idna` (dep. transitiva) | 3.13 | 3.14 |
| `[project.optional-dependencies]` | `ruff` isolado | Unificado em `[dependency-groups]` |
| `pytest` + `pytest-flask` | — | Adicionados ao grupo `dev` |
| `[tool.pytest.ini_options]` | — | `testpaths`, `pythonpath` configurados |
| `[tool.ruff.lint.per-file-ignores]` | — | `seed.py` e `tests/**` isentos de E501 |
| Versões mínimas | `flask>=3.0.0`, `werkzeug>=3.0.0` | Atualizadas para `>=3.1.0` |

---

---

## Sprint 5

### 15. Correção de datetime.utcnow() Depreciado

**Arquivo modificado:** `app/models.py`

`datetime.utcnow` foi removido em favor de datetimes timezone-aware (PEP 615 / Python 3.12).

```python
# Antes (gera DeprecationWarning no Python 3.12)
from datetime import datetime
criado_em = db.Column(db.DateTime, default=datetime.utcnow)

# Depois
from datetime import datetime, timezone
criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

Todos os três modelos (`Usuario`, `Restaurante`, `Avaliacao`) foram corrigidos. Não requer migration — apenas o default Python muda, não o schema do banco.

---

### 16. Gitignore — `.pytest_cache/` e `*_test.db`

**Arquivo modificado:** `.gitignore`

Adicionados:
- `.pytest_cache/` — diretório gerado pelo pytest com cache de execuções
- `*_test.db` — arquivos SQLite temporários criados pela suite de testes

---

### 17. Atualização do README — Comandos uv modernos

**Arquivo modificado:** `readme.markdown`

Seção "Instalar dependências" atualizada de `uv pip install -e ".[dev]"` para `uv sync`, refletindo a migração para `[dependency-groups]` no `pyproject.toml`. Adicionados comandos `uv add`, `uv add --dev` e `uv lock --upgrade`.

---

### 18. `create_app(test_config)` — padrão Flask para testes

**Arquivo modificado:** `app/__init__.py`

A função `create_app()` agora aceita um parâmetro opcional `test_config: dict | None`. Quando fornecido, as configurações são aplicadas ao `app.config` ANTES de `db.init_app(app)`, garantindo que Flask-SQLAlchemy 3.x crie a engine com a URI correta para testes.

Isso resolve o vazamento para o banco de desenvolvimento que ocorria porque `Config.SQLALCHEMY_DATABASE_URI` é avaliado em import-time e Flask-SQLAlchemy cria engines em `init_app()`, não de forma lazy.

---

---

## Sprint 6

### 19. Validadores WTForms Customizados (`app/validators.py`)

**Arquivo criado:** `app/validators.py`

| Classe | Campo | O que valida |
|---|---|---|
| `UniqueEmail` | `CadastroForm.email` | E-mail já existe para outro usuário |
| `UniqueNomeRestaurante` | `RestauranteForm.nome` | Nome já existe para outro restaurante (case-insensitive) |

Ambos aceitam `exclude_id` para suportar edição futura (ignora o próprio registro).

A verificação manual de e-mail duplicado foi **removida** de `app/auth/routes.py` — o erro agora aparece inline no formulário de cadastro, sem redirecionar.

---

### 20. Módulo JS de Validação Client-Side (`app/static/js/validacao.js`)

**Arquivo criado:** `app/static/js/validacao.js`

Módulo IIFE que adiciona validação imediata aos formulários via atributos `data-v`:

| Atributo | Descrição |
|---|---|
| `data-v="required"` | Campo não pode estar vazio |
| `data-v="email"` | Formato de e-mail validado por regex |
| `data-v="confirm"` + `data-v-confirm="id"` | Valor deve coincidir com outro campo |
| `data-v-min="N"` | Comprimento mínimo |
| `data-v-max="N"` | Comprimento máximo |
| `data-v-label="Texto"` | Nome do campo nas mensagens de erro |

**Comportamento:**
- Valida no `submit` (bloqueia envio se inválido)
- Valida no `blur` (feedback ao sair do campo)
- Limpa erro no `input` (ao digitar)
- Mostra ícone ✕ vermelho nos erros; borda verde nos campos válidos

Carregado globalmente via `base.html`. Inicializado por formulário:
```javascript
Validacao.init('form-cadastro');
```

---

### 21. Modal de Confirmação de Exclusão com Nome do Item

**Arquivos modificados:**

| Arquivo | Alteração |
|---|---|
| `app/templates/base.html` | Modal Bootstrap reutilizável + `<script>` para `validacao.js` |
| `app/templates/auth/perfil.html` | Botão de exclusão usa `confirmarExclusao(formId, nome, tipo)` |
| `app/templates/restaurantes/detalhe.html` | Idem |
| `app/templates/avaliacoes/editar.html` | Idem |

**Assinatura:**
```javascript
confirmarExclusao(formId, nomeItem, tipo = "item")
```

O modal exibe:
- Ícone 🗑️
- Título: "Excluir [tipo]?"
- Mensagem: "Tem certeza que deseja excluir **[nomeItem]**? Esta ação não pode ser desfeita."
- Botões: Cancelar / Excluir (vermelho)

A função JS antiga (`confirm()` nativo do browser) foi **removida** dos três templates.

---

### 22. Testes e Cobertura

**Arquivos modificados:** `tests/test_auth.py`, `tests/test_restaurantes.py`

4 novos testes adicionados:
- `test_cadastro_email_duplicado_exibe_erro_inline` — `UniqueEmail` retorna 200 com erro inline
- `test_cadastro_email_invalido_exibe_erro` — e-mail sem formato válido é rejeitado
- `test_cadastro_campo_vazio_rejeitado` — formulário com campos vazios não cria usuário
- `test_novo_restaurante_nome_duplicado_exibe_erro` — `UniqueNomeRestaurante` impede duplicata
- `test_novo_restaurante_campo_vazio_rejeitado` — campos obrigatórios vazios bloqueiam criação

**Total:** 25 testes passando. **Cobertura: 88%.**

```bash
uv run pytest tests/ --cov=app --cov-report=term-missing
```

---

### 23. uv e pyproject.toml (Sprint 6)

| Item | Antes | Depois |
|---|---|---|
| uv | 0.11.12 | 0.11.13 |
| `pytest-cov` | — | 7.1.0 |
| `coverage` | — | 7.14.0 (transitiva) |
| `.gitignore` | `.env.*` ignorava `.env.example` | Adicionado `!.env.example` como exceção |

---

## Resumo de dependências adicionadas

| Pacote | Versão | Motivo |
|---|---|---|
| `flask-migrate` | 4.1.0 | Migrações de schema com Alembic |
| `alembic` | 1.18.4 | Dependência transitiva |
| `mako` | 1.3.12 | Dependência transitiva |
| `pytest` | 9.0.3 | Suite de testes |
| `pytest-flask` | 1.3.0 | Integração Flask + pytest |
| `pytest-cov` | 7.1.0 | Cobertura de testes |
| `coverage` | 7.14.0 | Dependência transitiva do pytest-cov |
