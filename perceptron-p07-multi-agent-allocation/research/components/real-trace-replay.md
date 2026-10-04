# NYC TLC real-trace replay

Access date: 2026-10-04.

The live TLC page at `https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page` returned HTTP 403 to `web_fetch`, so the Wayback snapshot
`https://web.archive.org/web/20261003112013/https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page`
was used to confirm the official download links:

- Yellow Taxi Trip Records, July 2025: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-07.parquet`
- Taxi Zone Lookup Table: `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv`
- Taxi Zone Shapefile: `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip`

## Month and filtering

Month used: July 2025. July 2025 was available in the TLC page snapshot and includes July 4, a plausible demand-shock date. Any link to fireworks or other specific causes is **UNVERIFIED**.

Trips are kept only when both pickup and dropoff taxi zones are Manhattan zones from the lookup CSV, excluding unknown IDs 264/265. Kept fraction for the full month: `0.7817922355`.

For the two-day replay `test_days=["2025-07-03", "2025-07-04"]`, the un-thinned Manhattan pickup rate is `49.678125` requests/minute. The thinning probability for `target_rate=10.0` is:

```text
q = 0.2012958420
```

For the one-day smoke trace `test_days=["2025-07-04"]`, `q = 0.2327084680`.

## Zone-to-grid mapping

Mapping file: `components/scenarios/nyc_zone_to_cell.csv`.

Method:

1. Read Manhattan taxi zones from the lookup CSV.
2. Read taxi-zone polygons from `taxi_zones.zip` with `pyshp`.
3. Compute area-weighted polygon centroids.
4. Fit PCA on Manhattan centroids.
5. Rotate coordinates so the principal axis is the long Manhattan axis.
6. Cut the long and cross axes into 5 equal-width bins; cell ID is `row * 5 + col`.

Cell occupancy:

| cell | zones |
|---:|---:|
| 0 | 2 |
| 1 | 4 |
| 2 | 5 |
| 3 | 1 |
| 4 | 0 |
| 5 | 3 |
| 6 | 8 |
| 7 | 9 |
| 8 | 6 |
| 9 | 0 |
| 10 | 3 |
| 11 | 4 |
| 12 | 3 |
| 13 | 6 |
| 14 | 1 |
| 15 | 0 |
| 16 | 4 |
| 17 | 2 |
| 18 | 1 |
| 19 | 1 |
| 20 | 0 |
| 21 | 5 |
| 22 | 1 |
| 23 | 0 |
| 24 | 0 |

## Top July 4 surges

`find_surges("2025-07-04", train_days=["2025-07-01", "2025-07-02"])` ranks un-thinned 30-minute cell counts against the train-day same-time mean. These are demand anomalies only; causes are not claimed.

| rank | cell | window | count | train mean | ratio |
|---:|---:|---|---:|---:|---:|
| 1 | 3 | 2025-07-04 22:00–22:30 | 62 | 3.0 | 20.67 |
| 2 | 5 | 2025-07-04 03:30–04:00 | 90 | 9.5 | 9.47 |
| 3 | 8 | 2025-07-04 03:30–04:00 | 106 | 12.0 | 8.83 |
| 4 | 5 | 2025-07-04 04:00–04:30 | 53 | 6.0 | 8.83 |
| 5 | 21 | 2025-07-04 23:30–2025-07-05 00:00 | 29 | 3.5 | 8.29 |
| 6 | 3 | 2025-07-04 23:00–23:30 | 30 | 4.0 | 7.50 |
| 7 | 5 | 2025-07-04 04:30–05:00 | 22 | 3.0 | 7.33 |
| 8 | 8 | 2025-07-04 02:30–03:00 | 143 | 21.0 | 6.81 |
| 9 | 8 | 2025-07-04 02:00–02:30 | 173 | 25.5 | 6.78 |
| 10 | 8 | 2025-07-04 01:30–02:00 | 195 | 29.5 | 6.61 |

## Limitations

- The replay is Manhattan-only and drops all trips with non-Manhattan pickup or dropoff zones.
- Trips are independently thinned to match the simulator fleet scale.
- `DemandTrace.rates` is a proxy oracle: un-thinned test-day counts times `q`, smoothed by a centred 15-minute moving average.
- Real TLC data has no ground-truth change labels, so `change_points=[]`.
- TLC taxi-zone geography is compressed into 25 grid cells; empty cells remain valid simulator zones.

## Commands

```bash
cd /Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-cuddly-winner/perceptron-p07-multi-agent-allocation
uv pip install --python .venv/bin/python pyshp
components/scenarios/fetch_nyc_tlc.sh
.venv/bin/python -m pytest -q tests/test_nyc_tlc.py
nice -n 10 .venv/bin/python - <<'PY'
from components.scenarios.nyc_tlc import build_nyc_trace
from components.simulator.core import DispatchCore
from components.policies.policies import make_policy

trace, meta = build_nyc_trace(["2025-07-04"], ["2025-07-01", "2025-07-02", "2025-07-03"], seed=0)
p = make_policy("reactive")
p.reset(meta)
core = DispatchCore(trace, n_agents=40, patience=10, init_seed=0, init_shares=meta["hist_shares"])
served = arrivals = 0
while not core.done:
    st = core.state()
    info = core.step(p.act(st))
    p.observe(info)
    served += int(info.served.sum())
    arrivals += int(info.arrivals.sum())
print(served / arrivals)
PY
```

Validation:

- `tests/test_nyc_tlc.py`: `3 passed in 2.16s`
- Reactive one-day smoke: `arrivals=14324 served=13980 lost=289 served_fraction=0.975984`
