#!/usr/bin/env bash
# One-time fetch for the LIVE panel (needs network once; afterwards everything runs offline):
#   1. project venv with the pinned requirements (Python 3.11, via uv)
#   2. SmolLM2-135M into the local Hugging Face cache (~270 MB)
# The committed-results page needs neither.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || { echo "uv not found: https://docs.astral.sh/uv/ (or: pip install uv)"; exit 1; }
if [[ ! -x .venv/bin/python ]]; then uv venv --python 3.11 .venv; fi
uv pip install -p .venv/bin/python -r requirements.txt
if .venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("HuggingFaceTB/SmolLM2-135M", local_files_only=True)
PY
then echo "SmolLM2-135M already cached"
else
  HF_HUB_OFFLINE=0 .venv/bin/python -c 'from huggingface_hub import snapshot_download; print(snapshot_download("HuggingFaceTB/SmolLM2-135M"))'
fi
echo "fetch done: run demo/run.sh"
