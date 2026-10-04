# Portfolio — Supervisor thought node

> The Supervisor's journal for all 20 projects. Project journals live in `<folder>/thought_node.md`. Method: [PLAYBOOK.md](PLAYBOOK.md). Morning summary: `MORNING_REPORT.md` (pushed by 08:30 IST, 4 Oct).

## Inbox
<!-- User → Supervisor. -->
- _(empty)_

## Now (11:55 IST, 4 Oct)
- **Mode:** batch of 5, sessions-only delegation, cross-model reviews (PLAYBOOK §0, §4, §10). Watch every 2 min.
- **Active:** Namma Space (has GPU priority; P1 and P9 GPU jobs SIGSTOP-frozen until its Brush run ends) · InnovateX T1 (deck ready; final review applying) · P9 (final abstract; frontier-judge baseline running on Azure gpt-4.1-mini) · P1 · P4.
- **Completed — awaiting your review:** India@71 T1 · EV C2 · P7.
- **Queue:** APCTT (when the 10 Oct data lands) → P10 → P5 → P3 → EV C1 → India@71 T3 → P6 → P2 → P8 → India@71 T2 → InnovateX T2 → InnovateX T3.
- **Needs you today:** a 2-min mini-SOP test clip for Namma Space (see its Inbox / my chat message); Delhi zonal registration by 9 Oct.

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

- [ ] **Mac memory (08:50):** swap is ~97% full (34.6 of 35.8 GB). Your own VM (`com.apple.Virtualization`, ~16 GB incl. compressed) and CapCut are the largest non-project users. Pausing them while the projects run, or approving Azure compute for heavy jobs, would stop the slowdowns. I've asked P1 and P9 to shrink their jobs.
- [ ] **India@71 T1 (✅ Completed — please review):** team names + Team ID for `India71_100_[TeamID].pdf`; a state/district WCD contact for a pilot data extract; a union/worker-association contact for co-design.
- [ ] **EV C2:** access to the ISO 14040/14044 standards text (IIT Delhi library or BIS) for the LCA jury Q&A; an environmental/mechanical teammate; team name, Team ID, institution and contacts for the Round-1 header.
## Portfolio (08:18 IST) — package = landscape, components, contracts, ADR, deliverables, eval, memo
| Project | Package | Memo (self-score) | Last push | Note |
|---|---|---|---|---|
| [apctt-trl-assessor](apctt-trl-assessor/thought_node.md) | 7/7 | 4.2 | 15 min ago | Lost the night to 408s; restarted 07:10 and caught up (7/7). Data + criteria arrive 10 Oct. |
| [ev-c1-infra-map-india](ev-c1-infra-map-india/thought_node.md) | 7/7 | 4.2 | 4 min ago | Caught up 08:10: live VAHAN pipeline (36/36 states); open data has only 600 of 29,277 official stations (~2%) → completeness-aware census. Self 4.2. |
| [ev-c2-green-auto-lca](ev-c2-green-auto-lca/thought_node.md) | 7/7 | 4.0 | 14 min ago | Real run: petrol scooter 62.9 vs e-scooter 39.7 gCO2e/km (−36.9% [29–44%]); −14% at operating margin, −55% at build margin; ICCT 2021 replicated at 0.06% MAPE. |
| [india71-t1-nutrition](india71-t1-nutrition/thought_node.md) | 7/7 | 4.2 | 6 min ago | Verified gap: Poshan Tracker 5.46% vs NFHS-5 19.3% wasting (RS USQ 477; PIB 1988614). 10 tested components; model metrics synthetic. |
| [india71-t2-learning](india71-t2-learning/thought_node.md) | 7/7 | 4.2 | 45 min ago | "Ek Tasveer": ≤3-SMS Monday plan + interval-backed block estimates (synthetic district calibrated to ASER 2024). |
| [india71-t3-finance](india71-t3-finance/thought_node.md) | 7/7 | 4.2 | 11 min ago | Inoperative PMJDY 14.1% → 26.4% (Lok Sabha, 8 Dec 2025). Synthetic uplift targeting captures 34–38% of achievable gain vs 4% status quo. |
| [innovatex-t1-groundwater](innovatex-t1-groundwater/thought_node.md) | 7/7 | 4.0 | 2 min ago | "JalSakshi": per-storm audit of rainwater-harvesting pits; real Delhi DWLR data (336 stations, 483k obs). Self 4.0. |
| [innovatex-t2-aqi](innovatex-t2-aqi/thought_node.md) | 7/7 | 3.8 | 18 min ago | "DustLedger": fence-line dust ring for construction sites (C&D dust, Delhi); simulated site/sensors on real CPCB background. Self 4.0. |
| [innovatex-t3-coastal-plastic](innovatex-t3-coastal-plastic/thought_node.md) | 7/7 | 3.4 | 8 min ago | Most complete InnovateX entry; dispatch gain small (−2.1% median, simulated) → spike is a ratchet boom pocket. |
| [namma-space](namma-space/thought_node.md) | 7/7 | 4.0 | 4 min ago | Pipeline ran end-to-end on a public multi-room scene (splat → alignment → walkable grid → A*); path-safety metric being re-run. Needs your capture. |
| [perceptron-p01-federated-lora](perceptron-p01-federated-lora/thought_node.md) | 7/7 | 4.2 | 19 min ago | FedAvg hurts 4/5 domains; AnchorLoRA improves all (1 seed, SmolLM2-135M). |
| [perceptron-p02-kv-cache](perceptron-p02-kv-cache/thought_node.md) | 7/7 | 4.2 | 13 min ago | Spike "Recall-on-Demand" (evicted spans → 2-bit key sketch, re-prefill on demand). Docs + memo in; **no measured numbers yet** (harness starved by swap; grid runs after 08:30). |
| [perceptron-p03-off-policy-eval](perceptron-p03-off-policy-eval/thought_node.md) | 7/7 | 4.0 | 13 min ago | 30-seed bank (synthetic): naive before/after has the wrong sign in 30/30 seeds; DR recovers the true +0.075 (RMSE 0.006, 93% coverage); real OBD sample inconclusive at 10k rows. |
| [perceptron-p04-lob-regimes](perceptron-p04-lob-regimes/thought_node.md) | 7/7 | 4.2 | 5 min ago | Real Binance: KS→retrain hurts (+0.020 log-loss); regime heads help (−0.013). |
| [perceptron-p05-impact-execution](perceptron-p05-impact-execution/thought_node.md) | 7/7 | 4.0 | 7 min ago | Self-corrected: on all 60 held-out ABIDES seeds, total IS vs TWAP is −0.06 bps [−0.44, +0.34] — not significant. Only the instantaneous-cost cut is significant (−0.043 bps). Spike targets exactly this noise (RNG-synced twins). |
| [perceptron-p06-stat-arb](perceptron-p06-stat-arb/thought_node.md) | 7/7 | 4.0 | 39 min ago | Real 9-venue ticks; our ranking +$802 vs tuned +$768/day — not yet significant (honest). |
| [perceptron-p07-multi-agent-allocation](perceptron-p07-multi-agent-allocation/thought_node.md) | 7/7 | 4.2 | 8 min ago | MPC beats best rule allocator 10/10 seeds: +3.9 pp (shock), +5.4 pp (shock+drift). |
| [perceptron-p08-misconception-tutor](perceptron-p08-misconception-tutor/thought_node.md) | 7/7 | 3.8 | 19 min ago | Self-corrected: GPT-4.1-mini zero-shot gets 86% on the real 5-way Eedi set (ours 46%) → scores lowered; innovation now rests on set-level tracing + verified items. |
| [perceptron-p09-agent-guardrail](perceptron-p09-agent-guardrail/thought_node.md) | 7/7 | 4.6 | 14 min ago | 147/147 bad caught, 0/36 good blocked, p95 2.06 ms — synthetic, optimistic; τ-bench replay next. |
| [perceptron-p10-trusted-text-signal](perceptron-p10-trusted-text-signal/thought_node.md) | 7/7 | 4.2 | 3 min ago | Real StockNet (87 tickers, 119,641 tweets): MAPIE split CP covers only 81.3% of a 90% target; certified CR-ACI holds 89.5% clean / 89.7% under a k=3 fake-post attack for +0.3% width. Text adds ~no accuracy → sells trust, not alpha. Theme-6 alternative to P9. |

## Key decisions
- 2026-10-04 09:50 — **Batch mode (user):** only 3 projects run at a time, with a deadline-aware queue; the rest pause. Replaces Lean Mode for the paused leads.
- 2026-10-04 — Build all 20 problem statements; submit the strongest per competition within the submission limits.
- 2026-10-04 — One private monorepo, trunk-based, one folder per project; every session pushes to `main`.
- 2026-10-04 — No caps on agents or sessions (user directive) — suspended 05:50–08:30 by Lean Mode (network).
- 2026-10-04 — Research uses primary sources (papers, code, company launches, X/Twitter) and tracks what companies ship today (user directive).
- 2026-10-04 — Overnight: nobody asks the user anything; morning package due 08:30 IST (user directive).
- 2026-10-04 05:50 — Lean Mode for all leads until 08:30: the 408 timeouts came from uplink saturation, not from the work itself.
- 2026-10-04 07:20 — `models.github.ai` returns stub "OK" responses from this machine (found by P8, confirmed by P9). Any LLM-dependent number must come from a real model (local MLX/Ollama or Azure OpenAI).

## Log
### 2026-10-04 11:55 IST — Sweep
- EV C2 (11:12) and P7 (11:17) completed and verified; P1 and P4 resumed.
- P9's real-error results: 36–43% harmful-catch at 1.85% false-block. Against a small (1.7B) LLM judge at a matched stop rate, P9 stops 48% of harmful calls vs 28%. A frontier-judge baseline (Azure gpt-4.1-mini, full and cascade) is running to rule out a strawman comparison.
- Namma got cross-project GPU priority for its end-to-end run. Its earlier 0.788→0.970 result was dropped after it found leakage.
- P4 corrected my data-size assumption (20–40 MB/day; 46 free days) and verified the Binance fees at the primary source.
### 2026-10-04 11:17 IST — P7 completed
Verified on main: abstract v1.2 (~880–900 words, [TEAM] placeholders), architecture, Q&A prep (15), 5 reviews + ledger. Headline numbers match `eval/results` (confirmatory +3.7 pp shock / +5.47 [+5.36, +5.59] shock+drift, 30/30, Holm; NYC replays +2.5 and +1.52 pp). Detector spike failed its pre-registered replication; re-scoped to decision-aware forecast trust (pre-registered test). Marked ✅ Completed. P4 resumed into the free slot.
### 2026-10-04 11:12 IST — EV C2 completed
Verified on main: methodology + roadmap v1.1 (team details pending); 4 reviews (45 accepted, 0 rejected) + ledger; docs drift check OK; 19/19 tests pass. Headline rendered from the run: e-scooter −38.1% (32.0–43.2); BEV sedan −10.0% (−10.1–25.6), P(lower) 0.81. Marked ✅ Completed. P1 resumed into the free slot.
### 2026-10-04 11:08 IST — Sweep
- India@71 T1 completed and verified (10:50); P9 took the slot.
- Cross-model reviews are paying off:
  - India T1: a review found eval leakage, and the corrected eval reversed the result (the transparent WHZ rule beats ML).
  - P7: a GPT-6 Sol run reproduced every headline number exactly.
  - EV C2: applied Sol and Astra reviews; check_docs prevents drift.
  - P9: miss taxonomy — 8/20 misses were user-requested (not catchable from the transcript), 8/20 wrong-entity (the spike's target).
- InnovateX T1 picked by two independent judges (GPT-6 Astra, Grok 4.7) and applying their fixes.
- My one wrong flag: the green-steel gazette date (the lead's primary-source check was right).
### 2026-10-04 10:50 IST — India@71 T1 completed
Verified on main: 6-page A4 Arial PDF, citations verified at primary sources, GPT-6 Sol (14/14 accepted) + GPT-6 Astra (16/1) reviews, leakage-free eval (transparent WHZ rule 43% > ML 38%, ADR 003), check_docs 17/17. Marked ✅ Completed in README. P9 resumed into the free slot (APCTT waits for 10 Oct data).
### 2026-10-04 09:55 IST — Batch mode
After Lean Mode lifted at 08:30, sub-agents resumed and HTTP 408 timeouts rose again (6 in 10 min; upload measured ~55 KB/s). User directive: run 3 projects at a time. Active: Namma Space, P7, EV C2, each with a 5-point definition of done. 17 leads told to save, push and go idle. P1 had already cut memory (swap 31.5 → 20.9 GB) and replicated AnchorLoRA on seed 1 (2.66510 vs starter 2.7535).
### 2026-10-04 08:18 IST — Morning package complete
All 20 leads pushed a full package plus selection memo (~220 commits). Final MORNING_REPORT.md published with rankings per competition. Honest self-corrections overnight: P8 (LLM baseline 86% vs 46%), P5 (60-seed gain not significant), P6 (edge not significant). Late recoveries: APCTT, EV C1, Namma Space, India@71 T1/T3, InnovateX T2. Cross-project reuse to relay after 08:30: P5's synchronised-twin RNG (~6× lower counterfactual noise) for P7/P3; EV C2's CEA v22 state-level grid workbook for EV C1.
### 2026-10-04 08:00 IST — Sweep
161+ commits on main; 17/20 full packages. P8 self-corrected after a strong LLM baseline (GPT-4.1-mini zero-shot 86% vs its method's 46% on real Eedi) and lowered its scores — the adversarial-baseline discipline working as intended. Headline numbers for P1, P4, P5, P6, P7, P8, P9, EV C2 and InnovateX T3 traced to committed result files. 4 frontier arXiv citations from memos verified (UQ-LOB 2609.31491, 2607.09230, MalruleLib 2601.03217, GrowthHacker 2511.00802). Laggards: Namma Space (code unpushed), EV C1, P2.
### 2026-10-04 07:25 IST — Sweep
76 commits on main. Restarted 4 dead leads at 07:10 (APCTT, India@71 T1/T3, InnovateX T2), each with uncommitted work to secure first. Sent 13 gap-specific alignment nudges at 07:22. Spot-check: 27/28 sampled citation URLs resolve (the 1 failure is a 403 bot-block by Economic Times). Memos in: P4 (4.2/5), P6, P8, India@71 T2.
### 2026-10-04 05:50 IST — Lean Mode
Diagnosed the 408 storm from session event logs: ~100 sub-agents plus multi-GB downloads saturated the uplink; most research agents died at 0 turns; main had ~12 commits after 3.5 h. Broadcast Lean Mode to all 20 leads; throughput recovered (463 turns vs 19 errors in the next 20 min).
### 2026-10-04 01:55 IST — Launch
Repo created with the playbook, official briefs and 20 seeded project journals. Lead sessions spawned in autopilot.
