# C1 feed — market-data adapters

## 1) Responsibility + contract summary

C1 normalizes any market-data source into the project `QuoteFrame` top-of-book stream with two clocks. Inputs are Tardis normalized `quotes` CSVs or raw live websocket frames recorded as `recv_ns<TAB>json`. Output fields are `ts_exch_us`, `ts_recv_us`, `exch_ts_imputed`, `venue`, `instrument`, `bid_px`, `bid_sz`, `ask_px`, `ask_sz`, sorted by `ts_recv_us`. Invalid rows are dropped/counted: zero or NaN prices, and crossed/locked own books. Out-of-order exchange timestamps are kept but counted. Design SLO: >=2M rows/s batch parse on M5 and <50us live adapter overhead per frame.

## 2) State of the art / best existing practice

- **Historical Data Details — Overview · Tardis.dev · https://docs.tardis.dev/historical-data-details/overview · claim:** Tardis timestamps every received message at arrival with 100ns precision using a synchronized clock. Use this as the model for `ts_recv_us`: collector arrival time is first-class, not a derived field.
- **Historical Data Details — Overview · Tardis.dev · https://docs.tardis.dev/historical-data-details/overview · claim:** Tardis documents daily 00:00 UTC websocket re-subscription/restart to obtain initial order-book snapshots and warns of roughly 300-3000ms gaps during this process. Feed code must preserve data-gap metadata rather than pretending continuity.
- **Historical Data Details — Overview · Tardis.dev · https://docs.tardis.dev/historical-data-details/overview · claim:** Tardis validates subscription responses, sequence numbers where exchanges provide them, stale connections, duplicated trades, and crossed books. These are the right feed-health counters for our adapters.
- **Cryptocurrency Exchange Feed Handler README · cryptofeed · https://github.com/bmoscon/cryptofeed/blob/master/README.md · claim:** cryptofeed normalizes multiple crypto exchange feeds to standardized callback objects; callbacks receive both the normalized object and the timestamp cryptofeed received the message. This matches our two-clock adapter shape.
- **Cryptocurrency Exchange Feed Handler README · cryptofeed · https://github.com/bmoscon/cryptofeed/blob/master/README.md · claim:** cryptofeed ships a synthetic NBBO aggregator across user-specified exchanges and supports L1_BOOK, L2_BOOK, L3_BOOK, trades, ticker, funding, liquidations, index, and candles. Cross-venue top-of-book aggregation is therefore commodity plumbing; our differentiation should be latency-aware ranking.
- **Cryptocurrency Exchange Feed Handler README · cryptofeed · https://github.com/bmoscon/cryptofeed/blob/master/README.md · claim:** cryptofeed can record feeds to zstd-compressed pcap files and replay them later. Deterministic capture/replay is best practice for debugging live feed bugs.
- **ccxt docs home · CCXT · https://docs.ccxt.com/#/README · claim:** CCXT presents a unified API for 100+ crypto and prediction-market exchanges in multiple languages. It is a portability reference, but the opened page did not verify timestamp semantics for websocket receipt vs exchange event time.

## 3) Baseline we ship now

- Batch: `components/feed/normalize.py::load_tardis_quotes` reads Tardis `quotes`, maps `timestamp -> ts_exch_us` and `local_timestamp -> ts_recv_us`, filters non-positive/crossed rows, converts Deribit USD contract amounts to base units, casts to `QUOTE_FRAME`, and sorts by receive time.
- Live: `components/feed/live_recorder.py` records raw websocket frames for 12 venues with local `time.time_ns()` before parsing; `normalize.py::load_live` parses BBO shapes for Binance, Binance futures, Coinbase, Kraken, OKX, Bybit, Deribit, Hyperliquid, Gate.io, Bitget, etc.
- Operational counters to add around the baseline: rows-in, rows-valid, invalid-price drops, crossed-book drops, imputed exchange timestamp fraction, per-venue out-of-order `ts_exch_us` count, per-venue reconnect/gap intervals, and parse rows/s.

## 4) Innovation candidates

Scores: 1 = weak, 5 = strong.

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability |
|---|---|---:|---:|---:|---:|---:|
| Two-clock feed audit | Per-venue dashboard for `ts_recv_us - ts_exch_us`, negative-latency/skew rows, imputed timestamp fraction, and gap intervals. | 5 | 2 | 5 | 5 | 5 |
| Venue-specific health FSM | Normalize reconnects, stale socket, subscription ack, sequence-reset, snapshot, and gap states into one feed-health timeline. | 4 | 3 | 4 | 5 | 4 |
| Recorder/replay parity harness | Replay live raw frames through the same parser and diff against persisted `QuoteFrame` hashes and row counts. | 4 | 3 | 4 | 5 | 4 |
| Adaptive source selection | If two venues/products provide redundant anchors, downweight feeds with high recent latency or missing exchange timestamps before C3/C6. | 3 | 4 | 3 | 4 | 4 |

Best near-term candidate: **two-clock feed audit**, because it directly feeds C2/C7/C8 and is simple to demonstrate with real India-vantage recordings.

## 5) Isolated scalar metric

**Parse coverage (%):**

`parse_coverage = 100 * valid_quote_rows / raw_frames_or_csv_rows`

Compute per venue/instrument/source-day. For Tardis CSV, denominator is CSV rows; for live raw files, denominator is JSON frames that reached the parser. Report alongside `monotonicity_violations_per_1m = 1e6 * count(diff(ts_exch_us)<0 by leg) / valid_rows`, because high coverage with time disorder can still poison latency models.

## 6) Risks

- Exchange timestamps are heterogeneous; exact semantics for each live venue are **UNVERIFIED** unless their own docs are opened.
- Clock skew can create negative feed latencies; C1 must not silently clip because C2 needs the skew signal.
- Live websocket payloads change; parser failures can look like market silence unless counted by venue.
- Tardis daily snapshot/resubscription gaps can create false opportunity endings if C3/C6 do not mask gap intervals.
- `time.time_ns()` is not a hardware receive timestamp; Mac/India live latency is useful for demo but not colocated trading truth.
