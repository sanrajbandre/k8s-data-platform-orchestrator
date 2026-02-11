#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

make dev-up
make backend-install
make worker-install
make frontend-install

echo "Run migrations: make backend-migrate"
echo "Seed defaults: cd backend && source .venv/bin/activate && python -m app.db.seed"
