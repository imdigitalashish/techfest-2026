"""Minimal chat-completion client with on-disk cache and backoff.

Backends (chosen by environment):
- Azure OpenAI (default when AZURE_OPENAI_ENDPOINT is set): deployment name = model id without the
  "openai/" prefix; key read at runtime from AZURE_OPENAI_KEY or `az cognitiveservices account keys list`
  (resource from AZURE_OPENAI_RESOURCE, AZURE_OPENAI_RG) and kept in memory only.
- GitHub Models (fallback): GITHUB_TOKEN or `gh auth token`. NOTE 2026-10-04: models.github.ai returned
  HTTP 200 text/plain "OK" instead of completions from this machine, so it is not used for results.
Cache: .cache/llm/<sha256>.json (gitignored) so reruns are free and reproducible.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import time

import requests

GITHUB_ENDPOINT = "https://models.github.ai/inference/chat/completions"
AZURE_API_VERSION = "2024-10-21"
ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "llm"
_SECRETS: dict[str, str] = {}


class RateLimited(RuntimeError):
    pass


def backend() -> str:
    return "azure" if os.environ.get("AZURE_OPENAI_ENDPOINT") else "github"


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
    if backend() == "azure":
        ep = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
        dep = model.split("/", 1)[-1]
        url = f"{ep}/openai/deployments/{dep}/chat/completions?api-version={AZURE_API_VERSION}"
        b = {k: v for k, v in body.items() if k != "model"}
        return requests.post(url, json=b, timeout=90, headers={"api-key": _azure_key(), "Content-Type": "application/json"})
    return requests.post(GITHUB_ENDPOINT, json=body, timeout=90,
                         headers={"Authorization": f"Bearer {_github_token()}", "Content-Type": "application/json"})


def chat(messages: list[dict], model: str = "openai/gpt-4.1-mini", temperature: float = 0.0,
         max_tokens: int = 400, json_mode: bool = False, seed: int = 0, max_wait_s: float = 120.0) -> str:
    body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    key = hashlib.sha256(json.dumps({"backend": backend(), **body}, sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())["content"]
    waited = 0.0
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
            content = r.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            delay = 2 ** attempt * 2
            if waited + delay > 4 * max_wait_s:
                raise RateLimited(f"unparseable response: HTTP {r.status_code} {r.headers.get('content-type')}")
            time.sleep(delay)
            waited += delay
            continue
        content = content or ""
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"backend": backend(), "model": model, "content": content}))
        return content
    raise RateLimited("exhausted retries")
