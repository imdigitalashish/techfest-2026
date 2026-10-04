# Namma Space · Phone capture to 3D indoor twin with search and navigation — Thought Node

> Journal for `namma-space/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** active batch (Supervisor, 09:55). The definition of done has 6 items: E2E pipeline · viewer + POIs + search + path · abstract + video script + setup · drop-in script · memo + journal · cross-model review of the Round-1 deliverable.
- **Plan:** E2E on raw drjohnson photos (own SfM → Brush → align → NavGrid → package → site → eval v3) → POIs + site + viewer measurement (S_V) → fill the abstract → cross-model reviews as sessions (gpt-6-astra: deliverable; gpt-6-sol: eval code + headline numbers) → DONE message.
- **Doing:**
  - lead: E2E run (Brush training since 10:12); abstract v0.9 drafted with ⟨pending⟩ slots.
  - child sessions (2/2): [companies research](ghapp://sessions/f288d1bd-555c-428d-800f-15071f60f1bc), [SOTA nav/POI/AR/viewer](ghapp://sessions/4eb75b17-eb5d-4b07-9a64-ad9b17993992).
- **Next:** fill numbers → reviews → DONE. After DONE, only work that needs the user's capture: process it with `./process_capture.sh`, deploy, measure S_T / S_V.
- **Needs from user:**
  1. Register by 15 Oct (team ≤4; teammates' names).
  2. **Capture your home with [`deliverables/capture-sop.md`](deliverables/capture-sop.md)** (≈15–20 min). Print [`deliverables/assets/marker_aruco_4x4_id0_150mm.pdf`](deliverables/assets/marker_aruco_4x4_id0_150mm.pdf) at 100%. Time yourself with a stopwatch. Note the phone model (LiDAR or not). Hand off the originals via AirDrop/cable plus `capture.json`, then run `./process_capture.sh <folder> home` (or drop the folder path in the Inbox).
  3. Azure GPU quota is 0 for modern GPU families: request e.g. 8 vCPU "Standard NCASv3_T4 Family" or 36 vCPU "NVadsA10v5" (Central India / East US).
  4. OK to host the home twin publicly on an Azure static website (needed for the R1 link; anyone with the link sees your home).
  5. Optional: sign the ScanNet++ terms for a second real-geometry benchmark.
- **Risks:**
  - R1 depends on the user's capture (SOP untested in the field).
  - Viewer hitching while walking (p95 105 ms vs a 20 ms budget).
  - Path safety: ≈50% of routes come within 0.275 m of dense geometry (sparse map misses thin obstacles).
  - No CUDA; dataset licences (drjohnson is non-commercial: never host it).

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
- 2026-10-04 — **Spike candidates superseded:** see the ADR 001 v2 entry below.
- 2026-10-04 10:30 — **ADR 001 v2: spikes are D′ (quality-qualified capture→twin turnaround) and E (fidelity-constrained first-person delivery).** Walkable space and POIs become honestly measured R2 baselines. Trigger: two independent reviews (rubber-duck; gpt-6-astra max) + leak-free evals v2/v3 showing no evidence-fusion gain.
- 2026-10-04 — **Path-safety metric = eval v3** (`eval/nav_eval_v3.py`): frozen reference grid, verified-free endpoints, full-polyline swept check, all pairs, Wilson CIs, paired sign tests. v1/v2 numbers are historical only.
- 2026-10-04 — Search answers are leads only (one claimed MapAnything / Depth Anything 3 were unreleased; GitHub shows Apache-2.0 releases). Every SOTA claim is verified on arXiv/GitHub/project pages.
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
- **Winnability: 4/5.** The rubric rewards a complete pipeline. One command now runs from raw photos to a deployable site on a laptop: own SfM 99.6% registered, splats on Metal, alignment, NavGrid, viewer (`components/orchestrator/run_pipeline.py`). The threat is teams wrapping commercial apps (Polycam/Luma) for visual polish.
- **Innovation headroom: 3/5.** After two independent reviews and a leak-free re-evaluation, the v1 spike (walkable space from capture evidence) showed **no measurable gain**: eval v3, all 406–435 pairs, CFC 0.45–0.50 for every variant; paired sign tests p ≥ 0.06. ADR 001 v2 moves the spikes to **D′ quality-qualified capture→twin turnaround** (on-site QA + streaming; S_T scalar) and **E fidelity-constrained viewer delivery** (S_V scalar). Both are measurable and judge-weighted, but more engineering than novel.
- **Feasibility by the deadline: 4/5.** No CUDA needed for R1. SfM 6 min + Brush ≈37 min on the shared M5; CPU navigation in seconds. R2 by 17 Nov is realistic; AR is the stretch.
- **Demo strength: 5/5.** Walk the twin, search "sofa", follow the route; on Day 1, "capture → link in under 90 min" is itself the demo.
- **Fit with the user's strengths: 3/5.** Systems and frontier models map onto pipeline orchestration, cloud turnaround and VLM-based POIs. 3D vision itself is new territory.
- **Biggest risk:** (1) R1 depends on the user's own capture (phone unknown; SOP untested in the field). (2) Viewer hitching while walking (p95 105 ms vs a 20 ms budget). (3) Path safety: about half of the routes pass within 0.275 m of dense geometry, because the sparse-point map misses thin obstacles. R2 fix: dense-splat obstacles, judged on a real-geometry scene.
- **One-line pitch:** "Walk your space once with a phone. Within the hour, anyone can walk it from a link, search it and be routed around the sofa — and on-site, follow arrows through the camera."

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

### 2026-10-04 09:15 IST — Viewer + packager working on drjohnson; first ratchet running
- **Scene packager** (`components/scene_packager/package.py`): 2.0M splats → filters (opacity ≥ 0.02, scale ≤ 1.5 m) keep 1.79M → importance-pruned to 1.0M → `scene.splat` 32.0 MB, baked into the aligned frame (y-up, floor 0, metres); 489 s on the loaded M5 (pure NumPy, unoptimised).
- **Viewer** (`components/web_viewer/`; three.js 0.180 + Spark 2.3.1 from its README importmap; Spark is MIT, npm latest 2.3.1, modified 2026-10-01): PointerLock WASD with smoothed velocity, NavGrid collisions with wall sliding, minimap click-to-route, POI tagging (`P`) and search with route + auto-walk (`G`). Measured in Chrome 154 (ANGLE Metal, Apple M5, 1200×863), static: median 45.2 fps, p95 36.7 ms; first frame 1.05 s, splats loaded 10.5 s (localhost). While auto-walking: median 42.4 fps but p95 104.7 ms (first 3.5 s: 26.7 fps, p95 137 ms) → **movement hitching is the top viewer issue**. JS A*: 82–94 ms for 8–11 m routes. The camera stayed on the navigable grid the whole walk. Evidence: `eval/results/viewer_perf_drjohnson.json`; screenshots in `.data/runs/` (not committed).
- **Ratchet #1** (`components/walkable_space/autoresearch/`: program.md, frozen eval.py, loop.py, results.tsv): J = recall_nav − path_collision_rate; keep only if ΔJ_A ≥ 0.03 and ΔJ_B ≥ 0. Baseline J_A = 0.595 (reproduces run 2 exactly), J_B = 0.550. 8 hypotheses queued.
- Lean Mode lifted (≤2 agents): `r-companies-3` (what companies ship today) and `rd-adr001` (independent adversarial review of ADR 001) launched. The lead runs `research/verify_sources.py` (GitHub API / arXiv API / product pages → `research/sources_verified_2026-10-04.tsv`).

### 2026-10-04 10:20 IST — Active batch: one-command pipeline, leak-free path-safety eval, docs; SOTA verification under way
- **Supervisor directives handled:** active batch (Namma Space + 4 others). Definition of done = 6 items (pipeline E2E with timings + metrics, viewer + POIs + search + path, abstract + video script + setup with test data, drop-in script, memo + journal current, cross-model review of the Round-1 deliverable). Delegation now goes through child sessions (≤2 running); reviews are recorded in `reviews/` + `reviews/ledger.tsv`.
- **User (10:05):** "make sure you look into the latest SOTA research … you know exactly what the problem statement is?" → replied with the brief; launched `r-sota-recon` (verified research) + `astra-adr001` (gpt-6-astra, max) and verified the navigation leads myself.
- **Verified tonight (GitHub API / arXiv abstract pages / project pages, accessed 2026-10-04):**
  - colmap/glomap is marked "[DEPRECATED]", and pycolmap 4.2.1 exposes `global_mapping` → global SfM lives in COLMAP 4.x now.
  - MapAnything (Apache-2.0, 3.8k★) and Depth Anything 3 (Apache-2.0, 6.4k★) are released. A web-search answer claiming they were unreleased was **wrong**: search answers are leads only.
  - Spark 3.7k★ (MIT, pushed 2 Oct); Brush 5.1k★ (Apache-2.0, pushed 3 Oct); SAM 3 11.9k★.
  - Navigation in splats: Splat-Nav (arXiv 2403.02751); Habitat-GS (zju3dv, "[ECCV 2026]" per the repo, 309★); MeshSplatting (Apache-2.0, 730★; the project page demos walkable scenes in Unity from its meshes); navmesh validation by voxels (arXiv 2605.21397); 3DGS digital twin → collision geometry (arXiv 2601.03200).
- **Own SfM (E2E run, raw drjohnson photos):** global mapper, 262/263 registered (99.6%), 0.661 px, 12,316 points (vs 80,861 in the shipped model); 360 s (SIFT on CPU 219 s · matching 115 s · mapping 23 s · undistortion 3 s). Brush training is running.
- **Path-safety eval v2** (`eval/nav_eval_v2.py`, `eval/results/drjohnson_nav_v2.json`; buffered hold-out ±2 frames, snap ≤0.25 m, connectors checked, clearance at the 0.25 m agent radius): **all four evidence variants are within noise**. CFC@0.25: A 0.600/0.600/0.600/0.600, B 0.625/0.600/0.650/0.600 (points / +carving / +trajectory / full). Buffered recall 0.85–0.91. Proxy noise floor 15–18%. **Conclusion: the 0.788→0.970 recall gain reported earlier was mostly hold-out leakage through adjacent frames.** The 1st reviewer was right. Spike A has no demonstrated advantage yet → ADR 001 is being revised (waiting for the gpt-6-astra opinion).
- Added: `README.md` (setup, run, layout, credits), `setup.sh`, `process_capture.sh` (drop-in for the user's capture), `components/orchestrator/deploy_azure.sh`, `test_data/` (fetch script + README), `deliverables/demo-video-script.md`, `requirements.txt` (pinned), POI tool + drjohnson POI spec (7 POIs labelled from evidence frames).

### 2026-10-04 10:31 IST — gpt-6-astra review → eval v3 → ADR 001 v2 (spikes D′ + E); verified SOTA research
- **gpt-6-astra (max) review** of ADR 001 + eval v2: 9 items, all ACCEPTED (`reviews/2026-10-04-adr001-gpt-6-astra.md`; ledger updated). It found 2 blocking evaluator bugs in v2: the 0.30 m endpoint exclusion swallowed the ≤0.25 m connectors, and the reference grid depended on the candidate's bounds/cell.
- **eval v3** (`eval/nav_eval_v3.py` + contract test `eval/test_nav_eval_v3.py`: doorway geodesic 3.280 m vs analytic 3.170 m, within the ≤9% grid bound). On drjohnson (shipped poses), all 406 (A) / 435 (B) pairs: **CFC 0.453–0.466 (A), 0.490–0.501 (B)** for every evidence variant; Wilson ±0.05; refusals 0%; collisions ≈50%; stretch vs reference geodesic ≈0.98 (the candidate cuts corners the dense geometry says are within 0.275 m of something). Paired sign tests vs points-only: p ≥ 0.06 everywhere → **no variant differs**. Results: `eval/results/drjohnson_nav_v3.json`.
- **ADR 001 v2:** spikes = D′ (S_T = mean 𝟙[accepted]·max(0, 1 − T/90 min)) and E (S_V = max(T_visible/5 s, F95/20 ms) at ≤1 dB PSNR loss). Walkable space / POIs → R2 baselines; next baseline = dense-splat obstacles judged on a real-geometry scene (ARKitScenes) to avoid circularity.
- **Verified SOTA (`research/sota-reconstruction.md`, agent `r-sota-recon`, primary sources):**
  - Brush's latest release is still v0.3.0, but `main` has unreleased Mip-Splatting, a 4× memory cut and +10–15% speed → build from source.
  - VGGT-Ω (arXiv 2605.15195) is real, but FAIR non-commercial.
  - MapAnything (arXiv 2509.13414, Apache-2.0, metric, ~2000 views) is the licence-cleanest feed-forward option; AnySplat (MIT) for feed-forward Gaussians. Neither has confirmed MPS support.
  - OpenSplat has confirmed Metal (AGPL-3.0).

### 2026-10-04 11:35 IST — Research complete (verified); gpt-6-sol review processed; Round-1 review running
- **Child sessions** (visible in the sidebar; idle, work pushed, not archived):
  - [companies research](ghapp://sessions/f288d1bd-555c-428d-800f-15071f60f1bc) → `research/companies.md` (`fdd62bc`, ≈59 primary pages). No product ships capture → twin → walkable map → search → route → AR in one zero-install link; hosted 8th Wall shut down on 28 Feb 2026; Meta Hyperscape sharing was removed on 12 May 2026; nothing public on Juspay + spatial.
  - [SOTA nav/POI/AR/viewer](ghapp://sessions/4eb75b17-eb5d-4b07-9a64-ad9b17993992) → `research/sota-navigation-semantics-ar.md` (`1cff9ce`). R2 collision baseline = PlayCanvas splat-transform (MIT). iOS Safari has no WebXR → Android WebXR + hloc (DISK/ALIKED + LightGlue); backup Immersal. Spark `.RAD` paged LoD for spike E. Training-free POIs: SAM 3 / YOLOE + VLM + OCR.
  - [gpt-6-sol code review](ghapp://sessions/afbe9615-c383-40ca-ae49-6bc86988c90b) → `reviews/2026-10-04-pipeline-eval-gpt-6-sol.md` (`42d4c69`): 18 items, 17 accepted + 1 partly rejected; fixes pushed (see the decisions table in that file).
  - [gpt-6-astra Round-1 deliverable review](ghapp://sessions/6191e0c7-c5e1-4355-945f-a14226a55f57) running since 11:20.
- **`research/landscape.md` v1** rewritten as a verified synthesis (per-component SOTA → our choice; what companies ship; positioning; ≥7 wrong search leads caught).
- **eval v3 corrected** (gpt-6-sol H1/H2: margin cell·√2/2, no reference corner-cutting) and re-run: CFC 0.443–0.490 for every variant; **camera-level bootstrap 95% CI ≈0.30–0.69** (pair-level Wilson ±0.05 was too narrow); refusals 0% among 29/33 and 30/33 eligible endpoints; paired sign tests p ≥ 0.06 (no evidence of a difference, not equivalence).
- **Supervisor alignment (11:15):** agreed — the abstract leads with what R1 scores; walkable space is an R2 baseline with a frozen evaluator; the 0.788 → 0.970 result is dropped (leakage); path safety is a known gap with a fix plan.
- **E2E run:** Brush has been training for 82+ min (37 min when the machine was quieter). Likely GPU contention (CapCut ≈65% CPU plus other sessions). Waiting; the stage cache keeps SfM.
