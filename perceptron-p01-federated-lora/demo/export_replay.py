"""Export everything the demo page shows into demo/web/data.js (stdlib only; runs before any venv exists).

Sources, all committed:
  eval/results/v2_canonical.json, v2_dropout_canonical.json, base_per_domain_smollm2-135m.json  (headline numbers)
  eval/results/logs/v2_dropout_<strategy>_s<seed>.json                                       (per-round replay)
  demo/validation/results.json + runs/ghost_s<seed>.json      (pre-registered validation, ghosts of the live run)
  demo/fallback/recorded_live_s0.jsonl                         (RECORDED live run: the scripted unplug, seed 0)
The page reads headline numbers only through the embedded canonical dicts, by key, and prints the key next to
each number. `python3 demo/export_replay.py --check` regenerates in memory and fails if data.js is stale.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
OUT = ROOT / "demo" / "web" / "data.js"
STRATS = ["fedavg_ab_homo", "ffa_lora", "flexlora", "anchor_full"]
LABEL = {"fedavg_ab_homo": "Starter: PEFT LoRA r8 + FedAvg", "ffa_lora": "FFA-LoRA (ICLR 2024)",
         "flexlora": "FlexLoRA (arXiv 2402.11505)", "anchor_full": "AnchorLoRA (ours)"}
SHORT = {"fedavg_ab_homo": "Starter", "ffa_lora": "FFA-LoRA", "flexlora": "FlexLoRA", "anchor_full": "AnchorLoRA"}
DOMAINS = ["wiki", "pycode", "cheaders", "readmes", "manpages"]
# mirrors components/device_simulator/profiles.py (demo/smoke_checks.py asserts the match)
DEVICES = [("c0", "workstation", "wiki", 2400, 16, 16), ("c1", "laptop", "pycode", 300, 8, 8),
           ("c2", "phone", "cheaders", 300, 4, 4), ("c3", "raspberry-pi", "readmes", 300, 2, 2),
           ("c4", "tablet", "manpages", 300, 4, 4)]
SYM = {"ok": "o", "partial": "p", "offline": "-", "late_discarded": "x"}
SEEDS = [0, 1, 2, 3, 4]


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def _r(x, nd=6):
    return None if x is None else round(float(x), nd)


def replay() -> dict:
    runs = {}
    for s in STRATS:
        runs[s] = {}
        for seed in SEEDS:
            f = RES / "logs" / f"v2_dropout_{s}_s{seed}.json"
            rows = []
            for e in json.loads(f.read_text()):
                a = e["aggregation"]
                rows.append({"round": e["round"],
                             "status": "".join(SYM[u["status"]] for u in sorted(e["updates"], key=lambda u: u["client_id"])),
                             "steps": [[u["steps_done"], u["planned_steps"]] for u in sorted(e["updates"], key=lambda u: u["client_id"])],
                             "memory": a.get("used_memory_for", []),
                             "norm_share_c0": _r(a["norm_share"].get("c0")) if a["norm_share"] else None,
                             "eval": {d: _r(v) for d, v in e["eval"]["per_domain_loss"].items()} if "eval" in e else None})
            runs[s][str(seed)] = {"file": rel(f), "rounds": rows}
    return {"runs": runs, "outage": {"device": "c4", "rounds": [5, 6, 7, 8, 9]},
            "logs_glob": "eval/results/logs/v2_dropout_<strategy>_s<seed>.json"}


def validation() -> dict | None:
    vf = ROOT / "demo" / "validation" / "results.json"
    if not vf.exists():
        return None
    res = json.loads(vf.read_text())
    ghosts = {}
    for seed in SEEDS:
        g = ROOT / "demo" / "validation" / "runs" / f"ghost_s{seed}.json"
        if not g.exists():
            continue
        G = json.loads(g.read_text())
        gd = {"file": rel(g), "untuned": G["untuned"]}
        for rec in G["records"]:  # full precision: the page checks live == ghost bit for bit
            gd.setdefault(rec["fed"], {})[str(rec["round"])] = rec["delta"]
        ghosts[str(seed)] = gd
    for row in res.get("rows", []):
        row.pop("curves", None)  # the band and the ghosts carry the curves the page draws
    return {"file": rel(vf), "results": res, "ghosts": ghosts}


def recorded() -> dict | None:
    f = ROOT / "demo" / "fallback" / "recorded_live_s0.jsonl"
    if not f.exists():
        return None
    return {"file": rel(f), "events": [json.loads(line) for line in f.read_text().splitlines() if line.strip()]}


def build() -> str:
    data = {
        "generated_by": "demo/export_replay.py",
        "labels": LABEL, "short": SHORT, "strategies": STRATS, "domains": DOMAINS, "seeds": SEEDS,
        "devices": [dict(zip(["id", "cls", "domain", "n", "rank", "steps"], d)) for d in DEVICES],
        "untuned": json.loads((RES / "base_per_domain_smollm2-135m.json").read_text()),
        "canonical": json.loads((RES / "v2_canonical.json").read_text()),
        "dropout_canonical": json.loads((RES / "v2_dropout_canonical.json").read_text()),
        "files": {"untuned": "eval/results/base_per_domain_smollm2-135m.json",
                  "canonical": "eval/results/v2_canonical.json",
                  "dropout_canonical": "eval/results/v2_dropout_canonical.json"},
        "replay": replay(), "validation": validation(), "recorded": recorded(),
    }
    return "window.P1 = " + json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False) + ";\n"


def main() -> None:
    text = build()
    if "--check" in sys.argv:
        ok = OUT.exists() and OUT.read_text() == text
        print("data.js up to date" if ok else "data.js is STALE: run python3 demo/export_replay.py")
        sys.exit(0 if ok else 1)
    OUT.write_text(text)
    print(f"wrote {rel(OUT)} ({len(text) // 1024} KB)")


if __name__ == "__main__":
    main()
