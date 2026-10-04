# Round 1 abstract (final v1.1, 4 Oct 2026): Perceptron 2026, Problem 5

> Rendered from `round1-abstract.template.md` by `eval/render_docs.py`. Every result number comes from `eval/results/`, which `eval/check_docs.py` enforces. Tags: [built], [evaluated], [unresolved], [planned]. Teammates are placeholders until confirmed.

**Title:** *Twin-market execution: measure your own footprint before claiming to beat TWAP*

## 1. Problem and theme
Theme 3, **Problem 5: Market-Impact-Aware Execution Strategy**. A large order moves the price its owner pays, and market makers such as Optiver sit on the other side. Before trusting any "beats TWAP" number, we want to know, with error bars, how much of our cost we caused.

## 2. Understanding of the challenge
Slippage is endogenous: our orders consume liquidity; other agents react. Historical replay cannot identify the no-order price; an agent-based simulator (ABIDES) supplies a model-conditional one. We measured three obstacles [evaluated]:
1. **Noise.** After our first trade a same-seed twin without our order drifts apart: the mid gap's std grows from 4.7¢ (1 min) to 33¢ (20 min), while the 5-min mean gap is 3.2¢.
2. **Physics.** Impact grows roughly linearly with size: the registered five-size slope is 1.01 [0.55, 1.76] (75% of bootstrap draws usable; post hoc three-size estimate 0.87), against δ ≈ 0.5 for the square-root law. Whether any impact is permanent is unresolved.
3. **Statistics.** Sub-tick effects need paired designs, pre-registration and replication.

## 3. Proposed approach
- **Simulator** [built]: J.P. Morgan's ABIDES (rmsc04: an exchange and 1,116 noise, value, momentum and market-maker agents; 35-minute sessions), run through our Python 3.11 adapter.
- **Synchronised twins** [evaluated]:
  - Each seed runs with our agent and a null agent, coupled by re-keying every background agent's random stream at each wake-up (common random numbers). Pre-trade top-of-book event logs match exactly (60 seeds × 3 arms, E12).
  - In E4 (30 seeds), own-impact dispersion fell 6× (0.97 → 0.16 bps). On the same 60 test seeds, paired-difference std fell 7.7× (median of four policies; E3 vs E5).
  - The coupling keeps volume and trade counts within ±10% but widens mean spreads by 13%; volatility, autocorrelation and depth are unresolved (E11). Counterfactuals are conditional on this altered market.
- **Cost accounting** [built]: shortfall = drift + own impact (twin mid − our mid) + cost against the decision-time mid. It splits into decision-to-fill delay and at-fill concession.
- **Realism gate** [planned]: calibrate the agent mix to external, pre-declared impact targets (square-root exponent, permanent fraction), with held-out checks; MarS is the out-of-family check.
- **Counterfactual-mid estimator** [unresolved]: a propagator fitted to twin paths (τ = 120 s) predicts the no-order mid from our own fills (SELL: observed mid + estimated impact). Held-out R² is 0.15 / -0.02 on the seed-averaged path (TWAP / random slicing) and 0.010 / -0.004 per seed.
- **Agent** [built]: a propagator-QP schedule plus child-order tactics.
  - Touch-capped orders cut the at-fill concession by 0.041 bps vs TWAP. The same arm gives it back in drift (+0.023) and impact, so net ΔIS is +0.001 [-0.032, +0.033] (E12).
  - A paired candidate-vs-incumbent search with untouched confirmation seeds is [planned]; PPO is deferred.

## 4. Minimum Viable mapping
1. *TWAP/VWAP baseline* [built]: 40 equal market-order slices; VWAP follows a volume curve from training seeds.
2. *Agent that beats the baseline* [evaluated; not yet met on total slippage]. ΔIS is our shortfall minus TWAP's on the same seed (negative = cheaper).
   - **E6:** QP schedule plus front-loading (market orders) on 200 fresh seeds gave ΔIS -0.034 bps [95% CI -0.056, -0.013]. Hypothesis fixed before inspecting results.
   - **E8:** on 100 validation seeds it was not reproduced (ΔIS +0.006 bps).
   - **E10:** the strictly pre-registered replication on 400 new seeds gave ΔIS -0.013 bps [-0.029, +0.003]: H2 **not confirmed**.
   - E10's descriptive attribution detected a QP-associated own-impact reduction (-0.014 bps [-0.025, -0.002]); front-loading's effect lay within ±0.02 bps.
   - Pooled over both fixed-size test blocks (n = 600, descriptive): ΔIS -0.020 bps [-0.032, -0.007], i.e. 0.20¢ per share.
   - We do not claim to beat TWAP. The next test runs in a calibrated market.

## 5. Stretch ambitions
- **Counterfactual book:** the null twin is the simulator's no-order book under our coupling [evaluated for the mid]. Depth reconstruction and a live estimator are [planned].
- **Feedback loops:** in net-inventory terms, value agents end the session 4,096 shares longer (102% of our 4,000). No momentum amplification was detected (+70 [-60, +204] shares). Response paths and agent ablations are [planned].

## 6. Novelty
Common random numbers are classical, reactive impact simulation already exists (MarS, ABIDES-MARL), and Olby et al. (ICAIF 2025) split slippage into impact and risk. Ours is an evaluation discipline: a documented coupling with measured variance reduction and side effects, a per-seed cost decomposition, a realism gate before optimisation, and timestamped pre-registration with replication, including our own non-replication.

## 7. Evaluation plan
- **Primary:** paired shortfall vs TWAP (arrival-mid benchmark) with bootstrap CIs, in bps and cents per share.
- **Secondary:** the cost terms, CVaR95, completion.
- **Claims:** pre-registered, fixed-size test blocks with replication.
- **Baselines:** TWAP, VWAP, front-loaded TWAP, QP-only; Almgren–Chriss and Obizhaeva–Wang schedules [planned].
- **Realism:** impact-vs-size slope, permanence, market statistics.
- **Robustness:** 3–47% participation, buys and sells, agent-type ablations, MarS.

## 8. Feasibility and risks
**Team:** Ashish (IIT Delhi; large-scale systems at Microsoft), plus [teammate 2: RL/ML] and [teammate 3: quant/statistics], to be confirmed.

**Plan:** weeks 1–2 realism gate; week 3 estimator; week 4 tactics and search; replicated results by 17 Nov; exams 19–25 Nov (frozen); midway report 1 Dec; then MarS and demo.

**Risks:** ABIDES may miss the calibration targets (fallback: MarS); gains may stay sub-tick (we would report the instrument and an honest null); seed overfitting (untouched confirmation blocks).
