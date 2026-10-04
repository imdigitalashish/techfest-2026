"""Collect every number the deliverables quote into eval/results/headline.json, read only from committed
result files. The abstract and the architecture page are rendered from it (deliverables/render.py), and
eval/check_docs.py fails if a document drifts from it. Verdict wording follows the pre-registered rule
(eval/PREREGISTRATION-walkforward-12d.md): "supported" only if both 95% lower bounds are > 0.
Usage: .venv/bin/python -m eval.headline
"""
from __future__ import annotations

import json

R = "eval/results/"


def usd(x: float) -> str:
    s = f"{abs(x):,.0f}"
    return ("+" if x >= 0 else "−") + "$" + s


def ci(lo: float, hi: float) -> str:
    return f"[{usd(lo)}, {usd(hi)}]"


def ms(x: float, nd: int = 1) -> str:
    return f"{x:.{nd}f}"


def main() -> None:
    base = json.load(open(R + "baseline_0901_to_1001.json"))
    wf = json.load(open(R + "falsification_walkforward_12d_prereg.json"))
    cs = json.load(open(R + "falsification_clockskew.json"))
    dec = json.load(open(R + "decay_report.json"))
    bud = json.load(open(R + "latency_budget.json"))
    tim = json.load(open(R + "decision_timing.json"))
    live = json.load(open(R + "live_latency.json"))
    h: dict[str, str] = {}

    # ---------------- decay (MVP)
    a = {r["group"]: r for r in dec["part_a"]}
    allp = a["all pairs"]
    h["n_episodes"] = f"{allp['n']:,}"
    h["median_life_ms"] = ms(allp["median_ms"])
    h["median_ci_lo"] = ms(allp["median_ci_hour_block"][0])
    h["median_ci_hi"] = ms(allp["median_ci_hour_block"][1])
    h["S10"] = f"{allp['S(10ms)'][0]:.2f}"
    h["S100"] = f"{allp['S(100ms)'][0]:.2f}"
    for g in ("perp-perp", "spot-perp", "spot-spot"):
        h[f"median_{g.replace('-', '_')}"] = ms(a[f"group: {g}"]["median_ms"], 0)
    pairs = [r for r in dec["part_a"] if " > " in r["group"]]
    pm = sorted(r["median_ms"] for r in pairs)
    h["pair_median_min"], h["pair_median_max"] = ms(pm[0], 0), ms(pm[-1], 0)
    h["n_pairs"] = str(len(pairs))
    months = dec["part_b"]
    mm = [r["median_ms"] for r in months]
    h["month_median_min"], h["month_median_max"] = ms(min(mm), 0), ms(max(mm), 0)
    h["n_months"] = str(len(months))
    # Weibull shape from the baseline (decreasing hazard)
    h["weibull_rho"] = f"{base['survival']['aft_rho']:.2f}"

    # ---------------- ranking under latency (baseline, 1 bp/leg)
    rk = {(r["tier"], r["delta_ms"]): r for r in base["ranking"]}
    h["rho_edge_fast"] = f"{rk[('f1', 0.5)]['spearman_net_edge']:.2f}"
    h["rho_edge_slow"] = f"{rk[('f1', 50.0)]['spearman_net_edge']:.2f}"
    h["rho_lev_slow"] = f"{rk[('f1', 50.0)]['spearman_lev']:.2f}"
    h["top_decile_edge_slow"] = f"{rk[('f1', 50.0)]['top_decile_bps_by_edge']:+.2f}"
    h["top_decile_lev_slow"] = f"{rk[('f1', 50.0)]['top_decile_bps_by_lev']:+.2f}"

    # ---------------- walk-forward (pre-registered)
    c = wf["comparisons"]["lev - threshold_pair"]
    h["wf_n"] = str(c["n_days"])
    h["wf_pos"] = str(c["days_positive"])
    h["wf_mean"] = usd(c["mean_usd_per_day"])
    h["wf_tci"] = ci(*c["t_ci95"])
    h["wf_bci"] = ci(*c["ci95"])
    h["wf_rel"] = f"{c['relative_uplift_of_totals']:+.0%}"
    h["wf_sign_p"] = f"{c['sign_p']:.3f}"
    h["wf_wilcoxon_p"] = f"{c['wilcoxon_p']:.3f}"
    supported = c["t_ci95"][0] > 0 and c["ci95"][0] > 0
    h["wf_verdict"] = ("supported: both 95% lower bounds are above zero" if supported
                       else "not established: the t-interval includes zero, so the gain is within noise")
    u = wf["subsets"]["unseen7"]["lev - threshold_pair"]
    h["unseen_n"], h["unseen_pos"], h["unseen_mean"], h["unseen_tci"] = str(u["n_days"]), str(u["days_positive"]), usd(u["mean_usd_per_day"]), ci(*u["t_ci95"])
    tn = wf["comparisons"]["threshold_pair - naive"]
    h["thr_vs_naive"] = usd(tn["mean_usd_per_day"])
    ev = wf["comparisons"]["ev_kmpair - threshold_pair"]
    h["ev_vs_thr"] = usd(ev["mean_usd_per_day"])
    h["ev_vs_thr_pos"] = str(ev["days_positive"])
    ab = wf["comparisons"]["lev - lev_edge_only"]
    h["ablation_mean"], h["ablation_pos"] = usd(ab["mean_usd_per_day"]), str(ab["days_positive"])
    naive_neg = sum(1 for r in wf["table"] if r["naive"] < 0)
    h["naive_neg_days"] = str(naive_neg)

    # ---------------- clock-skew robustness
    v = cs["variants"]
    h["skew_rho_min"] = f"{min(x['pair_halflife_spearman_vs_exch'] for x in v):.2f}"
    up = [x["uplift_lev_minus_threshold"] for x in v]
    h["skew_uplift_min"], h["skew_uplift_max"] = usd(min(up)), usd(max(up))
    rec = next(x for x in v if x["variant"] == "recv")
    h["recv_ev"], h["recv_thr"] = usd(rec["totals"]["ev_kmpair"]), usd(rec["totals"]["threshold_pair"])

    # ---------------- latency budget and reaction time
    d = tim["decision_in_kernel_ns"]
    h["dec_p50_us"], h["dec_p99_us"] = f"{d['p50']/1e3:.1f}", f"{d['p99']/1e3:.1f}"
    h["det_ns_event"] = f"{tim['detector'][0]['ns_per_event']:.0f}"
    fe = bud["feed_tardis_collector_ms"]
    h["feed_fast_ms"] = f"{fe['binance-futures:BTCUSDT']['p50']:.1f}"
    h["feed_slow_ms"] = f"{max(x['p50'] for x in fe.values()):.0f}"
    be = bud["breakeven_oneway_ms"]["f1"]
    h["be_naive"], h["be_thr"], h["be_lev"] = be["naive"], be["threshold_pair"], be["lev"]
    p05 = [r["feed_p05_us"] / 1e3 for r in live if r["leg"] in ("binance-futures:BTCUSDT", "coinbase:BTC-USD", "kraken:BTC/USD", "deribit:BTC-PERPETUAL")]
    h["mac_p05_min"], h["mac_p05_max"] = f"{min(p05):.0f}", f"{max(p05):.0f}"

    cad = {r["leg"]: r for r in json.load(open(R + "update_cadence.json"))["legs"]}
    h["cad_bnf_ms"] = f"{cad['binance-futures_BTCUSDT']['median_gap_ms']:.0f}"
    h["cad_grid_ms"] = f"{cad['okex_BTC-USDT']['median_gap_ms']:.0f}"
    h["cad_cb_ms"] = f"{cad['coinbase_BTC-USD']['median_gap_ms']:.1f}"
    h["_sources"] = "baseline_0901_to_1001 · falsification_walkforward_12d_prereg · falsification_clockskew · decay_report · latency_budget · decision_timing · live_latency · update_cadence"
    json.dump(h, open(R + "headline.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(h, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
