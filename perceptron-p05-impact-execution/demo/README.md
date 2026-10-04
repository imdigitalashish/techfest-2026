# Ghost Market: P5 demo (SIMULATED, ABIDES rmsc04)
Run `demo/run.sh` from a fresh clone. It serves this folder on 127.0.0.1 and opens the browser in under a second; the replays need only python3. `DEMO_NO_OPEN=1` prints `READY: <url>` without opening a browser; `DEMO_STATIC=1` prints the file:// path and exits.
Three beats, five screens. Every screen is labelled SIMULATED and has a `source:` footnote.
1. The answer: TWAP vs our agent, and E10 not confirmed.
2. Why you can trust it: the ghost market (the size knob freezes the view at 09:55, with the 30-seed aggregate beside it), naive vs synchronised coupling, and one seed decomposed.
3. A live "bring your own seed" lane.

Live lane setup: the README's `.venv` plus `scripts/fetch_abides.sh`. After that, `server.py` runs fresh synced twins (about 5–10 s, nice 10, memory guard ≥ 30).
Data: `demo/export.py` re-runs seeds 100–129 through the committed code (`run_world` and `tca`) into `demo/data/*.js` (2.3 MB, ~5 min).
Check: `demo/smoke.sh` (headless) asserts that the data loads, that the numbers equal `claims.json`, that the exported T1 gaps equal the E7/E4/E8 CSVs, that run.sh prints READY within 60 s, and that one live run has pre-trade identity true.
Talk track: `SCRIPT.md`. Screenshots: `fallback/`. Shared helpers: `p5demo.py`. Checks: `smoke_check.py`.
