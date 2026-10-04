# Landscape v1 — phone capture → navigable 3D indoor twin (verified, 4 Oct 2026)

**How to read this.** This page is the synthesis. Every claim here is verified, with URL and access date, in the linked detail files. Each was checked at its primary source: arXiv abstract/API, CVF, the official GitHub repo (README/LICENSE via the GitHub API), official docs, caniuse/MDN, or company pages.
- [`sota-reconstruction.md`](sota-reconstruction.md) — posing, feed-forward 3D, splat training, Apple silicon.
- [`sota-navigation-semantics-ar.md`](sota-navigation-semantics-ar.md) — collision/navigation, POIs/search, AR, web viewers.
- [`companies.md`](companies.md) — what companies ship today (≈59 primary pages).
- [`datasets.md`](datasets.md) — datasets and licences.
- [`sources_verified_2026-10-04.tsv`](sources_verified_2026-10-04.tsv) — GitHub API metadata for 31 repos and 20 product pages.

Web-search answers were used as leads only. **At least 7 were wrong** (§5).

## 1. What the judges score → what we must show (`_briefs/namma-space.txt`)
| Round | Scored on | We must show |
|---|---|---|
| R1 · 31 Oct | SOP & pipeline · visual fidelity · viewer performance · docs & video | Our own home as a free-roam WASD link; ≤5-page abstract; 3–5 min video; repo with test data |
| R2 · 30 Nov (target 17 Nov) | POI tagging & spatial indexing · pathfinding accuracy · search UI & transitions · code | Click/search POIs; obstacle-aware floor routes in a live app |
| Finals · 16–17 Dec | capture 20 · reconstruction 20 · viewer/UX 20 · search & path 20 · pitch 20 · AR +10 | Capture → deploy a new IIT Bombay venue on Day 1 under a time limit; AR arrows for the bonus |

## 2. State of the art by component → our choice
| Component | Verified state of the art (Oct 2026) | We use now | We adopt next | Licence notes |
|---|---|---|---|---|
| Posing | Global SfM now lives in COLMAP: the GLOMAP repo is marked deprecated, and pycolmap 4.2 exposes `global_mapping`. Feed-forward 3D models: MapAnything (arXiv 2509.13414, metric, ~2000 views), Depth Anything 3, VGGT / VGGT-Ω (arXiv 2605.15195), π³. None documents Apple-MPS support; the large ones need 7–43 GB on an A100 | COLMAP 4.2 global SfM via pycolmap: 99.6% registered on [public] | MapAnything → COLMAP export → short refine, on an Azure GPU (if quota arrives) | MapAnything Apache-2.0. VGGT default checkpoint non-commercial (a gated commercial one exists). VGGT-Ω FAIR non-commercial |
| Splat training | Brush (Apache-2.0, Metal/WebGPU): `main` has unreleased Mip-Splatting, fused SSIM+L1, 4× pixel memory, faster sort. gsplat (Apache-2.0, CUDA): exposure from EXIF, appearance/pose optimisation, MCMC strategy. OpenSplat: real Metal support (AGPL-3.0). AnySplat: feed-forward init + post-opt (MIT, CUDA) | Brush v0.3.0 binary | Build Brush from `main` (spike D′). gsplat with exposure compensation on a cloud GPU for indoor lighting | OpenSplat AGPL — avoid shipping |
| Collision / walkable | PlayCanvas `splat-transform` (MIT, v3.9.0, 2 Oct 2026): floater cluster filter → 5 cm voxels at opacity ≥0.1 → room fill → capsule carve → collision GLB. Recast via `recast-navigation-js` (MIT, WASM). Mesh arms: AGS-Mesh / DN-Splatter (Apache-2.0, smartphone rooms), MeshSplatting (Apache-2.0, CVPR 2026). Research: Splat-Nav (arXiv 2403.02751), Habitat-GS (ECCV 2026), navmesh validation by voxels (arXiv 2605.21397) | Sparse SfM points + ray carving + trajectory → NavGrid → A*. Eval v3 (corrected): 44–49% of routes collision-free, camera-bootstrap 95% CI ≈30–69% (consistent with missing thin obstacles) | splat-transform voxels seeded by our trajectory → NavGrid; Recast arm; scored on ARKitScenes real geometry | MILo / 2DGS / GOF / PGSR research-only + CUDA |
| POIs & search | Lift 2D to 3D without per-scene training: SAM 3 concept prompts (MLX port in `mlx-vlm`), YOLOE (MPS), multi-view vote onto dominant Gaussians. Room naming + OCR with Qwen3-VL via `mlx-vlm`. HOV-SG-style room layer. Per-scene language fields (LangSplat, OpenGaussian) are CUDA-only and slow for Day 1 | Labelled frames → ray-cast placement; lexical search with aliases | SAM 3 / YOLOE + VLM naming + OCR on keyframes; voice tags; text-embedding search | YOLOE AGPL-3.0 (careful); SAM 3 own licence |
| Web viewer | Spark 2.3.1 (MIT, three.js): reads PLY/SPZ/SPLAT/KSPLAT/SOG, has a `.RAD` LoD tree with `paged: true` HTTP-Range streaming, `minRaycastOpacity` raycasts, `FpsMovement`. PlayCanvas SOG / streamed SOG + SuperSplat walk mode with voxel collision is the strongest alternative. GaussianSplats3D is no longer actively developed. SPZ ≈10× smaller than PLY (Niantic, MIT) | Spark 2.3.1 + `.splat` 32 MB (1M splats); 45 fps static, p95 105 ms walking | `.RAD` paged LoD + SPZ (spike E) | All MIT |
| AR (bonus) | Android Chrome: WebXR AR module, hit-test, anchors, DOM overlay, raw camera access on by default. **iOS Safari: no WebXR** (caniuse, iOS 26.4–27.2). Hosted 8th Wall shut down on 28 Feb 2026; its MIT engine has no SLAM. ARKit geotracking is outdoor-only. VPS: Immersal (web, iOS + Android), MultiSet (WebXR sample), Niantic Spatial (indoor only for pre-scanned spaces) | – | Android WebXR + server-side hloc (DISK/ALIKED + LightGlue) against our COLMAP model, padded with splat-rendered views; ArUco start pose. Backup: Immersal web VPS | hloc Apache-2.0; SuperPoint licence restrictive → use DISK/ALIKED |

## 3. What companies ship today ([`companies.md`](companies.md))
- **No product found that ships the whole chain** (evidence from ≈59 vendor pages, not proof of absence) (phone capture → photoreal twin → automatic walkable map → POI search → obstacle-aware route → AR) behind one zero-install link. Two camps don't meet:
  - **Capture/twin vendors** stop at viewing, measuring and floor plans: Matterport, Polycam, Niantic Scaniverse, KIRI, Luma, Varjo Teleport, Zillow.
  - **Wayfinding vendors** route over 2D maps built from floor plans or surveys, not over a capture: Pointr, Mapsted, Mappedin, IndoorAtlas, MapmyIndia, BootWay.
- **Gaussian splats are standard phone-capture output:** Polycam, Scaniverse (on-device; SPZ/PLY), KIRI (3DGS → mesh), Teleport (cloud, 1M–100M splats). None of the pages opened shows navigation on top of the splats.
- **Turnarounds vendors state:**
  - Meta Hyperscape: up to 8 h of cloud processing; sharing removed on 12 May 2026.
  - Matterport floor plans: 2 business days (6 h Express).
  - Polycam floor plans / Scaniverse splats: on-device.
  - **Nobody offers same-day capture → shareable link with routing.**
- **India:** MapmyIndia (indoor maps from floor plans and surveys) and BootWay (QR-code, no-app wayfinding) verified; no named airport/mall/metro deployment verified. **Juspay:** nothing public on spatial/3D (411 blog URLs, 378 GitHub repos checked).

## 4. Where Namma Space fits
| | Capture/twin vendors | Wayfinding vendors | **Namma Space** |
|---|---|---|---|
| Input | Phone/LiDAR/360 capture | Floor plans + surveys | **Phone video** (+ optional marker) |
| Output | Photoreal tour / splats / floor plan | 2D map + routes (+ AR via VPS) | **Photoreal splat twin + walkable map + POIs + routes** in one link |
| Routing around real furniture | ✗ | Over the drawn map only | **From the capture's own geometry** (being hardened for R2) |
| Turnaround | Minutes (on-device) to days | Weeks (mapping projects) | **Target <90 min capture → link** (spike D′) |

**Borrow:** SPZ + Spark (MIT); splat-transform's collision pipeline (MIT); Meta's three-step capture guidance for the SOP; BootWay-style QR / our ArUco marker as the AR start pose.
**Beat:** same-day automatic routing over a photoreal capture, with zero install.

## 5. Wrong search leads caught (why we verify)
1. "MapAnything and Depth Anything 3 have no open release" — **false**; both have Apache-2.0 code on GitHub (`sources_verified` TSV).
2. "Pi3 / VGGT-Long have no arXiv listing" — **false** per the research files.
3. Meta Hyperscape "share with up to 8 users" — sharing was **removed on 12 May 2026** (Meta help page).
4. Indian airports "among the first" indoor-wayfinding deployments — **UNVERIFIED**, no primary source.
5. Luma "Flythroughs sunset on 1 Jan 2026" — **UNVERIFIED** (third-party blog only).
6–7. Three more are recorded in [`sota-navigation-semantics-ar.md`](sota-navigation-semantics-ar.md#wrong-leads-caught).

## 6. Innovation room → ADR 001 v2
- **Spike D′:** quality-qualified capture → link in under 90 min. Nobody offers it same-day; the levers are verified (Brush `main`, per-clip streaming, on-site QA, feed-forward posing on a GPU).
- **Spike E:** fidelity-constrained delivery (`.RAD` paged LoD, SPZ, render budget).
- **R2 baselines:** collision from dense splats (splat-transform) + Recast arm, measured on real geometry; training-free POIs (SAM 3 / YOLOE + VLM + OCR + voice tags).
