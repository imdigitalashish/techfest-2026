# ADR 001 — Spike components: (A) walkable space from capture evidence, (B) capture-time semantic tagging

- **Status:** Accepted v1 (4 Oct 2026, 08:10 IST). Independent adversarial review (`rubber-duck` / First Principles agent) is **pending**: Supervisor Lean Mode banned sub-agents until 08:30, so the antithesis below was written by the lead.
- **Context:** the judging rewards (R1) SOP and pipeline soundness, visual fidelity and viewer performance; (R2) POI tagging, pathfinding accuracy, search UI; (finals) capture execution, reconstruction, viewer UX, search + "non-colliding pathing around physical obstacles" (20% each) and AR (+10%), all under a Day-1 time limit. Evidence so far: components 3–7 run end-to-end on Deep Blending *drjohnson* (`eval/results/`).

## Candidates and scores (1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasibility by deadline | Measurability (scalar) | Demoability | Total |
|---|---|---|---|---|---|---|
| **A · walkable-space evidence fusion** (sparse points + free-space ray carving + walked trajectory → NavGrid) | 5 — pathfinding accuracy is scored in R2 and finals | 4 — trajectory-as-free-space evidence is not standard in splat products (UNVERIFIED: market check pending) | 5 — CPU-only; v0 already runs (grid 0.2–39 s) | 5 — held-out trajectory recall at a fixed dense-collision rate | 4 | **23** |
| **B · capture-time semantic tagging** (voice tags + door-sign OCR + open-vocab detection → POIs) | 4 — POI accuracy + Day-1 annotation time | 4 — names come from language captured live, not from pixels | 4 — ASR/OCR are mature (model choice UNVERIFIED tonight) | 4 — POI precision/recall within 1 m of reference labels | 5 — say "Meeting Room 4", it appears in search | **21** |
| C · feed-forward posing (VGGT/MapAnything class) for turnaround | 4 | 2 — everyone can adopt it | 3 — weights licence + MPS memory UNVERIFIED | 5 | 2 | 16 |
| D · splat-training speed/quality on Apple silicon | 4 | 2 | 3 — no CUDA tonight | 5 | 3 | 17 |
| E · viewer streaming/LOD | 3 | 2 — Spark/PlayCanvas already strong (UNVERIFIED versions) | 4 | 5 | 3 | 17 |
| F · AR relocalisation against the twin | 3 (bonus) | 3 | 2 — iOS WebXR status UNVERIFIED | 4 | 5 | 17 |

**Decision:** spikes **A** and **B**. C, D and E use the best existing practice and are re-evaluated when better tools are verified. F is a bonus track that starts after Round 2 (17 Nov).

## Six Thinking Hats — A (walkable space)
- **White (facts):** on *drjohnson* (run 1, 07:43 IST), held-out camera positions inside the navigable map went 0.788 (points only) → 0.879 (+carving) → 0.939 (+trajectory) → 0.970 (full). In the same run, paths within 15 cm of the dense 3DGS proxy rose from 17.5% to 32.5–35% when the trajectory was used. That proxy kept only 3,244 splats, so run 2 (opacity > 0.1) re-measures it.
- **Red (gut, judges):** a path through a wall or a sofa loses the room instantly; a path that hugs the sofa feels "real".
- **Black (risks):** the trajectory prior over-opens space beside furniture; scale is ASSUMED without a marker (agent radius in the wrong units); glass, mirrors and unobserved floor; the eval proxy comes from the same photos (no ground truth on drjohnson).
- **Yellow (benefits):** free evidence, CPU-only, seconds; one NavGrid drives viewer collisions, desktop paths and AR guidance; a clean scalar to ratchet on.
- **Green (alternatives):** carving with dense depth rendered from the splats; an explicit "route pass" lane label from the SOP; a Recast navmesh on a 2DGS/TSDF mesh; LiDAR/RoomPlan when available; per-scene threshold learning.
- **Blue (process):** freeze `eval.py`; ratchet on J = held-out recall − λ·collision rate over fixed held-out pairs; confirm every kept change on a second scene with real geometry (ARKitScenes / ScanNet++ — see `research/datasets.md`).

## Six Thinking Hats — B (capture-time semantic tagging)
- **White:** the brief's queries are names ("Meeting Room 4") and categories ("3-seater sofas"). The SOP already asks for spoken tags and 2 s door-sign shots.
- **Red:** saying "Fridge" and later finding it by search is a memorable demo; judges see a real Day-1 time saving.
- **Black:** ASR errors on Indian names and accents and in noisy venues; the voice tag marks the *camera* position, not the object; judges may call it "manual annotation in disguise"; audio privacy.
- **Yellow:** about 1 s per POI at capture time vs minutes of clicking in 3D afterwards; works for names no detector can know.
- **Green:** OCR on door signs; open-vocabulary detectors for items; a VLM to name rooms; viewer confirm/rename UI; multilingual tags.
- **Blue:** metric = POI precision/recall (correct label within 1 m of hand-labelled references) on our own captures; report time-to-annotate vs manual tagging.

## Thesis → antithesis → synthesis
**A. Thesis.** A* is optimal on its graph, so all path errors are map errors. Capture already contains free-space evidence: every observation ray crossed empty space, and the person physically walked the route.
**Antithesis (lead acting as adversary).** (1) Map quality is invisible; judges see paths, so polish may matter more. (2) The trajectory is a biased prior: run 1 roughly doubled near-collisions. (3) A proxy built from the same photos cannot catch systematic errors such as glass. (4) Recast on a mesh is the industry-standard navmesh and may simply win.
**Synthesis.** Keep A, scored honestly: (i) recall at a fixed collision budget (Pareto), never recall alone; (ii) use the trajectory for *connectivity* (free floor exists) while clearance comes from obstacles only; (iii) add a scene with real ground-truth geometry before claiming wins; (iv) keep Recast-on-mesh as the comparison arm in the eval.

**B. Thesis.** Names live in language (people, signs), not pixels, so capture language at capture time and get the anchor pose from the timestamp for free.
**Antithesis.** ASR and OCR fail in the field; camera position ≠ object position; "voice tags" could be judged manual.
**Synthesis.** Fuse three sources (voice, OCR, detector) into one POI list with confidences. Anchor = the ray from the frame centre into the reconstructed geometry, not the camera. Always offer a 1-click confirm/rename in the viewer, and measure precision/recall and time saved.

## First principles (lead)
- Pathfinding accuracy is bounded by the free-space map, not by the search algorithm.
- POI naming is bounded by where the information exists: in language (signage, people), which images alone only partly contain.
- Day-1 turnaround is bounded by the slowest serial stage (posing + training ≈ 40 min on the M5 tonight), so stages must overlap: upload and process per clip while capture continues.

## Consequences
- `components/walkable_space/` gets `autoresearch/` (program.md, frozen eval.py, results.tsv) first; `poi_extraction/` follows once the user's capture (with voice tags) exists.
- Everything else is chosen by verified best practice. Re-open this ADR if a verified product or paper already ships trajectory-evidence navmeshes or voice-tagged capture.
