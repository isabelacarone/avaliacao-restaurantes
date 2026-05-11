# Modelos de Dados — Mesa Certa

## Diagrama ER (simplificado)

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│   Usuario   │       │   Avaliacao  │       │ Restaurante  │
├─────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)     │──┐    │ id (PK)      │  ┌──  │ id (PK)      │
│ nome        │  └──> │ usuario_id   │  │    │ nome         │
│ email       │       │ restaurante_id│<─┘    │ categoria    │
│ senha_hash  │       │ nota_atend.  │       │ faixa_preco  │
│ criado_em   │       │ nota_ambiente │       │ endereco     │
└─────────────┘       │ nota_prato   │       │ descricao    │
                      │ nota_preco   │       │ criado_em    │
                      │ media_calc.  │       └──────────────┘
                      │ comentario   │
                      │ foto_path    │
                      │ criado_em    │
                      └──────────────┘
```

---

## Classe `Usuario`

| Campo | Tipo | Restrição |
|---|---|---|
| id | Integer | PK, autoincrement |
| nome | String(120) | NOT NULL |
| email | String(150) | UNIQUE, NOT NULL |
| senha_hash | String(256) | NOT NULL |
| criado_em | DateTime | default=utcnow |

**Métodos:**
- `set_senha(senha: str) -> None` — gera e armazena o hash
- `check_senha(senha: str) -> bool` — valida contra o hash

---

## Classe `Restaurante`

| Campo | Tipo | Restrição |
|---|---|---|
| id | Integer | PK |
| nome | String(120) | NOT NULL |
| categoria | String(80) | NOT NULL |
| faixa_preco | String(30) | NOT NULL (`economico`, `moderado`, `sofisticado`) |
| endereco | String(200) | NOT NULL |
| descricao | Text | nullable |
| criado_em | DateTime | default=utcnow |

**Properties:**
- `media_geral -> float | None` — média das médias de todas as avaliações
- `total_avaliacoes -> int` — contagem de avaliações

---

## Classe `Avaliacao`

| Campo | Tipo | Restrição |
|---|---|---|
| id | Integer | PK |
| usuario_id | Integer | FK → usuario.id |
| restaurante_id | Integer | FK → restaurante.id |
| nota_atendimento | Integer | NOT NULL (1–5) |
| nota_ambiente | Integer | NOT NULL (1–5) |
| nota_prato | Integer | NOT NULL (1–5) |
| nota_preco | Integer | NOT NULL (1–5) |
| media_calculada | Float | nullable |
| comentario | Text | nullable |
| foto_path | String(256) | nullable |
| criado_em | DateTime | default=utcnow |

**Métodos:**
- `calcular_media() -> None` — aritmética simples das 4 notas, arredondada em 2 casas

---

## Categorias disponíveis

`brasileira`, `italiana`, `japonesa`, `mexicana`, `americana`, `francesa`, `árabe`, `vegana`, `frutos_do_mar`, `outra`

## Faixas de preço

| Valor no BD | Exibição |
|---|---|
| `economico` | Econômico (até R$30) |
| `moderado` | Moderado (R$30 a R$80) |
| `sofisticado` | Sofisticado (acima de R$80) |
