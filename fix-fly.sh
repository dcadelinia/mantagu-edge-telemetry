cho "Logs:   fly logs -a $APP"
#!/usr/bin/env bash
# fix-fly.sh - Fix workspace paths and deploy health status context
set -e

echo "⚙️ Cleaning up deployment configuration drift..."

# Ensure executable permissions on any build scripts
chmod +x "$0" 2>/dev/null || true

# Check for correct configuration paths
if [ ! -f "deploy/fly.toml" ] && [ -f "fly.toml" ]; then
    echo "📦 Synchronizing root fly.toml configuration layout..."
    mkdir -p deploy
    cp fly.toml deploy/fly.toml
fi

echo "🚀 Workspace optimized! Ready to run: fly deploy --config deploy/fly.toml"
