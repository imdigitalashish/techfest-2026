"""Record which rendered Markdown the exported PDF/PPTX/card were built from (run by deliverables/build.sh).

check_docs.py compares these hashes with the current rendered Markdown, so a stale export fails the check.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "deliverables"
SOURCES = ["zonal-deck.md", "presenter-card.md"]
EXPORTS = ["zonal-deck.pdf", "zonal-deck.pptx", "presenter-card.pdf"]
MANIFEST = D / "exports-manifest.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main() -> None:
    now = subprocess.check_output(["bash", "-c", "TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M IST'"], text=True).strip()
    data = {"built_at": now,
            "rendered_sources_sha256_16": {s: sha(D / s) for s in SOURCES},
            "exports_sha256_16": {e: sha(D / e) for e in EXPORTS if (D / e).exists()}}
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
    print("wrote", MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
