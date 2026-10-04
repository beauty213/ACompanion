#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Error: .venv virtual environment not found in $REPO_DIR"
    exit 1
fi

export PYTHONPATH="$REPO_DIR"
echo "⚓ Starting Anchor Backend on http://127.0.0.1:8001 ..."
uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
