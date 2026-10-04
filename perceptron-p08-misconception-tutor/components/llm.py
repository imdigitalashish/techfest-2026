"""Minimal LLM client for GitHub Models (OpenAI-compatible), with on-disk cache and backoff.

Auth: GITHUB_TOKEN env var, else `gh auth token`. Never logs the token.
Cache: .cache/llm/<sha256>.json so evaluation reruns are free and reproducible.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import time

import requests

ENDPOINT = "https://models.github.ai/inference/chat/completions"
ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "llm"
_TOKEN: str | None = None


class RateLimited(RuntimeError):
    pass


def _token() -> str:
    global _TOKEN
    if _TOKEN is None:
        _TOKEN = os.environ.get("GITHUB_TOKEN") or subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    return _TOKEN


def chat(messages: list[dict], model: str = "openai/gpt-4.1-mini", temperature: float = 0.0,
         max_tokens: int = 400, json_mode: bool = False, seed: int = 0, max_wait_s: float = 120.0) -> str:
    body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())["content"]
    waited = 0.0
    for attempt in range(8):
        r = requests.post(ENDPOINT, json=body, timeout=90,
                          headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"})
        if r.status_code == 429 or r.status_code >= 500:
            delay = float(r.headers.get("retry-after", 2 ** attempt * 4))
            if delay > max_wait_s or waited + delay > 4 * max_wait_s:
                raise RateLimited(f"HTTP {r.status_code}; retry-after={delay}s")
            time.sleep(delay)
            waited += delay
            continue
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"model": model, "content": content}))
        return content
    raise RateLimited("exhausted retries")
