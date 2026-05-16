#!/bin/bash
set -e

export PATH="$HOME/.local/bin:$PATH"

echo "Running database migrations..."
.venv/bin/flask db upgrade

echo "Starting gunicorn..."
exec .venv/bin/gunicorn --worker-class sync --workers 1 --timeout 60 --bind "0.0.0.0:${PORT:-5000}" run:app
