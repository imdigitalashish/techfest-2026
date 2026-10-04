"""Pre-registered E11: does per-wakeup RNG synchronisation preserve the null market's statistics?

Null worlds only (no orders), native vs synced, the same seed list (independent samples).
Statistics over 09:35–09:55: 1-min return std (bps), lag-1 autocorrelation of 10-s returns,
mean spread (¢), mean touch depth (shares), volume (shares), number of trades.
Usage: nice -n 10 .venv/bin/python eval/market_laws.py --seeds 100:160 --workers 4
"""
import argparse, json, multiprocessing as mp, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for c in ("sim_env", "execution_agent"):
    sys.path.insert(0, os.path.join(ROOT, "components", c))
STATS = ["ret_std_1m_bps", "ac1_10s", "spread_cents", "touch_depth", "volume", "n_trades"]


def stats_for(job):
    seed, mode = job
    import sim_env  # noqa: F401
    from sim_env.twins import run_null
    from sim_env.world import ns_at
    w = run_null(seed, "SELL", "09:35:00", "09:55:00", 40, "10:05:00", rng_sync=mode)
    t0, t1 = ns_at("09:35:00"), ns_at("09:55:00")
    g60 = np.arange(t0, t1 + 1, 60_000_000_000)
    g10 = np.arange(t0, t1 + 1, 10_000_000_000)
    m60, m10 = w.mid_at(g60), w.mid_at(g10)
    r60 = np.diff(np.log(m60)) * 1e4
    r10 = np.diff(np.log(m10))
    r10 = r10[~np.isnan(r10)]
    ac1 = float(np.corrcoef(r10[:-1], r10[1:])[0, 1]) if len(r10) > 3 and r10.std() > 0 else np.nan
    sel = (w.t >= t0) & (w.t <= t1) & ~np.isnan(w.bid) & ~np.isnan(w.ask)
    tsel = (w.tx_t >= t0) & (w.tx_t <= t1)
    return dict(seed=seed, mode=mode, ret_std_1m_bps=float(np.nanstd(r60, ddof=1)), ac1_10s=ac1,
                spread_cents=float(np.mean(w.ask[sel] - w.bid[sel])),
                touch_depth=float(np.mean((w.bid_q[sel] + w.ask_q[sel]) / 2)),
                volume=float(w.tx_q[tsel].sum()), n_trades=int(tsel.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="100:160"); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split(":"))
    jobs = [(s, m) for s in range(lo, hi) for m in ("naive", "per_wakeup")]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        rows = list(pool.imap_unordered(stats_for, jobs))
    import pandas as pd
    df = pd.DataFrame(rows).sort_values(["mode", "seed"])
    df.to_csv(os.path.join(ROOT, "eval", "results", "E11_market_laws.csv"), index=False, float_format="%.6g")
    out, L = summarize(df, lo, hi)
    json.dump(out, open(os.path.join(ROOT, "eval", "results", "E11_market_laws.json"), "w"), indent=1)
    open(os.path.join(ROOT, "eval", "results", "E11_market_laws.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def summarize(df, lo, hi):
    """Pure function of the committed E11 CSV (used by eval/claims.py; review sol #3)."""
    df = df.sort_values(["mode", "seed"])
    rs = np.random.RandomState(0)
    out, L = {}, ["# E11: market statistics, native vs synchronised null worlds (pre-registered)", "",
                  f"Seeds {lo}–{hi - 1}, n = {hi - lo} worlds per engine (independent samples); 09:35–09:55. "
                  "Ratio = synced mean / native mean (autocorrelation: difference), 95% CI from independent bootstrap of seeds (10k).", "",
                  "| statistic | native mean | synced mean | ratio or diff | 95% CI | label |", "|---|---|---|---|---|---|"]
    for st in STATS:
        x = df[df["mode"] == "naive"][st].dropna().values
        y = df[df["mode"] == "per_wakeup"][st].dropna().values
        bx = x[rs.randint(0, len(x), (10000, len(x)))].mean(1)
        by = y[rs.randint(0, len(y), (10000, len(y)))].mean(1)
        if st == "ac1_10s":
            v, b = y.mean() - x.mean(), by - bx
            lo_, hi_ = np.percentile(b, [2.5, 97.5])
            lab = "preserved (±0.05)" if (lo_ >= -0.05 and hi_ <= 0.05) else ("differs" if (lo_ > 0 or hi_ < 0) else "unresolved")
        else:
            v, b = y.mean() / x.mean(), by / bx
            lo_, hi_ = np.percentile(b, [2.5, 97.5])
            lab = "preserved (±10%)" if (lo_ >= 0.9 and hi_ <= 1.1) else ("differs" if (lo_ > 1 or hi_ < 1) else "unresolved")
        out[st] = dict(native=float(x.mean()), synced=float(y.mean()), value=float(v), ci95=[float(lo_), float(hi_)], label=lab)
        L.append(f"| {st} | {x.mean():.4g} | {y.mean():.4g} | {v:.3f} | [{lo_:.3f}, {hi_:.3f}] | {lab} |")
    out["n_per_engine"] = hi - lo
    return out, L


if __name__ == "__main__":
    main()
