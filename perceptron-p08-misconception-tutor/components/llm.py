"""Minimal chat-completion client with on-disk cache and backoff.

Backends (chosen by environment):
- Azure OpenAI (default when AZURE_OPENAI_ENDPOINT is set): deployment name = model id without the
  "openai/" prefix; key read at runtime from AZURE_OPENAI_KEY or `az cognitiveservices account keys list`
  (resource from AZURE_OPENAI_RESOURCE, AZURE_OPENAI_RG) and kept in memory only.
- GitHub Models (fallback): GITHUB_TOKEN or `gh auth token`. NOTE 2026-10-04: models.github.ai returned
  HTTP 200 text/plain "OK" instead of completions from this machine, so it is not used for results.
Reasoning models (gpt-5*, o*) use max_completion_tokens + reasoning_effort and api-version 2025-04-01-preview;
non-reasoning request bodies are unchanged, so earlier cache entries stay valid.
Cache: .cache/llm/<sha256>.json (gitignored): content, usage, finish_reason.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import time
from datetime import datetime, timezone

import requests

GITHUB_ENDPOINT = "https://models.github.ai/inference/chat/completions"
AZURE_API_VERSION = "2024-10-21"
AZURE_API_VERSION_REASONING = "2025-04-01-preview"
REASONING_PREFIXES = ("gpt-5", "o1", "o3", "o4")
ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "llm"
_SECRETS: dict[str, str] = {}


class RateLimited(RuntimeError):
    pass


def backend() -> str:
    return "azure" if os.environ.get("AZURE_OPENAI_ENDPOINT") else "github"


def is_reasoning(model: str) -> bool:
    return model.split("/", 1)[-1].startswith(REASONING_PREFIXES)


def _azure_key() -> str:
    if "azure" not in _SECRETS:
        key = os.environ.get("AZURE_OPENAI_KEY")
        if not key:
            key = subprocess.run(
                ["az", "cognitiveservices", "account", "keys", "list",
                 "-n", os.environ.get("AZURE_OPENAI_RESOURCE", "tf26-p08-aoai-1004"),
                 "-g", os.environ.get("AZURE_OPENAI_RG", "rg-tf26-p08"), "--query", "key1", "-o", "tsv"],
                capture_output=True, text=True, check=True).stdout.strip()
        _SECRETS["azure"] = key
    return _SECRETS["azure"]


def _github_token() -> str:
    if "github" not in _SECRETS:
        _SECRETS["github"] = os.environ.get("GITHUB_TOKEN") or subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    return _SECRETS["github"]


def _request(body: dict, model: str) -> requests.Response:
    timeout = 600 if is_reasoning(model) else 90
    if backend() == "azure":
        ep = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
        dep = model.split("/", 1)[-1]
        ver = AZURE_API_VERSION_REASONING if is_reasoning(model) else AZURE_API_VERSION
        url = f"{ep}/openai/deployments/{dep}/chat/completions?api-version={ver}"
        b = {k: v for k, v in body.items() if k != "model"}
        return requests.post(url, json=b, timeout=timeout, headers={"api-key": _azure_key(), "Content-Type": "application/json"})
    return requests.post(GITHUB_ENDPOINT, json=body, timeout=timeout,
                         headers={"Authorization": f"Bearer {_github_token()}", "Content-Type": "application/json"})


def _body(messages, model, temperature, max_tokens, json_mode, seed, reasoning_effort) -> dict:
    if is_reasoning(model):
        body = {"model": model, "messages": messages, "max_completion_tokens": max_tokens}
        if reasoning_effort:
            body["reasoning_effort"] = reasoning_effort
    else:
        body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    return body


def chat_full(messages: list[dict], model: str = "openai/gpt-4.1-mini", temperature: float = 0.0,
              max_tokens: int = 400, json_mode: bool = False, seed: int = 0, reasoning_effort: str | None = None,
              max_wait_s: float = 120.0, use_cache: bool = True) -> dict:
    """Returns {"content", "usage", "finish_reason", "cached", "latency_s"}; raises RateLimited / requests.HTTPError.
    use_cache=False forces a fresh call (for run-to-run consistency) and does not overwrite the cache."""
    body = _body(messages, model, temperature, max_tokens, json_mode, seed, reasoning_effort)
    key = hashlib.sha256(json.dumps({"backend": backend(), **body}, sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if use_cache and path.exists():
        d = json.loads(path.read_text())
        return {"content": d["content"], "usage": d.get("usage"), "finish_reason": d.get("finish_reason"), "cached": True}
    waited = 0.0
    t0 = time.perf_counter()
    for attempt in range(8):
        r = _request(body, model)
        if r.status_code == 429 or r.status_code >= 500:
            delay = float(r.headers.get("retry-after", 2 ** attempt * 4))
            if delay > max_wait_s or waited + delay > 4 * max_wait_s:
                raise RateLimited(f"HTTP {r.status_code}; retry-after={delay}s")
            time.sleep(delay)
            waited += delay
            continue
        r.raise_for_status()
        try:
            j = r.json()
            choice = j["choices"][0]
            content = choice["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            delay = 2 ** attempt * 2
            if waited + delay > 4 * max_wait_s:
                raise RateLimited(f"unparseable response: HTTP {r.status_code} {r.headers.get('content-type')}")
            time.sleep(delay)
            waited += delay
            continue
        content = content or ""
        usage = {k: v for k, v in (j.get("usage") or {}).items() if k != "latency_checkpoint"}
        rec = {"backend": backend(), "model": model, "content": content, "usage": usage,
               "finish_reason": choice.get("finish_reason"), "ts": datetime.now(timezone.utc).isoformat()}
        latency = round(time.perf_counter() - t0 - waited, 3)
        if use_cache:
            CACHE.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(rec))
        return {"content": content, "usage": usage, "finish_reason": rec["finish_reason"], "cached": False, "latency_s": latency}
    raise RateLimited("exhausted retries")


def chat(messages: list[dict], model: str = "openai/gpt-4.1-mini", temperature: float = 0.0,
         max_tokens: int = 400, json_mode: bool = False, seed: int = 0, max_wait_s: float = 120.0) -> str:
    return chat_full(messages, model=model, temperature=temperature, max_tokens=max_tokens, json_mode=json_mode,
                     seed=seed, max_wait_s=max_wait_s)["content"]
