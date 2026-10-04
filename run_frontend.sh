#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR/frontend"

echo "⚓ Starting Anchor Frontend on http://localhost:5173 ..."
npm run dev
