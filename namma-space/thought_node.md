# Namma Space · Phone capture to 3D indoor twin with search and navigation — Thought Node

> Journal for `namma-space/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 3–4 — walking skeleton on Deep Blending *drjohnson* (photos → 3DGS → alignment → walkable grid → A*) with real numbers; morning-package docs pushed. Lean Mode ends 08:30 (then ≤3 concurrent sub-agents).
- **Plan:** viewer + packager (Spark WASD, NavGrid collisions, POIs, path) → first auto-research loop on walkable-space → verify the landscape (≤3 agents) → own SfM run + Brush held-out PSNR → the user's home capture → Round-1 twin.
- **Doing:** lead: morning package complete (08:20); next is the viewer.
- **Next:** (1) `components/scene_packager` (.splat export, manifest) + `web/` viewer; (2) `components/walkable_space/autoresearch/` (program.md, frozen eval.py, results.tsv); (3) independent rubber-duck review of ADR 001; (4) landscape verification passes.
- **Needs from user:** (1) Register by 15 Oct. (2) **Capture your home with [`deliverables/capture-sop.md`](deliverables/capture-sop.md)** (≈15–20 min; print [`deliverables/assets/marker_aruco_4x4_id0_150mm.pdf`](deliverables/assets/marker_aruco_4x4_id0_150mm.pdf) if you can) and note your phone model (LiDAR or not). (3) Azure GPU quota is 0 for modern GPU families: request e.g. 8 vCPU "Standard NCASv3_T4 Family" or 36 vCPU "NVadsA10v5" in Central India / East US.
- **Risks:** no CUDA (visual quality and Day-1 turnaround); path safety against dense geometry (first run: 17.5–35% of paths within 15 cm of the proxy; being re-measured); dataset licences (drjohnson is non-commercial); shared-machine contention.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Namma Space — Techfest IIT Bombay. Teams that complete the full pipeline including AR navigation are considered for full-time roles at Juspay. Prize pool ₹1,50,000 (top 3).
- **Official statement:** [`_briefs/namma-space.pdf`](../_briefs/namma-space.pdf) (text: [`_briefs/namma-space.txt`](../_briefs/namma-space.txt)).
- **Challenge (verbatim):** "How would you design and build a complete software pipeline that turns ordinary smartphone photos or videos of an indoor space into an interactive 3D web application: one that lets remote users freely explore the space in first person, search for a specific room or item and jump straight to it, and see the best walking path to reach it around real physical obstacles?"
- **Required pipeline:** (1) our own capture SOP + automatic 3D reconstruction — no manual 3D modelling; any market technology allowed if credited; (2) zero-install web walkthrough with smooth first-person WASD + mouse movement; (3) POI tagging — click rooms or zones to see their names; (4) desktop navigation (mandatory) — optimal walkable paths that stay on the floor and avoid obstacles; (5) bonus — mobile AR navigation through the live camera, updating as the user walks.
- **Round 1 — due 31 Oct:** Drive folder with a ≤5-page technical abstract (architecture, pipeline, SOP, approach), a working free-roam web-viewer link for our own mapped space, a 3–5 min demo video, and the code repo (setup steps + sample data in a test directory). Judged on SOP & pipeline soundness, visual quality & fidelity, web-viewer performance, documentation & video clarity. Results 10 Nov.
- **Round 2 — due 30 Nov (finish by 17 Nov because of exams):** POI labelling, spatial search, obstacle-aware desktop pathfinding; live web app + 3–5 min video. Judged on spatial indexing & POI tagging, pathfinding accuracy, search UI & transitions, code cleanliness & repo setup. Finalists 7 Dec.
- **Round 3 — 16–17 Dec at IIT Bombay:** Day 1: capture a newly assigned campus venue (e.g. the Lecture Hall Complex), reconstruct, annotate POIs and deploy within the time limit. Day 2: 10-min live pitch + demo and 5-min technical Q&A. Scoring: SOP execution & capture 20% · reconstruction & visual quality 20% · web viewer & UX 20% · spatial search & path calculation 20% · pitch & Q&A 20% · on-site AR navigation bonus 10%.
- **Rules:** students, team ≤4 (cross-institute allowed); original work; open-source with licence compliance and credit in the abstract; extra links organised in one master PDF/Doc inside the Drive folder.
- **Round-1 deliverable for the morning package:** `deliverables/capture-sop.md` (so the user can capture) + `deliverables/round1-abstract.md` (draft) + the pipeline proven end-to-end on a public indoor dataset.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Capture apps: Polycam, Scaniverse, Luma (credit if used). Reconstruction: COLMAP / GLOMAP; feed-forward models (DUSt3R, MASt3R, VGGT and newer); 3D Gaussian Splatting (gsplat, nerfstudio splatfacto; OpenSplat and Brush run on Apple silicon).
- Web viewers: Spark (World Labs), PlayCanvas SuperSplat, GaussianSplats3D.
- Geometry for navigation: 2DGS / PGSR or TSDF meshing → floor plane + occupancy → navmesh (Recast/Detour via recast-navigation-js) + A*.
- Semantic POIs: open-vocabulary 3D segmentation (LangSplat, Gaussian Grouping, CLIP features). AR: WebXR, visual relocalisation (hloc), ARKit/ARCore.
- Day-1 on-site turnaround makes pipeline speed and automation critical. What companies ship: indoor digital-twin and 3D-capture products (e.g. Matterport, Polycam, Niantic, World Labs).

## Key decisions
- 2026-10-04 — **Apple-silicon path for Round 1**: Brush v0.3.0 (Metal) for 3DGS and pycolmap 4.2.1 for SfM I/O. Azure GPU quota is 0 for modern families, so CUDA tools wait for the quota ask.
- 2026-10-04 — **Public E2E scene: Deep Blending *drjohnson*** (HF mirror `nvs-bench/deepblending`). Its original licence is non-commercial research only (see [research/datasets.md](research/datasets.md)), so we don't host a derived twin publicly.
- 2026-10-04 — **Navigation frame:** aligned, y-up, metres, floor at y = 0; NavGrid with 5 cm cells; agent radius 0.25 m, height 1.70 m, step 0.15 m. Without a marker, scale comes from a camera-height prior (default 1.5 m, labelled ASSUMED).
- 2026-10-04 — **Spike candidates** (ADR 001 in progress): (A) walkable space from fused capture evidence (sparse points + free-space ray carving + the walked trajectory); (B) capture-time semantic tagging (voice tags + door-sign OCR → POIs). Everything else stays best practice.
- 2026-10-04 — SOP v1.0 published (gate). Novel elements: voice tags, the walked route as walkable evidence, and a camera-height scale fallback.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| 1 | capture (SOP) | person + phone → videos + `capture.json` | our SOP v1.0 | – | ✅ v1.0 | QA pass rate (sharp-frame ratio, coverage); minutes per room |
| 2 | ingest | video → keyframes + audio transcript | ffmpeg + Laplacian blur filter | – | ⏳ | registration rate of kept frames |
| 3 | posing | keyframes → COLMAP model | COLMAP 4.2 / pycolmap 4.2.1 | – | ✅ drjohnson ships poses; own SfM run next | registration rate, reprojection error, ATE vs reference |
| 4 | splat-training | images + poses → 3DGS PLY | Brush v0.3.0 (Metal) | – | ✅ 15k steps, 2M splats, 36.9 min | held-out PSNR/SSIM/LPIPS at a fixed time budget (not yet captured) |
| 5 | scene-alignment | COLMAP model → similarity T (y-up, floor y=0, metres) | camera-up + floor histogram + SVD | – | ✅ | floor residual; scale error vs marker |
| 6 | walkable-space | aligned points + rays + trajectory → NavGrid | height-band occupancy | **A** | ✅ v0 | held-out trajectory recall at a fixed dense-collision rate |
| 7 | path-planner | NavGrid + start/goal → polyline | 8-connected A* + clearance cost + string pulling | – | ✅ contract test | success, collision vs dense proxy, length ratio, p95 latency |
| 8 | poi-extraction | frames + transcript + poses → POIs | manual click-to-tag | **B** | ⏳ | POI precision/recall within 1 m |
| 9 | search | query → ranked POIs | fuzzy lexical over names and aliases | – | ⏳ | top-1 / MRR on a query set |
| 10 | scene-packager | splat + alignment + nav + POIs → package | PLY → .splat / .spz | – | ⏳ | MB per 1M splats; load time |
| 11 | web-viewer | package → WASD app (render, collide, click, search, path) | Spark / three.js | – | ⏳ | p95 frame time; time to first frame |
| 12 | ar-navigation | live camera → pose in twin + arrows | WebXR (Android) + server relocalisation | bonus | ⏳ | median localisation error (cm/°), success rate |
| 13 | orchestrator | capture folder → live URL | shell pipeline | – | ⏳ | end-to-end wall-clock (the Day-1 KPI) |
| 14 | eval-harness | datasets + splits → metrics | `eval/run_nav_e2e.py` | – | ✅ v0 | – |

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (portfolio prioritisation). Score each 1–5 with one line of evidence._
- **Winnability: 4/5.** The rubric rewards a complete pipeline. Tonight, photos → 3DGS → alignment → walkable grid → A* ran end-to-end on a public multi-room scene on a laptop GPU (`eval/results/drjohnson_nav.json`). The main threat is teams that wrap commercial apps (Polycam/Luma) for visual polish.
- **Innovation headroom: 4/5.** Spike A (walkable space from fused capture evidence) vs. the obvious points-only occupancy: held-out camera positions inside the navigable map rose from 0.788 → 0.970 on drjohnson (first run; see Log for caveats). Spike B (voice tags + door-sign OCR → POIs) targets Day-1 annotation time; it is designed but not yet built.
- **Feasibility by the deadline: 4/5.** No CUDA needed for Round 1: Brush on Metal ran 15k steps in 36.9 min on the shared M5, and the navigation stack runs on CPU (grid 0.2–39 s, A* median 13–41 ms). Round 2 by 17 Nov is realistic; AR is the stretch.
- **Demo strength: 5/5.** Walk a twin, search "sofa", watch the route bend around furniture; AR arrows on-site for the bonus.
- **Fit with the user's strengths: 3/5.** Systems and frontier models map onto pipeline orchestration, cloud turnaround and VLM-based POIs/search. 3D vision itself is new territory.
- **Biggest risk:** visual quality and Day-1 turnaround without a CUDA GPU, and path safety. In run 2, 25% (points only) to 37.5% (with the trajectory prior) of held-out paths pass within 15 cm of the dense 3DGS proxy; the ratchet targets recall at a fixed collision budget.
- **One-line pitch:** "Walk your space once with a phone and say what's there. Get a link where anyone can walk it, search it and be routed around the sofa — and on-site, follow arrows through the camera."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 05:25 IST — Phase 0 done; SOP v1.0 published; first splat trained
- Brief re-read against `_briefs/namma-space.txt`. What we must show: R1 (31 Oct) a free-roam WASD web viewer of the user's own space + ≤5-page abstract + 3–5 min video + repo with test data; R2 (target 17 Nov) POI click + search + obstacle-aware floor paths; finals Day-1 capture→deploy under a time limit (speed and automation are scored indirectly in 4 of 6 criteria).
- Compute check: Azure CLI works (VS Enterprise subscription) but GPU quota is 0 for T4/A10/A100/H100 families (`az vm list-usage`); only retired NC/NV families have quota. Decision: Apple-silicon tools tonight (Brush on Metal, pycolmap 4.2.1); CUDA ask under *Needs from user*.
- Dataset: Deep Blending *drjohnson* (263 images, 1332×876, multi-room house) from the Hugging Face mirror `nvs-bench/deepblending` (Inria's server delivered ~6 KB/s). The mirror ships COLMAP poses (80,861 points, 0.56 px mean reprojection error, read with pycolmap).
- Splat: Brush v0.3.0 (Metal), 15k steps, max 2M splats, eval split every 8th image → 2213.8 s wall-clock on the shared M5 (`/usr/bin/time`), 6.9 GB peak memory, 472 MB PLY. Reproduce: see `components/splat-training/README.md` (to be committed).
- SOP v1.0 published: `deliverables/capture-sop.md`, with a printable ArUco scale marker (a detector self-test finds id 0). Novel SOP elements: voice tags → automatic POIs; the walked route used as walkable-space evidence; camera height as a fallback scale.
- Research agents: 10 launched at 02:58; the companies, datasets, posing, web-viewer and social agents failed at 0 turns with model-API "408 timed out reading request body" (network saturation on the shared machine). Relaunched the capture, posing, web-viewer, datasets and social agents.

### 2026-10-04 08:00 IST — Walking skeleton runs end-to-end on drjohnson (navigation geometry); first numbers
- Code: `components/scene_alignment/align.py`, `components/walkable_space/walkable.py`, `components/path_planner/planner.py` (with a doorway contract test), and the harness `eval/run_nav_e2e.py`. Reproduce: `cd namma-space && .venv/bin/python eval/run_nav_e2e.py`.
- The planner contract test caught a discretisation bug (the line-of-sight check used `rint`, the metric mapping uses `floor`). Fixed with a conservative supercover check.
- **Run 1 (07:43, results in `eval/results/drjohnson_nav_run1_0743.json` + `_floorplan_run1_0743.png`; produced BEFORE the line-of-sight fix and with a dense proxy at opacity > 0.5, which kept only 3,244 of 2M splats — treat the collision numbers as indicative only):**
  - Alignment: floor found with 2.9° refinement over the camera-up mean (up-consistency 0.69: a mix of landscape and portrait shots); median camera height 1.5 m (ASSUMED scale; ×0.879 COLMAP units); point heights p1–p99 = −0.03…2.65 m (ceiling ≈2.65 m, plausible); 0.14% of points below the floor; 4.3 s.
  - Held-out camera recall of the navigable map (33 held-out cameras, every 8th image): points-only 0.788 → +carving 0.879 → +trajectory 0.939 → full 0.970. Recall of the walkable (pre-erosion) map is 0.97–1.0.
  - 40 held-out start/goal pairs: 100% success in every variant. Median path / straight-line length 1.009–1.026. A* median 13–41 ms, p95 477–823 ms (pure Python). Grid build 0.2 s (points+trajectory) to 38.8 s (with 18.2M ray samples).
  - Paths within 15 cm of the dense proxy: 17.5% (points-only, +carving) vs 32.5–35% (with trajectory). The trajectory widens the free space next to furniture; this is the trade-off the ratchet must tune (carve_beta, traj_radius, erosion).
- Diagnostics: the Brush PLY is in the COLMAP frame (per-axis percentiles match). Brush opacities are logits with p99 σ ≈ 0.42, so run 2 uses opacity > 0.1 for the dense proxy.
- Research: `research/datasets.md` written by the retried datasets agent (the drjohnson HF mirror's "MIT" tag is unsupported; the original licence is non-commercial). The other agents failed on API 408s; Supervisor Lean Mode → no new agents until 08:30.
- Selection memo v1 filled.

### 2026-10-04 08:20 IST — Morning package pushed; eval run 2 (corrected)
- **Run 2** (`eval/results/drjohnson_nav.json`, `drjohnson_floorplan.png`; fixed line-of-sight planner; dense proxy = 172,217 splats with opacity > 0.1, max scale < 0.2 m, in the 0.15–1.7 m band). Navigable-map recall of held-out positions: 0.788 / 0.879 / 0.939 / 0.970 (points / +carving / +trajectory / both). Paths within 15 cm of the proxy: 25.0% / 25.0% / 37.5% / 37.5%. Path samples in collision: 5.4% / 5.5% / 12.5% / 12.4%. Success 100% in all variants; A* p95 44–175 ms in Python. **The trajectory prior trades clearance for recall**, as ADR 001's antithesis predicted → ratchet objective = recall at a fixed collision budget.
- Lesson: a `git rebase` during an experiment that writes into tracked paths deleted `eval/results/` mid-run (run-2 attempt 1 crashed). Rule: never rebase while a run writes to tracked paths; write to `.data/` and copy afterwards.
- Pushed: `architecture/components.md` + `architecture/contracts/contracts.ts`, `architecture/adr/001-spike.md`, `research/landscape.md` v0 (sources opened tonight marked VERIFIED; the rest UNVERIFIED pending agent passes), `deliverables/round1-abstract.md` v0.1, selection memo v1.
- Not done yet (honest): web viewer and packager; Brush held-out PSNR; our own SfM run (we used the dataset's COLMAP poses); POI extraction; first auto-research loop; independent adversarial review of ADR 001; landscape verification (most "what companies ship" claims are UNVERIFIED).
