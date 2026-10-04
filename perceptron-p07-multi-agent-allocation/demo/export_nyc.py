"""Export the NYC TLC replay trace used by the demo's July 4th tab (run once; needs the gitignored .data/).

The output is the INPUT of the committed nyc-v2 run for thinning replicate seed 200: the thinned per-minute
request counts and destinations (real trips) plus what policies are allowed to know (the OD map, time-of-day
profile and historical shares learned from the training days). It is produced by the committed
components/scenarios/nyc_tlc.py and verified against the committed row eval/results/nyc-v2/episodes.csv.

    .venv/bin/python -m demo.export_nyc            # writes demo/data/nyc_jul03-04_r200.npz, then checks parity
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter

import numpy as np
import pandas as pd

from components.scenarios.nyc_tlc import MAPPING_CSV, PARQUET, build_nyc_trace, data_summary
from demo.engine import NYC_EXPORT, P7, BatchRun
from eval.harness import NYC

SEED = 200
SCENARIO = "nyc-jul03-04"


def cell_labels(train_days: list[str]) -> dict:
    """Per grid cell, its taxi zones ranked by Manhattan-internal pickups on the training days (labels for the UI)."""
    import pyarrow.parquet as pq
    m = pd.read_csv(MAPPING_CSV)
    cell, name = dict(zip(m.zone_id, m.cell)), dict(zip(m.zone_id, m.zone_name))
    df = pq.read_table(PARQUET, columns=["tpep_pickup_datetime", "PULocationID", "DOLocationID"]).to_pandas()
    day = pd.to_datetime(df["tpep_pickup_datetime"]).dt.strftime("%Y-%m-%d")
    keep = day.isin(train_days) & df["PULocationID"].isin(cell) & df["DOLocationID"].isin(cell)
    n = Counter(df.loc[keep, "PULocationID"].astype(int))
    out: dict = {}
    for z in sorted(cell, key=lambda z: -n[z]):
        out.setdefault(str(int(cell[z])), []).append([name[z], int(n[z])])
    return out


def main() -> None:
    test_days, train_days, event = NYC[SCENARIO]
    trace, meta = build_nyc_trace(test_days, train_days, seed=SEED)
    summ = data_summary(test_days)
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=P7, capture_output=True, text=True).stdout.strip()
    info = dict(scenario=SCENARIO, seed=SEED, test_days=test_days, train_days=train_days, event_window=list(event),
                q=summ["q"], kept_fraction=summ["kept_fraction"], mean_unthinned_rate=summ["mean_unthinned_rate"],
                requests=int(trace.counts.sum()), source="components/scenarios/nyc_tlc.py build_nyc_trace",
                cell_zones_by_train_pickups=cell_labels(train_days),
                data="NYC TLC yellow_tripdata_2025-07.parquet (Manhattan-internal trips), exported at commit " + head)
    NYC_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(NYC_EXPORT, counts=trace.counts.astype(np.int16), req_dest=trace.req_dest.astype(np.int8),
                        od_prob=meta["od_prob"], profile=meta["profile"], hist_shares=meta["hist_shares"],
                        init_level=meta["init_level"], init_level_raw=meta["init_level_raw"], info=json.dumps(info))
    print(f"wrote {NYC_EXPORT.relative_to(P7)} ({NYC_EXPORT.stat().st_size / 1024:.0f} KB, {info['requests']} requests)")
    b = BatchRun("nyc", seed=SEED)
    b.run()
    if b.error:
        raise SystemExit(b.error)
    for name, par in b.summary["parity"].items():
        print(name, b.summary["metrics"][name]["served_frac"], b.summary["metrics"][name]["event_lost"], par)
    if not b.summary["parity_all"]:
        raise SystemExit("PARITY FAILED: the export does not reproduce eval/results/nyc-v2/episodes.csv")
    print("parity with eval/results/nyc-v2/episodes.csv (seed 200): OK")


if __name__ == "__main__":
    main()
