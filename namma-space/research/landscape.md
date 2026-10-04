# Landscape v0 — phone capture → navigable 3D indoor twin (4 Oct 2026)

> **Read this first (honesty note).** Tonight's research fan-out (10 agents) mostly failed: model-API "408 timed out reading request body" errors caused by network saturation on the shared machine, and Supervisor Lean Mode then banned new agents until 08:30. This v0 therefore separates:
> - **VERIFIED**: sources opened tonight, listed with how they were opened;
> - **UNVERIFIED**: the lead's prior knowledge, kept as a map of what to check. Do not cite UNVERIFIED items externally until they are checked.
>
> Per-topic deep dives: [`datasets.md`](datasets.md) (done, cited). Reconstruction, posing, viewer, navigation, semantics, AR and companies follow after 08:30 with ≤3 agents.

## 1. What the judges score → what we must show (VERIFIED: `_briefs/namma-space.txt`)
| Round | Scored on | What we must show |
|---|---|---|
| R1 (31 Oct) | SOP & pipeline soundness · visual quality & fidelity · web-viewer performance · documentation & video | the user's own home as a free-roam WASD web twin, ≤5-page abstract, 3–5 min video, repo with test data |
| R2 (30 Nov; our target 17 Nov) | spatial indexing & POI tagging · pathfinding accuracy · search UI & transitions · code & repo | click POIs, search, obstacle-aware floor paths in a live web app |
| Finals (16–17 Dec) | capture 20 · reconstruction 20 · viewer/UX 20 · search & path 20 · pitch & Q&A 20 · AR +10 | capture → deploy a new venue within the Day-1 time limit; live AR arrows for the bonus |

## 2. Pipeline state of the art (by component)
| Component | Best existing practice (status) | What we verified tonight |
|---|---|---|
| Posing | Incremental SfM (COLMAP) and global SfM (GLOMAP, "Global Structure-from-Motion Revisited", ECCV 2024) — UNVERIFIED tonight. Feed-forward 3D models (DUSt3R/MASt3R, VGGT, MapAnything, Depth Anything 3, π³) are replacing matching for short sequences — UNVERIFIED (speed, licences, Apple-MPS support all unchecked). | **COLMAP 4.2.0** is the current Homebrew stable formula (`brew info colmap`); **pycolmap 4.2.1** installs on macOS arm64 and reads binary models (used in `components/scene_alignment`). Whether GLOMAP's global mapper is merged into COLMAP 4.x is UNVERIFIED. |
| Splat training | 3D Gaussian Splatting (Kerbl et al., SIGGRAPH 2023) and its many fast, compact and anti-aliased variants; CUDA trainers gsplat / nerfstudio splatfacto — UNVERIFIED tonight. | **Brush v0.3.0** (GitHub release 2025-09-14, macOS arm64 binary) trains on Apple Metal from a COLMAP folder. Its CLI exposes `--total-steps`, `--max-splats`, `--eval-split-every`, `--export-*` (`brush_app --help`). Our run: 15k steps, 2M splats in 36.9 min on the shared M5. The exported PLY header reads "Exported from Brush", "Vertical axis: y", SH degree 3. |
| Geometry for navigation | 2DGS / PGSR / Gaussian Opacity Fields for surfaces; TSDF fusion; Recast/Detour navmeshes (recast-navigation-js in the browser); Habitat-style navmesh from scanned meshes; Splat-Nav (robot planning in splat maps) — all UNVERIFIED tonight. | Our own baseline: a point/ray/trajectory evidence grid + A* runs in seconds on CPU (`eval/results/`). |
| Semantics / POIs | Open-vocab 3D (LangSplat, Gaussian Grouping, OpenGaussian), 2D detectors/segmenters lifted to 3D (Grounding DINO, OWLv2, SAM 2/SAM 3), 3D scene graphs (ConceptGraphs, HOV-SG) — UNVERIFIED. | – |
| Web viewer | three.js-based Spark (World Labs), PlayCanvas engine/SuperSplat with compressed SOG, GaussianSplats3D, Babylon.js; Niantic's SPZ format — UNVERIFIED (versions, LOD/streaming, licences). | – |
| AR navigation | WebXR immersive-ar on Android Chrome (ARCore); iOS Safari WebXR support for AR is the key unknown; visual relocalisation (hloc, scene-coordinate regression such as ACE, VPS products) — UNVERIFIED. | – |

## 3. What companies ship today (UNVERIFIED — product-page check pending)
| Company / product | What it is believed to ship | Borrow / beat |
|---|---|---|
| Matterport (Capture app, Pro cameras) | Indoor digital twins, floor plans, web tours; phone capture | Borrow: tour UX, floor plans. Beat: obstacle-aware routing + AR from phone video alone |
| Polycam | Phone photogrammetry, LiDAR scans, Gaussian splats, floor plans | Borrow: capture UX. Beat: navigation + search on the twin |
| Niantic (Scaniverse; VPS) | On-device splat capture; visual positioning | Borrow: SPZ compression, VPS idea for AR |
| Luma AI | Phone capture → radiance fields/splats, web embeds (product focus may have shifted) | Borrow: capture guidance |
| World Labs (Marble; Spark renderer) | Generated and captured 3D worlds; open-source web splat renderer | Borrow: Spark as our renderer |
| Meta (Hyperscape capture) | Room capture → photoreal splat worlds on Quest | Benchmark for visual quality |
| Apple (RoomPlan, Object Capture, ARKit) | Parametric room layouts with furniture categories (LiDAR); on-device photogrammetry | Borrow: RoomPlan-style semantics when LiDAR is present |
| Google (Maps indoor Live View, ARCore) | AR walking arrows indoors in selected venues | The UX target for our AR bonus |
| Indoor wayfinding (Pointr, Mapsted, IndoorAtlas, Immersal, MultiSet) | Indoor positioning and routing on maps prepared by operators | Beat: automatic map + routing from a phone capture |

**Gap no one is believed to close in one zero-install link (to verify):** phone video → photoreal splat twin → automatic walkable map → search → floor paths → AR arrows.

## 4. Datasets (VERIFIED by the datasets agent — see [`datasets.md`](datasets.md))
- Tonight: Deep Blending *drjohnson* (multi-room house, COLMAP poses) via the HF mirror `nvs-bench/deepblending`. The mirror's "MIT" tag is unsupported; the original licence is non-commercial research use, so we don't host a derived twin publicly.
- Next: Mip-NeRF 360 *room*; ARKitScenes (phone RGB-D + 3D boxes) for geometry and POI ground truth; ScanNet++ needs an agreement signed by the user (steps in `datasets.md`).

## 5. Innovation room (feeds ADR 001)
1. **Walkable space from capture evidence:** observation rays carve free space and the walked route proves floor connectivity. Spike A.
2. **Capture-time semantics:** voice tags + door-sign OCR give names that detectors can't infer. Spike B.
3. **Day-1 turnaround:** per-clip upload and parallel processing; feed-forward posing once verified.

## 6. Sources opened tonight (accessed 2026-10-04)
- Official statement: `_briefs/namma-space.txt` (Techfest 2026-27, Namma Space).
- Brush releases (GitHub API `repos/ArthurBrussee/brush/releases`): tags v0.3.0 (2025-09-14), 0.2.0 (2025-01-30); assets include `brush-app-aarch64-apple-darwin.tar.xz`. Brush CLI help and PLY header from the downloaded v0.3.0 binary.
- Homebrew formula metadata: `brew info colmap` → "colmap: stable 4.2.0 (bottled) — Structure-from-Motion and Multi-View Stereo — https://colmap.github.io/".
- pycolmap 4.2.1 (installed from PyPI via `uv pip install pycolmap`; version printed by `pycolmap.__version__`).
- Hugging Face API: `datasets/nvs-bench/deepblending` (file tree: `drjohnson/images`, `drjohnson/sparse/0`; README front-matter `license: mit`).
- Azure CLI `az vm list-usage` (quotas: 0 for NCASv3_T4 and NDASv4_A100; legacy NC/NV families 18 vCPU).
- [`datasets.md`](datasets.md): its own source list.
