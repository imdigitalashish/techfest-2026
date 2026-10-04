"""Publication cadence of our own live recorder's channels vs the Tardis samples (eval/results/update_cadence.md).

Only legs with venue timestamps are reported (Binance spot bookTicker carries none, so its receive-time gaps mostly
reflect network batching and are excluded). Data: the ~3 h live recording of 2026-10-04 in .data/live.
Usage: .venv/bin/python -m eval.live_cadence
"""
from __future__ import annotations

import json
import os
import subprocess

import numpy as np
import polars as pl

from components.feed.normalize import load_live


def main() -> None:
    q = load_live(".data/live", venues=["okx", "binance-futures", "bybit", "deribit", "coinbase", "kraken"])
    q = q.with_columns((pl.col("venue") + ":" + pl.col("instrument")).alias("leg")).filter(~pl.col("exch_ts_imputed"))
    rows = []
    for (leg,), g in q.group_by(["leg"]):
        t = np.unique(g["ts_exch_us"].to_numpy())
        d = np.diff(t)
        d = d[d > 0]
        if d.size < 100:
            continue
        rows.append({"leg": leg, "rows": g.height, "median_gap_ms": float(np.median(d) / 1e3), "p10_gap_ms": float(np.quantile(d, 0.1) / 1e3),
                     "share_below_10ms": float(np.mean(d < 10_000))})
    rows.sort(key=lambda r: r["leg"])
    out = {"legs": rows, "span_h": float((q["ts_recv_us"].max() - q["ts_recv_us"].min()) / 3.6e9),
           "commit": os.environ.get("P6_COMMIT") or subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "command": ".venv/bin/python -m eval.live_cadence"}
    json.dump(out, open("eval/results/live_cadence.json", "w"), indent=1)
    L = ["# Publication cadence of our live recorder's channels (venue timestamps)", "",
         f"Live recording of 2026-10-04, {out['span_h']:.1f} h. Compare with the Tardis `quotes` samples in `update_cadence.md`.", "",
         "| leg (our channel) | rows | median gap (ms) | p10 gap (ms) | share < 10 ms |", "|---|---|---|---|---|"]
    L += [f"| {r['leg']} | {r['rows']:,} | {r['median_gap_ms']:.1f} | {r['p10_gap_ms']:.1f} | {r['share_below_10ms']:.3f} |" for r in rows]
    L += ["", f"Commit `{out['commit']}` · `{out['command']}`", ""]
    open("eval/results/live_cadence.md", "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
