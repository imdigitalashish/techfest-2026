#!/usr/bin/env bash
# VM setup for the PyTorch CPU harness: torch (CPU wheel) + transformers, and export of the exact weights
# used on Apple silicon (mlx-community/Llama-3.2-1B-Instruct-4bit, dequantised) to safetensors for torch.
set -e
UV=~/.local/bin/uv
PY=~/venv/bin/python
$UV pip install -q --python $PY "torch==2.10.0" --index-url https://download.pytorch.org/whl/cpu
$UV pip install -q --python $PY "transformers==5.8.0" safetensors
mkdir -p ~/p02/.data
$PY - <<'PY'
import glob, json
import mlx.core as mx
from mlx.utils import tree_flatten
from mlx_lm import load
from mlx_lm.utils import dequantize_model
m, _ = load("mlx-community/Llama-3.2-1B-Instruct-4bit")
m = dequantize_model(m)
w = dict(tree_flatten(m.parameters()))
mx.save_safetensors("/home/azureuser/p02/.data/llama32_1b_q4deq_fp16.safetensors", w)
snap = glob.glob("/home/azureuser/.cache/huggingface/hub/models--mlx-community--Llama-3.2-1B-Instruct-4bit/snapshots/*/")[0]
json.dump(json.load(open(snap + "config.json")), open("/home/azureuser/p02/.data/llama32_1b_config.json", "w"))
print("exported", len(w), "tensors; dtypes", {str(v.dtype) for v in w.values()}, "snapshot", snap)
PY
$PY - <<'PY'
import time, torch, transformers
print("torch", torch.__version__, "transformers", transformers.__version__, "threads", torch.get_num_threads())
a, b = torch.randn(2048, 2048), torch.randn(2048, 8192)
a @ b
t = time.time()
for _ in range(3):
    a @ b
print("torch fp32 GEMM GFLOP/s", round(3 * 2 * 2048 * 2048 * 8192 / (time.time() - t) / 1e9, 1))
PY
