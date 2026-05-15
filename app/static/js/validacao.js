"use strict";

/**
 * Módulo de validação client-side para os formulários do Mesa Certa.
 *
 * Uso nos templates:
 *   <input data-v="required email" data-v-label="E-mail">
 *   <input data-v="required" data-v-min="6" data-v-label="Senha">
 *   <input data-v="required confirm" data-v-confirm="senha" data-v-label="Confirmar senha">
 *
 * Atributos data-v:
 *   required  — campo não pode estar vazio
 *   email     — valida formato de e-mail com regex
 *   confirm   — verifica se o valor coincide com o campo referenciado por data-v-confirm
 *
 * Atributos auxiliares:
 *   data-v-label    — nome do campo para mensagens (fallback: placeholder ou "Campo")
 *   data-v-min      — comprimento mínimo (inteiro)
 *   data-v-max      — comprimento máximo (inteiro, além do maxlength HTML)
 *   data-v-confirm  — id do campo cujo valor deve coincidir
 */
const Validacao = (() => {
    const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const COR_ERRO = "#dc3545";
    const COR_OK   = "#28a745";

    function labelDoCampo(campo) {
        return (
            campo.dataset.vLabel ||
            campo.placeholder ||
            campo.name ||
            "Campo"
        );
    }

    function mostrarErro(campo, mensagem) {
        campo.style.borderColor = COR_ERRO;
        campo.style.boxShadow   = `0 0 0 3px rgba(220,53,69,.12)`;

        const div = document.createElement("div");
        div.className = "v-erro";
        div.style.cssText =
            "font-size:11px;color:#dc3545;margin-top:3px;display:flex;align-items:center;gap:4px;";
        div.innerHTML = `<span style="font-size:13px;">✕</span> ${mensagem}`;
        campo.closest(".mb-3, .mb-4, .col-6, .col") ?.appendChild(div) ||
            campo.parentNode.appendChild(div);
    }

    function marcarOk(campo) {
        campo.style.borderColor = COR_OK;
        campo.style.boxShadow   = `0 0 0 3px rgba(40,167,69,.1)`;
    }

    function limparErrosCampo(campo) {
        const container =
            campo.closest(".mb-3, .mb-4, .col-6, .col") || campo.parentNode;
        container.querySelectorAll(".v-erro").forEach((el) => el.remove());
        campo.style.borderColor = "";
        campo.style.boxShadow   = "";
    }

    function validarCampo(campo) {
        const regras  = (campo.dataset.v || "").split(/\s+/);
        const label   = labelDoCampo(campo);
        const valor   = campo.value;
        const valorTrim = valor.trim();

        if (regras.includes("required") && valorTrim === "") {
            mostrarErro(campo, `${label} é obrigatório.`);
            return false;
        }

        if (valorTrim !== "" && regras.includes("email")) {
            if (!REGEX_EMAIL.test(valorTrim)) {
                mostrarErro(campo, "Informe um e-mail válido (ex.: nome@dominio.com).");
                return false;
            }
        }

        const min = parseInt(campo.dataset.vMin, 10);
        if (!isNaN(min) && valorTrim.length > 0 && valorTrim.length < min) {
            mostrarErro(campo, `${label} deve ter no mínimo ${min} caracteres.`);
            return false;
        }

        const max = parseInt(campo.dataset.vMax, 10);
        if (!isNaN(max) && valorTrim.length > max) {
            mostrarErro(campo, `${label} deve ter no máximo ${max} caracteres.`);
            return false;
        }

        if (regras.includes("confirm")) {
            const alvoId  = campo.dataset.vConfirm;
            const alvo    = alvoId ? document.getElementById(alvoId) : null;
            if (alvo && valor !== alvo.value) {
                mostrarErro(campo, "As senhas não coincidem.");
                return false;
            }
        }

        if (valorTrim !== "") marcarOk(campo);
        return true;
    }

    /**
     * Inicializa validação em um formulário.
     *
     * @param {string} formId - id do elemento <form>.
     * @param {Object} [opcoes] - opções opcionais.
     * @param {boolean} [opcoes.validarAoSair=true] - valida campo no evento blur.
     * @param {boolean} [opcoes.limparAoDigitar=true] - remove erro ao digitar.
     */
    function init(formId, opcoes = {}) {
        const form = document.getElementById(formId);
        if (!form) return;

        const { validarAoSair = true, limparAoDigitar = true } = opcoes;

        form.addEventListener("submit", (e) => {
            const campos  = [...form.querySelectorAll("[data-v]")];
            let formValido = true;

            campos.forEach((c) => {
                limparErrosCampo(c);
                if (!validarCampo(c)) formValido = false;
            });

            if (!formValido) {
                e.preventDefault();
                const primeiro = form.querySelector("[data-v]");
                if (primeiro) primeiro.focus();
            }
        });

        if (validarAoSair) {
            form.querySelectorAll("[data-v]").forEach((campo) => {
                campo.addEventListener("blur", () => {
                    limparErrosCampo(campo);
                    validarCampo(campo);
                });
            });
        }

        if (limparAoDigitar) {
            form.querySelectorAll("[data-v]").forEach((campo) => {
                campo.addEventListener("input", () => limparErrosCampo(campo));
            });
        }
    }

    return { init };
})();


/* ─────────────────────────────────────────────────────────
   Modal de confirmação de exclusão
   ─────────────────────────────────────────────────────── */

/**
 * Exibe o modal de confirmação personalizado antes de excluir um item.
 *
 * @param {string} formId   - id do <form> de exclusão a ser submetido.
 * @param {string} nomeItem - nome do item que será excluído (exibido no modal).
 * @param {string} [tipo]   - tipo do item para o subtítulo (ex.: "avaliação", "restaurante").
 */
function confirmarExclusao(formId, nomeItem, tipo = "item") {
    const modal     = document.getElementById("modal-excluir");
    const nomeEl    = document.getElementById("modal-excluir-nome");
    const tipoEl    = document.getElementById("modal-excluir-tipo");
    const btnConfirm = document.getElementById("modal-excluir-confirmar");

    if (!modal) return;

    nomeEl.textContent = nomeItem;
    tipoEl.textContent = tipo;

    const bsModal = bootstrap.Modal.getOrCreate(modal);

    const handler = () => {
        document.getElementById(formId)?.submit();
    };

    btnConfirm.removeEventListener("click", btnConfirm._handler);
    btnConfirm._handler = handler;
    btnConfirm.addEventListener("click", handler);

    bsModal.show();
}
