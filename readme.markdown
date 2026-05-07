# Mesa Certa: Uma Rede Social de Avaliação de Restaurantes

**Programação Avançada para Web**

**Autores:** Isabela Carone, Isabela Campagnollo e João Antônio

---

## Sobre o projeto

Plataforma web para avaliação de restaurantes construída com Flask, onde Usuários cadastram avaliações com notas por critério (atendimento, ambiente, prato, preço), comentário e foto. A aplicação também calcula a nota média de cada restaurante.

**Tecnologias:** Flask 3, SQLAlchemy, Flask-Login, Flask-WTF, Bootstrap 5, SQLite, uv

---

## Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 

### Instalar o uv (caso não tenha)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verifique a instalação:

```bash
uv --version
```

---

## Configuração do ambiente

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd avaliacao-restaurantes
```

### 2. Criar o ambiente virtual

```bash
uv venv --python 3.12
```

Isso cria a pasta `.venv/` com Python 3.12 isolado.

### 3. Ativar o ambiente virtual

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
uv pip install -e ".[dev]"
```

__O flag `-e` instala o projeto em modo editável__
<br>
__O `[dev]` inclui ferramentas de dev tipo o `ruff`__

---

## Entendendo o uv.lock

O arquivo `uv.lock` registra as versões exatas de todas as dependências resolvidas. Ele garante que todo membro da equipe e qualquer ambiente de CI instale exatamente os mesmos pacotes.

### Quando o uv.lock é atualizado?

- Quando você adiciona ou remove dependências no `pyproject.toml`
- Quando você roda `uv pip compile` manualmente

### Instalar a partir do lockfile (reproduzir ambiente exato)

```bash
uv pip sync uv.lock
```
### Regenerar o lockfile após mudar dependências

```bash
# 1. Edite pyproject.toml adicionando/removendo pacotes

# 2. Instale as novas dependências
uv pip install -e ".[dev]"

# 3. Atualize o lockfile
uv pip compile pyproject.toml -o uv.lock
```

### Adicionar uma nova dependência

```bash
# Edite pyproject.toml manualmente, depois:
uv pip install <pacote>
uv pip compile pyproject.toml -o uv.lock
```

---

## Rodando a aplicação

```bash
uv run python run.py
```

---

## Verificação rápida do código

O projeto usa [ruff](https://docs.astral.sh/ruff/), garantindo PEP 8

```bash
# Verificar erros
uv run ruff check app/ run.py

# Corrigir automaticamente os erros corrigíveis
uv run ruff check --fix app/ run.py
```

---
<!-- 
## Estrutura do projeto

```
avaliacao-restaurantes/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── config.py            # Configurações
│   ├── models.py            # Usuario, Restaurante, Avaliacao
│   ├── forms.py             # Formulários WTForms
│   ├── auth/                # Blueprint: login, cadastro, logout
│   ├── restaurantes/        # Blueprint: listagem, detalhe, cadastro
│   ├── avaliacoes/          # Blueprint: nova avaliação
│   ├── static/uploads/      # Fotos enviadas pelos usuários
│   └── templates/           # Templates Jinja2 (Bootstrap 5)
├── docs/                    # Documentação técnica
│   ├── arquitetura.md
│   ├── modelos.md
│   ├── rotas.md
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
| RF04 | Listagem de restaurantes | ✅ |
| RF05 | Avaliações com notas e comentários | ✅ |
| RF06 | Cálculo e exibição de nota média | ✅ |
| RF07 | Upload de foto na avaliação | ✅ |
| RF08 | Busca por nome, categoria e faixa de preço | ✅ |
| RF09 | Página de perfil do usuário | 🔲 pendente |

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

-->