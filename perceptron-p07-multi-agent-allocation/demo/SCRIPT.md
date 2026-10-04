# P7 demo: 3-minute talk track

**Before the judges arrive.**
- Run `perceptron-p07-multi-agent-allocation/demo/run.sh`. It opens the July 4th tab **armed**: nothing moves until you press ▶. The terminal prints the time to first visual.
- Go full screen at 100% zoom. The stage is built for 1280×720 (a projector) and scales up on larger screens. Nothing needs scrolling.
- Keys: space plays or pauses, 1–4 set the speed, r restarts the current run, Esc closes the drawer.
- Every label carries its provenance:
  - **LIVE**: computed now by the committed code, one run.
  - **COMMITTED**: copied verbatim from committed result files (means over seeds or replicates, paired 95% CIs). Hover any underlined number to see its file.
  - **RECORDED**: computed earlier by `demo/record.py` (fallback only).
- Receipts, legends and sources sit in the drawer (the ▸ button at the bottom of each sidebar).

## 0:00–0:50 · July 4th: the unperturbed reference run

1. **Point at the green data bar.**
   > "Real Manhattan yellow-taxi pickups, NYC TLC, July 2025, thinned to about 10 a minute for 40 vehicles. Real demand; the fleet, travel and patience are simulated. Left, the best rule on this data. Right, our planner: a linear program re-solved every simulated minute. Both get exactly the same requests."
2. **Press ▶ (pulsing green).** A time-lapse labelled *fast-forwarding, computed live* covers 3–4 July up to 21:15 on the 4th in a few seconds. The night then plays at 4 simulated minutes per second.
3. **At 22:00 the dashed *observed surge* box lights up on Two Bridges (bottom row, 4th cell).**
   > "This cell had **62** raw TLC pickups in half an hour, before thinning, against **3.0** on the training days. We don't know why, and neither fleet was told."
4. **At 23:30 it pauses by itself.** Point at the counters and the result card.
   > "Fleet-wide losses from 21:30 to 23:30: reactive **46**, planner **1**. The tick shows that matches our committed row for this replicate. Across 20 replicates the means are **1.40** versus **39.55**. This window is illustrative and chosen after the fact, not a causal estimate. Over the whole two days the planner serves **+2.52 pp [+2.39, +2.67], 20 of 20**."

## 0:50–1:20 · Handover: your turn, on real demand

1. **Press the pulsing amber "Your turn: restart at 21:15".** A separate run opens, armed at 21:15. Hand over the mouse.
   > "Click any cell to drop a surge. The clock starts when you click."
2. **The judge clicks; press 3 (8×).** Read the sidebar.
   > "Your surge: 21:15 to 24:00, 2 h 45 min. A surge lasts up to 6 hours, but this replay ends at midnight."
3. **It pauses two hours after the surge.** Point at *lost since your surge* and the chip under the planner.
   > "Live only: we have no committed evidence for surges injected on NYC."

## 1:20–2:05 · Stress test (SYNTHETIC city): the reference first, then your intervention

1. **Click "Stress test (SYNTHETIC city)".** The badge turns amber. The city opens armed at 05:00 in a 12-hour run, like the committed phase-v2 runs.
2. **Point at the card before anyone clicks.**
   > "At lead time 1 and patience 10, our committed result is **126.8 fewer** requests lost per surge than the best rule, and **+5.62 pp [+5.32, +5.93], 20 of 20** served. Each grey dot is one committed reference run."
3. **The judge clicks any zone; press 3 (30×).** About 4 seconds later the yellow dot lands. The chip says **IN-REFERENCE**: onset inside 04:12–06:36, ×1, one surge, same run length.
   > "That's your live intervention, shown alongside 20 committed reference runs. It is not a new test seed or a calibrated prediction for this location or time."
   - A second overlapping surge, a ×½ or ×2 size, or a late onset is flagged **OFF-REFERENCE** and drawn as a hollow ring.
4. **Click L = 8, P = 10 (bottom right of the grid).** The card turns red.
   > "Now moving a unit takes 8 minutes per hop. Our committed result here is **no reliable gain: −0.38 pp [−0.89, +0.04], 6 of 20**. We show you where we lose."

## 2:05–2:30 · A week (do not skip: 25 s)

1. **Click "A week".** The server recomputed it in the background at start-up. It plays 7 days in about 24 s.
2. **Point at the bars and the black ticks.**
   > "A shock every day, a drifting hotspot and spikes. The bars are this live run, seed 200; the black ticks are our committed means over 10 seeds. By day 7 greedy serves **0.466**, reactive **0.832** and the planner **0.912**. Over the week that's **+6.34 pp [+6.26, +6.43]** against reactive, **10 of 10** seeds. A 30-day month gives **+6.37**, but on only **4 seeds**."
3. **Point at the green tick line.** This live run matches the committed served-fraction and loss metrics; daily fractions match at committed precision.

## 2:30–3:00 · Honest panel and close

1. **Click "Evidence / honest panel" and read three lines.**
   1. "It cannot see a surge coming. It re-plans over the lead time with the units about to free up and the queues. It anticipates only what it learned: the daily cycle and drift."
   2. "Under a pure shock, a planner that ignores the forecast did better, **+1.19 pp**. A perfect forecast lowered service in **3 of 4** long-lead-time cells."
   3. "Our pre-registered change-detector hypothesis did not replicate."
2. **Point at the footer.** It holds the p-values; don't read them.
   > "The headline is pre-registered on 30 fresh seeds: **+3.73 pp** under a shock, **+5.47** under shock plus drift, 30 of 30."
3. **Close with the green line at the top of the panel.**
   > "The interventions and simulations were computed live; the reference distributions and confidence intervals are committed results."

## Numbers and their sources

| Number | Source |
|---|---|
| 62 vs 3.0 raw TLC cell pickups before thinning, 20.67×, cell 3, 22:00–22:30 | `research/components/real-trace-replay.md` (Top July 4 surges, rank 1) |
| Window losses 1.40 / 39.55 / 111.90 / 218.10 (planner / reactive / greedy / static) | means of `eval/results/nyc-v2/episodes.csv` (`summary.md` rounds them) |
| Replicate 200: reactive 46, planner 1 | `eval/results/nyc-v2/episodes.csv`, seed 200 (recomputed live, matched on screen) |
| +2.52 [+2.39, +2.67], 20/20 · +1.52 [+1.43, +1.59], 20/20 (drawer) | `eval/results/nyc-v2/summary.md` · `eval/results/nyc-v2b/summary.md` |
| Reference protocol: 12-h runs, onsets 04:12–06:36, seeds 200–219, one ×1 surge | `eval/results/phase-v2/config.json` |
| −126.8 per surge, +5.62 [+5.32, +5.93] (20/20) · +16.3, −0.38 [−0.89, +0.04] (6/20) | `eval/results/phase-v2/summary.md` |
| 0.910 → 0.466 · 0.906 → 0.832 · 0.960 → 0.912; +6.34 [+6.26, +6.43], 10/10 | `eval/results/long-week-v2/summary.md` |
| Month +6.37 [+6.29, +6.44], 4/4 seeds | `eval/results/long-month-v2/summary.md` |
| +3.73 / +5.47 / +5.99 pp, 30/30, Holm p = 1.1e-08 (footer) | `eval/results/mvp-v2/confirm.md` (pre-registered: `eval/preregistration.md`) |
| +1.19 [+1.06, +1.32] pp (queue-only vs EWMA, pure shock) | `eval/results/mvp-v2/confirm.md`, family S1 |
| 3 of 4 long-lead cells (−1.09, −1.49, −1.10 pp) | `eval/results/phase-v2/summary.md` |

Live numbers (the 46 and 1, the surge losses, the dot, the week bars) are one run each, computed on screen. The recomputes that are compared with committed rows match the committed served-fraction and loss metrics, and daily fractions match at committed precision. `demo/smoke.sh` checks this.

## If something fails

1. **"LIVE COMPUTATION STOPPED" banner.** The cities pause and nothing is relabelled.
   - Press **Retry**. If the server restarted, the run starts again, armed.
   - If it doesn't come back, press **Open recorded fallback**. The page switches to RECORDED: red banner, no live labels, clicks off. Say "this is a recording made earlier by the same committed code."
2. **The page misbehaves.** Reload with ⌘R. Or stop the server with Ctrl-C and rerun `demo/run.sh`.
3. **No Python.** Open `demo/index.html` directly. It starts in RECORDED mode. "Recorded turn: a surge at 21:15" replays a recorded intervention.
4. **Nothing runs.** Play `demo/fallback/p7-demo-walkthrough.mp4`, then step through the 1280×720 screenshots `01`–`11` in the order of this script.
