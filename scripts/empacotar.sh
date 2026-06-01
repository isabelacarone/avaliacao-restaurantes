#!/usr/bin/env bash
# Gera o .zip de entrega a partir do estado versionado no git.
#
# respeita o gitignore
set -euo pipefail

GRUPO="Grupo3"
PRODUTO="MesaCerta"
SAIDA="${GRUPO}_${PRODUTO}.zip"

cd "$(git rev-parse --show-toplevel)"

git archive --format=zip --output="${SAIDA}" HEAD

echo "Gerado: ${SAIDA}"
echo "Total de arquivos:"
unzip -l "${SAIDA}" | tail -n 1
