"""Feed delay: receive time minus exchange time for every message, per day (provenance for the
"2.9 ms median exchange-to-receive delay" figure; review A17).

    cd perceptron-p04-lob-regimes && python eval/feed_delay.py

Tardis records `timestamp` (exchange event time) and `local_timestamp` (receive time at Tardis's
collector, not on our machine) in microseconds. The difference includes exchange-to-collector network
delay and any clock offset between the two; it is a property of the archived feed, not of our system.
Writes eval/results/feed_delay.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.ingest import available_days, load_book_day  # noqa: E402


def main() -> int:
    rows, allq = [], []
    for d in available_days():
        b = load_book_day(d)
        lat = (b.recv_us - b.exch_us) / 1000.0
        q = np.percentile(lat, [50, 90, 99])
        rows.append((d, len(lat), *q, float(lat.max())))
        allq.append(q[0])
    L = ["# Feed delay (Tardis receive time − Binance exchange time), ms", "",
         "- Command: `python eval/feed_delay.py` · source: Tardis.dev `book_snapshot_5` (`local_timestamp − timestamp`)",
         "- Measured at Tardis's collector, not on our machine; includes network delay and any clock offset.", "",
         f"- Median over days of the daily median: **{np.median(allq):.1f} ms** (range {min(allq):.1f}–{max(allq):.1f} ms, {len(rows)} days).", "",
         "| day | messages | p50 ms | p90 ms | p99 ms | max ms |", "|---|---|---|---|---|---|"]
    L += [f"| {d} | {n} | {a:.1f} | {b_:.1f} | {c:.1f} | {m:.0f} |" for d, n, a, b_, c, m in rows]
    (ROOT / "eval" / "results" / "feed_delay.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
