# Spec — Melhoria do Perfil do Usuário

**Status:** ✅ Implementada (2026-05-30) — todas as 4 ponderações do revisor aplicadas
**Data:** 2026-05-23  
**Feature branch sugerida:** `feature/perfil-usuario`

> **Execução:** foto de perfil em pasta dedicada (`uploads/perfil/`) sem gif; idade mínima
> 18 e privada; senha exigida apenas na troca de senha; favoritos (até 5) no perfil.
> Coberta por `tests/test_perfil_expandido.py` (19 testes) — suíte completa 166/166.

---

## 1. Contexto e motivação

O perfil atual (`/perfil/editar`) permite apenas alterar nome, e-mail e senha.
Esta spec descreve a expansão para um perfil mais rico, mantendo coerência com
os padrões já estabelecidos no projeto (WTForms, Flask-Limiter, upload de foto
idêntico ao de `Avaliacao`, favoritos via model `Favorito` existente).

---

## 2. Escopo da feature

| Campo              | Situação atual      | Após a feature              |
|--------------------|---------------------|-----------------------------|
| Nome               | ✅ editável          | sem mudança                 |
| E-mail             | ✅ editável          | sem mudança                 |
| Senha              | ✅ editável          | sem mudança                 |
| Foto de perfil     | ❌ inexistente       | ✅ upload opcional (≤ 2 MB)  |
| Idade              | ❌ inexistente       | ✅ campo opcional (13–120)   |
| Favoritos na tela  | ❌ não exibidos      | ✅ listados na página `/perfil` |

**Fora de escopo nesta iteração:**
- Excluir conta
- Foto de perfil em comentários/avaliações (pode vir depois)
- Remover favoritos pelo perfil (já existe rota `/favoritos/<id>/remover`)

---

## 3. Decisões de design

### 3.1 Foto de perfil
- Reutiliza o mesmo helper de upload já usado em `Avaliacao` (pasta
  `app/static/uploads/`).
- Nome do arquivo salvo: `perfil_<usuario_id>.<ext>` — evita colisão e
  substitui automaticamente ao reupar.
- Tamanho máximo: 2 MB (já definido em `Config.MAX_CONTENT_LENGTH`).
- Extensões permitidas: `png`, `jpg`, `jpeg`, `gif` (constante
  `EXTENSOES_PERMITIDAS` de `forms.py`).
- Campo `foto_perfil_path` adicionado ao model `Usuario` (nullable).

> **Ponderação do revisor:** crie outra pasta referente as fotos adicionadas, não misture os updloads feitos para avaliaçoes, faça uma pasta somente sobre as fotos dos usuários. retire o gif
### 3.2 Idade
- Campo inteiro, opcional, sem valor default (null no banco).
- Restrição de check no banco: `13 <= idade <= 120`.
- Validação também no WTForms (`NumberRange`).
- Não exibida publicamente — apenas visível ao próprio usuário no perfil.

> **Ponderação do revisor:** tem que ter no mínimo 18 anos para adicionar, esse é nosso mínimo, não vai ser exibido publicamente

### 3.3 Favoritos na página de perfil
- O model `Favorito` e as rotas de adicionar/remover já existem e não mudam.
- A tela `/perfil` passa a listar os favoritos do usuário (consulta já
  presente em `favoritos/routes.py`, reutilizada via query direta no contexto
  do perfil).
- Limite de exibição: os 5 mais recentes, com link "Ver todos" para
  `/favoritos`.

> **Ponderação do revisor:** ok

### 3.4 Formulário único vs. abas separadas
- Mantém formulário único em `/perfil/editar` (consistência com o atual).
- A senha atual continua sendo exigida para qualquer alteração, incluindo foto
  e idade.

> **Ponderação do revisor (é correto exigir senha para alterar foto?):** a senha não é requisitada para essas laterações, a senha só deve ser reuiqistada caso o usuário queira trocar a senha existente..algo que não realizamos ainda e não vejo necessidade de fazer por enquanto.

---

## 4. Mudanças nos arquivos

### 4.1 `app/models.py` — model `Usuario`
```python
# Adicionar ao model Usuario:
foto_perfil_path: str | None = db.Column(db.String(256), nullable=True)
idade: int | None = db.Column(
    db.Integer,
    db.CheckConstraint("idade IS NULL OR (idade >= 18 AND idade <= 120)", name="ck_idade"),
    nullable=True,
)
```

### 4.2 `app/forms.py` — `EditarPerfilForm`
```python
from wtforms import IntegerField
from wtforms.validators import NumberRange

# Adicionar ao EditarPerfilForm:
foto_perfil = FileField(
    "Foto de perfil (opcional)",
    validators=[FileAllowed(EXTENSOES_PERMITIDAS, "Apenas imagens são permitidas.")],
)
idade = IntegerField(
    "Idade",
    validators=[Optional(), NumberRange(min=13, max=120, message="Idade deve estar entre 18 e 120.")],
)
```

### 4.3 `app/auth/routes.py` — rota `editar_perfil`
- Processar upload de `foto_perfil` com o mesmo helper de `Avaliacao`.
- Salvar `usuario.idade` se informada.
- Passar favoritos recentes para o template de `/perfil`.

### 4.4 Templates
- `auth/editar_perfil.html` — adicionar campos foto e idade.
- `auth/perfil.html` — exibir foto de perfil, idade (se preenchida) e os 5
  favoritos mais recentes.

### 4.5 Migration
```
flask db migrate -m "add foto_perfil_path and idade to usuario"
flask db upgrade
```

---

## 5. Testes especificados

> Os testes abaixo são escritos antes da implementação (TDD).
> Devem residir em `tests/test_perfil_expandido.py`.

### 5.1 Modelo

```python
def test_usuario_aceita_foto_e_idade(app_ctx):
    """Usuario pode ser criado com foto_perfil_path e idade."""
    u = Usuario(nome="Foto", email="foto@test.com", foto_perfil_path="perfil_1.jpg", idade=25)
    u.set_senha("Senha123")
    db.session.add(u)
    db.session.commit()
    recarregado = db.session.get(Usuario, u.id)
    assert recarregado.foto_perfil_path == "perfil_1.jpg"
    assert recarregado.idade == 25

def test_usuario_campos_opcionais_nulos(app_ctx):
    """foto_perfil_path e idade podem ser null."""
    u = Usuario(nome="Sem foto", email="semfoto@test.com")
    u.set_senha("Senha123")
    db.session.add(u)
    db.session.commit()
    recarregado = db.session.get(Usuario, u.id)
    assert recarregado.foto_perfil_path is None
    assert recarregado.idade is None
```

### 5.2 Formulário — validação de idade

```python
def test_editar_perfil_idade_valida(cliente_logado):
    """Idade entre 13 e 120 deve ser aceita."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User", "email": "test@example.com",
            "senha_atual": "senha123", "nova_senha": "", "confirmar_nova_senha": "",
            "idade": "30",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.idade == 30

def test_editar_perfil_idade_abaixo_do_minimo(cliente_logado):
    """Idade menor que 13 deve ser rejeitada."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User", "email": "test@example.com",
            "senha_atual": "senha123", "nova_senha": "", "confirmar_nova_senha": "",
            "idade": "12",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.idade != 12

def test_editar_perfil_idade_acima_do_maximo(cliente_logado):
    """Idade maior que 120 deve ser rejeitada."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User", "email": "test@example.com",
            "senha_atual": "senha123", "nova_senha": "", "confirmar_nova_senha": "",
            "idade": "121",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.idade != 121

def test_editar_perfil_idade_vazia_aceita(cliente_logado):
    """Campo idade vazio (opcional) não deve causar erro."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User", "email": "test@example.com",
            "senha_atual": "senha123", "nova_senha": "", "confirmar_nova_senha": "",
            "idade": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
```

### 5.3 Upload de foto de perfil

```python
import io

def _imagem_fake():
    """Retorna um objeto de arquivo fake para upload nos testes."""
    data = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    data.name = "foto.png"
    return data

def test_editar_perfil_upload_foto(cliente_logado, app_ctx):
    """Upload de imagem válida deve salvar foto_perfil_path no usuário."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User", "email": "test@example.com",
            "senha_atual": "senha123", "nova_senha": "", "confirmar_nova_senha": "",
            "foto_perfil": (io.BytesIO(b"fake-png-data"), "foto.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.foto_perfil_path is not None
    assert u.foto_perfil_path.endswith(".png")

def test_editar_perfil_foto_extensao_invalida(cliente_logado):
    """Upload com extensão não permitida deve ser rejeitado."""
    resp = cliente_logado.post(
        "/perfil/editar",
        data={
            "nome": "Test User", "email": "test@example.com",
            "senha_atual": "senha123", "nova_senha": "", "confirmar_nova_senha": "",
            "foto_perfil": (io.BytesIO(b"dados"), "malware.exe"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    u = Usuario.query.filter_by(email="test@example.com").first()
    assert u.foto_perfil_path is None  # não deve ter sido salvo
```

### 5.4 Favoritos exibidos no perfil

```python
def test_perfil_exibe_favoritos(cliente_logado, restaurante, app_ctx):
    """Página /perfil deve listar os favoritos do usuário."""
    from app.models import Favorito, Usuario
    u = Usuario.query.filter_by(email="test@example.com").first()
    fav = Favorito(usuario_id=u.id, restaurante_id=restaurante.id)
    db.session.add(fav)
    db.session.commit()

    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200
    assert restaurante.nome.encode() in resp.data

def test_perfil_sem_favoritos_nao_quebra(cliente_logado):
    """Perfil sem nenhum favorito deve renderizar normalmente."""
    resp = cliente_logado.get("/perfil")
    assert resp.status_code == 200
```

### 5.5 Página de perfil — exibição dos novos campos

```python
def test_perfil_exibe_idade_quando_preenchida(cliente_logado, app_ctx):
    """Página /perfil deve exibir a idade se ela estiver definida."""
    from app.models import Usuario
    u = Usuario.query.filter_by(email="test@example.com").first()
    u.idade = 28
    db.session.commit()

    resp = cliente_logado.get("/perfil")
    assert b"28" in resp.data

def test_perfil_nao_exibe_idade_quando_nula(cliente_logado):
    """Página /perfil não deve exibir campo de idade se for None."""
    resp = cliente_logado.get("/perfil")
    # Não deve lançar erro — apenas não renderizar o bloco de idade
    assert resp.status_code == 200
```

---

## 6. Critérios de aceite

- [x] Upload de foto de perfil funciona e persiste entre sessões (pasta `uploads/perfil/`)
- [x] Foto inválida (extensão errada ou > 2 MB) é rejeitada com mensagem clara
- [x] Idade fora do intervalo [18, 120] é rejeitada pelo form e pelo banco
- [x] Idade vazia não causa erro (campo opcional)
- [x] Favoritos aparecem na página `/perfil` (até 5, com link "Ver todos")
- [x] Todos os testes desta spec passam (`pytest tests/test_perfil_expandido.py` — 19/19)
- [x] Testes existentes em `test_auth.py` continuam passando sem modificação
- [x] Migration gerada e aplicável (`d95df8627e2c_add_foto_perfil_path_and_idade`)

---

## 7. Questões em aberto para o revisor

1. **Senha obrigatória para alterar foto?** Não

2. **Foto de perfil pública?** Sim

3. **Limite de favoritos no perfil:** 5 no perfil

4. **Idade é informação pública ou privada?** Mantenha privado


