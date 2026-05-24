"""Rotas de autenticação: login, cadastro, logout e perfil."""

import os

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm

from app import db, limiter
from app.auth import auth_bp
from app.forms import CadastroForm, EditarPerfilForm, LoginForm
from app.models import Avaliacao, Favorito, Restaurante, Usuario

_MAGIC_BYTES_PERFIL: dict[str, bytes] = {
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG",
}


def _salvar_foto_perfil(arquivo, usuario_id: int) -> str | None:
    """Salva foto de perfil em uploads/perfil/ com nome determinístico."""
    if not arquivo or not arquivo.filename:
        return None
    extensoes = current_app.config.get("ALLOWED_EXTENSIONS_PERFIL", set())
    if "." not in arquivo.filename:
        return None
    ext = arquivo.filename.rsplit(".", 1)[1].lower()
    if ext not in extensoes:
        return None
    cabecalho = arquivo.read(8)
    arquivo.seek(0)
    if not cabecalho.startswith(_MAGIC_BYTES_PERFIL.get(ext, b"")):
        return None
    nome_arquivo = f"perfil_{usuario_id}.{ext}"
    pasta = current_app.config["UPLOAD_FOLDER_PERFIL"]
    os.makedirs(pasta, exist_ok=True)
    arquivo.save(os.path.join(pasta, nome_arquivo))
    return nome_arquivo


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login() -> str:
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_senha(form.senha.data):
            login_user(usuario)
            current_app.logger.info("Login: %s", usuario.email)
            flash(f"Bem-vindo(a), {usuario.nome}!", "success")
            return redirect(url_for("restaurantes.listar"))
        current_app.logger.warning("Login falhou: %s", form.email.data)
        flash("E-mail ou senha incorretos. Tente novamente.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/cadastro", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def cadastro() -> str:
    form = CadastroForm()
    if form.validate_on_submit():
        usuario = Usuario(nome=form.nome.data, email=form.email.data)
        usuario.set_senha(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        current_app.logger.info("Cadastro: %s", usuario.email)
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/cadastro.html", form=form)


@auth_bp.route("/perfil")
@login_required
def perfil() -> str:
    page = request.args.get("page", 1, type=int)
    paginacao = current_user.avaliacoes.order_by(Avaliacao.criado_em.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    total = current_user.avaliacoes.count()
    favoritos_recentes = (
        Favorito.query.filter_by(usuario_id=current_user.id)
        .join(Restaurante)
        .filter(Restaurante.deletado_em.is_(None))
        .order_by(Favorito.criado_em.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "auth/perfil.html",
        avaliacoes=paginacao.items,
        paginacao=paginacao,
        total_avaliacoes=total,
        favoritos_recentes=favoritos_recentes,
        form_csrf=FlaskForm(),
    )


@auth_bp.route("/perfil/editar", methods=["GET", "POST"])
@login_required
def editar_perfil() -> str:
    form = EditarPerfilForm(obj=current_user)
    if form.validate_on_submit():
        # Troca de senha requer confirmação da senha atual
        if form.nova_senha.data:
            senha_atual = form.senha_atual.data
            senha_ok = senha_atual and current_user.check_senha(senha_atual)
            if not senha_ok:
                form.senha_atual.errors.append("Senha atual incorreta.")
                return render_template("auth/editar_perfil.html", form=form)
            current_user.set_senha(form.nova_senha.data)

        novo_email = form.email.data.strip().lower()
        if novo_email != current_user.email:
            existente = Usuario.query.filter(
                Usuario.email == novo_email, Usuario.id != current_user.id
            ).first()
            if existente:
                form.email.errors.append("Este e-mail já está cadastrado.")
                return render_template("auth/editar_perfil.html", form=form)

        current_user.nome = form.nome.data.strip()
        current_user.email = novo_email
        current_user.idade = form.idade.data

        nova_foto = _salvar_foto_perfil(form.foto_perfil.data, current_user.id)
        if nova_foto:
            current_user.foto_perfil_path = nova_foto

        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("auth.perfil"))

    return render_template("auth/editar_perfil.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout() -> str:
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("restaurantes.listar"))
