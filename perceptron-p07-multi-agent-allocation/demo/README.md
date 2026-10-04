# P7 demo: "your surge, live"

A judge-driven demo for Perceptron 2026, Problem 7 (splitting a shared fleet when demand keeps changing). Two fleets of 40 units, the best rule-based allocator and our look-ahead planner (an LP re-solved every simulated minute), face the **same requests**. The demo opens on **real NYC taxi demand on the night of 4 July 2025**. The judge can then drop a surge anywhere, on real demand or in a synthetic city, and watch both fleets respond. Every number on screen is either computed live by the committed code or copied verbatim from a committed result file, with its source shown on hover.

## Run it

```bash
perceptron-p07-multi-agent-allocation/demo/run.sh      # opens http://127.0.0.1:8707/ (CPU only, offline)
perceptron-p07-multi-agent-allocation/demo/smoke.sh    # headless checks; --quick skips the week recompute
```

- **First run on a fresh clone:** `demo/setup_venv.sh` creates `.venv` once. It uses Python 3.11, `requirements.txt` and `highspy==1.15.1` (the HiGHS version behind the committed results), and needs network once. After that, everything runs offline.
- **Options:**
  - `run.sh --no-open` serves without opening a browser;
  - `--port N` picks the port (the default is 8707, or the next free one);
  - `--no-prewarm` skips the background recomputes.
- **Time to first visual:** the server prints it once the page has drawn its first city ("first visual X s after run.sh started").
- **No backend?** Open `demo/index.html` directly (file://). It replays sessions recorded by `demo/record.py` under a red RECORDED banner. `demo/fallback/` holds screenshots and a short video.

## The four tabs

| Tab | What happens | Live or committed |
|---|---|---|
| **July 4th (real trips)**, opening | Real Manhattan yellow-taxi demand (NYC TLC, July 2025, thinned, replicate 200). It fast-forwards from 3 July 00:00 to 4 July 21:15 as a labelled time-lapse, then runs live. Reactive (the best rule on this replay) and the planner run side by side through the 21:30–23:30 window; the observed 22:00–22:30 surge is marked (cause UNVERIFIED). Clicking adds YOUR synthetic surge on top of real demand: live only, with no committed evidence. | Live: both fleets, counters, prices. Committed: the 20-replicate receipts (`eval/results/nyc-v2`, `nyc-v2b`). The window losses equal the committed row for replicate 200 when no surge is injected. |
| **Stress test (SYNTHETIC city)** | The committed (L, P) map is the knob. Before the judge clicks, the card shows the committed prediction for that cell. A click drops the committed shock shape (2×2 zones, +3× the zone-average rate, 6 h). After 120 simulated minutes the judge's result lands as a dot on the committed per-seed strip. | Live: the city, counters, the dot. Committed: prediction text, per-seed dots and heatmap (`phase-v2`, `mvp-v2`, `trust-v2`). |
| **A week** | Greedy, reactive and the planner over 7 synthetic days with a shock every day, drift and spikes (seed 200). | Recomputed live in a background process; bit-identical to `eval/results/long-week-v2/episodes.csv`. Bars are this run; ticks are the committed 10-seed means. |
| **Evidence / honest panel** | Honest limits, then the committed tables, verbatim. | Committed (`demo/data/evidence.js`). |

## Where each number comes from

- **Computed live** by the committed simulator, policies and planner, wrapped by `demo/engine.py`: every city, counter, served share, empty-hop rate, LP shadow price and solve time.
  - Shocks are injected only from the current minute onward. The past is asserted unchanged.
  - Both fleets share one request stream, so the comparison uses common random numbers, asserted every step.
- **Copied** by `demo/export_evidence.py` from committed `summary.md`, `confirm.md` and `episodes.csv` files. Cells are verbatim. The few derived values (means of committed per-seed values) are labelled "derived". `--check` fails if the copy goes stale.
- **Exported input** `demo/data/nyc_jul03-04_r200.npz` (35 KB), made by `demo/export_nyc.py` from the committed `components/scenarios/nyc_tlc.py`. It holds the thinned real trips of replicate 200 plus what policies may know: the OD map, time-of-day profile and shares learned from 1–2 July. It also holds cell labels ranked by 1–2 July pickups. The script checks parity with `eval/results/nyc-v2/episodes.csv`. Regenerating it needs the gitignored `.data/` (`components/scenarios/fetch_nyc_tlc.sh`).
- **Parity:** the shock-day, week and NYC recomputes reproduce the committed rows exactly. On this machine they match bit for bit with highspy 1.15.1, and `smoke.sh` checks this.

## Honesty notes (also on screen)

- **It cannot see a surge coming.** It wins by planning over the lead time with the units about to free up and the live queues. It anticipates only what it has learned: the daily cycle and drift. On 4 July it had only 1–2 July as history.
- **NYC is real demand on a simulated fleet:** 5×5 cells, same-zone matching, simulated travel and patience, trips thinned to ~10/min. Injected surges on NYC are synthetic and have no committed evidence.
- **Live numbers are one run.** Committed numbers are means over seeds or replicates with paired 95% CIs.
- **Seeds:**
  - Demo cities use seeds 7000+, which appear in no committed result or registration.
  - The NYC tab uses thinning replicate 200.
  - Reserved test seeds 300–329 are untouched.

## Files

`run.sh` · `setup_venv.sh` · `smoke.sh` → `smoke.py` · `server.py` (stdlib HTTP, 127.0.0.1 only) · `engine.py` · `index.html` (one file, vanilla JS + canvas, no URLs) · `export_evidence.py` · `export_nyc.py` · `record.py` · `data/` (committed exports) · `SCRIPT.md` (3-minute talk track) · `fallback/`.
