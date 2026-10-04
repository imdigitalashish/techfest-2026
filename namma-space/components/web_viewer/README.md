# web-viewer (component 11)

Zero-install viewer: three.js 0.180 + Spark 2.3.1 (MIT; importmap from the Spark README), PointerLock WASD + mouse, collisions against the NavGrid (slides along walls), minimap (click to route), POI labels, search with fly-along routes (`G` auto-walks the route), `P` to tag a POI (stored in localStorage; printed as JSON for `pois.json`).

Run locally:
```bash
cd namma-space && python3 -m http.server 8765 --bind 127.0.0.1
# open http://127.0.0.1:8765/components/web_viewer/index.html?scene=../../.data/packages/drjohnson/manifest.json
```
Build a package first: `components/scene_packager/package.py` (see its docstring). Measurements: `eval/results/viewer_perf_drjohnson.json`.
The in-browser planner (`nav.js`) is a port of `components/path_planner/planner.py` (same 8-connected A*, clearance penalty and supercover line-of-sight; clearance uses a 3-4 chamfer transform, so it is approximate).
