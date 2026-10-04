# Namma Space — Technical Abstract (Round 1)
**Phone capture → navigable, photoreal 3D web twin** · Techfest 2026 × Juspay · DRAFT v0.9 (4 Oct 2026)

> Every measured number cites a committed result file. **[public]** = Deep Blending *drjohnson* (a multi-room house, 263 photos; non-commercial research licence; used for evaluation only). **[home]** = our own capture: values are added after recording. The pipeline is implemented end-to-end; validation on our own home is pending.

## 1. Goal
One phone video of an indoor space should become, automatically and with no 3D modelling, a link that anyone can open to:
- walk through the space in first person (WASD + mouse);
- click and search points of interest;
- follow a walking path that stays on the floor and avoids walls and furniture.

**Links a judge gets:**
1. **Primary:** our own home, captured with our SOP (required by the brief).
2. **If the home twin fails our quality gate:** another space we capture ourselves (hostel room, lab), never a dataset.
3. **Extra, clearly labelled "public dataset — not our capture":** a viewer demo built from a CC BY-SA 4.0 walkthrough video of a public library (`test_data/public_demo/SOURCE.md`).

Round 1 asks for capture → reconstruction → free-roam viewer. We implemented the full chain from day one, because the same geometry drives collisions in the viewer and paths in Round 2.

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
- **Voice tags (planned for R2):** say each room or item name on entry. The timestamp → frame → ray will give a POI without manual 3D work. Today, POIs come from labelled frames or in-viewer tagging.
- **Before leaving:** a 3-minute checklist (sharpness spot-check, both loops, marker at start and end).
- **Large venues (finals):** a two-person crew; capture the corridor "spine" first, then each room as a clip that starts and ends in the corridor; upload while capturing the next clip.
- Every rule maps to a failure mode of SfM, splatting or navigation (SOP §10).

## 4. Reconstruction pipeline
Total processing on [public], from raw photos to a deployable site: **45.8 min** on an Apple M5 laptop. Breakdown: ingest 0.2 · posing 12.3 · training 33.1 · alignment, walkable, package, site and evaluation 0.2 min. Reproduce: `./process_capture.sh .data/deepblending/drjohnson/images drjohnson_e2e --reference-colmap .data/deepblending/drjohnson/sparse/0`.

| Stage | Method | **[public]** result (own pipeline, raw photos) |
|---|---|---|
| Ingest | ffmpeg keyframes at 4 fps → sharpest of every 2 (variance of Laplacian) → drop frames below 0.3× clip median sharpness | 263 frames, 9.9 s |
| Posing | COLMAP 4.2 via pycolmap: SIFT (CPU); **exhaustive** matching for photo sets, sequential for video; **global SfM** (the GLOMAP mapper, now in COLMAP) with an incremental fallback; undistortion; a **pose-sanity gate** | **263/263 registered**, 0.91 px. Trajectory error vs the dataset's reference poses: **0.07% of scene size** (RMSE 0.0072 reference units). 12.3 min (matching 10.8 min). *Lesson:* our first run used sequential matching on this unordered photo set. It reported 99.6% registered at 0.66 px, but was degenerate: 30 cameras up to 2 km away, error 34% of scene size, held-out PSNR 18.3 dB. Registration rate and reprojection error don't reveal this, so the pipeline now gates on camera-spread sanity (and on trajectory error when reference poses exist) |
| 3D Gaussian Splatting | Brush v0.3.0 on Apple Metal, 15k steps, ≤2M splats; held-out every 8th image | **29.56 dB PSNR / 0.929 SSIM** on 33 held-out views (every 8th photo); 33.1 min; 6.94 GB peak; 2M splats |
| Alignment | camera-up mean → floor = lowest dense height peak, refined by a plane fit → scale from ArUco marker / camera height → yaw from principal axes | 61% of points on the floor plane; plane fit refines camera-up by 2.9°; camera heights p10–p90 0.73–1.83 m (scale ASSUMED on [public]: no marker) |
| Walkable space | sparse points in the body band 0.15–1.70 m = obstacles; observation rays carve free space; walked trajectory adds connectivity; eroded by 0.25 m agent radius | 28.7 m² navigable; 95% of camera positions fall on it |
| Packaging | importance pruning (opacity × area) to ≤1M splats → aligned `.splat` (32 B/splat) + manifest + NavGrid + POIs | 1.0M of 2.0M splats → 32 MB |

Pose accuracy on [public] vs the dataset's reference reconstruction (Sim(3)-aligned camera centres): RMSE 0.0072 reference units = **0.07% of the scene extent** (`eval/results/drjohnson_e2e_report.json`).

## 5. Web viewer (zero install)
A static page: three.js + Spark (MIT) Gaussian-splat renderer, loaded from CDNs.
- **Movement:** PointerLock WASD + mouse-look at a 1.6 m eye height, with smoothed acceleration. Movement is constrained to the walkable map: sub-stepped, sliding along walls. How complete that map's obstacles are is limited (§6).
- **Minimap:** click it to route anywhere.
- **POIs:** labels; search by name or alias (e.g. "fireplace", "bookcase"), which plans a route and can auto-walk it.
- **Tagging:** press `P` to tag a POI where you stand.

**[public]**, frozen protocol (`eval/results/viewer_bench_drjohnson_e2e.json`): Chrome on the Apple M5, cold cache, 1280×800, network throttled to 40 Mbit/s, scripted walk; median of 3 runs; 1.0M splats (32 MB):

| Condition | Median fps | p95 frame time | Notes |
|---|---|---|---|
| Static view | 60 (vsync) | 17.5 ms | first frame 0.86 s |
| Walking | 60 | **22.4 ms** | camera stayed on the walkable map |
| Load | – | – | all splats visible after **7.45 s** (32 MB at 40 Mbit/s ≈ 6.4 s of transfer alone) |

Score S_V = max(T_visible / 5 s, p95 / 20 ms) = **1.49** (1.0 = on budget). Loading is the binding constraint, so compression and progressive loading come first (spike E). An earlier ad-hoc measurement under heavy machine load showed 104.7 ms walking p95; it isn't comparable. **[home]:** the same protocol over the public URL.

## 6. Navigation and search (Round-2 preview, measured honestly)
- **Planner:** 8-connected A* with a clearance penalty, then line-of-sight string pulling. Contract test: the route must use the doorway and never touch the wall. A JavaScript port of the same algorithm runs in the browser (8–11 m route in 82–94 ms); its clearance field is approximated, and cross-language equivalence tests are pending.
- **POIs:** 7 POI label specs on [public], each tied to an evidence frame, placed by casting a ray from the chosen pixel into the reconstruction, with an approach point snapped onto the walkable map.
- **Path-safety evaluation v3** (`eval/nav_eval_v3.py`), built after two independent reviews caught leakage in our first metric:
  - endpoints are held-out camera positions moved (≤0.5 m) to verified-free cells; 29/33 and 30/33 cameras qualify;
  - **all pairs among those endpoints** are tested;
  - the whole route, including connectors, is checked against a frozen dense-geometry reference (3DGS splats) at a 0.25 m body radius plus a quantisation margin;
  - uncertainty comes from a camera-level bootstrap (pairs share endpoints, so pair-level intervals are too narrow).
- **Result** (shipped-pose [public] benchmark, `eval/results/drjohnson_nav_v3.json`): **44–49%** of routes are fully collision-free under this strict reference (camera-bootstrap 95% CI ≈30–69%), for every map variant. Every eligible pair gets a route. Adding free-space carving or the walked trajectory shows **no evidence of a difference** — which is not proof of equivalence. The disagreement is consistent with missing thin-obstacle geometry, such as chair legs, in the sparse SfM points.
- **Limitation:** SfM uses all images. Splat training holds out every 8th image for appearance metrics; the navigation hold-out also removes ±2 neighbouring frames from map building. The reference comes from the same photos, so this is a same-scene consistency check, not ground truth.
- **Round-2 plan:**
  - obstacles from the dense splats (PlayCanvas `splat-transform`'s collision pipeline, MIT), with a mesh → Recast navmesh comparison arm;
  - an independent real-geometry benchmark (ARKitScenes laser-scanned meshes);
  - automatic POIs from voice tags, detection (SAM 3 / YOLOE) and VLM naming, replacing today's manual frame tagging.

## 7. Where we innovate (ADR 001 v2)
After two independent reviews (including GPT-6 Astra as a hostile methodologist), we put the innovation where the marks are:
- **D′ — quality-qualified turnaround:** maximise the mean over trials of 𝟙[accepted] · max(0, 1 − T/90 min). T counts capture → deployed link, including retries; a twin is accepted only if every room is present, scale error is ≤3% and held-out PSNR meets a frozen threshold. Levers: on-site QA that says which room to re-shoot before you leave, per-clip streaming, frame selection, faster training.
- **E — fidelity-constrained delivery:** minimise max(T_visible / 5 s, p95 frame time / 20 ms) on a frozen cold-cache walkthrough, with ≤1 dB PSNR loss. Levers: importance pruning, SPZ compression, progressive loading, render budget.

Both run as auto-research "ratchets": an agent edits the component, a frozen evaluator scores it, and only gains beyond noise are kept.

## 8. State of the art and positioning (verified 4 Oct 2026; details in `research/`)
- **Posing:** global SfM is now part of COLMAP — the standalone GLOMAP repo is marked deprecated, and pycolmap 4.2 exposes `global_mapping`. Feed-forward models such as MapAnything (Apache-2.0, metric) and VGGT-Ω (non-commercial) are the speed frontier. They sit behind our posing contract as drop-in candidates once Apple-silicon support is verified.
- **Splatting:** Brush (Apache-2.0) trains on Apple Metal; its unreleased main branch adds Mip-Splatting and a 4× pixel-buffer memory reduction.
- **Viewers:** Spark (MIT, three.js) reads PLY/SPZ/SPLAT/KSPLAT/SOG.
- **Navigation in splat twins:** Splat-Nav (robot planning in Gaussian-splat maps), Habitat-GS (ECCV 2026) and MeshSplatting (meshes with walkable scenes) are the closest research.
- **Products:** across ≈59 vendor pages we found **no product** that ships phone capture → photoreal twin → walkable map → search → obstacle-aware route in one zero-install link. Capture vendors stop at viewing, measuring and floor plans; wayfinding vendors route over 2D floor-plan maps (`research/companies.md`). This is evidence of absence in what we checked, not proof that none exists.
- **Our target:** that whole chain in one link, produced in under 90 minutes from capture (spike D′).

## 9. Evaluation discipline
- Fixed seeds and splits (every 8th frame held out, buffered).
- Committed result files, and one command per number.
- Contract tests per component.
- Headline claims are reviewed by independent models of other families before submission (three reviews so far; `reviews/ledger.tsv`).

## 10. Credits and licences
COLMAP / pycolmap (BSD) · Brush (Apache-2.0) · three.js (MIT) · Spark (MIT) · NumPy / SciPy (BSD) · OpenCV incl. ArUco (Apache-2.0) · ffmpeg (LGPL/GPL, CLI) · Deep Blending dataset (Hedman et al. 2018; non-commercial research use, evaluation only, not hosted).
