# Morning report — Techfest 2026 portfolio

**4 Oct 2026, 08:20 IST** · repo: [imdigitalashish/techfest-2026](https://github.com/imdigitalashish/techfest-2026) · journal: [thought_node.md](thought_node.md)

## Bottom line
- **All 20 problem statements delivered a morning package**: cited state-of-the-art review, component map with typed contracts, spike decision (ADR), Round-1 draft, eval harness, and a selection memo. ~220 commits overnight.
- **Real, reproducible numbers** exist for 16 projects; the rest are labelled synthetic or pending. I traced the headline numbers to committed result files, and 27 of 28 sampled citations resolve.
- **The system corrected itself honestly.** Three leads downgraded their own claims after stronger tests:
  - P8: a plain GPT-4.1-mini baseline beat its classifier, 86% vs 46%.
  - P5: its 18-seed gain vanished on 60 seeds.
  - P6: its edge is not yet significant.
  Treat the rest of this report the same way: confident where the evidence is.
- **Overnight incident:** the shared network saturated and model calls failed with HTTP 408 for ~3.5 h. *Lean Mode* at 05:50 fixed it. Four leads crashed and were restarted at 07:10; all recovered.

## What you need to do
| When | Action |
|---|---|
| **By 9 Oct** | **Register for AI for Technology Readiness** (team 1–3, all ≤35 on 17 Dec). The training guide and data come **10 Oct**, to registered teams only. Drop them into the Inbox of [apctt-trl-assessor/thought_node.md](apctt-trl-assessor/thought_node.md). |
| **By 7 Oct** | **InnovateX:** confirm you'll pitch at the **Delhi zonal (10 Oct, South Asian University)**. I'll pick T1 or T2 on 7 Oct. Register by 9 Oct. |
| **Today (~20 min)** | **Namma Space capture:** film your home per [capture-sop.md](namma-space/deliverables/capture-sop.md). Use 4K30 with HDR off and AE/AF lock. Print the marker at 100% scale, say room names aloud, and AirDrop the originals. |
| **This week** | **Teammates:** names and skills. Abstracts have `[TEAM]` placeholders. Limits: Perceptron ≤3 · APCTT 1–3 · EV 2–5 · Namma Space ≤4 · India@71 ≤4 · InnovateX ≤4. |
| **By 15 Oct** | **Register** Perceptron (one problem), EV (one track), Namma Space and India@71 (one theme), after my picks on **12 Oct**. |
| When convenient | **Azure GPU quota** for Namma Space: request *NCASv3_T4* (8 vCPU) or *NVadsA10v5* in Central India or East US. Current quota is 0. |
| Optional | Kaggle login (P8, P10) · DHS Program account (India@71 T1) · Open Charge Map key (EV C1) · a state WCD or district contact for pilot data (India@71 T1) · a Raspberry Pi or old phone (P1 stretch). |
| FYI | P8 created Azure OpenAI `tf26-p08-aoai-1004` (resource group `rg-tf26-p08`, Sweden Central). It costs money; delete it if P8 isn't pursued. |

## Recommendations by competition
Self-scores are each lead's own average of winnability, innovation, feasibility, demo and fit (1–5). My ranks also weigh evidence quality, how crowded the problem is, and fit with your strengths. **Final picks: 7 Oct (InnovateX) and 12 Oct (the rest).**

### Perceptron (IITB × Optiver) — one problem per team
| # | Problem | Self | Evidence on main (✱ = synthetic) | Read |
|---|---|---|---|---|
| 1 | [P7 Multi-agent allocation](perceptron-p07-multi-agent-allocation/thought_node.md) | 4.3 | Look-ahead MPC beats the best rule allocator on **10/10 held-out seeds**: +3.9 pp served under a shock [CI +3.3, +4.6], +5.4 pp under shock + drift [+5.2, +5.7] (simulator) | Strongest evidence; autoscaling/dispatch is your home turf. Risk: shrinks to "MPC beats rules" unless the change-detector spike adds measurable value. |
| 2 | [P9 Agent guardrail](perceptron-p09-agent-guardrail/thought_node.md) | 4.6 | Catches 147/147 bad tool calls, blocks 0/36 good ones, p95 2.06 ms ✱ (self-authored test set, optimistic) | Best fit for frontier models. "Pre-trade risk checks for AI agents" speaks Optiver's language. **Becomes #1 if it holds on real agent errors (τ-bench replay) by 10 Oct.** |
| 3 | [P1 Federated LoRA](perceptron-p01-federated-lora/thought_node.md) | 4.2 | Starter FedAvg leaves 4 of 5 domains *worse* than untuned (2.735 vs 2.706 macro loss); AnchorLoRA 2.665 improves every domain (SmolLM2-135M, 1 seed) | Striking and real; needs more seeds (running). |
| 4 | [P10 Trusted text signal](perceptron-p10-trusted-text-signal/thought_node.md) | 4.2 | Real StockNet: the starter's conformal bands cover 81.3% of a 90% target. Certified CR-ACI holds 89.5% clean and 89.7% under a fake-post attack, for +0.3% width | Rigorous; text adds almost no accuracy, so it sells trust, not alpha. Same theme as P9. |
| 5 | [P4 Order-book regimes](perceptron-p04-lob-regimes/thought_node.md) | 4.2 | Real Binance: textbook drift-retrain fires 48×/day and *hurts* (+0.020 log-loss); regime heads help (−0.013) | Optiver-native and honest; small effects; expert judges. |
| 6 | [P3 Off-policy evaluation](perceptron-p03-off-policy-eval/thought_node.md) | 4.0 | ✱ Naive before/after gets the wrong sign in 30/30 seeds; the doubly-robust estimator recovers the truth (93% coverage). Real OBD sample: inconclusive at 10k rows | Rigorous; statistics-heavy fit. |
| 7 | [P2 KV-cache](perceptron-p02-kv-cache/thought_node.md) | 4.2 | No measured numbers yet (memory swap starved the harness overnight) | Promising spike ("Recall-on-Demand") and fit 5; unproven. |
| 8 | [P5 Impact-aware execution](perceptron-p05-impact-execution/thought_node.md) | 4.4 | Its "synchronised twins" spike makes paired CIs 7.5× tighter. Impact-aware schedule vs TWAP: −0.050 bps [−0.100, −0.003], own impact −16% — **not significant after multiple-comparison correction**; a pre-registered 200-seed test is running | Real method contribution (noise reduction); trading edge still unproven. |
| 9 | [P6 Cross-asset stat arb](perceptron-p06-stat-arb/thought_node.md) | 3.8 | Real 9-venue ticks: 345,890 mispricings, median life 90.5 ms; ours +$802/day vs tuned threshold +$768 — **not significant** | Well built; no edge yet. |
| 10 | [P8 Misconception tutor](perceptron-p08-misconception-tutor/thought_node.md) | 3.8 | Real Eedi: zero-shot GPT-4.1-mini scores **86%** vs our classifier's 46% | Great demo, but the obvious baseline wins the MVP. |

### AI for Technology Readiness (APCTT, UN ESCAP) — one problem
[apctt-trl-assessor](apctt-trl-assessor/thought_node.md) · self 4.2. It lost the night to 408s, restarted at 07:10, and caught up with a full package, an ~8.6k-record public labelled set, and an offline, evidence-first ordinal design. The biggest unknown is the hidden data's genre and metric, which arrive 10 Oct. **Register regardless**: it's the largest prize, the only one open to non-students, and has 3 submissions.

### EV Infra & Green Mobility (MHI × ICAT) — one track per team
1. **[C2 Green Auto India — LCA](ev-c2-green-auto-lca/thought_node.md)** · self 4.0 · lean. Real run: petrol scooter 62.9 vs e-scooter 39.7 gCO₂e/km (**−36.9%**, CI 29–44%). Grid method alone swings the saving from 14% to 55%. It replicates the ICCT 2021 Indian 2W study within 0.06% and found ICCT's printed inputs don't reproduce its own table. Closest to ICAT's core work.
2. **[C1 EV Infra Map India](ev-c1-infra-map-india/thought_node.md)** · self 4.2 · close second. Live VAHAN pipeline (36/36 states, RTO level). Finding: open data covers only ~2% of official charging stations, so its spike is a "completeness-aware charger census". Risk: supply-side data access.

### Namma Space (Juspay) — one problem
[namma-space](namma-space/thought_node.md) · self 4.0. The whole pipeline ran end-to-end overnight on a public multi-room scene (photos → 3D Gaussian splat → floor alignment → walkable grid → A* path) on the M5, with no CUDA needed for Round 1. The path-safety metric is being re-run. **Blocked on your capture** for Round 1 (31 Oct).

### India @71/100 — one theme per team
1. **[T1 Nutrition — "Poshan Setu"](india71-t1-nutrition/thought_node.md)** · 4.2 · lean. The sharpest verified "scorecard vs reality" gap: Poshan Tracker reports **5.46%** wasting vs NFHS-5's **19.3%** (Rajya Sabha USQ 477; PIB 1988614). It has 10 tested components. Model metrics are synthetic (no public microdata); a state or district data contact would lift it.
2. **[T3 Financial inclusion — "Sakriya"](india71-t3-finance/thought_node.md)** · 4.2. The gap is *accounts vs people*:
   - Inoperative Jan Dhan accounts rose from **14.1% to 26.4%** (Lok Sabha, 8 Dec 2025).
   - Yet person-level inactivity *fell* from 27.4% to 14.3% (World Bank Findex, 2021→2024).
   - Those left behind are concentrated: 19.6% of women account-owners are inactive vs 12.6% of men.
   - On synthetic data, uplift-based targeting captures 33–37% of achievable gain vs the status quo's 4% (corrected after the lead fixed its own evaluator bug).
3. **[T2 Learning — "Ek Tasveer"](india71-t2-learning/thought_node.md)** · 4.2. Richest evidence base and a complete proposal; the demo runs on a synthetic district calibrated to ASER 2024.

### InnovateX — one theme, Delhi zonal 10 Oct
- **[T1 Groundwater — "JalSakshi"](innovatex-t1-groundwater/thought_node.md)** (4.0) and **[T2 AQI — "DustLedger"](innovatex-t2-aqi/thought_node.md)** (4.0) are tied.
  - T1 audits rainwater-harvesting pits per storm and uses real Delhi data (336 stations, 483k observations).
  - T2 runs a fence-line dust ring that attributes a construction site's own dust. It's Delhi's most relatable and most crowded theme.
  - Both have demo 5. I decide on 7 Oct after a hostile-judge review.
- [T3 Coastal plastic](innovatex-t3-coastal-plastic/thought_node.md) (3.4) is the most finished, but its own lead recommends it only if T1 and T2 falter: weak fit for a Delhi panel, and the dispatch gain is small.

## What happens next
- **08:30 — Lean Mode lifts with limits:** ≤3 concurrent sub-agents per lead, no downloads over 1 GB without a reason, and heavy compute staggered. The Mac hit load ~100 and ~42 GB swap overnight.
- Leads continue toward their Round-1 deadlines. Next jobs:
  - P9 replays real agent errors.
  - P1 adds seeds.
  - P2 runs its benchmark grid.
  - Namma Space processes your capture.
  - APCTT adapts on 10 Oct.
- I keep sweeping every 15 min and bring the 7 Oct and 12 Oct picks to you.
- **To steer a project,** write in the Inbox of its `thought_node.md` (the GitHub web editor is fine).
