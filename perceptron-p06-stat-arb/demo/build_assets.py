"""Deterministic asset builder for the P6 offline demo (PLAYBOOK §11). Heavy: run once, through the guard.

    eval/run_guarded.sh .venv/bin/python -m demo.build_assets

It reads the raw Tardis quotes of 2026-09-01 (train) and 2026-10-01 (held-out test) for the 5 walk-forward legs
(read-only, `.data/tardis`). If the walk-forward caches are present (`.cache/falsification`, `.cache/sensitivity`),
it asserts that its own recomputation equals them row for row. It then re-runs the committed pipeline on a grid:
    detect -> add_features -> candidates (net edge > 0 at fee f) -> intents -> simulate (frozen) / simulate_strict (V1)
- one-way latency δ in DELTAS, with decision delay D = 7 µs (the walk-forward's COMPUTE_US: "machine");
- at 1 bp/leg only, also D in RTS (a human reaction time).

Policies, exactly as in the registered tests:
- naive;
- per-pair threshold (rules.fit_threshold), re-tuned per (pair, fee, δ, D) on 09-01 labels;
- LEV (rules.fit_gbm_reg on the six registered 09-01 cells).
Each comes in two worlds: V0 frozen labels, and V1 strict labels (Amendment 1: policies refit on strict labels,
invalid rows dropped).

The script asserts that at δ = 1/5/20 ms the full-day totals reproduce
eval/results/falsification_walkforward_12d_prereg.json (V0) and sensitivity_amendment1.json (V1). It then exports
the densest 15-minute window, chosen by a stated rule.

Outputs go to demo/assets/:
- window_books.npz: exact quotes slice for the backend's simulator;
- data.js: front-end bundle, which the backend also reads;
- lev_*.pkl and lev_*.npz: sklearn models and their compiled.flatten arrays;
- provenance.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import pickle
import platform
import subprocess
import sys
import time

import numpy as np
import polars as pl
from lifelines import KaplanMeierFitter

from components.decay.survival import add_features
from components.decision import policies as P
from components.decision.autoresearch import rules as R
from components.decision.autoresearch.build_cells import COMPUTE_US, DELTAS_MS as REG_DELTAS, FEES, LEGS_FILES
from components.decision.compiled import RAW_FIELDS, flatten
from components.decision.lev import add_lev_columns
from components.detector.cross import detect
from components.sim.fills import simulate, truth_books
from components.sim.strict import simulate_strict
from eval.falsification import day_q
from eval.run_baseline import pair_group

OUT = "demo/assets"
TRAIN, TEST = "2026-09-01", "2026-10-01"
DELTAS = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 50.0, 70.0, 100.0]
RTS = [100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 500.0, 650.0, 800.0, 1000.0, 1500.0, 2000.0]
MACHINE_D_US = COMPUTE_US                      # 7 µs, the walk-forward's compute allowance
RACE_FEE = 1.0
WINDOW_S, LEAD_S, TAIL_S = 15 * 60, 120, 20
Q_MAX, STALE_CAP_US, MARKOUTS = 0.05, 1e6, (1.0, 10.0)
LEV_DELTA_RANGE = (min(REG_DELTAS), max(REG_DELTAS))
OC = {"none": 0, "sell_only": 1, "buy_only": 2, "both": 3}
SIMS = ("frozen", "strict")
CACHE_F, CACHE_S = ".cache/falsification", ".cache/sensitivity"
CHECKS: list[dict] = []


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def check(name: str, ok: bool, detail="") -> None:
    CHECKS.append({"check": name, "ok": bool(ok), "detail": detail})
    log(("PASS " if ok else "FAIL ") + name, detail)
    if not ok:
        raise SystemExit(f"check failed: {name} {detail}")


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cfg_key(sim: str, fee: float, d_ms: float, D_us: float) -> str:
    return f"{sim}|f{fee:g}|d{d_ms:g}|D{D_us:g}"


def configs() -> list[tuple[float, float, float]]:
    """(fee, δ ms, D µs): machine at both fees, human reaction times at the race fee."""
    out = [(f, d, MACHINE_D_US) for f in FEES for d in DELTAS]
    out += [(RACE_FEE, d, rt * 1000.0) for d in DELTAS for rt in RTS]
    return out


def candidates(opp: pl.DataFrame) -> dict[float, pl.DataFrame]:
    return {f: P.with_net(opp, f"f{f:g}").filter(pl.col("net0_bps") > 0) for f in FEES}


def label(o_fee: pl.DataFrame, books, legs: list[str], fee: float, d_ms: float, D_us: float, sim: str, part: str) -> pl.DataFrame:
    """Same construction as eval.falsification.cells / eval.strict_cells.build, with the decision delay D as a parameter."""
    d = d_ms * 1000.0
    c = o_fee.with_columns((pl.col("t_start_us") + int(d)).alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))
    it = P.intents(c, np.ones(c.height, bool), c["t_obs_us"].to_numpy() + D_us, c["net0_bps"].to_numpy(), "all")
    lat, fees = {l: d for l in legs}, {l: fee for l in legs}
    if sim == "frozen":
        r = simulate(it, books, lat, fees, Q_MAX)
        out = it.join(r.select("opp_id", "outcome", "pnl_usd", "pnl_bps"), on="opp_id")
    else:
        r = simulate_strict(it, books, lat, fees, Q_MAX, STALE_CAP_US, MARKOUTS)
        out = it.join(r, on="opp_id", how="inner")
    out = out.with_columns(pl.lit(fee).alias("fee_bps"), pl.lit(d_ms).alias("delta_ms"), pl.lit(float(2 * d_ms + D_us / 1000)).alias("L_ms"),
                           pl.lit(part).alias("part"), (pl.col("t_start_us") // 3_600_000_000).alias("hour"))
    return out.with_columns(pl.lit(D_us / 1000.0).alias("D_ms"))


def frames_equal(a: pl.DataFrame, b: pl.DataFrame) -> bool:
    if a.columns != b.columns or a.height != b.height:
        return False
    return a.equals(b, null_equal=True)


def day(date: str):
    t0 = time.time()
    q, legs = day_q(date)
    opp = add_lev_columns(pair_group(add_features(detect(q, legs, "ts_exch_us", theta_bps=1.0))), legs)
    books = truth_books(q)
    log(f"{date}: {q.height:,} quotes, {opp.height:,} episodes ({time.time() - t0:.0f}s)")
    return q, legs, opp, books


def is_reg(d_ms: float, D_us: float) -> bool:
    return D_us == MACHINE_D_US and d_ms in REG_DELTAS


def labels_stream(date: str, opp: pl.DataFrame, books, legs: list[str], sim: str):
    """Yield (fee, δ, D, rows) config by config (memory-light). Strict rows are V1's: invalid rows dropped (Amendment 1 erratum)."""
    cands = candidates(opp)
    for fee, d_ms, D_us in configs():
        x = label(cands[fee], books, legs, fee, d_ms, D_us, sim, date)
        yield fee, d_ms, D_us, (x.filter(pl.col("valid")) if sim == "strict" else x)


def registered(reg: dict) -> pl.DataFrame:
    """The six registered cells in the walk-forward's order (fees outer, latencies inner), without our D column."""
    return pl.concat([reg[(f, d)].drop("D_ms") for f in FEES for d in REG_DELTAS], how="diagonal_relaxed")


def assert_cache(name: str, mine: pl.DataFrame, path: str, strict: bool) -> None:
    if not os.path.exists(path):
        CHECKS.append({"check": name, "ok": None, "detail": f"{path} absent — skipped"})
        log("SKIP", name)
        return
    ref = pl.read_parquet(path)
    if strict:
        ref = ref.filter(pl.col("valid"))
    ok = frames_equal(mine.select(ref.columns), ref) and set(mine.columns) == set(ref.columns)
    check(name, ok, f"{mine.height} rows vs {path} ({md5(path)})")


def train_policies(opp: pl.DataFrame, books, legs: list[str]) -> dict:
    """09-01: thresholds per (pair, fee, δ, D) over the whole grid; LEV on the six registered cells, exactly as registered."""
    out = {}
    for sim in SIMS:
        t0 = time.time()
        th, reg = {}, {}
        for fee, d_ms, D_us, x in labels_stream(TRAIN, opp, books, legs, sim):
            th.update(R.fit_threshold(x, ["pair_id", "fee_bps", "delta_ms", "D_ms"])["th"])
            if is_reg(d_ms, D_us):
                reg[(fee, d_ms)] = x
        regf = registered(reg)
        if sim == "frozen":
            assert_cache(f"{TRAIN} frozen registered cells == .cache/falsification", regf, f"{CACHE_F}/cells_{TRAIN}_exch.parquet", False)
        else:
            assert_cache(f"{TRAIN} strict registered cells == .cache/sensitivity (valid rows)", regf, f"{CACHE_S}/cells_{TRAIN}.parquet", True)
        ref_thr = R.fit_threshold(regf, ["pair_id", "fee_bps", "delta_ms"])
        same = all(th.get((k[0], k[1], k[2], MACHINE_D_US / 1000.0), "missing") == v for k, v in ref_thr["th"].items())
        check(f"{sim}: grid thresholds at registered cells == walk-forward fit_threshold", same, f"{len(ref_thr['th'])} keys")
        out[sim] = {"thr": {"by": ["pair_id", "fee_bps", "delta_ms", "D_ms"], "th": th}, "lev": R.fit_gbm_reg(regf), "train_rows": regf.height}
        log(f"{TRAIN} {sim}: {len(th)} thresholds; LEV fitted on {regf.height} rows ({time.time() - t0:.0f}s)")
    return out


def score(rows: pl.DataFrame, pol: dict, with_lev: bool) -> dict[str, np.ndarray]:
    acts = {"naive": np.ones(rows.height, bool), "thr": np.asarray(R.act_threshold(pol["thr"], rows), bool)}
    if with_lev:
        acts["lev"] = np.asarray(R.act_gbm_reg(pol["lev"], rows), bool)
    return acts


def agg(rows: pl.DataFrame, mask: np.ndarray) -> dict:
    ch = rows.filter(pl.Series(mask))
    return {"usd": float(ch["pnl_usd"].sum()) if ch.height else 0.0, "n": int(ch.height),
            "n_both": int((ch["outcome"] == "both").sum()) if ch.height else 0}


def window_rule(opp: pl.DataFrame) -> tuple[int, int]:
    """Densest 15 minutes by detected-episode count, windows starting on whole UTC minutes; ties -> earliest."""
    ts = np.sort(opp["t_start_us"].to_numpy())
    W = WINDOW_S * 1_000_000
    first = (ts[0] // 60_000_000) * 60_000_000
    starts = np.arange(first, ts[-1] - W + 1, 60_000_000, dtype=np.int64)
    cnt = np.searchsorted(ts, starts + W, side="left") - np.searchsorted(ts, starts, side="left")
    i = int(np.argmax(cnt))
    return int(starts[i]), int(cnt[i])


def km_curve(dur_us: np.ndarray, cens: np.ndarray) -> dict:
    km = KaplanMeierFitter().fit((dur_us + 1) / 1000.0, (~cens).astype(int))
    sf = km.survival_function_
    med = float(km.median_survival_time_)
    return {"t_ms": [float(x) for x in sf.index.to_numpy()], "S": [float(x) for x in sf.iloc[:, 0].to_numpy()],
            "median_ms": med if np.isfinite(med) else None, "n": int(dur_us.size), "n_censored": int(cens.sum())}


def cents_delta(px: np.ndarray) -> list[int]:
    c = np.round(px * 100).astype(np.int64)
    if not np.allclose(c / 100.0, px, rtol=0, atol=1e-9):
        raise ValueError("price not on a 0.01 grid")
    return np.diff(c, prepend=0).tolist()


def committed_numbers() -> dict:
    j = lambda f: json.load(open(f"eval/results/{f}"))  # noqa: E731
    head, wf, sens, dt = j("headline.json"), j("falsification_walkforward_12d_prereg.json"), j("sensitivity_amendment1.json"), j("decision_timing.json")
    cad, lb, live = j("update_cadence.json"), j("latency_budget.json"), j("live_cadence.json")
    w = lambda name: sens["worlds"][name]["registered"]  # noqa: E731
    return {
        "headline": head,
        "walkforward_v0": {k: wf["comparisons"][k] for k in ("lev - threshold_pair", "threshold_pair - naive")},
        "walkforward_table": wf["table"],
        "v1": {k: w("V1_strict")[k] for k in ("lev - threshold_pair", "threshold_pair - naive")},
        "v2": {k: w("V2_strict_mo1")[k] for k in ("lev - threshold_pair", "threshold_pair - naive")},
        "v4": w("V4_transfer")["lev - threshold_pair"],
        "s3_v2": sens["collision_dropped"]["V2_strict_mo1"]["registered"]["lev - threshold_pair"],
        "decision_timing": {"in_kernel_ns": dt["decision_in_kernel_ns"], "from_python_ns": dt["decision_from_python_ns"],
                            "detector": dt["detector"], "commit": dt["commit"], "machine": dt["machine"]},
        "cadence": {r["leg"]: {"median_gap_ms": r["median_gap_ms"], "share_100ms_grid": r["share_100ms_grid"]} for r in cad["legs"]},
        "live_cadence": live["legs"],
        "feed_tardis_ms": lb["feed_tardis_collector_ms"], "feed_mac_india_p05_ms": lb["feed_mac_india_p05_ms"],
        "breakeven_oneway_ms": lb["breakeven_oneway_ms"],
        "sources": {"headline": "eval/results/headline.json", "walkforward": "eval/results/falsification_walkforward_12d_prereg.json",
                    "strict": "eval/results/sensitivity_amendment1.json", "timing": "eval/results/decision_timing.json",
                    "cadence": "eval/results/update_cadence.json", "live_cadence": "eval/results/live_cadence.json",
                    "latency": "eval/results/latency_budget.json", "decay": "eval/results/decay_report.md"},
    }


def main() -> None:
    t_all = time.time()
    os.makedirs(OUT, exist_ok=True)

    # ---------------------------------------------------------------- training day: labels, cache checks, fits
    q, legs, opp, books = day(TRAIN)
    pols = train_policies(opp, books, legs)
    train_counts = {sim: pols[sim]["train_rows"] for sim in SIMS}
    del q, opp, books

    # ---------------------------------------------------------------- held-out day: window first, then config by config
    q, legs, opp, books = day(TEST)
    keep = ["opp_id", "pair", "duration_us", "censored", "edge0_bps", "t_start_us"]
    po = f"{CACHE_F}/opp_{TEST}_exch.parquet"
    if os.path.exists(po):
        check(f"{TEST} episodes == .cache/falsification opp", frames_equal(opp.select(keep), pl.read_parquet(po)), f"{opp.height:,} episodes")
    w0, n_ep = window_rule(opp)
    w1 = w0 + WINDOW_S * 1_000_000
    s0, s1 = w0 - LEAD_S * 1_000_000, w1 + TAIL_S * 1_000_000
    sl = q.filter((pl.col("ts_exch_us") >= s0) & (pl.col("ts_exch_us") <= s1))
    wbooks = truth_books(sl)
    win = lambda df: df.filter((pl.col("t_start_us") >= w0) & (pl.col("t_start_us") < w1))  # noqa: E731
    ep = win(opp).sort(["t_start_us", "opp_id"])
    log(f"window {w0}..{w1}: {ep.height} episodes; slice {sl.height:,} quotes")
    check("window episode count == rule count", ep.height == n_ep, f"{ep.height}")
    day_cands = candidates(opp)
    cands = {f: win(c).sort(["t_start_us", "opp_id"]) for f, c in day_cands.items()}

    day_grid, grid_window, max_dev = {}, {}, 0.0
    for sim in SIMS:
        t0 = time.time()
        reg = {}
        for fee, d_ms, D_us, rows in labels_stream(TEST, opp, books, legs, sim):
            key = cfg_key(sim, fee, d_ms, D_us)
            if is_reg(d_ms, D_us):
                reg[(fee, d_ms)] = rows
            acts = score(rows, pols[sim], with_lev=(D_us == MACHINE_D_US))
            day_grid[key] = {p: agg(rows, m) for p, m in acts.items()}
            # window: the backend recomputes exactly this on the slice books, so assert slice == full day here
            wmask = ((rows["t_start_us"] >= w0) & (rows["t_start_us"] < w1)).to_numpy()
            wr = rows.filter(pl.Series(wmask))
            sub = label(cands[fee], wbooks, legs, fee, d_ms, D_us, sim, TEST)
            if sim == "strict" and not bool(sub["valid"].all()):
                raise SystemExit(f"invalid strict rows inside the window for {key}")
            if not frames_equal(wr.select("opp_id", "outcome", "pnl_usd").sort("opp_id"), sub.select("opp_id", "outcome", "pnl_usd").sort("opp_id")):
                raise SystemExit(f"slice recompute differs from full day for {key}")
            ids = cands[fee]["opp_id"].to_numpy()
            pos = {int(o): i for i, o in enumerate(ids)}
            n = len(ids)
            oc = np.full(n, -1, np.int8); pnl = np.zeros(n); thr = np.zeros(n, np.int8); lev = np.zeros(n, np.int8)
            idx = np.array([pos[int(o)] for o in wr["opp_id"].to_numpy()], dtype=np.int64)
            if idx.size:
                oc[idx] = [OC[o] for o in wr["outcome"].to_list()]
                pnl[idx] = wr["pnl_usd"].to_numpy()
                thr[idx] = acts["thr"][wmask]
            rec = {"oc": oc.tolist(), "pnl": [round(float(x), 6) for x in pnl], "thr": thr.tolist()}
            if "lev" in acts:
                if idx.size:
                    lev[idx] = acts["lev"][wmask]
                rec["lev"] = lev.tolist()
            rec["tot"] = {p: agg(wr, m[wmask]) for p, m in acts.items()}
            max_dev = max(max_dev, abs(sum(rec["pnl"]) - float(wr["pnl_usd"].sum())))
            grid_window[key] = rec
        regf = registered(reg)
        if sim == "frozen":
            assert_cache(f"{TEST} frozen registered cells == .cache/falsification", regf, f"{CACHE_F}/cells_{TEST}_exch.parquet", False)
        else:
            assert_cache(f"{TEST} strict registered cells == .cache/sensitivity (valid rows)", regf, f"{CACHE_S}/cells_{TEST}.parquet", True)
        del reg, regf
        log(f"{TEST} {sim}: scored {sum(1 for k in day_grid if k.startswith(sim))} configs ({time.time() - t0:.0f}s)")
    check("every window config: slice recompute == full-day labels (outcome, pnl)", True,
          f"{len(grid_window)} configs; max per-config rounding deviation of exported pnl {max_dev:.2e} USD")

    wf = json.load(open("eval/results/falsification_walkforward_12d_prereg.json"))
    v0_ref = next(r for r in wf["table"] if r["test"] == TEST)
    sens = json.load(open("eval/results/sensitivity_amendment1.json"))
    v1_ref = {p: sens["per_day_raw"]["V1_strict"][TEST][p]["total"] for p in ("naive", "threshold_pair", "lev")}
    for sim, ref in (("frozen", {"naive": v0_ref["naive"], "thr": v0_ref["threshold_pair"], "lev": v0_ref["lev"]}),
                     ("strict", {"naive": v1_ref["naive"], "thr": v1_ref["threshold_pair"], "lev": v1_ref["lev"]})):
        mine = {p: sum(day_grid[cfg_key(sim, f, d, MACHINE_D_US)][p]["usd"] for f in FEES for d in REG_DELTAS) for p in ref}
        ok = all(abs(mine[p] - ref[p]) < 1e-6 * max(1.0, abs(ref[p])) for p in ref)
        check(f"{sim}: day totals at δ=1/5/20 (6 cells) == committed {TEST} ({'V0 walk-forward' if sim == 'frozen' else 'V1 Amendment 1'})", ok,
              {p: [round(mine[p], 6), round(ref[p], 6)] for p in ref})
    cells_ref = {r["policy"]: r["cells"] for r in wf["per_day"] if r["test"] == TEST}
    ok = all(abs(day_grid[cfg_key("frozen", f, d, MACHINE_D_US)][p]["usd"] - cells_ref[rp][f"f{f:g}_d{d:g}"]) <= 0.005 + 1e-9
             for p, rp in (("naive", "naive"), ("thr", "threshold_pair"), ("lev", "lev")) for f in FEES for d in REG_DELTAS)
    check("frozen: per-cell day totals == walk-forward per-cell table (to the cent)", ok)
    cand_cols = ["opp_id", "t_start_us", "duration_us", "censored", "s", "b", "sell_venue", "buy_venue", "pair", "pair_id", "limit_sell_px",
                 "limit_buy_px", "size", "basis0_bps", "edge0_bps", "net0_bps", "edge_max_bps", "instr_group"] + \
        [c for c in RAW_FIELDS + R.LEARN_X if c not in ("L_ms", "fee_bps")]
    cand_cols = list(dict.fromkeys(cand_cols))

    # ---------------------------------------------------------------- exports
    np.savez_compressed(f"{OUT}/window_books.npz", legs=np.array(legs), w0=np.int64(w0), w1=np.int64(w1),
                        **{f"{k}__{i}": v for i, l in enumerate(legs) for k, v in
                           (("ts", wbooks[l].ts), ("bid", wbooks[l].bid), ("ask", wbooks[l].ask), ("bsz", wbooks[l].bsz), ("asz", wbooks[l].asz))})
    models = {}
    for sim in SIMS:
        m = pols[sim]["lev"]["m"]
        with open(f"{OUT}/lev_{sim}.pkl", "wb") as fh:
            pickle.dump(m, fh, protocol=5)
        a = flatten(m)
        np.savez_compressed(f"{OUT}/lev_{sim}.npz", **{k: np.asarray(v) for k, v in a.items()})
        models[sim] = {"n_trees": a["n_trees"], "n_nodes": a["n_nodes"], "train_rows": train_counts[sim], "features": R.LEARN_X,
                       "trained_on": f"{TRAIN} registered cells (fee {FEES} × δ {REG_DELTAS} ms), {'frozen' if sim == 'frozen' else 'strict V1'} labels"}
    thresholds = {sim: [[k[0], k[1], k[2], k[3], (None if not np.isfinite(v) else float(v))] for k, v in sorted(pols[sim]["thr"]["th"].items())]
                  for sim in SIMS}

    disp = {}
    for i, l in enumerate(legs):
        g = sl.filter(pl.col("leg") == l).sort("ts_exch_us", maintain_order=True)
        bid, ask, ts = g["bid_px"].to_numpy(), g["ask_px"].to_numpy(), g["ts_exch_us"].to_numpy()
        ch = np.ones(ts.size, bool)
        ch[1:] = (bid[1:] != bid[:-1]) | (ask[1:] != ask[:-1])
        tsr = ts[ch] - w0
        disp[l] = {"t_us_delta": np.diff(tsr, prepend=0).tolist(), "bid_c_delta": cents_delta(bid[ch]), "ask_c_delta": cents_delta(ask[ch]),
                   "n_raw": int(ts.size)}
    leg_idx = {l: i for i, l in enumerate(legs)}
    episodes = {"t_us": (ep["t_start_us"] - w0).to_list(), "dur_us": ep["duration_us"].to_list(), "s": ep["s"].to_list(),
                "b": ep["b"].to_list(), "edge0": [round(x, 4) for x in ep["edge0_bps"].to_list()], "cens": ep["censored"].to_list(),
                "opp_id": ep["opp_id"].to_list()}
    cand_out = {}
    for f, c in cands.items():
        cand_out[f"{f:g}"] = {col: c[col].to_list() for col in cand_cols}
    km = {"episodes": km_curve(ep["duration_us"].to_numpy(), ep["censored"].to_numpy()),
          "cands_f1": km_curve(cands[RACE_FEE]["duration_us"].to_numpy(), cands[RACE_FEE]["censored"].to_numpy())}
    data = {
        "meta": {"test_day": TEST, "train_day": TRAIN, "legs": legs, "leg_files": LEGS_FILES, "w0_us": w0, "w1_us": w1,
                 "slice_us": [s0, s1], "window_rule": "densest 15 minutes of 2026-10-01 by detected-episode count (episodes ≥ 1 bp beyond the "
                 "60 s EWMA fair basis, 5 legs), windows starting on whole UTC minutes, ties → earliest",
                 "window_episodes": ep.height, "window_candidates": {f"{f:g}": cands[f].height for f in FEES},
                 "day_episodes": opp.height, "day_candidates": {f"{f:g}": day_cands[f].height for f in FEES},
                 "deltas_ms": DELTAS, "rts_ms": RTS, "machine_D_us": MACHINE_D_US, "race_fee": RACE_FEE, "fees": FEES,
                 "reg_deltas_ms": REG_DELTAS, "lev_delta_range_ms": list(LEV_DELTA_RANGE), "q_max_btc": Q_MAX,
                 "stale_cap_us": STALE_CAP_US, "markouts_s": list(MARKOUTS), "models": models, "oc_codes": OC,
                 "leg_index": leg_idx},
        "quotes": disp, "episodes": episodes, "cands": cand_out, "grid_window": grid_window, "grid_day": day_grid, "km": km,
        "thresholds": thresholds, "committed": committed_numbers(), "checks": CHECKS,
    }
    with open(f"{OUT}/data.js", "w") as fh:
        fh.write("window.P6_DATA=")
        json.dump(data, fh, separators=(",", ":"), allow_nan=False)
        fh.write(";\n")

    # ---------------------------------------------------------------- provenance
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
    raw = {f"{d}/{k}": md5(f".data/tardis/quotes/{d}/{k}.csv.gz") for d in (TRAIN, TEST) for k in LEGS_FILES}
    caches = {p: md5(p) for p in [f"{CACHE_F}/cells_{TRAIN}_exch.parquet", f"{CACHE_F}/cells_{TEST}_exch.parquet", po,
                                  f"{CACHE_S}/cells_{TRAIN}.parquet", f"{CACHE_S}/cells_{TEST}.parquet"] if os.path.exists(p)}
    outs = {f: {"md5": md5(f"{OUT}/{f}"), "bytes": os.path.getsize(f"{OUT}/{f}")} for f in sorted(os.listdir(OUT))
            if f != "provenance.json" and not f.startswith(".")}
    import lifelines, numba, sklearn  # noqa: E401
    prov = {"built_at_ist": subprocess.run(["date", "+%Y-%m-%d %H:%M:%S IST"], capture_output=True, text=True,
                                           env={**os.environ, "TZ": "Asia/Kolkata"}).stdout.strip(),
            "commit": git("rev-parse", "HEAD"), "builder_unmodified_vs_commit": git("status", "--porcelain", "demo/build_assets.py") == "",
            "command": "eval/run_guarded.sh .venv/bin/python -m demo.build_assets", "runtime_s": round(time.time() - t_all, 1),
            "python": sys.version.split()[0], "platform": platform.platform(),
            "packages": {"numpy": np.__version__, "polars": pl.__version__, "scikit-learn": sklearn.__version__, "numba": numba.__version__,
                         "lifelines": lifelines.__version__},
            "inputs_raw_md5": raw, "caches_checked_md5": caches,
            "params": {"deltas_ms": DELTAS, "rts_ms": RTS, "machine_D_us": MACHINE_D_US, "fees": FEES, "race_fee": RACE_FEE, "window_s": WINDOW_S,
                       "lead_in_s": LEAD_S, "tail_s": TAIL_S, "q_max": Q_MAX, "stale_cap_us": STALE_CAP_US, "markouts_s": list(MARKOUTS),
                       "legs": LEGS_FILES, "registered_deltas_ms": REG_DELTAS},
            "window": {"w0_us": w0, "w1_us": w1, "episodes": ep.height, "candidates": {f"{f:g}": cands[f].height for f in FEES},
                       "slice_quotes": sl.height, "rule": data["meta"]["window_rule"]},
            "checks": CHECKS, "outputs": outs}
    json.dump(prov, open(f"{OUT}/provenance.json", "w"), indent=1)
    log(f"done in {time.time() - t_all:.0f}s; outputs:", {k: v["bytes"] for k, v in outs.items()})


if __name__ == "__main__":
    main()
