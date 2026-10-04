# Round-1 abstract — Perceptron 2026, Problem 7 (FINAL v1.2, 4 Oct 2026; reviewed by gpt-6-astra and gpt-6-sol)

**Title:** *When does look-ahead pay? Decision-aware reallocation of a shared fleet under demand shocks and drift*

**Problem & theme.** Theme 4, Problem 7: splitting a shared resource when demand keeps changing. Ride-hailing fleets, delivery riders and GPU clusters share a structure. Moving supply takes lead time L (driving, loading a model). Waiting demand leaves after patience P (customer patience, request timeout). Demand shifts without warning. [TEAM] works on large-scale systems, where autoscalers reacting one cold-start too late are a daily cost.

**Understanding of the challenge.** Reactive demand estimates update only after arrivals; supply delays then compete with patience. Look-ahead uses known returning units, demand forecasts, or both, and forecast quality and use interact: an abrupt shock is exactly when a forecast is stale. Fast change detection trades against false alarms on transient spikes, and agents must not herd onto one hotspot.

**Proposed approach.**
- *Environment (built):* a PettingZoo `ParallelEnv` where 40 agents (resource units) serve a 25-zone grid.
  - Poisson demand has a daily cycle, abrupt shocks, gradual hotspot drift, transient spikes, over-dispersion and ground-truth change labels.
  - Same-zone FIFO matching; deterministic patience P; empty repositioning takes L per hop.
  - A replay mode uses NYC TLC yellow-taxi trips (July 2025, Manhattan, thinned).
- *Allocator (built):* a rolling-horizon model-predictive planner. It is a linear program on a time-expanded zone graph: moves arrive after L steps, trips return units via origin–destination flows, backlog abandons at rate 1/P. Warm-started HiGHS loop: ~6 ms per step end to end (median episode average, laptop).
  - Inputs: an EWMA forecaster (time-of-day profile × per-zone level) and a per-zone Poisson CUSUM detector.
  - A coordinator turns zone flows into per-agent orders (centralised planning, per-agent execution).
- *Spike (planned) — decision-aware forecast trust:* grid-tune a per-zone trust gate from forecast residuals and CUSUM alarms, multiplying the forecast before planning; tune served fraction, not forecast error (Elmachtoub & Grigas 2022; Wilder et al. 2019); test against the best fixed trust on untouched seeds.

**Minimum Viable mapping.**
- *(i)* Three rule-based allocators: static historical shares, a decentralised greedy neighbour rule, and reactive proportional rebalancing.
- *(ii)* EWMA-MPC (no detector or adaptive trust) beats the reference rule in a pre-registered test (reference fixed on tuning seeds; 30 fresh test seeds):
  - +3.7 percentage points served under an abrupt shock (95% CI [+3.3, +4.2]);
  - +5.5 under shock-plus-drift;
  - 30/30 seeds, Holm-adjusted p ≈ 10⁻⁸.

**Stretch ambitions.**
- Both stretch goals already run:
  - Shock + drift + spikes in one run: +6.0 pp.
  - A simulated week with a shock every day plus drift (10 seeds): +6.3 pp over the best rule (CI [+6.3, +6.4]), 132 fewer requests lost per shock. Daily means: greedy falls from 91% to 47% by day 7; the planner stays above 90%.
  - A 30-day month (4 seeds): +6.4 pp.
- Real-trace replay: +1.5 to +2.5 pp on two NYC periods (20 thinnings each); 38 fewer requests lost in an observed July-4 night surge.
- Next: an RL comparator (MAPPO/IPPO), decentralised dual-price coordination, and a compute-cluster instance (L = cold start).

**Novelty / differentiation.** Forecast-driven fleet MPC is established (Iglesias et al. 2018); decision-focused tuning is also prior art. Our contribution is an empirical lead-time/patience ablation map, including failures, and a testable regime-gated-trust extension.
- Planning over the lead time beats the best rule in 7 of 8 (L, P) cells (+2.3 to +9.8 pp, 20/20 seeds each).
- The demand forecast is essential under drift and short patience. In our approximate LP, true-rate forecasts lowered service in three of four long-lead-time cells (−1.1 to −1.5 pp); the mechanism remains untested.
- Under a pure shock, ignoring the forecast entirely lost 62 fewer requests per shock.
- Our pre-registered change-detector hypothesis did not replicate with this planner, yet holds with a queue-chasing variant (same seeds): forecast value belongs to the forecast–planner pair.

That defines the spike: set forecast trust by its effect on service. Exploratory half-trust improves shock-plus-drift by +1.13 pp versus full trust and +1.50 versus queue-only; across tested weights, shocks favour 0.25 and drift 0.75.

**Evaluation plan.**
- *Metrics:*
  - served fraction (primary);
  - requests lost per shock (120-step window);
  - empty hops per served request (under shocks, the planner out-serves the reactive rule while moving less);
  - per component: detection delay, false alarms per zone-day, post-shock forecast error.
- *Baselines:*
  - the three rules;
  - same-planner ablations (myopic, queue-only, no detector);
  - a true-rate-forecast planner (not an upper bound).
- *Protocol* (Agarwal et al. 2021):
  - MVP: 30 fresh seeds, tuning-fixed references, paired bootstrap CIs, Wilcoxon/Holm.
  - Detector replication: pre-registered; other grid contrasts exploratory (20 seeds).
  - NYC: 20 thinnings of each two-day period; week/month: 10/4 seeds, descriptive.
- *Pre-registered next test (Addendum B):* fresh seeds 300–329; Holm-corrected contrasts against full/zero trust, best fixed trust and detector-free gating; every cell reported.

**Feasibility and risks.**
- *Team:* [TEAM-1] optimisation and simulation; [TEAM-2] RL comparator and coordination; [TEAM-3] statistics and the demo.
- *Built:* simulator, baselines, planner, harness, results.
- *Milestones:*
  - Oct: trust spike and mechanism tests.
  - Early Nov: RL comparator.
  - By 17 Nov: click-to-shock dashboard (exams 19–25 Nov).
  - 1 Dec: frozen results.
  - Dec: rehearsal.
- *Risks:*
  - The LP approximates first-step matching; tie-breaks are solver-specific (backend recorded).
  - Real replay retains synthetic travel, matching and patience.
  - Planning is centralised; a decentralised variant is planned.
  - RL may beat our planner; we would report it.
