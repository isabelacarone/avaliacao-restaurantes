# Mesa Certa - Rede de Avaliação de Restaurantes

**Programação Avançada para Web**

Breve aplicativo web em Flask para cadastro e avaliação de restaurantes. Usuários podem criar contas, enviar avaliações com notas por critério (atendimento, ambiente, prato, preço), comentário e foto; a aplicação calcula médias e exibe listagens.

Documentação de entrega em: `docs/documentacao-entrega.html` ou `docs/documentacao-entrega.md`

---

**Tecnologias principais**
- Python 3.12+
- Flask, SQLAlchemy
- Flask-Login, Flask-WTF
- Bootstrap 5
- SQLite 

---

## Pré-requisitos

- Python 3.12+
- Recomendado: `uv` 

Instalar `uv` (opcional):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

---

## Instalação e execução (Linux)

```bash
git clone <url-do-repositorio>
cd avaliacao-restaurantes

# criar ambiente virtual (opção uv)
uv venv --python 3.12
source .venv/bin/activate

# ou usando venv do Python
python -m venv .venv
source .venv/bin/activate

# instalar dependências
uv pip install -e ".[dev]"      # ou: pip install -r requirements.txt

# rodar a aplicação
uv run python run.py            # ou: python run.py
```
---

## Lockfile (`uv.lock`)

O `uv.lock` fixa versões exatas das dependências. Para reproduzir o ambiente exato use:

```bash
uv pip sync uv.lock
```

Ao alterar dependências:

```bash
uv pip install <pacote>
uv pip compile pyproject.toml -o uv.lock
```

---

## Seed e dados de teste

Para popular o banco com dados de exemplo execute:

```bash
python seed.py
```

No deploy atual (Render) o `seed.py` é executado automaticamente. Atenção: o Render free usa SQLite, dados persistentes exigem PostgreSQL ou outro serviço de banco.

---

## Testes e qualidade de código

Rodar testes:

```bash
pytest -q
```

Gerar relatório de coverage (HTML e XML):

```bash
pytest --cov=app --cov-report=html --cov-report=xml
```

O relatório HTML será criado em `htmlcov/` e o relatório XML em `coverage.xml`.

Lint/format (usando `ruff`):

```bash
uv run ruff check app/ run.py
uv run ruff check --fix app/ run.py
```

---

## Deploy

Aplicação hospedada em: https://avaliacao-restaurantes.onrender.com

No Render o processo usa `requirements.txt` e `Procfile`. A sequência de deploy configurada é:

```
flask db upgrade && python seed.py && gunicorn
```

---

## Estrutura do projeto (resumo)

```
avaliacao-restaurantes/
├── app/                # aplicação (blueprints, models, forms, templates)
├── docs/               # documentação técnica
├── run.py              # entrypoint
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

Para detalhes da arquitetura e rotas, veja a pasta `docs/`.

---

## Ferramentas utilizadas no desenvolvimento

Utilizamos o **GitHub Copilot** para avaliação de PRs e auxílio na documentação técnica; **GitHub Copilot Agent** e **Claude Code** foram usados para solucionar incompatibilidades no deploy no Render. O **Claude Code** também foi utilizado para testes e revisão de código dentro do VS Code, garantindo maior escalabilidade e legibilidade das features.

Utilizamos implementação via SDD (Spec Driven Development) para dois casos, a documentação relacionada está em `.specs/spec-conformidade-criterios.md` e `.specs/spec-perfil-usuario.md`.

---

## Autores

- Isabela Carone

- Isabela Campagnollo 

- João Antônio
