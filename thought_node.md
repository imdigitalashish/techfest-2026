# Portfolio — Supervisor thought node

> The Supervisor's journal for all 20 projects. Project journals live in `<folder>/thought_node.md`. Method: [PLAYBOOK.md](PLAYBOOK.md). Morning summary: `MORNING_REPORT.md` (pushed by 08:30 IST, 4 Oct).

## Inbox
<!-- User → Supervisor. -->
- _(empty)_

## Now (23:38 IST, 4 Oct) — PAUSED by you; resume tomorrow
- **Round 1:** 19 of 20 done. APCTT is gated on its 10 Oct data and needs your registration by 9 Oct.
- **Demos done (8), all re-verified by me:** P10, P2, P6, P7, P9, India@71 T1, P1, P5.
- **Paused mid-demo (5):**
  - P3: review fixes pushed; clean-checkout verify next.
  - P8: astra review triaged.
  - P4: review fixes landing.
  - India@71 T3: building.
  - InnovateX T1: §11 upgrade just started; zonal 10 Oct.
- **Still to upgrade to §11:** EV C1, Namma, India@71 T2, EV C2, InnovateX T2, InnovateX T3.
- **At pause:**
  - All Playwright Chrome instances, Playwright MCP servers in Techfest worktrees, demo servers (including InnovateX T3's :8765) and polling sleeps were killed.
  - All leads and demo builders were told STOP.
  - The 2-min watch automation is cleared.
## User action items
- [ ] **By 9 Oct — AI for Technology Readiness:** register (team 1–3, everyone ≤35 on 17 Dec 2026). The training guide + data arrive 10 Oct to registered teams only — drop them into the Inbox of `apctt-trl-assessor/thought_node.md`.
- [ ] **By 9 Oct — InnovateX:** register for the Delhi zonal (10 Oct, South Asian University) with T1 JalSakshi. Its zonal package is complete (see the InnovateX T1 item below).
- [ ] **By 15 Oct:** register Perceptron (one problem), EV (one track), Namma Space, India@71 (one theme) — after the 12 Oct selection memos.
- [ ] **Teammates:** names and skills for every "team fit" section (Perceptron ≤3 · APCTT 1–3 · EV 2–5 · Namma Space ≤4 · India@71 ≤4 · InnovateX ≤4).
- [ ] **Namma Space (✅ Completed — please review `namma-space/`):** the full automatic pipeline works from raw photos.
  - Held-out PSNR 29.56 dB / SSIM 0.929; trajectory error 0.07% of the scene; 45.8 min on this Mac.
  - Viewer: walking p95 22.4 ms at 60 fps; cold load 7.45 s at 40 Mbit/s; 6 POIs with search and routes.
  - **Needs from you:** your own capture (home, or a hostel room or lab) with the tape-measure checks; the demo video; the Drive master doc and PDF; approval to host your twin publicly.
  - Close the viewer side panel when you're done; it renders on the GPU, and Namma's `http.server 8080` feeds it.
- [ ] **Namma Space capture (ready now):** follow [namma-space/deliverables/capture-sop.md](namma-space/deliverables/capture-sop.md) (~15–20 min for a 2–3 room home): 4K30 video, HDR off, AE/AF lock; print the ArUco marker at 100% scale or measure the camera height; say room/object names aloud while filming; fill `capture.json`; transfer originals by AirDrop/cable (not WhatsApp); note phone model and LiDAR yes/no.
  - **Required for Round 1:** the brief says to map *your own* home or a similarly accessible indoor space, so a public dataset can't be the judges' link.
  - If your home capture fails the quality check, capture another space you can access (hostel room, lab or common room, with permission). It takes ~20 min, any day before 31 Oct.
  - Namma will also host a public scene, labelled "viewer demo on a public dataset — not our capture", as an extra; it never replaces the owned link.
- [ ] **Azure GPU quota:** both subscriptions have 0 quota for T4/A10/A100/H100 families. Request e.g. *Standard NCASv3_T4 Family* (8 vCPU) or *NVadsA10v5* (36 vCPU) in Central India or East US. Needed mainly by Namma Space (3D reconstruction); the others run on the M5.
- [ ] **Accounts that unlock better data:** Kaggle login (official Eedi data for P8) · DHS Program account (NFHS-5 microdata for India@71 T1) · Open Charge Map API key (free; EV C1).
- [ ] **Azure OpenAI `tf26-p08-aoai-1004` (rg `rg-tf26-p08`, pay-per-token; idle costs nothing):** P8 is done (total API spend $19.75) and recommends against itself. If you don't pick P8, delete it with `az group delete -n rg-tf26-p08`. P9's frontier baselines also used it, so deleting it only stops future re-runs.
- [ ] **If P8 is chosen:** its stretch goal needs a ~30-learner pilot in November.

- [ ] **Mac memory (updated 12:45):**
  - Memory level is 23% (my job-pause line is 25%) and swap is 22.5 of 23.5 GB on this 24 GB Mac.
  - Your VM (`com.apple.Virtualization`, up 7 days, 6.2 GB resident + 9.9 GB compressed) is by far the largest user. CapCut (~2.3 GB) and Brave/Chrome (~5 GB) come next.
  - Namma Space's 3D training is spending 79% of its CPU time in the kernel, i.e. thrashing.
  - Quitting the VM (Docker/OrbStack/UTM) and CapCut while the projects run is the single biggest speed-up. I've already closed the projects' leftover browsers and servers.
- [ ] **India@71 theme pick by 15 Oct (one theme per team):** all three are ✅. T1 nutrition (memo 4.2) is recommended by all three leads; T2 learning (3.9) and T3 financial inclusion (3.9) both recommend T1.
  - T2's honest findings: its intervals are conservative (96.7% coverage of nominal 90%, ±6 pp, in two pre-registered tests), and its allocation gain is not shown. It's the stronger reserve on evidence quality.
  - T3's honest finding: its learned targeting beats the transparent rule only on SYNTHETIC data, so the rule ships, as in T1.
  - If T3 is chosen: team details, a partner bank's financial-inclusion head, and field conversations.
- [ ] **India@71 T1 (✅ Completed — please review):** team names + Team ID for `India71_100_[TeamID].pdf`; a state/district WCD contact for a pilot data extract; a union/worker-association contact for co-design.
- [ ] **EV track pick by 15 Oct (one track per team). Both are ✅ Completed — please review.**
  - **C1 (EV Infra Map, `ev-c1-infra-map-india/`):** memo 4.1/5; astra 70/100. A national charger map validated against official state counts, a purged-backtest VAHAN forecast (error 0.177 vs 0.360 naive), and district supply validated on Chhattisgarh.
  - **C2 (Green Auto LCA, `ev-c2-green-auto-lca/`):** memo 4.0/5.
  - C1's own call: **C1, narrowly** (within rubric noise). It flips to C2 if your team has an LCA person but no GIS/data person.
  - Optional for C1: route the BEE charger-API request via MHI/ICAT.
- [ ] **EV C2:** access to the ISO 14040/14044 standards text (IIT Delhi library or BIS) for the LCA jury Q&A; an environmental/mechanical teammate; team name, Team ID, institution and contacts for the Round-1 header.
- [ ] **InnovateX T2 DustLedger (✅ Completed, documented alternative):** its own memo recommends pitching **T1** at the Delhi zonal.
  - It corrected itself on the record: the CAQM fine is ₹1–2 lakh, not ₹5 lakh; its forecast gain was an oracle (ML loses to persistence for PM2.5); and its self-calibration accuracy claim is withdrawn.
  - Needed only if you choose T2: team fields, a pilot or co-location site by ~20 Oct, and approval for a controlled dust test.
- [ ] **InnovateX T1 JalSakshi (✅ Completed — please review `innovatex-t1-groundwater/deliverables/`):**
  - register for the Delhi zonal by 9 Oct and fill in the team details;
  - a hardware teammate;
  - one timed rehearsal using `presenter-card.pdf`;
  - a pilot contact or letter (e.g. DJB, as the rainwater-harvesting nodal agency);
  - supplier quotes for the parts in `prototype-plan.md`.
- [ ] **Perceptron pick by 12 Oct (one problem per team).** P7, P9, P1, P4, P10, P5, P3, P6 and P8 are ✅ Completed and ready for your review; P2 is still running.
  - **P7 multi-agent allocation:** planning beats the best rule, +3.7 pp under shock and +5.5 pp under shock+drift (30/30 seeds, pre-registered). Its detector spike failed replication. astra hostile score 71/100.
  - **P9 agent guardrail:** on held-out real agent errors, 41% of harmful calls stopped at 2.0% of good calls blocked (30% held for review). astra 62/100; memo 3.8/5.
  - **P1 federated LoRA:** the only method that improves every domain (macro −0.081 vs the starter), at a stated cost on the data-rich domain. astra 68/100 on the draft before its fixes; memo 4.2/5.
  - **P4 order-book regimes:** the most rigorous (sol reproduced it exactly), but the gain is small (−0.0099 log-loss) and not tradable after fees. astra 53/100 before fixes; memo 3.4/5. P4 itself recommends P7 or P9.
  - **P10 trusted text signal:** prediction intervals that keep their promised coverage on messy, manipulated text (89.47% vs a 90% target). Its pre-registered test found the text adds no forecasting value (p = 0.46), so the pitch is trust and coverage guarantees, not alpha. astra 74/100; memo 3.7/5. P10 itself ranks P7 first and P10 a close second.
  - **P5 impact-aware execution:** its headline failed a strict pre-registered replication on 400 fresh seeds (−0.013 bps, CI [−0.029, +0.003]). The abstract is now honestly about measuring your own market impact. astra 3.45/5; P5 recommends against itself.
  - **P3 off-policy evaluation:** on real Open Bandit data (pre-registered), it shows the deployed policy drifted and that a "did it work" dashboard overstated the effect by 29%. Its overlap gate refuses to answer where the logs can't support one. astra 69/100; memo 3.6/5. P3 recommends P7, narrowly.
  - **P6 cross-asset stat arb:** its pre-registered 12-day test passed (+$299/day simulated, 12/12), but only about a quarter of the gain survives strict fills, and it's within noise once shared liquidity is removed. astra 62/100. P6 recommends P7 and offers itself as the fallback for the 4/5/6 group.
  - **P8 misconception tutor:** six pre-registered experiments found no gap vs GPT-5.5 on real data; the exact engine's edge is determinism and modest cost savings. astra 62/100 before revision. P8 recommends against itself.
  - **Note:** P4, P5 and P6 are a "choose exactly one" group, and P4 and P5 both recommend against themselves.
  - The astra scores were given at different stages and the memos are self-scored, so treat them as rough, not a ranking.
  - Whichever you pick: teammates' names for the [TEAM] placeholders, then register by 15 Oct.
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
### 2026-10-04 23:38 IST — Paused by user
- STOP sent to 5 leads (P3, P8, P4, India@71 T3, InnovateX T1) and 4 demo builders.
- Killed by explicit PID: 6 Playwright Chrome roots (all helpers gone), 15 Playwright MCP servers in Techfest worktrees, P7's leftover demo processes, InnovateX T3's dashboard server, and the pollers.
- The watch automation is cleared. Resume tomorrow: re-create the automation, verify DEMO DONE for P3/P8/P4/India@71 T3/InnovateX T1, then the §11 upgrades.
### 2026-10-04 23:23 IST — P5 demo done (8 demos); verify phase begins
- **P5 DEMO DONE (7817564):** smoke PASSED in my clone (replay checks; READY in 0.7 s). The live ABIDES lane was skipped in my clone (ABIDES not fetched there); the lead verified it from a clean worktree. Astra review 13/13.
  - Every screen is labelled SIMULATED (ABIDES).
  - Answer first: E10 −0.013 [−0.029, +0.003], NOT confirmed. Then "the ghost market": twin markets show your own footprint, with a size knob and a live "bring your own seed".
- **Verify phase:** none of the 7 older demos (InnovateX T1–T3, EV C1/C2, India@71 T2, Namma) has §11 packaging (run.sh, SCRIPT, fallback, smoke, astra review). Each gets an upgrade brief as slots free.
  - Order: InnovateX T1 (zonal 10 Oct, live pitch) first, then EV C1, Namma, India@71 T2, EV C2, InnovateX T2, InnovateX T3.
- Slot → InnovateX T1: package the existing JalSakshi demo (pulse flagged; unplug → deferred) to §11, fully offline for the venue.
### 2026-10-04 22:31 IST — Sweep
- The demo queue is empty. P8 and P5 are verified from clean checkouts; their astra demo reviews are running.
- P4: Amendment 3 discloses labeler float-noise ties (4 of 3.0M labels).
### 2026-10-04 22:21 IST — P1 demo done (7 demos); demo queue empty
- **P1 DEMO DONE (17eea3c):** full smoke PASS in my clone (0 failed, 61 s), including the live Flower path, bit-identical to the in-process harness. I used a temporary symlink to the worktree venv, then removed it. Astra review 7/10, 8/8 fixed.
  - Opens REAL: committed 5-seed per-domain bars with paired CIs (−0.081 [−0.093, −0.070]).
  - Crazy element: "Pull the plug". The real SmolLM2-135M trains side by side through Flower's in-process grid; the run holds after round 1 and the judge unplugs any device. Honestly labelled as an in-process node removal.
- Last queued slot → India@71 T3 ("try to break it"; real PMJDY opening).
- Next: once slots free, I check demo_verify myself: InnovateX T1–T3, EV C1/C2, India@71 T2, Namma.
### 2026-10-04 21:48 IST — India@71 T1 demo done (6 demos)
- **India@71 T1 DEMO DONE (1b48399, your India pick):** all 5 smoke steps pass in my clone: data invariants, JS/Python ledger parity, offline check, exporter re-derivation, headless page. Astra review 12/12 plus re-check 6/6.
  - REAL first: Poshan Tracker reports lower wasting than NFHS-5 in 36/36 states; 706 districts (spot-verified 24/24). Then SIMULATED children at REAL Nandurbar and Melghat rates.
  - Crazy element: find every child across departments without pooling names, with knobs for ID loss and typos. Honest about the privacy cost: 3,522 vs 4,063 links at equal precision.
- Slot → P5 demo ("the ghost market" twin, SIMULATED-labelled).
### 2026-10-04 21:39 IST — Sweep
- P4: the abstract now adds "each head alone worse than switching (+0.0138 to +0.0526)". The numbers are in eval/results/v2_holdout_posthoc_heads.json, labelled post hoc.
- India@71 T1: the linkage claim was corrected to a matched-precision comparison (IDs 1,565 / pooled names 4,063 / encoded 3,522 of 4,531). The privacy method recovers fewer links than pooled names, and the proposal now says so.
### 2026-10-04 21:24 IST — P9 demo done (5 demos)
- **P9 DEMO DONE (0834fb2):** smoke ALL PASS in my clone (155 PASS, 0 FAIL). Astra finals-judge review: 12/12 accepted.
  - Real first: a recorded gpt-4o τ-bench harmful write. Tier 0 holds it live; the replayed gpt-4.1-mini judge allows it. 61/120 vs 42/120 harmful calls stopped on 300 real calls, labelled not significant (+15.8 pp, CI −2 to +34).
  - Crazy element: "Hijack the agent". The judge types a support ticket, the scripted agent obeys it, and the committed guard blocks it live. Benign controls are allowed, and one known false block is labelled.
  - Four guard fixes surfaced by demo probing. Committed τ-bench decisions are identical to the pre-demo baseline (verified by me).
- Slot → P4 demo ("the alarm that cries wolf"; Tardis redistribution terms to check).
- Open item: P6's demo commits a raw Tardis quote slice (window_books.npz). Check Tardis' terms before the repo is shared publicly.
### 2026-10-04 21:13 IST — P7 demo done (4 demos)
- **P7 DEMO DONE (Perceptron consensus pick):** smoke 47/47 in my clone (44 s). Astra demo review 7.5/10, all 10 items applied.
  - Opens on REAL NYC July-4 trips: the best rule and the planner run live on identical demand, next to the committed receipts. Surge window 1.40 vs 39.55 lost; +2.52 pp, 20/20.
  - Crazy element: the judge drops a surge on real demand, labelled as an intervention. The honest cell where the planner loses is shown.
- Slot → P8 demo ("ask it again": deterministic engine vs GPT-5.5; Eedi licence check required).
### 2026-10-04 20:52 IST — Sweep
- P9: three demo-driven guard changes (untrusted-text rule, format-insensitive taint, own-record exemption). Each time I verified the committed τ-bench decisions and reasons are identical (991 test / 1,027 dev).
- P1: three demo pass criteria committed at 20:20:49; the validation runs were committed at 20:45:11. All three pass in 5/5 seeds.
### 2026-10-04 20:29 IST — P6 demo done (3 demos)
- **P6 DEMO DONE (74075ed):** smoke 31/31 in my clone (42.9 s, including headless Chrome). Astra demo review plus a re-review, all items fixed.
  - Crazy element: "race the machine". The judge's measured reaction time is scored by the committed simulator against compiled LEV, timed live.
  - Latency knob 10 µs–100 ms on a real Tardis BTC slice. The full-day counters equal the committed walk-forward (V0) and strict (V1) totals.
- Slot → P3 demo ("the evaluator that says I don't know", on real OBD logs).
### 2026-10-04 20:04 IST — Sweep
- P9: a demo-prep probe found an order-id laundering bypass in the retail guard. Fixed with regression tests; I checked that the committed τ-bench decisions are identical (991/991).
- India@71 T1: eval_v2 (infant gate) → rule 0.473 vs programme 0.413 vs ML 0.430, disclosed in the proposal. The PDF is re-rendered at 6 pages and check_docs passes 20/20.
### 2026-10-04 19:58 IST — P2 completed + demo done (19 of 20 Round-1; 2 demos)
- **P2 DONE (5aeb88f), verified:**
  - check_docs OK. Ledger: 2 sol reviews and 3 astra reviews.
  - Sol reproduction 320/320 rows. Abstract 70/100 from astra. Memo 4.2: a close call vs P1, and only one of P1/P2 can be entered.
  - VM `p02-kv-1` confirmed **deallocated** via az; the disk is kept.
- **P2 DEMO DONE (4066d32):** the replay smoke passed in my clone in 10 s. Live checks need the 2.5 GB weights; the lead ran them from a clean clone (20/20 rows).
  - Crazy element: a memory slider. At 10% memory, P2's method recalls a planted fact that the eviction baselines (StreamingLLM, SnapKV) forget. Shown with the honest caveat: on paraphrased questions, longer answers give full 32/48 vs RoD 36/48.
- Slot → P1 demo ("unplug the tablet": a real Flower process kill).
- Correction (appended 19:55 IST, re-checked 19:55 IST): this entry was committed at 19:53:04 IST (git). The "19:58" heading and the "19:57" in the P1 brief were estimated, not read from the clock (PLAYBOOK §6).
### 2026-10-04 19:29 IST — P10 demo done (first of 20)
- **P10 "Break the band" DEMO DONE (74e8dce):** I re-ran demo/smoke.sh and it passes all checks (62 PASS lines). Astra demo review: 78/100, "would lean in: yes".
  - Crazy element: a judge writes a fake pump post. One bot post breaks plain CQR, while the certified band holds.
  - Red team: 0 violations in 2,000 attacks within budget. The badge turns grey beyond k. The footer keeps "text adds no value (p = 0.46)".
- Slot → P9 demo (real τ-bench replay first).
### 2026-10-04 19:14 IST — Sweep
- P2: E6 confirmed the 10-token truncation confound. Full cache 67% vs RoD@10% 75% at max_new=32; the abstract now leads with this.
  - Sol reproduction: 320/320 rows identical. VM deallocated.
- P7: the demo opens on the real NYC July-4 surge.
- India@71 T1: real-first demo, using a state tile grid instead of a boundary map (Survey of India rules).
- P6: demo review triaged; smoke 18/18.
### 2026-10-04 18:26 IST — Sweep
- You asked "why is everyone simulation; will this win?" My answer: not on simulation alone. Round 1 is fine, but the finals need real evidence.
  - PLAYBOOK §11 now says "real data first" (47ac13d).
  - P7 and India@71 T1 were asked to open their demos on real data: the NYC replay and NFHS-5.
- P2: the demo plays back committed results (fp16 weights, fp32 compute in live mode). I asked it to deallocate the VM right after E6 if sol doesn't need it.
### 2026-10-04 17:59 IST — InnovateX T3 completed (18 of 20)
- **InnovateX T3 DONE (d82d80f), verified on main:** check_docs 0 problems (35 fact rows); 85 tests pass; astra and sol reviews in the ledger.
  - Tide model trained only on pre-2024 data: P2 vs P1 −5.2% [−15.9, −0.8], 39/40 (SIMULATED). The litter-counter fix replaced an artefactual 33% with +15.9% (SYNTHETIC).
  - Memo v4 keeps T1 as the zonal pick. The dashboard still needs the §11 demo pieces; it is in the demo-verify list.
- Slot → India@71 T1 demo (your India pick).
### 2026-10-04 17:36 IST — Sweep
- Demo phase running: briefs went to P7, P10 and P6 at 17:28. Each lead spawns one demo builder.
- P7 appended a correction listing the real commit times of its pre-registrations. Every registration still precedes its run.
- InnovateX T3: the lead is adding a check that the committed RESULTS.md matches a fresh results run (the z_review row was stale).
- P2: R1 passed its pre-registered non-inferiority rule. I raised a possible truncation artifact in the full-cache baseline: the answer cap is 10 tokens and 12 misses are a cut-off restated question.
### 2026-10-04 17:18 IST — P8 completed
- **P8 DONE (1a2b1b4), verified on main:** check_docs 143 claims OK; 10 tests.
  - Reviews: astra 23/23, sol 12/12.
  - No gap vs GPT-5.5 (pre-registered). Cascade cost $7.32 → $5.08 per 1,000 diagnoses on tutor-native items.
  - Memo recommends against P8. API spend $19.75.
- 2 leads remain: P2 and InnovateX T3.

### 2026-10-04 16:47 IST — India@71 T2 completed
- **T2 DONE (4c073af), verified on main:** check_docs 17/17; 67 tests; PDF 6 pp Arial.
  - Reviews: astra 24/25 + re-score, sol 12/12.
  - Memo 3.9: it recommends T1.
  - Killed its leftover Playwright Chrome (PID 82640).
- All three India@71 leads now recommend T1.
- No resume (queue gated); 3 leads active.

### 2026-10-04 16:44 IST — Sweep
- P2 identity checks pass (dev seed 100): the non-monotonic recall at 25/50% KV is a real effect of isolated re-prefill, not an artifact.
- India@71 T2 v2 coverage test registered 16:31:04 on fresh seeds 201–230; v1 stands.
- P8 cascade confirmed on prob_pack (H8, registered before the run); consistency measured.

### 2026-10-04 16:31 IST — InnovateX T2 completed
- **IX-T2 DONE (4ea3d82), verified on main:** check_docs 0 problems (5 docs, 25 fact rows); deck, Q&A, card and demo present.
  - Reviews: astra 37 items (32 accepted + 4 partial), sol reproduced the headline numbers.
  - Its memo recommends T1.
  - Killed its leftover Playwright Chrome (PID 58128).
- No resume: only APCTT is queued, and it's gated until 10 Oct.

### 2026-10-04 15:56 IST — P6 completed
- **P6 DONE (378ac26), verified on main:** check_docs OK; 7 tests.
  - Reviews: astra 13 + sol 16 + astra 8, all accepted.
  - Pre-registered pass (+$299/day, 12/12), but about 1/4 survives strict fills. It recommends P7.
  - Its short-lived Azure VM (p06vm, rg-p06-statarb) was deleted at 15:16.
- InnovateX T3 resumed. The queue now holds only APCTT, gated on the 10 Oct data.

### 2026-10-04 15:32 IST — India@71 T3 completed
- **T3 DONE (57dfa7c), verified on main:**
  - check_pdf PASS (6 pp, Arial ≥ 11 pt, 6/6 fonts embedded); check_docs 28/28; 17 tests.
  - Reviews: astra 15 + sol 18, plus a verification round each, all decided.
  - Memo 3.9 vs T1 4.2: it recommends T1.
- InnovateX T2 resumed into the slot.

### 2026-10-04 15:24 IST — Namma Space completed
- **Namma DONE (7be832f), verified on main:** no ⟨⟩ slots; E2E, viewer and degenerate-posing evidence files present.
  - 5 review rows ledgered (astra ADR and R1, sol code, plus sol and astra delta checks).
  - Tests via its venv: marker_scale 2/2, and the nav_eval_v3 contract test OK. Its venv has no pytest, and system Python lacks pycolmap.
- India@71 T2 resumed into the slot.

### 2026-10-04 15:12 IST — Sweep
- `watch.py` now skips STALLED for a lead with a live compute job (Python/Brush/COLMAP) running from its project folder; http servers are excluded. This stops false alarms while a lead waits on its own run.
- India@71 T3 v0.3 corrected test registered 14:57 (commit 14:57:58), before its run.
- Namma deep round: launch the reviews now, refresh Now, and stop the leftover 8080 server.

### 2026-10-04 14:58 IST — EV C1 completed
- **EV C1 DONE (9c9e1e3), verified on main:** check_docs OK (6 docs, 262 rendered keys, 28 fact rows).
  - Reviews: sol 11 items, astra 70/100 with 17 items, all accepted (1 routed to the user).
  - Memo 4.1 vs C2's 4.0: C1, narrowly.
- P8 resumed into the slot.
- **P6:** the pre-registered 12-day test passed. Frozen eval code was unchanged between registration (604f54d) and the run (9cadff6).

### 2026-10-04 14:36 IST — P3 completed
- **P3 DONE (563f013), verified on main:** check_docs PASS (0 untraced numbers); 14 tests.
  - Reviews: astra 59 → 69/100, sol reproduced all 44 abstract numbers; 25 items accepted. Memo 3.6/5; recommends P7 narrowly.
- P2 resumed into the slot, on its Azure CPU VM.
- Verified P6's 12-day pre-registration: code frozen 14:24:02, registered 14:24:44, prior looks disclosed, and no committed result before registration includes May 2026.

### 2026-10-04 14:20 IST — Sweep
- Pre-registration order verified on main:
  - India@71 T3 C6 v0.2: registered 14:00:34 → run 14:03:13 (SYNTHETIC, fresh seeds 10–19).
  - P3 gate validation: registered 14:10:45 → results 14:17:14.
- Namma: Brush run 3 started 14:00 on a verified pose solve (263/263 cameras, ATE 0.07% of the scene). The degenerate sequential-matching model is kept as evidence and is now caught by a sanity gate.
- Deep round EV C1: proposed a criteria→evidence map and appendix tables for a concise Round-1 submission.

### 2026-10-04 14:11 IST — P5 completed
- **P5 DONE (1ebd409), verified on main:** check_docs 237 claims OK; 7 tests; abstract body 895 words.
  - The strict replication (E10, n = 400 fresh seeds) did not confirm the headline; the abstract was reframed accordingly.
  - E7 slope 1.01 [0.55, 1.76], not square-root.
  - Reviews: astra 2.80 → 3.45/5; sol reproduced bit-for-bit; every item accepted. The memo recommends against P5.
- P6 resumed into the slot.

### 2026-10-04 13:52 IST — P10 completed; Namma jetsam diagnosis
- **P10 DONE (47ddf82), verified on main:**
  - Its pre-registered DJIA text test found no evidence that text adds value (p = 0.46); a positive control shows the test detects gains of 11% or more.
  - ACI coverage 89.47% vs the 90% target.
  - 70 tests pass in its venv. Under system Python they fail on `lightgbm`, because there's no dependency manifest. check_drift: no drift; abstract 894 words.
  - Reviews: astra 64 → 74/100, sol exact reproduction; 21 items accepted. Memo 3.7/5.
  - India@71 T3 resumed into the slot.
- **Namma:**
  - Its orchestrator was killed by macOS jetsam at 13:41:13 (kernel log: "killing largest compressed process Python [19913] 101341 MB").
  - Namma traced the cause to its degenerate SfM: the walkable grid's bounds became 4.8 km × 1.4 km, i.e. 2.7 billion cells.
  - Guards are being added.

### 2026-10-04 13:25 IST — Sweep
- **New PLAYBOOK §6 rule (13:06):** timestamps come from the clock. Two leads had written times 7–24 min ahead of it; P5 appended a correction (git commit times are authoritative) and disclosed that its original H1 was registered after launch but before inspection.
- **Pre-registration order verified on main:**
  - P10: registration 12:55 → result 13:04.
  - P3: registration 13:06:47 → run 13:10:59 → results 13:16:04.
  - P5: amendment A1 at 13:13:18, while E10 was still running and unread.
- **Namma:** run 1 killed at 3 h 03 m (memory thrash, no export); run 2 started 13:16 with the GPU held for it. P10 was asked to keep its scorers on CPU.
- **Language audit for the user (read-only, nothing changed):**
  - Python is the right main language in all 20 projects.
  - Second languages are needed only for InnovateX node firmware (C/C++, not yet written) and optional iOS AR (Swift).
  - InnovateX T3 uses Ultralytics YOLO, which is AGPL-3.0.
  - 10 projects have no dependency manifest.

### 2026-10-04 13:05 IST — P1 and P4 completed
- **P1 DONE (9b710f7), verified on main:**
  - 5 paired seeds with node dropout. AnchorLoRA's macro loss beats the starter by −0.081 [−0.093, −0.070], FFA-LoRA by −0.050 and FlexLoRA by −0.083.
  - It improves all 5 domains vs the untuned model; the starter improves only the data-rich one. Stated costs: sample-weighted (micro) loss +0.116, worst-domain loss +0.057.
  - check_claims 12/12; check_numbers PASS. Reviews: sol 13/14, astra 12/12. Memo 4.2/5.
- **P4 DONE (40fccc2), verified on main:**
  - Pre-registered; 22-day holdout; sol reproduced every number exactly.
  - KS-triggered retraining is worse (+0.0268 log-loss, 21/22 days). The volatility-regime gate is better (−0.0099, 22/22). The registered Fixed-Share spike failed H1.
  - Break-even fee 0.132 bps/side vs 1.7–5.0 bps taker fees: not tradable as a taker.
  - check_numbers: 185 numbers OK. astra review 18 items accepted (3 in part); sol 5/5. Memo 3.4/5. P4 itself recommends P7 or P9 over P4.
- P3 and EV C1 resumed into the slots. Neither project left browsers or servers running.

### 2026-10-04 12:52 IST — P9 completed
- **P9 DONE (2462e64), verified on main:** check_docs 22/22; 7 tests pass; abstract 877 words.
  - On 991 held-out real τ-bench write calls (a re-run after the code-review fixes, labelled exploratory), the tuned checker stops 41% [28–55] of harmful calls, blocks 2.0% of good calls and holds 30%.
  - A gpt-4.1-mini judge on a 300-call sample stops 35% while blocking 11.7% of good calls.
  - Blinded astra red team: 82/100 stopped.
  - Reviews: sol 11/11; astra hostile judge 3.10/5, 21/21 accepted. Memo 3.8/5.
- P5 resumed into the slot.
- PLAYBOOK §6: no `git stash` / `--autostash`, since worktrees share one stash list.
  - P9 had popped P7's leftover autostash. That entry is a stale 10:57 partial of `phase-v2c/episodes.csv`; main has the complete file (10:58), so nothing was lost.

### 2026-10-04 12:45 IST — InnovateX T1 completed; 408 storm; memory
- **InnovateX T1 DONE (8c183b9), verified on main:**
  - Zonal deck (9 + 5 backup slides, PDF/PPTX), presenter card, 28-question Q&A prep, offline demo and Round-2 prototype plan (₹11,166/node).
  - gpt-6-astra final-deck review: READY WITH FIXES, 28/28 items handled.
  - 7/7 tests pass. Headline 13.1% = `event_mdape` 13.097 in `eval/results/recharge_v1_evalv2_holdout.json` (simulation stress test).
  - P10 resumed into the slot.
- **12:11 storm:** all 5 leads hit HTTP 408 at once ("timed out reading request body").
  - Each request uploads the whole conversation; long-lived leads are 400k+ tokens (~2 MB per request).
  - Four leads recovered on their own; Namma was nudged at 12:31.
  - `watch.py` now flags a turn that died on an error (DIED) immediately, instead of after 6 min.
  - No lead rotation: the heaviest leads are near done, and fresh queued leads start small.
- **Spot-checks:**
  - P4's pre-registration (11:43) and Amendment 1 (11:58) predate the single holdout run (12:02).
  - P9's held-out test was re-run once after the sol code-review fixes; the abstract discloses it. One stale README line was flagged to P9.
- **Memory:** level 23%, swap 22.5/23.5 GB. Closed IX-T1's and EV C2's leftover Playwright Chromes and the EV C2 dashboard server. Namma's Brush is thrashing (79% kernel time); it decides at 13:15 whether to restart with lower memory.

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
