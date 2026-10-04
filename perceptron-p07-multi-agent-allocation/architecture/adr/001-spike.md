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
- **H1 (detector beats EWMA, growing as P/L shrinks):** *not supported at P ∈ {3, 10} with 1-step hops*. The detector, the EWMA and even the true-rate forecast tie.
- **Reason:** lead time here is 1–3 steps and H=6, so the MPC's view of the *observed* queue plus the units about to free up already captures the shock. Forecasts only matter when L is large relative to the reaction window.
- **Next test:** a hop-time knob of 3–5 steps per hop, which needs multi-step edges in the time-expanded LP, with H ≥ L + P.
- **Fallback if that also ties:** promote Spike B (price-based decentralised coordination). Keep the look-ahead planner plus the measured (L, P) law as the headline.

## Update 2026-10-04 10:40 IST — confirmatory evidence (mvp-v2, pre-registered) and a revised spike

**Primary (pre-registered, 30 fresh seeds 200–229, L=1, P=10; `eval/results/mvp-v2/confirm.md`).** `mpc-ewma` beats the pre-registered reference rule in **6/6 scenarios, 30/30 seeds each, Holm p = 1.1e-8**:
- shock: +3.73 pp [+3.28, +4.20]
- shock+drift: +5.47 [+5.36, +5.59]
- shock+drift+spikes: +5.99 [+5.82, +6.15]
- drift: +5.83
- spikes: +2.51
- stationary: +2.36

**Same-LP ablations (secondary S1–S3, Holm within family) — which look-ahead layer matters at L=1, P=10:**
- **Planning horizon helps everywhere.** Myopic (H=2) vs H=6: −0.12 to −2.29 pp (0/30 seeds better anywhere), with +25 to +43 more requests lost per shock.
- **The demand forecast is double-edged.**
  - Under *drift*, removing it (queue-only LP) costs −2.68 pp (0/30).
  - Under a *pure shock*, queue-only is **better**: +1.19 pp (30/30), and 62 fewer requests lost per shock (0/30 increase).
  - A **true-rate** forecast does not help in the shock either (−0.12 pp).
  - Interpretation: a certainty-equivalent LP over-trusts fractional expected demand in quiet zones and holds units back from the real queue at the shock.
- **The change detector (as built) hurts at L=1, P=10:** +8.0 [+4.5, +11.5] more requests lost per shock in the shock scenario (23/30 seeds), and −0.13 to −0.22 pp served fraction. This reproduces the phase-v1 harm at (1,10), which Addendum A pre-registered as a possible failure case.

**Revised spike (A′): regime-aware look-ahead.** The evidence says *what* the look-ahead plans on should depend on the regime:
- supply-side look-ahead (horizon, known incoming units) is always on;
- demand forecasts are trusted under drift and in quiet regimes;
- during an abrupt shock the planner should fall back towards the observed queues (forecast trust ↓);
- the change detector earns its place where lead time exceeds patience (phase-v1: P=3, L ≥ 2; replication phase-v2 pre-registered).

The detector's job shifts from "restart the level" to "gate how much the plan trusts the forecast". The exploratory `trust` sweep (0.25/0.5/0.75; `eval/results/trust-v2`) and the phase-v2 replication decide the final form.

**Limitations (from gpt-6-sol / gpt-6-astra reviews):**
- The LP lets demand be dropped, and at τ=0 does not force "stay ⇒ serve".
- Degenerate LP optima make trajectories solver-specific (the backend is recorded per run).
- L slows only empty repositioning (a set-up delay), not loaded trips.
- The stylised law G ≈ q([d_E+L−P]₊ − [d_D+L−P]₊) predicts a kink and a plateau, not unbounded growth. The mechanism test is planned.

## Decision (revised 2026-10-04 10:55 IST) — supersedes H1 and the "restart the forecast" spike

**Evidence.**
- *phase-v2* is the pre-registered replication (Addendum A): fresh seeds 200–219, abandonment-aware LP.
  - **H1 did not replicate.** Detector − EWMA, requests lost per shock: +4.4 at (1,10), Holm p = 0.026; +21.9 at (8,10), Holm p = 0.011. Only (2,3) points the predicted way (−9.3, n.s.).
  - Even the **true-rate** forecast lowers served fraction at long lead times: −1.09 / −1.49 / −1.10 pp at (4,3) / (8,3) / (8,10).
  - Under the legacy never-abandoning backlog (phase-v1) the same comparisons were positive. **Forecast value depends on how the planner treats uncertain demand.**
  - The "51–71% capture" figure is **retired**. It held only under the legacy planner.
  - A paired same-seed planner-sensitivity run (`eval/results/phase-v2c`) quantifies this.
- *Robust across everything run:* planning over the lead time beats the best rule.
  - Pre-registered mvp-v2: 6/6 scenarios, 30/30 seeds.
  - phase-v2: 7/8 cells, 20/20 seeds each.
  - Week: +6.3 pp. Month: +6.4 pp. NYC real trace: +2.5 pp.
  - Pareto: at a move cost of 0.5 the planner serves more *and* moves less than the reactive rule.
- *Prior art for the mechanism* — a more accurate forecast is not a better decision:
  - Elmachtoub & Grigas, "Smart Predict, then Optimize", Management Science 2022;
  - Wilder, Dilkina & Tambe, decision-focused learning, AAAI 2019.
  - Both verified (`research/landscape.md` §3b).

**Decision.**
- **Spike A″ = decision-aware forecast trust.** The planner plans on trust_z × forecast_z. Trust is set per zone from calibrated forecast uncertainty and the change detector's regime state, and tuned on **served fraction (decision loss), not forecast error**.
- The change detector is kept only as an input to trust, not as a level-restart.
- Novelty claim kept narrow: the decision-focused idea is prior art. Our contribution is (a) its use for regime-gated trust in lead-time-aware dispatch, and (b) the measured (L, P) map, including failures. A wider prior-art check is to be done before the 31 Oct claim.

**Pre-registered falsification test (to be committed before running, as Addendum B):**
- On fresh seeds, across the (L, P) grid and the scenario suite, tuned trust must beat **both** trust = 1 (EWMA-MPC) and trust = 0 (queue-only LP) on served fraction, with Holm correction.
- If it does not, we report that, and the deliverable rests on the robust planning claim plus the map.
- Exploratory signal so far: the trust sweep at L=1, P=10 (`eval/results/trust-v2`).

**Consequences.**
- The abstract leads with the robust claim plus the finding "a better forecast can make a certainty-equivalent planner serve fewer people".
- Innovation headroom in the memo is lowered to 3, with an honest note.
- The RL comparator and decentralised price coordination remain stretch goals.

## Update 2026-10-04 11:00 IST — paired planner sensitivity (`eval/results/phase-v2c/summary.md`, same seeds 200–219)

**Under the legacy queue-chasing backlog (never abandons), the phase-v1 pattern replicates on fresh seeds.**
- True-rate − EWMA: +0.99 / +1.88 / +3.63 / +1.13 pp at (2,3) / (4,3) / (8,3) / (8,10), 20/20 seeds each.
- Detector − EWMA: +0.45 (18/20) / +1.28 (20/20) / +2.63 (20/20) / +0.70 (18/20).
- Null at (1,3), (2,10) and (4,10); slight harm at (1,10).

**Under the abandonment-aware backlog the same comparisons are negative** at long lead times.

**Neither base planner dominates with EWMA.** Legacy − new = +0.30 at (1,3) and +0.88 at (8,10), but −0.57 at (4,3) and −1.66 at (8,3).

**Conclusion.** The value of a better forecast, and of the change detector, is a property of the *forecast–planner pair*. It is not a property of forecast accuracy, nor of (L, P) alone. This strengthens the decision-aware trust spike (A″): trust must be tuned on the decision outcome for the planner actually deployed. The pre-registered falsification test (Addendum B) will cover both planner variants.

## Update 2026-10-04 11:15 IST — gated-trust preview on tuning seeds (`eval/results/gated-tuning-preview/summary.md`)

- **Setup:** seeds 0–9 (tuning only); L=1, P=10; abandonment-aware LP.
- **Gating adds ≈0 over the best fixed trust.**
  - shock+drift: the best gated arm (τ_shock 0.25, τ_quiet 0.5) is +0.99 pp vs EWMA (10/10), but only +0.01 pp vs fixed trust 0.5.
  - shock: fixed trust 0.25 is best.
  - τ_quiet = 1 with any τ_shock equals EWMA.
- **So the benefit is *global* shrinkage of the forecast** (hedging certainty equivalence), not local down-weighting around alarms.
- **Design note for Addendum B** (to be amended, dated, before any test run):
  - Make the regime signal city-wide: trust ↓ globally while any shock regime is active.
  - Add an uncertainty-calibrated shrinkage (e.g. per-zone forecast variance relative to the mean), so trust is not a single hand-tuned scalar.
  - Fixed-trust and extremes remain the comparators.

## Update 2026-10-04 17:58 IST — design-space preview on tuning seeds (`eval/results/trust-designs-tuning-preview/summary.md`)

- **Setup:** seeds 0–9 only; L=1, P=10. Designs: city-wide regime gate (`mpc-gated@scope=1`); detector-free uncertainty shrinkage (`mpc-unctrust@kappa`); fixed global trust 0.5.
- **No adaptive design beats the best fixed global trust (0.5).**
  - Best city gate: +0.02 pp [−0.03, +0.06] (shock); −0.05 (shock+drift).
  - Uncertainty shrinkage: −0.02 at best (shock, κ=1); −0.15 at best (shock+drift, κ=0.5).
- **Implication for Addendum B/B1:** at (1,10) the spike will likely fail criterion (b) (beat the best fixed trust). The effective ingredient so far is decision-tuned *shrinkage* (a fixed trust chosen on served fraction), not regime adaptivity.
- **Before the test run:** tune across the full (L,P) grid on seeds 0–49. Adaptivity may matter at long lead times, where forecasts hurt most.
- **Fallback claim if (b) fails:** "a single decision-tuned trust level beats both certainty equivalence and ignoring the forecast", subject to criterion (a) on fresh seeds.
