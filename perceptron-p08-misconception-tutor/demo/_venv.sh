#!/usr/bin/env bash
# Shared by demo/run.sh and demo/smoke.sh: make sure the project venv (.venv, Python 3.11, CPU only) exists and has
# the packages the demo imports. Run from the project folder.
PKGS=(pydantic sympy numpy pandas pyarrow scikit-learn rank-bm25 requests pytest scipy)
if ! { [[ -x .venv/bin/python ]] && .venv/bin/python -c "import pydantic, sympy, numpy, pandas, pyarrow" 2>/dev/null; }; then
  echo "[demo] setting up .venv (one-off)…"
  if command -v uv >/dev/null 2>&1; then
    [[ -x .venv/bin/python ]] || nice -n 10 uv venv -q .venv --python 3.11
    nice -n 10 uv pip install -q --python .venv/bin/python "${PKGS[@]}"
  else
    [[ -x .venv/bin/python ]] || python3 -m venv .venv
    nice -n 10 .venv/bin/pip install -q "${PKGS[@]}"
  fi
fi
