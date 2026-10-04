# Perceptron P7 · Splitting a shared resource when demand keeps changing — Thought Node

> Journal for `perceptron-p07-multi-agent-allocation/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
_Updated 2026-10-04 17:30 IST._
- **Phase:** winning demo (PLAYBOOK §11; Supervisor, 17:28). The Round-1 DoD is complete (11:30).
- **Doing:**
  - Child session [P7 demo builder](ghapp://sessions/244315d0-41b1-4804-89fd-4975e72ceaa5), in plan mode. It proposes the "crazy" element first, I approve, then it builds `demo/` (run.sh, SCRIPT.md, fallback/, smoke.sh).
  - Starting hypothesis: "Break it yourself" — click-to-shock on a live city; rule vs planner side by side on identical demand; lead-time / patience / forecast-trust knobs; the live run bridged to the committed 20-seed (L,P) result; NYC July-4 replay; honest panel.
- **Next:**
  1. Approve or redirect the builder's plan.
  2. When built, spawn the gpt-6-astra "judge watching the demo" review (≤ 2 child sessions).
  3. Verify `demo/run.sh` and `demo/smoke.sh` from a fresh clone.
  4. Message "DEMO DONE".
  - October (after the 12 Oct pick): run the Addendum B/B1 trust test (seeds 300–329); mechanism test; RL comparator.
- **Needs from user:** register by 15 Oct; teammates' names and skills (`[TEAM-1..3]` in the abstract).
- **Risks:**
  - A live single run can contradict the 30-seed mean. Mitigation: label "live, 1 run" and show the committed CI beside it.
  - Never claim pre-positioning before an unforecastable shock.

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
| C4 | Change detector | counts, expected → alarm, onset, post-change rate | two-sided Poisson CUSUM | input to spike | built, ratchet v1; restart role failed pre-registered replication | delay at fixed ARL₀; F1 with margin |
| C5 | Forecaster + **trust gate** | observe / forecast(t, H) → mean (H, Z); planner sees trust × mean | deseasonalised EWMA | **yes (trust gate)** | built; fixed-trust sweep done (exploratory) | served fraction (decision loss), not forecast error |
| C6 | MPC planner | idle, incoming, queue, demand → Plan (flows, duals) | time-expanded LP, HiGHS | — | built | served fraction under the oracle forecast; p99 latency |
| C7 | Coordinator | flows → per-unit orders | lowest-index pick / Hungarian | (B later) | built | assignment cost ratio |
| C8 | RL comparator | per-unit obs → Discrete(Z) | MAPPO / IPPO (TorchRL) | — | planned | served fraction on test seeds |
| C9 | Rule-based baselines | FleetState → targets | static, greedy, reactive | — | built | end-to-end |
| C10 | Eval harness + stats | jobs → episodes.csv → summary.md | own (CRN, bootstrap, Wilcoxon + Holm) | — | built | CI half-width |
| C11 | Oracle | true rates → Forecast | MPC on true rates | — | built | — |
| C12 | Demo dashboard | sim stream → UI, click-to-shock | — | — | planned | fps / latency |

## Selection memo
_**Final for the 12 Oct pick** (2026-10-04 10:55 IST); supersedes the 07:35 first version. Scores 1–5, each with its evidence._
- **Winnability — 4.**
  - For: the pre-registered confirmatory test is decisive. MPC beats the reference rule (fixed on tuning seeds) in 6/6 scenarios on 30/30 fresh seeds, Holm p = 1.1e-8: shock +3.7 pp [+3.3, +4.2], shock+drift +5.5 [+5.4, +5.6] (`eval/results/mvp-v2/confirm.md`).
  - For: both stretch goals are done — week +6.3 pp (10/10 seeds) and month +6.4 pp (4/4).
  - For: the NYC real-trace replay gives +2.5 pp (20/20).
  - For: five reviews are recorded. The independent hostile score on the final abstract is 71/100 (gpt-6-astra), up from 48/100 for v0.2, and every headline number was independently reproduced (gpt-6-sol). That rigour (pre-registration, ablations, honest negatives) is rare among hackathon entries.
  - Against: "MPC beats heuristics" alone is known (Iglesias 2018).
- **Innovation headroom — 3** (was 3.5).
  - The detector spike as built **failed its pre-registered replication**: it adds losses at (1,10) and (8,10).
  - The new spike, decision-aware forecast trust, rests on a measured counter-intuitive finding: a *better* forecast (even the true rates) lowered service by 1.1–1.5 pp at long lead times, and a queue-only planner beat forecast planners under pure shocks.
  - The idea has prior art (Smart Predict-then-Optimize 2022; decision-focused learning 2019). Our novelty is narrow: regime-gated trust in lead-time-aware dispatch, plus the (L, P) map. It is untested until the pre-registered trust test.
- **Feasibility — 5.** Everything runs on the M5 CPU. A full pre-registered 1440-episode grid takes ~15 min; a week-long run takes 2.5 min. No GPU or large data is needed. RL is optional. All user-dependent work can be done before 17 Nov.
- **Demo strength — 4.** A click-to-shock live grid; the NYC July-4 replay (1.4 vs 39.6 requests lost in the surge window); the (L, P) heatmap; the service-vs-movement Pareto plot; the week-long panel where the greedy rule decays from 91% to 47% served.
- **Fit with the user's strengths — 5.** The mapping is autoscaling (L = cold start, P = request timeout) and dispatch (L = travel, P = patience), squarely in large-scale systems plus optimisation.
- **Biggest risk:** judges see "MPC beats rules" as incremental, and the spike is a plan rather than a result by 31 Oct. Mitigations:
  - run the pre-registered trust test in Oct;
  - lead with the counter-intuitive, pre-registered finding;
  - keep the (L, P) map with failures.
- **One-line pitch:** "Planning over the lead time beats every rule we tested — and we show, pre-registered, when a better forecast makes it serve fewer people. Next: decision-aware forecast trust for fleets and autoscalers."

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

### 2026-10-04 08:05 IST — P=3 test of H1 (`eval/results/p3-v1`)
- Reproduce: `.venv/bin/python -m eval.harness --scenarios shock --policies greedy reactive mpc-ewma mpc-cusum-v1 oracle --seeds 100-104 --patience 3 --horizon 1440 --out eval/results/p3-v1 && .venv/bin/python -m eval.stats eval/results/p3-v1`
- Served fraction: greedy 0.802 · reactive 0.783 · mpc-ewma 0.889 · mpc-cusum-v1 0.889 · oracle 0.890.
- Look-ahead vs best rule: +8.7 pp [+7.0, +10.8], 5/5 seeds (n=5 caps Wilcoxon p at 0.062). The margin roughly doubles from P=10.
- **H1 not supported:** the detector, EWMA and oracle forecasts tie. With 1-step hops the queue plus the units about to free up already capture the shock.
- Next: a hop-time knob (L of 3–5 steps per hop). ADR 001 now has an update section. Innovation score lowered to 3.
- Contract tests: 6 passed. README added. Per-component innovation scan: `research/components/innovation-scan.md`.

### 2026-10-04 09:45–10:25 IST — Active batch: lead-time knob, phase-v1, hostile review, v2 protocol
- **Supervisor:** P7 is provisionally the Perceptron pick and in the active batch. Delegation now goes through sessions; cross-model reviews use gpt-6-astra and gpt-6-sol.
- **Lead-time knob L** (repositioning steps per hop; loaded trips unchanged). It runs through the simulator, the LP (hop edges arrive after L steps) and the rules (which count in-flight units over L).
- **phase-v1** (legacy planner, seeds 100–109, 720 steps; `python -m eval.phase --hops 1 2 4 8 --patience 3 10 --seeds 100-109 --horizon 720 --out eval/results/phase-v1`):
  - Detector − EWMA at P=3: L=1 −0.01 pp, L=2 +0.58 [+0.35, +0.80] (9/10), L=4 +1.36 [+1.20, +1.50] (10/10), L=8 +2.40 [+2.17, +2.64] (10/10).
  - Detector − EWMA at P=10: null for L ≤ 4; +0.65 (10/10) at L=8.
  - Perfect-forecast (true-rate MPC) − EWMA follows the same pattern, so the detector recovers ~51–71% of the forecast value in the cells where forecasts matter. **[RETRACTED 10:50 — did not replicate in the pre-registered phase-v2 with the abandonment-aware planner; see the 10:50 entry.]**
  - **H1 supported qualitatively under the legacy planner.**
- **Planner backend:** warm-started highspy, 5–9× faster than scipy-IPM, with identical objectives (contract test). Legacy reproduction verified: mvp-v1 seed 100 matches to 1e-16.
- **NYC TLC adapter** (sub-agent):
  - July 2025 yellow taxi data, Manhattan-internal trips (78.2% of trips kept), thinned at q ≈ 0.20.
  - The live TLC page returned 403, so links were confirmed via Wayback.
  - The largest observed surge is cell 3 on 4 July 22:00–22:30 at 20.7× the train-day mean; cause UNVERIFIED.
  - `research/components/real-trace-replay.md`.
- **Hostile-judge review** (rubber-duck): 48/100. Recorded in `reviews/` (14 accepted, 1 rejected). The biggest fixes are ablations, pre-registration, abandonment-aware LP, wording on "multi-agent" and "oracle", and the movement Pareto curve.
- **Pre-registration** committed (10:15) before the mvp-v2 run. The tuning-seed rule run is in `eval/results/tuning-rules`.

### 2026-10-04 10:25–10:55 IST — Confirmatory results, failed replication, real trace, long horizons
- **mvp-v2, pre-registered** (30 fresh seeds 200–229; `eval/results/mvp-v2/confirm.md`):
  - MPC beats the pre-registered reference rule in 6/6 scenarios, 30/30 seeds each, Holm p = 1.1e-8.
  - Shock +3.73 pp [+3.28, +4.20]; shock+drift +5.47 [+5.36, +5.59]; shock+drift+spikes +5.99 [+5.82, +6.15].
  - Ablations:
    - myopic horizon is worse everywhere;
    - queue-only (no forecast) is −2.68 pp under drift but **+1.19 pp and 62 fewer lost per shock** under a pure shock;
    - the detector adds +8.0 lost per shock at (1,10).
- **phase-v2, pre-registered H1 replication** (Addendum A; 20 fresh seeds; abandonment-aware LP; `eval/results/phase-v2/summary.md`):
  - **H1 not replicated**: the detector adds losses at (1,10), Holm p = 0.026, and at (8,10), Holm p = 0.011.
  - The true-rate forecast is worse at L ≥ 4 (−1.1 to −1.5 pp).
  - Planning beats the best rule in 7/8 cells (20/20 seeds each).
  - Diagnostic (seed 200, (4,3)): the legacy LP moves units 1.6–2× more, and sharper forecasts make the abandonment-aware LP passive.
  - "51–71% capture" is **retired**.
- **NYC real trace** (July 3–4 2025, 20 thinning replicates; `eval/results/nyc-v2`): MPC +2.52 pp [+2.39, +2.67] vs reactive (20/20). Observed July-4 21:30–23:30 surge (cause UNVERIFIED): 1.4 vs 39.6 lost. Here the forecast helps (queue-only −0.47 pp).
- **Long horizons:**
  - Week (`long-week-v2`, 10 seeds): +6.34 pp [+6.26, +6.43]; greedy decays 0.91 → 0.47.
  - Month (`long-month-v2`, 4 seeds): +6.37 pp [+6.29, +6.44].
- **Pareto** (`pareto-v2` + mvp-v2 shock rows): the planner at a move cost of 0.5 serves 0.937 at 0.41 empty hops per served request, dominating reactive (0.900, 0.59) and static.
- **Reviews:** gpt-6-sol (code + eval, 9 items, all accepted, 2 fixes deferred) and gpt-6-astra (spike + law, 8 items, 7 accepted). Supervisor framing (10:47) accepted: lead with the forecast-hurts-planner finding; spike = decision-aware forecast trust.
- **Citations verified:** Elmachtoub & Grigas (Management Science 2022) and Wilder et al. (AAAI 2019) via arXiv API plus Crossref; Page (1954) bibliographic record via Crossref.
- **Fixes:** rates now reach only the oracle; `pending_frac`; seed-bootstrap CIs for long runs; integer `@k=v` parsing; `--legacy` in phase; Holm per endpoint in `confirm.py`.

### 2026-10-04 10:50–11:05 IST — Follow-ups, final abstract, review sessions
- **Matched-α** (`eval/results/phase-v2-merged/summary.md`):
  - Detector − EWMA(α=0.01) is positive in 7/8 cells (+0.18 to +0.64 pp). The restart beats equally slow smoothing but not the faster default EWMA(α=0.05).
  - Fixed H=14 for both arms gives the same negatives as phase-v2, so the horizon confound does not explain the miss.
- **Trust sweep** (exploratory, L=1, P=10, 30 seeds; `eval/results/trust-v2/summary.md`):
  - An intermediate trust beats both extremes in 4/4 scenarios: shock+drift +1.13 pp [+1.05, +1.21] (trust 0.5); shock+drift+spikes +1.24 (0.5); shock +0.20 (0.25); drift +0.16 (0.75).
  - The best trust varies by regime, which supports spike A″ (decision-aware, regime-gated trust). It must still pass the pre-registered test (Addendum B, to be written before the run).
- **Summaries written** so every abstract number has a committed file: `eval/summarise_misc.py` → nyc-v2, pareto-v2, trust-v2 `summary.md`.
- **Final abstract** (`deliverables/round1-abstract.md`): 899 words, all 8 required sections, `[TEAM-n]` placeholders.
  - Every number was audited against committed files.
  - One over-general claim was fixed: the true-rate forecast hurts "in three of four long-lead-time cells", not everywhere.
- **Architecture diagram final:** trust-gate spike.
- **Cross-model review sessions launched** (Supervisor directive: sessions, cap 2): gpt-6-astra hostile-judge review of the final abstract; gpt-6-sol independent reproduction of the headline numbers.

### 2026-10-04 11:00–11:08 IST — Planner sensitivity, Addendum B
- **phase-v2c** (legacy never-abandoning backlog, same fresh seeds 200–219; `eval/results/phase-v2c/summary.md`):
  - The phase-v1 pattern **replicates under the legacy LP**. Detector − EWMA: +0.45 / +1.28 / +2.63 / +0.70 pp at (2,3) / (4,3) / (8,3) / (8,10), 18–20/20 seeds. True-rate − EWMA: +0.99 to +3.63 pp.
  - Under the abandonment-aware LP the same comparisons are negative.
  - Neither base planner dominates with EWMA.
  - Conclusion: forecast value belongs to the forecast–planner pair. This supports the decision-aware trust spike.
- **Addendum B** (`eval/preregistration.md`): the frozen falsification test for the trust spike.
  - Seeds 300–329; 28 cells = scenarios + (L,P) grid × both planners; Holm.
  - Success = Holm-significant gain over the better extreme in ≥ 21/28 cells, and no significant loss > 0.5 pp.
- README updated with the v2 reproduction commands.
- Waiting on the two review sessions.

### 2026-10-04 11:08–11:18 IST — Reproduction review, gated-trust preview
- **gpt-6-sol headline reproduction** (child session): every headline number reproduced exactly (7/7 analyses; 8 episode replays, 31/31 metrics, highspy 1.15.1). Three wording items accepted: tested scalar trust vs planned per-zone trust; "not an upper bound" docstring; "~6 ms end-to-end". Recorded in `reviews/` and the ledger.
- **`mpc-gated` implemented**, with a tuning-seed preview (`eval/results/gated-tuning-preview`): regime gating adds ≈0 over the best fixed trust (+0.01 pp in shock+drift). The gain is global shrinkage. ADR note: amend Addendum B (city-wide regime and uncertainty-calibrated shrinkage) before any test run.
- Waiting on the gpt-6-astra final-abstract review session.

### 2026-10-04 11:15–11:30 IST — Final reviews applied, DONE
- **gpt-6-astra final-abstract review** (child session, `reviews/2026-10-04-abstract-final-gpt-6-astra.md`): 71/100, 8 issues, all ACCEPTED.
  - One numeric mismatch fixed: the trust-sweep comparator pair is now +1.13 pp vs full trust and +1.50 vs queue-only.
  - The spike is marked "planned"; MVP (ii) credits EWMA-MPC; novelty is positioned against Iglesias 2018 and decision-focused learning.
  - Mechanism wording is qualified; evidence scope is split by suite; the diagram is fixed (H=6 at L=1, not an upper bound, hindsight smoother).
- **Amendment B1** (before any test run): best fixed trust and a detector-free uncertainty gate are co-primary comparators.
- **Second NYC period** (July 10–11): +1.52 pp [+1.43, +1.59], 20/20 (`eval/results/nyc-v2b`).
- **Abstract v1.2:** 881 words. Q&A prep updated.
- DoD items 1–6 complete; DONE message sent to the Supervisor.

### 2026-10-04 17:30 IST — Demo phase start; git and timestamp hygiene
- **Supervisor directive (17:28):** winning demo per PLAYBOOK §11. Spawned one child session, *P7 demo builder* (plan mode, notify once), with a full kickoff: committed evidence, code APIs, honesty corrections, the §11 bar, rules.
- **New PLAYBOOK §6 rules acknowledged:** never `git stash`/`--autostash` (I had used `--autostash` in my push loop until now; from now on I commit before rebasing). Timestamps come from the clock.
- **Pre-registration times:** all four stated times were 2–11 minutes later than their commits. I appended a dated correction to `eval/preregistration.md` without editing the registered text. The order is verified for every registration: main prereg committed 10:10:38, mvp-v2 started 10:11:01; Addendum A 10:25:33, phase-v2 started 10:32:25; B (10:59:23) and B1 (11:14:31) have no test runs yet (max seed used = 229).
- **Memory guard** (as I interpret it): start heavy jobs only when `memory_pressure` reports free ≥ 30%. It was 32% at 17:28.
