"""End-to-end evaluation harness: every policy x every dev/holdout day, prequential.

    cd perceptron-p04-lob-regimes && python eval/run_baseline.py            # all policies
    python eval/run_baseline.py --policies static_snorm ks_refit --splits dev

Writes eval/results/baseline.json and eval/results/baseline.md (tables quoted in the docs).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from config import CFG, H_STEPS, SPLIT, STEP_S  # noqa: E402

from components.adapter import POLICIES, build_context, run_episode  # noqa: E402
from components.evaluator import (block_bootstrap_ci, detection_report, latency_summary,  # noqa: E402
                                  pointwise_logloss, score)
from components.features import build_features  # noqa: E402
from components.ingest import load_book_day  # noqa: E402
from components.labeler import make_labels  # noqa: E402

OUT = ROOT / "eval" / "results"
_G: dict = {}


def load_day(day: str):
    f = build_features(load_book_day(day), step_s=STEP_S)
    return f, make_labels(f, H_STEPS)


def load_events() -> dict[str, list[tuple[str, int]]]:
    ev: dict[str, list[tuple[str, int]]] = {}
    with open(ROOT / "data" / "events.csv") as fh:
        for r in csv.DictReader(fh):
            if not r["verified"].startswith("yes"):
                continue
            ts = datetime.fromisoformat(f"{r['date']}T{r['utc_time']}:00+00:00")
            ev.setdefault(r["date"], []).append((r["event_id"], int(ts.timestamp() * 1_000_000)))
    return ev


def _work(args):
    policy, day = args
    f, l = _G["days"][day]
    t0 = time.time()
    res = run_episode(policy, f, l, _G["ctx"])
    return policy, day, res.p_up, [(a.step, a.detector, a.statistic, a.detail) for a in res.alarms], \
        res.step_ns, res.extra["pred_ns"], time.time() - t0


def _init(days, ctx):
    _G["days"], _G["ctx"] = days, ctx


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policies", nargs="*", default=list(POLICIES))
    ap.add_argument("--splits", nargs="*", default=["dev", "holdout"])
    ap.add_argument("--tag", default="baseline")
    a = ap.parse_args()

    t_start = time.time()
    train = [load_day(d) for d in SPLIT["train"]]
    ctx = build_context(train, CFG)
    eval_days = [d for s in a.splits for d in SPLIT[s]]
    days = {d: load_day(d) for d in eval_days}
    events = load_events()

    insample = {}
    for (f, l), d in zip(train, SPLIT["train"]):
        insample[d] = score(ctx.head_static["static"].predict_batch(ctx.snorm.transform(f.X)), l.y, l.move_bps)

    jobs = [(p, d) for p in a.policies for d in eval_days]
    with ProcessPoolExecutor(max_workers=min(len(jobs), os.cpu_count() or 4), initializer=_init,
                             initargs=(days, ctx)) as ex:
        outs = list(ex.map(_work, jobs))

    per = {}
    preds = {}
    for policy, day, p, alarms, step_ns, pred_ns, secs in outs:
        f, l = days[day]
        s = score(p, l.y, l.move_bps)
        ev = events.get(day, [])
        if ev:
            e_us = ev[0][1]
            win = (f.grid_us >= e_us - 1800 * 10**6) & (f.grid_us < e_us + 3600 * 10**6)
            s["event_window"] = score(p, l.y, l.move_bps, mask=win)
        s["alarms"] = [{"step": st, "utc": datetime.fromtimestamp(f.grid_us[st] / 1e6, timezone.utc).strftime("%H:%M:%S"),
                        "detector": det, "stat": stat, **det_detail} for st, det, stat, det_detail in alarms]
        s["detection"] = detection_report([x[0] for x in alarms], f.grid_us, [e[1] for e in ev]) if alarms or ev else {}
        s["latency_pred"] = latency_summary(pred_ns)
        s["latency_step"] = latency_summary(step_ns)
        s["wall_s"] = secs
        per.setdefault(policy, {})[day] = s
        preds[(policy, day)] = p

    summary = {}
    for split in a.splits:
        for policy in a.policies:
            ll = np.concatenate([pointwise_logloss(preds[(policy, d)], days[d][1].y) for d in SPLIT[split]])
            ys = np.concatenate([days[d][1].y for d in SPLIT[split]])
            ps = np.concatenate([preds[(policy, d)] for d in SPLIT[split]])
            mv = np.concatenate([days[d][1].move_bps for d in SPLIT[split]])
            ref = np.concatenate([pointwise_logloss(preds[("static_snorm", d)], days[d][1].y) for d in SPLIT[split]]) \
                if "static_snorm" in a.policies else None
            s = score(ps, ys, mv)
            if ref is not None:
                mean, lo, hi = block_bootstrap_ci(ll - ref)
                s["dlogloss_vs_static"] = {"mean": mean, "ci95": [lo, hi]}
            s["n_alarms"] = int(sum(len(per[policy][d]["alarms"]) for d in SPLIT[split]))
            summary.setdefault(split, {})[policy] = s

    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    meta = {"created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "commit": commit,
            "machine": f"{platform.machine()} {platform.platform()}", "python": platform.python_version(),
            "split": SPLIT, "step_s": STEP_S, "h_steps": H_STEPS, "cfg": CFG, "runtime_s": round(time.time() - t_start, 1),
            "command": "python eval/run_baseline.py " + " ".join(sys.argv[1:])}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{a.tag}.json").write_text(json.dumps({"meta": meta, "insample_static": insample,
                                                   "summary": summary, "per_day": per}, indent=1, default=float))

    lines = [f"# Results: `{a.tag}`", "", f"- Command: `{meta['command']}` (from `perceptron-p04-lob-regimes/`)",
             f"- Commit: `{commit}` · {meta['created_utc']} · {meta['machine']} · runtime {meta['runtime_s']} s",
             f"- Data: Tardis.dev binance-futures BTCUSDT `book_snapshot_5` (free first-of-month days; MD5s in data/manifest.csv)",
             f"- Grid {STEP_S:g} s, horizon {H_STEPS} steps; label = sign of mid change (ties excluded); prequential, label delay enforced", "",
             "## In-sample (train days, static model) — the reference the model was fit on", "",
             "| day | n | logloss | acc | AUC |", "|---|---|---|---|---|"]
    for d, s in insample.items():
        lines.append(f"| {d} | {s['n']} | {s['logloss']:.4f} | {s['acc']:.4f} | {s['auc']:.4f} |")
    for split in a.splits:
        lines += ["", f"## {split}: {', '.join(SPLIT[split])}", "",
                  "| policy | logloss | Δ vs static (95% block-bootstrap CI) | acc | AUC | edge bps/signal | alarms |",
                  "|---|---|---|---|---|---|---|"]
        for policy in a.policies:
            s = summary[split][policy]
            dl = s.get("dlogloss_vs_static")
            dls = f"{dl['mean']:+.4f} [{dl['ci95'][0]:+.4f}, {dl['ci95'][1]:+.4f}]" if dl else "—"
            lines.append(f"| {policy} | {s['logloss']:.4f} | {dls} | {s['acc']:.4f} | {s['auc']:.4f} | {s['edge_bps']:+.3f} | {s['n_alarms']} |")
    lines += ["", "## Per day (logloss · AUC · alarms)", "", "| policy | " + " | ".join(eval_days) + " |",
              "|---|" + "---|" * len(eval_days)]
    for policy in a.policies:
        cells = [f"{per[policy][d]['logloss']:.4f} · {per[policy][d]['auc']:.3f} · {len(per[policy][d]['alarms'])}" for d in eval_days]
        lines.append(f"| {policy} | " + " | ".join(cells) + " |")
    ev_days = [d for d in eval_days if d in events]
    if ev_days:
        lines += ["", "## Scheduled-event windows (event −30 min … +60 min), logloss", "",
                  "| policy | " + " | ".join(f"{d} ({events[d][0][0]})" for d in ev_days) + " |", "|---|" + "---|" * len(ev_days)]
        for policy in a.policies:
            lines.append(f"| {policy} | " + " | ".join(f"{per[policy][d]['event_window']['logloss']:.4f}" for d in ev_days) + " |")
    lines += ["", "## Latency of the online step (Python reference implementation, single core)", "",
              "| policy | predict p50 µs | predict p99 µs | full step p50 µs | full step p99 µs |", "|---|---|---|---|---|"]
    for policy in a.policies:
        lp = np.median([per[policy][d]["latency_pred"]["p50_us"] for d in eval_days])
        lp99 = np.median([per[policy][d]["latency_pred"]["p99_us"] for d in eval_days])
        ls = np.median([per[policy][d]["latency_step"]["p50_us"] for d in eval_days])
        ls99 = np.median([per[policy][d]["latency_step"]["p99_us"] for d in eval_days])
        lines.append(f"| {policy} | {lp:.1f} | {lp99:.1f} | {ls:.1f} | {ls99:.1f} |")
    (OUT / f"{a.tag}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
