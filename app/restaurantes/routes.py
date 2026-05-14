"""Rotas de restaurantes: listagem, detalhe e cadastro."""

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import func

from app import db
from app.forms import RestauranteForm
from app.models import Avaliacao, Favorito, Restaurante
from app.restaurantes import restaurantes_bp

_ORDENS_VALIDAS: dict[str, object] = {}


def _ordem_clause(order: str, media_col: object, total_col: object) -> object:
    """Retorna a cláusula ORDER BY correspondente ao parâmetro recebido.

    Args:
        order: Identificador da ordenação ('recentes', 'nota', 'avaliacoes').
        media_col: Coluna de média da subquery.
        total_col: Coluna de total de avaliações da subquery.

    Returns:
        Expressão SQLAlchemy para ordenação.
    """
    if order == "nota":
        return media_col.desc().nulls_last()
    if order == "avaliacoes":
        return total_col.desc()
    return Restaurante.criado_em.desc()


@restaurantes_bp.route("/")
def listar() -> str:
    """Lista restaurantes com filtros por nome, categoria, faixa de preço e ordenação.

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
    media_col = metricas_subquery.c.media_geral
    total_col = func.coalesce(metricas_subquery.c.total_avaliacoes, 0)

    query = (
        db.session.query(
            Restaurante,
            media_col,
            total_col.label("total_avaliacoes"),
        )
        .outerjoin(
            metricas_subquery,
            metricas_subquery.c.restaurante_id == Restaurante.id,
        )
        .filter(Restaurante.deletado_em.is_(None))
    )

    termo = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    faixa_preco = request.args.get("faixa_preco", "").strip()
    order = request.args.get("order", "recentes").strip()
    nota_min = request.args.get("nota_min", type=float)

    if termo:
        query = query.filter(Restaurante.nome.ilike(f"%{termo}%"))
    if categoria:
        query = query.filter(Restaurante.categoria == categoria)
    if faixa_preco:
        query = query.filter(Restaurante.faixa_preco == faixa_preco)
    if nota_min:
        query = query.filter(media_col >= nota_min)

    page = request.args.get("page", 1, type=int)
    paginacao = query.order_by(_ordem_clause(order, media_col, total_col)).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template(
        "restaurantes/listar.html",
        restaurantes=paginacao.items,
        paginacao=paginacao,
        termo=termo,
        categoria=categoria,
        faixa_preco=faixa_preco,
        order=order,
        nota_min=nota_min,
    )


@restaurantes_bp.route("/restaurantes/<int:restaurante_id>")
def detalhe(restaurante_id: int) -> str:
    """Exibe os detalhes e avaliações paginadas de um restaurante específico.

    Args:
        restaurante_id: ID do restaurante a ser exibido.

    Returns:
        Renderização do template de detalhe ou erro 404.
    """
    restaurante = db.session.get(Restaurante, restaurante_id)
    if not restaurante or restaurante.deletado_em:
        abort(404)

    todas = restaurante.avaliacoes.order_by(Avaliacao.criado_em.desc()).all()
    medias = [av.media_calculada for av in todas if av.media_calculada is not None]
    media_geral = round(sum(medias) / len(medias), 1) if medias else None

    page = request.args.get("page", 1, type=int)
    ordem = request.args.get("ordem", "recentes")
    if ordem == "melhor":
        q_av = restaurante.avaliacoes.order_by(Avaliacao.media_calculada.desc())
    elif ordem == "pior":
        q_av = restaurante.avaliacoes.order_by(Avaliacao.media_calculada.asc())
    else:
        q_av = restaurante.avaliacoes.order_by(Avaliacao.criado_em.desc())

    paginacao = q_av.paginate(page=page, per_page=8, error_out=False)

    eh_favorito = False
    if current_user.is_authenticated:
        eh_favorito = (
            Favorito.query.filter_by(
                usuario_id=current_user.id, restaurante_id=restaurante_id
            ).first()
            is not None
        )

    return render_template(
        "restaurantes/detalhe.html",
        restaurante=restaurante,
        avaliacoes=paginacao.items,
        avaliacoes_todas=todas,
        paginacao=paginacao,
        media_geral=media_geral,
        total_avaliacoes=len(todas),
        form_csrf=FlaskForm(),
        ordem=ordem,
        eh_favorito=eh_favorito,
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
