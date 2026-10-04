# Perceptron P4 · Order-book forecasting under regime shifts — Thought Node

> Journal for `perceptron-p04-lob-regimes/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 4 (walking skeleton + real baseline numbers done) → writing the morning package (LEAN MODE per Supervisor 05:50: no sub-agents, small requests, no big downloads).
- **Plan:** "Invariance first, calibrated detection second, cheap adaptation third." Causal microstructure features (depth-normalised OFI etc.) → EWMA normaliser → logistic heads per volatility regime + online heads, mixed by Fixed-Share → rolling-KS (MV) with a *calibrated* null + loss-based harm test → latency-budgeted online loop. Spikes: C6 shift monitor (calibration + harm-awareness) and C7 regime-adaptive head mixer (ADR 001).
- **Doing (lead, solo):** landscape.md → components.md + contracts → ADR 001 → selection memo → round-1 abstract + architecture.md → first autoresearch loop on C6.
- **Next:** (1) calibrated-KS detector + autoresearch ledger; (2) download remaining first-of-month days after 08:30 (trades too) for a larger holdout; (3) GBDT / small DeepLOB-style head behind the same contract; (4) Numba/C++ step for the latency stretch goal.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** (a) Edge is small (AUC 0.62–0.67, 10 s horizon) — the story must be *robustness/adaptation*, not alpha; (b) naive rolling KS fires at its cooldown cap (48/day) on HF data — must calibrate or it looks naive to Optiver; (c) only 8 days on disk (network) — conclusions provisional until the holdout grows; (d) NFP dates unverified (bls.gov blocks scripts).

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 4 — Order Book Forecasting Under Regime Shifts** (Theme 3: Markets & Trading Intelligence — teams choose one of Problems 4, 5, 6)
- **Context:** Limit order book dynamics change abruptly around macro announcements, volatility spikes, and liquidity shocks. Models trained on one regime often degrade silently when the regime changes.
- **Challenge:** Build a short-horizon LOB forecasting model that detects when the data distribution has shifted and adapts, instead of silently degrading.
- **Starter resources:** Public LOB datasets (e.g. LOBSTER sample data, or crypto exchange order-book data via exchange APIs).
- **Minimum Viable:** predict short-term price direction or spread from order book features; detect at least one distribution shift using a simple statistical test (e.g. rolling KS test) and show the model reacting to it.
- **Stretch goals:** multiple regime-adaptive prediction heads; latency benchmarking under a defined budget.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: FI-2010, LOBSTER samples, crypto L2 depth via exchange websockets (Binance, Bybit, OKX) and historical vendors (e.g. Tardis.dev).
- Models: DeepLOB, TransLOB, the LOBCAST benchmark; order-flow imbalance (OFI) features.
- Shift detection and adaptation: rolling KS, ADWIN, Page-Hinkley, CUSUM, Bayesian online changepoint detection; HMM regimes, gated mixture-of-experts; online learning (River).
- Optiver judges will probe realism: look-ahead leakage, latency, transaction costs. Check what trading firms say publicly in tech talks and blogs.

## Key decisions
- 2026-10-04 — **Data:** Tardis.dev binance-futures BTCUSDT `book_snapshot_5`, free first-of-month days (other days 401 — verified). MD5s in `data/manifest.csv`. Scheduled FOMC days (2023-11-01, 2024-05-01 in eval; 2023-02-01 in train) are the natural experiments; times verified at federalreserve.gov (`data/events.csv`).
- 2026-10-04 — **Clock:** receive time (`local_timestamp`) for every as-of join and label; 1 s decision grid; 10 s horizon; raw (unsmoothed) direction label, ties excluded; label usable only at t+h (enforced + tested).
- 2026-10-04 — **Split (frozen, `eval/config.py`):** train 2023-02-01, 2023-08-01 · dev 2023-09-01, 2023-11-01, 2023-12-01 · holdout 2024-05-01, 2024-11-01, 2025-08-01.
- 2026-10-04 — **Primary metric:** prequential log-loss (proper scoring rule) with moving-block-bootstrap CIs; AUC/accuracy/edge secondary.
- 2026-10-04 — **Spikes:** C6 shift monitor + C7 regime-adaptive mixer — see [ADR 001](architecture/adr/001-spike.md).

## Components
Full contracts: [architecture/components.md](architecture/components.md) · code `components/contracts.py`.

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Ingest | Tardis CSV.gz → `BookDay` | polars reader, receive-time sort | | done | rows/s; recv−exch latency |
| C2 | Features | `BookDay` → `FeatureFrame` | CKS OFI, multi-level OFI, queue imbalance, micro-price | | done (17 feats) | single-feature AUC; causality test |
| C3 | Labeler | `FeatureFrame` → `Labels` | raw sign of Δmid at h, ties dropped | | done | tie rate; leakage test |
| C4 | Normaliser | X → Z | static z-score / EWMA z-score | | done | Δlog-loss vs static |
| C5 | Forecaster heads | Z → P(up) | logistic regression | | done | log-loss, AUC |
| C6 | Shift monitor | X, losses → `Alarm`s | rolling KS (Bonferroni), Page-Hinkley | **spike** | baseline done | false alarms/day on calm data · detection delay at events |
| C7 | Adapter / mixer | heads, labels, alarms → p_t | static, periodic, SGD, refit-on-alarm, regime-gated, Fixed-Share | **spike** | baseline done | Δlog-loss vs static (CI) on holdout |
| C8 | Evaluator | p, y, alarms → metrics | prequential, block bootstrap | | done | — |
| C9 | Latency bench | step timings → p50/p99 | perf_counter_ns per step | | done (Python) | p99 µs vs budget |

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

### 2026-10-04 02:00–05:50 IST — Phase 0–4 (lead)
- **Phase 0:** read PLAYBOOK, brief, `_briefs/perceptron.txt`. Judging → "what we must show": a correct crux (silent degradation; HF non-stationarity), leakage-free prequential evaluation with CIs, a detector that is *calibrated* (not a naive KS), adaptation that measurably helps on held-out days, and latency numbers.
- **Data probe (verified by download):** Binance `bookTicker` daily files exist only 2023-05-16…2024-03-30; Tardis free first-of-month CSVs need no key (other days → 401); Bybit ob500 zips exist (774 MB/day — too big tonight). Chose Tardis `book_snapshot_5` (23–39 MB/day). Network was ~0.2–0.5 MB/s, so stopped at 8 days (enough for the baseline).
- **Research agents:** 6 of 8 died on `408 Timed out reading request body` (saturated uplink). Relaunched with checkpointing; surviving notes in `research/notes/` (detectors 37 KB complete; adaptation 24 KB, industry 16 KB, features 7 KB, LOB models 2 KB partial). Supervisor then ordered LEAN MODE (no sub-agents) at 05:50.
- **Events:** FOMC statement times verified at federalreserve.gov press releases (2023-02-01 19:00 UTC; 2023-11-01 and 2024-05-01 18:00 UTC). NFP dates UNVERIFIED (bls.gov 403s scripts) — kept with `verified=no`, not used.
- **Skeleton (C1–C9) + 6 passing contract/leakage tests** (`python -m pytest -q tests`): future-perturbation causality test for features, label-availability test for the adapter (corrupting labels after step s leaves predictions up to s+h unchanged), EWMA causality, detector sanity, metrics.
- **Baseline numbers** (`python eval/run_baseline.py`, results in `eval/results/baseline.md`): static logistic model log-loss 0.6473 dev → 0.6808 holdout (AUC 0.674 → 0.618): silent degradation with temporal distance. **Naive rolling-KS + refit hurts** (+0.0167 dev, +0.0202 holdout log-loss; fires at its cooldown cap, 48 alarms/day, on every day) — on 1-s HF features "everything is a shift". Page-Hinkley-on-loss + refit also hurts (+0.0149 / +0.0093). **Regime-gated heads win** (−0.0133 [−0.0156, −0.0113] dev; −0.0132 [−0.0148, −0.0115] holdout) and are best in both FOMC windows; Fixed-Share mixture −0.0061 / −0.0070; online SGD −0.0074 / −0.0075.
- **Learned:** the bottleneck is not "detect a shift" (the test always rejects) but "detect a *harmful* shift with a controlled false-alarm rate" and "adapt without refitting on tiny noisy windows". This sets the spikes (ADR 001).
