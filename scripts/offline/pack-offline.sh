#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TS="$(date +%Y%m%d-%H%M%S)"
BUNDLE_DIR="${1:-$ROOT_DIR/dist/offline-bundle-$TS}"

echo "[1/7] Prepare bundle directory: $BUNDLE_DIR"
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/artifacts/source"
mkdir -p "$BUNDLE_DIR/artifacts/python-wheels"
mkdir -p "$BUNDLE_DIR/artifacts/frontend"
mkdir -p "$BUNDLE_DIR/artifacts/docker"

echo "[2/7] Archive project source"
tar -czf "$BUNDLE_DIR/artifacts/source/project-src.tar.gz" \
  --exclude='.git' \
  --exclude='dist' \
  --exclude='venv' \
  --exclude='frontend/node_modules' \
  --exclude='backend/media' \
  --exclude='docker/onlyoffice/data' \
  --exclude='docker/onlyoffice/logs' \
  -C "$ROOT_DIR" .

echo "[3/7] Download backend wheels (offline pip packages)"
PYTHON_BIN="$ROOT_DIR/venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
  echo "ERROR: Python venv not found at $PYTHON_BIN"
  exit 1
fi
"$PYTHON_BIN" -m pip download --prefer-binary \
  -r "$ROOT_DIR/backend/requirements.txt" \
  -d "$BUNDLE_DIR/artifacts/python-wheels"

echo "[4/7] Pack frontend dependencies (node_modules)"
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo "ERROR: frontend/node_modules missing. Run 'cd frontend && npm install' first."
  exit 1
fi
tar -czf "$BUNDLE_DIR/artifacts/frontend/frontend-node_modules.tar.gz" \
  -C "$ROOT_DIR/frontend" \
  node_modules package.json package-lock.json

echo "[5/7] Export Docker image (OnlyOffice)"
docker image inspect onlyoffice/documentserver:7.4.0 >/dev/null
docker save -o "$BUNDLE_DIR/artifacts/docker/onlyoffice-documentserver-7.4.0.tar" \
  onlyoffice/documentserver:7.4.0

echo "[6/7] Copy installer and docs"
cp "$ROOT_DIR/scripts/offline/install-offline.sh" "$BUNDLE_DIR/install-offline.sh"
chmod +x "$BUNDLE_DIR/install-offline.sh"
cat > "$BUNDLE_DIR/README-OFFLINE.txt" <<'EOF'
Offline Bundle Usage
====================

1) Copy this bundle directory to the target machine (USB or LAN transfer).
2) On target machine:
   - Ensure Docker Desktop / Python 3.9+ / Node 20 are installed.
   - Run: ./install-offline.sh
3) After installation:
   - cd excel-gongxiang
   - OFFLINE=1 ./start.sh
EOF

echo "[7/7] Generate checksums"
(
  cd "$BUNDLE_DIR"
  find . -type f ! -name "SHA256SUMS.txt" -print0 | sort -z | xargs -0 shasum -a 256 > SHA256SUMS.txt
)

echo "DONE: $BUNDLE_DIR"
