# Ghost Market: P5 demo (SIMULATED, ABIDES rmsc04)
Run `demo/run.sh` from a fresh clone. It serves this folder on 127.0.0.1 and opens the browser in under a second; the replays need only python3. `DEMO_NO_OPEN=1` prints `READY: <url>` without opening a browser; `DEMO_STATIC=1` prints the file:// path and exits.
Five screens, all labelled SIMULATED, each with a `source:` footnote:
1. the ghost market (our order vs the same seed without it, with an order-size knob);
2. naive vs synchronised twins;
3. TWAP vs the impact-aware schedule;
4. the E6 → E8 → E10 scoreboard;
5. a live "bring your own seed" lane.

Live lane setup: the README's `.venv` plus `scripts/fetch_abides.sh`. After that, `server.py` runs fresh synced twins (about 5–10 s, nice 10, memory guard ≥ 30).
Data: `demo/export.py` re-runs seeds 100–129 through the committed code (`run_world` and `tca`) into `demo/data/*.js` (2.3 MB, ~5 min).
Check: `demo/smoke.sh` (headless) asserts that the data loads, that the numbers equal `claims.json`, that the exported T1 gaps equal the E7/E4/E8 CSVs, that run.sh prints READY within 60 s, and that one live run has pre-trade identity true.
Talk track: `SCRIPT.md`. Screenshots: `fallback/`. Shared helpers: `p5demo.py`. Checks: `smoke_check.py`.
