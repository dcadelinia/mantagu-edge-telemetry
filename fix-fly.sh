#!/usr/bin/env bash
# Fix crashed Fly deploy: rebuild from THIS repo, force process command, allocate IPs
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
APP="${1:-mantagu-edge-telemetry}"

echo "==> App: $APP"
echo "==> Using Dockerfile + fly.toml from this package (uvicorn on 0.0.0.0:8080)"

# Ensure fly.toml is at root
cp -f deploy/fly.toml fly.toml 2>/dev/null || true

echo "==> Destroy broken machines (keeps app + volumes)"
fly machines list -a "$APP" --json 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); [print(m['id']) for m in d]" 2>/dev/null | \
  while read -r mid; do
    echo "    stopping/destroying $mid"
    fly machines stop "$mid" -a "$APP" 2>/dev/null || true
    fly machines destroy "$mid" -a "$APP" --force 2>/dev/null || true
  done || true

echo "==> Allocate public IPs if missing"
fly ips list -a "$APP" || true
fly ips allocate-v4 -a "$APP" --shared 2>/dev/null || fly ips allocate-v4 -a "$APP" 2>/dev/null || true
# Skip private_v6-only path that caused: org_slug is only supported with private_v6
fly ips allocate-v6 -a "$APP" 2>/dev/null || true

echo "==> Deploy building from local Dockerfile (not remote registry image)"
fly deploy -a "$APP" --config fly.toml --dockerfile Dockerfile --remote-only

echo "==> Status"
fly status -a "$APP"
echo ""
echo "Health: https://$APP.fly.dev/health"
echo "Docs:   https://$APP.fly.dev/docs"
echo "Logs:   fly logs -a $APP"
