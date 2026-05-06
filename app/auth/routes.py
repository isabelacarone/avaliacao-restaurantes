"""Rotas de autenticação: login, cadastro e logout."""

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from app import db
from app.auth import auth_bp
from app.forms import CadastroForm, LoginForm
from app.models import Usuario


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
        email_existente = Usuario.query.filter_by(email=form.email.data).first()
        if email_existente:
            flash("Este e-mail já está cadastrado. Faça login.", "warning")
            return redirect(url_for("auth.login"))
        usuario = Usuario(nome=form.nome.data, email=form.email.data)
        usuario.set_senha(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/cadastro.html", form=form)


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
