# P6 demo — 3-minute talk track

**Setup (once, from a fresh clone)**
```bash
cd perceptron-p06-stat-arb
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.lock
```

**Run:** `demo/run.sh`. It starts the backend on 127.0.0.1 and opens the browser.
- The page renders immediately from `demo/assets/`. Within a few seconds the badge turns green, **LIVE**: Numba has compiled, and the decision step has been timed on this laptop.
- If anything fails, open `demo/fallback/p6_demo_standalone.html`: one file, offline, the same page.

**Check:** `demo/smoke.sh`, headless, about 10–25 s on a warm venv; exit 0 = all assertions pass.
- Run it once before going on stage: it also compiles bytecode.
- Measured from a fresh clone with a brand-new venv on this shared Mac: the page was served 6.3 s after `run.sh` started and went LIVE at 48.9 s, while Python compiled numpy, polars, scikit-learn and numba for the first time.
- On a warm venv: page 0.5 s, LIVE in 4–14 s, depending on machine load.
- Adding `--compile-bytecode` to the `uv pip install` moves that compilation into setup.

Before you start, set the browser to full screen at 1440 px or wider. Fee: 1 bp. Simulator: frozen. δ: 1 ms. Leave the replay paused; it opens just before the busiest 30 s of the window.

| time | click | say | point at |
|---|---|---|---|
| 0:00–0:20 | nothing | "Cross-venue BTC mispricings live for tens of milliseconds. Detecting them is easy. The question is which ones are still worth anything when our order lands. This is a replay of real Tardis quotes from our **held-out day**, 2026-10-01, 13:37–13:52 UTC. The window is chosen by a rule fixed in code: the densest 15 minutes by episode count. Every dollar on screen is **simulated execution surplus, not P&L**." | the amber honesty strip; the LIVE badge |
| 0:20–0:50 | **▶ Play** at 1×, then **0.1×** | "Each arrow is a mispricing: buy at the tail venue, sell at the head. Orange means it beats both fees. The green ring flashes each time a venue publishes. Binance spot and OKX publish every 100 ms, Coinbase every 3 ms. That publication cadence is a floor on what anyone can measure from public data. Each clock grows while its mispricing is open. The yellow tick is where a machine's order lands at δ = 1 ms." | a decay clock closing; the shaded cadence floor; the ✓ / ½ / ✗ outcome next to it |
| 0:50–1:30 | drag the **latency knob**: 10 µs → 1 ms → 5 ms → 20 ms | "Same opportunities, same simulator, three policies. At 10 µs everyone makes money. At 1 ms naive is already losing, −$4.97 in this window, while the tuned threshold makes +$25.36. At 5 ms naive is −$92.51 here and −$650 over the full held-out day; the threshold is still +$249 for the day. The frontier shows naive's day total turning negative **between 2 and 3 ms one-way**. LEV is hatched outside 1–20 ms because it was only trained there." | counters (window and full day); frontier zero-crossing note; LEV hatching |
| 1:30–2:20 | **Start 5 trials**; hand the judge the keyboard | "Your turn. When a mispricing flashes yellow, press space. The replay runs at 1× wall clock and the rule is on screen. Every trial counts, and your screen and keyboard lag counts too, just as a feed handler's would." After the trials: "Your median reaction time goes straight into the committed simulator. It is tens of thousands of times our compiled decision step, measured live on this laptop; the page shows the exact ratio. Most of these mispricings, about 80% at 300 ms, had closed before your order landed. Acting on everything you saw lost about $110 in 15 minutes; at 300 ms, none of the 243 orders filled both legs. The selector, re-tuned at your speed, declines to trade: $0. The machine at 1 ms makes +$25." | the 2×2 (you / machine × naive / selector); the closed-before-landing %; the YOU pin on the frontier |
| 2:20–2:50 | toggle **strict V1** | "Now stress the fills: each leg fills against the *next* published quote, and both policies are refit on strict labels. The gap between the selector and naive survives: +$6,544/day over 12 months, 12 of 12. LEV's edge over the threshold shrinks to about a quarter, +$73/day. Once shared liquidity is dropped it is within noise. So LEV is a benchmark result, not a validated edge, and we show it that way." | the evidence cards (robust; LEV) and the counters under strict |
| 2:50–3:00 | — | "MVP: detection and decay with confidence intervals. Stretch: a latency budget and a paper-trading-style replay. Our compute is microseconds; the budget is spent on distance." | the "budget is distance" card: live µs vs feed ms |

Numbers above are for the build in `demo/assets/provenance.json`. The trial-dependent figures (reaction time, ×, %) change with every judge; the page computes them.

## Honest caveats a judge may raise

| question | answer | source |
|---|---|---|
| Is this real P&L? | No. It is *basis-adjusted simulated execution surplus*: IOC legs at observed prices, ≤ 0.05 BTC, inventory assumed pre-positioned, uniform fee levels of 1 and 2 bp per leg. Frozen fills use the last published quote at arrival, which is optimistic. Strict fills use the next published quote, a stress scenario. Neither is calibrated on our own orders. | `README.md`, `eval/results/sensitivity_amendment1.md` |
| Did you cherry-pick the window? | No. The rule is fixed in code (`demo/build_assets.py:window_rule`): the densest 15 minutes of the held-out day by detected-episode count. Full-day counters sit beside the window counters. At δ = 1/5/20 ms they reproduce the committed 2026-10-01 totals exactly: V0 −$2,487.83 / +$1,175.13 / +$1,341.53, V1 −$6,689.92 / −$19.51 / −$26.01. `smoke.sh` asserts this. | `demo/assets/provenance.json`, `eval/results/falsification_walkforward_12d_prereg.json`, `eval/results/sensitivity_amendment1.json` |
| Does LEV beat the threshold? | Pre-registered frozen walk-forward: +$299/day, t-CI [+$130, +$468], 12/12. Strict fills: +$73 [+$10, +$135]. Strict fills with a 1 s markout: +$70 [+$0.2, +$140]. Shared-liquidity collisions dropped: +$40 [−$12, +$92], within noise. A frozen-trained LEV scored strict: −$7.8. **A benchmark result, not a validated edge.** | `eval/results/falsification_walkforward_12d_prereg.md`, `eval/results/sensitivity_amendment1.md` |
| What is robust, then? | Latency-aware selection versus naive: the tuned threshold beats naive by +$2,898/day frozen and +$6,544/day strict, 12/12 months each. Naive's day total turns negative within a few ms of one-way latency: 4.6 ms on 9 legs at 1 bp/leg in `latency_budget.md`, and between 2 and 3 ms on this demo's 5-leg grid. | `eval/results/latency_budget.md`, the frontier panel |
| Your lifetimes are shorter than the venues' publication interval. | Yes. In these samples Binance spot and OKX publish on a 100 ms grid and Binance perp every 26 ms, so shorter lifetimes are unobservable; the clocks shade that floor. Pooled median 90.5 ms (9 legs), bounded to 11.3–147.1 ms by publication times; this window's median is 32.3 ms. Our own recorder sees Binance perp every 2 ms. | `eval/results/decay_report.md`, `update_cadence.md`, `live_cadence.md` |
| What is the order latency? | Assumed equal to the one-way feed latency δ, as in the frontier sweep. Sending orders needs exchange accounts, so it is not measured. | `eval/results/latency_budget.md` |
| Is this a live trading system? | No. The detector ran in batch over recorded quotes; open-time features are causal, so the replay is a paper-trading-style replay. Live paper trading is a stretch goal (C10). | `architecture/components.md` |
| Isn't comparing a human to a machine unfair? | It is a scale illustration, not a claim. The rule is fixed before the trials, the replay runs at 1×, every trial is reported, and display and input lag count. The human's selector is the threshold re-tuned on 09-01 at that latency (nearest 100 ms–2 s grid point). The machine's decision delay is the compiled step's p50 measured live, or the committed 6.08 µs when the backend is off. | `demo/live.py:race` |
| Can we trust laptop timings? | They are in-kernel `mach_absolute_time` on a shared machine, so treat them as upper bounds for a dedicated core. Committed: 6.1 µs p50 / 41.5 µs p99. The live figure varies with load. | `eval/results/decision_timing.md` |
| How are thresholds set at latencies outside the registered three? | Re-tuned per (pair, fee, δ, decision delay) on 2026-09-01 with the committed `rules.fit_threshold`. At δ = 1/5/20 ms they equal the walk-forward's fits (asserted in the build). | `demo/build_assets.py:train_policies` |
| Under strict fills the threshold is negative too. | Yes. With next-quote fills the selective policies are about break-even (threshold −$19.51 on 2026-10-01), while naive loses thousands. The robust result is the gap, not the level. | `eval/results/sensitivity_amendment1.md` |
| Why does LEV's frontier wiggle between 5 and 20 ms? | Its latency input was trained at only three latencies (1/5/20 ms one-way), so between them it interpolates step-wise. That is one more reason it is a benchmark, not a validated edge. | `components/decision/autoresearch/rules.py` |
| Fees? | Uniform 1 and 2 bp per leg, not venue tiers; official fee tables are only partly verified. | `research/notes/fees.md` |

## Files
- `run.sh`: one command; backend plus browser, or offline if there is no venv.
- `smoke.sh` → `smoke.py`: headless assertions.
- `index.html`, `app.js`, `style.css`: the page. No libraries, no CDN.
- `server.py` and `live.py`: the optional backend. Live recompute, the race, and in-kernel timing, all with committed code.
- `build_assets.py`: the deterministic asset builder. Run it once through `eval/run_guarded.sh`; it needs the raw Tardis days.
- `assets/`: what the page and backend read. `provenance.json` holds input md5s, source blob hashes and every reproduction check.
- `make_fallback.py` → `fallback/p6_demo_standalone.html`, plus the screenshots and recording in `fallback/`.
