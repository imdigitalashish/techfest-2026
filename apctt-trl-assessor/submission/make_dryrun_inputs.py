"""Dry-run inputs: 100 held-out TechPort docs (seeded sample of the frozen test split) + synthetic edge cases.
Gold labels go to <out>/../gold.json (outside the input folder, so the runner never sees them).
Usage: python submission/make_dryrun_inputs.py .data/dryrun/in
"""
from __future__ import annotations

import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    rows = {r["id"]: r for r in map(json.loads, (ROOT / ".data/techport/techport_trl.jsonl").open())}
    test = [int(x) for x in (ROOT / "eval/splits/techport_v0_trl_current_test_ids.txt").read_text().split()]
    test = [i for i in test if i in rows and rows[i]["trl_current"]]
    gold = {}
    for i in random.Random(20261004).sample(test, 100):
        r = rows[i]
        (out / f"techport_{i}.txt").write_text(f"{r['title']}\n\n{r['description']}\n\n{r['benefits']}")
        gold[f"techport_{i}"] = r["trl_current"]
    # SYNTHETIC edge cases (written by us; no gold labels)
    (out / "edge_empty.txt").write_text("")
    (out / "edge_nonenglish.txt").write_text("Ce prototype a été démontré dans un environnement pertinent. 这是一个测试。")
    (out / "edge_huge.txt").write_text("The breadboard was validated in the laboratory. " * 20000)
    (out / "edge_page.html").write_text("<html><body><h1>Pump</h1><p>A pilot plant was operated in the field.</p></body></html>")
    (out / "edge_binary.pdf").write_bytes(b"%PDF-1.4 not really a pdf \x00\x01\x02")
    src = out / f"techport_{next(iter(gold)).split('_')[1]}.txt"
    if shutil.which("cupsfilter"):  # macOS: text -> real PDF to exercise the PDF path
        pdf = subprocess.run(["cupsfilter", str(src)], capture_output=True).stdout
        if pdf.startswith(b"%PDF"):
            (out / "edge_real.pdf").write_bytes(pdf)
    (out.parent / "gold.json").write_text(json.dumps(gold))
    print(f"{len(gold)} gold docs + {len(list(out.glob('edge_*')))} edge cases -> {out}")


if __name__ == "__main__":
    main()
