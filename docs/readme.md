
## Estrutura do projeto

```
avaliacao-restaurantes/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── config.py            # Configurações
│   ├── models.py            # Usuario, Restaurante, Avaliacao
│   ├── forms.py             # Formulários WTForms
│   ├── auth/                # Blueprint: login, cadastro, logout, perfil
│   ├── restaurantes/        # Blueprint: listagem (paginada), detalhe, cadastro
│   ├── avaliacoes/          # Blueprint: nova avaliação (bloqueio de duplicata)
│   ├── static/uploads/      # Fotos enviadas pelos usuários
│   └── templates/           # Templates Jinja2 (Bootstrap 5)
│       ├── auth/perfil.html # Perfil do usuário (RF09)
│       └── ...
├── migrations/              # Alembic — histórico de schema
│   └── versions/
├── docs/                    # Documentação técnica
│   ├── arquitetura.md
│   ├── modelos.md
│   ├── rotas.md
│   ├── implementacoes.md    # Registro das implementações (Sprint 2)
│   └── proximos-passos.md
├── run.py                   # Ponto de entrada
├── pyproject.toml           # Metadados e dependências
└── uv.lock                  # Lockfile (versões exatas)
```

---

## Funcionalidades implementadas

| ID | Descrição | Status |
|---|---|---|
| RF01 | Cadastro de usuários | ✅ |
| RF02 | Login/logout | ✅ |
| RF03 | Cadastro de restaurantes | ✅ |
| RF04 | Listagem de restaurantes com paginação | ✅ |
| RF05 | Avaliações com notas e comentários | ✅ |
| RF06 | Cálculo e exibição de nota média | ✅ |
| RF07 | Upload de foto na avaliação | ✅ |
| RF08 | Busca por nome, categoria e faixa de preço | ✅ |
| RF09 | Página de perfil do usuário | ✅ |
| — | Bloqueio de avaliação duplicada | ✅ |
| — | Migrações de schema com Flask-Migrate | ✅ |

---

## Requisitos Funcionais e Não Funcionais

### Requisitos Funcionais

| ID | Descrição | Prioridade |
|---|---|---|
| RF01 | Cadastro com nome, e-mail e senha | Alta |
| RF02 | Autenticação via e-mail e senha | Alta |
| RF03 | Cadastro de restaurantes | Alta |
| RF04 | Listagem de restaurantes | Alta |
| RF05 | Avaliações com notas e comentários | Alta |
| RF06 | Cálculo automático de nota média | Alta |
| RF07 | Upload de imagem na avaliação | Média |
| RF08 | Busca por nome, categoria e faixa de preço | Média |
| RF09 | Página de perfil do usuário | Baixa |

### Requisitos Não Funcionais

| ID | Descrição | Status |
|---|---|---|
| RNF01 | Interface responsiva (Bootstrap 5) | ✅ |
| RNF02 | Senhas com hash (Werkzeug PBKDF2) | ✅ |
| RNF03 | Padrão MVC com Flask Blueprints | ✅ |
| RNF04 | Páginas carregam em menos de 3 segundos | ✅ |
| RNF05 | Versionado no GitHub | ✅ |

