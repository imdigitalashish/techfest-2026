"""Live replay build: run the committed policies on the replay days and write 10-minute aggregates for the page.

    cd perceptron-p04-lob-regimes && nice -n 10 python demo/build_replay.py --workers 3

Uses the v2 training context (12 days of 2023, build_context) and run_episode, unchanged. For each replay day
(demo/results/scoreboard.json -> replay_days) writes demo/.cache/replay_<day>.json (gitignored) containing ONLY
10-minute aggregates (OHLC candles of mid, mean log-loss per bin, regime-head share per bin) plus alarm
timestamps and per-day totals; demo/.cache/status.json tracks progress for the page.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime, timezone

import numpy as np

from common import (BIN_S, CACHE, CAL_Q, DEMO, EVAL_RESULTS, POLICIES, binned_mean, calibrated_thresholds,
                    ks_window_trace, load_day, mem_level, nice_self, pointwise_logloss, run_episode, score,
                    stop_episode, stop_ids, train_context)
from run_baseline import load_events  # noqa: E402

POLS = ["static_snorm", "static_enorm", "ks_refit", "regime_gated", "spike_gate"]
_G: dict = {}


def _init(ctx, cal, committed):
    nice_self()
    _G.update(ctx=ctx, cal=cal, committed=committed)


def _sec(f, step: int) -> int:
    return int((f.grid_us[step] // 10**6) % 86400)


def _day(day: str) -> dict:
    ctx, cal, com = _G["ctx"], _G["cal"], _G["committed"]
    t0 = time.time()
    f, l = load_day(day)
    T = f.X.shape[0]
    start_s = _sec(f, 0)
    off = start_s % BIN_S
    nb = int(np.ceil((T + off) / BIN_S))

    def bins(x: np.ndarray) -> list:  # align bins to wall-clock 10-minute boundaries (UTC)
        return binned_mean(np.concatenate([np.full(off, np.nan), x]), nb)

    mid = np.concatenate([np.full(off, np.nan), f.mid])
    candles = []
    for b in range(nb):
        seg = mid[b * BIN_S:(b + 1) * BIN_S]
        seg = seg[~np.isnan(seg)]
        if seg.size:
            candles.append([round(float(v), 2) for v in (seg[0], seg.max(), seg.min(), seg[-1])])
        else:
            candles.append(None)
    rv = f.X[:, ctx.names.index("rv_600s_bps")]
    reg = np.searchsorted(ctx.regime_edges, rv, side="right")
    reg_share = [[None] * nb for _ in range(3)]
    regp = np.concatenate([np.full(off, -1), reg])
    for b in range(nb):
        seg = regp[b * BIN_S:(b + 1) * BIN_S]
        seg = seg[seg >= 0]
        for r in range(3):
            reg_share[r][b] = round(float((seg == r).mean()), 4) if seg.size else None
    out = {"day": day, "start_utc_s": start_s - off, "bin_s": BIN_S, "n_bins": nb, "candles": candles,
           "regime_share": reg_share, "regime_edges_bps": [float(e) for e in ctx.regime_edges],
           "policies": {}, "stops": {}}
    for p in POLS:
        r = run_episode(p, f, l, ctx, POLICIES[p])
        ll = pointwise_logloss(r.p_up, l.y)
        s = score(r.p_up, l.y, l.move_bps)
        al = {}
        for a in r.alarms:
            al.setdefault(a.detector, []).append(_sec(f, a.step))
        rec = {"logloss": s["logloss"], "auc": s["auc"], "loss_bins": bins(ll), "alarms": al}
        c = com.get(p, {}).get(day)
        if c is not None:
            rec["committed"] = c
            rec["match"] = bool(abs(c - s["logloss"]) < 1e-9)
        out["policies"][p] = rec
    tr = ks_window_trace(f.X, ctx)
    out["ks_windows"] = {"n": int(tr["step"].size), "n_D1": int((tr["dmax"] >= 1.0).sum()),
                         "median_log10_pbon": float(np.median(np.log10(np.maximum(tr["pbon"], 1e-320))))}
    sweep = com.get("_sweep", {})
    for st in stop_ids():
        r = stop_episode(st, f, l, ctx, cal)
        ll = pointwise_logloss(r.p_up, l.y)
        s = score(r.p_up, l.y, l.move_bps)
        rec = {"logloss": s["logloss"], "loss_bins": bins(ll), "alarm_s": [_sec(f, a.step) for a in r.alarms]}
        if st.startswith("naive_"):
            rec["window_reject_share"] = float((tr["pbon"] < 10.0 ** (-int(st[6:]))).mean())
        c = sweep.get(st, {}).get(day)
        if c is not None:
            rec["committed_sweep"] = c
            rec["match"] = bool(abs(c - s["logloss"]) < 1e-9)
        out["stops"][st] = rec
    ev = load_events().get(day, [])
    out["events"] = [{"id": e[0], "utc_s": int((e[1] // 10**6) % 86400)} for e in ev]
    out["wall_s"] = round(time.time() - t0, 1)
    out["created_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (CACHE / f"replay_{day}.json").write_text(json.dumps(out))
    return {"day": day, "wall_s": out["wall_s"]}


def _status(st: dict) -> None:
    st["updated_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tmp = CACHE / "status.json.tmp"
    tmp.write_text(json.dumps(st))
    tmp.replace(CACHE / "status.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--days", nargs="*", default=None)
    ap.add_argument("--force", action="store_true", help="rebuild days already in the cache")
    a = ap.parse_args()
    nice_self()
    CACHE.mkdir(exist_ok=True)
    sb = json.loads((DEMO / "results" / "scoreboard.json").read_text())
    days = a.days or [r["day"] for r in sb["replay_days"]]
    st = {"days": {d: ("ready" if (CACHE / f"replay_{d}.json").exists() and not a.force else "queued") for d in days},
          "phase": "context"}
    todo = [d for d in days if st["days"][d] == "queued"]
    _status(st)
    if not todo:
        st["phase"] = "done"
        _status(st)
        print("replay cache already complete")
        return 0
    t0 = time.time()
    while mem_level() < 30:
        print("memory level < 30, waiting", flush=True)
        time.sleep(30)
    com = {}
    hj = json.loads((EVAL_RESULTS / "v2_holdout.json").read_text())["per_day"]
    aj = json.loads((EVAL_RESULTS / "v2_holdout_posthoc_ablation.json").read_text())["per_day"]
    for p in POLS:
        src = hj if p in hj else aj
        com[p] = {d: r["logloss"] for d, r in src[p].items()}
    sw = DEMO / "results" / "alarm_dial_sweep.json"
    if sw.exists():
        com["_sweep"] = {s["id"]: {d: r["logloss"] for d, r in s["per_day"].items()}
                         for s in json.loads(sw.read_text())["stops"]}
    ctx, train = train_context()
    cal = {q: calibrated_thresholds(ctx, train, q) for q in CAL_Q}
    del train
    print(f"context ready in {time.time() - t0:.0f} s", flush=True)
    st["phase"] = "replay"
    _status(st)
    pending = set()
    with ProcessPoolExecutor(max_workers=min(a.workers, 3), initializer=_init, initargs=(ctx, cal, com)) as ex:
        fut_day = {}
        while todo or pending:
            while todo and len(pending) < min(a.workers, 3):
                while mem_level() < 25:
                    print("memory level < 25, pausing", flush=True)
                    time.sleep(30)
                d = todo.pop(0)
                fu = ex.submit(_day, d)
                fut_day[fu] = d
                pending.add(fu)
                st["days"][d] = "building"
                _status(st)
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for fu in done:
                r = fu.result()
                st["days"][r["day"]] = "ready"
                _status(st)
                print(f"{r['day']} ready ({r['wall_s']} s)", flush=True)
    st["phase"] = "done"
    _status(st)
    print(f"replay build done in {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
