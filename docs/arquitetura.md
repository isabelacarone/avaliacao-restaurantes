# Arquitetura da Aplicação — Mesa Certa

## Visão Geral

Mesa Certa segue o padrão **MVC** (Model-View-Controller) implementado com **Flask Blueprints**, separando as responsabilidades em módulos independentes.

---

## Estrutura de Pastas

```
avaliacao-restaurantes/
├── app/
│   ├── __init__.py          # Application Factory — create_app(test_config)
│   ├── config.py            # Configurações centralizadas
│   ├── models.py            # Modelos do banco de dados (SQLAlchemy)
│   ├── forms.py             # Formulários WTForms com validação
│   ├── validators.py        # Validadores customizados (UniqueEmail, UniqueNomeRestaurante)
│   ├── auth/                # Blueprint: autenticação
│   │   ├── __init__.py
│   │   └── routes.py        # /login, /cadastro, /logout, /perfil
│   ├── restaurantes/        # Blueprint: restaurantes
│   │   ├── __init__.py
│   │   └── routes.py        # /, /restaurantes/<id>, /restaurantes/novo
│   ├── avaliacoes/          # Blueprint: avaliações
│   │   ├── __init__.py
│   │   └── routes.py        # /avaliacoes/nova, /editar, /excluir
│   ├── static/
│   │   ├── js/
│   │   │   └── validacao.js # Validação client-side + modal de confirmação
│   │   └── uploads/         # Fotos enviadas pelos usuários
│   └── templates/
│       ├── base.html        # Layout base — modal de exclusão + validacao.js
│       ├── auth/
│       │   ├── login.html
│       │   ├── cadastro.html  # Validação JS (data-v)
│       │   └── perfil.html
│       ├── restaurantes/
│       │   └── novo.html    # Validação JS (data-v)
│       └── avaliacoes/
│           ├── nova.html    # Formulário + preview de foto
│           └── editar.html  # Edição com preview e exclusão
├── tests/                   # Suite de testes automatizados
│   ├── conftest.py          # Fixtures compartilhadas
│   ├── test_auth.py
│   ├── test_restaurantes.py
│   └── test_avaliacoes.py
├── seed.py                  # Popula o banco com dados de desenvolvimento
├── migrations/              # Alembic — histórico de schema
│   ├── env.py
│   └── versions/
│       └── b5a7b14cbacf_initial_schema.py
├── docs/                    # Documentação do projeto
├── run.py                   # Ponto de entrada
├── pyproject.toml           # Metadados e dependências
└── uv.lock                  # Lockfile de dependências
```

---

## Camadas da Aplicação

### Model (app/models.py)

Três entidades principais conectadas por chaves estrangeiras:

```
Usuario ──< Avaliacao >── Restaurante
```

| Modelo | Campos principais |
|---|---|
| `Usuario` | id, nome, email, senha_hash, criado_em |
| `Restaurante` | id, nome, categoria, faixa_preco, endereco, descricao |
| `Avaliacao` | id, usuario_id, restaurante_id, 4 notas, media_calculada, comentario, foto_path |

### View (templates/)

Templates Jinja2 que herdam de `base.html`. Todos usam `{% raw %}{% extends 'base.html' %}{% endraw %}`.

### Controller (blueprints/)

| Blueprint | Prefixo | Responsabilidade |
|---|---|---|
| `auth_bp` | — | Login, cadastro, logout, perfil |
| `restaurantes_bp` | — | CRUD de restaurantes, filtros, paginação, ordenação |
| `avaliacoes_bp` | — | CRUD de avaliações, upload, bloqueio de duplicata |

---

## Fluxo de uma Requisição

```
Navegador → run.py → create_app() → Blueprint → Route function
                                                      ↓
                                               Form validation
                                                      ↓
                                           Model (db.session)
                                                      ↓
                                              Template render
                                                      ↓
                                            Resposta HTML
```

---

## Banco de Dados

- **SQLite** via Flask-SQLAlchemy
- Arquivo em `instance/mesa_certa.db`
- Schema gerenciado pelo **Flask-Migrate** (Alembic) — `db.create_all()` foi removido
- Senhas armazenadas com **Werkzeug PBKDF2** (nunca em texto plano)

### Workflow de migrations

```bash
# Após alterar models.py:
FLASK_APP=run.py uv run flask db migrate -m "descrição"
FLASK_APP=run.py uv run flask db upgrade
```

---

## Segurança

| Mecanismo | Implementação |
|---|---|
| Hash de senhas | `werkzeug.security.generate_password_hash` |
| Proteção CSRF | Flask-WTF (token em todos os formulários) |
| Autenticação de sessão | Flask-Login (`@login_required`) |
| Validação de upload | Extensões permitidas + limite de 2 MB |
| Nomes de arquivo | `uuid4()` — evita path traversal |
