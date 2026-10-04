# SOTA for navigation, POIs and search, AR navigation and web splat viewers (verified 2026-10-04)

> **How this was verified (all accessed 2026-10-04).**
> - **Papers:** every arXiv ID, date, title, venue comment and every quoted number comes from the arXiv API record (`export.arxiv.org/api/query?id_list=…`, the same record as `arxiv.org/abs/<id>`). Venues not in the arXiv comment come from the official repo banner or the CVF Open Access page, as marked.
> - **Repos:** star counts, last-push dates and licences come from the GitHub REST API (`gh api repos/<o>/<r>`). README, docs and LICENSE text was read through the same API.
> - **Browser support:** the raw caniuse data (`Fyrd/caniuse/features-json/webxr.json`), MDN browser-compat-data (`api/XRSystem.json`) and the chromestatus.com API.
> - **Products:** official docs and FAQ pages.
> - **Leads:** web-search answers were used only as leads. Three of them were wrong (see [Wrong leads caught](#wrong-leads-caught)).
> - Anything not opened at a primary source is marked **UNVERIFIED**.
> - Reconstruction SOTA is covered in [`sota-reconstruction.md`](sota-reconstruction.md) and is not repeated here.

## TL;DR — what to adopt for Namma Space

1. **Thin obstacles (R2 pathfinding): get obstacles from the dense splats with PlayCanvas `splat-transform` (MIT, v3.9.0, 2 Oct 2026).** It already ships the pipeline we were about to write:
   - `--filter-cluster` keeps only the connected component containing a seed point, which removes floaters;
   - voxelize at 5 cm, marking a voxel solid when a splat with opacity ≥ 0.1 touches it;
   - `--voxel-external-fill` seals rooms;
   - `--voxel-carve h,r` flood-fills a capsule from the seed;
   - `--collision-mesh` writes a `.collision.glb`.

   Seed it from our walked trajectory. Then either rasterise the carved voxels into the existing 5 cm NavGrid (primary arm) or feed the GLB to `recast-navigation-js` (MIT, WASM, three.js helpers; comparison arm). Score with eval v3 against ARKitScenes, not against the splat, which would be circular.
2. **Mesh arm on the Azure GPU: AGS-Mesh / DN-Splatter (Apache-2.0, built for smartphone indoor rooms) or MeshSplatting (Apache-2.0, CVPR 2026).** Feed the result to Recast. MILo, 2DGS, GOF and PGSR are research-only licences (Inria Gaussian-Splatting licence or ZJU non-profit) and need CUDA.
3. **POIs: lift 2D detections to 3D with no per-scene training. Don't train per-scene language fields.**
   - **Detect on posed keyframes:** SAM 3 concept prompts (an MLX port exists in `mlx-vlm` and runs on the M5) or YOLOE (Ultralytics, Apple MPS, AGPL-3.0).
   - **Lift to 3D:** ray-cast into the splat with multi-view voting, i.e. the Dr. Splat / Occam's LGS idea of registering to the dominant Gaussians.
   - **Name:** Qwen3-VL via `mlx-vlm` names rooms and objects; an OCR model in `mlx-vlm` reads door signs.
   - **Search:** lexical + aliases + text-embedding search over the result.
   - **Avoid** LangSplat/V2, OpenGaussian and Occam's LGS training: CUDA-only, mostly non-commercial licences, and they add training time on Day 1.
4. **AR (finals bonus): Android Chrome WebXR plus our own server relocalisation is the most reliable 6-week path.**
   - **Android Chrome:** the AR module, hit-test, anchors, DOM overlay and Raw Camera Access are all *enabled by default* (Chrome 79–107).
   - **iOS Safari has no WebXR:** caniuse lists iOS Safari 26.4 → 27.2 as *not supported*.
   - **Relocalisation:** send a camera frame → hloc (Apache-2.0) with **DISK or ALIKED + LightGlue** (SuperPoint's licence is restrictive) against our own COLMAP model. Pad the database with views rendered from the splat (arXiv 2502.13803).
   - **Fallback:** our printed ArUco marker as the start pose.
   - **Commercial backup** (each needs an extra mapping pass with its own app): Immersal web VPS (MIT sample; iOS Safari + Android Chrome) or MultiSet (WebXR sample tested on Chrome Android, plus an AR wayfinding sample).
5. **Viewer: stay on Spark (2.3.1, MIT).**
   - Pre-build a `.RAD` LoD tree (`npm run build-lod -- <file> --quality`) and load it with `paged: true` (HTTP-Range streaming). This attacks spike E's time-to-visible.
   - Use `SplatMesh` raycasting (`minRaycastOpacity`, default 0.2) for POI clicks and `FpsMovement` for WASD.
   - PlayCanvas (SOG / Streamed SOG, SuperSplat viewer walk mode with voxel collision) is the strongest alternative and a benchmark. Avoid GaussianSplats3D: its README says it is no longer actively developed.

---

## 1. Obstacle-aware navigation in splat / radiance-field twins

### 1a. Planning directly in Gaussian-splat maps (robotics line)
| Work | arXiv (first version → latest) | Venue | What it does (from the abstract) | Code (★, last push, licence) | Maturity · Apple silicon | Adopt for Namma Space? |
|---|---|---|---|---|---|---|
| **Splat-Nav** | [2403.02751](https://arxiv.org/abs/2403.02751) (5 Mar 2024 → v3 11 Jan 2025) | — | Splat-Plan builds a safe-by-construction polytope corridor from collision constraints on the Gaussians, then a Bézier trajectory; Splat-Loc does RGB pose estimation | [chengine/splatnav](https://github.com/chengine/splatnav) (141★, 2025-04-23, MIT) | Research code (drone) · not checked | **Idea only:** treat each Gaussian (inflated by the agent radius) as an obstacle. Overkill for a floor-bound walker. |
| **SAFER-Splat** | [2409.09868](https://arxiv.org/abs/2409.09868) (15 Sep 2024 → v2 17 Mar 2025) | ICRA (arXiv comment) | Control-barrier-function action filter over *all* Gaussians; "hundreds of thousands of Gaussians … 15 Hz during online Splat training" | [chengine/safer-splat](https://github.com/chengine/safer-splat) (49★, 2025-05-09, MIT) | Research · not checked | No — reactive control, not route planning |
| Collision-cone CBF on 3DGS | [2509.14421](https://arxiv.org/abs/2509.14421) (17 Sep 2025) | preprint (L-CSS/ACC) | Each splat → closed-form forward collision cone → CBF inside a QP | not checked | Paper | No |
| **PolyMerge** | [2606.16232](https://arxiv.org/abs/2606.16232) (15 Jun 2026) | IEEE RA-L 11(7), Jul 2026 | Compresses a 3DGS model into convex polytopes whose union **provably over-approximates all obstacles**; polytope count trades conservativeness for compute | not checked | Paper | **Idea:** a conservative obstacle superset is the right failure mode for "never route through a chair" |
| **LiftNav** | [2605.31376](https://arxiv.org/abs/2605.31376) (29 May 2026) | — | Plans on GSFusion's TSDF+GS dual map, because "GS … suffer[s] from soft geometry, limiting precise obstacle avoidance". YOLO detections are lifted with the TSDF; B-spline trajectories with a hinge-loss collision penalty. Replica sim: "100% feasibility rate and shorter trajectories" vs a radiance-field baseline | not checked | Paper | **Yes, principle:** plan on a volumetric occupancy (TSDF/voxels), not on raw Gaussians; take semantics from a 2D detector lifted by geometry |
| **NavArena** | [2609.04602](https://arxiv.org/abs/2609.04602) (4 Sep 2026) | — | Turns fixed 3DGS reconstructions into navigation benchmarks: **occupancy costmap from Gaussian density + height statistics**, semantic goals lifted from multi-view open-vocabulary masks; >2,000 scenes, 22.2 M expert trajectories; tools "will be released" | not released | Paper (newest) | **Yes, as a template:** the same three parts as our R2 (occupancy, lifted POIs, evaluation). Watch for the code. |
| AirSplan / SemSafe-3DGS / Splatblox | [2609.21226](https://arxiv.org/abs/2609.21226) (IROS 2026) · [2609.19330](https://arxiv.org/abs/2609.19330) (IROS 2026 workshop) · [2511.18525](https://arxiv.org/abs/2511.18525) | — | Quadrotor risk-aware planning; semantic risk-aware active navigation; outdoor traversability | not checked | Papers | No (drone/outdoor) |

### 1b. Splat simulators and phone-captured navigation (closest to our setting)
| Work | arXiv | Venue | Key facts (sourced) | Code | Adopt? |
|---|---|---|---|---|---|
| **EmbodiedSplat** (Chhablani et al.) | [2509.17430](https://arxiv.org/abs/2509.17430) (22 Sep 2025) | **ICCV 2025** (arXiv comment) | **iPhone-captured** scenes → meshes via GS → Habitat-Sim. Agents fine-tuned this way beat zero-shot HM3D / HSSD baselines by **+20% / +40% absolute success** on real-world ImageNav; sim-vs-real correlation **0.87–0.97** for the reconstructed meshes | `gchhablani/embodied-splat` exists (0★, no licence file, pushed 2025-10-09) | **Yes, as evidence for the pitch:** phone → splat → mesh → navmesh is a peer-reviewed, validated pipeline. Which mesher they used is UNVERIFIED (not read beyond the abstract). |
| **Habitat-GS** | [2604.12626](https://arxiv.org/abs/2604.12626) (14 Apr 2026 → v2 12 Sep 2026) | **ECCV 2026** (arXiv comment) | Habitat-Sim extension with 3DGS rendering + drivable Gaussian avatars. Its May 2026 `navmesh_editor` lets you "**draw/edit a walkable area** on the scene and bake a Habitat `.navmesh`" (local Flask tool). GS dataset: 129 scenes incl. 64 InteriorGS | [zju3dv/habitat-gs](https://github.com/zju3dv/habitat-gs) (309★, 2026-09-17, "Project Registration License v1.0": free for research/education/personal use; organisational "Project Use" free subject to its conditions) | **Partly:** even an ECCV 2026 simulator uses a *human-edited* walkable area for GS scenes, which supports our "auto + 1-click confirm" UX. Not a dependency (CUDA, Habitat stack). |
| High-fidelity digital twin for manipulation | [2601.03200](https://arxiv.org/abs/2601.03200) (6 Jan 2026 → v2 4 May 2026) | J. Robot Learning (arXiv comment) | 3DGS twin "within minutes from sparse RGB"; visibility-aware semantic fusion; filter-based conversion to **collision-ready** geometry (Unity-ROS2-MoveIt) | not checked | Idea only (manipulation) |

### 1c. Getting geometry out of splats (mesh / collision proxies)
| Method | arXiv | Venue | Sourced claim | Code (★, last push, licence) | Apple silicon | Adopt? |
|---|---|---|---|---|---|---|
| **MeshSplatting** | [2512.06818](https://arxiv.org/abs/2512.06818) (7 Dec 2025) | **CVPR 2026** ([CVF Open Access page](https://openaccess.thecvf.com/content/CVPR2026/html/Held_MeshSplatting_Differentiable_Rendering_with_Opaque_Meshes_CVPR_2026_paper.html) opened) | Opaque meshes via restricted Delaunay triangulation; "+0.69 dB over … MiLo" on Mip-NeRF360, "2x faster" training, "2x less memory". README ships a **Unity project with physics and walkable scenes** | [meshsplatting/mesh-splatting](https://github.com/meshsplatting/mesh-splatting) (730★, 2026-06-23, **Apache-2.0**) | No: Python 3.11 + CUDA 12.6 kernels | **Comparison arm on Azure:** mesh → Recast |
| **MILo** | [2506.24096](https://arxiv.org/abs/2506.24096) (30 Jun 2025) | SIGGRAPH Asia 2025 / TOG (repo banner) | Differentiable mesh extraction every iteration; "an order of magnitude fewer mesh vertices"; meshes suited to physics | [Anttwo/MILo](https://github.com/Anttwo/MILo) (527★, 2026-04-03, **Gaussian-Splatting License, non-commercial**) | No (CUDA) | Research only |
| **Triangle Splatting+** | [2509.25122](https://arxiv.org/abs/2509.25122) (29 Sep 2025) | — | "Differentiable Rendering with Opaque Triangles", motivated by Gaussians being "not natively compatible with the mesh-based pipelines used in VR headsets, and real-time graphics" (the abstract's results were not read) | [trianglesplatting/triangle-splatting](https://github.com/trianglesplatting/triangle-splatting) (1,197★, 2025-11-24, Apache-2.0) is the v1 repo; whether it contains "+" is UNVERIFIED | No (CUDA) | Watch |
| **DN-Splatter** + **AGS-Mesh** | [2403.17822](https://arxiv.org/abs/2403.17822) (WACV 2025) · [2411.19271](https://arxiv.org/abs/2411.19271) (28 Nov 2024) | WACV 2025 / — | AGS-Mesh targets "Indoor Room Reconstruction Using **Smartphones**": adaptive filtering of noisy phone-depth / monocular normal priors, plus scale-aware TSDF/octree meshing that "recovers finer details" | [maturk/dn-splatter](https://github.com/maturk/dn-splatter) (843★, 2025-07-05, **Apache-2.0**; repo hosts both) | No (nerfstudio, CUDA) | **Best-fit mesher for our phone captures** if we run a mesh arm |
| PlanarGS | [2510.23930](https://arxiv.org/abs/2510.23930) (27 Oct 2025) | NeurIPS 2025 | Vision-language planar priors for low-texture indoor surfaces | not checked | — | Watch (walls and floors) |
| 2DGS · PGSR · GOF | [2403.17888](https://arxiv.org/abs/2403.17888) · [2406.06521](https://arxiv.org/abs/2406.06521) · [2404.10772](https://arxiv.org/abs/2404.10772) | SIGGRAPH'24 · TVCG 2024 · SIGGRAPH Asia'24 | Surface-accurate splatting / meshing | hbb1 (3,304★, 2026-08-25) · zju3dv/PGSR (1,112★, 2024-12-25) · GOF (1,022★, 2024-11-15). Licences: Gaussian-Splatting (non-commercial) · ZJU "educational, research and non-profit" · Gaussian-Splatting | No (CUDA) | Research only; PGSR and GOF are dormant |

### 1d. Floaters and occupancy from splats
| Item | Source | Sourced claim | Adopt? |
|---|---|---|---|
| **splat-transform collision pipeline** | [docs: splat-transform/collision](https://github.com/playcanvas/developer-site/blob/main/docs/user-manual/splat-transform/collision.md); repo [playcanvas/splat-transform](https://github.com/playcanvas/splat-transform) (1,352★, v3.9.0 on 2026-10-02, MIT) | `input splat ──► filter-cluster ──► voxelize ──► fill ──► carve ──► [collision mesh]`.<br>• `--filter-cluster`: "keeps only the connected component containing `--seed-pos`" (stray floaters).<br>• `--voxel-size` default **0.05**; `--voxel-opacity` default **0.1**.<br>• `--voxel-external-fill [1.6]` for rooms.<br>• `--voxel-carve [h=1.6, r=0.2]`: capsule flood-fill.<br>• `--collision-mesh smooth\|faces` → `.collision.glb`.<br>• README: "platform-agnostic … Node.js and browser". | **Adopt now** (TL;DR #1). Set the carve capsule to our agent (h 1.70, r 0.25). Seed from trajectory points. Check whether `--voxel-opacity 0.1` keeps chair legs. GPU voxelisation on macOS is UNVERIFIED, so test it. |
| SuperSplat Studio collision | [docs: supersplat/studio/collision](https://github.com/playcanvas/developer-site/blob/main/docs/user-manual/supersplat/studio/collision.md) | Server-side voxeliser, default **5 cm** voxels; walk mode uses a fixed **1.8 m** head height; scale the splat so 1 unit = 1 m | Confirms the 5 cm choice in our NavGrid |
| **TIDI-GS** | [2601.09291](https://arxiv.org/abs/2601.09291) (14 Jan 2026) | Plug-in floater pruning for *indoor* 3DGS: multi-view consistency + spatial relationship + learned importance, detail-preserving; monocular-depth loss | Watch (code not checked); a training-time option if Brush output is noisy |
| **StableGS** | [2503.18458](https://arxiv.org/abs/2503.18458) (24 Mar 2025) | Floaters get stuck because their "opacity gradients … vanish" at a colour pseudo-equilibrium; a dual-opacity architecture fixes it | Watch |
| **Our own free-space evidence** | ADR 001 v2 | The walked trajectory and camera rays prove space is free | **Combine:** splat voxels = obstacle evidence; trajectory/rays = free-space evidence that may delete floaters near walked paths |

### 1e. Navmesh tooling and validation
| Item | Source (★, last push, licence) | Sourced facts | Adopt? |
|---|---|---|---|
| **recast-navigation-js** | [isaac-mason/recast-navigation-js](https://github.com/isaac-mason/recast-navigation-js) (430★, 2026-07-06, MIT) | WASM port of Recast/Detour: pathfinding, crowds, **temporary obstacles (TileCache)**, `@recast-navigation/three` integration. Navmesh built at runtime or offline then imported; can export glTF. README also points to **navcat**, a pure-JS reimplementation by the same author | **Comparison arm:** collision GLB → navmesh → Detour `computePath` in the browser |
| Recast/Detour (upstream) | [recastnavigation/recastnavigation](https://github.com/recastnavigation/recastnavigation) (7,941★, 2026-02-27, Zlib) | "Industry-standard navigation-mesh toolset for games" | Upstream reference |
| **Navmesh validation by geometry** | [2605.21397](https://arxiv.org/abs/2605.21397) (20 May 2026) | Rebuilds walkable space from geometry as voxels; samples locations (RL-prioritised) and compares **voxel reachability vs navmesh reachability**; less exploration effort at similar defect coverage | **Adopt the check in eval:** sample points and compare our NavGrid/navmesh reachability with reference voxel reachability from the ARKitScenes mesh |

**Best recipe for a phone-captured indoor twin (our synthesis of the above, to be tested with eval v3):**
1. Keep the alignment we have (y-up, metres, floor at y = 0).
2. Get obstacles from the **dense splats** using `splat-transform` (filter-cluster → voxelize 5 cm → external-fill → carve with our capsule), seeded by trajectory points.
3. Free space = carved voxels ∪ walked trajectory, inflated by the agent radius.
4. Rasterise the result to the 5 cm NavGrid → A* + string pulling (already contract-tested).
5. Recast navmesh from `.collision.glb` as the comparison arm.
6. Reachability-sampling validation (2605.21397) against ARKitScenes, then a 1-click human fix-up, as Habitat-GS also does.
7. Mesh arm (AGS-Mesh / MeshSplatting) only if the voxel route misses thin obstacles under eval v3.

---

## 2. Automatic POIs and search

### 2a. Open-vocabulary 3D on splats (newest first)
| Method | arXiv (date) | Venue | Sourced claim | Code (★, last push, licence) | Apple silicon | Adopt? |
|---|---|---|---|---|---|---|
| **EviSplat** | [2609.34853](https://arxiv.org/abs/2609.34853) (28 Sep 2026) | — | Keeps each per-view observation feature as "evidence" until query time; "state-of-the-art" (no number in the abstract) | not checked | — | Watch |
| **LEGO** | [2608.10057](https://arxiv.org/abs/2608.10057) (10 Aug 2026) | ECCV 2026 | 3D-consistent multi-level semantic hierarchy from multi-view SAM granularities | not checked | — | Watch (part/whole queries) |
| **ReLaGS** | [2603.17605](https://arxiv.org/abs/2603.17605) (18 Mar 2026) | CVPR 2026 | Hierarchical language-distilled Gaussian scene + **3D semantic scene graph without scene-specific training** | not checked | — | **Closest to our need** (rooms ↔ objects); read the full paper next |
| **OnlinePG** | [2603.18510](https://arxiv.org/abs/2603.18510) (19 Mar 2026) | CVPR 2026 | Online open-vocabulary *panoptic* mapping with 3DGS (sliding window, local-to-global) | not checked | — | Watch (on-site streaming) |
| EmbodiedSplat (feed-forward; different from §1b) | [2603.04254](https://arxiv.org/abs/2603.04254) (4 Mar 2026) | CVPR 2026 | Online feed-forward semantic 3DGS from streaming images | not checked | — | Watch |
| ProFuse · FLEG · Ilov3Splat | [2601.04754](https://arxiv.org/abs/2601.04754) · [2512.17541](https://arxiv.org/abs/2512.17541) · [2605.04506](https://arxiv.org/abs/2605.04506) | — · — · ICPR 2026 | Direct registration with cross-view context and "no render-supervised fine-tuning" · feed-forward language Gaussians "without camera parameters" · instance-level | not checked | — | Watch |
| **LangSplatV2** | [2507.07136](https://arxiv.org/abs/2507.07136) (9 Jul 2025) | NeurIPS 2025 | **476.2 FPS** feature splatting, **384.6 FPS** text querying; 42× / 47× over LangSplat "with improved query accuracy" | [ZhaoYujie2002/LangSplatV2](https://github.com/ZhaoYujie2002/LangSplatV2) (254★, 2025-10-17, **no LICENSE file**) | No (CUDA submodules) | No: per-scene training plus an unclear licence |
| **Dr. Splat** | [2502.16652](https://arxiv.org/abs/2502.16652) (23 Feb 2025) | CVPR 2025 ([CVF page](https://openaccess.thecvf.com/content/CVPR2025/html/Jun-Seong_Dr._Splat_Directly_Referring_3D_Gaussian_Splatting_via_Direct_Language_CVPR_2025_paper.html) opened) | CLIP embeddings **registered to the dominant Gaussians on each pixel ray**; product quantisation; "without per-scene optimization" of the language features | not checked | — | **Adopt the idea:** it is our ray-cast placement, generalised to many views |
| **Occam's LGS** | [2412.01807](https://arxiv.org/abs/2412.01807) (2 Dec 2024) | BMVC 2025 (repo banner) | Weighted multi-view feature aggregation; SOTA "with a speed-up of two orders of magnitude" | [insait-institute/OccamLGS](https://github.com/insait-institute/OccamLGS) (71★, 2025-11-18, Gaussian-Splatting licence) | No | **Adopt the idea** (simple weighted voting) |
| SceneSplat | [2503.18052](https://arxiv.org/abs/2503.18052) (23 Mar 2025) | ICCV 2025 Oral (repo) | Semantics from 3DGS data alone (vision-language pretraining) | [unique1i/SceneSplat](https://github.com/unique1i/SceneSplat) (360★, 2026-05-25, CC-BY-SA-4.0) | not checked | Watch |
| OpenGaussian · Gaussian Grouping · LangSplat | [2406.02058](https://arxiv.org/abs/2406.02058) · [2312.00732](https://arxiv.org/abs/2312.00732) · [2312.16084](https://arxiv.org/abs/2312.16084) | NeurIPS 2024 · ECCV 2024 · CVPR 2024 Highlight | Point-level open vocabulary · identity encodings · CLIP language field | 221★ (GS licence) · 1,060★ (**Apache-2.0**, last push 2024-07-04) · 1,090★ (GS licence) | No (CUDA) | Baselines only |
| **HOV-SG** | [2403.17846](https://arxiv.org/abs/2403.17846) (26 Mar 2024) | RSS 2024 (repo) | **Floor → room → object** open-vocabulary scene graph; cross-floor Voronoi graph; "75% reduction in representation size" vs dense open-vocabulary maps | [hovsg/HOV-SG](https://github.com/hovsg/HOV-SG) (546★, 2026-01-19, **MIT**) | not checked | **Adopt the room layer:** room segmentation from walkable space + room labels = "click a zone to reveal its name" |
| ConceptGraphs | [2309.16650](https://arxiv.org/abs/2309.16650) | — | Open-vocabulary 3D scene graphs | [concept-graphs](https://github.com/concept-graphs/concept-graphs) (962★, MIT) | — | Reference |

### 2b. 2D models to lift onto posed frames, VLM naming and OCR (Apple-silicon focus)
| Model | Paper | Sourced facts | Repo (★, last push, licence) | Apple silicon (sourced) | Adopt? |
|---|---|---|---|---|---|
| **SAM 3** (and SAM 3.1 checkpoints) | [2511.16719](https://arxiv.org/abs/2511.16719) (20 Nov 2025 → v2 28 Mar 2026) | Promptable concept segmentation from noun phrases or exemplars; "doubles the accuracy of existing systems in both image and video PCS"; SA-Co benchmark, 4 M concept labels | [facebookresearch/sam3](https://github.com/facebookresearch/sam3) (11,862★, 2026-09-18, custom **SAM License**: royalty-free limited licence) | The official README requires a "CUDA-compatible GPU with CUDA 12.6 or higher". **MLX port:** [`mlx_vlm/models/sam3`](https://github.com/Blaizzy/mlx-vlm/tree/main/mlx_vlm/models/sam3) ("~860M parameters"; boxes, masks, video tracking), plus a `sam3_1` directory | **Primary detector** (vocabulary: room/furniture nouns). Benchmark speed on the M5 first. Whether HF weights need access approval is UNVERIFIED. |
| **YOLOE** | [2503.07465](https://arxiv.org/abs/2503.07465) (ICCV 2025) | YOLOE-v8-S beats YOLO-Worldv2-S by **+3.5 AP on LVIS** with 3× less training cost and 1.4× faster inference; prompt-free mode with a **4,585-name** built-in vocabulary (Ultralytics docs) | [THU-MIG/yoloe](https://github.com/THU-MIG/yoloe) (2,300★, 2025-06-26, **AGPL-3.0**); [ultralytics](https://github.com/ultralytics/ultralytics) (62,183★, AGPL-3.0) | Ultralytics `device` accepts "**Apple MPS**" (docs `usage/cfg.md`) | **Fast fallback / prompt-free inventory**. AGPL is fine for our open repo, but credit it. |
| SAM 2 | [2408.00714](https://arxiv.org/abs/2408.00714) | Video segmentation and tracking | [facebookresearch/sam2](https://github.com/facebookresearch/sam2) (19,951★, Apache-2.0) | CUDA extension optional; the example notebook has an MPS branch ("if using Apple MPS, fall back to CPU for unsupported ops") | Mask propagation across keyframes |
| Grounding DINO | [2303.05499](https://arxiv.org/abs/2303.05499) | Open-set detection | 10,646★, Apache-2.0, **last push 2024-08-12** | not stated | Superseded by SAM 3 / YOLOE for us |
| Florence-2 | [2311.06242](https://arxiv.org/abs/2311.06242) | Unified vision tasks (incl. OCR) | weights on HF (licence UNVERIFIED) | MLX port exists (`mlx_vlm/models/florence2`) | Optional |
| **VLM naming: Qwen3-VL / FastVLM via `mlx-vlm`** | — | `mlx-vlm` "inference and fine-tuning of VLMs on your Mac using MLX"; model directory includes `qwen3_vl`, `qwen3_5`, `fastvlm`, `florence2`, `sam3` | [Blaizzy/mlx-vlm](https://github.com/Blaizzy/mlx-vlm) (5,564★, 2026-10-03, MIT); [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL) (20,032★, Apache-2.0 repo; per-checkpoint licences not checked); FastVLM repo uses a custom Apple licence | MLX = Apple-silicon native | **Adopt:** name rooms and objects from best-view crops and emit aliases for search |
| **Door-sign OCR** | — | `mlx-vlm` lists DeepSeek-OCR / -2, PaddleOCR-VL, GLM-OCR, dots.ocr, Falcon-OCR | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) (90,566★, Apache-2.0) | MLX ports listed in the `mlx-vlm` README | **Adopt:** "Meeting Room 4" comes from the door plate, not guessed. Apple Vision OCR is an untested alternative (UNVERIFIED here). |

**Recommended POI and search recipe:**
1. Run SAM 3 (MLX) or YOLOE (MPS) on sharp, posed keyframes.
2. Lift masks into 3D by ray-casting into the splat (depth or dominant Gaussian, as Dr. Splat does) and voting across views (Occam's LGS-style weights).
3. Merge into instances.
4. Label each instance with Qwen3-VL on its best crop and OCR any sign text.
5. Add room POIs: segment rooms from walkable space at doorways or narrow passages (HOV-SG's room layer) and let the VLM label each room type.
6. Search = lexical + aliases + text-embedding similarity; measure top-1 / MRR.
7. Finish with 1-click human confirmation in the editor.

Accuracy in every paper above is reported on LERF / 3D-OVS / ScanNet / Replica, never on phone-captured indoor twins, so we must measure POI precision and recall within 1 m ourselves.

---

## 3. Mobile AR navigation

### 3a. Browser AR status (primary compat data)
| Platform | Status (sourced) | Source |
|---|---|---|
| **Chrome Android** | **Enabled by default:** WebXR Device API (79), Anchors (79), **AR Module (81)**, **Hit-test (81)**, DOM Overlay (83), Depth API (90), Lighting Estimation (90), **Raw Camera Access (107)**. **Image Tracking:** "No active development". Plane Detection: "Proposed" (147). caniuse: Chrome Android 154 = partial ("API is very extensive") | [chromestatus API](https://chromestatus.com/api/v0/features?q=WebXR); [caniuse webxr.json](https://github.com/Fyrd/caniuse/blob/main/features-json/webxr.json) |
| **iOS / iPadOS Safari** | caniuse: **not supported** for iOS Safari 26.4, 26.5, 26.6, 27.0, 27.1, 27.2. Desktop Safari: "n d" (only behind the "WebXR Device API" experimental feature). MDN BCD: `XRSystem` safari `version_added: false`; `safari_ios` mirrors it | caniuse (above); [MDN BCD XRSystem.json](https://github.com/mdn/browser-compat-data/blob/main/api/XRSystem.json) |
| **8th Wall** | Hosted platform: "**February 28, 2026: End of platform access**", staged shutdown to Feb 28, 2027. **Distributed Engine Binary** (Jan 2026) *includes SLAM* under a binary-only licence "for continued commercial and noncommercial use"; *not included*: **VPS, Maps, Hand Tracking**. Framework [8thwall/8thwall](https://github.com/8thwall/8thwall) is MIT (488★, 2026-10-03): core, face effects, image targets, sky effects | [8thwall.org/docs/open-source](https://8thwall.org/docs/open-source); [Niantic Spatial blog "next chapter"](https://info.nianticspatial.com/blog/next-chapter) |

Whether 8th Wall's SLAM binary still gives 6-DoF world tracking in **iOS Safari** is **UNVERIFIED**. The engine source detects iOS Safari and uses `getUserMedia`, but no explicit support statement was found. If it works, it is our only iOS-browser 6-DoF path. Test on a device in week 1.

### 3b. Commercial VPS
| Service | Sourced facts | Fit for Namma Space |
|---|---|---|
| **Niantic Spatial VPS** (Scaniverse + NSDK 4.0) | **Free plan:** 20,000 credits/month (≈10 min scan activation, **≈1,500 VPS queries**), ≤5 users. **Plus** $20/mo, **Pro** $50/mo. iPhone 13+ recommended; LiDAR best ([FAQ](https://www.nianticspatial.com/faq/scaniverse)). The NSDK docs offer setup only for **Unity, Swift/iOS, Kotlin/Android**, with **no web SDK** ([docs](https://www.nianticspatial.com/docs/nsdk/)) | Native app only; needs a second capture with Scaniverse on Day 1 |
| **Immersal** | [immersal/vps-for-web](https://github.com/immersal/vps-for-web) (27★, 2026-10-02, MIT sample): "on-device localization natively on a (mobile) Web browser". Supported: **iOS Safari, Android Chrome**. "Uses the device IMU for orientation tracking, and continuous localization for translation (position) tracking to emulate SLAM". On-device (WASM) or on-server (REST). Three.js and Babylon.js. Maps come from the Immersal Mapper app (iOS/Android) or BLK2GO, with a developer token | **The only verified iOS-browser VPS route.** Needs an Immersal mapping pass; pricing UNVERIFIED |
| **MultiSet** | [multiset-webxr-sdk](https://github.com/MultiSet-AI/multiset-webxr-sdk) (11★, 2026-04-04, no licence file): React + Three.js WebXR localisation sample, "Tested with Chrome on Android". [multiset-vps-navigation-needle-sample](https://github.com/MultiSet-AI/multiset-vps-navigation-needle-sample) (13★, 2026-08-20): "Indoor AR wayfinding … follow an arrowed path along the floor", Unity + Needle Engine, browser on Android, includes navmesh steps. Native iOS/Android/Quest/Unity SDKs; SDK licence "Commercial use is allowed subject to the terms of service" | Closest ready-made demo of *our* finals feature; pricing UNVERIFIED |

### 3c. Relocalisation against our own map (research / open source)
| Method | arXiv | Venue | Sourced facts | Code (★, last push, licence) | Adopt? |
|---|---|---|---|---|---|
| **hloc** | [1812.03506](https://arxiv.org/abs/1812.03506) | CVPR 2019 | Retrieval (NetVLAD etc.) + local features (SuperPoint, DISK, D2-Net, SIFT…) + matchers (SuperGlue, LightGlue, NN). README Aachen day with SP+SG: 89.6 / 95.4 / 98.8; InLoc DUC1: 46.5 / 65.7 / 78.3 (thresholds per the visuallocalization.net benchmark) | [cvg/Hierarchical-Localization](https://github.com/cvg/Hierarchical-Localization) (4,229★, 2025-12-10, **Apache-2.0**) | **Adopt** server-side against our COLMAP model |
| LightGlue | — | ICCV 2023 | "weights of LightGlue and the code … Apache-2.0. DISK follows this license as well but **SuperPoint follows a different, restrictive license** … ALIKED … BSD-3-Clause" | [cvg/LightGlue](https://github.com/cvg/LightGlue) (4,810★, Apache-2.0) | **Use DISK or ALIKED + LightGlue** |
| **3DGS-augmented localisation** | [2502.13803](https://arxiv.org/abs/2502.13803) (19 Feb 2025) | — | Adding **images rendered from a 3DGS map at sampled poses** "significantly improves" geometry-based and SCR localisation in a large industrial indoor environment | not checked | **Adopt:** render extra database views from our splat along the walkable area |
| ULF-Loc | [2605.04730](https://arxiv.org/abs/2605.04730) (6 May 2026) | CVPR (highlight), per arXiv comment | −17% mean median translation error vs SOTA on Cambridge; 1/10 the training time and 1/6 the GPU memory of STDLoc | not checked | Watch |
| STDLoc | [2503.19358](https://arxiv.org/abs/2503.19358) | CVPR 2025 | Sparse-to-dense relocalisation on feature Gaussians, no pose prior | [zju3dv/STDLoc](https://github.com/zju3dv/STDLoc) (80★, 2025-06-14, **MIT**) | Watch (CUDA) |
| GS-CPR | [2408.11085](https://arxiv.org/abs/2408.11085) | ICLR 2025 | Test-time pose refinement: 3DGS renders + MASt3R matching | [XRIM-Lab/GS-CPR](https://github.com/XRIM-Lab/GS-CPR) (156★; bundles DUSt3R under **CC BY-NC-SA 4.0**) | Research only |
| GSFeatLoc | [2504.20379](https://arxiv.org/abs/2504.20379) | — | Render RGB-D at the initial pose → 2D-2D matches → PnP. ">10 seconds to as fast as 0.1 seconds"; tolerates 55° / 1.1-unit initial error; <5° / 0.05 units on 90% of synthetic/Mip-NeRF360 images but only 42% on Tanks and Temples | not checked | Idea for a refine step |
| Reloc3r | [2412.08376](https://arxiv.org/abs/2412.08376) | CVPR 2025 | Relative pose regression trained on ~8 M pairs; real time; generalises to new scenes | [ffrivera0/reloc3r](https://github.com/ffrivera0/reloc3r) (334★, **CC BY-NC-SA 4.0**) | Research only |
| ACE · GLACE · ACE0 | [2305.14059](https://arxiv.org/abs/2305.14059) · [2406.04340](https://arxiv.org/abs/2406.04340) · [2404.14351](https://arxiv.org/abs/2404.14351) | CVPR 2023 · CVPR 2024 · ECCV 2024 | Scene-coordinate regression ("relocalize in minutes") | nianticlabs/ace (439★), cvg/glace (107★), nianticlabs/acezero (809★): each LICENSE "allows for non-commercial use only" | Research only |
| Others seen (2025–26) | [2605.07351](https://arxiv.org/abs/2605.07351) SplitGS-Loc · [2508.18242](https://arxiv.org/abs/2508.18242) GSVisLoc (ICCV'25 W) · [2507.23569](https://arxiv.org/abs/2507.23569) GSFFs (CVPR 2025) · [2603.16538](https://arxiv.org/abs/2603.16538) (CVPR 2026) · [2409.14067](https://arxiv.org/abs/2409.14067) SplatLoc | — | GS feature-field localisation and refinement | not checked | Watch |

### 3d. The most reliable live-demo path for a student team (~6 weeks, our synthesis)
1. **Week 1:**
   - three.js WebXR `immersive-ar` on Android Chrome with `hit-test`, `anchors`, `dom-overlay` and `local-floor`.
   - Draw arrows along the A* path.
   - Get the start pose from our **printed 150 mm ArUco marker**, detected in a Raw Camera Access frame. WebXR image tracking is not shipped.
2. **Weeks 2–3:** server relocalisation.
   - Send a frame + intrinsics → hloc (DISK/ALIKED + LightGlue; SfM database + splat-rendered views) → PnP.
   - Compose with the WebXR viewer pose at capture time → twin↔AR transform.
   - Re-localise every few seconds and smooth with anchors.
3. **Week 4:** measure median error (cm/°) and success rate with marker ground truth.
4. **Week 5:** test the iOS route: the 8th Wall SLAM binary (UNVERIFIED) or the Immersal web sample. If neither works, demo on Android only.
5. **Week 6:** freeze and rehearse.
6. **Backup:** MultiSet or Immersal maps of the venue (extra capture time on Day 1; credit in the abstract).

---

## 4. Web splat viewers, streaming and compression

| Viewer / tool | Repo (★, last push, licence) · releases | Sourced capabilities | Adopt? |
|---|---|---|---|
| **Spark** | [sparkjsdev/spark](https://github.com/sparkjsdev/spark) (3,679★, 2026-10-02, MIT). Releases: v2.0.0 **2026-04-14**, v2.1.0 05-18, v2.2.0 09-11, v2.3.0 09-30, **v2.3.1 2026-10-01** | **Formats:** `.ply` (incl. compressed), `.spz`, `.sog`/`.zip` and `.rad` auto-detected; `.splat` and `.ksplat` when the type can be inferred.<br>**LoD:** `lod: true` builds a tree on load in a WebWorker ("1-3 seconds per 1M input splats", up to "30M or so"). Pre-built via `npm run build-lod -- my-splats.ply --quality` → `.RAD`; `paged: true` streams it "via HTTP Range requests" into a shared LRU "splat page table"; the LoD splat budget is tunable.<br>**Picking:** `raycastable` (default true), `minRaycastOpacity` (default 0.2).<br>**Controls:** `SparkControls` = `FpsMovement` (keyboard/mouse/gamepad) + `PointerControls` | **Keep.** Add `.RAD` + `paged` to spike E; picking via three.js `Raycaster` |
| **PlayCanvas engine / SuperSplat** | [engine](https://github.com/playcanvas/engine) (16,978★, v2.23.0 2026-10-01, MIT); [supersplat](https://github.com/playcanvas/supersplat) (10,296★, MIT); [supersplat-viewer](https://github.com/playcanvas/supersplat-viewer) (580★, MIT) | **SOG:** "lossy by design", "typically … ~15–20× smaller than an equivalent PLY"; lossless-WebP textures (16-bit positions, codebook scales, quaternions, DC + opacity, optional SH palette).<br>**Streamed SOG:** `lod-meta.json` spatial tree, chunks loaded "to fit a global splat budget".<br>**Picker API** with depth → world position.<br>**Viewer:** fly/walk modes; a `collision` asset (`.glb` or voxel) | **Benchmark / fallback.** Its `splat-transform` is useful even with Spark (Spark reads `.sog`) |
| **splat-transform** | (see §1d) v3.9.0, MIT | Reads PLY, compressed PLY, SOG, Streamed SOG, SPZ, SPLAT, KSPLAT, LCC; writes PLY, compressed PLY, SOG, Streamed SOG, SPZ, GLB, voxel, LOD, HTML viewer | **Adopt** for conversion, LOD and collision |
| **SPZ** | [nianticlabs/spz](https://github.com/nianticlabs/spz) (924★, 2026-09-01, MIT) | "typically around 10x smaller than the corresponding .ply"; **v4** = 32-byte header + independent **ZSTD** attribute streams (v1–3 gzip, read-only); SH quantisation defaults `sh1Bits` 5, `shRestBits` 4 | Use as the interchange format |
| GaussianSplats3D | [mkkellogg/GaussianSplats3D](https://github.com/mkkellogg/GaussianSplats3D) (2,903★, last push 2025-10-19, MIT) | README: "this repo is no longer in active development" | **Avoid** |

**MB per million splats.** The first two rows are format arithmetic; the rest are *derived from vendor ratios*, not measured by us.

| Format | Size per 1 M splats | Basis |
|---|---|---|
| 3DGS PLY, SH degree 3 | ≈ **248 MB** | 62 float32 properties (xyz, normals, 3 DC + 45 SH, opacity, 3 scales, 4 rotation) × 4 B |
| `.splat` (antimatter15) | ≈ **32 MB** (no SH) | 32 B/splat (`architecture/components.md`) |
| SPZ v4 | ≈ **25 MB** (SH3) | "~10× smaller than PLY" (README) |
| SOG | ≈ **12–17 MB** (SH3) | "~15–20× smaller than PLY" (docs) |
| `.RAD` | UNVERIFIED | No size figure found in the Spark docs read |

→ Measure on our 2 M-splat drjohnson model with `splat-transform` (seconds) and log the results in spike E.

---

## Wrong leads caught
| Lead (web-search answer) | Primary-source result |
|---|---|
| "GS-CPR = arXiv 2402.08752" | 2402.08752 is "Edge coloring lattice graphs"; GS-CPR is **2408.11085** |
| "MILo = arXiv 2402.00801" | 2402.00801 is a Bell-nonlocality paper; MILo is **2506.24096** |
| "No 2025–2026 successors to Splat-Nav exist" | arXiv lists SAFER-Splat (ICRA), PolyMerge (RA-L 2026), LiftNav, NavArena, AirSplan (IROS 2026) and more (§1a) |
| "No open-vocabulary 3DGS papers after LangSplatV2 / Dr. Splat / Occam's LGS" | arXiv lists EviSplat, LEGO (ECCV 2026), ReLaGS and OnlinePG (CVPR 2026) and more (§2a) |
| "SOG ≈ 10–12 MB per million Gaussians"; "Niantic VPS supports Web" | Not stated in the docs opened: SOG docs say 15–20× vs PLY; NSDK lists only Unity/Swift/Kotlin, and the FAQ's "Web: Supported" is about the Scaniverse platform |

## Gaps and follow-ups (explicit)
- **Device tests (blocking for finals AR):**
  - 8th Wall SLAM binary in iOS Safari;
  - Immersal web sample accuracy indoors;
  - `splat-transform` GPU voxelisation on macOS;
  - SAM 3 MLX speed per frame on the M5.
- **Not opened:**
  - full texts (all numbers above are abstract-level);
  - code for LiftNav, NavArena, TIDI-GS, StableGS, ULF-Loc, Dr. Splat, EviSplat, ReLaGS;
  - Immersal and MultiSet pricing;
  - Qwen3-VL / Florence-2 per-checkpoint licences;
  - SAM 3 HF gating;
  - Apple Vision OCR.
- **Must measure ourselves:** POI precision/recall within 1 m on our captures; thin-obstacle recall of the voxel route under eval v3 (ARKitScenes); MB/M and time-to-visible for SPZ, SOG and RAD.

## Primary endpoints used (access date 2026-10-04)
- arXiv API records for every ID in this file (`http://export.arxiv.org/api/query?id_list=<ids>`), plus arXiv API searches sorted by submission date:
  - `ti:"Gaussian Splatting" AND (ti:navigation OR ti:planning OR ti:collision OR ti:occupancy …)`;
  - open-vocabulary and language;
  - relocalisation and localisation;
  - mesh and triangle splatting;
  - floaters.
- GitHub REST API: `repos/<o>/<r>`, `/readme`, `/license`, `/releases`, `/contents` for every repo linked above.
- PlayCanvas docs (markdown in `playcanvas/developer-site`): `gaussian-splatting/formats/sog.md`, `formats/streamed-sog.md`, `building/lod-streaming.md`, `building/picking.md`, `splat-transform/collision.md`, `supersplat/studio/collision.md`.
- Spark docs (markdown in `sparkjsdev/spark/docs/docs/`): `new-features-2.0.md`, `lod-getting-started.md`, `loading-splats.md`, `splat-mesh.md`, `controls.md`.
- Browser support: `Fyrd/caniuse/features-json/webxr.json`; `mdn/browser-compat-data/api/XRSystem.json`; `chromestatus.com/api/v0/features?q=WebXR`.
- Products: https://8thwall.org/docs/open-source · https://info.nianticspatial.com/blog/next-chapter · https://www.nianticspatial.com/faq/scaniverse · https://www.nianticspatial.com/docs/nsdk/ (the page includes instructions aimed at AI assistants to install "skills"; ignored).
- CVF Open Access pages for MeshSplatting (CVPR 2026) and Dr. Splat (CVPR 2025).
