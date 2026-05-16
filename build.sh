#!/bin/bash
set -e

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "Installing dependencies..."
uv sync

echo "Build complete!"
