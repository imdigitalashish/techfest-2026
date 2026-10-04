# Sourced by run.sh, setup.sh and smoke.sh: resolve the Python interpreter and the shared-Mac guards.
DEMO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(dirname "$DEMO")"
export PYTHONPATH="$PROJ${PYTHONPATH:+:$PYTHONPATH}"

now() { perl -MTime::HiRes=time -e 'printf "%.2f\n", time'; }

_has_deps() { "$1" -c "import pydantic, numpy, rank_bm25, yaml" >/dev/null 2>&1; }

find_python() {  # sets PY to a ready interpreter, or returns 1
  if [ -n "${P9_PYTHON:-}" ]; then PY="$P9_PYTHON"; return 0; fi
  if [ -x "$PROJ/.venv/bin/python" ] && _has_deps "$PROJ/.venv/bin/python"; then PY="$PROJ/.venv/bin/python"; return 0; fi
  return 1
}

resolve_python() {  # ready interpreter, else one-time `uv sync` of the project's locked environment (setup.sh runs only this)
  find_python && return
  command -v uv >/dev/null || { echo "[demo] no usable Python: set P9_PYTHON, or install uv (https://docs.astral.sh/uv/)" >&2; exit 1; }
  echo "[demo] creating $PROJ/.venv from uv.lock (offline wheel cache first)…"
  (cd "$PROJ" && (uv sync -q --frozen --offline 2>/dev/null || uv sync -q --frozen))
  PY="$PROJ/.venv/bin/python"
  _has_deps "$PY" || { echo "[demo] setup failed: $PY lacks pydantic/numpy/rank_bm25/pyyaml" >&2; exit 1; }
  CREATED=1
}

# Shared Mac: start heavy steps only when kern.memorystatus_level >= 30 (no-op where sysctl lacks the key).
wait_for_memory() {
  local lvl
  lvl=$(sysctl -n kern.memorystatus_level 2>/dev/null || echo 100)
  while [ "$lvl" -lt 30 ]; do
    echo "[demo] memory level $lvl < 30 — waiting (shared machine)…"
    sleep 5
    lvl=$(sysctl -n kern.memorystatus_level 2>/dev/null || echo 100)
  done
}

free_port() {
  local p="$1"
  while curl -s -o /dev/null "http://127.0.0.1:$p/" 2>/dev/null; do p=$((p + 1)); done
  echo "$p"
}
