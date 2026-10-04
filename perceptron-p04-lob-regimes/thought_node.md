# Perceptron P4 · Order-book forecasting under regime shifts — Thought Node

> Journal for `perceptron-p04-lob-regimes/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** Demo phase (Supervisor 21:24 IST, PLAYBOOK §11). One child session, *P4 demo builder*, is writing `demo/PROPOSAL.md`; the lead approves it before the build. After the build: a gpt-6-astra demo review, then a clean-checkout verification, then DEMO DONE.
- **State:**
  - Pre-registered v2 evaluation done and independently reproduced; reviews triaged (23 accepted, 3 of them in part, 0 rejected).
  - Abstract v2.1 is final (830 words; `[TEAM]` placeholders).
  - Memo re-scored to 3.4/5.
- **Key numbers** (held-out, 22 days; Δ log-loss vs static; [`eval/results/v2_holdout.md`](eval/results/v2_holdout.md)):

  | Policy | Δ vs static | Days better |
  |---|---|---|
  | Textbook KS→refit | +0.0268 | 1/22 |
  | Regime gate | −0.0099 | 22/22 |
  | Gate + shrinkage | −0.0093 | 22/22 |
  | Registered Fixed-Share spike | −0.0010 (H1 not supported) | 10/22 |

  Break-even fee is 0.132 bps/side against taker fees of 1.7–5.0 bps, so it is not tradable as a taker.
- **Next (only if P4 is selected):**
  1. Event-rich continuous data (Binance bookTicker 2023-05…2024-03, ~150–370 MB/day) with event-window metrics frozen before testing.
  2. ARL calibration of the CUSUM on dependence-preserving nulls.
  3. A spread or no-move head.
  4. A compiled online step with end-to-end latency measured.
  5. A known-change replay demo with the gate on and off.
- **Needs from user:** if P4 is chosen, register by 15 Oct and fill the two `[TEAM]` placeholders (statistics/evaluation owner; data/demo owner) in `deliverables/round1-abstract.md`.
- **Risks:** novelty judged incremental; shrinkage benefit unproven; one instrument on a calendar-restricted sample; latency target unmet (85.6 µs p99 Python step).

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
- 2026-10-04 12:00 — **v2 protocol pre-registered** (`eval/PREREGISTRATION.md`, `d9ad7a9`). All 46 free days; train 2023, dev 2024, holdout 2025-01…2026-10; primary test is a 97.5% paired day-cluster bootstrap. Amendment 1 (`a9b310b`), made after dev and before the holdout, fixed H=10, B=600 and added `spike_gate`.
- 2026-10-04 12:35 — **Spike revised by evidence.** The volatility-regime gate plus harm-gated abstention replaces the Fixed-Share mixer, which failed H1 on the holdout. The calibrated KS stays as a label-free audit (ADR 001 *v2 outcome*).
- 2026-10-04 — **Costs:** Binance USDⓈ-M fees from the official page (Regular 2.0/5.0 bps, VIP 9 0.0/1.7 bps maker/taker). Taker edge is measured at +100 ms; maker figures are upper bounds.

## Components
Full contracts: [architecture/components.md](architecture/components.md) · code `components/contracts.py`.

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Ingest | Tardis CSV.gz → `BookDay` | polars reader, receive-time sort | | done | rows/s; recv−exch latency |
| C2 | Features | `BookDay` → `FeatureFrame` | CKS OFI, multi-level OFI, queue imbalance, micro-price | | done (17 feats) | single-feature AUC; causality test |
| C3 | Labeler | `FeatureFrame` → `Labels` | raw sign of Δmid at h, ties dropped | | done | tie rate; leakage test |
| C4 | Normaliser | X → Z | static z-score / EWMA z-score | | done | Δlog-loss vs static |
| C5 | Forecaster heads | Z → P(up) | logistic regression | | done | log-loss, AUC |
| C6 | Shift monitor | X, losses → `Alarm`s | rolling KS (Bonferroni), Page-Hinkley | **spike** | v2 done: calibrated KS (audit, 0.7 alarms/day holdout) + harm gate (CUSUM loss − ln 2 → shrink) | alarms/day · detection delay at events · event-window loss |
| C7 | Adapter / regime gate | heads, labels, alarms → p_t | static, periodic, SGD, refit-on-alarm, Fixed-Share, walk-forward, GBDT | **spike** | v2 done: regime gate −0.0099 vs static (22/22 holdout days) | Δlog-loss vs static, 97.5% day-cluster CI |
| C8 | Evaluator | p, y, alarms → metrics | prequential, block bootstrap | | done | — |
| C9 | Latency bench | step timings → p50/p99 | perf_counter_ns per step | | done (Python) | p99 µs vs budget |

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (a team can submit only one of the 10 Perceptron problems; the Supervisor ranks all 10 from these memos). Score each 1–5 with one line of evidence._
**Final version — 2026-10-04 13:20 IST, re-scored after the cross-model reviews** (`reviews/`). It supersedes the 12:40 version (3.8/5) and the 07:18 v1 memo (4.2/5).

Evidence:
- the pre-registered holdout, 22 real days ([`eval/results/v2_holdout.md`](eval/results/v2_holdout.md)), **reproduced exactly** by an independent `gpt-6-sol` session;
- the post-hoc sensitivity and ablation ([`eval/results/v2_holdout_sensitivity.md`](eval/results/v2_holdout_sensitivity.md));
- the hostile `gpt-6-astra` review, which scored the pre-fix abstract 2.65/5.

Scores:
- **Winnability: 3/5.**
  - For: the strongest Round-1 criteria for us are soundness (25%) and evaluation rigour (15%). We have pre-registration, an exact independent reproduction, a receive-time clock, official fees, and a non-obvious measured failure of the textbook baseline: KS→refit is worse on 21/22 held-out days.
  - Against: innovation (20%) is weak (astra 2/5), and the team section (10%) is unfilled.
  - My estimate for the revised abstract is ~3.3/5 (UNVERIFIED; there was no second review). A top-3 finish at the finals is unlikely with effects this small.
- **Innovation headroom: 2/5.**
  - The gain comes from conditioning on volatility regime. That is known, though confirmed here: −0.0083 vs one EWMA head, 22/22 days.
  - The genuinely new parts (CUSUM confidence shrinkage, KS audit) show no held-out benefit; shrinkage costs +0.0006.
  - The remaining headroom depends on event-rich data that has not been tested yet: Binance's continuous bookTicker archive, 2023-05…2024-03.
- **Feasibility: 5/5.** Built, tested (9 contract/leakage tests), evaluated and reproduced. Runs on the laptop; free, MD5-pinned data.
- **Demo strength: 3/5.** The FOMC replay shows the textbook KS firing every 30 min against a quiet audit and a CUSUM trigger, with a gate-only counterfactual. But the visible effect is small, and an honest demo cannot promise protection during events.
- **Fit with user's strengths: 4/5.** Streaming systems, contracts, latency, rigorous evaluation.
- **Biggest risk:** judges see "volatility-regime logistic heads" as incremental, and the spike's distinctive parts are unproven.
- **One-line pitch:** "On 22 held-out days, the textbook 'KS → retrain' made a BTC order-book forecaster worse on 21; conditioning on the volatility regime made it better on all 22. The result is pre-registered, independently reproduced, and priced with real exchange fees."
- **Overall: 3.4/5** (mean of the five scores).

**Lead's recommendation to the Supervisor:** P4 is an honest, rigorous and reproducible submission, but its novelty is its weak spot. Prefer P7 (or P9/P1) if that project's innovation evidence is stronger. Pick P4 if the panel weights rigour and realism above novelty.

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

### 2026-10-04 11:16–12:00 IST — Resumed (slot freed by P7): data ×5, fees verified, pre-registered v2, dev results, Amendment 1
- **Supervisor (11:16)** resumed P4. Definition of done: ≥24 days; held-out evaluation with paired bootstrap CIs and an edge-vs-fees number; the spike vs textbook KS→retrain and static under a pre-registered protocol; final abstract with a number check; astra and sol cross-model reviews; final memo. Rules: child sessions only (≤2), `nice`, one heavy job at a time.
- **Data:** all 46 free Tardis days (first of each month, 2023-01…2026-10) downloaded in batches of 5 at ~1 MB/s. ~1.1 GB total; reason: exhaustive coverage avoids day selection. MD5s in `data/manifest.csv`.
- **Supervisor (11:30) suggested stratified day selection.** Answered with evidence: the free tier only has first-of-month days, so there is nothing to stratify from; using all of them is selection-free.
- **Fees verified at the primary source:** binance.com/en/fee/futureFee (rendered in a browser, Trading → USDⓈ-M Futures, accessed 2026-10-04). Regular User USDT maker/taker 0.0200%/0.0500%; VIP 9 0.0000%/0.0170%. Tick size 0.10 (exchangeInfo, verified earlier).
- **Code:**
  - Exact fast KS statistic and SciPy-identical asymptotic p-value, unit-tested against `scipy.stats.ks_2samp` on 200 random cases including ties.
  - `HarmCUSUM`: CUSUM of (delayed loss − ln 2).
  - Abstain (coin) and GBDT experts; walk-forward contexts.
  - Shrink action.
  - Day-cluster paired bootstrap.
  - Execution-aware edge: taker at +0/+100 ms, maker upper bound, net of official fees, break-even fee.
  - `eval/run_v2.py`, `eval/check_numbers.py`, `eval/plot_day.py`.
  - Tests: 8 pass, with the label-availability test extended to the coin, harm and shrink paths.
- **Pre-registration** `eval/PREREGISTRATION.md` committed (`d9ad7a9`) before any v2 number existed: split 2023 train / 2024 dev / 2025-01…2026-10 holdout; H1, H2; 97.5% day-cluster CI; the dev tuning rule.
- **Dev (2024) results** (`eval/results/v2_dev.md`):
  - Textbook KS→refit is worse than static on 12/12 days (+0.0216).
  - Regime gating is the best adapter (−0.0125, 12/12); static GBDT −0.0111.
  - The registered Fixed-Share spike gains only −0.003 to −0.005: the abstain expert dilutes it and the α boost on harm alarms is inert.
  - All models are worse than a coin flip in the FOMC 2024-05-01 window.
  - Edge: gross ~0.33 bps per signal vs a ~0.02 bps spread; break-even fee ~0.14–0.16 bps per side, against 5.0 (Regular taker) or 1.7 (VIP 9 taker), so not tradable as a taker.
- **Amendment 1** (`a9b310b`, before the holdout):
  - The registered spike gets H=10, B=600 (by the rule).
  - Post-dev revision `spike_gate` (regime gate + harm-gated shrink): λ=0.5, H=20, B=300 by the same rule. Stated in advance: on dev it does *not* beat plain gating (0.6492 vs 0.6489); harm abstention helps only inside the event window.
- **Holdout run launched 11:58 IST**, single run: `nice -n 10 python eval/run_v2.py --stage holdout --tag v2_holdout --workers 3`.

### 2026-10-04 12:00–12:50 IST — Holdout results, final deliverables, reviews spawned
- **Holdout** (single pre-registered run, commit `a9b310b`, clean tree, runtime 247 s): [`eval/results/v2_holdout.md`](eval/results/v2_holdout.md). 97.5% day-cluster CIs, 22 days.
  - **H1 (registered Fixed-Share spike < static): not supported.** −0.0010 [−0.0044, +0.0020].
  - **H2 (spike < KS→refit): supported.** −0.0278 [−0.0316, −0.0245], 22/22 days.
  - **Post-dev `spike_gate`:** −0.0093 [−0.0129, −0.0062] vs static (22/22); −0.0361 vs KS→refit. Vs regime gate alone: +0.0006 [+0.0003, +0.0009] (H3 not supported, as Amendment 1 predicted).
  - **Comparators vs static:** regime gate −0.0099; GBDT −0.0052; daily retraining −0.0009 (CI spans 0); calibrated-KS→refit +0.0109 (still harmful). Textbook KS→refit is worse than static on 21/22 days.
  - **Alarms:** calibrated lean KS 0.7/day (16 over 22 days) vs 48/day for the textbook test.
  - **Edge:** gross 0.297 bps per signal, spread 0.013 bps, break-even fee 0.132 bps/side, against taker fees of 5.0 bps (Regular) and 1.7 bps (VIP 9). Not tradable as a taker; the maker upper bound is positive only at a 0% maker fee, and it ignores queues and adverse selection.
- **FOMC replay figure** `deliverables/figures/day_2024-05-01.png` (dev day): the calibrated KS fired at 18:09:32 and the harm gate at 18:17:43 (statement 18:00 UTC); both also fired after the 07:10 sell-off (harm 07:24, KS 07:42). The textbook KS fired every 30 min all day.
- **Final docs:**
  - the abstract (868 words incl. title; every required section; `[TEAM]` placeholders);
  - the architecture diagram;
  - ADR 001 *v2 outcome*;
  - landscape §6b plus the official fee source;
  - the final selection memo (3.8/5).
- **Number check:** `python eval/check_numbers.py` passes (163 quoted numbers matched to `eval/results/*`; external figures allowlisted with a reason in `eval/check_numbers_allow.tsv`).
- **Cross-model reviews spawned** (PLAYBOOK §10, 2 child sessions):
  - `gpt-6-astra` (max): hostile judge and methodology on the abstract, spike and pre-registration → `reviews/2026-10-04-abstract-and-spike-gpt-6-astra.md`.
  - `gpt-6-sol` (max): reproduction of the holdout numbers and code review → `reviews/2026-10-04-repro-and-code-gpt-6-sol.md`. It uses a symlink to this worktree's `.data`, so there is no re-download.

### 2026-10-04 12:50–13:20 IST — Cross-model reviews, triage, fixes
- **`gpt-6-sol` (max), reproduction:** exact match on all 17 policy summaries and 374/374 per-day records; tests and the number check pass. Five issues; all accepted:
  - S1: 2025-08-01 was in the v1 holdout;
  - S2: `score().edge_bps` excludes ties;
  - S3: `avail_step` is not enforced;
  - S4: stale midnight exit quote;
  - S5: the number check is sign-blind.
- **`gpt-6-astra` (max), hostile judge:** 2.65/5 before fixes. 18 issues, with blockers A1 (holdout exposure), A2 (post-dev headline) and A16 (team). All accepted (A8, A13 and A16 in part).
- **Fixes:**
  - Abstract v2.1: registered failure shown first; shrinkage ≠ abstention; conditional target; honest latency; convenience sample; novelty reframed; no quoting-value claim.
  - Amendment 2 (post-holdout disclosures); ADR and landscape superseded markers; architecture wording; Q&A Q11.
  - Code: S2–S5 (9 tests pass).
- **New committed analyses** (exploratory, post-hoc):
  - `eval/results/v2_holdout_sensitivity.md`: 21 clean days, 99% CIs, equal-day means, leave-one-day-out. No conclusion changes.
  - `eval/results/v2_holdout_posthoc_ablation.md`: regime heads vs one EWMA head −0.0083 [−0.0118, −0.0059], 22/22 days, so the gain is the regime heads, not the normaliser.
  - `eval/results/feed_delay.md`: median 2.9 ms over 46 days.
- **Ledger:** `reviews/ledger.tsv` has 2 lines. Memo re-scored to 3.4/5.

### 2026-10-04 21:24–21:32 IST — Demo phase started
- Supervisor directive: a winning demo per PLAYBOOK §11. It must open on real data, with simulation second and labelled. Rules: at most 2 child sessions, CPU only, `nice`, memory guard ≥30%, no git stash.
- **Tardis.dev ToS checked** (https://docs.tardis.dev/legal/terms-of-service, accessed 2026-10-04):
  - Clause 9.2 forbids redistributing the Data, except aggregated Derived Data such as OHLC candles at ≥10-minute resolution that cannot be used to reconstruct the raw data.
  - "Derived Data does not include Data that has merely been reformatted, filtered, sampled…".
  - Permitted use: internal research and educational use.
  - Consequence: commit only aggregates; per-second series are built locally after a documented fetch; prices are shown as 10-minute candles. No raw data was ever committed (checked with `git ls-files`).
- **Fixed my own figure** `deliverables/figures/day_2024-05-01.png`: it showed a ~1-s price line. It now uses 10-minute OHLC candles, and volatility, head and loss are 10-minute bin means.
- **Spawned the demo builder** (autopilot) with the ToS rules, committed facts, a concept ("the alarm that cries wolf" knob plus a real replay) and an instruction to stop after `demo/PROPOSAL.md`.
- **New post-hoc evidence** (exploratory): `eval/results/v2_holdout_posthoc_heads.md`, `eval/results/head_usage.md`.
  - Each regime head alone loses to the gate: high-vol head +0.0141 (better on 1/22 days), mid-vol +0.0138, low-vol +0.0526.
  - Held-out head usage: low/mid/high 20.7% / 33.2% / 46.0%, with large day-to-day swings.
  - So the gain comes from switching between heads, not from one better model. This answers a likely judge question.

