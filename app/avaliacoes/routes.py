"""Rotas de avaliações: criação, edição e exclusão."""

import os
import uuid

from flask import abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.avaliacoes import avaliacoes_bp
from app.forms import AvaliacaoForm
from app.models import Avaliacao, Restaurante

_MAGIC_BYTES: dict[str, bytes] = {
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG",
    "gif": b"GIF8",
}


def _conteudo_valido(arquivo, extensao: str) -> bool:  # noqa: ANN001
    """Verifica os primeiros bytes do arquivo contra a assinatura esperada."""
    cabecalho = arquivo.read(8)
    arquivo.seek(0)
    assinatura = _MAGIC_BYTES.get(extensao, b"")
    return cabecalho.startswith(assinatura)


def _extensao_valida(nome_arquivo: str) -> bool:
    """Verifica se a extensão do arquivo está na lista de permitidas.

    Args:
        nome_arquivo: Nome do arquivo com extensão.

    Returns:
        True se a extensão for permitida, False caso contrário.
    """
    extensoes = current_app.config.get("ALLOWED_EXTENSIONS", set())
    return "." in nome_arquivo and nome_arquivo.rsplit(".", 1)[1].lower() in extensoes


def _salvar_foto(arquivo: object) -> str | None:
    """Salva o arquivo de foto enviado e retorna o nome gerado.

    Args:
        arquivo: Objeto FileStorage do WTForms.

    Returns:
        Nome do arquivo salvo ou None se inválido/ausente.
    """
    if not arquivo or not arquivo.filename:
        return None
    if not _extensao_valida(arquivo.filename):
        return None
    extensao = arquivo.filename.rsplit(".", 1)[1].lower()
    if not _conteudo_valido(arquivo, extensao):
        return None
    nome_arquivo = f"{uuid.uuid4().hex}.{extensao}"
    pasta = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(pasta, exist_ok=True)
    arquivo.save(os.path.join(pasta, nome_arquivo))
    return nome_arquivo


def _excluir_foto(foto_path: str | None) -> None:
    """Remove o arquivo de foto do disco, se existir.

    Args:
        foto_path: Nome do arquivo salvo em UPLOAD_FOLDER, ou None.
    """
    if not foto_path:
        return
    caminho = os.path.join(current_app.config["UPLOAD_FOLDER"], foto_path)
    if os.path.isfile(caminho):
        os.remove(caminho)


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

    ja_avaliou = Avaliacao.query.filter_by(
        usuario_id=current_user.id, restaurante_id=restaurante_id
    ).first()
    if ja_avaliou:
        flash("Você já avaliou este restaurante.", "warning")
        return redirect(url_for("restaurantes.detalhe", restaurante_id=restaurante_id))

    form = AvaliacaoForm()
    if form.validate_on_submit():
        avaliacao = Avaliacao(
            usuario_id=current_user.id,
            restaurante_id=restaurante_id,
            nota_atendimento=int(form.nota_atendimento.data),
            nota_ambiente=int(form.nota_ambiente.data),
            nota_prato=int(form.nota_prato.data),
            nota_preco=int(form.nota_preco.data),
            comentario=form.comentario.data,
            foto_path=_salvar_foto(form.foto.data),
        )
        avaliacao.calcular_media()
        db.session.add(avaliacao)
        db.session.commit()
        flash("Avaliação registrada com sucesso!", "success")
        return redirect(url_for("restaurantes.detalhe", restaurante_id=restaurante_id))

    return render_template(
        "avaliacoes/nova.html",
        form=form,
        restaurante=restaurante,
    )


@avaliacoes_bp.route("/avaliacoes/<int:avaliacao_id>/editar", methods=["GET", "POST"])
@login_required
def editar(avaliacao_id: int) -> str:
    """Exibe o formulário pré-preenchido e salva alterações na avaliação.

    Apenas o autor da avaliação pode editá-la.

    Args:
        avaliacao_id: ID da avaliação a ser editada.

    Returns:
        Renderização do formulário de edição ou redirecionamento após sucesso.
    """
    avaliacao = db.session.get(Avaliacao, avaliacao_id)
    if not avaliacao:
        abort(404)
    if avaliacao.usuario_id != current_user.id:
        abort(403)

    form = AvaliacaoForm(obj=avaliacao)

    if form.validate_on_submit():
        nova_foto = _salvar_foto(form.foto.data)
        if nova_foto:
            _excluir_foto(avaliacao.foto_path)
            avaliacao.foto_path = nova_foto

        avaliacao.nota_atendimento = int(form.nota_atendimento.data)
        avaliacao.nota_ambiente = int(form.nota_ambiente.data)
        avaliacao.nota_prato = int(form.nota_prato.data)
        avaliacao.nota_preco = int(form.nota_preco.data)
        avaliacao.comentario = form.comentario.data
        avaliacao.calcular_media()
        db.session.commit()
        flash("Avaliação atualizada com sucesso!", "success")
        return redirect(
            url_for("restaurantes.detalhe", restaurante_id=avaliacao.restaurante_id)
        )

    # Pré-preenche os selects com os valores atuais
    if form.nota_atendimento.data is None:
        form.nota_atendimento.data = str(avaliacao.nota_atendimento)
        form.nota_ambiente.data = str(avaliacao.nota_ambiente)
        form.nota_prato.data = str(avaliacao.nota_prato)
        form.nota_preco.data = str(avaliacao.nota_preco)

    return render_template(
        "avaliacoes/editar.html",
        form=form,
        avaliacao=avaliacao,
        restaurante=avaliacao.restaurante,
    )


@avaliacoes_bp.route("/avaliacoes/<int:avaliacao_id>/excluir", methods=["POST"])
@login_required
def excluir(avaliacao_id: int) -> str:
    """Exclui a avaliação do usuário autenticado.

    Apenas o autor pode excluir. Método POST para evitar exclusão acidental via GET.

    Args:
        avaliacao_id: ID da avaliação a ser excluída.

    Returns:
        Redirecionamento para o detalhe do restaurante ou 403/404.
    """
    avaliacao = db.session.get(Avaliacao, avaliacao_id)
    if not avaliacao:
        abort(404)
    if avaliacao.usuario_id != current_user.id:
        abort(403)

    restaurante_id = avaliacao.restaurante_id
    _excluir_foto(avaliacao.foto_path)
    db.session.delete(avaliacao)
    db.session.commit()
    flash("Avaliação excluída.", "info")
    return redirect(url_for("restaurantes.detalhe", restaurante_id=restaurante_id))
