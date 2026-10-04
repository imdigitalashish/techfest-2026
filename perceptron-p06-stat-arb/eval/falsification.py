"""ADR 001 falsification tests 1 and 3.

walkforward — Test 1 (walk-forward superiority). For consecutive Tardis first-of-month days, every
    decision rule is fitted on day i−1's simulator-labelled cells and scored on day i. The cells are
    taker fee ∈ {1, 2} bps/leg × one-way latency δ ∈ {1, 5, 20} ms, with 5 BTC legs (as in the ratchet).
    A paired bootstrap over test days of (LEV − tuned per-pair threshold) total P&L gives a 95% CI.
    The claim "LEV beats the threshold" is FALSIFIED if the lower bound is ≤ 0.
clockskew — Test 3 (causal replay robustness). The 2026-09-01 → 2026-10-01 comparison is re-run with
    (a) receive-time detection (Tardis collector clock) and (b) per-venue exchange-clock offsets
    ~ U(−5, +5) ms (3 seeds, applied to both days and to the fill truth). Reports pair half-life rank
    stability and whether the LEV − threshold uplift keeps its sign.

Usage (heavy; run one at a time):
  nice -n 10 .venv/bin/python -m eval.falsification walkforward --days 2025-11-01 2025-12-01 ... 2026-10-01
  nice -n 10 .venv/bin/python -m eval.falsification clockskew
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np
import polars as pl
from lifelines import KaplanMeierFitter
from scipy.stats import spearmanr

from components.decay.survival import add_features
from components.decision import policies as P
from components.decision.autoresearch import rules as R
from components.decision.autoresearch.build_cells import COMPUTE_US, DELTAS_MS, FEES, LEGS_FILES
from components.decision.lev import add_lev_columns
from components.detector.cross import detect
from components.sim.fills import simulate, truth_books
from eval.run_baseline import load, pair_group

CACHE = ".cache/falsification"
LABELS = ["pnl_usd", "pnl_bps", "outcome"]
POLICIES = {
    "naive": (lambda tr: None, lambda m, te: np.ones(te.height, dtype=bool)),
    "threshold_pair": (lambda tr: R.fit_threshold(tr, ["pair_id", "fee_bps", "delta_ms"]), R.act_threshold),
    "ev_kmpair": (lambda tr: R.fit_ev(tr, ["pair_id"]), R.act_ev),
    "gbm_clf": (lambda tr: R.fit_gbm_clf(tr), R.act_gbm_clf),
    "lev": (lambda tr: R.fit_gbm_reg(tr), R.act_gbm_reg),
    "lev_edge_only": (lambda tr: R.fit_gbm_reg(tr, x=R.EDGE_ONLY_X), R.act_gbm_reg),  # Test 2 ablation
}


def cells(q: pl.DataFrame, legs: list[str], part: str, clock: str = "ts_exch_us", feed_extra: bool = True):
    """Simulator-labelled candidates for every (fee, δ) cell, plus the raw episodes."""
    opp = add_lev_columns(pair_group(add_features(detect(q, legs, clock, theta_bps=1.0))), legs)
    books = truth_books(q)
    out = []
    for f in FEES:
        o = P.with_net(opp, f"f{f:g}").filter(pl.col("net0_bps") > 0)
        for d_ms in DELTAS_MS:
            d = d_ms * 1000.0
            shift = int(d) if feed_extra else 0
            c = o.with_columns((pl.col("t_start_us") + shift).alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))
            it = P.intents(c, np.ones(c.height, bool), c["t_obs_us"].to_numpy() + COMPUTE_US, c["net0_bps"].to_numpy(), "all")
            r = simulate(it, books, {l: d for l in legs}, {l: f for l in legs}, 0.05)
            out.append(it.join(r.select("opp_id", "outcome", "pnl_usd", "pnl_bps"), on="opp_id").with_columns(
                pl.lit(f).alias("fee_bps"), pl.lit(d_ms).alias("delta_ms"),
                pl.lit(float(2 * d_ms + COMPUTE_US / 1000)).alias("L_ms"), pl.lit(part).alias("part"),
                (pl.col("t_start_us") // 3_600_000_000).alias("hour")))
    return pl.concat(out, how="diagonal_relaxed"), opp


def day_q(date: str, offsets: dict | None = None) -> tuple[pl.DataFrame, list[str]]:
    q = load(".data/tardis", date, LEGS_FILES)
    legs = sorted(q["leg"].unique().to_list())
    if len(legs) != len(LEGS_FILES):
        raise RuntimeError(f"{date}: expected {len(LEGS_FILES)} legs, got {legs}")
    if offsets:
        q = q.with_columns(pl.col("ts_exch_us") + pl.col("leg").replace_strict(offsets, return_dtype=pl.Int64))
    return q, legs


def cached_cells(date: str, tag: str = "exch", offsets: dict | None = None, clock: str = "ts_exch_us", feed_extra: bool = True):
    os.makedirs(CACHE, exist_ok=True)
    pc, po = f"{CACHE}/cells_{date}_{tag}.parquet", f"{CACHE}/opp_{date}_{tag}.parquet"
    if os.path.exists(pc) and os.path.exists(po):
        return pl.read_parquet(pc), pl.read_parquet(po)
    q, legs = day_q(date, offsets)
    c, o = cells(q, legs, date, clock, feed_extra)
    c.write_parquet(pc)
    o.select("opp_id", "pair", "duration_us", "censored", "edge0_bps").write_parquet(po)
    return c, o.select("opp_id", "pair", "duration_us", "censored", "edge0_bps")


def score_policies(train: pl.DataFrame, test: pl.DataFrame) -> list[dict]:
    rows = []
    feats = test.drop(LABELS)
    for name, (fit, act) in POLICIES.items():
        m = fit(train)
        mask = np.asarray(act(m, feats), dtype=bool)
        ch = test.filter(pl.Series(mask))
        per_cell = {(f, d): 0.0 for f in FEES for d in DELTAS_MS}
        if ch.height:
            for r in ch.group_by("fee_bps", "delta_ms").agg(pl.col("pnl_usd").sum()).iter_rows(named=True):
                per_cell[(r["fee_bps"], r["delta_ms"])] = r["pnl_usd"]
        rows.append({"policy": name, "total": float(sum(per_cell.values())), "n": ch.height,
                     "cells": {f"f{f:g}_d{d:g}": round(v, 2) for (f, d), v in per_cell.items()}})
    return rows


def t_ci(x: np.ndarray) -> tuple[float, float]:
    from scipy.stats import t as student_t
    if x.size < 2:
        return float("nan"), float("nan")
    h = student_t.ppf(0.975, x.size - 1) * x.std(ddof=1) / np.sqrt(x.size)
    return float(x.mean() - h), float(x.mean() + h)


def sign_p(x: np.ndarray) -> float:
    """One-sided sign-test p-value for 'more days positive than chance'."""
    from scipy.stats import binomtest
    k = int((x > 0).sum())
    return float(binomtest(k, x.size, 0.5, alternative="greater").pvalue)


def boot_ci(x: np.ndarray, n: int = 10000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, x.size), replace=True).mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def walkforward(days: list[str]) -> dict:
    data = {}
    for d in days:
        t0 = time.time()
        data[d] = cached_cells(d)[0]
        print(f"cells {d}: {data[d].height} rows ({time.time() - t0:.0f}s)", flush=True)
    per_day = []
    for prev, cur in zip(days[:-1], days[1:]):
        for r in score_policies(data[prev], data[cur]):
            per_day.append({"train": prev, "test": cur, **r})
        print("scored", cur, flush=True)
    df = pl.DataFrame([{k: v for k, v in r.items() if k != "cells"} for r in per_day])
    wide = df.pivot(on="policy", index="test", values="total").sort("test")
    out = {"days": days, "per_day": per_day, "table": wide.to_dicts(), "comparisons": {}}
    for a, b in [("lev", "threshold_pair"), ("gbm_clf", "threshold_pair"), ("ev_kmpair", "threshold_pair"), ("threshold_pair", "naive"),
                 ("lev", "lev_edge_only")]:
        diff = (wide[a] - wide[b]).to_numpy()
        lo, hi = boot_ci(diff)
        tlo, thi = t_ci(diff)
        out["comparisons"][f"{a} - {b}"] = {"mean_usd_per_day": float(diff.mean()), "ci95": [lo, hi], "t_ci95": [tlo, thi],
                                            "days_positive": int((diff > 0).sum()), "sign_p": sign_p(diff), "n_days": int(diff.size),
                                            "falsified (lower bound <= 0)": bool(lo <= 0 or tlo <= 0)}
    # per-cell LEV − threshold
    cell_keys = list(per_day[0]["cells"])
    pc = {}
    for k in cell_keys:
        lev = np.array([r["cells"][k] for r in per_day if r["policy"] == "lev"])
        thr = np.array([r["cells"][k] for r in per_day if r["policy"] == "threshold_pair"])
        lo, hi = boot_ci(lev - thr)
        pc[k] = {"mean": float((lev - thr).mean()), "ci95": [lo, hi], "days_positive": int(((lev - thr) > 0).sum())}
    out["lev_minus_threshold_by_cell"] = pc
    return out


def km_pairs(opp: pl.DataFrame, min_n: int = 200) -> dict[str, float]:
    res = {}
    for (pair,), g in opp.group_by(["pair"]):
        if g.height >= min_n:
            km = KaplanMeierFitter().fit((g["duration_us"].to_numpy() + 1) / 1000.0, (~g["censored"]).to_numpy())
            res[pair] = float(km.median_survival_time_)
    return res


def clockskew(train_day: str, test_day: str, seeds: list[int], max_skew_us: int) -> dict:
    variants = [("exch", None, "ts_exch_us", True), ("recv", None, "ts_recv_us", False)]
    legs = sorted(day_q(test_day)[1])
    for s in seeds:
        rng = np.random.default_rng(s)
        variants.append((f"skew{s}", {l: int(rng.integers(-max_skew_us, max_skew_us + 1)) for l in legs}, "ts_exch_us", True))
    out = {"train": train_day, "test": test_day, "max_skew_us": max_skew_us, "variants": []}
    base_pairs = None
    for tag, offs, clock, feed_extra in variants:
        t0 = time.time()
        tr, _ = cached_cells(train_day, tag, offs, clock, feed_extra)
        te, opp = cached_cells(test_day, tag, offs, clock, feed_extra)
        pairs = km_pairs(opp)
        if base_pairs is None:
            base_pairs = pairs
        common = sorted(set(pairs) & set(base_pairs))
        rho = float(spearmanr([base_pairs[p] for p in common], [pairs[p] for p in common]).statistic) if len(common) > 2 else None
        km = KaplanMeierFitter().fit((opp["duration_us"].to_numpy() + 1) / 1000.0, (~opp["censored"]).to_numpy())
        pol = {r["policy"]: r for r in score_policies(tr, te)}
        out["variants"].append({
            "variant": tag, "offsets_us": offs, "episodes_test": opp.height, "median_lifetime_ms": float(km.median_survival_time_),
            "S10ms": float(km.survival_function_at_times([10.0]).iloc[0]), "pair_halflife_spearman_vs_exch": rho, "n_pairs": len(common),
            "totals": {k: v["total"] for k, v in pol.items()},
            "uplift_lev_minus_threshold": pol["lev"]["total"] - pol["threshold_pair"]["total"],
            "uplift_ev_minus_threshold": pol["ev_kmpair"]["total"] - pol["threshold_pair"]["total"]})
        print(tag, json.dumps({k: out["variants"][-1][k] for k in ("median_lifetime_ms", "pair_halflife_spearman_vs_exch", "uplift_lev_minus_threshold")}),
              f"({time.time() - t0:.0f}s)", flush=True)
    return out


def md_walkforward(r: dict) -> str:
    pols = list(POLICIES)
    L = ["# Falsification test 1 — walk-forward (train on day i−1, test on day i)", "",
         f"Days: {', '.join(r['days'])}. 5 BTC legs ({', '.join(LEGS_FILES)}). Cells: fee {FEES} bps/leg × one-way latency {DELTAS_MS} ms; "
         "P&L = simulated USD/day summed over the 6 cells (0.05 BTC cap). Policies are fitted on the previous day only.", "",
         "| test day | " + " | ".join(pols) + " |", "|---|" + "---|" * len(pols)]
    for row in r["table"]:
        L.append(f"| {row['test']} | " + " | ".join(f"{row[p]:,.0f}" for p in pols) + " |")
    L += ["", "Falsified = the lower bound of either 95% interval is ≤ 0. With few test days the percentile bootstrap is optimistic, "
          "so the t-interval and a one-sided sign test are also reported.", "",
          "| comparison | mean USD/day | 95% bootstrap CI | 95% t-CI | days positive | sign-test p | falsified? |", "|---|---|---|---|---|---|---|"]
    for k, v in r["comparisons"].items():
        L.append(f"| {k} | {v['mean_usd_per_day']:+,.1f} | [{v['ci95'][0]:+,.1f}, {v['ci95'][1]:+,.1f}] | "
                 f"[{v['t_ci95'][0]:+,.1f}, {v['t_ci95'][1]:+,.1f}] | {v['days_positive']}/{v['n_days']} | {v['sign_p']:.3f} | "
                 f"{'YES' if v['falsified (lower bound <= 0)'] else 'no'} |")
    L += ["", "LEV − threshold by cell (mean USD/day, 95% CI, days positive):", "", "| cell | mean | CI | days + |", "|---|---|---|---|"]
    for k, v in r["lev_minus_threshold_by_cell"].items():
        L.append(f"| {k} | {v['mean']:+,.1f} | [{v['ci95'][0]:+,.1f}, {v['ci95'][1]:+,.1f}] | {v['days_positive']} |")
    return "\n".join(L) + "\n"


def md_clockskew(r: dict) -> str:
    L = ["# Falsification test 3 — clock skew and receive-time replay", "",
         f"Train {r['train']} → test {r['test']}, 5 BTC legs. `exch`: exchange clock (baseline). `recv`: detection on the Tardis collector "
         f"receive clock (real feed latency) with order latency δ. `skewN`: per-venue exchange-clock offsets ~ U(±{r['max_skew_us']/1000:g} ms), seed N, "
         "applied to detection and to fill truth on both days.", "",
         "| variant | test episodes | median lifetime (ms) | S(10 ms) | pair half-life Spearman vs exch | threshold P&L | EV P&L | LEV P&L | LEV − threshold |",
         "|---|---|---|---|---|---|---|---|---|"]
    for v in r["variants"]:
        t = v["totals"]
        rho = "—" if v["pair_halflife_spearman_vs_exch"] is None else f"{v['pair_halflife_spearman_vs_exch']:.3f}"
        L.append(f"| {v['variant']} | {v['episodes_test']:,} | {v['median_lifetime_ms']:.1f} | {v['S10ms']:.3f} | {rho} | {t['threshold_pair']:,.0f} | "
                 f"{t['ev_kmpair']:,.0f} | {t['lev']:,.0f} | {v['uplift_lev_minus_threshold']:+,.0f} |")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("walkforward"); w.add_argument("--days", nargs="+", required=True)
    c = sub.add_parser("clockskew"); c.add_argument("--train", default="2026-09-01"); c.add_argument("--test", default="2026-10-01")
    c.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2]); c.add_argument("--max-skew-ms", type=float, default=5.0)
    a = ap.parse_args()
    t0 = time.time()
    if a.cmd == "walkforward":
        res, name, md = walkforward(a.days), "falsification_walkforward", md_walkforward
    else:
        res, name, md = clockskew(a.train, a.test, a.seeds, int(a.max_skew_ms * 1000)), "falsification_clockskew", md_clockskew
    res["runtime_s"] = time.time() - t0
    res["commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    res["command"] = "python -m eval.falsification " + " ".join(sys.argv[1:])
    json.dump(res, open(f"eval/results/{name}.json", "w"), indent=1, default=str)
    text = md(res) + f"\nRuntime {res['runtime_s']:.0f} s · commit `{res['commit']}` · `{res['command']}`\n"
    open(f"eval/results/{name}.md", "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
