# Morning report — Techfest 2026 portfolio

**4 Oct 2026 · v1 written 07:45 IST** — refreshed after the 08:15 push cut-off; see the end for changes.

## Bottom line
- All 20 problem statements have a project lead; most have a cited state-of-the-art review, a component map with typed contracts, a spike decision (ADR) and a Round-1 draft on `main`.
- 9 projects already have a full morning package with **real, reproducible numbers** (P1, P3, P4, P6, P7, P8, P9, EV C2, India@71 T2) and InnovateX T3 is complete on simulated data; the rest land by 08:15 (status below).
- Overnight the shared network saturated and model calls failed with HTTP 408 for ~3.5 h; switching every lead to *Lean Mode* at 05:50 fixed it. Five projects lost most of the night (APCTT, P2, EV C1, Namma Space, InnovateX T2).
- Every number below traces to a committed result file (spot-checked); synthetic or simulated results are labelled. 27 of 28 sampled citations resolve (the 28th is a news-site bot block).

## What you need to do (in order)
1. **By 9 Oct — AI for Technology Readiness:** register (team 1–3, all ≤35 on 17 Dec). The training guide + data arrive **10 Oct** to registered teams only — drop them into the Inbox of [`apctt-trl-assessor/thought_node.md`](apctt-trl-assessor/thought_node.md).
2. **By 7 Oct — InnovateX:** decide whether to pitch at the **Delhi zonal on 10 Oct** (South Asian University); I'll recommend one theme from the 7 Oct memos. Register by 9 Oct.
3. **Today, ~20 min — Namma Space capture:** film your home following [`namma-space/deliverables/capture-sop.md`](namma-space/deliverables/capture-sop.md) (4K30, HDR off, AE/AF lock, print the marker at 100%, say room names aloud, AirDrop the originals). Round 1 (31 Oct) needs a working viewer of *your* space.
4. **Teammates:** names + skills for the team-fit sections (Perceptron ≤3 · APCTT 1–3 · EV 2–5 · Namma ≤4 · India@71 ≤4 · InnovateX ≤4). Several abstracts have `[TEAM]` placeholders.
5. **By 15 Oct:** register Perceptron (one problem), EV (one track), Namma Space, India@71 (one theme) — I'll give final picks by 12 Oct.
6. **Azure GPU quota (for Namma Space):** both subscriptions have 0 quota for T4/A10/A100/H100. Request *Standard NCASv3_T4 Family* (8 vCPU) or *NVadsA10v5* (36 vCPU) in Central India or East US.
7. **Optional accounts:** Kaggle (official Eedi data, P8) · DHS Program (NFHS-5 microdata, India@71 T1) · Open Charge Map API key (EV C1).
8. **FYI — Azure spend:** P8 created Azure OpenAI `tf26-p08-aoai-1004` (rg `rg-tf26-p08`, Sweden Central, gpt-4.1-mini). Delete the resource group if P8 isn't pursued.

## Recommendations by competition (preliminary — final picks by 12 Oct)
Scores are each lead's own 1–5 self-assessment (winnability · innovation · feasibility · demo · fit); my ranking also weighs evidence quality, crowding and fit with your strengths.

### Perceptron (IITB × Optiver) — one problem per team
| Rank | Problem | Self-score | Strongest evidence so far | My read |
|---|---|---|---|---|
| 1 | [P9 Agent guardrail](perceptron-p09-agent-guardrail/thought_node.md) | 4.6 | Tier-0 guard caught 147/147 bad calls, blocked 0/36 good, p95 2.06 ms — **synthetic split, self-authored templates (optimistic)** | Best fit for frontier models + systems; "pre-trade risk checks for AI agents" speaks Optiver's language. Needs real-error replay (τ-bench) to be credible. |
| 2 | [P7 Multi-agent allocation](perceptron-p07-multi-agent-allocation/thought_node.md) | ~4.3 | Look-ahead MPC beats 3 rule allocators under a demand shock (10-seed held-out); change detector 0.415 vs EWMA 0.438 | Your home turf (autoscaling = dispatch); single-problem theme. Risk: collapses to "MPC beats rules". |
| 3 | [P1 Federated LoRA](perceptron-p01-federated-lora/thought_node.md) | 4.2 | Starter FedAvg makes 4 of 5 domains *worse* than untuned (macro 2.735 vs 2.706); AnchorLoRA 2.665 improves every domain (SmolLM2-135M, 1 seed) | Striking, real finding; novelty is integration + measurement. More seeds running. |
| 4 | [P4 Order-book regimes](perceptron-p04-lob-regimes/thought_node.md) | 4.2 | Real Binance BTCUSDT: textbook KS→retrain fires 48×/day and *hurts* (+0.020 log-loss); regime heads help (−0.013) | Rigorous and Optiver-native, but small effects and expert judges. |
| 5 | [P8 Misconception tutor](perceptron-p08-misconception-tutor/thought_node.md) | 4.2 | Real Eedi: 5-way diagnosis 46% vs 38% TF-IDF vs 30% majority, 0% wrong attribution; simulated learners 5.5% vs 58.4% errors left | Best demo; weaker fit with your strengths; needs a real ~30-learner pilot. |
| 6 | [P3 Off-policy evaluation](perceptron-p03-off-policy-eval/thought_node.md) | 4.0 | Simulator + 5 estimators + confounding bounds built; 30-seed bank pending | Rigorous; statistics-heavy fit. |
| 7 | [P6 Cross-asset stat arb](perceptron-p06-stat-arb/thought_node.md) | 3.8 | Real 9-venue ticks: 345,890 mispricings, median life 90.5 ms; naive −$1,570/day vs tuned +$768 vs ours +$802 (not significant) | Honest and well built, but the edge isn't significant yet. |
| — | [P2 KV-cache](perceptron-p02-kv-cache/thought_node.md) · [P5 Execution](perceptron-p05-impact-execution/thought_node.md) · [P10 Text signal](perceptron-p10-trusted-text-signal/thought_node.md) | pending | Memos due 08:15 | P10 and P9 share Theme 6 (one per team). |

### AI for Technology Readiness (APCTT, UN ESCAP) — single problem
[apctt-trl-assessor](apctt-trl-assessor/thought_node.md): the lead lost the night to 408s and restarted at 07:10; landscape on main, rest by 08:15. The decisive inputs (data, criteria) arrive 10 Oct. **Register regardless** — it's the largest prize and open to you.

### EV Infra & Green Mobility (MHI × ICAT) — one track per team
- **Leaning [C2 Green Auto India (LCA)](ev-c2-green-auto-lca/thought_node.md)** (self-score 4.0): replicates the main open Indian 2-wheeler benchmark (ICCT 2021) within 0.06 % and exposes an inconsistency in it; the grid-factor method alone moves the e-scooter saving from 14 % to 55 %. No open India-specific automotive LCA database exists.
- [C1 EV Infra Map India](ev-c1-infra-map-india/thought_node.md): memo pending (lost time overnight).

### Namma Space (Juspay) — single problem
[namma-space](namma-space/thought_node.md): capture SOP done; first Gaussian splat trained on the M5 (Brush/Metal, public *drjohnson* scene, 36.9 min); navigation geometry in progress. Biggest dependency: **your capture** + GPU quota.

### India @71/100 — one theme per team
- **Leaning [T2 Foundational learning](india71-t2-learning/thought_node.md)** (self-score 4.2): "Ek Tasveer" — a ≤3-SMS Monday plan per teacher + interval-backed block estimates, on a synthetic district calibrated to ASER 2024 (23.4 % Std III reading). Richest public evidence base; proposal draft exists.
- [T1 Nutrition](india71-t1-nutrition/thought_node.md) and [T3 Financial inclusion](india71-t3-finance/thought_node.md): memos pending (both restarted 07:10).

### InnovateX — one theme per team, Delhi zonal 10 Oct
- [T3 Coastal plastic](innovatex-t3-coastal-plastic/thought_node.md) (self-score 3.4) is complete: Mumbai reality check, digital twin on real ERA5 rain + tides, pitch + prototype plan (flume ₹33,958; field node ₹82,282). Honest caveat: smart dispatch is a small lever (median −2.1 % escaped plastic, simulated), and Delhi judges may relate more to AQI.
- [T1 Groundwater](innovatex-t1-groundwater/thought_node.md) (real Delhi data: 336 stations, 483k observations) and [T2 AQI](innovatex-t2-aqi/thought_node.md): memos pending. Final pick from the 7 Oct memos.

## What changes now
- **Lean Mode lifts at 08:30 with limits:** ≤3 concurrent sub-agents per lead, no downloads over 1 GB without a reason, and heavy compute staggered. The Mac hit load ~100 and ~42 GB swap overnight.
- Leads continue autonomously toward their Round-1 deadlines; I keep sweeping and will bring the 7 Oct (InnovateX) and 12 Oct (all other) selections to you.
- Steer any project by writing in the Inbox of its `thought_node.md` (GitHub web editor is fine).
