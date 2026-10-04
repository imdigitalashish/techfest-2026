"""Re-download every raw source listed in data/sources/*.yaml that has a `url` and a `local_copy` into the gitignored
.data/raw/ tree. Skips files already present. Needed for the quote verifier (components/ingestion/autoresearch/eval.py)
and the digitizers; the LCA engine and eval/eval.py run from committed YAML alone.

Usage (from ev-c2-green-auto-lca/):  python3 data/fetch/fetch_sources.py [--dry-run]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


def main() -> int:
    dry = "--dry-run" in sys.argv
    failed = 0
    for f in sorted((ROOT / "data/sources").glob("*.yaml")):
        for s in yaml.safe_load(f.read_text()) or []:
            url, lc = s.get("url", ""), s.get("local_copy", "")
            if not url or not lc or not lc.startswith(".data/"):
                continue
            dest = ROOT / lc
            if dest.exists() and dest.stat().st_size > 0:
                print(f"have  {lc}")
                continue
            print(f"fetch {lc} <- {url}")
            if dry:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            r = subprocess.run(["curl", "-sL", "-m", "300", "-A", UA, "-o", str(dest), url])
            if r.returncode != 0 or not dest.exists() or dest.stat().st_size == 0:
                print(f"FAILED {lc}")
                failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
