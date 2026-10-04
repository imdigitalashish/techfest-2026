# ADR 001 — Spike choice: regime-aware look-ahead (detector → forecaster → MPC), tested along the lead-time / patience axis

- **Status:** accepted (morning-package version, 2026-10-04 07:00 IST). Revisit by 12 Oct with sweep results.
- **Deciders:** P7 project lead.
- **Process note:** PLAYBOOK §3 asks for an *independent* adversarial agent. Lean mode (no sub-agents after 05:50 IST, network saturated) made that impossible tonight. The antithesis below is the lead's own self-critique. An independent `rubber-duck` pass is queued for when sub-agents are allowed again.

## Context
- The MVP requires a rule-based allocator plus one RL or planning agent that beats it when demand suddenly shifts. The stretch goals are shock + drift in one run, and long horizons.
- "MPC on a demand forecast" for fleet rebalancing is established (Iglesias et al., ICRA 2018: wait time cut "by up to 89.6%"). Bi-level RL + LP is the research frontier (Gammelli et al. 2021–2025).
- Production systems use forecast + optimiser + **reactive guardrails** with fixed thresholds (Knative panic at 200% of capacity; AWS and Azure predictive scaling is scale-out only). See [landscape](../../research/landscape.md).
- **Evidence from our own runs** — smoke test, `eval/harness.py`, seed 0, shock scenario, 1 day, K=40 units; reproduce with the snippet in the thought-node Log, 06:20 entry:

  | policy | served_frac | served in 120-step shock window |
  |---|---|---|
  | static | 0.879 | 0.741 |
  | greedy | 0.933 | 0.857 |
  | reactive | 0.927 | 0.814 |
  | mpc-ewma | 0.977 | 0.886 |
  | mpc-cusum | 0.977 | 0.889 |
  | oracle | 0.976 | 0.884 |

  Look-ahead planning gives the large gain. **Forecast quality — even clairvoyance — adds almost nothing in this regime.** Single seed, so indicative only; the 10-seed held-out grid is in `eval/results/mvp-v1/`.

## Options scored (1–5: impact on judged criteria · novelty vs SOTA · feasibility by 15 Dec · measurability · demoability)

| Option | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| A. Regime-aware look-ahead: change detector (CUSUM → BOCPD) restarts the forecaster; conformal-calibrated buffers; MPC re-plans | 5 | 4 | 5 | 5 | 5 | **24** |
| B. Price-based decentralised coordination: units act on the LP's dual zone prices, plus a Bertsekas auction for conflicts | 4 | 4 | 4 | 4 | 4 | 20 |
| C. RL allocator (MAPPO/IPPO on the PettingZoo env, trained with shock/drift randomisation) | 4 | 2 | 3 | 5 | 3 | 17 |
| D. Bi-level RL + LP (learned terminal value for the MPC, as in Gammelli et al.) | 4 | 3 | 3 | 4 | 3 | 17 |
| E. MCTS planner instead of the LP | 3 | 2 | 3 | 4 | 3 | 15 |

## Six Thinking Hats (on option A)
- **White (facts).** The smoke test above shows planner gain ≫ forecaster gain at lead time ≤ patience. The CUSUM costs O(Z) per step; the MPC LP takes 17.7 ms at H=6 with HiGHS-IPM (benchmarked). In our partial search we found no work coupling a change detector to a rolling-horizon allocator.
- **Red (gut, judges).** A live demo where a judge clicks to create a shock, the detector fires, units pre-position and the baseline lags is memorable. A falsifiable phase diagram appeals to professors. Measured false-alarm rates and paired CIs appeal to Optiver.
- **Black (risks).** The detector may add ~nothing (today's evidence!). The CUSUM could fire on transient spikes and send units the wrong way. Synthetic data invites "toy" criticism. LP latency limits sweep size under CPU contention.
- **Yellow (benefits).** Each piece has an isolated metric (detection delay at fixed ARL₀; forecast error post-shock; planner served fraction under the oracle forecast). It transfers to compute clusters, where lead time = cold start, which is the user's systems strength.
- **Green (alternatives).**
  - BOCPD run-length mixture forecasts.
  - Conformal-PID safety stock sized by the detector state.
  - A spatial (multi-zone) CUSUM to detect faster.
  - Dual-price coordination (option B) as the multi-agent layer.
  - Real-trace replay (NYC TLC; the Azure traces are UNVERIFIED tonight).
- **Blue (decision).** Take A as the spike with an explicit, falsifiable hypothesis (below). Keep the MPC as best practice. Keep B as the second spike candidate after the 12 Oct selection. Run C as the RL comparator (stretch), so the "RL or planning" question is answered empirically rather than asserted.

## Thesis → antithesis → synthesis
- **Thesis.** Shocks break forecasts. An explicit detector restarts the forecast within about h/KL steps, so the MPC re-plans on the new regime and loses less demand after the shock than an EWMA forecaster tuned for quiet periods.
- **Antithesis (self-critique).**
  - The MPC already re-plans every step on the *observed queue*, and a queue is a faster, sharper "detector" than any count-based CUSUM. Today's run shows the oracle forecast ≈ EWMA ≈ CUSUM.
  - The detector is therefore second-order, and a well-tuned EWMA is a strong baseline.
  - Worse, a detector adds false-alarm risk on transient spikes.
- **Synthesis.**
  - The queue is a good detector **only if units can arrive before waiting demand abandons**, i.e. when the reallocation lead time L is at most the patience P.
  - When L > P (GPU cold starts of tens of seconds against request timeouts of seconds; large cities; tight delivery SLAs), every request arriving in the first L − P steps after a shock is lost unless supply was sent *before* the queue built. Then detection delay converts one-for-one into lost demand.
  - When requests are lost rather than queued (timeouts), the queue signal is censored, and count-based detection is the only signal left.
  - **So the spike is the regime-aware forecaster plus the claim of where it matters**, measured on a lead-time/patience grid. It is not a blanket "detector beats EWMA".

## First principles
The value of information about a shock is the demand that would be lost during (detection delay + lead time) beyond what patience covers. Roughly:

lost ≈ Δλ · max(0, d + L − P)

where Δλ is the extra demand rate, d the detection delay, L the reallocation lead time and P the patience. Reactive policies have d ≈ the queue build-up time. A CUSUM has d ≈ h / KL(λ₁‖λ₀). That gives two levers: reduce d (detector), or reduce effective L (pre-position using forecasts and units about to free up, which the MPC does). Our experiments vary P and the travel time per hop to trace this surface.

## Decision
- **Spike A:** components C4 (change detector) and C5 (forecaster) feeding C6 (MPC).
- **Hypothesis H1 (falsifiable):** mpc-cusum's shock-window lost demand < mpc-ewma's, by a margin that grows as P/L shrinks. At P ≥ L the difference is within noise. Tested on frozen seeds 100+, with paired bootstrap CIs and Holm correction.
- **Auto-research ratchet** on C4+C5 hyper-parameters and structure (delta, h, alpha, spatial pooling, BOCPD), against a frozen `eval.py` at P = 3.
- **Consequences:**
  - The planner, coordinator and simulator stay best practice.
  - RL (C8) is the comparator.
  - Option B is revisited for the finals' "multi-agent" emphasis.
  - If H1 is falsified everywhere, we report that honestly and the spike moves to B.
