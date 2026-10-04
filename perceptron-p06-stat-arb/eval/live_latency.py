"""Feed latency from this Mac (India) to each venue, from the live recorder (.data/live).

latency = local receive time − venue timestamp, for venues that stamp their messages.
Caveat: includes the Mac's clock offset vs UTC (logged by the recorder via sntp).
Usage: .venv/bin/python -m eval.live_latency
"""
from __future__ import annotations

import os

import polars as pl

from components.feed.normalize import load_live
from components.latency.model import feed_latency_table

if __name__ == "__main__":
    q = load_live(".data/live")
    t = feed_latency_table(q, "mac-india")
    span_h = (q["ts_recv_us"].max() - q["ts_recv_us"].min()) / 3.6e9
    offs = open(".data/live/_clock/offsets.tsv").read().strip().splitlines() if os.path.exists(".data/live/_clock/offsets.tsv") else []
    lines = ["# Feed latency from the Mac in India (live recorder)", "",
             f"Rows: {q.height:,} quotes over {span_h:.2f} h; venues without a venue timestamp are excluded. "
             "Latency = receive − venue timestamp (ms); includes Mac clock offset (sntp log below).", "",
             "| leg | n | p05 | p50 | p95 | p99 | share < 0 |", "|---|---|---|---|---|---|---|"]
    for r in t.iter_rows(named=True):
        lines.append(f"| {r['leg']} | {r['n']:,} | {r['feed_p05_us']/1e3:.1f} | {r['feed_p50_us']/1e3:.1f} | {r['feed_p95_us']/1e3:.1f} | {r['feed_p99_us']/1e3:.1f} | {r['negative_frac']:.3f} |")
    lines += ["", "sntp offset log (local − reference):", ""] + [f"- `{o}`" for o in offs[-6:]]
    lines += ["", "Command: `.venv/bin/python -m eval.live_latency`", ""]
    os.makedirs("eval/results", exist_ok=True)
    open("eval/results/live_latency.md", "w").write("\n".join(lines))
    t.write_json("eval/results/live_latency.json")
    print("\n".join(lines[:30]))
