# Round 1 abstract (final v1.0, 4 Oct 2026): Perceptron 2026, Problem 5

> Rendered from `round1-abstract.template.md` by `eval/render_docs.py`. Every result number comes from `eval/results/`, which `eval/check_docs.py` enforces. Tags: [built], [evaluated], [unresolved], [planned]. Teammates are placeholders until confirmed.

**Title:** *Twin-market execution: measure your own footprint before claiming to beat TWAP*

## 1. Problem and theme
Theme 3, **Problem 5: Market-Impact-Aware Execution Strategy**. A large order moves the price its owner then pays, and market makers such as Optiver sit on the other side of it. We want to know, with error bars, how much of our cost we caused, before trusting any "beats TWAP" number.

## 2. Understanding of the challenge
Slippage is endogenous: our child orders consume liquidity and other agents react, so no historical backtest can say what the price would have been without us. In the ABIDES simulator that counterfactual exists, but we measured three obstacles [evaluated]:
1. **Noise.** After our first trade, a same-seed twin without our order drifts apart. The twin mid gap's std grows from {{gap_std_60}}¢ after one minute to {{gap_std_1200}}¢ after twenty, while our mean impact at five minutes is {{gap_mean_300}}¢.
2. **Physics.** In the default market our impact is near-linear in size (log-log slope {{e7_delta_resolved}} [{{e7_delta_resolved_lo}}, {{e7_delta_resolved_hi}}]; empirical square-root law: 0.5) and leaves no detectable permanent component. With such impact, TWAP is close to optimal and scheduling gains are tiny.
3. **Statistics.** Effects of a fraction of a tick need paired designs, pre-registration and replication.

## 3. Proposed approach
- **Simulator** [built]: J.P. Morgan's ABIDES (rmsc04: an exchange and {{n_trading_agents}} noise, value, momentum and market-maker agents; 35-minute sessions), run through our Python 3.11 adapter.
- **Synchronised twins** [evaluated]:
  - Each seed runs with our agent and with a null agent. Re-keying every agent's random stream per wake-up (a common-random-numbers coupling) keeps them aligned; pre-trade mids match in {{twin_runs_identical}}/{{twin_runs_total}} runs.
  - Own-impact dispersion falls {{noise_reduction}}× ({{own_std_naive}} → {{own_std_sync}} bps); paired CIs tighten {{ci_tightening}}×.
  - The counterfactual is conditional on the simulator and this coupling.
- **Cost accounting** [built]: shortfall = drift + own impact (twin mid − our mid) + cost against the decision-time mid. That last term splits into decision-to-fill delay and at-fill cost (E12).
- **Realism gate** [planned]: recalibrate the agent mix (order splitting and liquidity replenishment drive square-root impact in an agent-based study, arXiv:2607.04280) until impact is concave and partly permanent; Microsoft's MarS is the out-of-family check.
- **Counterfactual-mid estimator** [unresolved]: a propagator fitted to twin paths (τ = {{e9_tau}} s) predicts the no-order mid from our fills (for a SELL: observed mid + estimated impact).
  - Held-out R² is {{e9_r2_twap}} (TWAP) and {{e9_r2_probe}} (random slicing).
  - Per-seed RMSE is {{e9_rmse}}¢, against {{e1_rmse}}¢ with naive twins.
- **Agent** [built]: a propagator-QP schedule plus child-order tactics.
  - Touch-capped orders cut cost against the decision mid by {{touch_instant_pct}}%, but lose {{touch_drift}} bps to timing.
  - Policy search is a development-time ratchet with paired comparisons and untouched confirmation seeds; PPO is deferred.

## 4. Minimum Viable mapping
1. *TWAP/VWAP baseline* [built]: 40 equal market-order slices; VWAP follows a volume curve from training seeds.
2. *Agent that beats the baseline* [evaluated]:
   - **E6:** the arm "QP schedule plus front-loading, market orders" beat TWAP on {{h1_n}} fresh seeds by {{h1_gain}} bps [95% CI {{h1_gain_lo}}, {{h1_gain_hi}}]. That is {{h1_cents}}¢ per share, or about ${{h1_usd}} on a ${{parent_usd_m}}M parent order. The hypothesis was fixed before inspecting results.
   - **E8:** on 100 validation seeds the gain did not reproduce ({{e8_IA_sched_only}} bps).
   - **E10:** our strictly pre-registered replication on {{e10_n}} new seeds gives {{e10_dis}} bps [{{e10_lo}}, {{e10_hi}}], so H2 is **{{e10_h2}}**. {{E10_SENTENCE}}

## 5. Stretch ambitions
- **Counterfactual book:** the null twin is the simulator's no-order book under our coupling [evaluated for the mid]. Depth and queue reconstruction, and a live estimator, are [planned].
- **Feedback loops:** under TWAP, value agents end the session holding {{fb_value}} [{{fb_value_lo}}, {{fb_value_hi}}] of our {{task_qty}} shares and momentum agents {{fb_momentum}} [{{fb_momentum_lo}}, {{fb_momentum_hi}}]. This is inventory redistribution, not yet a mechanism; timestamped response paths and agent-type ablations are [planned].

## 6. Novelty
Common random numbers are classical; reactive impact simulation exists (MarS, ABIDES-MARL); Olby et al. (ICAIF 2025) split slippage into impact and risk. Ours is an evaluation discipline for ABIDES execution research: a documented coupling with measured variance reduction, a per-seed cost decomposition, a realism gate before optimisation, and timestamped pre-registration with replication, including our own non-replication. We found no prior synchronised-twin study of order-book simulators (UNVERIFIED beyond our arXiv searches).

## 7. Evaluation plan
- **Primary:** implementation shortfall against the arrival mid, as a paired difference vs TWAP with bootstrap CIs, in bps, cents per share and dollars.
- **Secondary:** the cost terms, CVaR95, completion.
- **Claims:** only from pre-registered, fixed-size test blocks, with replication.
- **Baselines:** TWAP, VWAP, front-loaded TWAP, QP-only; Almgren–Chriss and Obizhaeva–Wang schedules [planned].
- **Realism:** impact-vs-size slope, permanence, market statistics.
- **Robustness:** {{e7_part_min}}–{{e7_part_max}}% participation, buys and sells, agent-type ablations, MarS.

## 8. Feasibility and risks
**Team:** Ashish (IIT Delhi; large-scale systems at Microsoft), plus [teammate 2: RL/ML] and [teammate 3: quant/statistics], to be confirmed.

**Plan:** weeks 1–2 realism gate; week 3 estimator; week 4 tactics and ratchet; replicated results by 17 November; exams 19–25 November (frozen); midway report 1 December; then MarS check and demo.

**Risks:** ABIDES may never reach realistic impact (fallback: MarS); gains may stay below a tick (we then report the instrument and an honest null); seed overfitting (untouched confirmation blocks).
