# ADR 001 — Spike choice: regime-aware look-ahead (detector → forecaster → MPC), tested along the lead-time / patience axis

- **Status:** accepted (morning-package version, 2026-10-04 07:00 IST). Revisit by 12 Oct with sweep results.
- **Deciders:** P7 project lead.
- **Process note:** PLAYBOOK §3 asks for an *independent* adversarial agent. Lean mode (no sub-agents after 05:50 IST, network saturated) made that impossible tonight. The antithesis below is the lead's own self-critique. An independent `rubber-duck` pass is queued for when sub-agents are allowed again.

## Context
- The MVP requires a rule-based allocator plus one RL or planning agent that beats it when demand suddenly shifts. The stretch goals are shock + drift in one run, and long horizons.
- "MPC on a demand forecast" for fleet rebalancing is established (Iglesias et al., ICRA 2018: wait time cut "by up to 89.6%"). Bi-level RL + LP is the research frontier (Gammelli et al. 2021–2025).
- Production systems use forecast + optimiser + **reactive guardrails** with fixed thresholds (Knative panic at 200% of capacity; AWS and Azure predictive scaling is scale-out only). See [landscape](../../research/landscape.md).
- **Evidence from our own runs** (held-out seeds 100–109, 1440 steps, K=40, P=10; `eval/results/mvp-v1/summary.md`; reproduce with `.venv/bin/python -m eval.harness --scenarios shock shock+drift --seeds 100-109 --horizon 1440 --out eval/results/mvp-v1 && .venv/bin/python -m eval.stats eval/results/mvp-v1`). Mean served fraction [95% bootstrap CI], and requests lost in the 120 steps after shock onset:

  | policy | shock: served | shock: lost after onset | shock+drift: served | shock+drift: lost after onset |
  |---|---|---|---|---|
  | static | 0.866 [0.862, 0.870] | 559 | 0.753 [0.741, 0.768] | 786 |
  | greedy | 0.910 [0.904, 0.919] | 355 | 0.739 [0.715, 0.769] | 665 |
  | reactive | 0.904 [0.898, 0.911] | 412 | 0.882 [0.873, 0.890] | 455 |
  | mpc-ewma | 0.950 [0.942, 0.958] | 274 | 0.936 [0.927, 0.945] | 334 |
  | mpc-cusum (v0 detector) | 0.949 [0.941, 0.956] | 274 | 0.934 [0.924, 0.942] | 351 |
  | oracle | 0.948 [0.941, 0.956] | 277 | 0.935 [0.926, 0.943] | 336 |

  - **Look-ahead beats the best rule on 10/10 seeds in both scenarios.** Shock: +3.9 pp, paired CI [+3.3, +4.6]. Shock+drift: +5.4 pp [+5.2, +5.7]. Wilcoxon p = 0.002 for each.
  - **Forecast quality (even clairvoyance) adds nothing measurable at P = 10.** The MPC policies above used the un-ratcheted v0 detector, and mpc-cusum is slightly worse than mpc-ewma on lost-after-onset under shock+drift (351 vs 334).
  - A single-seed pilot at H=8 (thought node Log, 06:20) showed the same pattern.

## Options scored (1–5: impact on judged criteria · novelty vs SOTA · feasibility by 15 Dec · measurability · demoability)

| Option | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| A. Regime-aware look-ahead: change detector (CUSUM → BOCPD) restarts the forecaster; conformal-calibrated buffers; MPC re-plans | 5 | 4 | 5 | 5 | 5 | **24** |
| B. Price-based decentralised coordination: units act on the LP's dual zone prices, plus a Bertsekas auction for conflicts | 4 | 4 | 4 | 4 | 4 | 20 |
| C. RL allocator (MAPPO/IPPO on the PettingZoo env, trained with shock/drift randomisation) | 4 | 2 | 3 | 5 | 3 | 17 |
| D. Bi-level RL + LP (learned terminal value for the MPC, as in Gammelli et al.) | 4 | 3 | 3 | 4 | 3 | 17 |
| E. MCTS planner instead of the LP | 3 | 2 | 3 | 4 | 3 | 15 |

## Six Thinking Hats (on option A)
- **White (facts).** The held-out grid above shows planner gain ≫ forecaster gain at lead time ≤ patience (P=10). The CUSUM costs O(Z) per step; the MPC LP takes 17.7 ms at H=6 with HiGHS-IPM (benchmarked). In our partial search we found no work coupling a change detector to a rolling-horizon allocator.
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

## Update 2026-10-04 08:05 IST — first test of H1 (not supported yet)
- **Run:** `eval/results/p3-v1` (shock, seeds 100–104, P=3, 1-step hops; reproduce with `.venv/bin/python -m eval.harness --scenarios shock --policies greedy reactive mpc-ewma mpc-cusum-v1 oracle --seeds 100-104 --patience 3 --horizon 1440 --out eval/results/p3-v1`).
- **Served fraction:** greedy 0.802 · reactive 0.783 · mpc-ewma 0.889 · mpc-cusum-v1 0.889 · oracle 0.890.
- **Look-ahead vs best rule:** +8.7 pp (paired CI [+7.0, +10.8]), 5/5 seeds; n=5 caps the Wilcoxon p at 0.062. The margin roughly doubles from P=10 (+3.9 pp). That fits the first-principles story: the shorter the patience, the more structurally late reactive allocation is.
- **H1 (detector beats EWMA, growing as P/L shrinks):** *not supported at P ∈ {3, 10} with 1-step hops*. The detector, the EWMA and even the clairvoyant forecast tie.
- **Reason:** lead time here is 1–3 steps and H=6, so the MPC's view of the *observed* queue plus the units about to free up already captures the shock. Forecasts only matter when L is large relative to the reaction window.
- **Next test:** a hop-time knob of 3–5 steps per hop, which needs multi-step edges in the time-expanded LP, with H ≥ L + P.
- **Fallback if that also ties:** promote Spike B (price-based decentralised coordination). Keep the look-ahead planner plus the measured (L, P) law as the headline.
