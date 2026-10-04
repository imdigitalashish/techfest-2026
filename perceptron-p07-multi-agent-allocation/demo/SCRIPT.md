# P7 demo: 3-minute talk track

**Before the judges arrive.**
- Run `perceptron-p07-multi-agent-allocation/demo/run.sh`. It opens the July 4th tab; the first visual takes about 3 s.
- Make the browser full screen at 100% zoom.
- Keys: space pauses, 1–4 set the speed, r restarts the current tab.
- A red RECORDED banner means the backend isn't running; restart `run.sh`.

All numbers below are either live (one run, computed now) or committed. Hover over any underlined number to see its source file.

## 0:00–1:00 · A real night, a real surge (July 4th tab, opens by itself)

1. **Point at the green data bar.**
   > "Real Manhattan yellow-taxi trips from NYC TLC, July 2025, public data, thinned to fit 40 vehicles. Real demand; the fleet is simulated. Left is the best rule-based allocator on this data. Right is our planner, a linear program re-solved every simulated minute. Both sides get exactly the same requests."
2. **During the time-lapse (about 5–15 s depending on load, labelled *fast-forwarding, computed live*).**
   > "Two days, 3 and 4 July, computed live up to 21:15 on the 4th."
3. **When the dashed *observed surge* box lights up on Two Bridges (bottom row, 4th cell), around 22:00.**
   > "This cell had **62** pickups in half an hour, against **3.0** on the training days: **20.67×**. We don't know why. The cause is unverified, and the planner had no way to know either; it learned from 1–2 July only."
4. **Point at the big counters.** The rule's losses climb while the planner stays near zero.
   - Live replicate 200 finishes at **46 vs 1**, and the card shows **✓ equals the committed row for replicate 200**.
5. **Point at the receipts.**
   > "Across 20 thinning replicates, the mean losses in this window are **1.40** for the planner and **39.55** for reactive. Over the two days it serves **+2.52 pp [+2.39, +2.67], 20/20**. On ordinary days, 10–11 July, it still serves **+1.52 pp [+1.43, +1.59], 20/20**."
6. **Point at the amber heat on the planner city.**
   > "It cannot see a surge coming. It wins by planning over the lead time with the units about to free up and the live queues. The amber is the LP's shadow price of one more idle unit."

## 1:00–1:30 · Now you try, on real demand

1. Hand over the mouse.
   > "Click anywhere in Manhattan to add your own surge."
2. Read the label aloud.
   > "Real demand plus *your* synthetic surge: live only. We have no committed evidence for surges injected on NYC."
3. Point at **lost since YOUR surge** and the green line under the planner.

## 1:30–2:30 · Stress test (SYNTHETIC city): we predict first

1. Click **Stress test (SYNTHETIC city)**. The badge turns amber: SYNTHETIC.
2. Point at the prediction card **before** anyone clicks.
   > "At lead time 1 and patience 10, our committed result is that the planner loses **126.8 fewer** requests per surge than the best rule, and serves **+5.62 pp [+5.32, +5.93], 20/20 seeds**. Each grey dot is one committed seed."
3. The judge clicks any zone.
   > "Unannounced to both fleets."
   - After 120 simulated minutes (about 15 s; press 3 for 30 min/s) the yellow dot lands.
   > "Your surge is seed number 21."
4. Click **L = 8, P = 10** in the grid; the prediction turns red.
   > "Moving a unit now takes 8 minutes per hop. Here we predicted **no reliable gain: −0.38 pp [−0.89, +0.04], 6/20**. We show you where we lose."
5. Point at the footer.
   > "The headline is pre-registered: 30 fresh seeds, **+3.73 pp** under a shock, **+5.47** under shock plus drift, **30/30**, Holm **p = 1.1e-08**."

## 2:30–3:00 · Honest panel

1. Click **Evidence / honest panel** and read three lines.
   1. "It cannot see a surge coming."
   2. "Under a pure shock, a planner that ignores the forecast did better (**+1.19 pp**). A perfect forecast lowered service in **3 of 4** long-lead-time cells."
   3. "Real demand, simulated fleet. Our pre-registered change-detector hypothesis did not replicate."
2. Close.
   > "Everything you saw was computed live by the committed code. The NYC and week runs reproduce our committed rows bit for bit."

**If asked about long horizons** (A week tab, recomputed in the background):
> "A shock every day plus drift: greedy falls from **0.910** to **0.466** served by day 7. The planner goes **0.960** to **0.912**, which is **+6.34 pp [+6.26, +6.43]** vs the best rule, 10/10 seeds. Over a 30-day month: **+6.37 pp**."

## Numbers and their sources

| Number | Source |
|---|---|
| 62 pickups vs 3.0, 20.67×, cell 3, 22:00–22:30 | `research/components/real-trace-replay.md` (Top July 4 surges, rank 1) |
| Window losses 1.40 / 39.55 / 111.90 / 218.10 (planner / reactive / greedy / static) | means of `eval/results/nyc-v2/episodes.csv` (`summary.md` rounds to 1.4 / 39.5 / 111.9 / 218.1) |
| Replicate 200: reactive 46, planner 1 | `eval/results/nyc-v2/episodes.csv`, seed 200 (recomputed live) |
| +2.52 [+2.39, +2.67], 20/20 · +1.52 [+1.43, +1.59], 20/20 | `eval/results/nyc-v2/summary.md` · `eval/results/nyc-v2b/summary.md` |
| −126.8 per surge; +5.62 [+5.32, +5.93] (20/20); −0.38 [−0.89, +0.04] (6/20) | `eval/results/phase-v2/summary.md` |
| +3.73 / +5.47 / +5.99 pp, 30/30, Holm p = 1.1e-08 | `eval/results/mvp-v2/confirm.md` (pre-registered: `eval/preregistration.md`) |
| +1.19 [+1.06, +1.32] pp (queue-only vs EWMA, pure shock) | `eval/results/mvp-v2/confirm.md`, family S1 |
| 3 of 4 long-lead cells (−1.09, −1.49, −1.10 pp) | `eval/results/phase-v2/summary.md` |
| 0.910 → 0.466; 0.960 → 0.912; +6.34 [+6.26, +6.43], 10/10; month +6.37 | `eval/results/long-week-v2/summary.md`, `eval/results/long-month-v2/summary.md` |

## If something fails

1. Reload the page (⌘R).
2. Stop the server (Ctrl-C) and rerun `demo/run.sh`.
3. If there's no Python, open `demo/index.html` directly. It replays recorded sessions under a red RECORDED banner, with clicks off.
4. If nothing runs, play `demo/fallback/p7-demo-walkthrough.mp4` (60 s) and step through screenshots `01`–`09` in the same order as this script.
