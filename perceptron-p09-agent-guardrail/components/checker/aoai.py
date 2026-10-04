"""Azure OpenAI chat client for frontier-judge baselines (no SDK dependency; key only from the environment).

Env: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT (default gpt-4.1-mini).
Never write the key to a file; the eval scripts read it from the environment at run time.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

API_VERSION = "2024-10-21"
USAGE = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0}


def chat(system: str, user: str, max_tokens: int = 160, temperature: float = 0.0) -> tuple[str, float]:
    ep = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    dep = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
    url = f"{ep}/openai/deployments/{dep}/chat/completions?api-version={API_VERSION}"
    body = json.dumps({"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                       "max_tokens": max_tokens, "temperature": temperature}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json", "api-key": os.environ["AZURE_OPENAI_API_KEY"]})
    t = time.perf_counter()
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                j = json.loads(r.read())
            u = j.get("usage", {})
            USAGE["calls"] += 1
            USAGE["prompt_tokens"] += u.get("prompt_tokens", 0)
            USAGE["completion_tokens"] += u.get("completion_tokens", 0)
            return j["choices"][0]["message"]["content"] or "", (time.perf_counter() - t) * 1000
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 9:
                ra = e.headers.get("retry-after-ms") or e.headers.get("Retry-After")
                wait = float(ra) / 1000 if e.headers.get("retry-after-ms") else float(ra or 0)
                time.sleep(max(wait, min(60, 5 * 2 ** attempt)))
                continue
            if e.code == 400:  # content filter or bad request: treat as no verdict
                return "", (time.perf_counter() - t) * 1000
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < 9:
                time.sleep(2 ** attempt)
                continue
            raise
    return "", (time.perf_counter() - t) * 1000
