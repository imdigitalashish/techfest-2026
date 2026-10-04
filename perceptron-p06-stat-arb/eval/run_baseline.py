"""End-to-end baseline evaluation (C11).

  decay report (MVP)  : Kaplan–Meier lifetimes of mispricing episodes on the exchange clock,
                        by pair group and edge bucket, plus the edge-magnitude decay curve.
  survival eval       : KM vs Weibull-AFT, integrated Brier (log-time) and C-index on the test set.
  policy frontier     : naive · tuned threshold · EV(KM) · EV(AFT) · EV+wait(AFT) · oracle,
                        across extra one-way latency δ and fee tiers, filled by the latency simulator.

Usage (from perceptron-p06-stat-arb/):
  .venv/bin/python -m eval.run_baseline --train 2026-09-01 --test 2026-10-01
  .venv/bin/python -m eval.run_baseline --train 2026-09-01 --split-day        # first 12 h train, last 12 h test
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time

import numpy as np
import polars as pl
from scipy.stats import spearmanr

from components.costs.fees import FEES_VERIFIED, TIERS, leg_venue, taker_bps
from components.decay.survival import add_features, evaluate, fit_km, fit_weibull_aft, km_summary
from components.decision import policies as P
from components.detector.cross import detect
from components.feed.normalize import load_tardis_day
from components.latency.model import feed_latency_table
from components.sim.fills import truth_books, simulate

USD = ("coinbase", "kraken", "bitstamp", "deribit")
DELTAS_MS = [0.0, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 50, 100, 250]
THETAS = [0.0, 0.5, 1, 2, 3, 5, 10]
Q_MAX = 0.05  # BTC per arbitrage (≈ USD 4k) — labelled sizing assumption


def load(root: str, date: str, include: list[str] | None) -> pl.DataFrame:
    q = load_tardis_day(root, date, include)
    return q.with_columns((pl.col("venue") + ":" + pl.col("instrument")).alias("leg"))


def pair_group(opp: pl.DataFrame) -> pl.DataFrame:
    sp, bp = pl.col("sell_is_perp") > 0, pl.col("buy_is_perp") > 0
    usd = lambda c: pl.col(c).str.split(":").list.first().is_in(list(USD))  # noqa: E731
    return opp.with_columns(
        pl.when(sp & bp).then(pl.lit("perp-perp")).when(sp | bp).then(pl.lit("spot-perp")).otherwise(pl.lit("spot-spot")).alias("instr_group"),
        pl.when(usd("sell_venue") == usd("buy_venue")).then(pl.lit("same-ccy")).otherwise(pl.lit("USD-vs-USDT")).alias("ccy_group"),
        pl.col("edge0_bps").cut([2, 5, 10], labels=["1-2bps", "2-5bps", "5-10bps", ">10bps"]).cast(pl.Utf8).alias("edge_bucket"),
        (pl.col("sell_venue") + " > " + pl.col("buy_venue")).alias("pair"),
    )


def edge_decay(opp: pl.DataFrame, books, deltas_ms) -> list[dict]:
    out = []
    for d in deltas_ms:
        r = []
        for (sv, bv), g in opp.group_by(["sell_venue", "buy_venue"]):
            t = g["t_start_us"].to_numpy() + d * 1000
            _, bid_s, _, _, _ = books[sv].at(t)
            _, _, ask_b, _, _ = books[bv].at(t)
            mid = 0.5 * (g["limit_sell_px"].to_numpy() + g["limit_buy_px"].to_numpy())
            e = (bid_s - ask_b) / mid * 1e4 - g["basis0_bps"].to_numpy()
            r.append(e / g["edge0_bps"].to_numpy())
        r = np.concatenate(r)
        out.append({"delta_ms": d, "mean_ratio": float(np.mean(r)), "median_ratio": float(np.median(r)),
                    "share_still_positive": float(np.mean(r > 0))})
    return out


def refresh_limits(it: pl.DataFrame, books, d_us: float, compute_us: float, tier: str) -> pl.DataFrame:
    """Re-read observed prices at the (delayed) decision time; drop if no longer profitable."""
    if it.height == 0:
        return it
    parts = []
    for (sv, bv), g in it.group_by(["sell_venue", "buy_venue"]):
        t_seen = g["t_decide_us"].to_numpy() - compute_us - d_us
        _, bid_s, _, bsz, _ = books[sv].at(t_seen)
        _, _, ask_b, _, asz = books[bv].at(t_seen)
        mid = 0.5 * (bid_s + ask_b)
        net = (bid_s - ask_b) / mid * 1e4 - g["basis0_bps"].to_numpy() - taker_bps(leg_venue(sv), tier) - taker_bps(leg_venue(bv), tier)
        parts.append(g.with_columns(pl.Series("limit_sell_px", bid_s), pl.Series("limit_buy_px", ask_b),
                                    pl.Series("size", np.minimum(bsz, asz)), pl.Series("net_refresh", net)).filter(pl.col("net_refresh") > 0))
    return pl.concat(parts).drop("net_refresh")


def summarise(res: pl.DataFrame, policy: str, tier: str, d_ms: float, extra: dict | None = None) -> dict:
    n = res.height
    row = {"policy": policy, "tier": tier, "delta_ms": d_ms, "n_trades": n,
           "both_fill_rate": float((res["outcome"] == "both").mean()) if n else 0.0,
           "pnl_usd": float(res["pnl_usd"].sum()) if n else 0.0,
           "mean_pnl_bps": float(res["pnl_bps"].mean()) if n else 0.0,
           "hit_rate": float((res["pnl_usd"] > 0).mean()) if n else 0.0}
    row.update(extra or {})
    return row


def run(args) -> dict:
    t_start = time.time()
    root = args.root
    include = args.legs.split(",") if args.legs else None
    if args.split_day:
        q = load(root, args.train, include)
        cut = q["ts_exch_us"].min() + 12 * 3600 * 1_000_000
        q_tr, q_te = q.filter(pl.col("ts_exch_us") < cut), q.filter(pl.col("ts_exch_us") >= cut)
        test_label = f"{args.train} 12-24h (train 0-12h)"
    else:
        q_tr, q_te = load(root, args.train, include), load(root, args.test, include)
        test_label = args.test
    legs = sorted(set(q_tr["leg"].unique().to_list()) & set(q_te["leg"].unique().to_list()))
    meta = {"train": args.train, "test": test_label, "legs": legs, "theta_detect_bps": args.theta, "q_max_btc": Q_MAX,
            "fees_verified": FEES_VERIFIED, "rows_train": q_tr.height, "rows_test": q_te.height,
            "assumptions": ["inventory pre-positioned on every venue (no transfers)",
                            "order one-way latency = feed one-way latency = δ for every venue (colo-style sweep)",
                            "IOC limit legs fill only if the exchange-time top of book is at/through our limit; size capped at top-of-book",
                            "unfilled-leg mismatch unwound on the same venue 2·δ later at top of book, paying taker fee",
                            "P&L marked against the EWMA fair basis observed at decision time",
                            "retail/vip fees are placeholders until research/notes/fees.md is verified; mm = 0 bps"]}

    lat = pl.concat([feed_latency_table(q_tr, "tardis-collector").with_columns(pl.lit("train").alias("day")),
                     feed_latency_table(q_te, "tardis-collector").with_columns(pl.lit("test").alias("day"))])

    opp_tr = pair_group(add_features(detect(q_tr, legs, "ts_exch_us", theta_bps=args.theta)))
    opp_te = pair_group(add_features(detect(q_te, legs, "ts_exch_us", theta_bps=args.theta)))
    books_tr, books_te = truth_books(q_tr), truth_books(q_te)
    del q_tr, q_te

    # ---------------- MVP decay report (exchange clock, test day)
    decay = {
        "overall_test": km_summary(opp_te).to_dicts(),
        "overall_train": km_summary(opp_tr).to_dicts(),
        "by_instr_group": km_summary(opp_te, ["instr_group"]).to_dicts(),
        "by_ccy_group": km_summary(opp_te, ["ccy_group"]).to_dicts(),
        "by_edge_bucket": km_summary(opp_te, ["edge_bucket"]).sort("mean_edge0_bps").to_dicts(),
        "top_pairs": km_summary(opp_te, ["pair"]).sort("n", descending=True).head(12).to_dicts(),
        "edge_decay": edge_decay(opp_te.sample(min(opp_te.height, 200_000), seed=0), books_te,
                                 [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 250, 500, 1000]),
        "episodes_per_hour_test": opp_te.height / 24.0 if not args.split_day else opp_te.height / 12.0,
    }

    # ---------------- survival models: train → test
    km = fit_km(opp_tr)
    aft = fit_weibull_aft(opp_tr)
    surv = {"km": evaluate(km, opp_te), "weibull_aft": evaluate(aft, opp_te),
            "aft_rho": aft.rho, "aft_beta": dict(zip(["%s" % f for f in __import__("components.decay.survival", fromlist=["FEATURES"]).FEATURES] + ["intercept"], map(float, aft.beta)))}

    # decision compute latency: single-opportunity EV evaluation in numpy (what C8 adds to L)
    x1 = opp_te.select(__import__("components.decay.survival", fromlist=["FEATURES"]).FEATURES).head(1).to_numpy()
    reps = 20000
    t0 = time.perf_counter()
    for _ in range(reps):
        P._s_at(aft, x1, np.array([1.0]))
    compute_us = (time.perf_counter() - t0) / reps * 1e6
    surv["ev_compute_us_per_opportunity"] = compute_us
    compute_us = float(np.ceil(compute_us))

    # ---------------- policy frontier on the test day
    rows, ranking = [], []
    for tier in args.tiers.split(","):
        fees = {l: taker_bps(leg_venue(l), tier) for l in legs}
        tr, te = P.with_net(opp_tr, tier), P.with_net(opp_te, tier)
        # oracle: zero latency, zero compute, every profitable episode
        o0 = te.with_columns(pl.col("t_start_us").alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))
        orc = simulate(P.naive(o0, 0.0), books_te, {l: 0.0 for l in legs}, fees, Q_MAX)
        oracle_pnl = float(orc["pnl_usd"].sum()) if orc.height else 0.0
        rows.append(summarise(orc, "oracle", tier, 0.0))
        for d_ms in args.deltas:
            d = d_ms * 1000.0
            prep = lambda o: o.with_columns((pl.col("t_start_us") + int(d)).alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))  # noqa: E731
            trp, tep = prep(tr), prep(te)
            olat = {l: d for l in legs}
            tr_naive = simulate(P.naive(trp, compute_us), books_tr, olat, fees, Q_MAX)
            failed = tr_naive.filter(pl.col("outcome") != "both") if tr_naive.height else tr_naive
            lam = max(0.0, -float(failed["pnl_bps"].mean())) if failed.height else 0.0
            best_th, best_p = 0.0, -np.inf
            for th in THETAS:
                r = simulate(P.threshold(trp, compute_us, th), books_tr, olat, fees, Q_MAX)
                p = float(r["pnl_usd"].sum()) if r.height else 0.0
                if p > best_p:
                    best_th, best_p = th, p
            L = np.full(tep.height, 2 * d + compute_us)
            cands = {
                "naive": P.naive(tep, compute_us),
                "threshold": P.threshold(tep, compute_us, best_th),
                "ev_km": P.ev(tep, km, L, lam, compute_us),
                "ev_aft": P.ev(tep, aft, L, lam, compute_us),
                "ev_wait_aft": refresh_limits(P.ev_wait(tep, aft, L, lam, compute_us), books_te, d, compute_us, tier),
            }
            for name, it in cands.items():
                r = simulate(it, books_te, olat, fees, Q_MAX)
                rows.append(summarise(r, name, tier, d_ms, {"lambda_bps": lam, "theta_star_bps": best_th,
                                                            "capture_ratio": (float(r["pnl_usd"].sum()) / oracle_pnl) if (r.height and oracle_pnl > 0) else None}))
                if name == "naive" and r.height > 50 and d_ms in (0.5, 5.0, 50.0):
                    j = it.join(r, on="opp_id")
                    ev_score = P.ev(j.with_columns(pl.lit(0.0).alias("dummy")), aft, np.full(j.height, 2 * d + compute_us), lam, compute_us)
                    sc = j.select("opp_id", "net0_bps", "pnl_bps").join(ev_score.select("opp_id", pl.col("score").alias("ev_score")), on="opp_id", how="left").fill_null(-1e9)
                    k = max(1, sc.height // 10)
                    ranking.append({"tier": tier, "delta_ms": d_ms, "n": sc.height,
                                    "spearman_net_edge": float(spearmanr(sc["net0_bps"], sc["pnl_bps"]).statistic),
                                    "spearman_ev": float(spearmanr(sc["ev_score"], sc["pnl_bps"]).statistic),
                                    "top_decile_bps_by_edge": float(sc.sort("net0_bps", descending=True).head(k)["pnl_bps"].mean()),
                                    "top_decile_bps_by_ev": float(sc.sort("ev_score", descending=True).head(k)["pnl_bps"].mean())})
    out = {"meta": meta, "latency_tardis_collector": lat.to_dicts(), "decay": decay, "survival": surv,
           "policy_frontier": rows, "ranking": ranking, "runtime_s": time.time() - t_start}
    return out


def to_markdown(res: dict) -> str:
    m = res["meta"]
    L = [f"# Baseline results — train {m['train']} → test {m['test']}", "",
         f"Legs: {', '.join(m['legs'])}. Detection threshold {m['theta_detect_bps']} bps over the fair basis. "
         f"Fees verified: {m['fees_verified']}. Size cap {m['q_max_btc']} BTC.", "", "Assumptions: " + "; ".join(m["assumptions"]) + ".", ""]
    d = res["decay"]
    L += ["## Decay (MVP): episode lifetimes on the exchange clock, test day", "",
          "| group | n | half-life (ms) | t at S=0.9 (ms) | t at S=0.1 (ms) | S(1ms) | S(10ms) | S(100ms) | mean edge0 (bps) |", "|---|---|---|---|---|---|---|---|---|"]
    for key, rows in (("overall", d["overall_test"]), ("instr_group", d["by_instr_group"]), ("ccy_group", d["by_ccy_group"]),
                      ("edge_bucket", d["by_edge_bucket"]), ("pair", d["top_pairs"])):
        for r in rows:
            name = r.get(key, "all") if key != "overall" else "all"
            L.append(f"| {name} | {r['n']} | {r['half_life_ms']:.3g} | {r['t_S90_ms']:.3g} | {r['t_S10_ms']:.3g} | {r['S(1ms)']:.3f} | {r['S(10ms)']:.3f} | {r['S(100ms)']:.3f} | {r['mean_edge0_bps']:.2f} |")
    L += ["", "Edge-magnitude decay E[edge(t0+Δ)/edge(t0)]:", "", "| Δ (ms) | mean | median | share still > 0 |", "|---|---|---|---|"]
    L += [f"| {r['delta_ms']:g} | {r['mean_ratio']:.3f} | {r['median_ratio']:.3f} | {r['share_still_positive']:.3f} |" for r in d["edge_decay"]]
    s = res["survival"]
    L += ["", "## Survival models (train → test)", "", "| model | IBS (log-t, lower better) | C-index |", "|---|---|---|",
          f"| Kaplan–Meier | {s['km']['ibs_logt']:.4f} | {s['km']['c_index']:.3f} |",
          f"| Weibull AFT (covariates) | {s['weibull_aft']['ibs_logt']:.4f} | {s['weibull_aft']['c_index']:.3f} |", "",
          f"Weibull shape ρ = {s['aft_rho']:.3f} (ρ < 1 ⇒ decreasing hazard: young crosses die fastest). "
          f"EV evaluation cost: {s['ev_compute_us_per_opportunity']:.2f} µs per opportunity (numpy, M5).", ""]
    L += ["## Policy frontier (test day, simulated fills)", "", "| tier | δ one-way (ms) | policy | trades | both-fill | PnL (USD) | mean bps | hit | capture |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res["policy_frontier"]:
        cap = "" if r.get("capture_ratio") is None else f"{r['capture_ratio']:.3f}"
        L.append(f"| {r['tier']} | {r['delta_ms']:g} | {r['policy']} | {r['n_trades']} | {r['both_fill_rate']:.3f} | {r['pnl_usd']:.2f} | {r['mean_pnl_bps']:.3f} | {r['hit_rate']:.3f} | {cap} |")
    if res["ranking"]:
        L += ["", "## Ranking quality among all naive trades", "", "| tier | δ (ms) | n | Spearman(edge, PnL) | Spearman(EV, PnL) | top-decile bps by edge | by EV |", "|---|---|---|---|---|---|---|"]
        L += [f"| {r['tier']} | {r['delta_ms']:g} | {r['n']} | {r['spearman_net_edge']:.3f} | {r['spearman_ev']:.3f} | {r['top_decile_bps_by_edge']:.3f} | {r['top_decile_bps_by_ev']:.3f} |" for r in res["ranking"]]
    L += ["", f"Runtime {res['runtime_s']:.0f} s. Commit `{res.get('commit', '?')}`. Command: `{res.get('command', '')}`", ""]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".data/tardis")
    ap.add_argument("--train", default="2026-09-01")
    ap.add_argument("--test", default="2026-10-01")
    ap.add_argument("--split-day", action="store_true")
    ap.add_argument("--legs", default="", help="comma list of file keys like binance_BTCUSDT (default: all present)")
    ap.add_argument("--theta", type=float, default=1.0)
    ap.add_argument("--tiers", default=",".join(TIERS))
    ap.add_argument("--deltas", type=float, nargs="+", default=DELTAS_MS)
    ap.add_argument("--out", default="eval/results/baseline")
    a = ap.parse_args()
    res = run(a)
    res["commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    res["command"] = "python -m eval.run_baseline " + " ".join(os.sys.argv[1:])
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out + ".json", "w") as f:
        json.dump(res, f, indent=1, default=str)
    with open(a.out + ".md", "w") as f:
        f.write(to_markdown(res))
    print(to_markdown(res)[:6000])


if __name__ == "__main__":
    main()
