#!/usr/bin/env bash
# clear-world-signals.sh — Atomically clears pending-signals.json after
# the RightClamp agent has processed the signals into world events.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/scripts-config.env" 2>/dev/null || true

STATE_DIR="${OPENCLAW_HOME:-$HOME}/world-events"
SIGNALS_FILE="${STATE_DIR}/pending-signals.json"

if [ -f "$SIGNALS_FILE" ]; then
    tmp="${SIGNALS_FILE}.tmp"
    echo '[]' > "$tmp"
    mv "$tmp" "$SIGNALS_FILE"
    echo "ok: signals cleared"
else
    echo "ok: no signals file to clear"
fi
