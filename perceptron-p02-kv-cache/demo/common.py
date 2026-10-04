"""Shared paths/helpers for the P2 demo (no torch import here)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parent
ROOT = DEMO.parent  # perceptron-p02-kv-cache/
DATA = ROOT / ".data"
WEB = DEMO / "web"
REPO_ID = "mlx-community/Llama-3.2-1B-Instruct-4bit"
REVISION = "08231374eeacb049a0eade7922910865b8fce912"  # the snapshot used on the VM (eval/results/env_artifacts.json)
for p in (ROOT / "eval", ROOT / "components" / "recall_on_demand"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def snapshot_dir() -> Path:
    hub = Path(os.environ.get("HF_HUB_CACHE") or Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub")
    snap = hub / f"models--{REPO_ID.replace('/', '--')}" / "snapshots" / REVISION
    if not (snap / "tokenizer.json").exists():
        raise FileNotFoundError(f"model snapshot {REVISION[:8]} not in the HF cache ({snap}); run demo/fetch.sh")
    return snap


def load_tokenizer():
    from transformers import AutoTokenizer
    from transformers.utils import logging as hf_logging
    hf_logging.set_verbosity_error()
    return AutoTokenizer.from_pretrained(str(snapshot_dir()))


def data_ready() -> tuple[bool, str]:
    need = ["haystack.txt", "llama32_1b_config.json", "llama32_1b_q4deq_fp16.safetensors"]
    missing = [n for n in need if not (DATA / n).exists()]
    if missing:
        return False, "missing .data/" + ", .data/".join(missing) + " (run demo/fetch.sh)"
    try:
        snapshot_dir()
    except FileNotFoundError as e:
        return False, str(e)
    return True, "ok"
