# Mesa Certa: Uma Rede Social de Avaliação de Restaurantes

**Programação Avançada para Web**

**Autores:** Isabela Carone, Isabela Campagnollo e João Antônio

---

## Sobre o projeto

Plataforma web para avaliação de restaurantes construída com Flask, onde usuários cadastram avaliações com notas por critério (atendimento, ambiente, prato, preço), comentário e foto. A aplicação também calcula a nota média de cada restaurante.

**Tecnologias utilizadas:** Flask 3, SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF, Bootstrap 5, SQLite, uv

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
uv sync
```

Instala todas as dependências a partir do `uv.lock`, garantindo versões exatas. 

---


## Rodando a aplicação

```bash
uv run python run.py
```
---

## Estrutura do projeto

```
avaliacao-restaurantes/
├── app/
│   ├── __init__.py          
│   ├── config.py            
│   ├── models.py            
│   ├── forms.py             
│   ├── auth/                
│   ├── restaurantes/        
│   ├── avaliacoes/          
│   ├── static/uploads/      
│   └── templates/           
│       ├── auth/perfil.html
│       ├── avaliacoes/nova.html    
│       └── avaliacoes/editar.html  
├── migrations/              
│   └── versions/
├── docs/                    
│   ├── arquitetura.md
│   ├── modelos.md
│   ├── rotas.md
│   └── implementacoes.md
│   
│ambiente
├── run.py                   
├── pyproject.toml           
└── uv.lock                   
```

---

## Funcionalidades implementadas

| ID | Descrição |
|---|---|
| RF01 | Cadastro de usuários |
| RF02 | Login/logout |
| RF03 | Cadastro de restaurantes |
| RF04 | Listagem com paginação e ordenação |
| RF05 | Avaliações com notas e comentários |
| RF06 | Cálculo e exibição de nota média |
| RF07 | Upload de foto com preview |
| RF08 | Busca por nome, categoria e faixa de preço |
| RF09 | Página de perfil do usuário |
| RF10 | Edição e exclusão de avaliações próprias |
| RF11 | Bloqueio de avaliação duplicada |
| RF12 | Migrações de schema com Flask-Migrate |
| RF13 | Tratamento de erro 413 (upload acima de 2 MB) |
| RF14 | Paginação de avaliações no detalhe do restaurante |
| RF15 | Botões editar/excluir no detalhe (apenas o autor) |
| RF16 | Testes automatizados (21 testes com pytest) |
| RF17 | Seed de banco para desenvolvimento |
| RF18 | Datas com fuso horário (timezone-aware) |
| RF19 | Isolamento total dos testes do banco real |
| RF20 | Validadores WTForms: e-mail único, nome de restaurante único |
| RF21 | Validação client-side JS (vazio, e-mail, confirmação de senha) |
| RF22 | Modal de confirmação de exclusão com nome do item |
| RF23 | Cobertura de testes 88% (pytest-cov) |

---

## Requisitos Funcionais e Não Funcionais

### Requisitos Funcionais

| ID | Descrição | 
|---|---|
| RF01 | Cadastro com nome, e-mail e senha |
| RF02 | Autenticação via e-mail e senha |
| RF03 | Cadastro de restaurantes | 
| RF04 | Listagem de restaurantes | 
| RF05 | Avaliações com notas e comentários | 
| RF06 | Cálculo automático de nota média | 
| RF07 | Upload de imagem na avaliação | 
| RF08 | Busca por nome, categoria e faixa de preço | 
| RF09 | Página de perfil do usuário | 

### Requisitos Não Funcionais

| ID | Descrição | 
|---|---|
| RNF01 | Interface responsiva (Bootstrap 5) |
| RNF02 | Senhas com hash (Werkzeug PBKDF2) | 
| RNF03 | Padrão MVC com Flask Blueprints | 
| RNF04 | Versionado no GitHub | 


