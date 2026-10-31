#!/usr/bin/env bash
# One-command deploy helpers for common clouds
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

usage() {
  cat <<EOF
Usage: $0 <target>

Targets:
  local       Build & run with docker compose
  fly         Deploy to Fly.io (global edge)
  render      Open Render blueprint deploy
  railway     Deploy to Railway
  gcp         Build & deploy to Cloud Run via Cloud Build
  k8s         Apply Kubernetes manifests (cluster must exist)

Examples:
  ./scripts/deploy.sh local
  ./scripts/deploy.sh fly
EOF
}

case "${1:-}" in
  local)
    docker compose up --build -d
    echo "API: http://localhost:8080/health"
    echo "Docs: http://localhost:8080/docs"
    ;;
  fly)
    command -v fly >/dev/null || { echo "Install flyctl: https://fly.io/docs/hands-on/install-flyctl/"; exit 1; }
    fly launch --config deploy/fly.toml --copy-config --yes || true
    fly deploy --config deploy/fly.toml
    ;;
  render)
    echo "Connect this repo at https://dashboard.render.com/select-repo?type=blueprint"
    echo "Blueprint file: deploy/render.yaml"
    ;;
  railway)
    command -v railway >/dev/null || { echo "Install Railway CLI: https://docs.railway.app/guides/cli"; exit 1; }
    railway up
    ;;
  gcp)
    command -v gcloud >/dev/null || { echo "Install gcloud CLI"; exit 1; }
    gcloud builds submit --config deploy/cloudbuild.yaml .
    ;;
  k8s)
    kubectl apply -f deploy/k8s/deployment.yaml
    echo "Update Ingress host and image registry as needed."
    ;;
  *)
    usage
    exit 1
    ;;
esac
