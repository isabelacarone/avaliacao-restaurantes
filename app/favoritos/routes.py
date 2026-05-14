"""Rotas de favoritos: adicionar, remover e listar."""

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.favoritos import favoritos_bp
from app.models import Favorito, Restaurante


@favoritos_bp.route("/favoritos/<int:restaurante_id>/adicionar", methods=["POST"])
@login_required
def adicionar(restaurante_id: int) -> str:
    restaurante = db.session.get(Restaurante, restaurante_id)
    if not restaurante or restaurante.deletado_em:
        abort(404)

    ja_favoritou = Favorito.query.filter_by(
        usuario_id=current_user.id, restaurante_id=restaurante_id
    ).first()
    if not ja_favoritou:
        fav = Favorito(usuario_id=current_user.id, restaurante_id=restaurante_id)
        db.session.add(fav)
        db.session.commit()
        flash(f'"{restaurante.nome}" adicionado aos favoritos.', "success")
    return redirect(url_for("restaurantes.detalhe", restaurante_id=restaurante_id))


@favoritos_bp.route("/favoritos/<int:restaurante_id>/remover", methods=["POST"])
@login_required
def remover(restaurante_id: int) -> str:
    fav = Favorito.query.filter_by(
        usuario_id=current_user.id, restaurante_id=restaurante_id
    ).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash("Removido dos favoritos.", "info")
    return redirect(url_for("restaurantes.detalhe", restaurante_id=restaurante_id))


@favoritos_bp.route("/favoritos")
@login_required
def listar() -> str:
    favs = (
        Favorito.query.filter_by(usuario_id=current_user.id)
        .join(Restaurante)
        .filter(Restaurante.deletado_em.is_(None))
        .order_by(Favorito.criado_em.desc())
        .all()
    )
    return render_template("favoritos/listar.html", favoritos=favs)
