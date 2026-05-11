# Próximos Passos — Mesa Certa

## Funcionalidades concluídas

| Item | Sprint |
|---|---|
| RF09 — Página de perfil (`GET /perfil`) | 2 |
| Paginação na listagem (12 por página) | 2 |
| Bloqueio de avaliação duplicada | 2 |
| Flask-Migrate configurado e migration inicial aplicada | 2 |
| Preview de imagem antes do upload | 3 |
| Edição de avaliação própria (`GET/POST /avaliacoes/<id>/editar`) | 3 |
| Exclusão de avaliação própria (`POST /avaliacoes/<id>/excluir`) | 3 |
| Ordenação da listagem (recentes / melhor nota / mais avaliados) | 3 |
| Tratamento de erro 413 (arquivo acima de 2 MB) | 3 |
| `.gitignore` corrigido; `.env.example` criado | 3 |
| Paginação de avaliações no detalhe do restaurante (8 por página) | 4 |
| Botões editar/excluir no detalhe do restaurante (apenas para o autor) | 4 |
| Testes automatizados com pytest e pytest-flask (21 testes) | 4 |
| Seed do banco de dados (`seed.py`) | 4 |
| uv atualizado (0.11.9 → 0.11.12); pyproject.toml consolidado | 4 |
| Correção de `datetime.utcnow()` depreciado em `models.py` | 5 |
| `.gitignore` + `.pytest_cache/` e `*_test.db` | 5 |
| README atualizado com comandos uv modernos (`uv sync`, `uv add`) | 5 |
| `create_app(test_config)` — isolamento total dos testes do banco real | 5 |
| uv atualizado (0.11.12 → 0.11.13); `pytest-cov` adicionado | 6 |
| Validadores WTForms customizados (`UniqueEmail`, `UniqueNomeRestaurante`) | 6 |
| Módulo JS client-side `validacao.js` (vazio, e-mail, confirmação de senha) | 6 |
| Modal de confirmação de exclusão com nome do item (`confirmarExclusao`) | 6 |
| Remoção de verificações manuais de duplicata das rotas | 6 |
| 25 testes passando; cobertura 88% | 6 |

---

## Melhorias recomendadas

### Variáveis de ambiente em produção

O arquivo `.env.example` documenta as variáveis necessárias. Antes de qualquer deploy:

1. Copie `.env.example` para `.env`
2. Gere uma `SECRET_KEY` segura:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Troque `DATABASE_URL` para o banco de produção (ex.: PostgreSQL)

---

### Ampliar cobertura de testes

Cobertura atual: **88%**. Linhas não cobertas incluem:

- `app/avaliacoes/routes.py` — helper de foto e edição (72%)
- `app/models.py` — propriedades `media_geral` e `total_avaliacoes` (85%)

```bash
uv run pytest tests/ --cov=app --cov-report=term-missing
```

---

### Limitação de upload em produção

Servidores como Nginx/Gunicorn têm seu próprio limite de tamanho de body. Configurar `client_max_body_size 2m;` no Nginx é necessário além do `MAX_CONTENT_LENGTH` do Flask.
