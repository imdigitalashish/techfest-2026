"""Update cadence of each venue's quotes in the Tardis samples: the time resolution at which decay can be measured.

For each leg: rows, median / p10 gap between consecutive distinct exchange timestamps, the share of gaps within
2 ms of a multiple of 100 ms (a 100 ms publication grid), and the share of gaps below 10 ms.
Usage: .venv/bin/python -m eval.update_cadence --date 2026-10-01
"""
from __future__ import annotations

import argparse
import json
import subprocess

import numpy as np
import polars as pl

LEGS9 = "binance_BTCUSDT,binance-futures_BTCUSDT,coinbase_BTC-USD,okex_BTC-USDT,okex-swap_BTC-USDT-SWAP,bybit_BTCUSDT,kraken_BTC-USD,bitstamp_BTCUSD,deribit_BTC-PERPETUAL".split(",")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-10-01")
    a = ap.parse_args()
    rows = []
    for f in LEGS9:
        t = pl.read_csv(f".data/tardis/quotes/{a.date}/{f}.csv.gz", columns=["timestamp"],
                        schema_overrides={"timestamp": pl.Int64})["timestamp"].to_numpy()
        d = np.diff(t)
        d = d[d > 0]
        r = d % 100_000
        rows.append({"leg": f, "rows": int(t.size), "median_gap_ms": float(np.median(d) / 1e3), "p10_gap_ms": float(np.quantile(d, 0.1) / 1e3),
                     "min_gap_ms": float(d.min() / 1e3), "share_100ms_grid": float(np.mean((r < 2_000) | (r > 98_000))),
                     "share_below_10ms": float(np.mean(d < 10_000))})
    out = {"date": a.date, "legs": rows,
           "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "command": f".venv/bin/python -m eval.update_cadence --date {a.date}"}
    json.dump(out, open("eval/results/update_cadence.json", "w"), indent=1)
    L = [f"# Quote update cadence in the Tardis samples ({a.date})", "",
         "Gaps between consecutive distinct exchange timestamps. A venue on a 100 ms grid cannot show a mispricing closing faster "
         "than its next publication, so millisecond lifetimes are measured at this resolution.", "",
         "| leg | rows | median gap (ms) | p10 gap (ms) | min gap (ms) | share on 100 ms grid | share < 10 ms |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['leg']} | {r['rows']:,} | {r['median_gap_ms']:.1f} | {r['p10_gap_ms']:.1f} | {r['min_gap_ms']:.2f} | {r['share_100ms_grid']:.3f} | {r['share_below_10ms']:.3f} |")
    L += ["", f"Commit `{out['commit']}` · `{out['command']}`", ""]
    open("eval/results/update_cadence.md", "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
