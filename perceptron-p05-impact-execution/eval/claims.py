"""Claims registry: every number quoted in the deliverables, computed only from eval/results/.

`compute()` returns {claim_id: rendered_string}. Bootstrap CIs use a fresh RandomState(0),
10,000 resamples, seeds sorted. Groups whose source file is missing are skipped; templates
that need them then fail to render (see eval/check_docs.py).
Usage: .venv/bin/python eval/claims.py [--write]   # --write updates eval/results/claims.json
"""
import json, os, sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "eval", "results")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _ci(d, n=10000):
    bm = np.random.RandomState(0).choice(d, size=(n, len(d))).mean(1)
    return float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))


def _paired(df, label, base, metric):
    P = df.pivot(index="seed", columns="label", values=metric).sort_index()
    d = (P[label] - P[base]).values
    return float(d.mean()), *_ci(d), P


def _csv(name):
    return pd.read_csv(os.path.join(R, name))


def _json(name):
    return json.load(open(os.path.join(R, name)))


def g_h1(c):
    df = _csv("E6_confirm_sync.csv")
    m, lo, hi, P = _paired(df, "IA_sched_only", "TWAP", "is_bps")
    c["h1_n"] = f"{df.seed.nunique()}"
    c["h1_gain"], c["h1_gain_lo"], c["h1_gain_hi"] = f"{-m:.3f}", f"{-hi:.3f}", f"{-lo:.3f}"
    c["h1_dis"], c["h1_dis_lo"], c["h1_dis_hi"] = f"{m:+.3f}", f"{lo:+.3f}", f"{hi:+.3f}"
    c["h1_win"] = f"{np.mean((P['IA_sched_only'] - P['TWAP']).values < 0):.0%}"
    om, olo, ohi, O = _paired(df, "IA_sched_only", "TWAP", "own_impact_bps")
    tw, ia = O["TWAP"].mean(), O["IA_sched_only"].mean()
    c["h1_own_twap"], c["h1_own_ia"] = f"{tw:.3f}", f"{ia:.3f}"
    c["h1_own_pct"] = f"{-100 * om / tw:.0f}"
    c["h1_own_lo"], c["h1_own_hi"] = f"{-ohi:.3f}", f"{-olo:.3f}"
    I = df.pivot(index="seed", columns="label", values="instant_bps")
    im, ilo, ihi, _ = _paired(df, "IA_full", "TWAP", "instant_bps")
    c["touch_instant_pct"] = f"{-100 * im / I['TWAP'].mean():.0f}"
    dm, dlo, dhi, _ = _paired(df, "IA_full", "TWAP", "drift_bps")
    c["touch_drift"], c["touch_drift_lo"], c["touch_drift_hi"] = f"{dm:+.3f}", f"{dlo:+.3f}", f"{dhi:+.3f}"
    fm, flo, fhi, _ = _paired(df, "IA_full", "TWAP", "is_bps")
    c["touch_dis"], c["touch_dis_lo"], c["touch_dis_hi"] = f"{fm:+.3f}", f"{flo:+.3f}", f"{fhi:+.3f}"
    c["twap_controllable"] = f"{O['TWAP'].mean() + I['TWAP'].mean():.2f}"
    px = float(df.arrival.mean())                # cents per share (≈ 100,000)
    qty = float(df.qty.iloc[0])
    cents = -m * 1e-4 * px                       # ¢/share saved
    c["h1_cents"], c["h1_usd"] = f"{cents:.2f}", f"{cents * qty / 100:.0f}"
    c["h1_usd_lo"], c["h1_usd_hi"] = f"{-hi * 1e-4 * px * qty / 100:.0f}", f"{-lo * 1e-4 * px * qty / 100:.0f}"
    c["parent_usd_m"] = f"{px * qty / 100 / 1e6:.0f}"
    c["h1_ticks"] = f"{cents:.2f}"                # tick = 1¢
    c["h1_share_of_controllable"] = f"{100 * -m / (O['TWAP'].mean() + I['TWAP'].mean()):.0f}"


def g_ci_tightening(c):
    e3, e5 = _csv("E3_test.csv"), _csv("E5_test_sync.csv")
    r = []
    for l in ["IA_full", "IA_sched_only", "TWAP_touch_limit", "VWAP"]:
        s3 = (e3.pivot(index="seed", columns="label", values="is_bps")[l] - e3.pivot(index="seed", columns="label", values="is_bps")["TWAP"]).std()
        s5 = (e5.pivot(index="seed", columns="label", values="is_bps")[l] - e5.pivot(index="seed", columns="label", values="is_bps")["TWAP"]).std()
        r.append(s3 / s5)
    c["ci_tightening"] = f"{np.median(r):.1f}"
    c["e3_e5_n"] = f"{e5.seed.nunique()}"


def g_noise(c):
    n0, n1 = _csv("E4_nsr_naive.csv"), _csv("E4_nsr_sync.csv")
    a, b = n0.own_impact_bps.std(), n1.own_impact_bps.std()
    c["own_std_naive"], c["own_std_sync"], c["noise_reduction"] = f"{a:.2f}", f"{b:.2f}", f"{a / b:.0f}"
    c["e4_n"] = f"{n1.seed.nunique()}"
    j = _json("nsr_E4_nsr_naive_vs_E4_nsr_sync.json")["exps"]
    nsr = lambda e: j[e]["1200"]["std"] / abs(j[e]["1200"]["mean"])
    c["nsr_naive"], c["nsr_sync"] = f"{nsr('E4_nsr_naive'):.1f}", f"{nsr('E4_nsr_sync'):.1f}"
    e1 = _json("nsr_E1_calib_train.json")["exps"]["E1_calib_train"]
    c["gap_std_60"], c["gap_std_1200"] = f"{e1['60']['std']:.1f}", f"{e1['1200']['std']:.0f}"
    c["gap_mean_300"] = f"{e1['300']['mean']:.1f}"


def g_integrity(c):
    tot = ok = 0
    for f in sorted(os.listdir(R)):
        if f.endswith(".csv") and f.startswith("E") and "pre_window_identical" in open(os.path.join(R, f)).readline():
            d = _csv(f)
            tot += len(d); ok += int(d.pre_window_identical.astype(bool).sum())
    c["twin_runs_total"], c["twin_runs_identical"] = f"{tot:,}", f"{ok:,}"


def g_facts(c):
    f = _json("sim_facts.json")
    c["n_trading_agents"] = f"{f['n_trading_agents']:,}"
    c["abides_commit"] = f["abides_commit"][:7]
    c["tick_bps"] = f"{f['tick_bps']:.1f}"
    c["price_usd"] = f"{f['r_bar_cents'] / 100:,.0f}"
    t = f["task"]
    c["task_qty"], c["task_start"], c["task_end"], c["task_slots"] = f"{t['qty_default']:,}", t["start"][:5], t["end"][:5], f"{t['n_slots']}"


def g_speed(c):
    d = _csv("E8_ablation_val.csv")
    c["wall_median_s"] = f"{d.wall_s.median():.0f}"


def g_e8(c):
    from attribution import analyze
    j = analyze(_csv("E8_ablation_val.csv"), "E8_ablation_val")   # recomputed from the CSV
    k = j["contrasts"]
    fmt = lambda t: (f"{t[0]:+.3f}", f"{t[1]:+.3f}", f"{t[2]:+.3f}")
    c["e8_n"] = f"{j['n_seeds']}"
    c["e8_A"], c["e8_A_lo"], c["e8_A_hi"] = fmt(k["A_qp_main"]["is_bps"])
    c["e8_B"], c["e8_B_lo"], c["e8_B_hi"] = fmt(k["B_frontload_main"]["is_bps"])
    c["e8_D"], c["e8_D_lo"], c["e8_D_hi"] = fmt(k["D_fixed_feedback"]["is_bps"])
    c["e8_A_own"], c["e8_A_own_lo"], c["e8_A_own_hi"] = fmt(k["A_qp_main"]["own_impact_bps"])
    c["e8_B_own"], c["e8_B_own_lo"], c["e8_B_own_hi"] = fmt(k["B_frontload_main"]["own_impact_bps"])
    c["e8_attr_is"], c["e8_attr_own"] = j["attribution_is"], j["attribution_own"]
    for arm in ["QP_only", "IA_sched_only", "IA_sched_fixed", "TWAP_legacy_fb"]:
        t = fmt(j["arms"][arm]["d_is_bps_vs_TWAP"])
        c[f"e8_{arm}"], c[f"e8_{arm}_lo"], c[f"e8_{arm}_hi"] = t


def g_e7(c):
    j = _json("realism_scorecard.json")
    # consistency: point estimate recomputed from the committed CSVs must equal the JSON (review sol #3)
    from realism import load, slope
    data = {q: load(f"E7_size_q{q}") for q in j["qs"]}
    seeds = sorted(set.intersection(*[set(v) for v in data.values()]))
    m = np.array([np.mean([data[q][s_][0] for s_ in seeds]) for q in j["qs"]])
    part = np.array(j["qs"], float) / np.mean([data[j["qs"][0]][s_][2] for s_ in seeds])
    assert abs(slope(np.log(part), np.log(m)) - j["delta"]) < 1e-9, "realism_scorecard.json is stale vs E7 CSVs"
    ph = j["post_hoc"]
    c["e7_delta_resolved"] = f"{ph['delta_resolved']:.2f}"
    c["e7_delta_resolved_lo"], c["e7_delta_resolved_hi"] = f"{ph['delta_resolved_ci95'][0]:.2f}", f"{ph['delta_resolved_ci95'][1]:.2f}"
    c["e7_valid_pct"] = f"{100 * j['boot_valid_frac']:.0f}"
    r = [x for x in ph["doubling_ratios"] if x is not None]
    c["e7_doubling_min"], c["e7_doubling_max"] = f"{min(r):.1f}", f"{max(r):.1f}"
    c["e7_n"] = f"{j['n_seeds']}"
    c["e7_delta"] = "n/a" if j["delta"] is None else f"{j['delta']:.2f}"
    lo, hi = j["delta_ci95"] or (float("nan"), float("nan"))
    c["e7_delta_lo"], c["e7_delta_hi"] = f"{lo:.2f}", f"{hi:.2f}"
    c["e7_verdict"] = j["verdict"]
    c["e7_qmin"], c["e7_qmax"] = f"{j['qs'][0]:,}", f"{j['qs'][-1]:,}"
    c["e7_part_min"], c["e7_part_max"] = f"{100 * j['participation'][0]:.0f}", f"{100 * j['participation'][-1]:.0f}"
    i = j["qs"].index(4000)
    c["e7_decay_4000"] = "n/a" if j["decay_ratio"][i] is None else f"{j['decay_ratio'][i]:.2f}"


def g_e9(c):
    j = _json("calibration_sync.json")
    o, k = j["kernel_oos_second_half"], j["kernel"]
    c["e9_r2_twap"], c["e9_r2_probe"] = f"{o['twap']['r2_mean_path']:.2f}", f"{o['probe']['r2_mean_path']:.2f}"
    c["e9_tau"] = f"{k['tau_s']:.0f}"
    c["e9_r2_seed_twap"], c["e9_r2_seed_probe"] = f"{o['twap']['r2_per_seed']:.3f}", f"{o['probe']['r2_per_seed']:.3f}"
    c["e9_rmse"] = f"{np.mean([o['twap']['rmse_per_seed_cents'], o['probe']['rmse_per_seed_cents']]):.1f}"
    nn = _json("calibration_e1_numeric_split.json")["kernel_oos_second_half"]
    c["e1_rmse"] = f"{np.mean([nn['twap']['rmse_per_seed_cents'], nn['probe']['rmse_per_seed_cents']]):.1f}"
    n = _json("calibration_e1_numeric_split.json")["kernel_oos_second_half"]  # same registered split as E9
    c["e1_r2_twap"], c["e1_r2_probe"] = f"{n['twap']['r2_mean_path']:.1f}", f"{n['probe']['r2_mean_path']:.1f}"
    assert j["fit_seeds"] == list(range(0, 20)) and j["oos_seeds"] == list(range(20, 40)), "E9 must use the registered split"


def g_e10(c):
    df = _csv("E10_replication_test.csv")
    m, lo, hi, P = _paired(df, "IA_sched_only", "TWAP", "is_bps")
    d = (P["IA_sched_only"] - P["TWAP"]).values          # seed-sorted (registered procedure; review sol #4)
    bm = np.random.RandomState(0).choice(d, size=(10000, len(d))).mean(1)
    up = float(np.percentile(bm, 95))
    c["e10_n"] = f"{df.seed.nunique()}"
    c["e10_dis"], c["e10_lo"], c["e10_hi"], c["e10_up95"] = f"{m:+.3f}", f"{lo:+.3f}", f"{hi:+.3f}", f"{up:+.3f}"
    c["e10_h2"] = "confirmed" if up < 0 else "not confirmed"
    from attribution import analyze
    j = analyze(df, "E10_replication_test")                # recomputed from the CSV (review sol #3)
    om, olo, ohi, _ = _paired(df, "IA_sched_only", "TWAP", "own_impact_bps")
    c["e10_own"], c["e10_own_lo"], c["e10_own_hi"] = f"{om:+.3f}", f"{olo:+.3f}", f"{ohi:+.3f}"
    im, ilo, ihi, _ = _paired(df, "IA_sched_only", "TWAP", "instant_bps")
    c["e10_instant"] = f"{im:+.3f}"
    c["e10_A_own"], c["e10_A_own_lo"], c["e10_A_own_hi"] = (f"{x:+.3f}" for x in j["contrasts"]["A_qp_main"]["own_impact_bps"])
    c["e10_B_label"] = j["a1_labels"]["B_frontload_main"]["is_bps"]
    c["e10_A_label"] = j["a1_labels"]["A_qp_main"]["is_bps"]
    c["e10_A_own_label"] = j["a1_labels"]["A_qp_main"]["own_impact_bps"]
    k = j["contrasts"]
    c["e10_attr_is"], c["e10_attr_own"] = j["attribution_is"], j["attribution_own"]
    for key, name in [("A_qp_main", "A"), ("B_frontload_main", "B"), ("D_fixed_feedback", "D")]:
        t = k[key]["is_bps"]
        c[f"e10_{name}"], c[f"e10_{name}_lo"], c[f"e10_{name}_hi"] = f"{t[0]:+.3f}", f"{t[1]:+.3f}", f"{t[2]:+.3f}"
    for arm in ["QP_only", "IA_sched_fixed", "TWAP_legacy_fb"]:
        t = j["arms"][arm]["d_is_bps_vs_TWAP"]
        c[f"e10_{arm}"], c[f"e10_{arm}_lo"], c[f"e10_{arm}_hi"] = f"{t[0]:+.3f}", f"{t[1]:+.3f}", f"{t[2]:+.3f}"
    # pooled over all synced test seeds (E5 u E6 u E10): descriptive, not pre-registered
    pool = []
    for f in ["E5_test_sync.csv", "E6_confirm_sync.csv", "E10_replication_test.csv"]:
        x = _csv(f)
        Q = x.pivot(index="seed", columns="label", values="is_bps")
        pool.append((Q["IA_sched_only"] - Q["TWAP"]).rename(f))
    p2 = pd.concat(pool[1:]).sort_index()        # E6 u E10 (A1 item 5): no discovery data
    assert p2.index.is_unique
    m2, l2, h2 = float(p2.mean()), *_ci(p2.values)
    c["pool2_n"], c["pool2_dis"], c["pool2_lo"], c["pool2_hi"] = f"{len(p2)}", f"{m2:+.3f}", f"{l2:+.3f}", f"{h2:+.3f}"
    c["pool2_cents"] = f"{-m2 * 10:.2f}"          # bps -> ¢/share at $1,000 (1 bp = 10¢)
    pd_ = pd.concat(pool).sort_index()
    assert pd_.index.is_unique, "pooled seeds must be disjoint"
    pm, plo, phi = float(pd_.mean()), *_ci(pd_.values)
    c["pool_n"], c["pool_dis"], c["pool_lo"], c["pool_hi"] = f"{len(pd_)}", f"{pm:+.3f}", f"{plo:+.3f}", f"{phi:+.3f}"
    # feedback attribution: who ends up holding our shares (TWAP arm, end-of-day position vs null twin)
    tw = df[df.label == "TWAP"].sort_values("seed")
    q = float(tw.qty.iloc[0])
    for col, name in [("dpos_ValueAgent", "value"), ("dpos_MomentumAgent", "momentum"),
                      ("dpos_AdaptiveMarketMakerAgent", "mm"), ("dpos_NoiseAgent", "noise")]:
        v = tw[col].values.astype(float)
        vlo, vhi = _ci(v)
        c[f"fb_{name}"], c[f"fb_{name}_lo"], c[f"fb_{name}_hi"] = f"{v.mean():+,.0f}", f"{vlo:+,.0f}", f"{vhi:+,.0f}"
        c[f"fb_{name}_pct"] = f"{100 * v.mean() / q:.0f}"
        c[f"fb_{name}_abs"] = f"{abs(v.mean()):,.0f}"


def g_reviews(c):
    import re as _re
    rows = open(os.path.join(ROOT, "reviews", "ledger.tsv")).read().splitlines()[1:]
    for r in rows:
        f = r.split("\t")
        m = _re.search(r"Weighted rubric (\d\.\d\d)/5", f[7])
        if f[2] == "gpt-6-astra" and m:
            key = "astra_final" if "final" in f[1].lower() else "astra_draft"
            c[key] = m.group(1)
    c["reviews_issues"] = f"{sum(int(r.split(chr(9))[4]) for r in rows)}"
    c["reviews_accepted"] = f"{sum(int(r.split(chr(9))[5]) for r in rows)}"


def g_e11(c):
    from market_laws import summarize
    d = _csv("E11_market_laws.csv")
    j, _ = summarize(d, int(d.seed.min()), int(d.seed.max()) + 1)   # recomputed from the CSV
    c["e11_n"] = f"{j['n_per_engine']}"
    lab = [v["label"] for k, v in j.items() if isinstance(v, dict)]
    c["e11_preserved"], c["e11_total"] = f"{sum(x.startswith('preserved') for x in lab)}", f"{len(lab)}"
    c["e11_differs"] = f"{sum(x == 'differs' for x in lab)}"
    c["e11_spread_pct"] = f"{100 * (j['spread_cents']['value'] - 1):.0f}"
    for k in ("volume", "spread_cents", "ret_std_1m_bps", "touch_depth", "n_trades"):
        c[f"e11_{k}_ratio"] = f"{j[k]['value']:.2f}"
        c[f"e11_{k}_lo"], c[f"e11_{k}_hi"] = f"{j[k]['ci95'][0]:.2f}", f"{j[k]['ci95'][1]:.2f}"
        c[f"e11_{k}_label"] = j[k]["label"]


def g_e12(c):
    df = _csv("E12_filltime_test.csv")
    c["e12_n"] = f"{df.seed.nunique()}"
    c["e12_arms"] = f"{df.label.nunique()}"
    c["e12_exact"], c["e12_rows"] = f"{int(df.pre_window_exact.astype(bool).sum())}", f"{len(df)}"
    for arm, key in [("IA_full", "ia"), ("TWAP_touch_limit", "tl")]:
        for m in ("delay_bps", "at_fill_bps", "instant_bps"):
            mm, lo, hi, _ = _paired(df, arm, "TWAP", m)
            c[f"e12_{key}_{m[:-4]}"], c[f"e12_{key}_{m[:-4]}_lo"], c[f"e12_{key}_{m[:-4]}_hi"] = f"{mm:+.3f}", f"{lo:+.3f}", f"{hi:+.3f}"
    for m_, key in [("is_bps", "is"), ("drift_bps", "drift"), ("own_impact_bps", "own"), ("delay_bps", "delay")]:
        mm, lo, hi, _ = _paired(df, "TWAP_touch_limit", "TWAP", m_)
        c[f"e12_tl_{key}_d"], c[f"e12_tl_{key}_d_lo"], c[f"e12_tl_{key}_d_hi"] = f"{mm:+.3f}", f"{lo:+.3f}", f"{hi:+.3f}"
    am, alo, ahi, _ = _paired(df, "TWAP_touch_limit", "TWAP", "at_fill_bps")
    c["e12_tl_at_fill_abs"], c["e12_tl_at_fill_abs_lo"], c["e12_tl_at_fill_abs_hi"] = f"{-am:.3f}", f"{-ahi:.3f}", f"{-alo:.3f}"
    res = (df.instant_bps - df.delay_bps - df.at_fill_bps).abs().max()
    c["e12_identity_resid"] = f"{res:.1e}"


GROUPS = [g_h1, g_ci_tightening, g_noise, g_integrity, g_facts, g_speed, g_e8, g_e7, g_e9, g_e10, g_reviews, g_e11, g_e12]


def compute(strict=False):
    c, missing = {}, []
    for g in GROUPS:
        try:
            g(c)
        except FileNotFoundError as e:
            missing.append(f"{g.__name__}: {os.path.basename(e.filename)}")
            if strict:
                raise
    return c, missing


if __name__ == "__main__":
    c, missing = compute()
    for k in sorted(c):
        print(f"{k} = {c[k]}")
    if missing:
        print("MISSING SOURCES:", "; ".join(missing))
    if "--write" in sys.argv:
        json.dump(c, open(os.path.join(R, "claims.json"), "w"), indent=1, sort_keys=True)
        print("wrote eval/results/claims.json")
