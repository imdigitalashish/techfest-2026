# Round 1 abstract (final v1.0, 4 Oct 2026): Perceptron 2026, Problem 5

> Rendered from `round1-abstract.template.md` by `eval/render_docs.py`. Every result number comes from `eval/results/`, which `eval/check_docs.py` enforces. Tags: [built], [evaluated], [unresolved], [planned]. Teammates are placeholders until confirmed.

**Title:** *Twin-market execution: measure your own footprint before claiming to beat TWAP*

## 1. Problem and theme
Theme 3, **Problem 5: Market-Impact-Aware Execution Strategy**. A large order moves the price its owner pays; market makers such as Optiver sit on the other side. We want to know, with error bars, how much of our cost we caused before trusting any "beats TWAP" number.

## 2. Understanding of the challenge
Slippage is endogenous: our orders consume liquidity and other agents react, so no backtest can say what the price would have been without us. ABIDES can, but we measured three obstacles [evaluated]:
1. **Noise.** A same-seed twin without our order drifts apart after our first trade: the mid gap's std grows from 4.7¢ (1 min) to 33¢ (20 min), against a mean impact of 3.2¢.
2. **Physics.** In the default market our impact is near-linear in size (log-log slope 0.87 [0.57, 1.35]; square-root law: δ ≈ 0.5) and fully transient, so TWAP is near-optimal and scheduling gains are tiny.
3. **Statistics.** Sub-tick effects need paired designs, pre-registration and replication.

## 3. Proposed approach
- **Simulator** [built]: J.P. Morgan's ABIDES (rmsc04: an exchange and 1,116 noise, value, momentum and market-maker agents; 35-minute sessions) via our Python 3.11 adapter.
- **Synchronised twins** [evaluated]:
  - Each seed runs with our agent and with a null agent. Re-keying every agent's random stream per wake-up (a common-random-numbers coupling) keeps them aligned; pre-trade books match event-by-event in 180/180 runs checked exactly.
  - Own-impact dispersion falls 6× (0.97 → 0.16 bps); paired CIs tighten 7.7×.
  - The counterfactual is conditional on the simulator and the coupling. The coupling keeps volume and trade counts within ±10% but widens mean spreads by 13% (E11), so it describes a slightly different market.
- **Cost accounting** [built]: shortfall = drift + own impact (twin mid − our mid) + cost vs the decision-time mid, split into decision-to-fill delay and at-fill cost.
- **Realism gate** [planned]: recalibrate the agent mix (order splitting and liquidity replenishment drive square-root impact in arXiv:2607.04280) until impact is concave and partly permanent; MarS is the out-of-family check.
- **Counterfactual-mid estimator** [unresolved]: a propagator fitted to twin paths (τ = 120 s) predicts the no-order mid from our fills (SELL: observed mid + estimated impact); held-out R² is 0.15 (TWAP) and -0.02 (random slicing), per-seed RMSE 5.0¢ vs 19.7¢ with naive twins.
- **Agent** [built]: a propagator-QP schedule plus child-order tactics.
  - Touch-capped orders improve the fill price by 0.041 bps [0.036, 0.046] vs TWAP (genuine price improvement, not decision-to-fill movement; E12), but give it back in timing (+0.026 bps).
  - Policy search: a development-time ratchet with paired comparisons and untouched confirmation seeds; PPO deferred.

## 4. Minimum Viable mapping
1. *TWAP/VWAP baseline* [built]: 40 equal market-order slices; VWAP follows a volume curve from training seeds.
2. *Agent that beats the baseline* [evaluated; not yet met on total slippage]. ΔIS = our shortfall − TWAP's on the same seed (negative = cheaper):
   - **E6:** QP schedule plus front-loading (market orders) on 200 fresh seeds: ΔIS -0.034 bps [95% CI -0.056, -0.013]; the hypothesis was fixed before inspecting results.
   - **E8:** on 100 validation seeds it did not reproduce (ΔIS +0.006 bps).
   - **E10:** the strictly pre-registered replication on 400 new seeds gives ΔIS -0.013 bps [-0.029, +0.003]: H2 **not confirmed**.
   - What replicated is smaller: the QP schedule lowers own impact (-0.014 bps [-0.025, -0.002]) but pays part back in instantaneous cost; front-loading is negligible.
   - Pooled over both fixed-size test blocks (n = 600, descriptive): ΔIS -0.020 bps [-0.032, -0.007], 0.20¢ per share cheaper.
   - We do not yet claim to beat TWAP: with near-linear impact the headroom is tiny, so the realism gate comes first.

## 5. Stretch ambitions
- **Counterfactual book:** the null twin is the simulator's no-order book under our coupling [evaluated for the mid]. Depth and queue reconstruction, and a live estimator, are [planned].
- **Feedback loops:** with synchronised twins, value agents absorb 102% of our 4,000 shares by session end, while momentum agents end at +70 [-60, +204] shares. The amplification that naive twins suggested vanishes. This is inventory redistribution, not yet a mechanism; response paths and agent ablations are [planned].

## 6. Novelty
Common random numbers are classical; reactive impact simulation exists (MarS, ABIDES-MARL); Olby et al. (ICAIF 2025) split slippage into impact and risk. Ours is an evaluation discipline: a documented coupling with measured variance reduction, a per-seed cost decomposition, a realism gate before optimisation, and timestamped pre-registration with replication, including our own non-replication.

## 7. Evaluation plan
- **Primary:** paired shortfall vs TWAP (arrival-mid benchmark) with bootstrap CIs, in bps and cents per share.
- **Secondary:** the cost terms, CVaR95, completion.
- **Claims:** pre-registered fixed-size test blocks with replication.
- **Baselines:** TWAP, VWAP, front-loaded TWAP, QP-only; Almgren–Chriss and Obizhaeva–Wang schedules [planned].
- **Realism:** impact-vs-size slope, permanence, market statistics.
- **Robustness:** 3–47% participation, buys and sells, agent-type ablations, MarS.

## 8. Feasibility and risks
**Team:** Ashish (IIT Delhi; large-scale systems at Microsoft), plus [teammate 2: RL/ML] and [teammate 3: quant/statistics], to be confirmed.

**Plan:** weeks 1–2 realism gate; week 3 estimator; week 4 tactics and ratchet; replicated results by 17 Nov; exams 19–25 Nov (frozen); midway report 1 Dec; then MarS and demo.

**Risks:** ABIDES may never reach realistic impact (fallback: MarS); gains may stay sub-tick (we would report the instrument and an honest null); seed overfitting (untouched confirmation blocks).
