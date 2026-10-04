# P7 demo: "your surge, live"

A judge-driven demo for Perceptron 2026, Problem 7: splitting a shared fleet when demand keeps changing.

- **The setup.** Two fleets of 40 units face the **same requests**: the best rule-based allocator, and our look-ahead planner (an LP re-solved every simulated minute).
- **The flow.**
  1. It opens, armed, on **real NYC taxi demand on the night of 4 July 2025**.
  2. The unperturbed reference run pauses at its 23:30 result.
  3. The judge then gets their own run and drops a surge anywhere, on real demand or in a synthetic city.
- **Provenance.** Every number on screen is labelled with one value:
  - **LIVE**: computed now by the committed code.
  - **COMMITTED**: copied verbatim from a committed result file, with its source on hover.
  - **RECORDED**: computed earlier by `demo/record.py` (fallback only).

## Run it

```bash
perceptron-p07-multi-agent-allocation/demo/run.sh      # opens http://127.0.0.1:8707/ (CPU only, offline)
perceptron-p07-multi-agent-allocation/demo/smoke.sh    # headless checks; --quick skips the week and recording checks
```

- **First run on a fresh clone.** `demo/setup_venv.sh` creates `.venv` once, with Python 3.11, `requirements.txt` and `highspy==1.15.1` (the HiGHS version behind the committed results). It needs network once; after that everything runs offline.
- **Options.**
  - `run.sh --no-open` serves without opening a browser.
  - `--port N` picks the port (default 8707, or the next free one).
  - `--no-prewarm` skips the background week recompute.
- **Time to first visual.** The server prints it once the page has drawn its first city ("first visual X s after run.sh started").
- **Stage.** The layout is built for a 1280×720 projector viewport and scales up on larger screens. Receipts, legends and sources sit in a drawer (▸).
- **No backend?**
  - Open `demo/index.html` directly (file://). It replays the sessions recorded by `demo/record.py` under a red RECORDED banner, with clicks off.
  - If the server dies mid-demo, the page pauses and shows **LIVE COMPUTATION STOPPED** with **Retry** and **Open recorded fallback**. It never relabels live results as recorded.
  - `demo/fallback/` holds 1280×720 screenshots and a short video.

## The four tabs

| Tab | What happens | Provenance |
|---|---|---|
| **July 4th (real trips)**, opening | Real Manhattan yellow-taxi demand (NYC TLC, July 2025, thinned, replicate 200). The **reference run** opens armed. Press ▶ and a labelled time-lapse runs from 3 July 00:00 to 4 July 21:15; the 21:30–23:30 window then plays and **pauses at 23:30**. Reactive (the best rule on this replay) and the planner run side by side. The counters are fleet-wide losses, 21:30–23:30, an illustrative, retrospectively chosen window, not a causal estimate. The observed 22:00–22:30 anomaly is labelled as raw TLC cell pickups before thinning (cause UNVERIFIED). The reference run refuses surges. **"Your turn: restart at 21:15"** opens a separate run, pre-warmed in the background, armed at 21:15; the judge's click drops a synthetic surge and starts the clock. Each surge shows its real start, end and duration: up to 6 h, but this replay ends at midnight. | LIVE: both fleets, counters, prices. COMMITTED: the 20-replicate receipts (`eval/results/nyc-v2`, `nyc-v2b`). The reference run matches the committed served-fraction and loss metrics of replicate 200. Surges on NYC are live only, with no committed evidence. |
| **Stress test (SYNTHETIC city)** | The committed (L, P) map is the knob. The city follows the committed reference protocol: phase-v2 is 12-hour runs armed at 05:00, with onsets 04:12–06:36; mvp-v2 and trust-v2 are 24-hour runs armed at 10:00. Before the judge clicks, the card shows the committed result for that cell and the 20 per-seed reference runs. A click drops the committed shock shape: 2×2 zones, +3× the zone-average rate, up to 6 h, cut at the end of the run. After 120 simulated minutes the result lands as a yellow dot: the judge's live intervention, shown alongside the committed reference runs, not a new test seed or a calibrated prediction. A surge is **IN-REFERENCE** or **OFF-REFERENCE**; an off-reference surge has its onset outside the window, a size other than ×1, an overlap with another surge, or a different run length. | LIVE: the city, counters, the dot. COMMITTED: the card, per-seed dots and map (`phase-v2`, `mvp-v2`, `trust-v2`). |
| **A week** | Greedy, reactive and the planner over 7 synthetic days with a shock every day, drift and spikes (seed 200). Bars show this run; black ticks show the committed 10-seed means. The month line is committed and has only 4 seeds. | LIVE: recomputed in a background process; it matches the committed served-fraction and loss metrics in `eval/results/long-week-v2/episodes.csv`, and daily fractions match at committed precision. RECORDED in fallback mode. |
| **Evidence / honest panel** | The closing line, the honest limits, then the committed tables verbatim. | COMMITTED (`demo/data/evidence.js`). |

## Where each number comes from

- **Computed live** by the committed simulator, policies and planner, wrapped by `demo/engine.py`: every city, counter, served share, empty-hop rate, LP shadow price and solve time.
  - Surges are injected only from the current minute onward; the past is asserted unchanged. Surges after the end of a run are refused (no zero-length surges).
  - Both fleets share one request stream (common random numbers), asserted every step.
- **Copied** by `demo/export_evidence.py` from the committed `summary.md`, `confirm.md` and `episodes.csv` files. Cells are verbatim. The few derived values (means of committed per-seed values) are labelled "derived". `--check` fails if the copy goes stale.
- **Read at start-up** by `demo/engine.py`: the reference protocol of each synthetic city (run length, seeds, onset window) from the committed `eval/results/<run>/config.json` and the committed shock shape (`components/scenarios/scenarios.py`).
- **Recorded** by `demo/record.py` into `demo/data/recorded_live.js`:
  - the NYC reference run;
  - a recorded turn: a surge on the Midtown Center block at 21:15;
  - the stress test with a surge at 05:00;
  - the week, thinned to 30-minute frames.

  Solve times and wall time are dropped. `--check` verifies the file reproduces from the committed code.
- **Exported input.** `demo/data/nyc_jul03-04_r200.npz` (35 KB) comes from `demo/export_nyc.py`, which uses the committed `components/scenarios/nyc_tlc.py`.
  - It holds the thinned real trips of replicate 200, plus what policies may know: the OD map, time-of-day profile and shares learned from 1–2 July, and cell labels ranked by 1–2 July pickups.
  - The script checks parity with `eval/results/nyc-v2/episodes.csv`.
  - Regenerating it needs the gitignored `.data/` (`components/scenarios/fetch_nyc_tlc.sh`).
- **Parity.** The NYC reference run and the shock-day, week and NYC recomputes match the committed served-fraction and loss metrics; daily fractions match at committed precision. Concretely: `served_frac` within 1e-12, shock and event losses exactly, daily fractions at the committed 5 decimals. This is not whole-row or trajectory identity. `smoke.sh` checks it with highspy 1.15.1.

## Honesty notes (also on screen)

- **It cannot see a surge coming.** It wins by planning over the lead time with the units about to free up and the current queues. It anticipates only what it has learned: the daily cycle and drift. On 4 July it had only 1–2 July as history.
- **NYC is real demand on a simulated fleet:** 5×5 cells, same-zone matching, simulated travel and patience, trips thinned to about 10 a minute.
  - The 62 vs 3.0 anomaly counts raw TLC cell pickups before thinning.
  - The 46 vs 1 counter is fleet-wide losses over two hours.
  - The window is illustrative, not a causal estimate.
  - Surges injected on NYC are synthetic and have no committed evidence.
- **A click is an intervention, not a seed.** It is shown alongside the committed reference runs and is not a new test seed or a calibrated prediction for that location or time.
- **Live numbers are one run.** Committed numbers are means over seeds or replicates with paired 95% CIs. The month has only 4 seeds.
- **Seeds.**
  - Demo cities use seeds 7000+, which appear in no committed result or registration.
  - The NYC tab uses thinning replicate 200.
  - Reserved test seeds 300–329 are untouched.

## Files

`run.sh` · `setup_venv.sh` · `smoke.sh` → `smoke.py` · `server.py` (stdlib HTTP, 127.0.0.1 only) · `engine.py` · `index.html` (one file, vanilla JS + canvas, no URLs) · `export_evidence.py` · `export_nyc.py` · `record.py` · `data/` (committed exports) · `SCRIPT.md` (3-minute talk track) · `fallback/` (1280×720 screenshots and video).
