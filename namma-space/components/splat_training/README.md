# splat-training (baseline: Brush on Metal)

**Contract:** in = images + COLMAP model (`images/`, `sparse/0/`) · out = 3DGS PLY (INRIA-style fields: `f_dc_*`, `f_rest_*`, `opacity` as a logit, `scale_*` as log-scale, `rot_*`; header says "Vertical axis: y"). Splat centres are in the COLMAP world frame; we checked that per-axis percentiles match the COLMAP points.

**Baseline run (drjohnson, 4 Oct 2026):**
```bash
cd namma-space
# Brush v0.3.0 macOS arm64 release: gh release download v0.3.0 -R ArthurBrussee/brush -p 'brush-app-aarch64-apple-darwin.tar.xz'
/usr/bin/time -l .cache/brush/brush-app-aarch64-apple-darwin/brush_app .data/deepblending/drjohnson \
  --total-steps 15000 --max-splats 2000000 --eval-split-every 8 --eval-every 5000 \
  --export-every 5000 --export-path .data/runs/drjohnson_brush --export-name 'drjohnson_{iter}.ply' --seed 42
```
| Metric | Value | Source |
|---|---|---|
| Wall-clock, 15k steps | 2213.8 s (36.9 min) | `/usr/bin/time -l`, shared M5 under load from ~20 sessions |
| Peak memory footprint | 6.92 GB | same |
| Splats | 2,000,000 (hit the cap) | PLY header |
| PLY size | 472 MB (15k), 414 MB (10k), 124 MB (5k) | `ls -la` |
| Activated opacity p50 / p99 | σ(−2.70) ≈ 0.063 / σ(−0.33) ≈ 0.42 | `eval` diagnostics |
| Held-out PSNR/SSIM/LPIPS | **not captured**: Brush printed no eval metrics to stdout | rerun with `--eval-save-to-disk` (next) |

Notes: Brush is Apache-2.0 (the release tarball ships `LICENSE`; to be re-checked against the repo). The 2M cap was reached, so for the web we must prune or compress (next: packager → `.splat`/`.spz`).
