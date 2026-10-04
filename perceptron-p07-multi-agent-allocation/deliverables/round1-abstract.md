# Round-1 abstract — Perceptron 2026, Problem 7 (DRAFT v0.1, 4 Oct 2026)

**Title:** *Shock-aware look-ahead: a multi-agent allocator that detects demand regime changes and re-plans before supply runs out*

**Problem & theme.** Theme 4 (Agents that compete, cooperate and adapt), Problem 7: splitting a shared resource when demand keeps changing. The same structure appears in ride-hailing fleets, delivery riders and GPU clusters serving models. Units of supply take time to move, while demand moves without warning. Our lead works on large-scale systems and has seen the cost of autoscalers that react a cold-start too late. This problem lets us build and measure the fix rigorously.

**Understanding of the challenge.** Reallocation has a *lead time* L: a vehicle must drive, a GPU must load a model. Waiting demand has a *patience* P before it abandons. A reactive allocator learns about a shift only once queues form, so whenever L is comparable to or larger than P, it is structurally late. Look-ahead fixes that only if its demand model is right, and a sudden shift is exactly the moment the model breaks. The crux is a coupled trade-off:
1. **Detect, but don't chase noise.** Detect a regime change fast (low detection delay) without reacting to Poisson noise or one-off spikes (low false-alarm rate).
2. **Plan over the lead time.** Pre-position supply over a horizon at least as long as L, counting units that will free up and the trips that relocate them.
3. **Coordinate the agents.** Coordinate many agents so they don't all chase the same hotspot (herding), while weighing empty travel against service.

A slow abrupt shock and a gradual drift stress opposite sides of this trade-off, which is why handling both in one run is hard.

**Proposed approach.** A PettingZoo `ParallelEnv` multi-agent dispatch simulator (built; Python/numpy):
- a zone grid where each resource unit is an agent;
- Poisson demand per zone with a diurnal cycle, abrupt shocks, gradual hotspot drift, transient spikes and over-dispersion;
- FIFO queues with abandonment, travel at one step per hop, and trips that relocate units.

Every scenario carries ground-truth change labels, and all policies see identical request streams (common random numbers). The allocator is a pipeline of components with typed contracts:
1. **Change detector:** a two-sided Poisson CUSUM per zone, deseasonalised. It estimates the onset and the post-change rate; Bayesian online change-point detection (BOCPD) is the upgrade.
2. **Forecaster:** a learned time-of-day profile × a per-zone level. A slow EWMA tracks drift; a detector alarm *restarts* the level at the post-change estimate. Calibrated upper bounds from conformal PID control are planned as safety stock.
3. **Model-predictive planner:** a rolling-horizon linear program on a time-expanded zone graph — hop flows, service flows that return units along the origin–destination matrix, and backlog — solved by HiGHS in about 18 ms per step.
4. **Coordinator:** turns zone flows into per-unit orders. LP dual prices give a decentralised, market-style variant.

**Minimum Viable mapping.**
- *(i) Rule-based baseline allocator:* three are implemented — static historical-share rebalancing, a decentralised greedy neighbour rule, and reactive proportional rebalancing to the last 30 minutes of demand.
- *(ii) A planning agent that outperforms it when demand suddenly shifts:* the MPC look-ahead agent, with a clairvoyant-oracle MPC as the reference. Preliminary held-out results: **[filled from `eval/results/mvp-v1/summary.md`]**. The demo shows a judge injecting a shock live.

**Stretch ambitions.**
1. Shock plus drift (plus spikes) in **one** run. This scenario already exists.
2. Week-to-month horizons with repeated regime changes, using batch-means confidence intervals.
3. An RL comparator: MAPPO/IPPO via TorchRL on the same PettingZoo API, trained with shock/drift randomisation. This answers "RL or planning?" with evidence.
4. A compute-cluster instantiation: replicas across services, with lead time = cold start.

**Novelty / differentiation.** The obvious design is "forecast + MPC" or "train RL". Production systems guard against shocks with fixed-threshold heuristics: Knative's panic mode at 200% of capacity, and AWS/Azure predictive scaling that only scales out. In our literature scan we found no allocator that couples a statistical change detector (with a tunable, *measured* false-alarm rate) to the forecast inside a rolling-horizon planner. Our framing contribution is a falsifiable "when does look-ahead pay?" law. Lost demand ≈ Δλ·max(0, d + L − P), where Δλ is the extra demand rate, d the detection delay, L the lead time and P the patience. We map it empirically across the lead-time/patience plane rather than claiming one blanket win.

**Evaluation plan.**
- **Primary metric:** served fraction.
- **Shock-window metrics:** demand lost in the 2 hours after onset (the resilience-triangle area) and time-to-recover to 90% served.
- **Secondary metrics:** mean and p95 wait, empty moves per served request, planner latency.
- **Per-component metrics:** detection delay at a fixed false-alarm rate (TCPD-style F1 with margin); post-shock forecast error; planner quality under the oracle forecast.
- **Baselines:** the three rules, EWMA-MPC (look-ahead without a detector, the ablation), RL, and the oracle (regret reference).
- **Statistics** (following Agarwal et al., NeurIPS 2021): ≥20 frozen test seeds kept separate from tuning seeds; paired bootstrap 95% CIs; IQM; Wilcoxon signed-rank tests with Holm correction; win-rate per seed.
- **Scenarios:** stationary, shock, drift, shock+drift, spikes (false-alarm bait), plus a lead-time/patience sweep.

**Feasibility and risks.**
- **Team:** systems/optimisation (Ashish, IIT Delhi), RL [teammate 2, TBD] and statistics/visualisation [teammate 3, TBD].
- **Done already:** the simulator, the baselines, the MPC and the harness.
- **Milestones:**
  - Oct: BOCPD and conformal buffers; the lead-time sweep.
  - early Nov: RL comparator.
  - before 17 Nov: demo dashboard (exams 19–25 Nov).
  - 1 Dec: frozen-seed results.
  - Dec: real-trace replay and rehearsal.
- **Risks:**
  - The detector may add little when L ≤ P. Our pilot suggests exactly this, so we test where it matters instead of assuming.
  - RL may beat MPC; we would report it.
  - Synthetic demand; mitigated by replaying public trip traces.
  - LP latency at city scale; mitigated by warm starts, coarser far-horizon steps, or min-cost flow.
