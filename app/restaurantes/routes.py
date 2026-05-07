"""Rotas de restaurantes: listagem, detalhe e cadastro."""

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import func

from app import db
from app.forms import RestauranteForm
from app.models import Avaliacao, Restaurante
from app.restaurantes import restaurantes_bp


@restaurantes_bp.route("/")
def listar() -> str:
    """Lista restaurantes com suporte a filtros por nome, categoria e faixa de preço.

    Returns:
        Renderização do template de listagem com os restaurantes filtrados.
    """
    metricas_subquery = (
        db.session.query(
            Avaliacao.restaurante_id.label("restaurante_id"),
            func.avg(Avaliacao.media_calculada).label("media_geral"),
            func.count(Avaliacao.id).label("total_avaliacoes"),
        )
        .group_by(Avaliacao.restaurante_id)
        .subquery()
    )
    query = db.session.query(
        Restaurante,
        metricas_subquery.c.media_geral,
        func.coalesce(metricas_subquery.c.total_avaliacoes, 0).label(
            "total_avaliacoes"
        ),
    ).outerjoin(metricas_subquery, metricas_subquery.c.restaurante_id == Restaurante.id)
    termo = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    faixa_preco = request.args.get("faixa_preco", "").strip()

    if termo:
        query = query.filter(Restaurante.nome.ilike(f"%{termo}%"))
    if categoria:
        query = query.filter(Restaurante.categoria == categoria)
    if faixa_preco:
        query = query.filter(Restaurante.faixa_preco == faixa_preco)

    restaurantes = query.order_by(Restaurante.criado_em.desc()).all()
    return render_template(
        "restaurantes/listar.html",
        restaurantes=restaurantes,
        termo=termo,
        categoria=categoria,
        faixa_preco=faixa_preco,
    )


@restaurantes_bp.route("/restaurantes/<int:restaurante_id>")
def detalhe(restaurante_id: int) -> str:
    """Exibe os detalhes e avaliações de um restaurante específico.

    Args:
        restaurante_id: ID do restaurante a ser exibido.

    Returns:
        Renderização do template de detalhe ou erro 404.
    """
    restaurante = db.session.get(Restaurante, restaurante_id)
    if not restaurante:
        abort(404)
    avaliacoes = restaurante.avaliacoes.order_by(Avaliacao.criado_em.desc()).all()
    total_avaliacoes = len(avaliacoes)
    medias = [
        avaliacao.media_calculada
        for avaliacao in avaliacoes
        if avaliacao.media_calculada is not None
    ]
    media_geral = round(sum(medias) / len(medias), 1) if medias else None
    return render_template(
        "restaurantes/detalhe.html",
        restaurante=restaurante,
        avaliacoes=avaliacoes,
        media_geral=media_geral,
        total_avaliacoes=total_avaliacoes,
    )


@restaurantes_bp.route("/restaurantes/novo", methods=["GET", "POST"])
@login_required
def novo() -> str:
    """Exibe o formulário e cria um novo restaurante.

    Returns:
        Renderização do formulário de cadastro ou redirecionamento após sucesso.
    """
    form = RestauranteForm()
    if form.validate_on_submit():
        restaurante = Restaurante(
            nome=form.nome.data,
            categoria=form.categoria.data,
            faixa_preco=form.faixa_preco.data,
            endereco=form.endereco.data,
            descricao=form.descricao.data,
        )
        db.session.add(restaurante)
        db.session.commit()
        flash(f'Restaurante "{restaurante.nome}" cadastrado com sucesso!', "success")
        return redirect(url_for("restaurantes.detalhe", restaurante_id=restaurante.id))
    return render_template("restaurantes/novo.html", form=form)
