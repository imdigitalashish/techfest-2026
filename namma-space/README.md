# Namma Space — phone capture → navigable 3D web twin

Walk through a space once with a phone. One command turns the video into a photoreal 3D Gaussian-splat twin that anyone can explore in a browser, with no install:
- first-person WASD + mouse movement, with collisions against walls and furniture;
- click and search points of interest;
- follow an obstacle-aware walking path on the floor.

Built for Techfest 2026 (IIT Bombay) × Juspay. Journal and decisions: [`thought_node.md`](thought_node.md). Architecture: [`architecture/components.md`](architecture/components.md).

## Quick start (macOS, Apple silicon)
```bash
cd namma-space
./setup.sh                                   # Python env (uv) + Brush v0.3.0 (Metal 3DGS trainer); needs ffmpeg + uv
./process_capture.sh <capture_folder> home   # videos/photos + capture.json → .data/work/home/site/
cd .data/work/home/site && python3 -m http.server 8080    # open http://127.0.0.1:8080/
```
- Capture instructions (the SOP): [`deliverables/capture-sop.md`](deliverables/capture-sop.md).
- Public test scene: [`test_data/README.md`](test_data/README.md).
- Deploy as an Azure static website: `components/orchestrator/deploy_azure.sh <site_dir> <storage_account>`.

**Viewer controls:** click to walk · `W A S D` move · mouse look · `Shift` run · `/` search · `G` auto-walk the route · `P` tag a POI · `F` fly · click the minimap to route.

## Pipeline (one command: `components/orchestrator/run_pipeline.py`)
| Stage | Component | Tooling |
|---|---|---|
| ingest | video/photos → sharp keyframes (blur filter) | ffmpeg, OpenCV |
| posing | keyframes → camera poses + sparse points, undistorted | COLMAP 4.2 global SfM via pycolmap (CPU) |
| splat | 3D Gaussian Splatting + held-out PSNR/SSIM | Brush v0.3.0 (Apple Metal) |
| align | gravity, floor at y = 0, metric scale (ArUco marker > camera height > assumed) | NumPy, OpenCV ArUco |
| walkable | NavGrid: sparse points + free-space ray carving + walked trajectory | NumPy/SciPy |
| package | aligned, pruned `.splat` + `manifest.json` + `nav.json` + `pois.json` | NumPy |
| site | static viewer + scene | three.js + Spark (MIT) |
| evaluate | path safety v3 (frozen reference, camera-bootstrap CIs), posing accuracy vs a reference | `eval/nav_eval_v3.py` |

Each stage is timed and cached in `.data/work/<name>/report.json`; re-runs resume.

## Repository layout
```
architecture/        components.md, contracts/contracts.ts (typed I/O), adr/
components/<name>/   one folder per component (code, tests, autoresearch/)
eval/                harnesses + results/*.json (committed numbers)
deliverables/        capture SOP, Round-1 abstract, video script
research/            landscape, datasets, verified sources
reviews/             independent and cross-model reviews + ledger.tsv
test_data/           fetch script for the public scene; our own sample capture
.data/ .cache/       gitignored: datasets, splats, work dirs, Brush binary
```

## Evaluation (reproduce)
```bash
.venv/bin/python components/path_planner/planner.py          # planner contract test (doorway)
.venv/bin/python components/scene_alignment/test_marker_scale.py
.venv/bin/python eval/test_nav_eval_v3.py                     # evaluator contract test (doorway geodesic)
.venv/bin/python eval/nav_eval_v3.py --colmap .data/deepblending/drjohnson/sparse/0 --alignment .data/packages/drjohnson/alignment.json --ply .data/runs/drjohnson_brush/drjohnson_15000.ply --out eval/results/drjohnson_nav_v3.json   # needs the public scene + a trained splat (≈10 min CPU); for your own run use .data/work/<name>/{sfm/colmap/sparse/0,alignment.json,splat/splat_15000.ply}
.venv/bin/python components/walkable_space/autoresearch/loop.py   # ratchet (frozen eval.py)
```

## Credits and licences
COLMAP / pycolmap (BSD) · Brush (Apache-2.0) · three.js (MIT) · Spark (MIT) · NumPy / SciPy (BSD) · OpenCV (Apache-2.0) · ffmpeg (LGPL/GPL, used as a CLI) · Deep Blending dataset (Hedman et al., 2018; non-commercial research use, evaluation only).
