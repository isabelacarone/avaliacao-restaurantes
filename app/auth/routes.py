"""Rotas de autenticação: login, cadastro, logout e perfil."""

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm

from app import db
from app.auth import auth_bp
from app.forms import CadastroForm, EditarPerfilForm, LoginForm
from app.models import Avaliacao, Usuario


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    """Exibe o formulário de login e autentica o usuário.

    Returns:
        Renderização do template de login ou redirecionamento para a listagem.
    """
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_senha(form.senha.data):
            login_user(usuario)
            flash(f"Bem-vindo(a), {usuario.nome}!", "success")
            return redirect(url_for("restaurantes.listar"))
        flash("E-mail ou senha incorretos. Tente novamente.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro() -> str:
    """Exibe o formulário de cadastro e cria um novo usuário.

    Returns:
        Renderização do template de cadastro ou redirecionamento após sucesso.
    """
    form = CadastroForm()
    if form.validate_on_submit():
        # Unicidade de e-mail já validada por UniqueEmail() no formulário
        usuario = Usuario(nome=form.nome.data, email=form.email.data)
        usuario.set_senha(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/cadastro.html", form=form)


@auth_bp.route("/perfil")
@login_required
def perfil() -> str:
    """Exibe o perfil do usuário autenticado com suas avaliações.

    Returns:
        Renderização do template de perfil.
    """
    avaliacoes = (
        current_user.avaliacoes.order_by(Avaliacao.criado_em.desc()).all()
    )
    return render_template(
        "auth/perfil.html", avaliacoes=avaliacoes, form_csrf=FlaskForm()
    )


@auth_bp.route("/perfil/editar", methods=["GET", "POST"])
@login_required
def editar_perfil() -> str:
    """Exibe o formulário e salva alterações no nome, e-mail e senha do usuário.

    Returns:
        Renderização do formulário de edição ou redirecionamento após sucesso.
    """
    form = EditarPerfilForm(obj=current_user)
    if form.validate_on_submit():
        if not current_user.check_senha(form.senha_atual.data):
            form.senha_atual.errors.append("Senha atual incorreta.")
            return render_template("auth/editar_perfil.html", form=form)

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
        if form.nova_senha.data:
            current_user.set_senha(form.nova_senha.data)
        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("auth.perfil"))

    return render_template("auth/editar_perfil.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout() -> str:
    """Encerra a sessão do usuário autenticado.

    Returns:
        Redirecionamento para a listagem de restaurantes.
    """
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("restaurantes.listar"))
