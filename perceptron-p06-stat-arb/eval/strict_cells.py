"""Strict-simulator cells for Amendment 1 (S1/S2/S3), cached with a provenance fingerprint (P6-11).

A cache file is reused only if its fingerprint matches: git blob hashes of every source file that determines the
cells, md5 of the day's five input files, and the cell parameters. Otherwise it is rebuilt.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

import numpy as np
import polars as pl

from components.decay.survival import add_features
from components.decision import policies as P
from components.decision.autoresearch.build_cells import COMPUTE_US, DELTAS_MS, FEES, LEGS_FILES
from components.decision.lev import add_lev_columns
from components.detector.cross import detect
from components.sim.fills import truth_books
from components.sim.strict import simulate_strict
from eval.falsification import day_q
from eval.run_baseline import pair_group

CACHE = ".cache/sensitivity"
FP_FILES = ["eval/strict_cells.py", "components/sim/strict.py", "components/sim/fills.py", "components/detector/cross.py",
            "components/decision/policies.py", "components/decay/survival.py", "components/costs/fees.py", "components/feed/normalize.py",
            "components/decision/lev.py", "components/decision/autoresearch/build_cells.py", "eval/run_baseline.py", "eval/falsification.py"]
PARAMS = {"fees": FEES, "deltas_ms": DELTAS_MS, "compute_us": COMPUTE_US, "q_max": 0.05, "stale_cap_us": 1e6, "markouts_s": [1.0, 10.0],
          "theta_bps": 1.0, "legs": LEGS_FILES}


def blob(path: str) -> str:
    return subprocess.run(["git", "hash-object", path], capture_output=True, text=True, check=True).stdout.strip()


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(date: str) -> dict:
    return {"sources": {f: blob(f) for f in FP_FILES},
            "data": {k: md5(f".data/tardis/quotes/{date}/{k}.csv.gz") for k in LEGS_FILES}, "params": PARAMS}


def build(date: str) -> pl.DataFrame:
    q, legs = day_q(date)
    opp = add_lev_columns(pair_group(add_features(detect(q, legs, "ts_exch_us", theta_bps=1.0))), legs)
    books = truth_books(q)
    out = []
    for f in FEES:
        o = P.with_net(opp, f"f{f:g}").filter(pl.col("net0_bps") > 0)
        for d_ms in DELTAS_MS:
            d = d_ms * 1000.0
            c = o.with_columns((pl.col("t_start_us") + int(d)).alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))
            it = P.intents(c, np.ones(c.height, bool), c["t_obs_us"].to_numpy() + COMPUTE_US, c["net0_bps"].to_numpy(), "all")
            r = simulate_strict(it, books, {l: d for l in legs}, {l: f for l in legs}, PARAMS["q_max"], PARAMS["stale_cap_us"],
                                tuple(PARAMS["markouts_s"]))
            out.append(it.join(r, on="opp_id", how="inner").with_columns(
                pl.lit(f).alias("fee_bps"), pl.lit(d_ms).alias("delta_ms"), pl.lit(float(2 * d_ms + COMPUTE_US / 1000)).alias("L_ms"),
                pl.lit(date).alias("part"), (pl.col("t_start_us") // 3_600_000_000).alias("hour")))
    return pl.concat(out, how="diagonal_relaxed")


def strict_cells(date: str) -> tuple[pl.DataFrame, dict]:
    os.makedirs(CACHE, exist_ok=True)
    pc, pf = f"{CACHE}/cells_{date}.parquet", f"{CACHE}/cells_{date}.fp.json"
    fp = fingerprint(date)
    if os.path.exists(pc) and os.path.exists(pf) and json.load(open(pf)) == fp:
        return pl.read_parquet(pc), fp
    c = build(date)
    c.write_parquet(pc)
    json.dump(fp, open(pf, "w"), indent=1)
    return c, fp
