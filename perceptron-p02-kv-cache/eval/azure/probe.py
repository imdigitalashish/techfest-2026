"""CPU speed probe for the kvbench engine on the Azure VM (MLX CPU backend).

Times one forward pass over N tokens (prefill-like) and one single-token step (decode-like) for the
4-bit weights as shipped, and for the same weights dequantised to bf16 and fp32.
Usage: python eval/azure/probe.py [--n 512]
"""
import argparse
import os
import platform
import time

import mlx.core as mx
from mlx_lm import load
from mlx_lm.utils import dequantize_model

MODEL_ID = "mlx-community/Llama-3.2-1B-Instruct-4bit"


def bench(model, n):
    ids = mx.array([list(range(1000, 1000 + n))])
    mx.eval(model(ids[:, :8]))  # warm-up
    t = time.time()
    mx.eval(model(ids))
    t_prefill = time.time() - t
    t = time.time()
    for _ in range(3):
        mx.eval(model(ids[:, :1]))
    return round(t_prefill, 2), round((time.time() - t) / 3, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=512)
    a = ap.parse_args()
    mx.set_default_device(mx.cpu)
    print(f"mlx {mx.__version__} | {platform.platform()} | cpus {os.cpu_count()}", flush=True)
    model, _ = load(MODEL_ID)
    print("q4    prefill_s, step_s:", bench(model, a.n), flush=True)
    model = dequantize_model(model)
    model.set_dtype(mx.bfloat16)
    print("bf16  prefill_s, step_s:", bench(model, a.n), flush=True)
    model.set_dtype(mx.float32)
    print("fp32  prefill_s, step_s:", bench(model, a.n), flush=True)


if __name__ == "__main__":
    main()
