"""Content hash of the code that produces results (robust to rebases and dirty trees)."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ["components/checker", "components/kb", "components/tools", "components/redteam", "architecture/contracts", "eval/taubench",
        "eval/run_eval.py"]


def code_sha256() -> str:
    h = hashlib.sha256()
    files = []
    for c in CODE:
        p = ROOT / c
        files += sorted(p.rglob("*.py")) if p.is_dir() else [p]
    for f in files:
        h.update(str(f.relative_to(ROOT)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]
