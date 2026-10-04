"""Build the self-contained submission folder .data/dist/trl_assessor_<version>/ and its zip.

Contents: trl_assessor/ (pipeline code, no tests) + trl_assessor/resources/{model.npz, rubric.json,
contracts.schema.json} + run.py + requirements.txt (pinned from this environment) + MANIFEST.json (sha256).
Usage: python submission/build.py [--version v0]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "components" / "skeleton"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--version", default="v0"); a = ap.parse_args()
    dist = ROOT / ".data" / "dist" / f"trl_assessor_{a.version}"
    if dist.exists():
        shutil.rmtree(dist)
    pkg, res = dist / "trl_assessor", dist / "trl_assessor" / "resources"
    res.mkdir(parents=True)
    for f in sorted(SRC.glob("*.py")):
        if not f.name.startswith("test_"):
            shutil.copy2(f, pkg / f.name)
    shutil.copy2(ROOT / "architecture/contracts/rubric_eu_nasa_v0.json", res / "rubric.json")
    shutil.copy2(ROOT / "architecture/contracts/contracts.schema.json", res / "contracts.schema.json")
    shutil.copy2(ROOT / ".data/models/thr_ridge_v0_trl_current.npz", res / "model.npz")
    (dist / "run.py").write_text(
        '"""Entry point: python run.py --in INPUT_DIR --out OUTPUT_DIR [--offline] [--rule median]"""\n'
        "import sys\n\nfrom trl_assessor.runner import main\n\nif __name__ == \"__main__\":\n    sys.exit(main())\n")
    (dist / "requirements.txt").write_text(f"numpy=={md.version('numpy')}\npypdf=={md.version('pypdf')}\n")
    manifest = {str(p.relative_to(dist)): sha256(p) for p in sorted(dist.rglob("*")) if p.is_file()}
    (dist / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    z = dist.with_suffix(".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(dist.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(dist.parent))
    size = sum(p.stat().st_size for p in dist.rglob("*") if p.is_file())
    print(f"built {dist} ({size/1e3:.0f} kB, {len(manifest)} files); zip {z.stat().st_size/1e3:.0f} kB sha256 {sha256(z)[:16]}")


if __name__ == "__main__":
    main()
