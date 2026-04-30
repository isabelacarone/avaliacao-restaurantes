# Projeto: Rede Social de Avaliação de Restaurantes
**Programação Avançada para Web**

**Autores:** **_Isabela Carone, Isabela Campagnollo e João Antônio_**

---

## 1. Introdução
Este projeto consiste no desenvolvimento de uma plataforma web estática de avaliação de restaurantes, construída com o framework Flask (Python). A aplicação permite que usuários cadastrem avaliações de estabelecimentos gastronômicos com base em critérios objetivos, como atendimento, ambiente, qualidade dos pratos e faixa de preço. A plataforma é acessível por navegadores web.

## 2. Objetivos

### 2.1 Objetivo Geral
Desenvolver uma aplicação web com Flask que permita o registro e a consulta de avaliações de restaurantes, promovendo maior visibilidade e competitividade entre os estabelecimentos.

### 2.2 Objetivos Específicos
* Facilitar a forma como restaurantes recebem e visualizam avaliações de seus clientes.
* Criar um ambiente gastronômico mais competitivo por meio da transparência das avaliações.
* Permitir que os usuários encontrem restaurantes com base em filtros de localização e faixa de preço.
* Oferecer uma interface simples e intuitiva para o cadastro de avaliações com texto e fotos.

## 3. Público-alvo
* Donos e gestores de restaurantes que desejam maior visibilidade e contato com seus clientes.
* Consumidores que buscam novas experiências gastronômicas e querem embasar suas escolhas em avaliações reais.
* Usuários que desejam que suas opiniões sobre restaurantes tenham impacto e visibilidade.

## 4. Tecnologias Utilizadas
* Back-end: Python com Flask
* Front-end: HTML5, CSS3, Bootstrap 5 (templates Jinja2)
* Banco de dados: SQLite (via SQLAlchemy)
* Controle de versão: Git/GitHub

## 5. Funcionalidades da Aplicação

### 5.1 Cadastro e Autenticação de Usuários
* Registro de novo usuário com nome, e-mail e senha.
* Login e logout com controle de sessão (Flask-Login).
* Página de perfil exibindo as avaliações feitas pelo usuário.

### 5.2 Gerenciamento de Restaurantes
* Cadastro de restaurante com nome, endereço, categoria e faixa de preço.
* Listagem de todos os restaurantes cadastrados.
* Página de detalhes de cada restaurante com suas avaliações.

### 5.3 Sistema de Avaliações
* Registro de avaliação com nota (1 a 5) nos critérios: atendimento, ambiente, qualidade do prato e preço.
* Adição de comentário textual e upload de uma foto do prato (opcional).
* Cálculo automático da nota média do restaurante com base nas avaliações recebidas.

### 5.4 Filtro de Busca
* Busca por nome de restaurante.
* Filtro por faixa de preço (econômico, moderado, sofisticado).
* Filtro por categoria (ex.: italiana, japonesa, brasileira).

---

## 6. Requisitos Funcionais

| ID | Descrição | Tipo | Prioridade |
| :--- | :--- | :--- | :--- |
| RF01 | O sistema deve permitir o cadastro de novos usuários com nome, e-mail e senha. | Funcional | Alta |
| RF02 | O sistema deve autenticar usuários via e-mail e senha. | Funcional | Alta |
| RF03 | O sistema deve permitir o cadastro de restaurantes com nome, endereço, categoria e faixa de preço. | Funcional | Alta |
| RF04 | O sistema deve exibir a listagem de todos os restaurantes cadastrados. | Funcional | Alta |
| RF05 | O sistema deve permitir que usuários autenticados registrem avaliações com notas e comentários. | Funcional | Alta |
| RF06 | O sistema deve calcular e exibir a nota média de cada restaurante. | Funcional | Alta |
| RF07 | O sistema deve permitir upload de imagem do prato na avaliação. | Funcional | Média |
| RF08 | O sistema deve permitir a busca de restaurantes por nome, categoria e faixa de preço. | Funcional | Média |
| RF09 | O sistema deve exibir uma página de perfil com as avaliações do usuário logado. | Funcional | Baixa |

## 7. Requisitos Não Funcionais

| ID | Descrição | Tipo | Prioridade |
| :--- | :--- | :--- | :--- |
| RNF01 | A aplicação deve ser responsiva e funcionar em dispositivos móveis e desktops. | Não Funcional | Alta |
| RNF02 | As senhas dos usuários devem ser armazenadas com hash (ex.: bcrypt). | Não Funcional | Alta |
| RNF03 | O código deve estar organizado seguindo o padrão MVC com Flask Blueprints. | Não Funcional | Média |
| RNF04 | A aplicação deve carregar as páginas principais em menos de 3 segundos. | Não Funcional | Média |
| RNF05 | O projeto deve ser versionado no GitHub com commits regulares. | Não Funcional | Média |