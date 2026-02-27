#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$BUNDLE_DIR/excel-gongxiang}"

echo "[1/7] Verify bundle structure"
test -f "$BUNDLE_DIR/artifacts/source/project-src.tar.gz"
test -f "$BUNDLE_DIR/artifacts/docker/onlyoffice-documentserver-7.4.0.tar"
test -d "$BUNDLE_DIR/artifacts/python-wheels"
test -f "$BUNDLE_DIR/artifacts/frontend/frontend-node_modules.tar.gz"

echo "[2/7] Extract source -> $TARGET_DIR"
mkdir -p "$TARGET_DIR"
tar -xzf "$BUNDLE_DIR/artifacts/source/project-src.tar.gz" -C "$TARGET_DIR"

echo "[3/7] Load Docker image (OnlyOffice)"
docker load -i "$BUNDLE_DIR/artifacts/docker/onlyoffice-documentserver-7.4.0.tar"

echo "[4/7] Setup Python venv and install backend deps offline"
cd "$TARGET_DIR"
python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip
./venv/bin/pip install --no-index --find-links "$BUNDLE_DIR/artifacts/python-wheels" \
  -r backend/requirements.txt

echo "[5/7] Restore frontend dependencies"
tar -xzf "$BUNDLE_DIR/artifacts/frontend/frontend-node_modules.tar.gz" -C frontend

echo "[6/7] Prepare env file"
if [ ! -f backend/.env ] && [ -f backend/.env.example ]; then
  cp backend/.env.example backend/.env
fi

echo "[7/7] Done"
echo "Next:"
echo "  cd \"$TARGET_DIR\""
echo "  OFFLINE=1 ./start.sh"
