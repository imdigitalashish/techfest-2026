# P6 demo — 3-minute talk track (stage view)

**Setup (once, from a fresh clone)**
```bash
cd perceptron-p06-stat-arb
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.lock --compile-bytecode
```
`--compile-bytecode` is optional; it moves Python's first-use compilation into setup (7 s here).

**Run:** `demo/run.sh` starts the backend on 127.0.0.1 and opens the browser.
- The page opens in the **stage view**: three steps, each fitting one 1440×900 screen.
- Within seconds the badge turns green, **LIVE**: Numba has compiled, and the decision step has been timed on this laptop.
- If anything fails, open `demo/fallback/p6_demo_standalone.html`: one file, offline, the same page.

**Check:** `demo/smoke.sh`, headless, about 30–60 s; exit 0 means every assertion passed.
- It includes a headless-Chrome run of the race and of a killed backend.
- It reports SKIP if no Chrome or Chromium is installed.

**Timings measured on this shared Mac (fresh clone):**
- The first visual is immediate: the page renders from the exported assets in OFFLINE mode and upgrades itself to LIVE.
- With `--compile-bytecode` (load average 5–7): page served 2.1 s after `run.sh` started; LIVE at 44.4 s.
- Without it (load average 9): page 6.5 s; LIVE at 128.7 s, while Python compiled numpy, polars, scikit-learn and numba and loaded the native libraries for the first time.
- After one run (warm venv): page 0.3–0.5 s; LIVE in 4–14 s, depending on load. That is why step 1 below is to run `demo/smoke.sh` once.

## Before going on stage
1. Run `demo/smoke.sh` once. It checks everything and warms the bytecode.
2. Run `demo/run.sh` and wait for the green **LIVE** badge.
3. Set the browser to full screen at 1440×900 or larger. If a step does not fit, press ⌘− once.
4. Step 1 opens at the race setup: frozen fills · 1 bp/leg · δ 1 ms one-way, paused just before the busiest 30 s of the window.
5. Keys: → / ← or PageDown / PageUp (clickers) change step. **SPACE** is the race key. "Dashboard (Q&A)" shows everything on one page for questions.

**Rule for numbers:** read every number off the screen.
- The "expected" values below are what the screen shows **at the setup named in the same row**. They come from the exported grid, which smoke checks against the live code.
- Window values are this 15-minute window; day values are the full held-out day **at that one setup**. The evidence cards use a different statistic, the 6-scenario day score, and say so.

| time | step · click | say | expected on screen (setup) |
|---|---|---|---|
| 0:00–0:17 | **Step 1**, nothing yet | "Cross-venue BTC mispricings live for milliseconds. Which are still worth anything when our order lands? This replays recorded quotes from a day held out from fitting, though inspected before; the window is fixed by a rule. Every dollar is **simulated execution surplus, not P&L**." | the amber scope strip (2026-10-01 13:37–13:52 UTC, densest 15 min by episode count); the LIVE badge |
| 0:17–0:35 | **▶ Play** at 1×, then **0.1×** | "Arrows are mispricings: buy at the tail, sell at the head; orange beats both fees. Each clock runs while its mispricing is open; the shaded part is faster than these quotes can resolve. The yellow tick is where a machine's order lands." | a clock closing with ✓ / ½ / ✗ and its simulated dollars; "every ~100 ms" under Binance spot and OKX, "~3.3 ms" under Coinbase |
| 0:35–0:55 | drag the **knob**: 10 µs → 1 ms → 5 ms | "The knob is one-way latency: same opportunities, same simulator, three policies. At 1 ms naive already loses here; the threshold makes money. At 5 ms the threshold dips **in this window** but stays positive **over the day**; that is why the day column is there." | 1 ms: window naive **−$4.97**, threshold **+$25.36**; day **+$180**, **+$662**. 5 ms: window **−$92.51**, **−$5.17**; day **−$650**, **+$249**. Big number (threshold − naive) at 5 ms: **+$87.34** window, **+$899** day |
| 0:55–1:15 | click **strict V1** (still at 5 ms, or back at 1 ms), then **frozen** | "Strict fills use the *next* published quote, with policies refit. Selection falls to about break-even; naive loses heavily. The robust result is the **gap**: over 12 sampled days, 5 inspected before, about $2.9k frozen and $6.5k strict, **mean day-level uplift summed over 6 fee/latency scenarios**, 12 of 12 days." | strict, 1 ms: window naive **−$110.10**, threshold **+$0.69**; day **−$1,958**, **+$7**. The note under the big number: **+$2,898** frozen, **+$6,544** strict, 12/12 and 12/12 |
| 1:15–1:22 | **→ Step 2**; point at the rule | "Your turn: press space when a mispricing flashes yellow. The rule is fixed on screen; every trial counts, lag included." | rule panel (random draw from 243, 1.5–4 s lead-in at 1×, 5 trials or 45 s); race setup line |
| 1:22–1:50 | **Start 5 trials**; the judge presses SPACE; stay quiet. **At 30 s on the race clock, press Stop now** (the clock turns amber and says so) | — | Start applies the race setup: **frozen · 1 bp/leg · δ 1 ms**, 1×, controls locked. Stop scores the completed trials |
| 1:50–2:12 | point at the **2×2** beside the replay | "This is the whole window at your median reaction time, not just your five trials. Acting on everything you saw loses about a hundred dollars; the selector, re-tuned at your speed, declines to trade. The machine's selector at 1 ms makes twenty-five. Most had already closed when your order landed." | at about 300 ms: you · naive **≈ −$109 to −$118**, 0 both legs; you · threshold **$0**, 0 trades; machine · naive **−$4.97**; machine · threshold **+$25.36**. About **79–81%** closed at your L vs **15%** at 2 ms. The ratio "×" is computed on screen |
| 2:12–2:45 | **→ Step 3** | "Over the full day naive turns negative within a few milliseconds. Our learned model, LEV, beat the threshold in the pre-registered test, about $300 on the same six-scenario score; under strict fills a quarter survives, within noise once shared liquidity is dropped: **a benchmark, not a validated edge**. Median observed lifetime: 90 ms; the 11 to 147 ms spread is an illustrative sensitivity range, not a bound. Compute is microseconds; the budget is distance." | frontier note: **2 ms–3 ms** (5 legs), **4.6 ms** (9 legs). Cards: **+$299** [+$130, +$468], 12/12; unseen-7 **+$343** [+$70, +$616]; strict **+$73**; collisions dropped **+$40** [−$12, +$92]; **90.5 ms**; **11.3–147.1 ms**; **6.1 µs** p50 |
| 2:45–3:00 | — | "MVP: detection and decay with confidence intervals. Stretch: a simulated latency budget and this replay; live paper trading is next." | the budget card; about 8 s spare |

**Time budget:**
- Spoken: 344 words, about 115 s at 180 words per minute.
- Race: about 25 s, with Stop as the cue at 30 s.
- Clicks and pauses fill the rest of the 3:00.

`demo/smoke.sh` fails if the spoken column grows past 350 words.

**Where the cut detail went:** venue cadences, the race rule's specifics, the leg sets of the two naive crossings, and the unseen-7, strict and collision numbers are in the right-hand column (point, don't read) and in the Q&A table below.

The trial-dependent figures (reaction time, the "×" ratio, the per-trial outcomes, the percentage closed) change with every judge. The page computes them; never quote them from this table.

## If something goes wrong
- **Badge turns amber, "OFFLINE · backend lost at …":** keep going. Every number now comes from the exported grid, produced by the same committed code; the labels say so.
  - A finished race is rescored on the grid at once; its status reads "scored after the backend was lost".
  - New races still work, with reaction times snapped to the 100 ms–2 s grid and the machine simulated at the 7 µs allowance.
  - Restarting `demo/run.sh` upgrades the page back to LIVE within about 5 s.
- **The race runs long:** at 30 s the race clock turns amber; press **Stop now · score completed trials**. The 45 s deadline stops it anyway, and every trial, false start and timeout stays listed.
- **The race was scored at another setup**, because someone changed δ or the simulator afterwards: the setup line says "Rescored at the current setup". Click **↺ back to the race setup**, or read the numbers as shown.
- **The browser or page fails:** open `demo/fallback/p6_demo_standalone.html` (offline, same page) or play `demo/fallback/p6_demo_walkthrough.mp4`.

## Honest caveats a judge may raise

| question | answer | source |
|---|---|---|
| Is this real P&L? | No. It is *basis-adjusted simulated execution surplus*: IOC legs at observed prices, ≤ 0.05 BTC, inventory assumed pre-positioned, uniform fees of 1 and 2 bp per leg. Frozen fills use the last published quote at arrival, which is optimistic. Strict fills use the next published quote, a stress scenario. Neither is calibrated on our own orders. | `README.md`, `eval/results/sensitivity_amendment1.md` |
| What exactly is "+$2,898" or "+$299"? | A mean over 12 test days of a **day score summed over 6 fee/latency scenarios** (1 and 2 bp/leg × δ 1, 5, 20 ms), as pre-registered. It is not one policy's surplus at one setup. The counters' day column is one setup, so the two are not comparable. | `eval/PREREGISTRATION-walkforward-12d.md` |
| Were the test days untouched? | 12 sampled first-of-month days; 5 of them (2026-06-01 … 2026-10-01, including the demo day) were inspected before registration. On the 7 never-inspected days, LEV − threshold was +$343 [+$70, +$616], 7/7. 2026-10-01 is held out from fitting, not a blind confirmation. | `eval/PREREGISTRATION-walkforward-12d.md` (disclosure of prior looks), `eval/results/falsification_walkforward_12d_prereg.md` |
| Did you cherry-pick the window? | The rule (`demo/build_assets.py:window_rule`) counts detected episodes, with no P&L term. It was written after we had inspected this day, so it is a disclosed rule, not proof of an untouched window. The window does not carry every sign: at 5 ms the threshold is −$5.17 here and +$249 over the day. The day column sits beside it. At δ = 1/5/20 ms the day grid reproduces the committed 2026-10-01 totals exactly: V0 −$2,487.83 / +$1,175.13 / +$1,341.53 and V1 −$6,689.92 / −$19.51 / −$26.01. Smoke asserts this. | `demo/assets/provenance.json`, `eval/results/falsification_walkforward_12d_prereg.json`, `eval/results/sensitivity_amendment1.json` |
| Does LEV beat the threshold? | Pre-registered frozen walk-forward: +$299 mean day-level uplift (6-scenario sum), t-CI [+$130, +$468], 12/12. Strict fills: +$73 [+$10, +$135]. Strict fills with a 1 s markout: +$70 [+$0.2, +$140]. Shared-liquidity collisions dropped: +$40 [−$12, +$92], within noise. A frozen-trained LEV scored under strict fills: −$7.8. **A benchmark, not a validated edge.** | `eval/results/sensitivity_amendment1.md` |
| What is robust, then? | Selection versus naive. The threshold − naive gap, mean day-level uplift summed over 6 scenarios, is +$2,898 frozen and +$6,544 strict, 12/12 days each (a pre-registered secondary analysis). Naive turns negative within a few ms: between 2 and 3 ms one-way on the 5 walk-forward legs (this demo's grid), and at 4.6 ms on the 9-leg baseline day (`latency_budget.md`, log-linear interpolation). | `eval/results/latency_budget.md`, the frontier panel |
| Your lifetimes are shorter than the venues' publication interval. | Yes. In these samples Binance spot and OKX publish about every 100 ms and Binance perp every 26 ms, so faster closes are not resolvable from these quotes; the clocks shade that region. Pooled median observed lifetime 90.5 ms (hour-block CI 84.0–100.0). Shifting endpoints within publication intervals gives an illustrative 11.3–147.1 ms sensitivity range, not a bound on executable lifetime. This window's median is 32.3 ms. | `eval/results/decay_report.md`, `update_cadence.md`, `live_cadence.md`, `deliverables/round1-abstract.md` |
| What latency does this laptop really have? | We don't know it. The "this Mac (India)" presets are the 5th percentile of *receive minus venue timestamp*, and the Mac's clock offset is unresolved: the SNTP log in `live_latency.md` shows uncertainties of hundreds of ms. They are not lower bounds on network latency. The Tardis-collector p50s (1.8–40 ms) are venue → collector. Order latency is not measured; the simulator assumes order = feed = δ. Presets snap to the nearest grid δ, and the chip says which. | `eval/results/live_latency.md`, `eval/results/latency_budget.md` |
| Is this a live trading system? | No. The detector ran in batch over recorded quotes; open-time features are causal, so the replay is paper-trading-like. Live paper trading is a stretch goal (C10). | `architecture/components.md` |
| Isn't comparing a human to a machine unfair? | It is a scale illustration, not a claim. The rule is fixed and shown before the trials: uniform random draw, 1.5–4 s lead-in at 1×, every trial reported. Display and input lag count. The 2×2 is the whole window simulated at the median RT, not the sum of the trials. The human's selector is the threshold re-tuned on 09-01 at that latency (nearest grid point, 100 ms–2 s). The machine's decision delay is the live p50 when LIVE; offline it is the walk-forward's 7 µs allowance, and the ratio is against the committed 6.08 µs p50. | `demo/app.js` (race), `demo/live.py:race` |
| How long can the race take? | At most 45 s: five trials, or the presenter deadline, whichever comes first. Stop scores the completed trials. Smoke drives a 5-trial race with a false start in headless Chrome and asserts it ends within the deadline (about 20 s). | `demo/browser_check.py` |
| Can we trust laptop timings? | They are in-kernel `mach_absolute_time` on a shared machine, so treat them as upper bounds for a dedicated core. Committed: 6.1 µs p50 / 41.5 µs p99. The live figure varies with load. | `eval/results/decision_timing.md` |
| How are thresholds set at latencies outside the registered three? | Re-tuned per (pair, fee, δ, decision delay) on 2026-09-01 with the committed `rules.fit_threshold`. At δ = 1/5/20 ms they equal the walk-forward's fits (asserted in the build). | `demo/build_assets.py:train_policies` |
| Under strict fills the threshold is negative too. | Over the 12 days, yes for several days. With next-quote fills, selective policies are about break-even (threshold −$19.51 on 2026-10-01, 6-scenario sum) while naive loses thousands. The robust result is the gap, not the level. | `eval/results/sensitivity_amendment1.md` |
| Why does LEV's frontier wiggle between 5 and 20 ms? | Its latency input was trained at only three latencies (1/5/20 ms one-way), so it interpolates step-wise between them; outside 1–20 ms it is hatched or dashed. One more reason it is a benchmark. | `components/decision/autoresearch/rules.py` |
| Fees? | Uniform 1 and 2 bp per leg, not venue tiers; official fee tables are only partly verified. | `research/notes/fees.md` |

## Files
- `run.sh`: one command; backend plus browser, or offline if there is no venv.
- `smoke.sh` → `smoke.py` + `browser_check.py`: headless assertions, including a headless-Chrome race and backend-loss check.
- `index.html`, `app.js`, `style.css`: the page (stage view and dashboard). No libraries, no CDN.
- `server.py` and `live.py`: the optional backend. Live recompute, the race, and in-kernel timing, all with committed code.
- `build_assets.py`: the deterministic asset builder. Run it once through `eval/run_guarded.sh`; it needs the raw Tardis days.
- `assets/`: what the page and backend read. `provenance.json` holds input md5s, source blob hashes and every reproduction check.
- `make_fallback.py` → `fallback/p6_demo_standalone.html`, plus the screenshots and recording in `fallback/` (see its README).
