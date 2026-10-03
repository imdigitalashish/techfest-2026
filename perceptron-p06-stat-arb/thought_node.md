# Perceptron P6 · Cross-asset statistical arbitrage with latency budgets — Thought Node

> Journal for `perceptron-p06-stat-arb/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 0 done → 1 (research) + 2 (components) + 4 (skeleton) in parallel. Updated 05:10 IST.
- **Plan (to 08:30):** (1) data: Tardis free samples 2026-09-01 (train) + 2026-10-01 (held-out) for 9 BTC venues + 2 ETH perps; live BBO recorder (12 venues, from this Mac in India, measured feed latency) running 05:05→08:17. (2) components + typed contracts. (3) walking skeleton: normalise → as-of consolidated book → detector → decay (Kaplan–Meier half-lives) → latency-injected simulator → policies (naive threshold · z-score · latency-aware EV) → eval with real numbers. (4) first ratchet loop on the decision spike. (5) abstract + architecture + ADR + selection memo.
- **Doing:** lead builds skeleton + architecture; recorder (`shellId recorder`); Tardis fetch (`shellId tardis`); research agents `papers-methods`, `social-signal` still running.
- **Next:** contracts → normaliser → decay report → simulator → eval → ratchet → deliverables.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** (a) the shared uplink is saturated (~200 KB/s down; 3 of 5 research agents died on model-API 408 timeouts after 1.5–2.5 h) → fewer, smaller agents; lead writes the critical path. (b) Fee tiers dominate cross-venue edges for retail; must show results across fee tiers, not one. (c) Exchange timestamps differ in semantics per venue (event vs match time; some have none) → latency numbers must name the timestamp used. (d) Mac clock offset vs NTP (logged every 10 min) bounds feed-latency accuracy.

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

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (a team can submit only one of the 10 Perceptron problems; the Supervisor ranks all 10 from these memos). Score each 1–5 with one line of evidence._
- **Winnability:**
- **Innovation headroom** (the spike, and why it beats the obvious baseline):
- **Feasibility by the deadline** on an M5 Mac (+ Azure), around the 19–25 Nov exams:
- **Demo strength** at the finals:
- **Fit with the user's strengths** (large-scale systems, frontier models):
- **Biggest risk:**
- **One-line pitch:**

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05–05:10 IST — Phase 0 + data + research fan-out (lead)
- Read PLAYBOOK, brief, official statement; criterion → evidence map above. Branch renamed.
- Env: `uv` venv in `perceptron-p06-stat-arb/.venv` (numpy 2.4.6, polars 1.44.2, lifelines 0.30.0, websockets 17.2, numba 0.68.0). Azure CLI logged in (Visual Studio Enterprise subscription) — not needed yet.
- Tardis free samples verified: `datasets.tardis.dev/v1/<ex>/quotes/2026/09/01/<sym>.csv.gz` returns 200 without an API key (a Range header gives 403). 2026-09-01 sizes: binance 9.3 MB, coinbase 31.2 MB, okex 5.7 MB, okex-swap 9.8 MB, bybit 16.4 MB, kraken (`BTC-USD`) 13.6 MB, bitstamp 2.4 MB, deribit 6.9 MB. `kraken XBT-USD` → 400.
- Live recorder `components/feed/live_recorder.py` (raw frames + `time.time_ns()` receive stamp, hourly gz rotation, reconnects, app-level pings, `sntp` offset log). First `sntp` reading: +0.026 s ± 0.114 s vs time.apple.com.
- Research: 5 background agents launched 02:20. `papers-microstructure` and `companies-ship-today` wrote their notes (`research/notes/`) and then died on model-API 408 upload timeouts; `data-fees-code` died with nothing written. Measured link: ~200 KB/s download, 39 ms RTT to 1.1.1.1 → recorder switched to a BBO-only, bandwidth-light config.
