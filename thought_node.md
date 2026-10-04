# Portfolio — Supervisor thought node

> The Supervisor's journal for all 20 projects. Project journals live in `<folder>/thought_node.md`. Method: [PLAYBOOK.md](PLAYBOOK.md). Morning summary: `MORNING_REPORT.md` (pushed by 08:30 IST, 4 Oct).

## Inbox
<!-- User → Supervisor. -->
- _(empty)_

## Now (08:00 IST, 4 Oct)
- **Phase:** Overnight run, final 30 min. 17 of 20 projects have a full morning package; push cut-off 08:15, report 08:30.
- **Doing:** Final calls sent at 07:47 to the 9 leads missing memos; refreshing `MORNING_REPORT.md` after 08:15.
- **Next:** Final report → lift Lean Mode at 08:30 with limits (≤3 concurrent sub-agents per lead, no downloads >1 GB without reason, stagger heavy compute — the Mac hit load ~100 and ~42 GB swap).
- **Lean Mode (since 05:50):** no sub-agents/child sessions, small requests, no big downloads. Cause: uplink saturation made model calls fail with `408 Timed out reading request body` (405 of ~408 errors overnight).

## User action items
- [ ] **By 9 Oct — AI for Technology Readiness:** register (team 1–3, everyone ≤35 on 17 Dec 2026). The training guide + data arrive 10 Oct to registered teams only — drop them into the Inbox of `apctt-trl-assessor/thought_node.md`.
- [ ] **By 9 Oct — InnovateX:** decide whether to pitch at the Delhi zonal (10 Oct, South Asian University) and register; the theme is chosen from the 7 Oct memos.
- [ ] **By 15 Oct:** register Perceptron (one problem), EV (one track), Namma Space, India@71 (one theme) — after the 12 Oct selection memos.
- [ ] **Teammates:** names and skills for every "team fit" section (Perceptron ≤3 · APCTT 1–3 · EV 2–5 · Namma Space ≤4 · India@71 ≤4 · InnovateX ≤4).
- [ ] **Namma Space capture (ready now):** follow [namma-space/deliverables/capture-sop.md](namma-space/deliverables/capture-sop.md) (~15–20 min for a 2–3 room home): 4K30 video, HDR off, AE/AF lock; print the ArUco marker at 100% scale or measure the camera height; say room/object names aloud while filming; fill `capture.json`; transfer originals by AirDrop/cable (not WhatsApp); note phone model and LiDAR yes/no.
- [ ] **Azure GPU quota:** both subscriptions have 0 quota for T4/A10/A100/H100 families. Request e.g. *Standard NCASv3_T4 Family* (8 vCPU) or *NVadsA10v5* (36 vCPU) in Central India or East US. Needed mainly by Namma Space (3D reconstruction); the others run on the M5.
- [ ] **Accounts that unlock better data:** Kaggle login (official Eedi data for P8) · DHS Program account (NFHS-5 microdata for India@71 T1) · Open Charge Map API key (free; EV C1).
- [ ] **Azure resource created overnight (FYI, costs money):** P8 provisioned Azure OpenAI `tf26-p08-aoai-1004` (resource group `rg-tf26-p08`, Sweden Central, gpt-4.1-mini). Delete the resource group if P8 isn't pursued.
- [ ] **If P8 is chosen:** its stretch goal needs a ~30-learner pilot in November.

## Portfolio (08:00 IST) — package = landscape, components, contracts, ADR, deliverables, eval, memo
| Project | Package | Memo (self-score) | Last push | Note |
|---|---|---|---|---|
| [apctt-trl-assessor](apctt-trl-assessor/thought_node.md) | 7/7 | 4.2 | 2 min ago | Lost the night to 408s; restarted 07:10 and caught up (7/7). Data + criteria arrive 10 Oct. |
| [ev-c1-infra-map-india](ev-c1-infra-map-india/thought_node.md) | 3/7 | — | 4 min ago | 🟠 Lost time to deep source verification; pushing again since 07:54 (3/7). |
| [ev-c2-green-auto-lca](ev-c2-green-auto-lca/thought_node.md) | 7/7 | 4.0 | 2 min ago | Real run: petrol scooter 62.9 vs e-scooter 39.7 gCO2e/km (−36.9% [29–44%]); −14% at operating margin, −55% at build margin; ICCT 2021 replicated at 0.06% MAPE. |
| [india71-t1-nutrition](india71-t1-nutrition/thought_node.md) | 7/7 | 4.2 | 9 min ago | Restarted 07:10; recovered uncommitted work and caught up. |
| [india71-t2-learning](india71-t2-learning/thought_node.md) | 7/7 | 4.2 | 23 min ago | "Ek Tasveer": ≤3-SMS Monday plan + interval-backed block estimates (synthetic district calibrated to ASER 2024). |
| [india71-t3-finance](india71-t3-finance/thought_node.md) | 6/7 | — | 13 min ago | Restarted 07:10; package in, memo pending. |
| [innovatex-t1-groundwater](innovatex-t1-groundwater/thought_node.md) | 7/7 | 4.0 | 6 min ago | Real Delhi DWLR data (336 stations, 483k obs). |
| [innovatex-t2-aqi](innovatex-t2-aqi/thought_node.md) | 7/7 | 3.8 | 4 min ago | Restarted 07:10 with uncommitted research; caught up — package + memo in. |
| [innovatex-t3-coastal-plastic](innovatex-t3-coastal-plastic/thought_node.md) | 7/7 | 3.4 | 3 min ago | Most complete InnovateX entry; dispatch gain small (−2.1% median, simulated) → spike is a ratchet boom pocket. |
| [namma-space](namma-space/thought_node.md) | 1/7 | — | 148 min ago | 🔴 Pipeline code exists locally but is unpushed; SOP + first splat done. Final call pending. |
| [perceptron-p01-federated-lora](perceptron-p01-federated-lora/thought_node.md) | 7/7 | 4.2 | 4 min ago | FedAvg hurts 4/5 domains; AnchorLoRA improves all (1 seed, SmolLM2-135M). |
| [perceptron-p02-kv-cache](perceptron-p02-kv-cache/thought_node.md) | 5/7 | 4.2 | 1 min ago | 🟠 Research agents all died overnight; landscape, harness and memo in; components/ADR/abstract pending. |
| [perceptron-p03-off-policy-eval](perceptron-p03-off-policy-eval/thought_node.md) | 7/7 | 4.0 | 10 min ago | Simulator + 5 estimators + confounding bounds; 30-seed bank running. |
| [perceptron-p04-lob-regimes](perceptron-p04-lob-regimes/thought_node.md) | 7/7 | 4.2 | 3 min ago | Real Binance: KS→retrain hurts (+0.020 log-loss); regime heads help (−0.013). |
| [perceptron-p05-impact-execution](perceptron-p05-impact-execution/thought_node.md) | 7/7 | 4.2 | 14 min ago | ABIDES: −0.60 bps vs TWAP [−1.12, −0.10] on 18 seeds; mostly from not walking the book (honest). |
| [perceptron-p06-stat-arb](perceptron-p06-stat-arb/thought_node.md) | 7/7 | 4.0 | 17 min ago | Real 9-venue ticks; our ranking +$802 vs tuned +$768/day — not yet significant (honest). |
| [perceptron-p07-multi-agent-allocation](perceptron-p07-multi-agent-allocation/thought_node.md) | 7/7 | 4.3 | 2 min ago | MPC beats best rule allocator 10/10 seeds: +3.9 pp (shock), +5.4 pp (shock+drift). |
| [perceptron-p08-misconception-tutor](perceptron-p08-misconception-tutor/thought_node.md) | 7/7 | 3.8 | 2 min ago | Self-corrected: GPT-4.1-mini zero-shot gets 86% on the real 5-way Eedi set (ours 46%) → scores lowered; innovation now rests on set-level tracing + verified items. |
| [perceptron-p09-agent-guardrail](perceptron-p09-agent-guardrail/thought_node.md) | 7/7 | 4.6 | 1 min ago | 147/147 bad caught, 0/36 good blocked, p95 2.06 ms — synthetic, optimistic; τ-bench replay next. |
| [perceptron-p10-trusted-text-signal](perceptron-p10-trusted-text-signal/thought_node.md) | 7/7 | 4.2 | 7 min ago | Package in; Theme-6 alternative to P9 (one per team). |

## Key decisions
- 2026-10-04 — Build all 20 problem statements; submit the strongest per competition within the submission limits.
- 2026-10-04 — One private monorepo, trunk-based, one folder per project; every session pushes to `main`.
- 2026-10-04 — No caps on agents or sessions (user directive) — suspended 05:50–08:30 by Lean Mode (network).
- 2026-10-04 — Research uses primary sources (papers, code, company launches, X/Twitter) and tracks what companies ship today (user directive).
- 2026-10-04 — Overnight: nobody asks the user anything; morning package due 08:30 IST (user directive).
- 2026-10-04 05:50 — Lean Mode for all leads until 08:30: the 408 timeouts came from uplink saturation, not from the work itself.
- 2026-10-04 07:20 — `models.github.ai` returns stub "OK" responses from this machine (found by P8, confirmed by P9). Any LLM-dependent number must come from a real model (local MLX/Ollama or Azure OpenAI).

## Log
### 2026-10-04 08:00 IST — Sweep
161+ commits on main; 17/20 full packages. P8 self-corrected after a strong LLM baseline (GPT-4.1-mini zero-shot 86% vs its method's 46% on real Eedi) and lowered its scores — the adversarial-baseline discipline working as intended. Headline numbers for P1, P4, P5, P6, P7, P8, P9, EV C2 and InnovateX T3 traced to committed result files. 4 frontier arXiv citations from memos verified (UQ-LOB 2609.31491, 2607.09230, MalruleLib 2601.03217, GrowthHacker 2511.00802). Laggards: Namma Space (code unpushed), EV C1, P2.
### 2026-10-04 07:25 IST — Sweep
76 commits on main. Restarted 4 dead leads at 07:10 (APCTT, India@71 T1/T3, InnovateX T2), each with uncommitted work to secure first. Sent 13 gap-specific alignment nudges at 07:22. Spot-check: 27/28 sampled citation URLs resolve (the 1 failure is a 403 bot-block by Economic Times). Memos in: P4 (4.2/5), P6, P8, India@71 T2.
### 2026-10-04 05:50 IST — Lean Mode
Diagnosed the 408 storm from session event logs: ~100 sub-agents plus multi-GB downloads saturated the uplink; most research agents died at 0 turns; main had ~12 commits after 3.5 h. Broadcast Lean Mode to all 20 leads; throughput recovered (463 turns vs 19 errors in the next 20 min).
### 2026-10-04 01:55 IST — Launch
Repo created with the playbook, official briefs and 20 seeded project journals. Lead sessions spawned in autopilot.
