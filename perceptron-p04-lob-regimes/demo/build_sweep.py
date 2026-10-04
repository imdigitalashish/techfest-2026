"""Post-hoc demo sweep (NOT pre-registered): textbook KS->refit at every dial stop on the 22 held-out days.

    cd perceptron-p04-lob-regimes && nice -n 10 python demo/build_sweep.py --workers 3

Needs all 12 training days and all 22 holdout days in .data/ (data/fetch_batches.sh). Writes the committed
aggregate demo/results/alarm_dial_sweep.json: per-day log-loss and alarm counts, 22-day pooled log-loss and
paired day-cluster bootstrap deltas (committed evaluator), and the leave-one-train-day-out null rejection rate
of the naive test. No per-second series are written (Tardis ToS 9.2).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime, timezone

import numpy as np

from common import (CACHE, CAL_Q, CFG_V2, NAIVE_LOG10, POLICIES, RESULTS, ROOT, SPLIT_V2, calibrated_thresholds,
                    ks_pvalue_asymp, ks_stat_sorted, ks_window_trace, load_day, log10_separation_prob, mem_level,
                    nice_self, pointwise_logloss, run_episode, stop_episode, stop_ids, train_context)
from components.evaluator import day_cluster_bootstrap_ci  # noqa: E402

REFS = ["static_snorm", "static_enorm", "regime_gated"]
_G: dict = {}


def _init(ctx, cal_thr):
    nice_self()
    _G["ctx"], _G["cal"] = ctx, cal_thr


def _sum_n(ll: np.ndarray) -> tuple[float, int]:
    m = ~np.isnan(ll)
    return float(ll[m].sum()), int(m.sum())


def _day(day: str) -> dict:
    ctx, cal = _G["ctx"], _G["cal"]
    t0 = time.time()
    f, l = load_day(day)
    out = {"day": day, "refs": {}, "stops": {}}
    ref_ll = {}
    for r in REFS:
        ll = pointwise_logloss(run_episode(r, f, l, ctx, POLICIES[r]).p_up, l.y)
        ref_ll[r] = ll
        s, n = _sum_n(ll)
        out["refs"][r] = {"sum": s, "n": n, "logloss": s / n}
    tr = ks_window_trace(f.X, ctx)
    d1_at = dict(zip(tr["step"].tolist(), (tr["dmax"] >= 1.0).tolist()))
    out["windows"] = {"n": int(tr["step"].size), "n_D1": int((tr["dmax"] >= 1.0).sum()),
                      "n_p0": int((tr["pbon"] == 0.0).sum())}
    for st in stop_ids():
        r = stop_episode(st, f, l, ctx, cal)
        ll = pointwise_logloss(r.p_up, l.y)
        s, n = _sum_n(ll)
        steps = [a.step for a in r.alarms]
        rec = {"sum": s, "n": n, "logloss": s / n, "n_alarms": len(steps)}
        if st.startswith("naive_") or st == "off":
            rec["n_alarms_D1"] = int(sum(d1_at.get(t, False) for t in steps))
        for ref in ("static_snorm", "regime_gated"):
            rec[f"sum_d_{ref}"] = float(np.nansum(ll - ref_ll[ref]))
        out["stops"][st] = rec
    out["wall_s"] = round(time.time() - t0, 1)
    return out


def _null_train(ctx, train) -> dict:
    """Leave-one-train-day-out windows of the naive test (same construction as calibrate_ks_null):
    each training day is compared with a reference built from the other 11 training days."""
    k = CFG_V2["ks"]
    pb, dm = [], []
    for i, (fi, _) in enumerate(train):
        ref = np.vstack([fj.X for j, (fj, _) in enumerate(train) if j != i])[::k["subsample"]][:, ctx.ks_idx]
        ref = [np.sort(ref[:, j]) for j in range(ref.shape[1])]
        for t in range(k["window"], fi.X.shape[0], k["stride"]):
            cur = fi.X[t - k["window"] + 1:t + 1:k["subsample"]][:, ctx.ks_idx]
            D = np.array([ks_stat_sorted(cur[:, j], ref[j]) for j in range(len(ref))])
            p = min(ks_pvalue_asymp(D[j], cur.shape[0], ref[j].shape[0]) for j in range(len(ref))) * len(ref)
            pb.append(p)
            dm.append(D.max())
    pb, dm = np.array(pb), np.array(dm)
    return {"n_windows": int(pb.size), "share_D1": float((dm >= 1.0).mean()), "share_p0": float((pb == 0.0).mean()),
            "reject_share": {str(e): float((pb < 10.0 ** e).mean()) for e in NAIVE_LOG10},
            "median_log10_pbon": float(np.median(np.log10(np.maximum(pb, 1e-320))))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--days", nargs="*", default=None, help="subset of holdout days (debug only)")
    a = ap.parse_args()
    nice_self()
    t_start = time.time()
    while mem_level() < 30:
        print("memory level < 30, waiting", flush=True)
        time.sleep(30)
    ctx, train = train_context()
    cal = {q: calibrated_thresholds(ctx, train, q) for q in CAL_Q}
    null = _null_train(ctx, train)
    del train
    print(f"context + null ready in {time.time() - t_start:.0f} s", flush=True)
    days = a.days or SPLIT_V2["holdout"]
    res, pending, todo = {}, set(), list(days)
    with ProcessPoolExecutor(max_workers=min(a.workers, 3), initializer=_init, initargs=(ctx, cal)) as ex:
        while todo or pending:
            while todo and len(pending) < min(a.workers, 3):
                while mem_level() < 25:
                    print("memory level < 25, pausing", flush=True)
                    time.sleep(30)
                pending.add(ex.submit(_day, todo.pop(0)))
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for fu in done:
                r = fu.result()
                res[r["day"]] = r
                print(f"{r['day']} done in {r['wall_s']} s  (off={r['stops']['off']['logloss']:.6f}, "
                      f"a=1e-3 alarms={r['stops']['naive_3']['n_alarms']})", flush=True)
    days = [d for d in days if d in res]
    day_ids = np.arange(len(days))
    n_ref = ctx.ks_ref.shape[0]
    m = CFG_V2["ks"]["window"] // CFG_V2["ks"]["subsample"]
    sep = log10_separation_prob(m, n_ref)

    def dc(key_sum: str, st: str) -> dict:
        # Equal per-day sums and counts as the pointwise arrays, so day_cluster_bootstrap_ci gives the same result.
        d = np.concatenate([np.full(res[x]["stops"][st]["n"], res[x]["stops"][st][key_sum] / res[x]["stops"][st]["n"])
                            for x in days])
        ids = np.concatenate([np.full(res[x]["stops"][st]["n"], i) for i, x in zip(day_ids, days)])
        return day_cluster_bootstrap_ci(d, ids)

    stops = []
    for st in stop_ids():
        rows = {x: res[x]["stops"][st] for x in days}
        S, N = sum(r["sum"] for r in rows.values()), sum(r["n"] for r in rows.values())
        info = {"id": st, "pooled_logloss": S / N,
                "alarms_per_day": sum(r["n_alarms"] for r in rows.values()) / len(days),
                "vs_static_snorm": dc("sum_d_static_snorm", st), "vs_regime_gated": dc("sum_d_regime_gated", st),
                "per_day": {x: {k: rows[x][k] for k in ("logloss", "n_alarms", "n_alarms_D1") if k in rows[x]}
                            for x in days}}
        if st.startswith("naive_"):
            e = -int(st[6:])
            info.update(kind="naive", log10_alpha=e, below_separation=bool(e < sep),
                        label=f"α = 1e{e}")
            na = sum(r["n_alarms"] for r in rows.values())
            info["share_alarms_D1"] = (sum(r["n_alarms_D1"] for r in rows.values()) / na) if na else None
            info["null_train_reject_share"] = null["reject_share"][str(e)]
        elif st.startswith("cal_"):
            info.update(kind="calibrated", quantile=float(st[4:]), label=f"calibrated q = {st[4:]}")
        else:
            info.update(kind="off", label="off (α = 0)")
        stops.append(info)
    refs = {}
    for r in REFS:
        S = sum(res[x]["refs"][r]["sum"] for x in days)
        N = sum(res[x]["refs"][r]["n"] for x in days)
        refs[r] = {"pooled_logloss": S / N, "per_day": {x: res[x]["refs"][r]["logloss"] for x in days}}
    win = {"n": sum(res[x]["windows"]["n"] for x in days), "n_D1": sum(res[x]["windows"]["n_D1"] for x in days),
           "n_p0": sum(res[x]["windows"]["n_p0"] for x in days)}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    out = {"status": "post-hoc demo sweep, not pre-registered",
           "meta": {"created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "commit": commit,
                    "command": "python demo/build_sweep.py " + " ".join(sys.argv[1:]), "days": days,
                    "runtime_s": round(time.time() - t_start, 1),
                    "ks": CFG_V2["ks"], "ks_features": CFG_V2["ks_features"],
                    "note": "naive = textbook asymptotic two-sample KS (SciPy kstwo), Bonferroni over 7 features, "
                            "persist 3, cooldown 1800 s (max 48 alarms/day); calibrated = empirical leave-one-train-day-out "
                            "null at quantile q (q = 0.999 is the committed ksc_refit); off = alpha 0 (never fires)."},
           "separation": {"m": m, "n_ref": n_ref, "log10_prob": sep,
                          "text": "exact probability under exchangeability that a window of m points lies entirely "
                                  "outside a reference of n points (D = 1): 2 / C(m+n, m)"},
           "null_train": null, "holdout_windows": win, "refs": refs, "stops": stops}
    p = RESULTS / "alarm_dial_sweep.json" if not a.days else CACHE / "alarm_dial_sweep_subset.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1))
    print(f"wrote {p} in {time.time() - t_start:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
