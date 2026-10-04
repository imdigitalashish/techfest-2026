"""Simulated end-to-end latency budget (stretch goal 1), derived only from committed result files.

L_end_to_end = feed latency (venue → our process) + detector + decision + order latency (our process → venue).
  - feed: measured per venue on the Tardis collector (exchange timestamp → collector receive time), held-out day;
          and from this Mac in India (live recorder, p05 only: medians were inflated by local congestion);
  - detector + decision: measured on the M5 (eval/results/decision_timing.json);
  - order: NOT measurable without exchange accounts → assumed equal to the one-way feed latency (labelled).
The value of a budget comes from the latency–P&L frontier (eval/results/baseline_0901_to_1001.json): for each fee
level and policy, the largest one-way latency at which simulated P&L is still positive (break-even), by linear
interpolation in log-latency between grid points.
Usage: .venv/bin/python -m eval.latency_budget
"""
from __future__ import annotations

import json
import subprocess

import numpy as np

POLICIES = ["naive", "threshold_pair", "ev_kmpair", "lev"]


def breakeven(rows: list[dict], tier: str, policy: str) -> str:
    pts = sorted((r["delta_ms"], r["pnl_usd"]) for r in rows if r["tier"] == tier and r["policy"] == policy)
    if not pts:
        return "n/a"
    if pts[0][1] <= 0:
        return f"< {pts[0][0]:g}"
    for (d0, p0), (d1, p1) in zip(pts, pts[1:]):
        if p1 <= 0 < p0:
            x = np.log(d0) + (np.log(d1) - np.log(d0)) * p0 / (p0 - p1)
            return f"{np.exp(x):.1f}"
    return f"> {pts[-1][0]:g}"


def main() -> None:
    base = json.load(open("eval/results/baseline_0901_to_1001.json"))
    timing = json.load(open("eval/results/decision_timing.json"))
    live = {r["leg"]: r for r in json.load(open("eval/results/live_latency.json"))}
    feed = {r["leg"]: r for r in base["latency_tardis_collector"] if r["day"] == "test"}
    det5 = timing["detector"][0]
    dec = timing["decision_in_kernel_ns"]
    compute_p50_us = det5["ns_per_event"] / 1e3 + dec["p50"] / 1e3
    compute_p99_us = det5["ns_per_event"] / 1e3 + dec["p99"] / 1e3
    rows = base["policy_frontier"]
    out = {"feed_tardis_collector_ms": {k: {"p50": v["feed_p50_us"] / 1e3, "p99": v["feed_p99_us"] / 1e3} for k, v in feed.items()},
           "compute_us": {"detector_amortised": det5["ns_per_event"] / 1e3, "decision_p50": dec["p50"] / 1e3, "decision_p99": dec["p99"] / 1e3,
                          "total_p50": compute_p50_us, "total_p99": compute_p99_us},
           "breakeven_oneway_ms": {t: {p: breakeven(rows, t, p) for p in POLICIES} for t in ("f0", "f1", "f2", "f5")}}
    live_map = {"binance-futures:BTCUSDT": "binance-futures:BTCUSDT", "coinbase:BTC-USD": "coinbase:BTC-USD", "kraken:BTC/USD": "kraken:BTC/USD",
                "deribit:BTC-PERPETUAL": "deribit:BTC-PERPETUAL", "okex:BTC-USDT": "okx:BTC-USDT", "okex-swap:BTC-USDT-SWAP": "okx:BTC-USDT-SWAP",
                "bybit:BTCUSDT": "bybit:BTCUSDT"}
    out["feed_mac_india_p05_ms"] = {k: live[v]["feed_p05_us"] / 1e3 for k, v in live_map.items() if v in live}
    out["commit"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    out["command"] = ".venv/bin/python -m eval.latency_budget"
    json.dump(out, open("eval/results/latency_budget.json", "w"), indent=1)

    L = ["# Simulated end-to-end latency budget", "",
         "L = feed (venue → us) + detector + decision + order (us → venue). Feed latency is measured; compute is measured on the M5; "
         "**order latency is an assumption** (= one-way feed latency) because sending orders needs exchange accounts.", "",
         "## 1. Where the time goes", "",
         "| term | value | source |", "|---|---|---|",
         f"| detector, per market-data event (Numba, amortised, 5 legs) | {det5['ns_per_event']/1e3:.2f} µs | decision_timing.json |",
         f"| decision step: features + LEV + act (Numba, in-kernel) | p50 {dec['p50']/1e3:.2f} µs · p99 {dec['p99']/1e3:.2f} µs | decision_timing.json |",
         f"| **our compute, total** | **p50 {compute_p50_us:.2f} µs · p99 {compute_p99_us:.2f} µs** | sum of the two rows above |", "",
         "| venue (feed one-way) | Tardis collector p50 | p99 | this Mac in India, p05 (floor) |", "|---|---|---|---|"]
    for k in sorted(feed, key=lambda k: feed[k]["feed_p50_us"]):
        mac = out["feed_mac_india_p05_ms"].get(k)
        L.append(f"| {k} | {feed[k]['feed_p50_us']/1e3:.2f} ms | {feed[k]['feed_p99_us']/1e3:.1f} ms | {'' if mac is None else f'{mac:.0f} ms'} |")
    L += ["", "Our compute is 3–4 orders of magnitude below the network terms: the budget is spent on distance, not on the model.", "",
          "## 2. What a budget buys — break-even one-way latency (ms) by fee level", "",
          "Largest one-way latency δ (feed = order = δ, as in the frontier sweep) at which simulated P&L on the held-out day "
          "2026-10-01 (9 legs) is still positive. Grid 0.5–100 ms; log-linear interpolation.", "",
          "| fee per leg | naive | tuned per-pair threshold | EV (KM by pair) | LEV |", "|---|---|---|---|---|"]
    for t, v in out["breakeven_oneway_ms"].items():
        L.append(f"| {t[1:]} bp | " + " | ".join(v[p] for p in POLICIES) + " |")
    L += ["", f"Commit `{out['commit']}` · `{out['command']}`", ""]
    open("eval/results/latency_budget.md", "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
