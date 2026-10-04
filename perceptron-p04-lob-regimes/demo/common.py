"""Shared helpers for the P4 demo ("the alarm that cries wolf").

Imports the frozen evaluation code (components/, eval/) and never modifies it. The KS significance
level is varied with dataclasses.replace(ctx, cfg=...) and the empirical-null quantile with
dataclasses.replace(ctx, ks_thresholds=...), so every dial stop runs the committed run_episode.
"""
from __future__ import annotations

import dataclasses
import math
import os
import sys
import warnings
from pathlib import Path

import numpy as np

DEMO = Path(__file__).resolve().parent
ROOT = DEMO.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))
warnings.filterwarnings("ignore", category=RuntimeWarning)  # spurious Accelerate matmul warnings in LogisticHead.fit

from config_v2 import CFG_V2, SPLIT_V2, H_STEPS as H_STEPS_, STEP_S as STEP_S_  # noqa: E402,F401
from run_v2 import load_day  # noqa: E402

from components.adapter import POLICIES, build_context, run_episode  # noqa: E402
from components.evaluator import pointwise_logloss, score  # noqa: E402
from components.shift_detector import calibrate_ks_null, ks_pvalue_asymp, ks_stat_sorted  # noqa: E402

CACHE = DEMO / ".cache"
RESULTS = DEMO / "results"
EVAL_RESULTS = ROOT / "eval" / "results"

# Dial stops. Naive = textbook asymptotic KS p-value (Bonferroni over the 7 v1 features) at level alpha.
NAIVE_LOG10 = [-1, -2, -3, -5, -7, -10, -15, -20, -30, -50, -75, -100, -150, -200, -250, -300]
CAL_Q = [0.99, 0.999, 0.9999]  # empirical-null (leave-one-train-day-out) quantiles; 0.999 = committed ksc_refit
BIN_S = 600  # every committed / on-screen time series is binned at >= 10 minutes (Tardis ToS 9.2)


def stop_ids() -> list[str]:
    return [f"naive_{-k}" for k in NAIVE_LOG10] + [f"cal_{q}" for q in CAL_Q] + ["off"]


def nice_self() -> None:
    try:
        os.nice(10)
    except OSError:
        pass


def mem_level() -> int:
    try:
        import subprocess
        return int(subprocess.check_output(["sysctl", "-n", "kern.memorystatus_level"], text=True).strip())
    except Exception:
        return 100


def train_context():
    train = [load_day(d) for d in SPLIT_V2["train"]]
    return build_context(train, CFG_V2), train


def calibrated_thresholds(ctx, train, q: float) -> np.ndarray:
    if abs(q - CFG_V2["ksc"]["quantile"]) < 1e-12:
        return ctx.ks_thresholds
    k = CFG_V2["ks"]
    return calibrate_ks_null([f.X for f, _ in train], ctx.ks_idx, k["window"], k["subsample"],
                             CFG_V2["ksc"]["stride"], q)


def stop_episode(stop: str, f, l, ctx, cal_thr: dict):
    """Run the committed run_episode for one dial stop. Returns EpisodeResult."""
    if stop == "off":
        c = dataclasses.replace(ctx, cfg={**ctx.cfg, "ks": {**ctx.cfg["ks"], "alpha": 0.0}})
        return run_episode("ks_refit", f, l, c, POLICIES["ks_refit"])
    if stop.startswith("naive_"):
        a = 10.0 ** (-int(stop[6:]))
        c = dataclasses.replace(ctx, cfg={**ctx.cfg, "ks": {**ctx.cfg["ks"], "alpha": a}})
        return run_episode("ks_refit", f, l, c, POLICIES["ks_refit"])
    q = float(stop[4:])
    c = dataclasses.replace(ctx, ks_thresholds=cal_thr[q])
    return run_episode("ksc_refit", f, l, c, POLICIES["ksc_refit"])


def log10_separation_prob(m: int, n: int) -> float:
    """log10 of the exact probability, under exchangeability (i.i.d. null), that two samples of sizes m and n
    are completely separated (two-sample KS D = 1): 2 / C(m+n, m)."""
    log_c = math.lgamma(m + n + 1) - math.lgamma(m + 1) - math.lgamma(n + 1)
    return (math.log(2.0) - log_c) / math.log(10.0)


def ks_window_trace(X: np.ndarray, ctx) -> dict:
    """Per KS evaluation step of the naive rolling KS (same windows as RollingKS): max D over the monitored
    features and the Bonferroni-adjusted asymptotic p-value. Exactly the quantities RollingKS thresholds."""
    k = ctx.cfg["ks"]
    ref = [np.sort(ctx.ks_ref[:, j]) for j in range(ctx.ks_ref.shape[1])]
    steps, dmax, pbon = [], [], []
    for t in range(k["window"], X.shape[0], k["stride"]):
        cur = X[t - k["window"] + 1:t + 1:k["subsample"]][:, ctx.ks_idx]
        m = cur.shape[0]
        D = np.array([ks_stat_sorted(cur[:, j], ref[j]) for j in range(len(ref))])
        p = np.array([ks_pvalue_asymp(D[j], m, ref[j].shape[0]) for j in range(len(ref))])
        steps.append(t)
        dmax.append(D.max())
        pbon.append(p.min() * len(ref))
    return {"step": np.array(steps), "dmax": np.array(dmax), "pbon": np.array(pbon), "m": m}


def binned_mean(x: np.ndarray, n_bins: int, bin_steps: int = BIN_S) -> list:
    out = []
    for b in range(n_bins):
        seg = x[b * bin_steps:(b + 1) * bin_steps]
        seg = seg[~np.isnan(seg)]
        out.append(round(float(seg.mean()), 6) if seg.size else None)
    return out


CACHE_SCHEMA = 2


def cache_key(days: list[str], extra: tuple[str, ...] = ()) -> str:
    """Identity of a cache artifact: hash of the code that computes it (components/, eval configs and harness,
    demo builders) and of the inputs (manifest MD5s of the training and replay days, committed result files)."""
    import csv
    import hashlib
    h = hashlib.sha256(f"schema={CACHE_SCHEMA}".encode())
    files = sorted((ROOT / "components").rglob("*.py")) + [ROOT / "eval" / n for n in
            ("config.py", "config_v2.py", "run_v2.py", "run_baseline.py")] + \
        [DEMO / n for n in ("common.py", "build_replay.py", "build_splice.py")] + [ROOT / x for x in extra]
    for p in files:
        if p.exists() and "autoresearch" not in p.parts:
            h.update(p.relative_to(ROOT).as_posix().encode())
            h.update(p.read_bytes())
    md5 = {r["day"]: r["md5"] for r in csv.DictReader(open(ROOT / "data" / "manifest.csv")) if r["dtype"] == "book_snapshot_5"}
    for d in sorted(set(SPLIT_V2["train"]) | set(days)):
        h.update(f"{d}:{md5.get(d, 'missing')}".encode())
    return h.hexdigest()[:16]


def cache_valid(path: Path, key: str, **expect) -> bool:
    """A cache file is reused only if it parses, has the current schema and code/input key, and matches `expect`."""
    import json
    try:
        d = json.loads(path.read_text())
    except Exception:
        return False
    return d.get("schema") == CACHE_SCHEMA and d.get("cache_key") == key and all(d.get(k) == v for k, v in expect.items())
