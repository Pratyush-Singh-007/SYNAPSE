#!/usr/bin/env bash
# Quick launcher for Multi-Domain Tactical Decision-Making Trainer
set -e

# Portably detect script directory across bash, zsh, and sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-8000}"
export PORT

echo "======================================================================"
echo " IMMERSIVE MULTI-DOMAIN DECISION-MAKING TRAINER (DMUU)                "
echo " For Degraded & Contested Communication Environments                 "
echo "======================================================================"
echo " Tactical Terminal: http://localhost:${PORT}"
echo " Live AAR Debrief:  http://localhost:${PORT}/aar"
echo " Download PDF AAR:  http://localhost:${PORT}/api/aar/download-pdf"
echo " API Metrics JSON:  http://localhost:${PORT}/api/aar.json"
echo "======================================================================"

if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/server.py"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$SCRIPT_DIR/server.py"
else
    exec python "$SCRIPT_DIR/server.py"
fi
