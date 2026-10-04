"""Live computation for the P6 demo: committed code on the committed window (demo/assets).

Everything here re-runs the same functions the walk-forward used, on the exact quote slice exported by
demo/build_assets.py:
- demo.build_assets.label wraps components/sim/fills.simulate and components/sim/strict.simulate_strict;
- the thresholds are the rules.fit_threshold tables;
- the LEV models are pickled sklearn regressors (rules.fit_gbm_reg). They are compiled to Numba with
  components/decision/compiled.build and timed in-kernel with compiled.make_timer.
The page works without this module (precomputed grid); with it, the page upgrades to live mode.
"""
from __future__ import annotations

import gzip
import json
import os
import pickle
import platform
import threading
import time

import numpy as np
import polars as pl

from components.decision.autoresearch import rules as R
from components.decision.compiled import RAW_FIELDS, build, make_timer, ns_per_tick
from components.sim.fills import LegBook
from demo.build_assets import OC, label

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")


def load_data() -> dict:
    raw = open(os.path.join(ASSETS, "data.js")).read().strip()
    assert raw.startswith("window.P6_DATA=") and raw.endswith(";")
    return json.loads(raw[len("window.P6_DATA="):-1])


def load_books() -> tuple[list[str], dict[str, LegBook]]:
    z = np.load(os.path.join(ASSETS, "window_books.npz"))
    legs = [str(x) for x in z["legs"]]
    return legs, {l: LegBook(z[f"ts__{i}"], z[f"bid__{i}"], z[f"ask__{i}"], z[f"bsz__{i}"], z[f"asz__{i}"]) for i, l in enumerate(legs)}


def nearest(grid: list[float], x: float) -> float:
    g = np.asarray(grid, float)
    return float(g[np.argmin(np.abs(np.log(g) - np.log(max(x, 1e-9))))])


class Live:
    def __init__(self) -> None:
        t0 = time.time()
        self.data = load_data()
        m = self.data["meta"]
        self.legs, self.books = load_books()
        assert self.legs == m["legs"], (self.legs, m["legs"])
        self.deltas, self.rts, self.machine_D_us = m["deltas_ms"], m["rts_ms"], float(m["machine_D_us"])
        self.cands = {}
        for f, cols in self.data["cands"].items():
            df = pl.DataFrame(cols)
            self.cands[float(f)] = df.with_columns(pl.col("t_start_us").cast(pl.Int64), pl.col("duration_us").cast(pl.Int64),
                                                   pl.col("opp_id").cast(pl.Int64))
        self.thr = {}
        for sim, rows in json.load(open(os.path.join(ASSETS, "thresholds.json"))).items():
            self.thr[sim] = {"by": ["pair_id", "fee_bps", "delta_ms", "D_ms"],
                             "th": {(r[0], r[1], r[2], r[3]): (np.inf if r[4] is None else r[4]) for r in rows}}
        self.models = {}
        for sim in ("frozen", "strict"):
            with gzip.open(os.path.join(ASSETS, f"lev_{sim}.pkl.gz"), "rb") as fh:
                self.models[sim] = pickle.load(fh)
        self.compiled: dict[str, tuple] = {}
        self.stage = "loaded assets; compiling LEV with Numba"
        self.timing: dict | None = None
        self.load_s = time.time() - t0
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ Numba warm-up (background thread)
    def warm(self) -> None:
        t0 = time.time()
        for sim, model in self.models.items():
            _, decide, _, a = build(model)
            timed = make_timer(decide)
            R0 = self._raw_rows(sim, 1.0, 1.0, self.machine_D_us)
            timed(R0, np.empty(R0.shape[0], np.uint64), np.empty(R0.shape[0]))   # triggers JIT
            self.compiled[sim] = (decide, timed, a)
            self.stage = f"compiled LEV ({sim})"
        self.stage = "timing the decision step on this machine"
        self.measure_timing()
        self.warm_s = time.time() - t0
        self.stage = "ready"

    def ready(self) -> bool:
        return self.stage == "ready"

    # ------------------------------------------------------------------ helpers
    def _raw_rows(self, sim: str, fee: float, d_ms: float, D_us: float) -> np.ndarray:
        c = self.cands[fee].with_columns(pl.lit(float(2 * d_ms + D_us / 1000)).alias("L_ms"), pl.lit(fee).alias("fee_bps"))
        return np.ascontiguousarray(c.select(RAW_FIELDS).to_numpy())

    def lev_values(self, sim: str, rows: pl.DataFrame) -> tuple[np.ndarray, str, float]:
        """E[P&L bps | x, L] per row: compiled Numba when warm (checked against sklearn), sklearn before that."""
        ref = self.models[sim].predict(rows.select(R.LEARN_X).to_numpy())
        if sim not in self.compiled or rows.height == 0:
            return ref, "sklearn (Numba still compiling)", 0.0
        _, timed, _ = self.compiled[sim]
        Rw = np.ascontiguousarray(rows.select(RAW_FIELDS).to_numpy())
        vals = np.empty(Rw.shape[0])
        with self._lock:
            timed(Rw, np.empty(Rw.shape[0], np.uint64), vals)
        return vals, "numba (components/decision/compiled.py)", float(np.max(np.abs(vals - ref)))

    def _rows(self, sim: str, fee: float, d_ms: float, D_us: float, thr_D_ms: float) -> pl.DataFrame:
        rows = label(self.cands[fee], self.books, self.legs, fee, d_ms, D_us, sim, self.data["meta"]["test_day"])
        if sim == "strict":
            rows = rows.filter(pl.col("valid"))
        # threshold lookup at the grid point the table was fitted on (09-01 grid)
        return rows.with_columns(pl.lit(nearest(self.deltas, d_ms)).alias("delta_ms"), pl.lit(thr_D_ms).alias("D_ms"))

    @staticmethod
    def _agg(rows: pl.DataFrame, mask: np.ndarray) -> dict:
        ch = rows.filter(pl.Series(mask))
        return {"usd": float(ch["pnl_usd"].sum()) if ch.height else 0.0, "n": int(ch.height),
                "n_both": int((ch["outcome"] == "both").sum()) if ch.height else 0}

    # ------------------------------------------------------------------ endpoints
    def evaluate(self, sim: str, fee: float, d_ms: float, D_us: float | None = None) -> dict:
        t0 = time.perf_counter()
        D_us = self.machine_D_us if D_us is None else float(D_us)
        rows = self._rows(sim, fee, d_ms, D_us, self.machine_D_us / 1000.0)
        acts = {"naive": np.ones(rows.height, bool), "thr": np.asarray(R.act_threshold(self.thr[sim], rows), bool)}
        vals, engine, err = self.lev_values(sim, rows)
        acts["lev"] = (vals > 0.0) & (rows["net0_bps"].to_numpy() > 0.0)
        ids = self.cands[fee]["opp_id"].to_list()
        pos = {o: i for i, o in enumerate(ids)}
        n = len(ids)
        oc, pnl, thr, lev, val = [-1] * n, [0.0] * n, [0] * n, [0] * n, [None] * n
        for k, (o, out, p) in enumerate(zip(rows["opp_id"].to_list(), rows["outcome"].to_list(), rows["pnl_usd"].to_list())):
            i = pos[o]
            oc[i], pnl[i], thr[i], lev[i], val[i] = OC[out], p, int(acts["thr"][k]), int(acts["lev"][k]), float(vals[k])
        return {"sim": sim, "fee": fee, "delta_ms": d_ms, "D_us": D_us, "thr_grid_delta_ms": nearest(self.deltas, d_ms),
                "tot": {p: self._agg(rows, m) for p, m in acts.items()}, "oc": oc, "pnl": pnl, "thr": thr, "lev": lev, "lev_value_bps": val,
                "lev_engine": engine, "lev_max_abs_err_vs_sklearn_bps": err, "elapsed_ms": (time.perf_counter() - t0) * 1e3}

    def race(self, rt_ms: float, d_ms: float, sim: str, trial_ids: list[int], machine_D_us: float | None = None) -> dict:
        """2×2: {you: δ + RT + δ, machine: δ + live p50 + δ} × {naive, tuned threshold}, at the race fee, on the whole window."""
        t0 = time.perf_counter()
        fee = float(self.data["meta"]["race_fee"])
        rt_ms = float(np.clip(rt_ms, 1.0, 2000.0))
        rt_grid = nearest(self.rts, rt_ms)
        if machine_D_us is None:
            machine_D_us = self.timing["p50_us"] if self.timing else None
        src = "live p50 measured on this machine" if self.timing else "committed decision_timing.json p50"
        if machine_D_us is None:
            machine_D_us = self.data["committed"]["decision_timing"]["in_kernel_ns"]["p50"] / 1e3
        out = {"rt_ms": rt_ms, "rt_threshold_grid_ms": rt_grid, "delta_ms": d_ms, "sim": sim, "fee": fee, "machine_D_us": machine_D_us,
               "machine_D_source": src}
        for who, D_us, thr_D in (("you", rt_ms * 1000.0, rt_grid), ("machine", machine_D_us, self.machine_D_us / 1000.0)):
            rows = self._rows(sim, fee, d_ms, D_us, thr_D)
            thr = np.asarray(R.act_threshold(self.thr[sim], rows), bool)
            out[who] = {"naive": self._agg(rows, np.ones(rows.height, bool)), "thr": self._agg(rows, thr), "n_rows": rows.height,
                        "L_ms": 2 * d_ms + D_us / 1000.0}
            by_id = {o: (oc, p, int(a)) for o, oc, p, a in zip(rows["opp_id"].to_list(), rows["outcome"].to_list(), rows["pnl_usd"].to_list(), thr)}
            out[who]["trials"] = [{"opp_id": o, "outcome": by_id.get(o, ("not sent", 0.0, 0))[0], "pnl_usd": by_id.get(o, (None, 0.0, 0))[1],
                                   "thr_would_act": by_id.get(o, (None, 0.0, 0))[2]} for o in trial_ids]
        out["elapsed_ms"] = (time.perf_counter() - t0) * 1e3
        return out

    def measure_timing(self, passes: int = 20) -> dict:
        """In-kernel timing of the compiled decision step (features + LEV + act) on this machine, as eval/decision_timing does."""
        sim = "frozen"
        if sim not in self.compiled:
            return {"ready": False}
        _, timed, a = self.compiled[sim]
        Rm = np.concatenate([self._raw_rows(sim, f, d, self.machine_D_us) for f in self.cands for d in self.deltas])
        ticks = np.empty(Rm.shape[0], np.uint64)
        vals = np.empty(Rm.shape[0])
        ns = []
        with self._lock:
            for _ in range(passes):
                timed(Rm, ticks, vals)
                ns.append(ticks.astype(np.float64) * ns_per_tick())
        ns = np.concatenate(ns)
        # sklearn on the batch path (LEARN_X columns of the same rows), as eval/decision_timing.py does
        Xm = np.concatenate([self.cands[f].with_columns(pl.lit(float(2 * d + self.machine_D_us / 1000)).alias("L_ms"), pl.lit(f).alias("fee_bps"))
                             .select(R.LEARN_X).to_numpy() for f in self.cands for d in self.deltas])
        ref = self.models[sim].predict(Xm)
        q = lambda p: float(np.quantile(ns, p)) / 1e3  # noqa: E731
        self.timing = {"ready": True, "p50_us": q(0.5), "p90_us": q(0.9), "p99_us": q(0.99), "p999_us": q(0.999), "n_calls": int(ns.size),
                       "tick_ns": ns_per_tick(), "exact_max_abs_err_bps": float(np.max(np.abs(vals - ref))),
                       "n_trees": int(a["n_trees"]), "n_nodes": int(a["n_nodes"]), "machine": platform.platform(), "processor": platform.processor(),
                       "measured_at": time.strftime("%H:%M:%S"), "note": "shared machine, load not controlled"}
        return self.timing
