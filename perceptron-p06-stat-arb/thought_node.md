# Perceptron P6 · Cross-asset statistical arbitrage with latency budgets — Thought Node

> Journal for `perceptron-p06-stat-arb/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** morning package complete (Phases 0–5 v1; fact-checked). Next: Phase 3/5 depth — multi-day walk-forward and falsification tests. Updated 07:40 IST.
- **Plan (to 12 Oct selection):** (1) download ≥12 Tardis first-of-month days (2025-10 … 2026-10) and run the walk-forward; (2) receive-time replay + ±5 ms clock-offset perturbation; (3) residual survival S(a+L)/S(a) and downside-quantile LEV; (4) compiled/linear LEV path (≤10 µs); (5) tier-3 BTC/ETH lead–lag; (6) paper-trading loop on the live recorder; (7) re-measure latency from Azure regions.
- **Doing:** nothing running except the live recorder (`shellId recorder`, ends ≈08:17 IST on its own).
- **Next:** walk-forward data fetch → falsification test 1 (walk-forward superiority) → selection memo v2.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the abstract's [TEAM] lines.
- **Risks:** (a) the spike's gain over a tuned per-pair threshold is still within noise (+14%, < 1 SE); (b) cross-venue exchange clocks aren't a common clock, and Tardis binance-spot quotes are ~100 ms granular; (c) one held-out day so far; (d) Tonight's live latency medians are inflated by local congestion (seconds), so only p05 is used as a path-latency floor; (e) fee schedules are only partly verified, so headline results use uniform fee levels 0/1/2/5 bps.

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

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | `feed` | Tardis CSV / raw ws frames → QuoteFrame | Tardis normalised quotes | no | built (Tardis + 10 live parsers) | parse coverage, monotonicity |
| C2 | `latency` | QuoteFrame → per-venue latency quantiles | constant latency | no | built (Tardis collector + Mac-India tables) | pinball loss |
| C3 | `book` | QuoteFrame → as-of state + quote ages | as-of join | no | inlined in the C6 numba loop | events/s, look-ahead test |
| C4 | `fair_value` | state → fair basis, lead–lag | EWMA basis (60 s) | next upgrade | EWMA inlined; Kalman/HY pending | OOS RMSE of 100 ms mid-diff |
| C5 | `costs` | venue, tier → bps | uniform fee levels + official tables | no | built; fees partly verified | unit tests vs fee tables |
| C6 | `detector` | state + basis → OpportunityFrame | threshold over fair basis | no | built; 345,890 episodes on held-out day | AUC-PR at latency L |
| C7 | `decay` | episodes → S(t\|x), half-lives | Kaplan–Meier | core of spike | KM, KM-by-pair (IBS 0.109), Weibull AFT | IBS, C-index |
| C8 | `decision` | opportunity + S + L → order intents | naive · tuned threshold | **SPIKE** | naive, threshold(+pair), EV, EV+wait, LEV; ratchet v1 | simulated P&L at (L, fee) |
| C9 | `sim` | intents + exchange-time truth → fills, P&L | zero-latency backtest | no | built; contract tests pass | determinism, fill-rule tests |
| C10 | `paper` | live feed → same path → dashboard | — | stretch | recorder live; loop pending | live-vs-sim divergence |
| C11 | `eval` | everything → reports, frontier | — | — | `eval.run_baseline`, `eval.plots`, `eval.live_latency` | latency–P&L frontier |

## Selection memo
_First version 2026-10-04 07:20 IST; final by 12 Oct. Scores 1–5 with evidence._
- **Winnability — 3/5.** Real multi-venue tick data, a held-out day, honest frontier plots and an end-to-end build already exist, which most abstracts won't have. But Theme 3 is crowded (P4/P5/P6) and Optiver judges are domain experts, so the bar is high.
- **Innovation headroom — 3/5.** The spike ranks by value at arrival, not visible gap. It is clearly better *at ranking* under latency: at 50 ms and 1 bp/leg, the top decile by LEV earned +0.89 bp/trade vs +0.04 bp by raw edge. It is not yet significantly better *in P&L* than a tuned per-pair threshold (+14% on validation, < 1 bootstrap SE). Headroom: residual survival, downside quantiles, lead–lag features, vantage choice.
- **Feasibility by the deadline — 5/5.** MVP done tonight on an M5 (9-venue day in ~5 min). Remaining work is rigor and engineering, and fits around the 19–25 Nov exams.
- **Demo strength — 4/5.** Live 12-venue feed, live decay curves, latency–P&L frontier, paper trading on the same code path.
- **Fit with the user's strengths — 4/5.** Latency/systems engineering plus ML evaluation, and Azure regions for vantage-point experiments. Less "frontier-model" heavy than other Perceptron problems.
- **Biggest risk:** the spike may never beat a well-tuned threshold beyond noise; clock-skew artefacts at millisecond scale could also undermine decay claims. Both are testable (ADR 001's falsification tests).
- **One-line pitch:** "Every mispricing has a price tag in milliseconds — we rank cross-venue crypto mispricings by what they'll be worth when our order lands, not what they show now."

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
