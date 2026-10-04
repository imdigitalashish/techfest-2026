# Round-1 abstract — Perceptron 2026, Problem 7 (FINAL v1.0, 4 Oct 2026)

**Title:** *When does look-ahead pay? Decision-aware reallocation of a shared fleet under demand shocks and drift*

**Problem & theme.** Theme 4, Problem 7: splitting a shared resource when demand keeps changing. Ride-hailing fleets, delivery riders and GPU clusters share a structure. Moving supply takes lead time L (driving, loading a model). Waiting demand leaves after patience P (customer patience, request timeout). Demand shifts without warning. [TEAM] works on large-scale systems, where autoscalers reacting one cold-start too late are a daily cost.

**Understanding of the challenge.** A reactive allocator learns of a shift only once queues form: structurally late whenever L is comparable to P. Look-ahead needs a demand model, whose quality and use interact. An abrupt shock is exactly when the model is stale, and a planner treating forecasts as certain holds supply back for demand that may never arrive. Fast change detection trades against false alarms on transient spikes, and agents must not herd onto one hotspot.

**Proposed approach.**
- *Environment (built):* a PettingZoo `ParallelEnv` where 40 agents (resource units) serve a 25-zone grid.
  - Poisson demand has a daily cycle, abrupt shocks, gradual hotspot drift, transient spikes, over-dispersion and ground-truth change labels.
  - Queues are FIFO with abandonment; repositioning takes lead time L per hop.
  - A replay mode uses NYC TLC yellow-taxi trips (July 2025, Manhattan, thinned).
- *Allocator:* a rolling-horizon model-predictive planner. It is a linear program on a time-expanded zone graph: moves arrive after L steps, trips return units via origin–destination flows, backlog abandons at rate 1/P. With warm-started HiGHS a decision step takes ~6 ms end to end (median, laptop).
  - Inputs: a forecaster (time-of-day profile × per-zone level) and a per-zone Poisson CUSUM detector.
  - A coordinator turns zone flows into per-agent orders (centralised planning, per-agent execution).
- *Spike — decision-aware forecast trust:* the planner sees trust × forecast, with trust set from calibrated forecast uncertainty and the regime state, tuned for served fraction rather than forecast error (cf. Elmachtoub & Grigas 2022; Wilder et al. 2019).

**Minimum Viable mapping.**
- *(i)* Three rule-based allocators: static historical shares, a decentralised greedy neighbour rule, and reactive proportional rebalancing.
- *(ii)* A planning agent that beats them under sudden shifts, shown in a pre-registered test (reference rule fixed on tuning seeds; 30 fresh test seeds):
  - +3.7 percentage points served under an abrupt shock (95% CI [+3.3, +4.2]);
  - +5.5 under shock-plus-drift;
  - 30/30 seeds, Holm-adjusted p ≈ 10⁻⁸.

**Stretch ambitions.**
- Both stretch goals already run:
  - Shock + drift + spikes in one run: +6.0 pp.
  - A simulated week with a shock every day plus drift: +6.3 pp over the best rule (CI [+6.3, +6.4]), with 132 fewer requests lost per shock. The greedy rule decays from 91% to 47% served by day 7; the planner stays above 90%.
  - A 30-day month (4 seeds): +6.4 pp.
- Real-trace replay: +2.5 pp on NYC trips; 38 fewer requests lost in an observed July-4 night surge.
- Next: an RL comparator (MAPPO/IPPO), decentralised dual-price coordination, and a compute-cluster instance (L = cold start).

**Novelty / differentiation.** Production systems guard against shocks with fixed heuristics: Knative's panic mode at 200% of capacity; AWS/Azure predictive scaling that only scales out. We contribute a measured map of which look-ahead layer helps where, from same-solver ablations across lead time and patience, failures included.
- Planning over the lead time beats the best rule in 7 of 8 (L, P) cells (+2.3 to +9.8 pp, 20/20 seeds each).
- The demand forecast is essential under drift and short patience. Yet a better forecast — even the true rates — made the certainty-equivalent planner serve fewer people in three of four long-lead-time cells (−1.1 to −1.5 pp).
- Under a pure shock, ignoring the forecast entirely lost 62 fewer requests per shock.
- Our pre-registered change-detector hypothesis did not replicate with this planner, yet holds with a queue-chasing variant (same seeds): forecast value belongs to the forecast–planner pair.

That defines the spike: set forecast trust by its effect on service. An exploratory global-trust sweep agrees: half-trust beats both full trust and queue-only by +1.1–1.2 pp under shock-plus-drift; the best trust varies by regime (0.25 shocks, 0.75 drift).

**Evaluation plan.**
- *Metrics:*
  - served fraction (primary);
  - requests lost per shock;
  - empty moves per request (the planner out-serves the reactive rule while moving less);
  - per component: detection delay, false alarms per zone-day, post-shock forecast error.
- *Baselines:*
  - the three rules;
  - same-planner ablations (myopic, queue-only, no detector);
  - a true-rate-forecast planner.
- *Protocol* (following Agarwal et al. 2021):
  - pre-registration, with reference rules fixed on tuning seeds;
  - 30 fresh test seeds; paired bootstrap CIs; Wilcoxon tests with Holm correction;
  - the (L, P) grid, NYC replay, week and month horizons.
- *Pre-registered spike test:* tuned trust must beat both full trust (1) and queue-only (0) across the grid on fresh seeds.

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
  - Demand is mostly synthetic (real replay mitigates).
  - Planning is centralised; a decentralised variant is planned.
  - RL may beat our planner; we would report it.
