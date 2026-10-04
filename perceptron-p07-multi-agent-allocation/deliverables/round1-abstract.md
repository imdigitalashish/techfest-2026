# Round-1 abstract — Perceptron 2026, Problem 7 (DRAFT v0.2, 4 Oct 2026)

**Title:** *Shock-aware look-ahead: a multi-agent allocator that detects demand regime changes and re-plans before supply runs out*

**Problem & theme.** Theme 4, Problem 7: splitting a shared resource when demand keeps changing. Ride-hailing fleets, delivery riders and GPU clusters serving models share one structure: units of supply take time to move, while demand moves without warning. Our lead works on large-scale systems and has seen autoscalers react one cold-start too late. We want to build and *measure* the fix.

**Understanding of the challenge.** Reallocation has a lead time L (driving, loading a model); waiting demand has a patience P before it abandons. A reactive allocator learns of a shift only once queues form, so when L is comparable to or larger than P, it is structurally late. Look-ahead helps only if its demand model is right, and a sudden shift is exactly when the model breaks. The crux is coupled:
1. **Detect, but don't chase noise.** Catch regime changes quickly (low detection delay) without reacting to Poisson noise or one-off spikes (low false-alarm rate).
2. **Plan over the lead time.** Pre-position supply over a horizon of at least L, counting units about to free up and the trips that relocate them.
3. **Coordinate the agents.** Keep agents from herding onto one hotspot, and weigh empty travel against service.

Abrupt shocks and gradual drift stress opposite sides of this trade-off.

**Proposed approach.** A PettingZoo `ParallelEnv` dispatch simulator (built, numpy):
- 25 zones, with each resource unit as an agent;
- Poisson demand with a diurnal cycle, shocks, hotspot drift, transient spikes and over-dispersion;
- FIFO queues with abandonment, and travel at one step per hop;
- ground-truth change labels, and identical request streams for every policy (common random numbers).

The allocator is a pipeline of components with typed contracts:
1. **Change detector:** a two-sided Poisson CUSUM per zone, deseasonalised, which estimates the onset and the post-change rate; Bayesian online change-point detection (BOCPD) is next.
2. **Forecaster:** a learned time-of-day profile × a per-zone level. A slow EWMA tracks drift; an alarm restarts the level at the running post-change mean. Conformal-PID upper bands are planned as safety stock.
3. **Model-predictive planner:** a rolling-horizon LP on a time-expanded zone graph — hop flows, service flows returning units along the origin–destination matrix, and backlog. HiGHS solves it in about 18 ms per step.
4. **Coordinator:** turns zone flows into per-unit orders; LP dual prices give a decentralised, market-style variant.

**Minimum Viable mapping.**
- *(i) Rule-based allocators (built):* static historical shares, a decentralised greedy neighbour rule, and reactive proportional rebalancing.
- *(ii) A planning agent that beats them under sudden shifts (built):* the MPC look-ahead agent. On 10 held-out seeds (1 simulated day, 40 units, P=10) with an abrupt shock, it served 95.0% of requests vs 91.0% for the best rule. That is +3.9 pp, paired 95% CI [+3.3, +4.6], better on 10/10 seeds, Wilcoxon p=0.002. It lost 82 fewer requests in the two hours after the shock.
- With shock **and** drift in one run, the margin is +5.4 pp [+5.2, +5.7] over the best rule.
- A clairvoyant-forecast MPC scores the same (94.8%). At this patience, *planning*, not prediction, carries the gain. This is why our spike targets the regime where prediction matters.

**Stretch ambitions.**
1. Shock + drift + spikes in one run — implemented.
2. Week-to-month horizons with repeated regime changes, using batch-means confidence intervals.
3. An RL comparator (MAPPO/IPPO via TorchRL, trained with shock/drift randomisation), to answer "RL or planning?" with evidence.
4. A compute-cluster instantiation, where L = cold start.

**Novelty / differentiation.** Production systems guard against shocks with fixed-threshold heuristics: Knative's panic mode at 200% of capacity; AWS/Azure predictive scaling that only scales out. In our scan we found no allocator that couples a statistical change detector (with a tunable, *measured* false-alarm rate) to the forecast inside a rolling-horizon planner. We contribute a falsifiable law for when look-ahead pays: lost demand ≈ Δλ·max(0, d + L − P), where Δλ is the extra demand rate, d the detection delay, L the lead time and P the patience. We map it across the (L, P) plane instead of claiming one blanket win.

**Evaluation plan.**
- **Primary metric:** served fraction.
- **Shock-window metrics:** demand lost in the two hours after onset, and time to recover to 90% served.
- **Secondary metrics:** p95 wait, empty moves, planner latency.
- **Per-component metrics:** detection delay at a fixed false-alarm rate; post-shock forecast error.
- **Baselines:** the three rules, EWMA-MPC (the no-detector ablation), RL, and the oracle (regret reference).
- **Statistics** (Agarwal et al., NeurIPS 2021): ≥20 frozen test seeds kept separate from tuning seeds; paired bootstrap CIs, IQM, Wilcoxon tests with Holm correction.
- **Scenarios:** stationary, shock, drift, shock+drift, spikes, plus the (L, P) sweep.

**Feasibility and risks.**
- **Team:** systems/optimisation (Ashish, IIT Delhi), RL [teammate 2, TBD], statistics and visualisation [teammate 3, TBD].
- **Built already:** the simulator, baselines, MPC, harness, and a first auto-tuning loop on the detector.
- **Milestones:**
  - Oct: BOCPD, conformal buffers, the (L, P) sweep.
  - early Nov: RL comparator.
  - by 17 Nov: demo dashboard (exams 19–25 Nov).
  - 1 Dec: frozen-seed results.
  - Dec: real-trace replay (NYC TLC) and rehearsal.
- **Risks:**
  - The detector may add little when L ≤ P (our pilot shows exactly this), so we test where it matters.
  - RL may beat MPC; we would report it.
  - Synthetic demand.
  - LP latency at city scale; mitigated by warm starts or min-cost flow.
