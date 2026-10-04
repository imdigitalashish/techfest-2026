# Spike E — fidelity-constrained first-person delivery (ratchet program)

**Goal:** minimise S_V = max(T_visible / 5 s, F95 / 20 ms) (`measure_viewer.mjs`, FROZEN), subject to:
- held-out PSNR loss ≤1 dB vs the unpruned splat (computed on the packaged splat with the same eval split);
- view coverage unchanged (same walkthrough trace).

**Protocol (frozen):** installed Chrome via playwright-core, fresh context (cold cache), 1280×800 at DPR 1, throttled 40/10 Mbit/s with 40 ms RTT, a scripted walk (route to the farthest navigable cell, 8 s auto-walk). Median of 3 runs. The machine state (other jobs) is recorded with each run.

**Editable:** `components/scene_packager/package.py` (pruning, compression, format), `components/web_viewer/*.js` (render budget, pixel ratio, sort cadence, progressive loading). The `ScenePackage` contract must not change.

**Keep rule:** S_V improves by more than 5% on the median of 3 runs **and** the PSNR constraint holds. Every trial goes to `results.tsv`.

**Backlog:** splat budget 1.0M → 0.75M / 0.5M (importance pruning) · SPZ instead of .splat (≈10× smaller per the nianticlabs/spz README) · progressive load (coarse subset first) · pixel ratio 1.0 while moving · SH degree 0 vs 3 · Spark LOD/paging options (verify in the docs first).

Run: `node components/web_viewer/autoresearch/measure_viewer.mjs http://127.0.0.1:8080/ results/run.json`
