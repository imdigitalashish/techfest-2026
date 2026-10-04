# Namma Space — Technical Abstract (Round 1)
**Phone capture → navigable, photoreal 3D web twin** · Techfest 2026 × Juspay · DRAFT v0.9 (4 Oct 2026)

> Every number in this document comes from a committed run with a reproduce command (repository `namma-space/`). **[public]** = Deep Blending *drjohnson* (a multi-room house, 263 photos; non-commercial research licence; used for evaluation only). **[home]** = our own capture, added after recording. ⟨…⟩ = value pending from the run in progress.

## 1. Goal
One phone video of an indoor space should become, automatically and with no 3D modelling, a link that anyone can open to:
- walk through the space in first person (WASD + mouse);
- click and search points of interest;
- follow a walking path that stays on the floor and avoids walls and furniture.

Round 1 asks for capture → reconstruction → free-roam viewer. We built the full chain end-to-end from day one, because the same geometry drives collisions in the viewer and paths in Round 2.

## 2. Architecture
Fourteen components with typed contracts (`architecture/contracts/contracts.ts`), each with its own scalar metric, so any one can be replaced or auto-tuned in isolation:

`capture SOP → ingest → posing (SfM) → 3D Gaussian Splatting → scene alignment → walkable space → path planner → POIs + search → scene packager → web viewer (→ AR, finals bonus)`

- **One frame for everything:** splats, walkable map, POIs and (later) AR live in a gravity-aligned frame with the floor at y = 0 and metric scale.
- **One command:** `./process_capture.sh <capture_folder> <name>` runs all stages, times each, caches results so re-runs resume, and writes `report.json` plus a static site ready to serve or deploy.
- **Laptop-first:** the whole Round-1 pipeline runs on an Apple M5 laptop (Metal GPU). Cloud GPUs are an accelerator, not a dependency.

## 3. Capture SOP (`deliverables/capture-sop.md`)
- **Settings:** 4K30 video, HDR off, 1× lens only, exposure and focus locked, landscape.
- **Per room, three passes:** an inward loop; an outward loop tilted 20–40° down (floor edges and furniture legs for navigation); and a "route pass" along real walking routes.
- **Doorways:** crossed at half speed, pausing 1 s on each side. This is where reconstructions split, so overlap is critical.
- **Scale:** a printed 150 mm ArUco marker on the floor, filmed at the start and end. It is triangulated from the posed frames to give metric scale (unit test: <1% scale error on synthetic views). Fallback: the measured camera height.
- **Voice tags:** say each room or item name on entry. The timestamp → frame → ray gives a POI without manual 3D work.
- **Before leaving:** a 3-minute checklist (sharpness spot-check, both loops, marker at start and end).
- **Large venues (finals):** a two-person crew; capture the corridor "spine" first, then each room as a clip that starts and ends in the corridor; upload while capturing the next clip.
- Every rule maps to a failure mode of SfM, splatting or navigation (SOP §10).

## 4. Reconstruction pipeline
| Stage | Method | **[public]** result (own pipeline, raw photos) |
|---|---|---|
| Ingest | ffmpeg keyframes at 4 fps → sharpest of every 2 (variance of Laplacian) → drop frames below 0.3× clip median sharpness | 263 frames, 9.9 s |
| Posing | COLMAP 4.2 via pycolmap: SIFT (CPU), sequential matching (overlap 20, quadratic), **global SfM** (the GLOMAP mapper, now in COLMAP), undistortion | **262/263 registered (99.6%)**, 0.661 px mean reprojection error, 12,316 points, 6.0 min |
| 3D Gaussian Splatting | Brush v0.3.0 on Apple Metal, 15k steps, ≤2M splats; held-out every 8th image | ⟨PSNR / SSIM⟩ held-out, ⟨train min⟩, ⟨peak GB⟩ |
| Alignment | camera-up mean → floor = lowest dense height peak, refined by a plane fit → scale from ArUco marker / camera height → yaw from principal axes | ⟨floor inliers, tilt⟩ (scale ASSUMED on [public]: no marker) |
| Walkable space | sparse points in the body band 0.15–1.70 m = obstacles; observation rays carve free space; walked trajectory adds connectivity; eroded by 0.25 m agent radius | ⟨navigable m²⟩, ⟨camera positions on navigable⟩ |
| Packaging | importance pruning (opacity × area) to ≤1M splats → aligned `.splat` (32 B/splat) + manifest + NavGrid + POIs | ⟨MB⟩ |

Pose accuracy on [public] vs the dataset's reference reconstruction (Sim(3)-aligned camera centres): ⟨ATE⟩.

## 5. Web viewer (zero install)
A static page: three.js + Spark (MIT) Gaussian-splat renderer, loaded from CDNs.
- **Movement:** PointerLock WASD + mouse-look at a 1.6 m eye height, with smoothed acceleration. Every step is checked against the walkable map and slides along walls, so you can't walk through walls or furniture.
- **Minimap:** click it to route anywhere.
- **POIs:** labels; search by name or alias (e.g. "fireplace", "bookcase"), which plans a route and can auto-walk it.
- **Tagging:** press `P` to tag a POI where you stand.

**[public]**, Chrome on Apple M5 (shared machine), 1.0M splats:

| Condition | Median fps | p95 frame time | Notes |
|---|---|---|---|
| Static view | 45 | 36.7 ms | first frame 1.05 s, all splats loaded 10.5 s (localhost) |
| Walking | 42 | 104.7 ms | hitching: the main optimisation target (§7) |

Frozen protocol for the next measurement: cold cache, throttled network, scripted walk — ⟨S_V⟩. **[home]:** public URL and the same measurements.

## 6. Navigation and search (Round-2 preview, measured honestly)
- **Planner:** 8-connected A* with a clearance penalty, then line-of-sight string pulling. Contract test: the route must use the doorway and never touch the wall. An identical JavaScript port runs in the browser: an 8–11 m route in 82–94 ms.
- **POIs:** labelled from evidence frames, placed by casting a ray from the chosen pixel into the reconstruction, with an approach point snapped onto the walkable map. 7 POIs on [public].
- **Path-safety evaluation v3** (`eval/nav_eval_v3.py`), built after two independent reviews caught leakage in our first metric:
  - endpoints are held-out camera positions, moved to verified-free cells;
  - **every** pair is tested (406 / 435 per split);
  - the whole route is checked against a frozen dense-geometry reference (3DGS splats) with a 0.25 m body radius;
  - Wilson 95% intervals and paired sign tests.
- **Result:** 45–50% of routes are fully collision-free under this strict reference (Wilson ±5%). There are no refusals: every pair gets a route. Adding free-space carving or the walked trajectory does **not** change this (paired p ≥ 0.06). The sparse SfM points miss thin obstacles such as chair legs.
- **Round-2 plan:** obstacles from the dense splats, a mesh → Recast navmesh comparison arm, and a real-geometry benchmark (ARKitScenes laser-scanned meshes) so the reference is independent of our own reconstruction.

## 7. Where we innovate (ADR 001 v2)
After two independent reviews (including GPT-6 Astra as a hostile methodologist), we put the innovation where the marks are:
- **D′ — quality-qualified turnaround:** maximise 𝟙[accepted] · (1 − T/90 min). T counts capture → deployed link, including retries; a twin is accepted only if every room is present, scale error is ≤3% and held-out PSNR meets a frozen threshold. Levers: on-site QA that says which room to re-shoot before you leave, per-clip streaming, frame selection, faster training.
- **E — fidelity-constrained delivery:** minimise max(T_visible / 5 s, p95 frame time / 20 ms) on a frozen cold-cache walkthrough, with ≤1 dB PSNR loss. Levers: importance pruning, SPZ compression, progressive loading, render budget.

Both run as auto-research "ratchets": an agent edits the component, a frozen evaluator scores it, and only gains beyond noise are kept.

## 8. State of the art and positioning (verified 4 Oct 2026; details in `research/`)
- **Posing:** global SfM is now part of COLMAP — the standalone GLOMAP repo is marked deprecated, and pycolmap 4.2 exposes `global_mapping`. Feed-forward models such as MapAnything (Apache-2.0, metric) and VGGT-Ω (non-commercial) are the speed frontier. They sit behind our posing contract as drop-in candidates once Apple-silicon support is verified.
- **Splatting:** Brush (Apache-2.0) trains on Apple Metal; its unreleased main branch adds Mip-Splatting and a 4× memory reduction.
- **Viewers:** Spark (MIT, three.js) reads PLY/SPZ/SPLAT/KSPLAT/SOG.
- **Navigation in splat twins:** Splat-Nav (robot planning in Gaussian-splat maps), Habitat-GS (ECCV 2026) and MeshSplatting (meshes with walkable scenes) are the closest research.
- **Products:** ⟨summary from `research/companies.md`⟩.
- **Our gap:** phone video → photoreal twin → walkable map + search + routing (+ AR) in one zero-install link, produced in under an hour.

## 9. Evaluation discipline
- Fixed seeds and splits (every 8th frame held out, buffered).
- Committed result files, and one command per number.
- Contract tests per component.
- Every headline claim reviewed by an independent model before submission (`reviews/ledger.tsv`).

## 10. Credits and licences
COLMAP / pycolmap (BSD) · Brush (Apache-2.0) · three.js (MIT) · Spark (MIT) · NumPy / SciPy (BSD) · OpenCV incl. ArUco (Apache-2.0) · ffmpeg (LGPL/GPL, CLI) · Deep Blending dataset (Hedman et al. 2018; non-commercial research use, evaluation only, not hosted).
