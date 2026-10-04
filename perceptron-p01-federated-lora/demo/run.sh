#!/usr/bin/env bash
# P1 demo: one command. Opens the page in the browser; committed results show at once (system python3 only).
# The LIVE panel enables itself when the project venv and the cached SmolLM2-135M exist (run demo/fetch.sh once).
# Options are passed to demo/server.py: --port N (default 8765, next free port is used), --no-browser.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo "python3 not found (needed for the stdlib demo server)"; exit 1; }
exec python3 demo/server.py "$@"
