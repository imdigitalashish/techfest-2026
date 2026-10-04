"""FROZEN evaluator for the C8 decision ratchet. The loop never edits this file.

Prints one scalar line `METRIC <value>` (sum of validation P&L USD over 6 cells) plus secondary
metrics as JSON. The candidate sees training labels only.
Usage:
  .venv/bin/python -m components.decision.autoresearch.eval            # loop metric (val half of 09-01)
  .venv/bin/python -m components.decision.autoresearch.eval --holdout  # lead re-check on 2026-10-01
"""
from __future__ import annotations

import argparse
import importlib
import json
import time

import numpy as np
import polars as pl

LABELS = ["pnl_usd", "pnl_bps", "outcome"]


def score(chosen: pl.DataFrame, n_boot: int = 200, seed: int = 0) -> dict:
    total = float(chosen["pnl_usd"].sum()) if chosen.height else 0.0
    se = 0.0
    if chosen.height:
        v = chosen.group_by("hour").agg(pl.col("pnl_usd").sum())["pnl_usd"].to_numpy()
        if v.size > 2:
            rng = np.random.default_rng(seed)
            se = float(np.std([rng.choice(v, v.size).sum() for _ in range(n_boot)]))
    cells = (chosen.group_by("fee_bps", "delta_ms").agg(pl.col("pnl_usd").sum().round(2), pl.len().alias("n"))
             .sort("fee_bps", "delta_ms").to_dicts() if chosen.height else [])
    return {"metric": total, "boot_se": se, "n_trades": chosen.height,
            "hit_rate": float((chosen["pnl_usd"] > 0).mean()) if chosen.height else 0.0,
            "mean_bps": float(chosen["pnl_bps"].mean()) if chosen.height else 0.0, "cells": cells}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--candidate", default="components.decision.autoresearch.candidate")
    a = ap.parse_args()
    if a.holdout:
        df = pl.read_parquet(".cache/autoresearch/cells_holdout.parquet")
        train, test = df.filter(pl.col("part") == "train_full"), df.filter(pl.col("part") == "holdout")
    else:
        df = pl.read_parquet(".cache/autoresearch/cells_0901.parquet")
        train, test = df.filter(pl.col("part") == "train"), df.filter(pl.col("part") == "val")
    cand = importlib.import_module(a.candidate)
    t0 = time.time()
    model = cand.fit(train)
    mask = np.asarray(cand.act(model, test.drop(LABELS)), dtype=bool)
    assert mask.shape == (test.height,), "act() must return one bool per row"
    res = score(test.filter(pl.Series(mask)))
    res["all_trades_metric"] = float(test["pnl_usd"].sum())
    res["seconds"] = time.time() - t0
    res["config"] = getattr(cand, "CONFIG", {})
    print(f"METRIC {res['metric']:.4f}")
    print(json.dumps(res, default=str))


if __name__ == "__main__":
    main()
