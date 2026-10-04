#!/usr/bin/env python3
"""Splat training (component 4): COLMAP folder (images/ + sparse/0) -> 3DGS PLY via Brush (Metal).

Also computes held-out PSNR/SSIM ourselves from Brush's saved eval renders (--eval-save-to-disk) against
the ground-truth images (8-bit, same size), so the metric does not depend on Brush's logging.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import time

import cv2
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BRUSH = os.path.join(ROOT, ".cache/brush/brush-app-aarch64-apple-darwin/brush_app")


def ssim(a, b):
    a, b = a.astype(np.float64), b.astype(np.float64)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    blur = lambda x: cv2.GaussianBlur(x, (11, 11), 1.5)
    mu_a, mu_b = blur(a), blur(b)
    va, vb, cov = blur(a * a) - mu_a ** 2, blur(b * b) - mu_b ** 2, blur(a * b) - mu_a * mu_b
    m = ((2 * mu_a * mu_b + c1) * (2 * cov + c2)) / ((mu_a ** 2 + mu_b ** 2 + c1) * (va + vb + c2))
    return float(m.mean())


def eval_renders(export_dir, image_dir):
    gts = {os.path.splitext(f)[0]: os.path.join(image_dir, f) for f in os.listdir(image_dir)}
    rows = []
    for r in sorted(glob.glob(os.path.join(export_dir, "**", "*.png"), recursive=True)):
        stem = os.path.splitext(os.path.basename(r))[0]
        key = next((k for k in sorted(gts, key=len, reverse=True) if k in stem or stem in k), None)
        if key is None or "gt" in stem.lower():
            continue
        pr, gt = cv2.imread(r), cv2.imread(gts[key])
        if pr is None or gt is None:
            continue
        if pr.shape != gt.shape:
            gt = cv2.resize(gt, (pr.shape[1], pr.shape[0]), interpolation=cv2.INTER_AREA)
        mse = float(np.mean((pr.astype(np.float64) - gt.astype(np.float64)) ** 2))
        rows.append({"image": key, "psnr": 10 * np.log10(255.0 ** 2 / max(mse, 1e-10)),
                     "ssim": ssim(cv2.cvtColor(pr, cv2.COLOR_BGR2GRAY), cv2.cvtColor(gt, cv2.COLOR_BGR2GRAY))})
    if not rows:
        return {"n": 0, "note": "no eval renders matched; check Brush export naming",
                "files": [os.path.basename(p) for p in glob.glob(os.path.join(export_dir, "**", "*"), recursive=True)][:10]}
    return {"n": len(rows), "psnr": float(np.mean([r["psnr"] for r in rows])),
            "ssim": float(np.mean([r["ssim"] for r in rows])), "per_image": rows}


def train(data_dir, out, steps=15000, max_splats=2_000_000, eval_every_n=8, seed=42, extra=()):
    os.makedirs(out, exist_ok=True)
    cmd = ["/usr/bin/time", "-l", BRUSH, data_dir, "--total-steps", str(steps), "--max-splats", str(max_splats),
           "--eval-split-every", str(eval_every_n), "--eval-every", str(steps), "--eval-save-to-disk",
           "--export-every", str(steps), "--export-path", out, "--export-name", "splat_{iter}.ply",
           "--seed", str(seed), *extra]
    t0 = time.perf_counter()
    p = subprocess.run(cmd, capture_output=True, text=True)
    wall = time.perf_counter() - t0
    log = (p.stdout or "") + (p.stderr or "")
    with open(os.path.join(out, "brush.log"), "w") as f:
        f.write(log)
    peak = re.search(r"(\d+)\s+peak memory footprint", log)
    plys = sorted(glob.glob(os.path.join(out, "splat_*.ply")))
    if p.returncode != 0 or not plys:
        raise RuntimeError(f"Brush failed (exit {p.returncode}); see {out}/brush.log")
    ply = plys[-1]
    with open(ply, "rb") as f:
        head = f.read(4096).decode("ascii", "ignore")
    nsp = int(re.search(r"element vertex (\d+)", head).group(1))
    ev = eval_renders(out, os.path.join(data_dir, "images"))
    res = {"ply_path": ply, "frame": "colmap", "n_splats": nsp, "train_seconds": round(wall, 1),
           "steps": steps, "max_splats": max_splats, "peak_memory_gb": round(int(peak.group(1)) / 1e9, 2) if peak else None,
           "ply_mb": round(os.path.getsize(ply) / 1e6, 1),
           "heldout": {k: v for k, v in ev.items() if k != "per_image"} | {"split": f"every {eval_every_n}th image (Brush eval split)"},
           "brush": "v0.3.0 (Metal)"}
    with open(os.path.join(out, "splat.json"), "w") as f:
        json.dump(res | {"heldout_per_image": ev.get("per_image", [])}, f, indent=1)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir")
    ap.add_argument("out")
    ap.add_argument("--steps", type=int, default=15000)
    ap.add_argument("--max-splats", type=int, default=2_000_000)
    ap.add_argument("--eval-only", action="store_true")
    a = ap.parse_args()
    if a.eval_only:
        print(json.dumps({k: v for k, v in eval_renders(a.out, os.path.join(a.data_dir, "images")).items() if k != "per_image"}))
    else:
        print(json.dumps(train(a.data_dir, a.out, a.steps, a.max_splats)))
