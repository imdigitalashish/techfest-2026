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
from components.decay.survival import KMByPair, add_features, evaluate, fit_km, fit_weibull_aft, km_summary
from components.decision.lev import LEV, LEV_FEATURES, add_lev_columns
from threadpoolctl import threadpool_limits
from components.decision import policies as P
from components.detector.cross import detect
from components.feed.normalize import load_tardis_day
from components.latency.model import feed_latency_table
from components.sim.fills import truth_books, simulate

USD = ("coinbase", "kraken", "bitstamp", "deribit")
DELTAS_MS = [0.5, 1, 2, 5, 10, 20, 50, 100]
THETAS = [0.0, 0.5, 1, 2, 3, 5, 10]
LEV_DELTAS_MS = [0.5, 2, 5, 10, 20, 50]
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
    opp_tr, opp_te = add_lev_columns(opp_tr, legs), add_lev_columns(opp_te, legs)
    kmp = KMByPair(opp_tr)
    surv["km_pair"] = evaluate(kmp, opp_te)
    prep = lambda o, d: o.with_columns((pl.col("t_start_us") + int(d)).alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))  # noqa: E731
    rows, ranking, lev_info = [], [], {}
    for tier in args.tiers.split(","):
        fees = {l: taker_bps(leg_venue(l), tier) for l in legs}
        tr, te = P.with_net(opp_tr, tier), P.with_net(opp_te, tier)
        o0 = prep(te, 0)
        orc = simulate(P.naive(o0, 0.0), books_te, {l: 0.0 for l in legs}, fees, Q_MAX)
        oracle_pnl = float(orc["pnl_usd"].sum()) if orc.height else 0.0
        rows.append(summarise(orc, "oracle", tier, 0.0))
        # LEV training labels: execute every near-profitable train candidate at each latency in a grid
        lev_parts = []
        for d_ms in LEV_DELTAS_MS:
            d = d_ms * 1000.0
            cand = prep(tr, d).filter(pl.col("net0_bps") > -2.0)
            if cand.height == 0:
                continue
            it = P.intents(cand, np.ones(cand.height, bool), cand["t_obs_us"].to_numpy() + compute_us, cand["net0_bps"].to_numpy(), "all")
            r = simulate(it, books_tr, {l: d for l in legs}, fees, Q_MAX)
            lev_parts.append(it.join(r.select("opp_id", "pnl_bps"), on="opp_id").with_columns(
                pl.lit(float(np.log((2 * d + compute_us) / 1000.0))).alias("log_L_ms")))
        levm = None
        if lev_parts:
            lev_df = pl.concat(lev_parts)
            if lev_df.height > 600_000:
                lev_df = lev_df.sample(600_000, seed=0)
            levm = LEV().fit(lev_df)
            x1 = prep(te, 0).head(1).with_columns(pl.lit(0.0).alias("log_L_ms")).select(LEV_FEATURES).to_numpy()
            with threadpool_limits(1):
                levm.m.predict(x1)
                t0 = time.perf_counter()
                for _ in range(200):
                    levm.m.predict(x1)
            lev_info[tier] = {"train_rows": lev_df.height, "predict_us_single": (time.perf_counter() - t0) / 200 * 1e6}
        lev_compute_us = float(np.ceil(lev_info.get(tier, {}).get("predict_us_single", compute_us)))
        for d_ms in args.deltas:
            d = d_ms * 1000.0
            trp, tep = prep(tr, d), prep(te, d)
            olat = {l: d for l in legs}
            it_tr = P.naive(trp, compute_us)
            res_tr = simulate(it_tr, books_tr, olat, fees, Q_MAX)
            j = it_tr.select("opp_id", "net0_bps", "pair_id").join(res_tr.select("opp_id", "pnl_usd", "pnl_bps", "outcome"), on="opp_id") if it_tr.height else None
            lam, best_th, theta_pair = 0.0, 0.0, {}
            if j is not None and j.height:
                failed = j.filter(pl.col("outcome") != "both")
                lam = max(0.0, -float(failed["pnl_bps"].mean())) if failed.height else 0.0
                best_th = max(THETAS, key=lambda th: float(j.filter(pl.col("net0_bps") > th)["pnl_usd"].sum()))
                for (pid,), g in j.group_by(["pair_id"]):
                    best = (np.inf, 0.0)
                    for th in THETAS:
                        p = float(g.filter(pl.col("net0_bps") > th)["pnl_usd"].sum())
                        if p > best[1]:
                            best = (th, p)
                    theta_pair[float(pid)] = best[0]
            L = 2 * d + compute_us
            Larr = np.full(tep.height, L)
            cands = {
                "naive": P.naive(tep, compute_us),
                "threshold": P.threshold(tep, compute_us, best_th),
                "threshold_pair": P.threshold_pair(tep, compute_us, theta_pair),
                "ev_km": P.ev(tep, km, Larr, lam, compute_us, "ev_km"),
                "ev_kmpair": P.ev(tep, kmp, Larr, lam, compute_us, "ev_kmpair"),
                "ev_wait_kmpair": refresh_limits(P.ev_wait(tep, kmp, Larr, lam, compute_us, "ev_wait_kmpair"), books_te, d, compute_us, tier),
            }
            if levm is not None:
                cands["lev"] = P.lev(tep, levm, 2 * d + lev_compute_us, lev_compute_us)
            for name, it in cands.items():
                r = simulate(it, books_te, olat, fees, Q_MAX)
                rows.append(summarise(r, name, tier, d_ms, {"lambda_bps": lam, "theta_star_bps": best_th,
                                                            "capture_ratio": (float(r["pnl_usd"].sum()) / oracle_pnl) if (r.height and oracle_pnl > 0) else None}))
                if name == "naive" and r.height > 50 and d_ms in (0.5, 5.0, 50.0):
                    jj = it.join(r.select("opp_id", "pnl_bps"), on="opp_id")
                    s = P._s_at(kmp, jj["pair_id"].to_numpy(), np.full(jj.height, L / 1000.0))
                    ev_score = s * jj["net0_bps"].to_numpy() - (1 - s) * lam
                    lev_score = levm.predict(jj, 2 * d + lev_compute_us) if levm is not None else ev_score
                    pnl = jj["pnl_bps"].to_numpy(); k = max(1, jj.height // 10)
                    top = lambda sc: float(pnl[np.argsort(-sc)[:k]].mean())  # noqa: E731
                    ranking.append({"tier": tier, "delta_ms": d_ms, "n": jj.height,
                                    "spearman_net_edge": float(spearmanr(jj["net0_bps"], pnl).statistic),
                                    "spearman_ev_kmpair": float(spearmanr(ev_score, pnl).statistic),
                                    "spearman_lev": float(spearmanr(lev_score, pnl).statistic),
                                    "top_decile_bps_by_edge": top(jj["net0_bps"].to_numpy()),
                                    "top_decile_bps_by_ev": top(ev_score), "top_decile_bps_by_lev": top(lev_score)})
    surv["lev"] = lev_info
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
          f"| Weibull AFT (covariates) | {s['weibull_aft']['ibs_logt']:.4f} | {s['weibull_aft']['c_index']:.3f} |",
          f"| Kaplan–Meier by venue pair | {s['km_pair']['ibs_logt']:.4f} | {s['km_pair']['c_index']:.3f} |", "",
          f"LEV model: {json.dumps(s.get('lev', {}))}", "",
          f"Weibull shape ρ = {s['aft_rho']:.3f} (ρ < 1 ⇒ decreasing hazard: young crosses die fastest). "
          f"EV evaluation cost: {s['ev_compute_us_per_opportunity']:.2f} µs per opportunity (numpy, M5).", ""]
    L += ["## Policy frontier (test day, simulated fills)", "", "| tier | δ one-way (ms) | policy | trades | both-fill | PnL (USD) | mean bps | hit | capture |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res["policy_frontier"]:
        cap = "" if r.get("capture_ratio") is None else f"{r['capture_ratio']:.3f}"
        L.append(f"| {r['tier']} | {r['delta_ms']:g} | {r['policy']} | {r['n_trades']} | {r['both_fill_rate']:.3f} | {r['pnl_usd']:.2f} | {r['mean_pnl_bps']:.3f} | {r['hit_rate']:.3f} | {cap} |")
    if res["ranking"]:
        L += ["", "## Ranking quality among all naive trades (test day)", "", "| tier | δ (ms) | n | Spearman edge | Spearman EV(KM-pair) | Spearman LEV | top-decile bps: edge | EV | LEV |", "|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {r['tier']} | {r['delta_ms']:g} | {r['n']} | {r['spearman_net_edge']:.3f} | {r['spearman_ev_kmpair']:.3f} | {r['spearman_lev']:.3f} | {r['top_decile_bps_by_edge']:.3f} | {r['top_decile_bps_by_ev']:.3f} | {r['top_decile_bps_by_lev']:.3f} |" for r in res["ranking"]]
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
