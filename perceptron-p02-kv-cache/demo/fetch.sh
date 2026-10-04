#!/usr/bin/env bash
# One-time fetch for the P2 demo's LIVE mode (REPLAY needs nothing). After it, the demo runs offline.
# Creates gitignored perceptron-p02-kv-cache/.data/ and verifies every file against eval/results/env_artifacts.json:
#   haystack.txt                      WikiText-103 paragraphs (eval/fetch_haystack.py, HF dataset cache)
#   llama32_1b_q4deq_fp16.safetensors mlx-community/Llama-3.2-1B-Instruct-4bit @ 08231374, dequantised by MLX
#   llama32_1b_config.json            exactly as eval/azure/setup_torch.sh exports them (~2.5 GB, ~1 min)
# The weights' bytes depend on MLX's backend rounding (same mlx 0.32.3 / mlx-lm 0.32.0 everywhere):
#   e8f57b3c... VM export (mlx[cpu], Linux x86; env_artifacts.json)
#   c2d5994a... Apple-silicon export (Metal) == correctly rounded fp16(q*scale+bias) (numpy fp32/fp64 check)
#   2ec681e2... MLX CPU backend on arm64 (rounds q*scale to fp16 first); not used
# Live numbers are computed on whichever accepted export is present; smoke.sh checks it reproduces committed rows.
# Options (env):
#   P02_DATA_FROM=/path/.data    reuse an already verified .data (APFS clone: instant, no extra disk)
#   P02_MLX_PYTHON=/path/python  a python with mlx==0.32.3 + mlx-lm==0.32.0 (else .venv is created; needs network)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
P="$(dirname "$HERE")"
D="$P/.data"
REPO_ID="mlx-community/Llama-3.2-1B-Instruct-4bit"
REV="08231374eeacb049a0eade7922910865b8fce912"
mkdir -p "$D"

want() { python3 -c "import json,sys; print(json.load(open('$P/eval/results/env_artifacts.json'))['sha256']['.data/'+sys.argv[1]])" "$1"; }
APPLE_W="c2d5994a1a6576de5171a5f05f58e3306d0b196505f50d0bcdb8d0b781a14344"
ok() {
  [ -f "$D/$1" ] || return 1
  local h; h="$(shasum -a 256 "$D/$1" | cut -d' ' -f1)"
  [ "$h" = "$(want "$1")" ] || { [ "$1" = llama32_1b_q4deq_fp16.safetensors ] && [ "$h" = "$APPLE_W" ]; }
}
FILES="haystack.txt llama32_1b_config.json llama32_1b_q4deq_fp16.safetensors"

if [ -n "${P02_DATA_FROM:-}" ]; then
  for f in $FILES; do
    if ! ok "$f" && [ -f "$P02_DATA_FROM/$f" ]; then rm -f "$D/$f"; cp -c "$P02_DATA_FROM/$f" "$D/$f" 2>/dev/null || cp "$P02_DATA_FROM/$f" "$D/$f"; fi
  done
fi

ok haystack.txt || python3 "$P/eval/fetch_haystack.py"
ok haystack.txt || { echo "fetch: haystack.txt sha256 mismatch" >&2; exit 1; }

if ! { ok llama32_1b_config.json && ok llama32_1b_q4deq_fp16.safetensors; }; then
  SNAP="$(HF_HUB_OFFLINE=1 python3 -c "from huggingface_hub import snapshot_download as s; print(s('$REPO_ID', revision='$REV'))" 2>/dev/null \
          || python3 -c "from huggingface_hub import snapshot_download as s; print(s('$REPO_ID', revision='$REV'))")"
  MLX_PY="${P02_MLX_PYTHON:-$P/.venv/bin/python}"
  if ! "$MLX_PY" -c "import mlx_lm" 2>/dev/null; then
    echo "fetch: creating $P/.venv with mlx==0.32.3 mlx-lm==0.32.0 (network)"
    python3 -m venv "$P/.venv" && "$P/.venv/bin/pip" install -q "mlx==0.32.3" "mlx-lm==0.32.0"
    MLX_PY="$P/.venv/bin/python"
  fi
  echo "fetch: exporting dequantised fp16 weights from $SNAP (MLX, ~1 min)"
  nice -n 10 "$MLX_PY" - "$SNAP" "$D" <<'PY'
import json, sys
import mlx.core as mx
from mlx.utils import tree_flatten
from mlx_lm import load
from mlx_lm.utils import dequantize_model
snap, out = sys.argv[1].rstrip("/") + "/", sys.argv[2]
m, _ = load(snap)
m = dequantize_model(m)
w = dict(tree_flatten(m.parameters()))
mx.save_safetensors(out + "/llama32_1b_q4deq_fp16.safetensors", w)
json.dump(json.load(open(snap + "config.json")), open(out + "/llama32_1b_config.json", "w"))
print("exported", len(w), "tensors from", snap)
PY
fi
for f in $FILES; do ok "$f" || { echo "fetch: $f sha256 does not match eval/results/env_artifacts.json" >&2; exit 1; }; done
echo "fetch: OK — .data verified (sha256: env_artifacts.json, or the Apple-silicon weights export noted above)"
