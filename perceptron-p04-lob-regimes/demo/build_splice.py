"""Act 2, SEMI-SYNTHETIC stress test: splice two real held-out order books at a known time and replay.

    cd perceptron-p04-lob-regimes && nice -n 10 python demo/build_splice.py

Method: from the UTC day of book A (the calmest held-out day) keep every snapshot received before the splice
time tau; from book B (the most volatile held-out day) keep every snapshot received at or after the same
second-of-day, with B's prices shifted ADDITIVELY by an integer number of ticks (re-rounded to the 0.1 tick grid, i.e. the
same doubles a decimal parse gives) so that the mid is continuous at tau. Both directions (calm -> volatile, volatile -> calm) at five splice times. The spliced book goes
through the committed build_features / make_labels / run_episode unchanged.

Integrity checks stored with each splice (and asserted by smoke.sh):
  * causality: every feature row and label strictly before tau equals the unspliced day A exactly;
  * shift invariance: every label after tau (+60 s) equals day B's own label (an additive price shift
    cannot change the direction of a mid move).
Writes demo/.cache/splice_<dir>_<HH>.json (10-minute aggregates + alarm times only; gitignored).
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

from build_replay import POLS, _sec, frame_summary
from common import CACHE, CACHE_SCHEMA, DEMO, cache_key, cache_valid, H_STEPS_, STEP_S_, mem_level, nice_self, train_context
from components.contracts import BookDay
from components.features import TICK_SIZE, build_features
from components.ingest import load_book_day
from components.labeler import make_labels

TAUS_H = [6, 9, 12, 15, 18]
DAY_US = 86400 * 10**6
WIN_S = 7200


def splice(A: BookDay, B: BookDay, tau_s: int) -> tuple[BookDay, int, int]:
    a0 = (A.recv_us[0] // DAY_US) * DAY_US
    shift = a0 - (B.recv_us[0] // DAY_US) * DAY_US
    tau = a0 + tau_s * 10**6
    ia = int(np.searchsorted(A.recv_us, tau, "left"))
    brecv = B.recv_us + shift
    ib = int(np.searchsorted(brecv, tau, "left"))
    tick = TICK_SIZE[A.symbol]
    mid_a = 0.5 * (A.bid_px[ia - 1, 0] + A.ask_px[ia - 1, 0])
    mid_b = 0.5 * (B.bid_px[ib - 1, 0] + B.ask_px[ib - 1, 0])
    k = int(round((mid_a - mid_b) / tick))
    c = k * tick
    S = BookDay(A.symbol, A.day,
                np.concatenate([A.recv_us[:ia], brecv[ib:]]),
                np.concatenate([A.exch_us[:ia], B.exch_us[ib:] + shift]),
                np.vstack([A.bid_px[:ia], np.round(B.bid_px[ib:] + c, 1)]), np.vstack([A.bid_sz[:ia], B.bid_sz[ib:]]),
                np.vstack([A.ask_px[:ia], np.round(B.ask_px[ib:] + c, 1)]), np.vstack([A.ask_sz[:ia], B.ask_sz[ib:]]))
    return S, k, tau


def _eq_nan(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.array_equal(a, b, equal_nan=True))


def main() -> int:
    nice_self()
    t0 = time.time()
    while mem_level() < 30:
        print("memory level < 30, waiting", flush=True)
        time.sleep(30)
    sb = json.loads((DEMO / "results" / "scoreboard.json").read_text())
    held = [r["day"] for r in sb["replay_days"] if r["role"].startswith("held-out")]
    calm, vol = held[0], held[-1]
    key = cache_key([calm, vol])
    if "--force" not in sys.argv and cache_valid(CACHE / "splice_index.json", key) and all(
            cache_valid(CACHE / f"splice_{dr}_{th:02d}.json", key) for dr in ("calm_to_volatile", "volatile_to_calm") for th in TAUS_H):
        print("splice cache valid; nothing to do")
        return 0
    ctx, train = train_context()
    del train
    books = {d: load_book_day(d) for d in (calm, vol)}
    frames = {}
    for d in (calm, vol):
        f = build_features(books[d], step_s=STEP_S_)
        frames[d] = (f, make_labels(f, H_STEPS_))
    index = []
    for direction, (a, b) in (("calm_to_volatile", (calm, vol)), ("volatile_to_calm", (vol, calm))):
        fa, la = frames[a]
        fb, lb = frames[b]
        for th in TAUS_H:
            tau_s = th * 3600
            S, k, tau = splice(books[a], books[b], tau_s)
            f = build_features(S, step_s=STEP_S_)
            l = make_labels(f, H_STEPS_)
            assert np.array_equal(f.grid_us, fa.grid_us), "grid must match day A"
            pre = f.grid_us < tau
            pre_lab = f.grid_us + H_STEPS_ * f.step_us < tau
            sod = (f.grid_us - (f.grid_us[0] // DAY_US) * DAY_US)
            sod_b = (fb.grid_us - (fb.grid_us[0] // DAY_US) * DAY_US)
            post = f.grid_us >= tau + 60 * 10**6
            jb = np.searchsorted(sod_b, sod[post])
            ok_b = (jb < sod_b.size) & (sod_b[np.minimum(jb, sod_b.size - 1)] == sod[post])
            checks = {"causal_features_pre": bool(np.array_equal(f.X[pre], fa.X[pre])),
                      "causal_labels_pre": _eq_nan(l.y[pre_lab], la.y[pre_lab]),
                      "n_post_labels_compared": int(ok_b.sum()), "n_post_unmatched": int((~ok_b).sum())}
            # A real mid move is >= half a tick (~0.007 bps); |move| < 1e-6 bps is floating-point noise on an exact
            # decimal tie (0.5 * (bid + ask) rounding), whose sign the committed labeler reads as up or down.
            ys, yb, mb = l.y[post][ok_b], lb.y[jb[ok_b]], lb.move_bps[jb[ok_b]]
            real = np.abs(mb) > 1e-6
            checks["labels_shift_invariant_post"] = _eq_nan(ys[real | np.isnan(mb)], yb[real | np.isnan(mb)])
            checks["n_float_noise_ties"] = int((~real & ~np.isnan(mb) & (mb != 0)).sum())
            checks["n_float_noise_ties_flipped"] = int((~real & ~np.isnan(mb) & ~((ys == yb) | (np.isnan(ys) & np.isnan(yb)))).sum())
            out = frame_summary(f, l, ctx, None, f"{a} ⟶ {b} @ {th:02d}:00")
            ll, reg = out.pop("_ll"), out.pop("_reg")
            out.pop("_bins")
            before = (f.grid_us >= tau - WIN_S * 10**6) & (f.grid_us < tau)
            after = (f.grid_us >= tau) & (f.grid_us < tau + WIN_S * 10**6)
            win = {p: {"before_2h": float(np.nanmean(ll[p][before])), "after_2h": float(np.nanmean(ll[p][after]))}
                   for p in POLS}
            det = {}
            for p, name in (("ks_refit", "rolling_ks"), ("spike_gate", "rolling_ks_calibrated"), ("spike_gate", "harm_cusum")):
                ts = np.array(out["policies"][p]["alarms"].get(name, []))
                post_t = ts[ts >= tau_s]
                det[name] = {"before": int((ts < tau_s).sum()), "after": int(post_t.size),
                             "first_delay_min": round(float(post_t.min() - tau_s) / 60, 1) if post_t.size else None}
            h1b = (f.grid_us >= tau - 3600 * 10**6) & (f.grid_us < tau)
            h1a = (f.grid_us >= tau) & (f.grid_us < tau + 3600 * 10**6)
            heads = {"before_1h": [float((reg[h1b] == r).mean()) for r in range(3)],
                     "after_1h": [float((reg[h1a] == r).mean()) for r in range(3)]}
            out.update(schema=CACHE_SCHEMA, cache_key=key, status="SEMI-SYNTHETIC", direction=direction, day_a=a, day_b=b, splice_utc_s=tau_s,
                       shift_ticks=k, shift_usd=round(k * TICK_SIZE[S.symbol], 2), checks=checks, window_2h=win,
                       detectors=det, gate_heads=heads, events=[])
            name = f"splice_{direction}_{th:02d}.json"
            (CACHE / name).write_text(json.dumps(out))
            index.append({"file": name, "direction": direction, "hour": th, "checks": checks})
            print(f"{name}: shift {k} ticks, checks {checks}", flush=True)
            del S, f, l
    (CACHE / "splice_index.json").write_text(json.dumps({"schema": CACHE_SCHEMA, "cache_key": key,
                                                          "status": "SEMI-SYNTHETIC", "calm": calm, "volatile": vol,
                                                          "taus_h": TAUS_H, "splices": index}))
    print(f"splices done in {time.time() - t0:.0f} s")
    bad = [s["file"] for s in index if not all(v for k_, v in s["checks"].items() if not k_.startswith("n_")) or s["checks"]["n_post_unmatched"] > 1]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
