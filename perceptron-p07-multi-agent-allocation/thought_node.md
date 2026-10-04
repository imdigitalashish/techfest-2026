# Perceptron P7 · Splitting a shared resource when demand keeps changing — Thought Node

> Journal for `perceptron-p07-multi-agent-allocation/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
_Updated 2026-10-04 07:30 IST._
- **Phase:** 4–6. The walking skeleton and eval harness are built, and there are **held-out MVP numbers**: look-ahead beats the best rule on 10/10 seeds under shock and under shock+drift. The first ratchet is done. Abstract v0.2 is written (896 words).
- **Plan:** PettingZoo dispatch simulator → 3 rule-based allocators vs a look-ahead MPC (EWMA or change-aware forecaster) vs a clairvoyant oracle → paired statistics on frozen seeds → spike = regime-aware forecasting, tested along the lead-time/patience axis ([ADR 001](architecture/adr/001-spike.md)).
- **Doing:** morning package complete and pushed. Next is the P=3 patience sweep to test H1. No sub-agents (Supervisor lean mode).
- **Next (ordered):**
  2. Run the patience sweep (P=3 vs 10) to test hypothesis H1.
  3. Write contract tests: PettingZoo `parallel_api_test`; core ≡ wrapper; conservation.
  4. Get an independent rubber-duck review of ADR 001 and the abstract once sub-agents are allowed.
  5. Re-run the failed research threads (compute-cluster papers, social/competitions).
  6. Build the RL comparator (TorchRL MAPPO).
  7. Continue the ratchet: spatial pooling, BOCPD.
  8. Build the demo dashboard.
  9. Move long sweeps to an Azure VM (subscription active).
- **Needs from user:** register by 15 Oct (after the 12 Oct selection); teammates' names and skills for the team-fit section.
- **Risks:**
  - The detector's end-to-end value may be small when lead time ≤ patience. The pilot suggests exactly this, so the spike is framed as a falsifiable phase diagram.
  - "MPC beats rules" alone is known (Iglesias 2018).
  - The data is synthetic; mitigation is a real-trace replay.
  - CPU contention on the shared Mac slows sweeps.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 7 — Splitting a Shared Resource When Demand Keeps Changing** (Theme 4: Agents That Compete, Cooperate, and Adapt — the theme's only problem)
- **Context:** Delivery fleets, compute clusters, or robot swarms must divide limited resources among agents while demand shifts unpredictably.
- **Challenge:** Build a multi-agent system that reallocates resources as demand shifts, using some form of look-ahead rather than a fixed static policy.
- **Starter resources:** An open multi-agent simulation environment (e.g. a grid-world dispatch simulator, or PettingZoo-based environment) provided or pointed to by organizers.
- **Minimum Viable:** implement a rule-based baseline allocator; build one agent (RL or planning-based) that outperforms it when demand suddenly shifts.
- **Stretch goals:** handle both an abrupt shock and a gradual drift in the same run; evaluate over long horizons, not just short episodes.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Environments and libraries: PettingZoo, VMAS, BenchMARL / TorchRL; algorithms MAPPO, IPPO, QMIX.
- Look-ahead: model-predictive control / rolling-horizon planning on demand forecasts, MCTS; detecting non-stationarity.
- Domains to borrow from: ride-hailing and fleet rebalancing; cluster schedulers and autoscalers (the user's large-scale-systems background is an edge here).
- What companies ship: dispatch and rebalancing systems at ride-hailing/delivery companies; cloud autoscaling and scheduling papers.

## Key decisions
- 2026-10-04 — We build our own PettingZoo ParallelEnv (numpy core) rather than adopt RL4AMoD or VMAS. Reasons: speed for many seeds × long horizons, labelled shocks, and MIT-only dependencies ([landscape §5](research/landscape.md)).
- 2026-10-04 — Same-zone FIFO matching is fixed inside the simulator for every policy, so policies differ **only** in where idle units go.
- 2026-10-04 — Spike = regime-aware look-ahead: C4 + C5 feeding C6, tested along the lead-time/patience axis with the falsifiable hypothesis H1 ([ADR 001](architecture/adr/001-spike.md)).
- 2026-10-04 — Seeds 100+ are frozen test seeds; seeds 0–99 are for tuning and the ratchet. Policies are paired by seed (common random numbers).
- 2026-10-04 — MPC LP: H=6, HiGHS interior-point. The benchmark gave 17.7 ms at H=6 and 26.4 ms at H=8 (default HiGHS: 25.0 / 33.0 ms).
- 2026-10-04 — Lean mode (Supervisor, 05:50): no sub-agents. ADR 001's antithesis is therefore labelled self-critique; an independent review is queued.

## Components
Details: [architecture/components.md](architecture/components.md) · contracts: [architecture/contracts/contracts.py](architecture/contracts/contracts.py)

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Simulator (+ PettingZoo wrapper) | targets (K,) → StepInfo; FleetState | own numpy core | — | built | steps/s; determinism, conservation |
| C2 | Scenario generator | config, seed → DemandTrace + labels | own parametric model (synthetic) | — | built | rate fidelity |
| C3 | Nowcaster | counts → level | EWMA / moving average | — | built | nowcast MAE |
| C4 | Change detector | counts, expected → alarm, onset, post-change rate | two-sided Poisson CUSUM | **yes** | built, ratchet v1 | delay at fixed ARL₀; F1 with margin |
| C5 | Forecaster | observe / forecast(t, H) → mean (H, Z) | deseasonalised EWMA | **yes** | built, ratchet v1 | frozen `eval.py` score (MAE_all + MAE_post_shock) |
| C6 | MPC planner | idle, incoming, queue, demand → Plan (flows, duals) | time-expanded LP, HiGHS | — | built | served fraction under the oracle forecast; p99 latency |
| C7 | Coordinator | flows → per-unit orders | lowest-index pick / Hungarian | (B later) | built | assignment cost ratio |
| C8 | RL comparator | per-unit obs → Discrete(Z) | MAPPO / IPPO (TorchRL) | — | planned | served fraction on test seeds |
| C9 | Rule-based baselines | FleetState → targets | static, greedy, reactive | — | built | end-to-end |
| C10 | Eval harness + stats | jobs → episodes.csv → summary.md | own (CRN, bootstrap, Wilcoxon + Holm) | — | built | CI half-width |
| C11 | Oracle | true rates → Forecast | MPC on true rates | — | built | — |
| C12 | Demo dashboard | sim stream → UI, click-to-shock | — | — | planned | fps / latency |

## Selection memo
_First version, 4 Oct 07:35 IST; final by 12 Oct. Scores 1–5._
- **Winnability — 4.** The MVP was reached overnight. On held-out seeds 100–109, the look-ahead MPC beats the best rule on 10/10 seeds: +3.9 pp served under shock (CI [+3.3, +4.6]) and +5.4 pp under shock+drift ([+5.2, +5.7]), losing 82–121 fewer requests in the two hours after the shock (`eval/results/mvp-v1/summary.md`). P7 is the only problem in Theme 4, so it probably draws many "RL on PettingZoo" entries. We separate ourselves through evaluation rigour (frozen seeds, paired CIs, oracle regret) and a falsifiable lead-time law.
- **Innovation headroom — 3.5.**
  - The spike: a statistical change detector inside the forecaster that feeds the rolling-horizon planner, plus a lost ≈ Δλ·max(0, d + L − P) "when look-ahead pays" phase diagram.
  - For: the first ratchet run beats the EWMA reference on the isolated metric (0.4154 vs 0.4385; detection in ~5.6 steps).
  - Against: the pilot shows little *end-to-end* gain when lead time ≤ patience, and "MPC beats rules" alone is known (Iglesias 2018).
  - Second spike candidate: LP dual-price (market-style) decentralised coordination.
- **Feasibility — 5.** Simulator, baselines, MPC, harness, statistics and the ratchet already run on the M5 CPU; no GPU or data download is needed. The RL comparator is optional. Everything user-dependent can finish before 17 Nov.
- **Demo strength — 4.** A live grid where a judge clicks to inject a shock: the detector fires, units pre-position and the baselines lag, with live served-fraction and CI panels. Less flashy than a 3D or LLM demo, but very legible.
- **Fit with the user's strengths — 5.** This is autoscaling and dispatch: lead time = cold start, patience = timeout. Large-scale systems and optimisation are Ashish's home turf, and the compute-cluster instantiation maps directly.
- **Biggest risk:** the innovation could shrink to "MPC beats rules" if H1 fails. Judges may also call synthetic demand a toy. Mitigations: the phase diagram either way, real-trace replay (NYC TLC), and the RL comparator.
- **One-line pitch:** "Dispatchers and autoscalers react one lead time too late. We detect demand regime changes statistically, re-plan over the lead time, and prove with frozen-seed CIs exactly when look-ahead pays."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:03 IST — Phase 0 read; research fan-out
Read PLAYBOOK, this node's brief and `_briefs/perceptron.txt`; the verbatim P7 brief matches the seed. Launched 7 research workers: fleet papers, non-stationarity, compute autoscaling, code/envs/data, companies, social/competitions, evaluation methodology.

### 2026-10-04 02:56–05:02 IST — Network saturation
- Workers failed at turn 0 with HTTP 408; the first `uv pip install` timed out.
- Relaunched narrow workers with incremental writes. Four partial raw files survived in `research/raw/`: fleet (15 sources), non-stationarity (6), companies (9), evaluation + envs. The other workers died.
- PettingZoo 1.27.0 and Gymnasium 1.3.0 installed into `.venv` (verified by import).

### 2026-10-04 05:02–06:20 IST — Walking skeleton built (lead, directly)
- Built `contracts.py` v1, the scenario generator (shock, drift, spikes, over-dispersion, labelled change points, common random numbers), the numpy simulator core plus PettingZoo wrapper, the Poisson CUSUM, the forecasters, the time-expanded MPC LP, the coordinator, 6 policies and the harness.
- 05:50: Supervisor lean mode acknowledged; no new sub-agents since.

### 2026-10-04 06:20 IST — Pilot (indicative, single seed, superseded)
- Setup: seed 0, shock, 1440 steps, K=40, P=10, at the *pre-change* planner settings (H=8, default HiGHS).
- Served fraction: static 0.879 · greedy 0.933 · reactive 0.927 · mpc-ewma 0.977 · mpc-cusum 0.977 · oracle 0.976.
- Shock-window served: 0.741 · 0.857 · 0.814 · 0.886 · 0.889 · 0.884.
- Lesson: look-ahead *planning* carries the gain at L ≤ P; forecast quality (even clairvoyance) barely matters there. That led to ADR 001's lead-time/patience framing.
- These numbers come from console output and are not reproducible at current defaults (H=6, IPM). They are superseded by mvp-v1.

### 2026-10-04 06:25–06:50 IST — Speed, metric fix, grid relaunch
- LP benchmark: HiGHS-IPM takes 17.7 ms at H=6 vs 25.0 ms with default HiGHS. Adopted H=6 + IPM.
- `recover_steps` changed to an absolute 0.90 served bar. The old relative bar penalised better policies.
- The first grid was killed: other projects keep the load average at 35–43, so my workers got ~1.4 CPUs. The harness now writes rows incrementally.
- Relaunched: `.venv/bin/python -m eval.harness --scenarios shock shock+drift --seeds 100-109 --horizon 1440 --workers 10 --out eval/results/mvp-v1`

### 2026-10-04 06:40–07:20 IST — Package documents
- Wrote research/landscape.md (cited, with "What companies ship today" and explicit coverage gaps), architecture/components.md, ADR 001, deliverables/round1-abstract.md (v0.1) and deliverables/architecture.md.

### 2026-10-04 07:12–07:19 IST — First auto-research ratchet (C4+C5)
- Run with: `python -m components.forecasting.autoresearch.eval <module:factory>` (frozen; dev seeds 0–19).
- EWMA reference: 0.4385.
- v0, CUSUM jump-restart: 0.4927. It detects in 5.5 steps, but the post-shock error is worse.
- **v1, running post-change mean: 0.4154 — kept.** It beats the EWMA reference.
- v2 (δ=0.5): 0.4710, reverted. v3 (δ=0.5, h=6): 0.4410, reverted.
- Ledger: `components/forecasting/autoresearch/results.tsv`.

### 2026-10-04 07:22 IST — Supervisor alignment check
Agreed: refresh Now/Log first, then add numbers and the memo. Done in this update.

### 2026-10-04 07:40–07:55 IST — Held-out MVP results (mvp-v1)
- Reproduce: `.venv/bin/python -m eval.harness --scenarios shock shock+drift --seeds 100-109 --horizon 1440 --workers 10 --out eval/results/mvp-v1 && .venv/bin/python -m eval.stats eval/results/mvp-v1`. Settings: K=40, P=10, H=6, 25 zones.
- **shock**, served fraction: static 0.866 · greedy 0.910 · reactive 0.904 · mpc-ewma 0.950 · mpc-cusum 0.949 · oracle 0.948.
  - mpc-ewma vs the best rule (greedy): +3.9 pp [+3.3, +4.6], 10/10 seeds, Wilcoxon p=0.002.
  - Requests lost in the 120 steps after onset: 355 → 274.
- **shock+drift**, served fraction: static 0.753 · greedy 0.739 · reactive 0.882 · mpc-ewma 0.936 · mpc-cusum 0.934 · oracle 0.935.
  - Against the best rule (reactive): +5.4 pp [+5.2, +5.7] (mpc-ewma) and +5.2 pp [+5.0, +5.4] (mpc-cusum), 10/10 seeds each.
  - Lost after onset: 455 → 334 / 351.
- **Interpretation:**
  - The look-ahead *planner* carries the gain.
  - At P=10, forecasts don't matter: oracle ≈ EWMA ≈ CUSUM. This supports ADR 001's antithesis and the lead-time/patience framing.
  - The greedy local rule collapses under drift (0.739), a nice multi-agent coordination point.
- **Statistics caveat:** with n=10, Holm correction over all 28 paired tests per scenario gives a smallest adjusted p of 0.068. The pre-registered primary test (served fraction, look-ahead vs best rule) has p=0.002. ≥20 test seeds are needed for family-wide significance; that is planned.
- Updated: abstract v0.2 (numbers in, 896 words), ADR 001 evidence table, selection memo.
