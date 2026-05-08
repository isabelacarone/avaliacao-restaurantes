"""Rotas de avaliações: criação de nova avaliação."""

import os
import uuid

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.avaliacoes import avaliacoes_bp
from app.forms import AvaliacaoForm
from app.models import Avaliacao, Restaurante


def _extensao_valida(nome_arquivo: str) -> bool:
    """Verifica se a extensão do arquivo está na lista de permitidas.

    Args:
        nome_arquivo: Nome do arquivo com extensão.

    Returns:
        True se a extensão for permitida, False caso contrário.
    """
    extensoes = current_app.config.get("ALLOWED_EXTENSIONS", set())
    return "." in nome_arquivo and nome_arquivo.rsplit(".", 1)[1].lower() in extensoes


@avaliacoes_bp.route("/avaliacoes/nova/<int:restaurante_id>", methods=["GET", "POST"])
@login_required
def nova(restaurante_id: int) -> str:
    """Exibe o formulário e registra uma nova avaliação para o restaurante.

    Args:
        restaurante_id: ID do restaurante a ser avaliado.

    Returns:
        Renderização do formulário ou redirecionamento após sucesso.
    """
    restaurante = db.session.get(Restaurante, restaurante_id)
    if not restaurante:
        abort(404)

    form = AvaliacaoForm()
    if form.validate_on_submit():
        foto_path = None
        arquivo = form.foto.data
        if arquivo and arquivo.filename:
            if _extensao_valida(arquivo.filename):
                extensao = arquivo.filename.rsplit(".", 1)[1].lower()
                nome_arquivo = f"{uuid.uuid4().hex}.{extensao}"
                pasta = current_app.config["UPLOAD_FOLDER"]
                os.makedirs(pasta, exist_ok=True)
                arquivo.save(os.path.join(pasta, nome_arquivo))
                foto_path = nome_arquivo

        avaliacao = Avaliacao(
            usuario_id=current_user.id,
            restaurante_id=restaurante_id,
            nota_atendimento=int(form.nota_atendimento.data),
            nota_ambiente=int(form.nota_ambiente.data),
            nota_prato=int(form.nota_prato.data),
            nota_preco=int(form.nota_preco.data),
            comentario=form.comentario.data,
            foto_path=foto_path,
        )
        avaliacao.calcular_media()
        db.session.add(avaliacao)
        db.session.commit()
        flash("Avaliação registrada com sucesso!", "success")
        return redirect(
            url_for("restaurantes.detalhe", restaurante_id=restaurante_id)
        )

    return render_template(
        "avaliacoes/nova.html",
        form=form,
        restaurante=restaurante,
    )
