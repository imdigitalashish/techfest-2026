# walkable-space ratchet — program

**Goal:** maximise `J = recall_nav − path_collision_rate` on drjohnson split A (held-out every 8th image), confirmed on split B (offset 4), with path success = 1.0.
- `recall_nav`: share of held-out camera floor positions inside the navigable map. People stood there, so those positions must be walkable.
- `path_collision_rate`: share of 40 fixed held-out start→goal paths passing within 15 cm of the dense 3DGS proxy (not ground truth).

**Frozen:** `eval.py`, the splits, the dense-proxy definition, agent radius 0.25 m, agent height 1.70 m, step height 0.15 m, 5 cm cells. **Editable:** `params.json` and `components/walkable_space/walkable.py`; the contract (`NavGrid`) must not change.

**Keep rule:** ΔJ_A ≥ 0.03 (≈ one held-out position or one pair) **and** ΔJ_B ≥ 0. Otherwise revert. Every trial goes to `results.tsv`.

**Watch for gaming:** an empty or tiny navigable map has collision 0 but recall ≈ 0 (J ≤ 0); success < 1 forces J = −1; `proxy_hits_at_heldout_cams` should stay ≈ 0 (if the proxy flags camera positions, the proxy is noisy, not the map). Re-check on a second scene with real geometry before claiming a general win.

**Backlog (initial, in `loop.py`):** trajectory as connectivity only · carve_beta 2/8 · traj_radius 0.20 · obstacle inflation 5 cm · single-point obstacles · smaller closing · wider floor dilation.
**Next ideas:** use dense depth rendered from the splats for carving; per-cell confidence instead of binary; a route-pass lane label from the SOP; a Recast-on-mesh comparison arm.

Run: `cd namma-space && .venv/bin/python components/walkable_space/autoresearch/loop.py`
