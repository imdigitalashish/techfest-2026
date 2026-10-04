# ADR 001: Spike choice. Synchronised counterfactual twins (C2) feeding a deployable own-impact model (C4)

- **Status:** accepted (first version, 4 Oct 2026, 07:35 IST). **First evidence, 08:12 IST:** synchronised twins cut the own-impact term's per-seed std from 0.971 to 0.164 bps, and NSR at T1 from 4.7 to 1.4 (E4, 30 val seeds; `eval/results/nsr_E4_nsr_naive_vs_E4_nsr_sync.md`). Review on 12 Oct with the selection memo.
- **Deciders:** P5 lead (solo, lean mode; the adversarial pass was done by the lead, not an independent agent. **To redo with an independent rubber-duck agent once sub-agents work again.**)

## Context
- The brief's minimum viable product is "TWAP/VWAP baseline + one agent that measurably beats it on slippage". Stretch goals: counterfactual "book without our order" and multi-step feedback analysis.
- "RL/heuristic beats TWAP in a simulator" is crowded prior art (Karpe 2020; Hafsi & Vittori 2024; Espana–Hafsi–Lillo 2025; Olby et al. ICAIF 2025; see `research/landscape.md` §3). Karpe et al. even report their RL agent "converges towards a TWAP strategy" in some scenarios.
- **Our measurement (E1, 40 train seeds, committed):** same-seed ABIDES twins are bit-identical before our first order (80/80), but the twin gap Δmid then decorrelates. Its std grows 4.7¢ → 33¢ → 64¢ (60 s → 20 min → 30 min) while the mean own impact is only ~3–5¢. An impact kernel fitted on 20 seeds has **negative out-of-sample R²**. So any claim that "agent X has lower impact" is currently noise-limited, and so is any "ghost book".

## Options considered (score 1–5: judged impact · novelty · feasibility · measurability · demo)
| Option | Score | Note |
|---|---|---|
| A. PPO/DQN execution agent in ABIDES-Gym | 4·2·3·3·3 = **15** | Crowded; gym 0.18/ray 1.7 pins are a Py3.11 install risk; the win is often spread capture rather than impact awareness |
| B. Propagator-QP schedule + touch-limit tactics (impact-aware heuristic) | 4·3·5·4·3 = **19** | Our MV agent; already built and running on test seeds |
| **C. ★ Synchronised twins: per-agent, per-wakeup RNG re-keying so the twins differ only through causal responses to our orders, then a deployable own-impact / ghost-book estimator validated against them** | 5·5·4·5·5 = **24** | Turns stretch goal 1 into a rigorous, measurable instrument; also powers stretch goal 2 and gives a much lower-variance evaluation of A/B |
| D. MarS generative simulator as the main environment | 3·4·2·3·4 = **16** | Linux/GPU; better as a robustness check (stretch) |
| E. Multi-agent (ABIDES-MARL-style) adaptive market makers | 4·4·2·3·4 = **17** | Prior art exists (2511.02016); keep as a feedback-loop ablation, not the spike |

**Decision:** spike = **C2 twin_runner (RNG synchronisation) + C4 impact_model (ghost book)**. B is the minimum-viable agent and the vehicle for the autoresearch ratchet. Everything else is best practice.

## Six Thinking Hats
- **White (facts):** twins are exactly paired up to our first order. Divergence noise dominates later (numbers above). Sims cost 0.9 s idle and ~10 s under tonight's load. rmsc04 has 1,117 background agents, each with its own seeded RandomState (verified in `rmsc04.py`).
- **Red (gut):** judges from a market maker will love "we measured our *own* footprint exactly and know who absorbed it". A plot of the real book and its ghost twin is a memorable demo.
- **Black (risks):** (1) Re-keying may not cut the divergence if it is genuinely chaotic (state-dependent decisions), not stream misalignment. Mitigation: measure NSR before/after; even a negative result is reportable, and the paired evaluation still works with more seeds. (2) Re-keying changes the simulator's stochastic structure. Mitigation: show stylised facts are unchanged (realism scorecard C1). (3) Over-engineering vs the MV bar. Mitigation: B already satisfies the MV.
- **Yellow (benefits):** variance reduction makes every downstream claim cheaper and sharper. Exact own-impact labels allow supervised training of the ghost-book estimator (no RL needed). It enables per-agent-type attribution (feedback loops) for free.
- **Green (alternatives):** antithetic twins; control variates (twin drift as a covariate); common-random-number "branching" (fork the kernel state at T0 and replay); learning the ghost book with a small sequence model; checking the square-root law in ABIDES (does rmsc04 even reproduce δ ≈ 0.5? cf. 2607.04280).
- **Blue (process):** C2 gets an autoresearch loop with frozen metric **NSR** (std/|mean| of Δmid at T1 over 40 val seeds). C4 gets a loop with frozen metric **ghost-book RMSE** vs the twin mid. B gets a loop with frozen metric **paired ΔIS vs TWAP on val seeds**. Test seeds are used only for releases.

## Thesis → antithesis → synthesis
- **Thesis:** exact, low-variance counterfactuals are the missing instrument. With them, "impact-aware" becomes a measured property (own-impact bps) instead of a story, and both stretch goals become quantitative.
- **Antithesis (strongest case against):** judges score the *agent*, not the instrument. Real markets have no twin, so a twin-only method is a lab curiosity. And if ABIDES' impact is unrealistic (no square-root law), precise measurement of the wrong physics is worthless.
- **Synthesis:** (1) keep the agent at the centre of the pitch: the twins *train and certify* a **deployable** ghost-book estimator that uses only observables, which is exactly what a live desk could run; (2) report the C1 realism scorecard (impact vs size exponent, decay) next to every claim; (3) show the agent beats TWAP on paired test seeds under both naive and synchronised twins.

## First principles
Slippage for a SELL = (exogenous drift) + (our own displacement of the mid) + (spread and book walking). Only the last two are controllable, and only the middle one is "market impact". You can't optimise what you can't measure: with naive twins, the middle term's per-seed noise (~1.36 bps std) is ≈ 11× its mean (~0.12 bps) for TWAP in E1. The bottleneck is the measurement, not the policy class.

## Consequences
- Next build items: `rng_sync="per_wakeup"` in C1/C2 (patch each background agent's `wakeup` to re-key `random_state` from (seed, agent_id, wakeup_count)); NSR measurement; C4 trained against synchronised twins; the C10 attribution plot.
- Evaluation always reports IS **decomposed** (drift / own impact / instant) and paired ΔIS with 95% CIs.
