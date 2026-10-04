# Sourced by run.sh and smoke.sh: resolve the Python interpreter and the shared-Mac guards.
DEMO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(dirname "$DEMO")"
export PYTHONPATH="$PROJ${PYTHONPATH:+:$PYTHONPATH}" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 P10_DEVICE=cpu

now() { perl -MTime::HiRes=time -e 'printf "%.2f\n", time'; }

_has_deps() { "$1" -c "import numpy, pandas, pyarrow, scipy, sklearn, lightgbm, mapie" >/dev/null 2>&1; }

find_python() {  # sets PY to a ready interpreter, or returns 1
  if [ -n "${P10_PYTHON:-}" ]; then PY="$P10_PYTHON"; return 0; fi
  for c in "$PROJ/.venv/bin/python" "$DEMO/.venv/bin/python"; do
    if [ -x "$c" ] && _has_deps "$c"; then PY="$c"; return 0; fi
  done
  return 1
}

resolve_python() {  # ready interpreter, else one-time setup of demo/.venv (setup.sh runs only this)
  find_python && return
  command -v uv >/dev/null || { echo "[demo] no usable Python: set P10_PYTHON, or install uv (https://docs.astral.sh/uv/)" >&2; exit 1; }
  echo "[demo] creating $DEMO/.venv with uv (offline wheel cache first)…"
  uv venv -q --python 3.11 "$DEMO/.venv"
  uv pip install -q --compile-bytecode --python "$DEMO/.venv/bin/python" --offline -r "$DEMO/requirements.txt" 2>/dev/null \
    || uv pip install -q --compile-bytecode --python "$DEMO/.venv/bin/python" -r "$DEMO/requirements.txt"
  PY="$DEMO/.venv/bin/python"
  # first load of freshly installed native libraries is slow on macOS (one-time scan); pay it here, once
  echo "[demo] first load of the new libraries (one-time)…"
  "$PY" -c "import numpy, pandas, pyarrow, scipy, sklearn, lightgbm, mapie" \
    && ("$PY" -c "import torch, transformers" >/dev/null 2>&1 || echo "[demo] torch/transformers unavailable: VADER fallback")
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
