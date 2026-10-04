# Per-component innovation scan (morning version, 2026-10-04)

> Lean-mode note: the planned per-component research agents were not run, because sub-agents were disabled at 05:50 IST. This scan uses the lead's analysis, the cited sources in [landscape.md](../landscape.md), and our own measured results. Claims about the literature cite only sources listed there. Ideas without a source are our own and are marked *(ours)*. Scores (1–5): impact · novelty · feasibility · measurability · demo.

## C1 Simulator + C2 Scenarios
- **Now.** A numpy core plus a PettingZoo 1.27 wrapper. Same-zone FIFO matching, patience, Manhattan travel. Labelled shocks, drift and spikes; gamma-Poisson over-dispersion; common random numbers. 6/6 contract tests pass.
- **Room to innovate:**
  1. **Lead-time and patience as first-class knobs** — travel time per hop, cold-start delay, patience distribution — so the "when does look-ahead pay" surface can be mapped *(ours)*: 5·3·5·5·4.
  2. **Real-trace replay** (NYC TLC zones aggregated to a grid; open the official TLC page before use — UNVERIFIED tonight): 4·2·4·5·4.
  3. **Compute-cluster skin:** OD = identity, trip = service time, travel = cold start *(ours)*: 4·3·4·5·3.
  4. **Judge-injected shocks in the demo** *(ours)*: 3·2·5·3·5.
- **Isolated metric:** steps/s; rate fidelity; conservation (tested).

## C3 Nowcaster
- Observed arrivals are uncensored here. In compute settings timeouts censor demand, so a censored-demand estimator is the open question *(ours)*: 3·3·4·4·2.

## C4 Change detector (SPIKE)
- **Now.** A two-sided Poisson CUSUM per zone, deseasonalised. On dev seeds it detects the shock in about 5.6 steps at 0.23 false alarms per zone-day (ratchet v1, `results.tsv`).
- **Room to innovate:**
  1. **Spatial pooling:** CUSUM on 2×2 blocks plus single zones, so a block shock is detected about √4–4× faster *(ours; to measure)*: 4·3·5·5·4.
  2. **BOCPD** run-length posterior (Adams & MacKay 2007) and **robust BOCPD** (Altamirano et al., ICML 2023) for spike robustness: 4·3·4·5·4.
  3. **Multi-scale δ** (two detectors) to catch shocks smaller than 2× in busy zones *(ours)*: 3·2·5·5·3.
  4. **Thresholds set by measured average run length (ARL₀)** instead of fixed constants — the contrast with Knative's fixed 200% panic threshold (landscape §6): 4·3·5·5·4.
- **Isolated metric:** detection delay at a fixed false-alarm rate; TCPD-style F1 with margin (formula to be opened).

## C5 Forecaster (SPIKE)
- **Now.** A learned time-of-day profile × per-zone level. Ratchet v1 (running post-change mean after an alarm) scores **0.4154 vs 0.4385 for the EWMA reference** on the frozen metric.
- **Room to innovate:**
  1. **Conformal-PID upper band** (Angelopoulos et al., NeurIPS 2023; tested on count data) used as safety stock in the planner. The detector state would reset the conformal integrator *(the coupling is ours)*: 5·4·4·5·4.
  2. **Run-length mixture forecast** from BOCPD: 4·3·4·5·3.
  3. **Holt trend** for drift: 2·1·5·5·2.
  4. **Conformal Decision Theory** (Lekeufack et al., ICRA 2024) to calibrate the *decision* (risk of lost demand) rather than the interval: 4·4·3·4·3.
- **Isolated metric:** frozen `autoresearch/eval.py` score (MAE_all + MAE_post_shock); later, coverage and width of the upper band.

## C6 MPC planner
- **Now.** A time-expanded LP over H=6 steps. HiGHS-IPM takes 17.7 ms (benchmark). On held-out seeds it equals the oracle-forecast MPC, so planning carries the gain at P=10.
- **Room to innovate:**
  1. **Scenario/robust MPC** with conformal bands (pairs with C5.1): 4·3·4·5·3.
  2. **Learned terminal value** (bi-level RL + LP, as in Gammelli et al. 2023/2024): 4·3·3·4·3.
  3. **Speed:** warm starts or min-cost-flow for city scale: 3·1·4·5·2.
  4. **Coarser far-horizon time buckets** to lengthen look-ahead cheaply *(ours)*: 3·2·5·5·2.
- **Isolated metric:** served fraction under the oracle forecast; p99 solve time.

## C7 Coordinator (second spike candidate)
- **Now.** Zone flows → lowest-index idle units. Units are interchangeable, so this is optimal.
- **Room to innovate:**
  1. **Decentralised price-based execution:** units act on the LP's dual zone values (`Plan.zone_value`), with an auction to resolve conflicts. A market-style protocol with O(K) messages and no central dispatch *(ours as applied here; auction algorithms are classic — cite Bertsekas once opened)*: 4·4·4·4·4.
  2. **Heterogeneous units** (battery, capacity) make assignment non-trivial (Hungarian): 3·2·4·4·3.
- **Isolated metric:** assignment cost / optimal; messages per step; served-fraction gap vs centralised.

## C8 RL comparator
- MAPPO/IPPO via TorchRL (active repo; landscape §5) on the PettingZoo API, trained with shock/drift domain randomisation. Purpose: answer "RL or planning?" empirically. Production evidence (Lyft, DiDi) uses RL as a *value* input to matching or optimisation, not as end-to-end allocation (landscape §6): 4·2·3·5·3.

## C9 Rule-based baselines
- **Measured.** Greedy is the best rule under a pure shock (0.910). Reactive is best under shock+drift (0.882), where greedy collapses to 0.739. Report all three. The best rule per scenario is the reference for every paired test.

## C10 Eval harness
- **Now.** Common random numbers; frozen test seeds (100+); paired bootstrap CIs; IQM; Wilcoxon + Holm; shock-window loss area; time-to-recover.
- **Room to innovate:**
  1. The **(L, P) phase diagram** as a headline figure *(ours)*: 5·4·5·5·5.
  2. **Batch-means CIs** for single long runs (week to month): 3·2·5·5·2.
  3. **Performance profiles** (Agarwal et al. 2021): 3·1·5·5·3.
- **Gap noted:** n=10 gives Holm-adjusted p ≥ 0.068 across 28 tests. Move to ≥20 test seeds.

## Pick (see ADR 001)
- **Spike A** = C4 + C5, tested along the lead-time/patience axis (C1.1 + C10.1).
- **Spike B (candidate)** = C7.1 price-based decentralised coordination.
- Everything else stays best practice.
