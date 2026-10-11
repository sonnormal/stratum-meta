#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🚀 Stratum E2E Multi-Container Stack Provisioning"
echo "=================================================="

# 1. Check or start Host Ollama daemon
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "⚡ Host Ollama is not running. Starting ollama serve..."
    nohup /opt/homebrew/bin/ollama serve > /tmp/stratum-ollama.log 2>&1 &
    sleep 3
    if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Failed to start host Ollama daemon. Please run 'ollama serve' manually."
        exit 1
    fi
    echo "✅ Host Ollama daemon started."
else
    echo "✅ Host Ollama daemon is already active."
fi

# 2. Launch Docker Compose Stack
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/../deploy/docker-compose.yml"

echo "📦 Bringing up Docker multi-container stack..."
docker compose -f "$COMPOSE_FILE" up -d

# 3. Poll Healthchecks until green
echo "⏳ Waiting for healthchecks to pass..."
TIMEOUT=30
ELAPSED=0
until (curl -s -4 http://127.0.0.1:8000/healthz 2>/dev/null | grep -q "ok") && \
      (curl -s -4 http://127.0.0.1:8001/healthz 2>/dev/null | grep -q "ok"); do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "❌ Timed out waiting for containers to become healthy."
        exit 1
    fi
done

echo ""
echo "=================================================="
echo "✅ E2E Environment is LIVE & READY FOR ACCEPTANCE TESTING!"
echo "   • Perimeter Gateway  : http://127.0.0.1:8000"
echo "   • Cashflow Core      : http://127.0.0.1:8001"
echo "   • PostgreSQL Ledger  : 127.0.0.1:5432"
echo "   • Host Metal Ollama  : http://127.0.0.1:11434"
echo "=================================================="
