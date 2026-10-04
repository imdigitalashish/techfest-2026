# Review — ADR 001 (spike choice) — rubber-duck agent, harness-default model — 2026-10-04 09:30 IST

Reviewer: `rubber-duck` sub-agent (`rd-adr001`), model not overridden (harness default), effort default. Verdict: "Reopen ADR 001."
Decision legend: ACCEPTED = changed or scheduled; REJECTED = kept as-is, with the reason.

| # | Issue (summary) | Severity | Decision | Action / reason |
|---|---|---|---|---|
| 1 | Spikes A and B both serve "search & path" (20% of finals); reconstruction, viewer and capture are 60%; R1 criteria aren't served | blocking | **ACCEPTED** | ADR 001 v2 re-scores with judge weights (pending the gpt-6-astra second opinion) |
| 2 | Spike A misses its own SLO (recall ≥0.95 at ≤10% collisions) | blocking | **ACCEPTED** | Stated in the selection memo and abstract; the SLO stays as the target |
| 3 | J = recall − collision has a −1 cliff and asymmetric weights | blocking | **ACCEPTED** | v2 primary score CFC@0.25 (continuous; refusing a route = colliding) — `eval/nav_eval_v2.py` |
| 4 | `traj_override` erased obstacle evidence | blocking | **ACCEPTED** | Already fixed: ratchet #1 kept `traj_override=False` (now the default in `walkable.py`) |
| 5 | Held-out recall leaks through adjacent frames; camera ≠ body position | high | **ACCEPTED** | v2: ±2-frame buffer around held-out frames; first/last 0.30 m excluded; snap ≤0.25 m |
| 6 | Dense 3DGS proxy is not a safety oracle (15.2% proxy hits at cameras) | high | **ACCEPTED (partly)** | v2 reports the proxy noise floor; real-geometry scene (ARKitScenes/ScanNet++) scheduled. The proxy is kept as a relative signal only |
| 7 | Snapping up to 1 m inflated success; connectors unchecked | high | **ACCEPTED** | v2: snap ≤0.25 m, connectors densified and checked |
| 8 | Harness used shipped poses / existing PLY, not E2E | high | **ACCEPTED** | One-command pipeline (`components/orchestrator/run_pipeline.py`) now runs from raw photos with our own SfM |
| 9 | Competitor would use ARKit/LiDAR/RoomPlan + Recast + human correction + reticle POI capture | medium | **ACCEPTED (partly)** | LiDAR/ARKit path added to the backlog for LiDAR phones; Recast-on-mesh kept as the comparison arm; viewer already has manual POI tagging. REJECTED as the *default*: the user's phone may lack LiDAR, and the brief says "only a smartphone" |
| 10 | Demote B; prioritise capture→URL reliability and viewer/reconstruction quality | — | **ACCEPTED (pending second opinion)** | See ADR 001 v2 |
