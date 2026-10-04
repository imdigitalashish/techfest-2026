# Autoresearch program: execution agent (C5–C7 policy parameters)

**Goal:** minimise the mean paired implementation-shortfall difference vs TWAP (bps) on validation seeds 100–139: SELL 4,000 shares, 09:35–09:55, 40 slots.

**Frozen evaluator:** `eval.py` (never edited by the loop). It prints the scalar on line 1 and the CI, win rate and own impact on line 2.

**Keep rule:** keep a change only if the new mean beats the incumbent by more than the incumbent's CI half-width / 2 **and** the new CI's upper bound < 0. Re-check every 5 kept changes on a fresh val slice (seeds 140–199) to catch seed overfitting. Test seeds (1000+) are used only by the lead for releases.

**Search space (only `execution_agent/policies.py` params or new policy code):**
1. `max_levels` ∈ {1, 2} and posting price (touch vs one tick inside).
2. Feedback gain `beta` ∈ [0, 1.5], `catchup_tol` ∈ [0.05, 0.3].
3. QP schedule on/off; kernel τ ∈ {30, 60, 120} s (sensitivity to calibration error).
4. A passive-first variant: post at our own touch, cross only when behind schedule.
5. Depth-adaptive sizing: scale the child by touch depth / median depth.
6. Later: a PPO policy over the same features (C11).

**Constraints:** 100% completion (forced sweep at the end). Contract tests must pass (`pytest -q tests`). No look-ahead (policies only see `DecisionContext`).

**Known pitfall:** the gain must not come only from spread capture. Always read `own_impact_bps` and run the tactic-only ablation.
