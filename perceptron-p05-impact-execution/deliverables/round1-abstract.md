# Round 1 abstract (draft v0.1, 4 Oct 2026): Perceptron 2026, Problem 5

> Draft for the 31 Oct submission (600–900 words; currently ≈ 880). Numbers marked † come from committed runs (`eval/results/`), reproducible with the commands in `perceptron-p05-impact-execution/thought_node.md`. **Team names and skills are placeholders until the user confirms the team.**

**Title:** *Ghost-Book Execution: measuring and minimising our own market impact with counterfactual twin markets*

## 1. Problem and theme
Theme 3 (Markets & Trading Intelligence), **Problem 5: Market-Impact-Aware Execution Strategy**. A large order moves the very price its owner then pays; market makers like Optiver sit on the other side of it. We want an agent that knows its own footprint, and an evaluation that proves it.

## 2. Understanding of the challenge
Slippage is **endogenous**. When we sell, our child orders consume bids, displace the mid, and trigger reactions: market makers re-quote, momentum traders join, value traders absorb. Part of that displacement decays and part persists, so a historical backtest can't answer "what would the price have been without us?". In a simulator the counterfactual exists, but we found it is fragile. In ABIDES, a world with our order and its same-seed twin without it are bit-identical until our first trade (80/80 runs)†. After that they **decorrelate**: the std of the twin mid-price gap grows from 4.7¢ at 1 minute to 33¢ at 20 minutes, while our systematic impact is only ~3–5¢†. The crux is therefore twofold: act on an impact signal that is small compared with market noise, and **measure** it well enough to prove the agent beats TWAP for the right reason.

## 3. Proposed approach
- **Simulator:** J.P. Morgan's **ABIDES** (rmsc04: exchange plus 1,117 noise, value, momentum and adaptive market-maker agents), running on Python 3.11 through our adapter. One simulated day takes ≈1 s on an M5 Mac†.
- **Counterfactual twins:** every episode runs twice on the same seed, with our agent and with a null agent. To cut decorrelation we will **re-key each background agent's random stream per wake-up** (random-number synchronisation), so the twins differ only through causal responses to our orders.
- **Exact cost decomposition:** shortfall = *drift* (twin mid move) + *own impact* (twin mid − our mid) + *instantaneous cost* (spread, book walking); an identity enforced by unit tests†.
- **Own-impact model:** a propagator I(t) = Σ qᵢ·(g_perm + g_tr·e^{−(t−tᵢ)/τ}) fitted to twin-measured impact paths. The current fit on train seeds gives τ ≈ 60 s†. The deployable **ghost book** (observed mid minus estimated own impact) is trained against the twins but uses only observable data, as a live desk would.
- **Impact-aware agent:** (i) a schedule that solves the discrete propagator-model quadratic program, (ii) feedback that slows down while our estimated own impact is above its steady state, and (iii) child orders capped at the touch, with the remainder posted passively. Forced completion at the deadline.
- **Optimiser:** an autoresearch ratchet on validation seeds (keep only significant gains); PPO on the same features as a challenger.

## 4. Minimum Viable mapping
1. *TWAP/VWAP baseline:* **built.** TWAP sends 40 equal market-order slices. VWAP follows a volume curve learned on training seeds only.
2. *Agent that measurably beats the baseline on slippage:* **built.** On held-out seeds (preliminary, n = 18), the impact-aware agent's shortfall is 0.78 bps vs TWAP's 1.38 bps. The paired difference is **−0.60 bps [95% CI −1.12, −0.10]** and it wins on 67% of seeds†. An ablation shows most of the gain comes from not walking the book (touch-only tactic: −0.62 bps). That cuts our twin-measured own impact from 0.71 to ≈ 0.15 bps†. By 31 Oct we will report n = 200 test seeds.

## 5. Stretch ambitions
- **Counterfactual book:** synchronised twins give the exact "book without our order". The ghost-book estimator reproduces it live, scored by RMSE against the twin.
- **Feedback loops:** who absorbed our 4,000 shares and who amplified them (per agent type), market-maker spread/depth response, and impulse responses after completion, including adaptive market makers (cf. ABIDES-MARL, 2025).

## 6. Novelty
Prior work trains RL agents in reactive simulators and reports "beats TWAP" (Karpe 2020; Hafsi & Vittori 2024; Olby et al. 2025). We add: (a) **paired twin evaluation** with an exact own-impact decomposition per seed; (b) a measured **decorrelation problem** and a fix (random-number synchronisation), which we have not found in the literature; (c) a **deployable** counterfactual estimator certified against ground truth; (d) ablations that attribute savings to schedule, tactic and feedback.

## 7. Evaluation plan
- **Primary metric:** implementation shortfall (bps vs arrival mid), as the paired ΔIS vs TWAP with 95% bootstrap CIs and win rate.
- **Secondary:** std, CVaR95, the drift/own-impact/instant split, mark-outs at +5/+10 min, 100% completion.
- **Seeds:** disjoint train (calibration) / validation (tuning) / test (claims) sets.
- **Baselines:** TWAP, VWAP, Almgren–Chriss, and tactic-only and schedule-only ablations.
- **Realism scorecard:** impact-vs-size exponent against the square-root law (δ ≈ 0.5, Sato & Kanazawa, PRL 2025) and decay after completion.
- **Robustness:** 3–25% participation, buy and sell, market-maker ablations, and Microsoft's MarS generative simulator.

## 8. Feasibility and risks
**Team:** Ashish (IIT Delhi; large-scale systems at Microsoft) plus *[teammate 2: RL/ML]* and *[teammate 3: quant/statistics]*, to be confirmed.

**Plan:**
- Weeks 1–2: synchronised twins and realism scorecard.
- Week 3: ghost-book estimator.
- Week 4: agent ratchet and PPO.
- Before 17 Nov: n = 200 test results and the feedback analysis.
- 19–25 Nov: exams (frozen).
- 1 Dec: midway report.
- Then: MarS check and demo.

**Risks:**
- Decorrelation may be intrinsic chaos. Mitigation: more seeds and control variates.
- Unrealistic ABIDES impact. Mitigation: the scorecard and MarS.
- Overfitting to seeds. Mitigation: a held-out test set.
- Gains that are only spread capture. Mitigation: decomposition and ablations.
