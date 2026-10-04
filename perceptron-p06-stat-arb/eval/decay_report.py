"""MVP decay report with uncertainty: "how fast does the opportunity typically decay?"

Part A — held-out day 2026-10-01, 9 BTC legs, exchange clock. Kaplan–Meier per ordered venue pair:
  median lifetime with (i) the exponential-Greenwood 95% CI (lifelines; assumes independent episodes) and
  (ii) an hour-block bootstrap 95% CI (200 resamples of the day's 24 hours; honest under the strong
  clustering of episodes in time), plus S(1 ms), S(10 ms), S(100 ms) with Greenwood CIs.
Part B — stability across months: pooled and per-instrument-group KM medians for every walk-forward day
  (5 legs, cached episodes from eval/falsification.py), with hour-block bootstrap CIs.
Usage: eval/run_guarded.sh .venv/bin/python -m eval.decay_report --days 2025-10-01 ... 2026-10-01
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from lifelines import KaplanMeierFitter  # noqa: E402
from lifelines.utils import median_survival_times  # noqa: E402

from components.decay.survival import add_features  # noqa: E402
from components.detector.cross import detect  # noqa: E402
from eval.run_baseline import load, pair_group  # noqa: E402

LEGS9 = "binance_BTCUSDT,binance-futures_BTCUSDT,coinbase_BTC-USD,okex_BTC-USDT,okex-swap_BTC-USDT-SWAP,bybit_BTCUSDT,kraken_BTC-USD,bitstamp_BTCUSD,deribit_BTC-PERPETUAL".split(",")
PERP = ("binance-futures", "okex-swap", "bybit", "deribit")
N_BOOT = 200
TIMES = (1.0, 10.0, 100.0)


def km_median_np(T: np.ndarray, E: np.ndarray) -> float:
    """Product-limit median (smallest t with S(t) <= 0.5), matching lifelines' definition."""
    if T.size == 0:
        return float("nan")
    o = np.argsort(T, kind="mergesort")
    T, E = T[o], E[o].astype(float)
    uniq, start = np.unique(T, return_index=True)
    d = np.add.reduceat(E, start)
    at_risk = T.size - start
    S = np.cumprod(1.0 - d / at_risk)
    j = np.flatnonzero(S <= 0.5)
    return float(uniq[j[0]]) if j.size else float("inf")


def block_boot_median(T, E, hour, n=N_BOOT, seed=0) -> tuple[float, float]:
    hours = np.unique(hour)
    by_h = {h: np.flatnonzero(hour == h) for h in hours}
    rng = np.random.default_rng(seed)
    meds = []
    for _ in range(n):
        idx = np.concatenate([by_h[h] for h in rng.choice(hours, hours.size, replace=True)])
        meds.append(km_median_np(T[idx], E[idx]))
    meds = np.asarray(meds)
    meds = meds[np.isfinite(meds)]
    return (float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))) if meds.size else (float("nan"), float("nan"))


def ci_at(km: KaplanMeierFitter, t: float) -> tuple[float, float, float]:
    sf, ci = km.survival_function_, km.confidence_interval_survival_function_
    i = np.searchsorted(sf.index.to_numpy(), t, side="right") - 1
    if i < 0:
        return 1.0, 1.0, 1.0
    return float(sf.iloc[i, 0]), float(ci.iloc[i, 0]), float(ci.iloc[i, 1])


def publication_bounds(opp: pl.DataFrame, ts_by_leg: dict[str, np.ndarray]) -> pl.DataFrame:
    """Interval bounds on each episode's true lifetime implied by the venues' publication times.
    True start ∈ (previous publication of the venue that opened it, t_start]; true end ∈ (previous publication of the venue
    that closed it, t_end]. Hence T ∈ [max(0, prev_close − t_start), t_end − prev_open]. If both venues published at the same
    instant, the earlier previous publication is used (wider, conservative). Censored episodes keep their observed time."""
    t0 = opp["t_start_us"].to_numpy(); t1 = t0 + opp["duration_us"].to_numpy()
    sell = opp["pair"].str.split(" > ").list.get(0).to_numpy(); buy = opp["pair"].str.split(" > ").list.get(1).to_numpy()
    prev_open = np.full(t0.size, np.inf); prev_close = np.full(t0.size, np.inf)
    for side in (sell, buy):
        for leg in np.unique(side):
            m = side == leg
            ts = ts_by_leg[leg]
            for t, prev in ((t0, prev_open), (t1, prev_close)):
                i = np.searchsorted(ts, t[m], side="left")
                hit = (i < ts.size) & (ts[np.clip(i, 0, ts.size - 1)] == t[m])
                pv = np.where(i > 0, ts[np.clip(i - 1, 0, ts.size - 1)], t[m]).astype(float)
                cur = prev[m]
                prev[m] = np.where(hit, np.minimum(cur, pv), cur)
    prev_open = np.where(np.isfinite(prev_open), prev_open, t0)
    prev_close = np.where(np.isfinite(prev_close), prev_close, t1)
    cens = opp["censored"].to_numpy()
    lo = np.where(cens, t1 - t0, np.maximum(0.0, prev_close - t0))
    hi = np.where(cens, t1 - t0, t1 - prev_open)
    return opp.with_columns(pl.Series("T_lo_ms", (lo + 1) / 1000.0), pl.Series("T_hi_ms", (hi + 1) / 1000.0))


def bounds_summary(g: pl.DataFrame) -> dict:
    E = (~g["censored"]).to_numpy()
    out = {}
    for k in ("lo", "hi"):
        km = KaplanMeierFitter().fit(g[f"T_{k}_ms"].to_numpy(), E)
        out[f"median_{k}_ms"] = float(km.median_survival_time_)
        out[f"S10_{k}"] = float(km.survival_function_at_times([10.0]).iloc[0])
    return out


def summarise(g: pl.DataFrame, label: str) -> dict:
    T = (g["duration_us"].to_numpy() + 1) / 1000.0
    E = (~g["censored"]).to_numpy()
    km = KaplanMeierFitter().fit(T, E)
    med = float(km.median_survival_time_)
    gw = median_survival_times(km.confidence_interval_).to_numpy().ravel()
    lo, hi = block_boot_median(T, E, (g["t_start_us"].to_numpy() // 3_600_000_000))
    row = {"group": label, "n": g.height, "censored_frac": float(1 - E.mean()), "median_ms": med,
           "median_ci_greenwood": [float(gw[0]), float(gw[1])], "median_ci_hour_block": [lo, hi]}
    for t in TIMES:
        s, l, h = ci_at(km, t)
        row[f"S({t:g}ms)"] = [s, l, h]
    if "T_lo_ms" in g.columns:
        row.update(bounds_summary(g))
    return row, km


def part_a(date: str) -> tuple[list[dict], dict]:
    q = load(".data/tardis", date, LEGS9)
    legs = sorted(q["leg"].unique().to_list())
    opp = pair_group(add_features(detect(q, legs, "ts_exch_us", theta_bps=1.0)))
    ts_by_leg = {l: np.unique(g["ts_exch_us"].to_numpy()) for (l,), g in q.group_by(["leg"])}
    opp = publication_bounds(opp.with_columns((pl.col("sell_venue") + " > " + pl.col("buy_venue")).alias("pair")), ts_by_leg)
    del q
    rows, curves = [], {}
    r, km = summarise(opp, "all pairs")
    rows.append(r); curves["all pairs"] = km
    for (grp,), g in opp.group_by(["instr_group"], maintain_order=True):
        r, km = summarise(g, f"group: {grp}")
        rows.append(r)
    pair_rows = []
    for (pair,), g in opp.group_by(["pair"]):
        if g.height >= 200:
            r, km = summarise(g, pair)
            pair_rows.append(r); curves[pair] = km
    pair_rows.sort(key=lambda r: -r["n"])
    return rows + pair_rows, curves


def part_b(days: list[str]) -> list[dict]:
    out = []
    for d in days:
        p = f".cache/falsification/opp_{d}_exch.parquet"
        if not os.path.exists(p):
            continue
        o = pl.read_parquet(p)
        if "t_start_us" not in o.columns:   # older cache files: rebuild hour from opp_id order is impossible → skip CI
            o = o.with_columns(pl.lit(0, dtype=pl.Int64).alias("t_start_us"))
        o = o.with_columns(pl.col("pair").str.split(" > ").alias("_p")).with_columns(
            pl.col("_p").list.get(0).str.split(":").list.first().is_in(list(PERP)).alias("_sp"),
            pl.col("_p").list.get(1).str.split(":").list.first().is_in(list(PERP)).alias("_bp"))
        o = o.with_columns(pl.when(pl.col("_sp") & pl.col("_bp")).then(pl.lit("perp-perp"))
                           .when(pl.col("_sp") | pl.col("_bp")).then(pl.lit("spot-perp")).otherwise(pl.lit("spot-spot")).alias("instr_group"))
        q = load(".data/tardis", d, LEGS9[:5])
        ts_by_leg = {l: np.unique(g["ts_exch_us"].to_numpy()) for (l,), g in q.group_by(["leg"])}
        del q
        o = publication_bounds(o, ts_by_leg)
        r, _ = summarise(o, "all pairs")
        r["day"] = d
        for (grp,), g in o.group_by(["instr_group"], maintain_order=True):
            rr, _ = summarise(g, grp)
            r[f"median_ms[{grp}]"] = rr["median_ms"]
        out.append(r)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-10-01")
    ap.add_argument("--days", nargs="*", default=[])
    a = ap.parse_args()
    rows, curves = part_a(a.date)
    months = part_b(a.days)
    res = {"part_a_date": a.date, "part_a": rows, "part_b": months,
           "commit": (os.environ.get("P6_COMMIT") or subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()),
           "command": "eval/run_guarded.sh .venv/bin/python -m eval.decay_report --days " + " ".join(a.days)}
    json.dump(res, open("eval/results/decay_report.json", "w"), indent=1)

    fmt = lambda v: f"{v:.1f}" if np.isfinite(v) else "∞"  # noqa: E731
    L = [f"# Decay report — how fast cross-venue BTC mispricings close ({a.date}, 9 legs, exchange clock)", "",
         "Episode = a cross of ≥ 1 bp beyond the pair's EWMA fair basis (C6 detector), from the first to the last exchange "
         "timestamp at which it is open. Kaplan–Meier with right-censoring at feed gaps (> 30 s). Greenwood CIs assume "
         "independent episodes; episodes cluster in time, so the **hour-block bootstrap CI** (200 resamples of the 24 hours) "
         "is the one to quote.", "",
         "**Resolution caveat** (`eval/results/update_cadence.md`): in these samples Binance spot and OKX quotes are published on a "
         "100 ms grid and Binance perpetual quotes every 26 ms, while Coinbase and Kraken update within milliseconds. A lifetime "
         "cannot be resolved below the cadence of the venues involved, so sub-26 ms decay is only measurable on Coinbase/Kraken/Deribit pairs.", "",
         "**Publication-time bounds:** each lifetime is only known to lie in [max(0, prev. publication of the closing venue − start), "
         "end − prev. publication of the opening venue]; Kaplan–Meier on the two ends brackets the true curve (`median bounds`).", "",
         "| group / ordered pair (sell > buy) | n | median lifetime (ms) | median bounds (ms) | 95% CI hour-block | 95% CI Greenwood | S(1 ms) | S(10 ms) | S(100 ms) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        s = [r[f"S({t:g}ms)"] for t in TIMES]
        L.append(f"| {r['group']} | {r['n']:,} | {fmt(r['median_ms'])} | [{fmt(r.get('median_lo_ms', float('nan')))}, {fmt(r.get('median_hi_ms', float('nan')))}] | "
                 f"[{fmt(r['median_ci_hour_block'][0])}, {fmt(r['median_ci_hour_block'][1])}] | "
                 f"[{fmt(r['median_ci_greenwood'][0])}, {fmt(r['median_ci_greenwood'][1])}] | "
                 + " | ".join(f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]" for v in s) + " |")
    if months:
        L += ["", "## Stability across months (5 walk-forward legs, first day of each month)", "",
              "| day | episodes | median (ms) | median bounds (ms) | 95% CI hour-block | perp-perp | spot-perp | spot-spot |", "|---|---|---|---|---|---|---|---|"]
        for r in months:
            L.append(f"| {r['day']} | {r['n']:,} | {fmt(r['median_ms'])} | [{fmt(r['median_lo_ms'])}, {fmt(r['median_hi_ms'])}] | "
                     f"[{fmt(r['median_ci_hour_block'][0])}, {fmt(r['median_ci_hour_block'][1])}] | "
                     f"{fmt(r.get('median_ms[perp-perp]', float('nan')))} | {fmt(r.get('median_ms[spot-perp]', float('nan')))} | "
                     f"{fmt(r.get('median_ms[spot-spot]', float('nan')))} |")
        med = np.array([r["median_ms"] for r in months])
        L += ["", f"Across {len(months)} days the pooled median lifetime ranges {med.min():.1f}–{med.max():.1f} ms (median of medians {np.median(med):.1f} ms)."]
    L += ["", f"Commit `{res['commit']}` · `{res['command']}`", ""]
    open("eval/results/decay_report.md", "w").write("\n".join(L))

    fig, axes = plt.subplots(1, 2 if months else 1, figsize=(14 if months else 7, 4.8))
    axes = np.atleast_1d(axes)
    ax = axes[0]
    show = ["all pairs"] + [r["group"] for r in rows if r["group"] in curves and r["group"] != "all pairs"][:6]
    for name in show:
        km = curves[name]
        sf, ci = km.survival_function_, km.confidence_interval_survival_function_
        t = sf.index.to_numpy()
        ax.step(t, sf.iloc[:, 0], where="post", lw=2.2 if name == "all pairs" else 1.2, label=name, color="k" if name == "all pairs" else None)
        ax.fill_between(t, ci.iloc[:, 0], ci.iloc[:, 1], step="post", alpha=0.18)
    ax.set_xscale("log"); ax.set_xlim(0.1, 5000); ax.set_ylim(0, 1.01)
    ax.set_xlabel("time since the mispricing appeared (ms, exchange clock)"); ax.set_ylabel("share still open S(t), 95% CI")
    ax.set_title(f"Kaplan–Meier decay by venue pair, {a.date}"); ax.legend(fontsize=7)
    if months:
        ax = axes[1]
        x = np.arange(len(months))
        med = [r["median_ms"] for r in months]
        lo = [r["median_ms"] - r["median_ci_hour_block"][0] for r in months]
        hi = [r["median_ci_hour_block"][1] - r["median_ms"] for r in months]
        ax.errorbar(x, med, yerr=[lo, hi], fmt="o-", color="k", label="all pairs (hour-block 95% CI)")
        for grp in ("perp-perp", "spot-perp", "spot-spot"):
            ax.plot(x, [r.get(f"median_ms[{grp}]", np.nan) for r in months], ".--", label=grp)
        ax.set_xticks(x, [r["day"][:7] for r in months], rotation=45, fontsize=7)
        ax.set_ylabel("median lifetime (ms)"); ax.set_title("Median lifetime, first day of each month (5 legs)"); ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig("eval/results/decay_report.png", dpi=130)
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
