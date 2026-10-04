# Code review of the measurement pipeline (sub-agent `p5-code-review`, read-only, finished ~09:35 IST 4 Oct 2026)

Verbatim summary of the agent's report. The bug fix is in `components/execution_agent/execution_agent/policies.py` (`ref_mode="pre_trade"`).

**One real logic error: the impact-aware feedback almost never slows trading down.**
- **Where:** `policies.py:164-167`, medium severity.
- **Problem:** `own_impact(ctx)` is measured before this slot's trade, so it sums past fills only, the latest one 30 s old. `ref = rate·g_tr/(1−e^{−dt/τ})` is the steady state measured right after a trade, so it includes a fill at the current instant. When trading exactly at the average rate, own impact is ref·e^{−dt/τ}, about 0.61·ref. That gives excess ≈ −0.39 and a multiplier of about 1.2.
- **Evidence:**
  - The feedback signal was recomputed from the saved fills and decisions for every IA decision in slots 1–38 (4,560 decisions each in E5_test_sync and E3_test). It said "slow down" in only 0.02% and 0.04% of decisions. Mean excess was −0.42, range −0.92 to +0.13.
  - An offline replay reproduces the logged slice sizes for seed 1000. With feedback the first three slices are 145, 153, 81; the optimal schedule without feedback gives 145, 115, 104.
- **Impact on reported numbers:** the E3/E5 numbers are valid measurements of the code as written, but the explanation is not. The −0.050 bps result and the −16% own impact come from the propagator-optimised schedule plus a systematic speed-up, not from slowing down while the book is displaced. E6, the hypothesis registered in advance, inherits the same problem.
- **Minimal fix:** compare against the before-trade steady state, `ref·e^{−dt/τ}`, and run a variant with `use_feedback=False` to separate the effects.

**Checked and found correct:**
- **Twins diverge only after our first order.**
  - After `build_config`, the global RNG is used only by `config_add_agents`, identically in both arms, and by the oracle's megashock draw. The expected number of megashocks per session is about 6e-6.
  - The latency model is deterministic.
  - Message and order ids only break ties between messages from the same sender to the same recipient at the same time, so background ordering is unchanged.
  - Before 09:35 the null agent sends the same messages as the treatment agent, and the exchange's delays are 0.
  - Pre-window mids are identical in 300/300 runs.
- **`_synchronise_rng`:**
  - State is bound fresh on each loop iteration, so agents don't share it.
  - Both instance-level wrappers take effect; E4's naive and synced markets differ.
  - Value agents' next wake time is the first draw after re-keying.
  - There are no seed collisions within a world, and none across seeds 1000–1259 (brute-force checked).
- **Fills:**
  - The cancel is processed before the spread query; no overfill.
  - No decision has more attributed fills than it sent, and no fill timestamp equals a decision time.
  - Every run filled 4,000/4,000.
- **TCA:** the IS = drift + own impact + instant identity holds to within 1.2e-5 bps. SELL and BUY signs and units are consistent, and position changes across agent types net to zero.
- **`summarize.py`:** runs are paired by seed through a pivot; the bootstrap is standard.
- **Leakage:** calibration seeds 0–39 are disjoint from test seeds 1000+. Policies see only their own past fills and the current book.
