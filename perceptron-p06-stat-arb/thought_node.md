# Perceptron P6 · Cross-asset statistical arbitrage with latency budgets — Thought Node

> Journal for `perceptron-p06-stat-arb/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- 2026-10-04 17:28 IST (Supervisor 17:28, by message): NEW PHASE — winning demo per PLAYBOOK §11. Spawn one demo builder child session; approve its "crazy" element; verify `demo/run.sh` and `demo/smoke.sh` from a clean checkout; one `gpt-6-astra` (max) demo review; then "DEMO DONE". → acting (see Now/Log).
- 2026-10-04 14:11 (Supervisor, by message): resumed with a 5-point definition of done (walk-forward ≥ 12 pre-registered days, decay CIs + latency budget + compiled timing, final rendered abstract + drift check, cross-model reviews, final memo → "DONE — slot free"). → acting (see Now/Log).
- 2026-10-04 09:55 (Supervisor, by message): pause. → paused at 10:00 with a resume point.
- 2026-10-04 08:22 (Supervisor, by message): "Package accepted. Lean limits from 08:30: ≤2 concurrent sub-agents/child sessions; no downloads over 1 GB without a stated reason; heavy jobs one at a time under `nice -n 10`. Next: run ADR 001's falsification tests (clock skew; whether LEV beats the tuned threshold beyond noise on more held-out days). If it still doesn't separate, say so in the memo." → acting (see Now/Log).

## Now
- **Phase:** ▶ DEMO (PLAYBOOK §11), started 2026-10-04 17:28 IST (Supervisor 17:28, user directive). The evaluation phase is DONE at 378ac26: memo = keep P7, P6 as Theme 3 fallback.
- **Plan:** one child session, the *demo builder*, owns `demo/`.
  1. It proposes the "crazy" element; I approve it.
  2. It builds to the §11 bar: `demo/run.sh` (one command, offline, first visual ≤ 60 s), `demo/SCRIPT.md`, `demo/fallback/`, `demo/smoke.sh`.
  3. I spawn one `gpt-6-astra` (max) "judge watching the demo" review (child session 2 of 2) and decide its dispositions.
  4. I verify run and smoke from a clean checkout, then message the Supervisor "DEMO DONE".
- **Demo core (lead's brief to the builder):**
  - Lead with what is *robust*: on a real cross-venue BTC replay, latency-aware selection stays positive where naive trading turns negative. Threshold − naive is significant under every simulator.
  - LEV vs threshold is shown honestly as modest, with a strict-fills toggle.
  - Decay clock with the cadence floor; live compiled decision timing.
  - Every number comes from committed results or committed code running live on a committed slice.
- **Doing (17:29):** [P6 demo builder](ghapp://sessions/d90f3e4a-6dd4-4baf-8ddd-6a1e15f31123), child 1 of 2, is building. At 17:36 I approved its crazy element **A, "Race the machine"**, with 7 conditions (see Log).
- **Needs from user:** register by 15 Oct (after the 12 Oct selection); teammates' names and skills for the abstract's [TEAM] lines.
- **Risks:**
  - Demo honesty: the LEV gain is fragile, so the demo must not imply a validated edge.
  - Committed-slice size: keep assets ≤ 10 MB.
  - First visual ≤ 60 s despite Numba JIT: the page must render from exported JSON while the backend warms up.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 6 — Cross-Asset Statistical Arbitrage with Latency Budgets** (Theme 3: Markets & Trading Intelligence — teams choose one of Problems 4, 5, 6)
- **Context:** Arbitrage opportunities across correlated instruments exist for only milliseconds before they close.
- **Challenge:** Identify and rank cross-asset mispricings in near real time, trading off signal confidence against acting-on-it latency.
- **Starter resources:** Synthetic paired price series, or public multi-exchange crypto price data for the same asset.
- **Minimum Viable:** detect mispricings using a threshold or statistical model; report how fast the opportunity typically decays.
- **Stretch goals:** simulated end-to-end latency budget; a basic paper-trading demo.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: multi-exchange crypto feeds (exchange websockets, CCXT), spot–perpetual basis, historical tick data vendors.
- Models: cointegration (Engle–Granger, Johansen), Kalman-filter hedge ratios, Ornstein–Uhlenbeck half-life, lead–lag estimation (e.g. Hayashi–Yoshida).
- Decay as survival analysis; a decision rule for the expected value of acting now vs waiting, given latency, fees and confidence; an event-driven backtester with injected latency.
- What practitioners ship: public talks and posts from HFT and market-making firms on latency budgets and signal decay.

## Phase 0 — what the judges must be able to see (criterion → evidence)
| Criterion (weight) | What we must show |
|---|---|
| Problem understanding (20%) | The crux is not *detecting* a price gap — it is that the gap's value is conditional on (i) it being real (not a stale/noisy quote), (ii) it surviving our end-to-end latency, (iii) clearing fees. Confidence costs time; time kills the opportunity. |
| Technical soundness (25%) | Real multi-venue tick data with exchange + receive timestamps; executable (bid/ask, size-limited) edges net of official fees; survival-analysis decay with censoring; event-driven simulator that fills at the book *as it is when our order arrives*. |
| Innovation (20%) | Beyond "threshold on spread": latency-conditioned survival model + confidence → expected-value ranking and an act-now-vs-wait rule; the latency–PnL frontier as the headline evaluation. |
| Clarity (10%) | One diagram, one decision formula, one frontier plot. |
| Evaluation rigour (15%) | Held-out day, fixed seeds, three baselines (naive cross, z-score, oracle upper bound), metrics per component, fee tiers swept, latency swept. |
| Team fit (10%) | Week-by-week plan avoiding the 19–25 Nov exams; skills map (systems, ML, quant). |

**Hard constraints (from `_briefs/perceptron.txt`):** team ≤3, students; one Perceptron problem per team (choose exactly one of P4/P5/P6); original work not protected by patents/publications; Round 1 = 600–900-word abstract + optional 1-page diagram, team leader submits once via techfest.org; register by 15 Oct; abstract 31 Oct; shortlist 10 Nov (25–30 teams overall); 1-page midway report 1 Dec (unscored); finals 15–18 Dec need a working build of the Minimum Viable scope.

## Key decisions
- 2026-10-04 — Data: Tardis.dev free first-of-month samples (quotes; exchange `timestamp` + collector `local_timestamp`) as the reproducible historical set; our own live recording as the "what a laptop in India sees" set. Both real; no synthetic data in the headline numbers.
- 2026-10-04 — Scope tiers: (1) same asset across venues, (2) spot vs perpetual basis, (3) correlated assets (BTC/ETH). Tier 1 is the MVP; tiers 2–3 reuse the same detector/decay/decision contracts.
- 2026-10-04 — **Spike = C8 decision layer** (latency-conditioned executable value LEV + EV/act-or-wait), with C7 survival decay as its interpretable core; the tuned per-pair threshold is the bar to beat. See [ADR 001](architecture/adr/001-spike.md).
- 2026-10-04 — Simulator semantics: decide on receive-time state, fill each leg on exchange-time truth at `t_decide + L_order[venue]`; IOC legs, top-of-book size, same-venue unwind of mismatches; inventory pre-positioned (labelled assumption).
- 2026-10-04 — Headline P&L uses uniform taker-fee levels (0/1/2/5 bps per leg), not unverified venue tiers; official tiers are cited only where `research/notes/fees.md` verified them.

- 2026-10-04 — **Final evaluation stance:** the pre-registered walk-forward is primary (+$299/day, [+$130, +$468]). Amendment 1's stricter simulators are reported beside it: +$70/day under strict fills and a 1 s markout; +$40/day after dropping shared-liquidity collisions. The frozen metric is renamed *basis-adjusted simulated execution surplus*. See the ADR 001 status.
- 2026-10-04 — Amendment 1 run 1 went to my own short-lived Azure D16s_v5 (Japan East), because the shared Mac sat at load average 73. Data md5 was verified and the VM deleted. The corrected run 2 ran on the Mac; the registered quantities agree across the two machines to within 7e-13 (floating-point round-off).
- 2026-10-04 — **Selection recommendation: keep P7, with P6 as the Theme 3 fallback** (see memo).

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | `feed` | Tardis CSV / raw ws frames → QuoteFrame | Tardis normalised quotes | no | built (Tardis + 10 live parsers) | parse coverage, monotonicity |
| C2 | `latency` | QuoteFrame → per-venue latency quantiles | constant latency | no | built (Tardis collector + Mac-India tables) | pinball loss |
| C3 | `book` | QuoteFrame → as-of state + quote ages | as-of join | no | inlined in the C6 numba loop | events/s, look-ahead test |
| C4 | `fair_value` | state → fair basis, lead–lag | EWMA basis (60 s) | next upgrade | EWMA inlined; Kalman/HY pending | OOS RMSE of 100 ms mid-diff |
| C5 | `costs` | venue, tier → bps | uniform fee levels + official tables | no | built; fees partly verified | unit tests vs fee tables |
| C6 | `detector` | state + basis → OpportunityFrame | threshold over fair basis | no | built; 345,890 episodes on held-out day | AUC-PR at latency L |
| C7 | `decay` | episodes → S(t\|x), half-lives | Kaplan–Meier | MVP report + baseline | KM by pair with hour-block CIs and publication-time bounds; survival EV trails the threshold | IBS, C-index, median CI |
| C8 | `decision` | opportunity + S + L → order intents | naive · tuned threshold | **SPIKE** | LEV: pre-registered, passed; fragile under strict simulators; Numba-compiled (exact) | simulated execution surplus at (L, fee) |
| C9 | `sim` | intents + exchange-time truth → fills, P&L | zero-latency backtest | no | frozen (optimistic) + strict (next quote, markout, collisions, end-of-data censoring) | determinism, fill-rule tests |
| C10 | `paper` | live feed → same path → dashboard | — | stretch | recorder live; loop pending | live-vs-sim divergence |
| C11 | `eval` | everything → reports, frontier | — | — | `eval.run_baseline`, `eval.plots`, `eval.live_latency` | latency–P&L frontier |

## Selection memo
_Final version, 2026-10-04 15:39 IST. Scores are 1–5, each with evidence. Every number is checked by `eval/check_docs.py` against `eval/results/headline.json` or `deliverables/static_numbers.tsv`._

**Recommendation: keep P7 as the team's Perceptron pick, and hold P6 as the Theme 3 fallback.** P6 is the most rigorously evaluated build in Theme 3; P4 and P5 recommend against themselves. But its spike's measured edge does not survive realistic execution with confidence, and P7's evidence is stronger.

- **Winnability — 3.** For:
  - pre-registered evidence on real exchange ticks;
  - independent reproduction twice: all comparison fields by the `gpt-6-sol` reviewer, and the registered decision quantities equal to within 7e-13 on Azure x86 and the Mac;
  - published negative results and stated observability limits.

  Against: the hostile judge scored the final abstract 62/100, up from 53/100 for the plan (P7's final abstract scored 71/100), and the headline weakens under scrutiny (below).
- **Innovation headroom — 2.**
  - With the frozen simulator, LEV beat a tuned per-pair threshold in 12/12 months: +$299/day, t-CI [+$130, +$468]. In the 7 never-inspected months it was 7/7.
  - Under the registered stricter simulators it is +$73/day with next-quote fills (24% of the frozen gain) and +$70/day, t-CI [+$0.2, +$140], adding a 1 s markout (23%).
  - Dropping intents that reuse displayed liquidity leaves +$40/day, t-CI [−$12, +$92], within noise.
  - A LEV trained on optimistic fills has no established advantage over the threshold under strict fills (−$7.8/day).
  - The latency input mattered under optimistic fills (+$477/day) but much less under strict ones (+$40/day; with the GBM-classifier comparison, neither significant).

  What remains novel is the method: a falsification-first latency-decision benchmark that shows where public quote data stops resolving the answer.
- **Feasibility by the deadline — 5.** MVP and both stretch simulators run. The full sensitivity suite takes 5 minutes on a 16-core VM. The compiled decision step is 6.1 µs at p50 and 41.5 µs at p99 on the shared laptop, so the ≤ 10 µs target holds at p50 only. Work fits around the 19–25 Nov exams.
- **Demo strength — 4.**
  - Live 12-venue recorder.
  - Decay with confidence intervals and publication-time bounds: median 90.5 ms, bounded to 11.3–147.1 ms.
  - Latency budget: compute in microseconds against distance in milliseconds; naive trading stops paying at 4.6 ms one-way.
  - Weak point: "LEV beats the threshold" needs every caveat above.
- **Fit with the user's strengths — 4.** Latency and systems engineering, rigorous ML evaluation, Azure for vantage-point capture.
- **P6 vs P7 (current consensus pick).**
  - *Evidence:* P7's primary claim is decisive and pre-registered (6/6 scenarios on 30/30 fresh seeds, per its memo), and its final abstract scored 71/100 with a hostile judge. P6's primary passes, but only 24% survives strict fills, and it is within noise once shared liquidity is dropped. **P7 wins on evidence.**
  - *Novelty:* both are narrow. P7's headline (MPC beats rules) is known, but it adds a counter-intuitive pre-registered finding (better forecasts can serve fewer people). P6's LEV is applied integration; its novelty is the benchmark and the observability limits. Roughly even, with P7 more memorable.
  - *Sponsor fit:* P6 sits on Optiver's home ground with real exchange data, its one clear edge.
  - *Risk:* P6's core claim can be dismantled with an execution-model question; P7's spike (forecast trust) is still a plan.
  - **Net: P7 first, P6 second.**
- **Biggest risk:** public replay cannot pin down LEV's value — from within noise to +$299/day depending on execution assumptions. Settling it needs tick-by-tick capture near the exchanges plus live paper fills before 15–18 Dec.
- **One-line pitch:** "We measure what a crypto mispricing is worth when our order lands — and exactly where public data stops being able to tell."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05–05:10 IST — Phase 0 + data + research fan-out (lead)
- Read PLAYBOOK, brief, official statement; criterion → evidence map above. Branch renamed.
- Env: `uv` venv in `perceptron-p06-stat-arb/.venv` (numpy 2.4.6, polars 1.44.2, lifelines 0.30.0, websockets 17.2, numba 0.68.0). Azure CLI logged in (Visual Studio Enterprise subscription) — not needed yet.
- Tardis free samples verified: `datasets.tardis.dev/v1/<ex>/quotes/2026/09/01/<sym>.csv.gz` returns 200 without an API key (a Range header gives 403). 2026-09-01 sizes: binance 9.3 MB, coinbase 31.2 MB, okex 5.7 MB, okex-swap 9.8 MB, bybit 16.4 MB, kraken (`BTC-USD`) 13.6 MB, bitstamp 2.4 MB, deribit 6.9 MB. `kraken XBT-USD` → 400.
- Live recorder `components/feed/live_recorder.py` (raw frames + `time.time_ns()` receive stamp, hourly gz rotation, reconnects, app-level pings, `sntp` offset log). First `sntp` reading: +0.026 s ± 0.114 s vs time.apple.com.
- Research: 5 background agents launched 02:20. `papers-microstructure` and `companies-ship-today` wrote their notes (`research/notes/`) and then died on model-API 408 upload timeouts; `data-fees-code` died with nothing written. Measured link: ~200 KB/s download, 39 ms RTT to 1.1.1.1 → recorder switched to a BBO-only, bandwidth-light config.

### 2026-10-04 05:10–07:20 IST — Components, skeleton, real baseline, first ratchet, deliverables (lead)
- **Architecture:** `architecture/components.md` (11 components, mermaid graph, contracts, isolated metrics) + `architecture/contracts/` (pydantic row models, polars frame schemas).
- **Research:** `research/notes/` {papers-microstructure, papers-methods, companies, social, fees}; `research/components/` (11 files, by 4 scoped agents); `research/landscape.md` compiled from the notes (no new claims). The `first-principles` agent disappeared without output (not retried).
- **Skeleton:** `components/` feed · latency · detector (numba, EWMA fair basis inlined) · decay (KM, KM-by-pair, Weibull AFT) · decision (naive, threshold, per-pair threshold, EV, EV+wait, LEV) · sim (latency-injected IOC fills on exchange-time truth). `components/test_contracts.py`: 4/4 pass (`.venv/bin/python -m pytest -q components/test_contracts.py`).
- **Held-out baseline** (`.venv/bin/python -m eval.run_baseline --train 2026-09-01 --test 2026-10-01 --legs …` — exact command in `eval/results/baseline_0901_to_1001.md`, commit 4d21a39, 319 s):
  - **Decay (MVP):** 345,890 episodes ≥1 bps over the fair basis on 2026-10-01 across 9 BTC legs. KM median lifetime 90.5 ms; S(1 ms) 0.965, S(10 ms) 0.822, S(100 ms) 0.485; 10% die within 3.85 ms; by group: perp–perp 46 ms, spot–perp 105 ms, spot–spot 95 ms; Deribit pairs 200–257 ms. Mean edge ratio 0.743 after 100 ms and 0.476 after 500 ms. Weibull ρ = 0.431.
  - **Survival models:** IBS (log-t): KM 0.1260, Weibull AFT 0.1273 (C 0.529), KM-by-pair **0.1090** (C 0.625).
  - **Frontier at 1 bp/leg** (USD, 0.05 BTC cap, simulated):

    | Policy | δ = 1 ms | δ = 10 ms | δ = 100 ms |
    |---|---|---|---|
    | naive | +1,490 | −1,570 | −4,433 |
    | tuned per-pair threshold | +1,977 | +768 | +30 |
    | EV (KM by pair) | +1,990 | +672 | −95 |
    | LEV | +1,926 | +802 | −33 |

  - **Ranking (f1):** Spearman with realised P&L: raw edge 0.834 → 0.051 (δ 0.5 → 50 ms); LEV 0.822 → 0.408. Top-decile bps at 50 ms: edge 0.04, EV 0.53, LEV 0.89.
  - **Caveat:** the "oracle" is naive at zero latency, not an upper bound. Selective policies can exceed it because the zero-latency naive still loses on ms-granular timestamp ties.
- **Latency:** Tardis collector median feed latency on 2026-10-01: binance-futures 1.83 ms, binance 2.45, okex 4.45, okex-swap 4.76, kraken 7.51, deribit 8.73, bitstamp 34.0, bybit 37.2, coinbase 39.7 ms. Mac-India live (`eval/results/live_latency.md`, ~1.3 h): p05 69–107 ms for binance-futures/coinbase/kraken/deribit. Medians are seconds because of local congestion (bufferbloat), so they're not representative. Bybit shows 29% negative latencies (timestamp semantics) and is flagged.
- **Ratchet v1** (`components/decision/autoresearch/`, frozen `eval.py`, `results.tsv`): 9 hypotheses on the 09-01 train/val halves. Kept H0 per-pair×cell threshold ($689 val). GBM classifier +$97 and GBM regressor (LEV) +$99 were not kept because they fall within the bootstrap SE (~$150). Holdout 2026-10-01 re-check: $1,175 (H0).
- **Antithesis** (rubber-duck): survival ≠ executable profit, λ heterogeneous, cross-venue clock skew, one day ≠ robustness; proposed direct executable-markout model. Adopted as the synthesis in ADR 001, with three falsification tests.
- **Deliverables:** `deliverables/round1-abstract.md` (~890 words, [TEAM] placeholders), `deliverables/architecture.md` (mermaid + metric table), `architecture/adr/001-spike.md`, selection memo v1 above; figure `eval/results/baseline_0901_to_1001_frontier.png`.
- **Self fact-check:** my own numbers checked against the results files before pushing. One error fixed: the Mac-India p05 range is 69–107 ms (Deribit 69.4), not 75–110.

### 2026-10-04 07:25–07:40 IST — Supervisor sync, fact-check, README (lead)
- Messaged the Supervisor that the selection memo gate is ready, with a cross-project warning that the saturated uplink killed agents with 408 errors. The Supervisor's 07:22 alignment note (write ADR, abstract, architecture, memo, Now/Log) crossed with my 07:25 push, which already contained all of them, so no reply was needed.
- Independent fact-check (`research` agent) of 8 load-bearing landscape claims: 3 PASS, 5 PARTIAL, 0 FAIL. Fixes applied in `research/landscape.md` and `research/notes/fees.md`: Hyperliquid top-tier maker is 0.0000% (−0.002% is a separate rebate table); Aquilina et al. URL added; arXiv 1812.00595 authors named; per-route AWS/Avelacom numbers marked as not re-verified. A verdict table is appended to the landscape.
- Added `README.md` with reproduce commands.

### 2026-10-04 08:25–10:00 IST — ADR 001 falsification tests (Supervisor 08:22), then paused (09:55)
- **Test 3, clock skew + receive-time replay** (`eval/results/falsification_clockskew.md`; train 09-01 → test 10-01, 5 BTC legs, 6 fee×latency cells, 1 h run). Pair half-life rankings were stable: Spearman ≥ 0.984 against the exchange clock under receive-time detection and three seeds of per-venue ±5 ms offsets. LEV − threshold stayed positive in all 5 variants (+$106 … +$261). The survival-EV rule failed under receive-time replay (−$415 against the threshold's +$442). **Passed for LEV; failed for survival-EV as a decision rule.**
- **Test 1, walk-forward** (`eval/results/falsification_walkforward.md`; commit f8cb48f, 202 s with cached cells). LEV beat the tuned per-pair threshold on 4/4 test days (07-01 +$650, 08-01 +$43, 09-01 +$132, 10-01 +$166), mean +$248/day. Bootstrap CI [+$74, +$520], but t-CI [−$187, +$682] and sign p = 0.062. **Not established at n = 4** by the stricter criterion. Threshold vs naive is significant (+$3,555/day, t-CI excludes 0).
- **Test 2, partial ablation:** LEV with full features beat LEV with edge/pair/latency only on 4/4 days (+$209/day; same significance caveat).
- **Downloads:** 2026-05…08 first-of-month days for 5 legs (321 MB), within the 08:30 limit. When the Supervisor re-imposed a 200 MB cap at 09:40, the fetch had already been killed by a session restart; only May's last 3 files (69 MB) were fetched after that. Further days are deferred.
- **Paused** at 09:55 per the Supervisor (user decision). Nothing running; resume point under *Now*.

### 2026-10-04 14:13–14:31 IST — Resumed: data, pre-registration, compiled step, docs pipeline, reviewers (lead)
- **Data:** 7 more first-of-month days (2025-10 … 2026-04) for the 5 walk-forward legs, fetched sequentially and alone (`fetch_tardis.py --set wf5`). The ~0.83 GB took about 2 minutes; the uplink was free. All 13 days pass the gzip integrity check. A manifest of sizes and md5 is in `eval/results/data_manifest_wf12.tsv`. Interpretation recorded: "run downloads alone" = one download stream, no parallel fetchers.
- **Exploratory 5-day walk-forward** (May → Jun…Oct; commit 4947f65, 113 s): LEV − tuned threshold +$237.5/day, 5/5 days positive, sign p = 0.031. The t-CI [−$57.5, +$532.5] includes 0, so it is not significant by the stricter rule. My own `git mv` mix-up overwrote the output file; it is being regenerated deterministically as `falsification_walkforward_5d` (queued). The 4-day file is preserved as `_4d`.
- **Pre-registered** the final test at 14:24 IST (commit 0ca23e8; code 604f54d; blob hashes and data md5s in the file): `eval/PREREGISTRATION-walkforward-12d.md`. 12 test days. Supported iff both the 95% t-CI and bootstrap lower bounds are > 0. The 7 test days never examined before (2025-11 … 2026-05) are reported as a subset.
- **Compiled decision step:** `components/decision/compiled.py` flattens the sklearn LEV into Numba. sklearn 1.9 wraps HGB in a ColumnTransformer that moves categoricals first and ordinal-encodes them; this is now handled. `test_compiled.py` gives an exact match (< 1e-9), including unseen categories.
- **Data resolution finding** (`eval/results/update_cadence.md`, 2026-10-01): Binance spot and OKX spot/swap quotes are on a 100 ms grid (99.6–100% of gaps), Binance perp every 26.0 ms (minimum 26 ms), Bybit at a 39 ms median and Bitstamp at 328 ms. Coinbase (3.3 ms) and Kraken (12.8 ms) are fine-grained. So decay below a venue's cadence is not resolvable, and absolute P&L at 1–5 ms is optimistic. Policy comparisons remain like-for-like. This confirms the antithesis's resolution point; the caveat is now in the decay report and the abstract.
- **Docs pipeline:** `eval/headline.py` → `eval/results/headline.json` → `deliverables/render.py` (abstract and architecture rendered from templates) → `eval/check_docs.py` (re-render diff, numeric-token tracing against headline values or `deliverables/static_numbers.tsv`, 600–900 words). Dry-run: 875 words.
- **Machine rules:** `eval/run_guarded.sh` waits for `kern.memorystatus_level` ≥ 30, sends SIGSTOP below 25, resumes at ≥ 30, and runs under nice 10. Memory sat at 24–28 for most of this window (other projects), so heavy jobs are queued, not running.

### 2026-10-04 14:35–15:39 IST — Pre-registered result, reviews, Amendment 1 (Azure + Mac), final deliverables (lead)
- **Pre-registered 12-day walk-forward** (results commit 340d4df; run at 9cadff6, frozen files byte-identical to registration code 604f54d): LEV − tuned threshold +$299/day, 12/12, t-CI [+$130, +$468], bootstrap [+$165, +$451]. **Supported.** Unseen-7: 7/7, +$343/day, [+$70, +$616]. Survival EV trails the threshold (−$77/day).
- **Determinism and reproduction:**
  - The 6 rebuilt cache days are byte-identical, and the regenerated 5-day run matches.
  - `gpt-6-sol` reproduced all 91 fields and rebuilt Feb from raw data.
  - Amendment 1 on Azure x86 vs the Mac arm64: all registered quantities identical; only the GBM classifier's fit varies on one V3 day (`eval/results/sensitivity_amendment1.provenance.md`).
- **Reviews:**
  - `gpt-6-astra` TASK 1 gave 53/100 and 13 findings, all accepted (some partly); see `reviews/2026-10-04-dispositions.md`.
  - `gpt-6-sol` TASK A gave 7 items, all accepted. It then found post-end quote reuse in `strict.py`, fixed by the registered erratum (0 rows affected), and asked for softer V4 wording (accepted). It withdrew its collision-rule point after re-reading the registration.
- **Amendment 1** (registered 14:46 before implementation; erratum 15:19 before the corrected run):
  - V1 strict fills: +$73/day, [+$10, +$135].
  - V2 strict fills + 1 s markout: +$70/day, [+$0.2, +$140]. **The registered rule passes, but at 24% of the frozen gain.**
  - S3 collision-dropped: +$40/day, [−$12, +$92], within noise.
  - V4 transfer: −$7.8/day, [−$148, +$132]; no established advantage.
  - Exploratory: LEV − GBM classifier +$98/day frozen vs −$0.3/day strict+markout. LEV − no-latency-input +$477/day vs +$40/day.
- **Decay with publication-time bounds** (Supervisor 14:41): median 90.5 ms (hour-block CI 84.0–100.0), bounded to 11.3–147.1 ms. Monthly 5-market medians range 26–68 ms.
- **Reaction time:** compiled decision step 6.1 µs at p50, 41.5 µs at p99; detector 87 ns per event.
- **Deliverables:** abstract and architecture page rendered from `headline.json`; `eval/check_docs.py` passes. **Memo final: keep P7, with P6 as the Theme 3 fallback** (Supervisor 15:29 asked for an explicit comparison with P7).

### 2026-10-04 15:40–15:52 IST — Final review round, corrections, DONE (lead)
- **`gpt-6-sol` final review** (16 items, all accepted). It reproduced the 91 primary fields and the Feb raw rebuild byte-identically; `headline.json` regenerates identically; `check_docs` passes.
  - It corrected my "bit-identical" cross-platform claim: the figures agree to within 6.8e-13, not bit for bit. Fixed in the thought node and provenance note.
  - Scope notes appended: `falsification_clockskew.md` (skew = rephased market, P6-C06) and `baseline_0901_to_1001.md` ("oracle" = naive at zero latency, P6-C13).
  - `decay_report` now fails loudly on missing days (P6-C11).
- **`gpt-6-astra` final abstract review: 62/100** (up from 53; 8 items, all accepted). Wording fixes:
  - sensitivity range, not bound;
  - next-quote fills are a stress scenario;
  - paper trading is planned;
  - legacy top-decile claim removed;
  - uncalibrated laptop latency removed;
  - pooled collision share 22%;
  - exact clipping statement.

  The architecture page was regenerated to match the evaluated system.
- **New evidence for the finals fix** (`eval/results/live_cadence.md`): our recorder's channels publish Binance perpetual every 2 ms (median) versus 26 ms in the Tardis samples, and OKX every 20–30 ms versus 100 ms. Coinbase's live `ticker` is coarser than Tardis level-2 quotes.
- **Records:** `reviews/2026-10-04-dispositions.md` (37 items: 13 + 16 + 8) and `reviews/ledger.tsv` (3 lines). The abstract, at 897 words, passes `check_docs`.

### 2026-10-04 17:27–17:29 IST — Demo phase kickoff (lead)
- The Supervisor's 17:28 message (user directive, PLAYBOOK §11) moved P6 into the demo phase.
- Spawned [P6 demo builder](ghapp://sessions/d90f3e4a-6dd4-4baf-8ddd-6a1e15f31123) with the runtime-default model. It owns `demo/` and reads the lead's `.data`/`.cache` via read-only symlinks.
- Lead's brief to the builder:
  - Lead the demo with the robust result: latency-aware selection vs naive trading under latency.
  - Show LEV vs threshold honestly, with a strict-fills toggle.
  - Architecture: offline HTML fed by exported JSON (which doubles as the fallback), plus a Python backend only for live recompute and live Numba timing.
  - Committed slice: 10–20 minutes of 2026-10-01 for the 5 walk-forward legs, using the walk-forward's own LEV model (trained on 2026-09-01).
  - Candidate crazy element: "race the machine" (the judge's measured reaction time fed into the committed simulator); the builder proposes and I approve.
- **17:36 — Crazy element approved: A, "Race the machine".**
  - The judge does 5 reaction trials on real 2026-10-01 mispricings, each scored by the committed simulator with RT in place of compute. Then a one-way latency knob (10 µs → 100 ms), a fee 1/2 bp switch and a frozen/strict toggle drive naive / threshold / LEV counters for the live window and for the full held-out day (exported grid).
  - Conditions:
    1. 1× replay during trials;
    2. a fixed flash rule, with all trials reported;
    3. a 2×2 {judge RT, machine} × {naive, selector}, with machine latency from live-measured compiled timing;
    4. strict = V1 world, with the day grid at δ = 1/5/20 asserted by smoke against the committed walk-forward (V0) and Amendment 1 (V1) 2026-10-01 totals;
    5. window chosen by a stated rule;
    6. LEV hatched outside its trained L range;
    7. option B (bullet time) only after the §11 bar is green.
- **18:37–19:08 — Demo ready for review, verified, reviewed.**
  - The builder reported READY FOR REVIEW at d170f52 (window 13:37–13:52 UTC = densest 15 minutes on 2026-10-01; smoke 18/18).
  - **My clean-checkout check** (fresh clone, no `.data`/`.cache`, venv from the lock): smoke **18/18 in 104 s**. Day grid at δ = 1/5/20 equals the committed 2026-10-01 V0 and V1 totals; live recompute equals the exported grid; compiled LEV equals sklearn exactly. `run.sh`: first visual **0.7 s**, live **16.7 s**.
  - **`gpt-6-astra` demo review** (child 2 of 2, f8addd0): wow 3, clarity 2, honesty 3, robustness 3, fit 5. All 10 findings accepted (dispositions + ledger), plus one of mine: the two naive break-even figures come from different leg sets.
  - Fix list sent to the builder in priority order: race length; race setup snapshot; copy pass (6-scenario denominator, 5 inspected days, sensitivity-not-bound, uncalibrated laptop timestamps, abstention caption, offline ratio); live-state consistency; 3-step stage view.
