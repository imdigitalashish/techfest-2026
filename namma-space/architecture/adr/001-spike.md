# ADR 001 (v2) — Spike components: D′ quality-qualified capture→twin turnaround, E fidelity-constrained first-person delivery

- **Status:** Accepted v2 — 4 Oct 2026, 10:30 IST. Supersedes v1 (08:10 IST; spikes A "walkable space from capture evidence" and B "capture-time semantic tagging"; v1 is in git history).
- **Why revised:**
  - two independent reviews: [`reviews/2026-10-04-adr001-rubber-duck-default.md`](../../reviews/2026-10-04-adr001-rubber-duck-default.md) and [`reviews/2026-10-04-adr001-gpt-6-astra.md`](../../reviews/2026-10-04-adr001-gpt-6-astra.md);
  - our own leak-free re-evaluations (`eval/results/drjohnson_nav_v2.json`, `drjohnson_nav_v3.json`) show v1's evidence for spike A came mostly from hold-out leakage.

## Context (what is scored)
- **Finals:** the only published weights — capture 20 · reconstruction 20 · viewer/UX 20 · search & path 20 · pitch 20 · AR +10 bonus.
- **R1 (31 Oct):** SOP & pipeline · visual fidelity · viewer performance · docs/video. **R2 (30 Nov; our target 17 Nov):** POIs · path accuracy · search UI · code. No percentages are published for R1/R2.
- **Urgency weighting** (gpt-6-astra, an explicit planning assumption): R1 ≈ 50%, R2 ≈ 31%, finals ≈ 19% of near-term attention. R1 is a qualification gate: later points can't compensate for missing it.

## Evidence that changed the decision
1. **Spike A has no demonstrated advantage without leakage.**
   - v2 (±2-frame buffered hold-out, 40 pairs): CFC@0.25 = 0.600–0.650 for all four evidence variants. Wilson 95% for 24/40 is 0.446–0.737, so they are indistinguishable.
   - v3 (all 406/435 pairs, frozen reference): CFC = 0.45–0.50 for every variant, with 0% refusals and ~50% of routes passing within 0.275 m of dense geometry. The sparse-point map misses thin obstacles.
   - The v1 gain (recall 0.788 → 0.970) came from adjacent-frame leakage.
2. **Reviewers' re-scoring** (urgency-weighted, subjective; gpt-6-astra): viewer streaming/LOD 16.0 > reconstruction speed/quality 12.9 > walkable space 10.6 > feed-forward posing 10.4 > semantic tagging 8.0 > AR ≤1.9.
3. **Measured weak spots:**
   - Walking p95 frame time is 104.7 ms vs a 20 ms budget; splats take 10.5 s to load even on localhost.
   - SfM + training take ≈43 min for 263 photos on the M5 (own SfM 6.0 min + Brush ≈37 min).
   - SOP timing is unmeasured until the user's capture.

## Decision
**Spike 1 — D′: quality-qualified capture→twin turnaround** (serves R1 SOP/pipeline + fidelity, finals capture + reconstruction = 40%).
- **Scalar:** S_T = mean over trials of 𝟙[accepted] · max(0, 1 − T / 90 min). T = elapsed minutes from the start of capture to a deployed URL, including retries and human steps.
- **Acceptance:** all required rooms and doorways present; scale error ≤3% (marker); held-out PSNR ≥ a threshold frozen after the first home capture. A failed trial scores 0.
- **Innovation room** (verified leads in [`research/sota-reconstruction.md`](../../research/sota-reconstruction.md)):
  - per-clip streaming (process while still capturing);
  - on-site QA that says which room to re-shoot before you leave;
  - frame selection;
  - Brush built from `main` (unreleased Mip-Splatting, 4× memory cut, +10–15% speed);
  - MapAnything (Apache-2.0, metric) as a drop-in posing seam once MPS support is checked.

**Spike 2 — E: fidelity-constrained first-person delivery** (serves R1 viewer performance, finals viewer/UX 20%).
- **Scalar:** S_V = max(T_visible / 5 s, F95 / 20 ms) on frozen walkthrough traces over a fixed network profile, cold cache, on a reference laptop. Lower is better; an empty first frame doesn't count.
- **Constraints:** ≤1 dB held-out PSNR loss vs the unpruned model, and fixed view coverage.
- **Innovation room:** importance pruning + SPZ/SOG compression, progressive/LOD loading (Spark 2.x reads PLY/SPZ/SPLAT/KSPLAT/SOG), a sort budget, and NavGrid-aware camera smoothing.

**Best-practice baselines (not spikes) for R2:**
- **Walkable space:** NavGrid → A* scored with eval v3 against a real-geometry scene (ARKitScenes mesh + 3D boxes).
- **Next baseline candidate:** obstacles from the dense splats (fixes the thin-obstacle misses; can't be judged on the splat proxy because that would be circular).
- **Comparison arm:** a mesh from the splats (e.g. MeshSplatting, Apache-2.0) → Recast navmesh (recast-navigation-js, MIT).
- **POIs:** frames / voice tags → ray-cast placement + 1-click confirm. **Search:** lexical + aliases.

A and B may return as spikes after R1 if their metrics show headroom.

## Six Thinking Hats (summary)
- **White:** see Evidence. D′ and E both have frozen, measurable scalars; A and B currently show no measured gain.
- **Red:** judges first see the walkthrough. A twin that stutters or takes hours to build loses before paths matter.
- **Black:**
  - D′ depends on the user's capture (phone unknown) and on the shared M5's load.
  - E's optimisation can trade away fidelity, so the PSNR constraint is mandatory.
  - Both are "engineering" more than "novel"; novelty earns no separate points, but the pitch needs a story → the on-site QA loop and "link in under 90 min" are the story.
- **Yellow:** both move R1 qualification and 40–60% of finals points; both make a strong live demo.
- **Green:** feed-forward posing + short refinement; per-room parallel training; streaming LOD; on-device AR later.
- **Blue:** freeze `eval.py` per spike before any ratchet; keep only gains beyond noise on two traces/captures; re-check on an untouched capture.

## Thesis → antithesis → synthesis
- **Thesis (v1):** the innovation lives in navigation (A) and semantics (B), because they are the brief's distinctive asks.
- **Antithesis (two independent reviews + v2/v3 data):**
  - v1's metric was leaky and gameable;
  - A's gain disappears without leakage;
  - R1 is judged on reconstruction and viewer;
  - novelty earns no separate points.
- **Synthesis:** spike where points and risk concentrate now (D′, E). Run navigation and POIs as honestly measured baselines with a real-geometry benchmark, and re-open them as spikes after R1.

## Consequences
- New `autoresearch/` folders: `components/orchestrator/autoresearch/` (S_T) and `components/web_viewer/autoresearch/` (S_V; Playwright traces).
- `components/walkable_space/autoresearch/` stays as a baseline tuner, on eval v3 only.
- Needs from user: one timed rehearsal capture (SOP stopwatch) to set T and the PSNR threshold.
