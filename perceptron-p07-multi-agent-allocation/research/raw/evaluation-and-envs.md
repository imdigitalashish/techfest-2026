# Evaluation Methodology & Environments — Research Notes (Perceptron P07)

**Scope:** Perceptron Hackathon 2026 (IIT Bombay x Optiver), Problem 7 — multi-agent
resource reallocation under shifting demand (zone grid, travel delays, Poisson demand
with shocks/drift, queue abandonment). Judges include Optiver; 15% of Round-1 marks =
"rigor of evaluation plan".

**Access date for all sources below: 2026-10-04.** Status: IN PROGRESS (being written incrementally).

Network conditions: slow/flaky (10-20s/request). Cap ~12 sources. Only sources actually
opened this session are cited with facts; everything else is listed under UNVERIFIED leads.

---

## TL;DR

_(pending — filled in after sources gathered)_

---

## Sources table

| # | Title/Repo | Type | Link | Status |
|---|------------|------|------|--------|
| A1 | Agarwal, Schwarzer, Castro, Courville, Bellemare — "Deep RL at the Edge of the Statistical Precipice" (NeurIPS 2021, Outstanding Paper) | Paper | arxiv.org/abs/2108.13264 | OPENED (via arXiv API, abstract + metadata) |
| A2 | Gorsane, Mahjoub, de Kock, Dubb, Singh, Pretorius — "Towards a Standardised Performance Evaluation Protocol for Cooperative MARL" (NeurIPS 2022) | Paper | arxiv.org/abs/2209.10485 | OPENED (via arXiv API, abstract + metadata) |
| A3 | van den Burg, Williams — "An Evaluation of Change Point Detection Algorithms" | Paper | arxiv.org/abs/2003.06222 | OPENED (abstract via arXiv API; full text via ar5iv pending) |

---

## Notes

### A1 — Agarwal et al. 2021, arXiv:2108.13264 (opened via export.arxiv.org/api/query, 2026-10-04)
- v4, published 2021-08-30, last revised 2022-01-05. **Outstanding Paper Award at NeurIPS 2021.** Website: agarwl.github.io/rliable. 28 pages, 33 figures.
- Core claim (verbatim from abstract): most deep RL papers compare **point estimates** (mean/median) across tasks "ignoring the statistical uncertainty implied by the use of a finite number of training runs," and this is exacerbated by compute-heavy benchmarks (e.g., Atari 100k) pushing toward very few runs/task.
- Proposed fixes (verbatim/paraphrased from abstract): report **interval estimates** of aggregate performance; use **performance profiles** to show variability across runs/tasks; use more robust/efficient aggregate metrics, in particular the **interquartile mean (IQM)**, to shrink uncertainty vs. mean/median at the same sample size.
- They re-analyze existing published results on ALE, Procgen, DeepMind Control Suite and find discrepancies vs. the original point-estimate-based conclusions — i.e., published rankings change once uncertainty is accounted for.
- Open-source library released alongside: **rliable** (see Environments section below for repo facts).
- Authors: Rishabh Agarwal, Max Schwarzer, Pablo Samuel Castro, Aaron Courville, Marc G. Bellemare. Categories: cs.LG, cs.AI, stat.ME, stat.ML — i.e., explicitly framed as a statistics-methodology paper, not just an RL paper, which matters for Optiver judging.

### A2 — Gorsane et al. 2022, arXiv:2209.10485 (opened via export.arxiv.org/api/query, 2026-10-04)
- v1, published 2022-09-21. Published at NeurIPS 2022. 43 pages, 21 figures, 8 tables. Project site: sites.google.com/view/marl-standard-protocol (meta-analysis data released there; not opened this session).
- Meta-analysis of **75 cooperative-MARL papers (2016–2022)** evaluation methodologies; abstract states this reveals "worrying trends that put into question the true rate of progress" in the field.
- Explicitly builds on single-agent RL evaluation literature (i.e., directly extends Agarwal et al.'s line of argument to the multi-agent setting) and proposes a **standardised performance evaluation protocol for cooperative MARL** combining meta-analysis recommendations with "novel insights."
- Authors: Rihab Gorsane, Omayma Mahjoub, Ruan de Kock, Roland Dubb, Siddarth Singh, Arnu Pretorius (InstaDeep-affiliated MARL group). Categories: cs.LG, cs.AI, cs.GL, cs.MA.
- **Gap:** abstract alone does not give the exact protocol steps (number of seeds, specific stats tests) — would need full text/project site for that; not opened this session (budget). Flagged as UNVERIFIED-detail (title/claims verified, internal protocol specifics not pulled).

### A3 — van den Burg & Williams 2020, arXiv:2003.06222 (opened via export.arxiv.org/api/query, 2026-10-04; see below for full-text follow-up)
- v3, originally published 2020-03-13, revised 2022-02-12. Code/data: github.com/alan-turing-institute/TCPDBench (not opened this session).
- Introduces **TCPD**: a curated dataset of **37 real-world time series**, each annotated by **5 independent human annotators** for change-point presence/location, used to measure inter-annotator consistency and to benchmark **14 change-point detection algorithms**.
- Key abstract claim directly relevant to us: prior CPD evaluation relied on simulated data or a handful of series with "unreliable ground truth" — motivates needing proper metrics under multiple/noisy ground-truth annotations (relevant to how we'd score "shock/drift onset detection" if we build a change-point-style diagnostic for our post-shock recovery analysis).
- **Formulas for "F1 with margin" and "cover metric" not yet pulled from abstract** — abstract doesn't state them explicitly. Follow-up fetch of ar5iv/PDF needed (see below).

---

## Recommended evaluation protocol

_(pending — concrete protocol with metrics/formulas, seeds, horizon, stats tests, anti-gaming)_

---

## Environments table

(All facts below pulled live via `https://api.github.com/repos/OWNER/REPO`, opened 2026-10-04. Stars/pushed_at are snapshot values as of that call.)

| Repo (as queried) | Resolved slug | Stars | Last push | License | Fit for us |
|---|---|---|---|---|---|
| Farama-Foundation/PettingZoo | same | 3524 | 2026-10-03T00:10:56Z | MIT | Our base API family (ParallelEnv). Extremely active (pushed same week), largest community of the lot — safest long-term dependency to build our custom env against. |
| proroba/VMAS (as given) | **proroklab/VectorizedMultiAgentSimulator** | 617 | 2026-05-19T22:19:49Z | GPL-3.0 | Vectorized (GPU/torch) 2D physics multi-robot sim — fast parallel rollout for many seeds, but physics-engine framing is a poor match for a zone/queue dispatch model; GPL-3.0 is a copyleft constraint to note if we'd vendor code. Mainly useful as a reference for *vectorized* seed-parallel rollout design, not as our base env. |
| facebookresearch/BenchMARL | same | 668 | 2026-02-07T16:00:29Z | MIT | A benchmarking *harness* (algorithm x task x seed sweep runner) built on TorchRL — relevant as a design reference for how to structure our seed-sweep/eval harness, not an env itself. |
| pytorch/rl (TorchRL) | same | 3589 | 2026-10-03T20:06:47Z | MIT | RL algorithm library (PPO etc.), not an env. Candidate for implementing our RL baseline agent if we want a maintained, actively-pushed (same week) library rather than hand-rolling PPO. |
| FLAIROx/JaxMARL (as given) | **org moved → bold-lab-ai/JaxMARL** (GitHub 301 redirect confirmed live) | 854 | 2026-09-10T09:18:10Z | Apache-2.0 | JAX-based MARL envs + baselines, very fast (JIT/vmap) for huge seed counts at 10^4-10^5 steps — strong fit *if* we're willing to reimplement our zone-dispatch env in JAX for speed; otherwise just a speed benchmark reference. Note the org rename for citation hygiene. |
| semitable/robotic-warehouse (RWARE) | same | 439 | 2024-09-15T17:05:19Z | MIT | Closest existing *off-the-shelf* analogue to our problem: grid warehouse, multi-agent, PettingZoo-compatible, agents move to fulfil shifting pick requests. Good for sanity-checking our env design conventions, but no built-in travel-time/queueing/Poisson-shock demand model — not pushed in >1 year (2024-09-15), so treat as a stable-but-slow-moving reference, not a live dependency. |
| Cognitive-AI-Systems/pogema | same | 300 | 2026-09-14T11:58:10Z | MIT | Partially-observable grid MAPF (multi-agent pathfinding), ICLR-2025 paper. Relevant only for the *travel/congestion* sub-problem (agents navigating a grid without collisions), not for demand/queueing — could inform our "travel delay" layer if we add explicit pathfinding, but is not an allocation/dispatch benchmark per se. |
| google/rliable (as given) | **google-research/rliable** | 879 | 2024-08-12T20:48:27Z | Apache-2.0 | THE stats toolkit for Part A (IQM, stratified bootstrap CIs, performance profiles, probability-of-improvement) — directly reusable for our protocol's plotting/CI layer. Description self-identifies as "NeurIPS'21 Outstanding Paper" library "even with only a handful of seeds," i.e. designed for exactly our many-seeds-but-not-infinite situation. Not pushed in >1 year (last 2024-08-12) — stable/maintenance mode, still fine to depend on. |
| AMoD repo by DanieleGammelli | **DanieleGammelli/gnn-rl-for-amod** (primary) + **DanieleGammelli/graph-meta-rl-for-amod** (secondary) | 84 / 16 | 2021-04-28T11:21:40Z / 2022-03-03T22:59:13Z | MIT / MIT | Direct domain analogue: "Graph Neural Network Reinforcement Learning for Autonomous Mobility-on-Demand" (gnn-rl-for-amod) and its meta-RL/transfer follow-up (graph-meta-rl-for-amod, "...Transferable Autonomous Mobility-on-Demand") — AMoD = fleet rebalancing under shifting demand, i.e. the same structural problem as ours (look-ahead/anticipatory rebalancing vs reactive dispatch). Both low-star and not pushed in 3-4+ years — treat as algorithmic/modeling inspiration (GNN state representation, anticipatory rebalancing objective), not as a maintained dependency. Full GitHub user search for `user:DanieleGammelli` returned 12 repos total; these two are the only AMoD-named ones. |

---

## UNVERIFIED leads

_(pending)_
