# Portfolio — Supervisor thought node

> The Supervisor's journal for all 20 projects. Project journals live in `<folder>/thought_node.md`. Method: [PLAYBOOK.md](PLAYBOOK.md). Morning summary: `MORNING_REPORT.md` (pushed by 08:30 IST, 4 Oct).

## Inbox
<!-- User → Supervisor. -->
- _(empty)_

## Now (07:25 IST, 4 Oct)
- **Phase:** Overnight run, final hour. Every lead is writing its morning package; push cut-off 08:15 IST, report 08:30.
- **Doing:** Sweeps every 15 min — status checks, restarting dead leads, gap nudges, hallucination spot-checks.
- **Next:** 08:15 final pull → `MORNING_REPORT.md` (delivered work, real numbers, rankings per competition, what needs you) → lift Lean Mode after 08:30.
- **Lean Mode (since 05:50):** no sub-agents/child sessions, small requests, no big downloads. Reason: the shared uplink saturated (~55 KB/s per stream) and model calls failed with `408 Timed out reading request body` — 405 of ~408 errors overnight. Errors fell from ~20 to ~2 per 10 min once it took effect.

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

## Portfolio (07:25 IST)
| Project | Status | Note |
|---|---|---|
| perceptron-p01-federated-lora | 🟢 | Landscape (42 verified sources), components, contracts, first results. Missing ADR, abstract, memo. |
| perceptron-p02-kv-cache | 🔴 | Research agents all died on 408s; little pushed. Nudged 07:22. |
| perceptron-p03-off-policy-eval | 🟢 | Landscape, components, contracts, ADR, abstract (894 words). 30-seed bank running; memo + numbers by 08:15. |
| perceptron-p04-lob-regimes | 🟢 | Full package except abstract. Memo v1 4.2/5; real Binance runs. |
| perceptron-p05-impact-execution | 🟠 | Eval + code; docs missing. Nudged 07:22. |
| perceptron-p06-stat-arb | 🟢 | Full package incl. abstract; memo v1 (honest: edge not yet significant). |
| perceptron-p07-multi-agent-allocation | 🟢 | Landscape, components, ADR, harness; journal stale. Nudged 07:22. |
| perceptron-p08-misconception-tutor | 🟢 | Full package + memo; real Eedi numbers. |
| perceptron-p09-agent-guardrail | 🟠 | Contracts, eval, code (local models). Docs missing. Nudged 07:22. |
| perceptron-p10-trusted-text-signal | 🟠 | Contracts, eval, code. Docs missing. Nudged 07:22. |
| apctt-trl-assessor | 🔴 | Died on 408s (02:30, 05:51); restarted 07:10. |
| ev-c1-infra-map-india | 🟠 | Code + data work; docs missing. Nudged 07:22. |
| ev-c2-green-auto-lca | 🟠 | Cited factor DB, benchmarks, engine; docs partial. Nudged 07:22. |
| namma-space | 🟠 | Capture SOP published; first splat trained on M5; docs missing. Nudged 07:22. |
| india71-t1-nutrition | 🔴 | Died 06:07 with uncommitted work; restarted 07:10. |
| india71-t2-learning | 🟢 | Components, contracts, ADR, proposal skeleton, memo. Missing landscape. |
| india71-t3-finance | 🟠 | Components, contracts, skeleton. Died 06:05; restarted 07:10. |
| innovatex-t1-groundwater | 🟢 | Landscape, contracts, real Delhi DWLR data (185 stations). Missing components, ADR, pitch. Nudged 07:22. |
| innovatex-t2-aqi | 🔴 | Died 06:17 with uncommitted research; restarted 07:10. |
| innovatex-t3-coastal-plastic | 🟢 | Most complete: landscape, ADR, twin sim (real ERA5/tides), MRV dashboard, prototype plan. |

## Key decisions
- 2026-10-04 — Build all 20 problem statements; submit the strongest per competition within the submission limits.
- 2026-10-04 — One private monorepo, trunk-based, one folder per project; every session pushes to `main`.
- 2026-10-04 — No caps on agents or sessions (user directive) — suspended 05:50–08:30 by Lean Mode (network).
- 2026-10-04 — Research uses primary sources (papers, code, company launches, X/Twitter) and tracks what companies ship today (user directive).
- 2026-10-04 — Overnight: nobody asks the user anything; morning package due 08:30 IST (user directive).
- 2026-10-04 05:50 — Lean Mode for all leads until 08:30: the 408 timeouts came from uplink saturation, not from the work itself.
- 2026-10-04 07:20 — `models.github.ai` returns stub "OK" responses from this machine (found by P8, confirmed by P9). Any LLM-dependent number must come from a real model (local MLX/Ollama or Azure OpenAI).

## Log
### 2026-10-04 07:25 IST — Sweep
76 commits on main. Restarted 4 dead leads at 07:10 (APCTT, India@71 T1/T3, InnovateX T2), each with uncommitted work to secure first. Sent 13 gap-specific alignment nudges at 07:22. Spot-check: 27/28 sampled citation URLs resolve (the 1 failure is a 403 bot-block by Economic Times). Memos in: P4 (4.2/5), P6, P8, India@71 T2.
### 2026-10-04 05:50 IST — Lean Mode
Diagnosed the 408 storm from session event logs: ~100 sub-agents plus multi-GB downloads saturated the uplink; most research agents died at 0 turns; main had ~12 commits after 3.5 h. Broadcast Lean Mode to all 20 leads; throughput recovered (463 turns vs 19 errors in the next 20 min).
### 2026-10-04 01:55 IST — Launch
Repo created with the playbook, official briefs and 20 seeded project journals. Lead sessions spawned in autopilot.
