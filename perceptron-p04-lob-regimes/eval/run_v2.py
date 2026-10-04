"""v2 evaluation harness (pre-registered protocol: eval/PREREGISTRATION.md).

    cd perceptron-p04-lob-regimes
    nice -n 10 python eval/run_v2.py --stage dev --tag v2_dev --extra-specs eval/tuning_v2.json
    nice -n 10 python eval/run_v2.py --stage holdout --tag v2_holdout

Differences from eval/run_baseline.py (v1, kept for reproducibility): split v2 (eval/config_v2.py),
walk-forward contexts for policies with "wf", day-cluster paired bootstrap (primary) alongside the
moving-block bootstrap, comparisons against both the static model and textbook KS->refit, a
trading-edge table (taker, maker upper bound, fees from the official schedule), and per-day
regime descriptors.
"""
from __future__ import annotations

import argparse
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

from config_v2 import ALL_DAYS, CFG_V2, H_STEPS, SPLIT_V2, STEP_S  # noqa: E402
from run_baseline import load_events  # noqa: E402

from components.adapter import POLICIES, build_context, refit_context, run_episode  # noqa: E402
from components.evaluator import (block_bootstrap_ci, day_cluster_bootstrap_ci, exec_arrays,  # noqa: E402
                                  latency_summary, pointwise_logloss, score, trading_edge)
from components.features import build_features  # noqa: E402
from components.ingest import load_book_day  # noqa: E402
from components.labeler import make_labels  # noqa: E402

OUT = ROOT / "eval" / "results"
_G: dict = {}


def load_day(day: str):
    f = build_features(load_book_day(day), step_s=STEP_S)
    return f, make_labels(f, H_STEPS)


def _init(days, ctx, wf_ctx):
    os.nice(10)
    _G["days"], _G["ctx"], _G["wf"] = days, ctx, wf_ctx


def _work(args):
    name, spec, day = args
    f, l = _G["days"][day]
    ctx = _G["wf"][day] if spec.get("wf") else _G["ctx"]
    t0 = time.time()
    r = run_episode(name, f, l, ctx, spec)
    return name, day, r.p_up, [(a.step, a.detector, a.statistic) for a in r.alarms], r.step_ns, \
        r.extra["pred_ns"], r.extra["w_trace"], time.time() - t0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["dev", "holdout"], required=True)
    ap.add_argument("--policies", nargs="*", default=None)
    ap.add_argument("--extra-specs", default=None, help="JSON {name: spec} added to the run (dev tuning)")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    t_start = time.time()
    os.environ.setdefault("OMP_NUM_THREADS", "2")

    specs = {k: POLICIES[k] for k in (a.policies or CFG_V2["policies_" + a.stage])}
    if a.extra_specs:
        specs.update(json.loads(Path(a.extra_specs).read_text()))

    train = [load_day(d) for d in SPLIT_V2["train"]]
    ctx = build_context(train, CFG_V2)
    eval_days = SPLIT_V2[a.stage]
    frames = {d: load_day(d) for d in ALL_DAYS if d <= max(eval_days)}
    days = {d: frames[d] for d in eval_days}
    wf_ctx = {}
    if any(s.get("wf") for s in specs.values()):
        for d in eval_days:
            prior = [frames[x] for x in ALL_DAYS if x < d]
            wf_ctx[d] = refit_context(prior, ctx, stride=CFG_V2["wf_stride"])
    del frames
    events = load_events()

    jobs = [(n, s, d) for n, s in specs.items() for d in eval_days]
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_init, initargs=(days, ctx, wf_ctx)) as ex:
        outs = list(ex.map(_work, jobs, chunksize=1))
    preds, per = {}, {}
    for name, day, p, alarms, step_ns, pred_ns, w_trace, secs in outs:
        f, l = days[day]
        s = score(p, l.y, l.move_bps)
        s["alarms_by_detector"] = {}
        for st, det, stat in alarms:
            s["alarms_by_detector"][det] = s["alarms_by_detector"].get(det, 0) + 1
        s["alarm_utc"] = [(datetime.fromtimestamp(f.grid_us[st] / 1e6, timezone.utc).strftime("%H:%M:%S"), det)
                          for st, det, _ in alarms]
        ev = events.get(day, [])
        if ev:
            e_us = ev[0][1]
            win = (f.grid_us >= e_us - 1800 * 10**6) & (f.grid_us < e_us + 3600 * 10**6)
            s["event"] = {"id": ev[0][0], "window": score(p, l.y, l.move_bps, mask=win)}
        s["latency_pred"], s["latency_step"], s["wall_s"] = latency_summary(pred_ns), latency_summary(step_ns), secs
        per.setdefault(name, {})[day] = s
        preds[(name, day)] = p

    # Execution arrays (book as of decision + delay) for the trading-edge table.
    exs = {}
    for d in eval_days:
        b = load_book_day(d)
        f, l = days[d]
        for dl in CFG_V2["exec_delays_ms"]:
            exs[(d, dl)] = exec_arrays(b.recv_us, b.bid_px[:, 0], b.ask_px[:, 0], f.grid_us, f.mid, H_STEPS, f.step_us, dl)
        del b

    day_ids = np.concatenate([np.full(days[d][0].X.shape[0], i) for i, d in enumerate(eval_days)])
    Y = np.concatenate([days[d][1].y for d in eval_days])
    MV = np.concatenate([days[d][1].move_bps for d in eval_days])
    LL = {n: np.concatenate([pointwise_logloss(preds[(n, d)], days[d][1].y) for d in eval_days]) for n in specs}
    PP = {n: np.concatenate([preds[(n, d)] for d in eval_days]) for n in specs}
    refs = [r for r in ("static_snorm", "ks_refit", "regime_gated", "static_wf") if r in specs]
    fees = CFG_V2["fees_bps"]
    tau = {}
    if a.stage == "holdout":
        for f_ in ("v2_dev.json", "v2_dev_amend1.json"):
            if (OUT / f_).exists():
                tau.update(json.loads((OUT / f_).read_text()).get("tau_top_decile", {}))
        tau.update({k: tau[v] for k, v in CFG_V2.get("tau_alias", {}).items() if v in tau})
    summary = {}
    for n in specs:
        s = score(PP[n], Y, MV)
        for r in refs:
            if r == n:
                continue
            dd = LL[n] - LL[r]
            mean, lo, hi = block_bootstrap_ci(dd)
            s[f"vs_{r}"] = {"day_cluster": day_cluster_bootstrap_ci(dd, day_ids), "moving_block95": [lo, hi], "mean": mean}
        s["alarms_per_day"] = {}
        for d in eval_days:
            for det, c in per[n][d]["alarms_by_detector"].items():
                s["alarms_per_day"][det] = s["alarms_per_day"].get(det, 0) + c / len(eval_days)
        edge = {}
        for dl in CFG_V2["exec_delays_ms"]:
            parts = [trading_edge(preds[(n, d)], exs[(d, dl)], days[d][1].move_bps) for d in eval_days]
            nn = sum(x["n"] for x in parts)
            agg = {k: sum(x[k] * x["n"] for x in parts) / nn for k in ("gross_mid_bps", "taker_bps", "maker_ub_bps", "spread_bps")}
            agg["n"] = nn
            agg["break_even_fee_per_side_bps"] = agg["taker_bps"] / 2
            for tier, fz in fees.items():
                agg[f"taker_net_{tier}_bps"] = agg["taker_bps"] - 2 * fz["taker"]
                agg[f"maker_ub_net_{tier}_bps"] = agg["maker_ub_bps"] - 2 * fz["maker"]
            if n in tau:
                tp = [trading_edge(preds[(n, d)], exs[(d, dl)], days[d][1].move_bps,
                                   mask=np.abs(preds[(n, d)] - 0.5) >= tau[n]) for d in eval_days]
                tn = sum(x["n"] for x in tp)
                if tn:
                    agg["top_decile_rule"] = {"tau": tau[n], "n": tn, "share": tn / nn,
                                              "taker_bps": sum(x["taker_bps"] * x["n"] for x in tp if x["n"]) / tn,
                                              "gross_mid_bps": sum(x["gross_mid_bps"] * x["n"] for x in tp if x["n"]) / tn}
            edge[str(dl)] = agg
        s["edge"] = edge
        summary[n] = s
    out = {"stage": a.stage, "summary": summary, "per_day": per}
    if a.stage == "dev":
        out["tau_top_decile"] = {n: float(np.quantile(np.abs(PP[n] - 0.5), 0.9)) for n in specs}
    regime = {}
    for d in eval_days:
        f = days[d][0]
        regime[d] = {"rv_600s_bps_mean": float(f.col("rv_600s_bps").mean()), "spread_ticks_mean": float(f.spread_ticks.mean()),
                     "log_depth5_mean": float(f.col("log_depth5").mean()), "mid_mean": float(f.mid.mean()),
                     "tie_rate": float(np.isnan(days[d][1].y).mean())}
    out["regime_by_day"] = regime
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--", "components", "eval"], cwd=ROOT, text=True).strip())
    except Exception:
        commit, dirty = "unknown", True
    out["meta"] = {"created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "commit": commit,
                   "dirty_tree": dirty, "machine": f"{platform.machine()} {platform.platform()}",
                   "split": SPLIT_V2, "eval_days": eval_days, "h_steps": H_STEPS, "step_s": STEP_S,
                   "cfg": CFG_V2, "specs": specs, "runtime_s": round(time.time() - t_start, 1),
                   "command": "python eval/run_v2.py " + " ".join(sys.argv[1:])}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{a.tag}.json").write_text(json.dumps(out, indent=1, default=float))
    write_md(out, a.tag, eval_days, refs)
    print((OUT / f"{a.tag}.md").read_text())
    return 0


def write_md(out: dict, tag: str, eval_days: list[str], refs: list[str]) -> None:
    m, S = out["meta"], out["summary"]
    L = [f"# Results: `{tag}` (stage: {out['stage']})", "",
         f"- Command: `{m['command']}` (from `perceptron-p04-lob-regimes/`)",
         f"- Commit `{m['commit']}`{' (dirty tree)' if m['dirty_tree'] else ''} · {m['created_utc']} · {m['machine']} · runtime {m['runtime_s']} s",
         f"- Days ({len(eval_days)}): {', '.join(eval_days)}",
         "- Primary CI: paired day-cluster bootstrap (2000 resamples of whole days); secondary: moving-block bootstrap (600-step blocks).", ""]
    L += ["## Forecast quality (pooled)", "",
          "| policy | log-loss | AUC | acc | " + " | ".join(f"Δ vs {r} [97.5% day-cluster CI] (days better)" for r in refs) + " | alarms/day |",
          "|---|---|---|---|" + "---|" * len(refs) + "---|"]
    for n, s in S.items():
        cells = []
        for r in refs:
            v = s.get(f"vs_{r}")
            if v is None:
                cells.append("—")
            else:
                dc = v["day_cluster"]
                cells.append(f"{dc['mean']:+.4f} [{dc['ci97.5'][0]:+.4f}, {dc['ci97.5'][1]:+.4f}] ({dc['days_better']}/{dc['n_days']})")
        al = ", ".join(f"{k}: {v:.1f}" for k, v in s["alarms_per_day"].items()) or "0"
        L.append(f"| {n} | {s['logloss']:.4f} | {s['auc']:.4f} | {s['acc']:.4f} | " + " | ".join(cells) + f" | {al} |")
    L += ["", "## Is it tradable? Edge per signal in bps of mid (pooled; signal = sign(p − 0.5) every second, 10 s hold)", "",
          "Fees: Binance USDⓈ-M Regular User maker/taker 2.0/5.0 bps, VIP 9 0.0/1.7 bps (official fee page, accessed 2026-10-04). "
          "Taker = cross the spread on entry and exit at decision/horizon + delay. Maker = optimistic upper bound "
          "(both legs filled passively at the touch, no queue position or adverse selection).", "",
          "| policy | delay ms | gross mid | taker | spread | break-even fee/side | taker net Regular | taker net VIP9 | maker UB net Regular | maker UB net VIP9 | top-decile taker (share) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, s in S.items():
        for dl, e in s["edge"].items():
            td = e.get("top_decile_rule")
            tds = f"{td['taker_bps']:+.3f} ({td['share']:.0%})" if td else "—"
            L.append(f"| {n} | {dl} | {e['gross_mid_bps']:+.3f} | {e['taker_bps']:+.3f} | {e['spread_bps']:.3f} | "
                     f"{e['break_even_fee_per_side_bps']:+.3f} | {e['taker_net_regular_bps']:+.2f} | {e['taker_net_vip9_bps']:+.2f} | "
                     f"{e['maker_ub_net_regular_bps']:+.2f} | {e['maker_ub_net_vip9_bps']:+.2f} | {tds} |")
    L += ["", "## Per day: log-loss (alarms)", "", "| policy | " + " | ".join(d[2:] for d in eval_days) + " |",
          "|---|" + "---|" * len(eval_days)]
    for n in S:
        L.append(f"| {n} | " + " | ".join(f"{out['per_day'][n][d]['logloss']:.4f} ({sum(out['per_day'][n][d]['alarms_by_detector'].values())})"
                                         for d in eval_days) + " |")
    evd = [d for d in eval_days if "event" in out["per_day"][next(iter(S))][d]]
    if evd:
        L += ["", "## Scheduled-event windows (−30 min … +60 min): log-loss", "",
              "| policy | " + " | ".join(f"{d} ({out['per_day'][next(iter(S))][d]['event']['id']})" for d in evd) + " |",
              "|---|" + "---|" * len(evd)]
        for n in S:
            L.append(f"| {n} | " + " | ".join(f"{out['per_day'][n][d]['event']['window']['logloss']:.4f}" for d in evd) + " |")
    L += ["", "## Regime descriptors per day", "", "| day | mean rv_600s (bps) | mean spread (ticks) | mean log depth5 | mean mid | tie rate |",
          "|---|---|---|---|---|---|"]
    for d, r in out["regime_by_day"].items():
        L.append(f"| {d} | {r['rv_600s_bps_mean']:.2f} | {r['spread_ticks_mean']:.3f} | {r['log_depth5_mean']:.3f} | {r['mid_mean']:.0f} | {r['tie_rate']:.3f} |")
    L += ["", "## Online-step latency (Python reference, median over days)", "",
          "| policy | predict p50 µs | predict p99 µs | step p50 µs | step p99 µs |", "|---|---|---|---|---|"]
    for n in S:
        q = lambda key, k: float(np.median([out["per_day"][n][d][key][k] for d in eval_days]))
        L.append(f"| {n} | {q('latency_pred','p50_us'):.1f} | {q('latency_pred','p99_us'):.1f} | {q('latency_step','p50_us'):.1f} | {q('latency_step','p99_us'):.1f} |")
    (OUT / f"{tag}.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
