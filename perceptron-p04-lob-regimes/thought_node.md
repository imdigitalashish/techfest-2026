# Perceptron P4 · Order-book forecasting under regime shifts — Thought Node

> Journal for `perceptron-p04-lob-regimes/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ⏸ **PAUSED** (Supervisor, 09:55 IST, 4 Oct — user's decision: only 3 projects run at a time; P7 is the Perceptron pick unless the user overrides). The morning package is complete on `main`. No jobs are running.
- **Plan (on resume):** "Invariance first, calibrated detection second, cheap adaptation third". Spikes: C6 shift monitor and C7 regime mixer ([ADR 001](architecture/adr/001-spike.md)).
- **Resume point (exact, in order):**
  1. Grow the data (resumes; skips days already on disk; batches of 5 files, each < 200 MB): `cd perceptron-p04-lob-regimes && data/fetch_batches.sh book_snapshot_5`. 9 of 46 first-of-month days (2023-01 … 2026-10) are on disk; 37 are missing.
  2. Cost model for "is it tradable?": tick size verified (below); fee schedule still to open at the official Binance page (UNVERIFIED until then). Report gross mid-to-mid edge; taker edge net of crossing the spread, with an execution delay (book as of t + 50 ms); net of maker/taker fees; edge by confidence decile; break-even fee.
  3. Harm gate (C6): one-sided CUSUM on ℓ_t − ln 2 using delayed labels, i.e. "the forecast is now worse than a coin flip". On alarm, shrink p toward 0.5. Evidence it targets real harm: the static model's log-loss in the FOMC windows is 0.7194 and 0.7329, above ln 2 = 0.6931 (`eval/results/baseline.md`). Calibrate H on dev; run the ratchet.
  4. GBDT head: sklearn `HistGradientBoostingClassifier` on EWMA-normalised features (no download), as a static expert column in the Fixed-Share mixer; this tests the ADR antithesis "GBDT with volatility as a feature ≈ regime heads".
  5. Split v2 (new flag, v1 stays reproducible): train 2023 · dev 2024 · holdout 2025–26. Add a walk-forward monthly-retrain baseline (fit on prior days only) and run all policies; workers should load days from cache to keep RAM low.
  6. Refresh the abstract numbers, selection memo, landscape and this node; message the Supervisor only if the selection ranking changes.
- **Needs from user:** Register by 15 Oct if P4 is chosen (the Supervisor currently recommends P7). Teammates' names and skills for the abstract's team section.
- **Risks:** (a) Small edge (AUC 0.62–0.67): the story is robustness, not alpha. (b) The calibrated KS is either noisy (37/day) or quiet but blind (cand_003), so the harm gate is the next lever. (c) Data growth depends on network. (d) NFP dates are UNVERIFIED. (e) Latency was measured on a heavily shared machine.

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
- **Winnability: 4/5** — The track is Optiver-sponsored and the judges are domain experts, which rewards measured realism. On day 1 we already have a leakage-tested pipeline on real Binance data and a non-obvious, evidence-backed finding: the textbook "rolling KS → retrain" fires 48 times a day and *raises* held-out log-loss by +0.020 [+0.016, +0.025]. Risk: P4 is the most "standard ML" of Theme 3, so expect crowding.
- **Innovation headroom: 4/5** — The spike is a calibrated, harm-aware shift monitor (empirical null, plus a sequential loss test after Podkopaev & Ramdas, plus calendar priors). It drives a regime-adaptive head mixer whose switching rate rises on alarms instead of refitting on tiny windows. The 2026 frontier is adjacent but different: UQ-LOB (arXiv 2609.31491) calibrates forecasts from realised windows; Jeon (arXiv 2607.09230) classifies liquidity states around macro events. Neither does calibrated detection with adaptation inside a µs loop.
- **Feasibility by the deadline: 5/5** — The end-to-end skeleton runs on the M5 Mac in about 3 minutes for 54 policy-days. No GPU is needed. The data is free (Tardis first-of-month days). Remaining work is incremental: more days, the harm gate, a GBDT head and a compiled step. Plan: MVP plus stretch done by 17 Nov, before the 19–25 Nov exams; the 1 Dec midway report needs no new work.
- **Demo strength: 4/5** — Replay an FOMC day: price, alarm timeline (naive vs calibrated), mixer weights shifting to the high-volatility head at 18:00 UTC, rolling log-loss against the static model, and a latency panel. A live Binance websocket feed works at the venue (public, free). Weakness: the effect sizes are statistical (−0.013 log-loss), not dramatic PnL.
- **Fit with the user's strengths: 4/5** — Streaming systems, typed contracts, latency budgets and evaluation rigour match large-scale systems work. There is less room for frontier-model work, though a small transformer head (TLOB-style) is optional.
- **Biggest risk:** Small, noisy gains and only 8 days on disk. Judges may say "this edge is not tradable". Mitigation: grow to 24+ days, report bootstrap CIs, report edge in bps against the 1-tick spread and fees, and frame the work as *robustness and knowing when you're wrong*, which is what a market maker needs.
- **One-line pitch:** "A 10-second BTC order-book forecaster that knows when the market has changed: calibrated shift alarms (the textbook KS fires 48×/day and hurts — we measured it) steer a microsecond-cheap mixture of regime-specific heads that stays sharp through FOMC releases."
- **Overall: 4.2/5** (mean of the five scores).

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

### 2026-10-04 05:50–07:30 IST — Morning package (lean mode)
- Supervisor LEAN MODE (05:50): no sub-agents, small requests, no big downloads. Complied; all work below is the lead's own.
- Spot-verified key citations myself via the arXiv API/abs pages (titles, dates, authors): 2609.27179 (Bhattacharyya & Ramdas, 2026-09-23), 2412.08435 (Proceed), 2502.15757 (TLOB), 2308.01915 (LOBCAST), 2110.06177, 2203.03532, 1011.6402, 1907.06230. Found and read abstracts of 2026 papers adjacent to us: UQ-LOB 2609.31491, Jeon 2607.09230 (Binance BTCUSDT + macro events, event-clustered validation — closest prior art), 2606.25986 (inference-compute vs latency frontier), LOBIN 2608.02424 (in-network inference), 2607.17555, 2604.21993.
- Wrote `research/landscape.md` (with "What companies ship today"), `architecture/components.md` + `contracts/README.md`, `research/components/README.md`, `architecture/adr/001-spike.md`, the selection memo (4.2/5), `deliverables/round1-abstract.md` (884 words) + `deliverables/architecture.md`. Messaged the Supervisor that the memo is ready.
- Implemented the calibrated KS (`calibrate_ks_null`: leave-one-train-day-out empirical null of the windowed KS statistic) and policies `ksc_refit` and `fs_ksc_boost`; tests still pass (6/6). C6 ratchet scaffold: frozen `eval.py` (SCORE = false alarms per dev day + 10 × missed-event fraction), `program.md`, `results.tsv` (naive baseline 47.67 from the committed baseline run).
- Learned: the naive detector's "FOMC detections" are artefacts — it fires every 30 min (its cooldown) on message rate and depth, so any event gets "detected" within 30 min. Any detector claim must therefore charge for false alarms.

### 2026-10-04 07:30–08:00 IST — First calibrated-KS result (honest negative) and ratchet
- `python eval/run_baseline.py --policies static_snorm ks_refit ksc_refit regime_gated fixed_share fs_ksc_boost --tag calibrated_ks` (runtime 2689 s at load avg ~90) → [`eval/results/calibrated_ks.md`](eval/results/calibrated_ks.md).
- The empirical-null KS cut alarms from 48 to 37–39 per dev day (15–47 on holdout days). It is still dominated by `log_msgs_10s` and `log_depth5`: activity *levels* drift month to month, and a 2-day null cannot cover that.
- Refit on calibrated alarms still hurts: +0.0175 [+0.0132, +0.0220] dev, +0.0152 [+0.0113, +0.0196] holdout. Boosting Fixed-Share on alarms is neutral: −0.0066 vs −0.0070 holdout.
- Ledger row 001 recorded with SCORE 37.33 (vs 47.67 naive), kept provisionally. The FOMC "hit" is a chance alignment of the cooldown-periodic alarm, as stated in the note.
- ADR 001 updated: the spike is calibration *plus* monitoring the invariant/normalised representation *plus* the harm gate. Candidate 003 (drop the level features) is running.
- Numbers in the abstract, landscape and components were cross-checked against `baseline.md`; two latency figures were tightened.
- 07:59 Ratchet: cand_001 confirmed by frozen eval.py (SCORE 37.33, kept provisionally); cand_002 (q=1.0) rejected (45.67, misses FOMC). The null's 99.9% KS distances between two calm training days reach 0.87 (depth level) and 0.99 (60 s realised vol): raw activity/volatility levels are nearly disjoint day to day, so per-feature KS must run on normalised/invariant features (cand_003 running).
- 08:09 Ratchet: cand_003 (KS only on scale-free features: spread, rv_60s, OFI, queue imbalance, return; empirical 0.999 null) cut false alarms to 0/2/0 per dev day (from 37/38/37) but missed the FOMC 2023-11-01 window. SCORE 10.67; not kept under the program rule (no newly missed events). Lesson: quietness is solved by monitoring invariant features; the next ratchet target is sensitivity (harm gate on delayed loss, calendar prior around scheduled releases).

### 2026-10-04 09:40–09:58 IST — Resumed, then paused
- 09:40 The Supervisor resumed P4 in lean mode: grow the data, add the harm gate and a GBDT head, and report edge in bps against spread and fees.
- 09:48 Started `data/fetch_batches.sh` (new; round-robin across years, 5 files per batch). Throughput was ~0.1 MB/s per stream. 2024-01-01 finished (22.8 MB; MD5 in `data/manifest.csv`); 2023-01-01 and 2025-01-01 were partial (deleted).
- 09:52 Verified at the official endpoint https://fapi.binance.com/fapi/v1/exchangeInfo (accessed 2026-10-04, serverTime 1790941589240): BTCUSDT is a PERPETUAL with PRICE_FILTER tickSize 0.10, LOT_SIZE stepSize 0.001 and MIN_NOTIONAL 50. This matches `TICK_SIZE` in `components/contracts.py`. At BTC ≈ 30–100k USDT, one tick is ≈ 0.01–0.03 bps, so the spread is negligible next to fees. The fee schedule is the deciding cost; it is still UNVERIFIED.
- 09:55 **PAUSE** from the Supervisor (only 3 projects run at a time; P7 is the Perceptron pick unless the user overrides). Stopped the download job (PIDs 30598, 30636). No jobs are running. The resume point is in *Now*.
