#!/usr/bin/env bash
# Start the NeuroVista-DR prototype (backend + frontend) with a single command.
#
# Usage:
#   ./run.sh            # start both
#   ./run.sh backend    # start backend only
#   ./run.sh frontend   # start frontend only

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

start_backend() {
  echo "Starting NeuroVista-DR backend on :${BACKEND_PORT} ..."
  (cd "$ROOT" && exec uvicorn backend.main:app --host 0.0.0.0 --port "${BACKEND_PORT}")
}

start_frontend() {
  echo "Starting NeuroVista-DR frontend on :${FRONTEND_PORT} ..."
  (cd "$ROOT" && exec npm run dev -- --port "${FRONTEND_PORT}")
}

case "${1:-}" in
  backend) start_backend ;;
  frontend) start_frontend ;;
  *)
    # Trap so Ctrl+C stops both child processes.
    cleanup() { kill 0 2>/dev/null || true; }
    trap cleanup EXIT INT TERM
    start_backend &
    start_frontend &
    wait
    ;;
esac
