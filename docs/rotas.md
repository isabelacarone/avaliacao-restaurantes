# Mapa de Rotas — Mesa Certa

## Blueprint `auth` — Autenticação

| Método | URL | Função | Autenticação |
|---|---|---|---|
| GET/POST | `/login` | `auth.login` | Pública |
| GET/POST | `/cadastro` | `auth.cadastro` | Pública |
| GET | `/logout` | `auth.logout` | `@login_required` |
| GET | `/perfil` | `auth.perfil` | `@login_required` |

---

## Blueprint `restaurantes` — Restaurantes

| Método | URL | Função | Autenticação |
|---|---|---|---|
| GET | `/` | `restaurantes.listar` | Pública |
| GET | `/restaurantes/<int:id>` | `restaurantes.detalhe` | Pública |
| GET/POST | `/restaurantes/novo` | `restaurantes.novo` | `@login_required` |

### Parâmetros de query em `/restaurantes/<id>`

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `page` | integer | `1` | Página de avaliações (8 por página) |

### Parâmetros de query em `/`

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `q` | string | `""` | Busca parcial por nome (ilike) |
| `categoria` | string | `""` | Filtro exato por categoria |
| `faixa_preco` | string | `""` | Filtro exato por faixa de preço |
| `page` | integer | `1` | Página atual (12 restaurantes por página) |
| `order` | string | `recentes` | Ordenação: `recentes`, `nota`, `avaliacoes` |

---

## Blueprint `avaliacoes` — Avaliações

| Método | URL | Função | Autenticação |
|---|---|---|---|
| GET/POST | `/avaliacoes/nova/<int:restaurante_id>` | `avaliacoes.nova` | `@login_required` |
| GET/POST | `/avaliacoes/<int:id>/editar` | `avaliacoes.editar` | Autor da avaliação |
| POST | `/avaliacoes/<int:id>/excluir` | `avaliacoes.excluir` | Autor da avaliação |

---

## Fluxos principais

### Cadastro de usuário
```
GET /cadastro → exibe formulário
POST /cadastro → valida → cria Usuario → flash → redirect /login
```

### Login
```
GET /login → exibe formulário
POST /login → valida credenciais → login_user() → redirect /
```

### Cadastrar restaurante
```
GET /restaurantes/novo → (requer login) → exibe formulário
POST /restaurantes/novo → valida → cria Restaurante → redirect /restaurantes/<id>
```

### Avaliar restaurante
```
GET /avaliacoes/nova/<id> → (requer login)
                          → checa duplicata (usuario_id + restaurante_id)
                          → se já avaliou: flash warning + redirect /restaurantes/<id>
                          → exibe formulário
POST /avaliacoes/nova/<id> → valida → salva foto (se houver)
                           → calcular_media() → cria Avaliacao
                           → redirect /restaurantes/<id>
```

### Perfil do usuário
```
GET /perfil → (requer login) → lista avaliações do current_user
           → renderiza auth/perfil.html
```
