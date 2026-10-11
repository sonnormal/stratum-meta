#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "🛑 Stratum E2E Multi-Container Stack Teardown"
echo "=================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/../deploy/docker-compose.yml"

docker compose -f "$COMPOSE_FILE" down
echo "✅ E2E containers stopped and removed."
