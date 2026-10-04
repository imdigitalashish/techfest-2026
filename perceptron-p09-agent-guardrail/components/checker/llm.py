"""Local LLM access (MLX). One shared loader; deterministic (greedy) decoding."""
from __future__ import annotations

import json
import re
import time

FAST = "mlx-community/Qwen3-1.7B-4bit"
CAREFUL = "mlx-community/Qwen3-8B-4bit"
_MODELS: dict[str, tuple] = {}


def _load(name: str):
    if name not in _MODELS:
        from mlx_lm import load
        _MODELS[name] = load(name)
    return _MODELS[name]


def chat(name: str, system: str, user: str, max_tokens: int = 160) -> tuple[str, float]:
    from mlx_lm import generate
    model, tok = _load(name)
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    t = time.perf_counter()
    out = generate(model, tok, prompt=prompt, max_tokens=max_tokens)
    return out, (time.perf_counter() - t) * 1000


def parse_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}
