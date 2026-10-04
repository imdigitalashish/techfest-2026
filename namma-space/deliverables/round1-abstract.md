# Namma Space — Round 1 Technical Abstract (DRAFT v0.1, 4 Oct 2026)

> Draft for the ≤5-page PDF due 31 Oct. Numbers marked **[drjohnson]** come from committed runs on a public scene (reproduce commands in the repo). Sections marked **TODO(home)** are filled after the user's own capture. Nothing here is a projection unless labelled "target".

**Team:** TBD · **Repo:** `namma-space/` · **Live viewer:** TBD (Round-1 link)

## 1. Problem and goal
Turn an ordinary smartphone video of an indoor space into a photoreal 3D web twin. Anyone can open it from a link, walk through it in first person (WASD + mouse), click rooms to see their names, search for a room or item, and follow an obstacle-aware walking path on the floor. No manual 3D modelling at any stage. Round 1 covers capture → reconstruction → free-roam viewer. We built the navigation layer from day one because the same geometry drives collisions in the viewer.

## 2. System architecture
Fourteen components, each behind a typed contract (`architecture/contracts/contracts.ts`) with its own scalar metric, so each can be improved independently:

`capture SOP → ingest (keyframes + voice tags) → posing (SfM) → splat training (3DGS) → scene alignment (gravity, floor, metric scale) → walkable space (NavGrid) → path planner → POIs + search → scene packager → web viewer (→ AR, bonus)`

Design principles:
1. **One aligned frame** (y-up, floor at y = 0, metres) shared by the splat, the navigation grid, POIs and the AR session.
2. **Apple-silicon first.** The whole Round-1 pipeline runs on a laptop GPU (Metal); cloud GPUs are an accelerator, not a dependency.
3. **Evidence over guesswork.** Every stage reports its own quality metric, which makes it measurable on Day 1 of the finals.

## 3. Capture SOP (summary of `deliverables/capture-sop.md`)
- **Settings:** 4K30 video, HDR off, 1× lens, exposure/focus locked, landscape, audio on.
- **Per room, three passes:** an inward loop, an outward loop tilted 20–40° down (floor edges and furniture legs for navigation), and a "route pass" along real walking routes. Doorways are crossed at half speed with a 1 s pause on each side (that is where reconstructions split).
- **Scale:** a printed ArUco marker (150 mm) on the floor, or the measured camera height as a fallback.
- **Voice tags:** say the room or item name on entry ("Kitchen", "Three-seater sofa"). The timestamp gives the camera pose, so POIs need no manual 3D work.
- **Large venues (finals):** a two-person crew; capture the corridor "spine" first, then rooms as clips that start and end in the corridor; upload each clip while capturing the next.
- **Why each rule exists:** see SOP §10. Each rule maps to a failure mode of SfM, splatting or navmesh extraction.

## 4. Reconstruction pipeline
1. **Ingest:** ffmpeg keyframes at 2–4 fps; a variance-of-Laplacian blur filter; audio transcription for voice tags. *(In progress.)*
2. **Posing:** COLMAP 4.2 via pycolmap (sequential matching for video). Feed-forward posing models are evaluated as a drop-in behind the same contract. *(Verification pending.)*
3. **3D Gaussian Splatting:** Brush v0.3.0 on Apple Metal. **[drjohnson]** 263 images (1332×876), 15k steps, 2M splats: **36.9 min** wall-clock on a shared Apple M5 (6.9 GB peak memory). Held-out PSNR is not yet captured (next run).
4. **Scene alignment:** up = mean camera up, refined by a floor plane fitted to the lowest dense height peak; scale from the marker or camera height; yaw from the principal axes. **[drjohnson]** 4.3 s; floor refined by 2.9° over the camera-up estimate; point heights span −0.03 to 2.65 m (p1–p99), consistent with a floor and a ceiling. Scale on drjohnson is ASSUMED (no marker; 1.5 m camera-height prior).
5. **Packaging:** importance-pruned, compressed splats + `nav.json` + `pois.json` + a manifest. *(Next.)*

## 5. Web viewer *(in progress)*
three.js + a WebGL Gaussian-splat renderer (Spark planned; licence and version to be confirmed), with PointerLock WASD and mouse-look at a 1.6 m eye height. Movement is collision-checked against the NavGrid, so the user can't walk through walls or furniture. POI labels are click targets. Targets: ≥50 fps p95 on a 2023 laptop, first frame ≤5 s. **TODO(home):** measured fps, time to first frame and package size on the user's home.

## 6. Navigation layer (preview of Round 2)
**Walkable space (our spike A).** The evidence already in the capture is fused into a 5 cm NavGrid:
- sparse points in the body band 0.15–1.70 m are obstacles;
- every camera→point observation ray carves free space, which removes floaters;
- the route the person actually walked is evidence of connected floor;
- the walkable area is eroded by a 0.25 m agent radius.

The planner is 8-connected A* with a clearance penalty, plus line-of-sight string pulling (contract test: it must pass through a doorway and never touch a wall).

**[drjohnson] results** (33 held-out camera positions; 40 held-out start/goal pairs; collisions measured against an independent dense proxy, 172k splats from the trained 3DGS — *not* ground truth):

| Evidence used | Held-out positions inside navigable map | Paths passing <15 cm from dense geometry | Path / straight-line length (median) | A* median / p95 |
|---|---|---|---|---|
| points only | 0.788 | 25.0% | 1.029 | 18.7 / 174.9 ms |
| + ray carving | 0.879 | 25.0% | 1.012 | 10.5 / 65.9 ms |
| + walked trajectory | 0.939 | 37.5% | 1.009 | 7.3 / 44.4 ms |
| both | **0.970** | 37.5% | 1.009 | 6.5 / 43.6 ms |

All variants found a path for 100% of pairs. Evidence fusion makes far more of the real walkable space reachable. The trajectory prior also brings paths closer to furniture, so our optimisation target is recall *at a fixed collision budget*, tuned on a held-out split and confirmed on a second scene with real geometry.

## 7. Evaluation protocol
Fixed held-out splits (every 8th image), fixed seeds, one command per result (`.venv/bin/python eval/run_nav_e2e.py`). Each component has an isolated metric: registration rate (posing), held-out PSNR/SSIM/LPIPS at a time budget (splats), floor residual and marker scale error (alignment), recall at a collision budget (walkable space), success / collision / latency (planner), p95 frame time (viewer). **TODO(home):** the same table on the user's home capture.

## 8. Credits and licences (to be finalised)
COLMAP / pycolmap (BSD, to verify) · Brush (Apache-2.0 per the release `LICENSE`, to verify against the repository) · three.js (MIT, to verify) · splat renderer (TBD) · NumPy / SciPy / OpenCV (BSD/Apache, to verify) · Deep Blending *drjohnson* (Hedman et al. 2018; non-commercial research licence — used only for internal evaluation, not hosted).

## 9. Roadmap
- **By 31 Oct (R1):** the user's home captured with the SOP → posing → splat → viewer at a public link; abstract, video and repo with test data.
- **By 17 Nov (R2, early because of exams):** POIs (voice tags + OCR + manual confirm), search, desktop paths in the viewer.
- **Dec (finals):** Day-1 rehearsal on a new venue with a stopwatch; AR bonus (Android WebXR + relocalisation).
