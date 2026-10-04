#!/usr/bin/env python3
"""Orchestrator (component 13): ONE command from a capture folder to a deployable web twin.

  .venv/bin/python components/orchestrator/run_pipeline.py --input <capture_dir> --name <name>

Stages (each timed; outputs under --work, default .data/work/<name>/; re-runs skip finished stages
unless --force <stage>):
  ingest   video/photos -> sharp keyframes                      (components/ingest)
  posing   keyframes -> COLMAP model, undistorted               (components/posing, pycolmap 4.2 CPU)
  splat    3DGS training + held-out PSNR/SSIM                   (components/splat_training, Brush/Metal)
  align    y-up, floor y=0, metric scale (marker > camera height > ASSUMED)  (components/scene_alignment)
  walkable NavGrid from points + ray carving + trajectory       (components/walkable_space)
  package  pruned aligned .splat + manifest + nav + pois        (components/scene_packager)
  site     viewer + package -> <work>/site/ (static; serve or deploy)
  evaluate path-safety v3 on held-out frames, posing ATE vs --reference-colmap (optional)
Writes <work>/report.json and prints the local viewer command.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "components"))
sys.path.insert(0, os.path.join(ROOT, "eval"))
STAGES = ["ingest", "posing", "splat", "align", "walkable", "package", "site", "evaluate"]


def umeyama(src, dst):
    mu_s, mu_d = src.mean(0), dst.mean(0)
    xs, xd = src - mu_s, dst - mu_d
    U, S, Vt = np.linalg.svd(xd.T @ xs / len(src))
    E = np.eye(3)
    if np.linalg.det(U @ Vt) < 0:
        E[2, 2] = -1
    R = U @ E @ Vt
    s = np.trace(np.diag(S) @ E) / (xs ** 2).sum(1).mean()
    return s, R, mu_d - s * R @ mu_s


def pose_ate(ours_dir, ref_dir, frames_json):
    from scene_alignment.align import load_colmap
    a, b = load_colmap(ours_dir), load_colmap(ref_dir)
    src_of = {f["name"]: f.get("source", f["name"]) for f in json.load(open(frames_json))["frames"]}
    ref = {n: i for i, n in enumerate(b.names)}
    pairs = [(i, ref[src_of.get(n, n)]) for i, n in enumerate(a.names) if src_of.get(n, n) in ref]
    if len(pairs) < 3:
        return {"n_matched": len(pairs)}
    ia, ib = map(np.array, zip(*pairs))
    s, R, t = umeyama(a.centers[ia], b.centers[ib])
    err = np.linalg.norm((s * (R @ a.centers[ia].T)).T + t - b.centers[ib], axis=1)
    extent = float(np.linalg.norm(np.percentile(b.centers[ib], 95, 0) - np.percentile(b.centers[ib], 5, 0)))
    return {"n_matched": len(pairs), "ate_rmse_ref_units": float(np.sqrt((err ** 2).mean())),
            "ate_median_ref_units": float(np.median(err)), "ate_rmse_pct_of_extent": float(100 * np.sqrt((err ** 2).mean()) / extent),
            "n_ref_images": len(b.names)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="capture folder (videos/photos + optional capture.json)")
    ap.add_argument("--name", required=True)
    ap.add_argument("--work", default=None)
    ap.add_argument("--steps", type=int, default=15000)
    ap.add_argument("--max-splats", type=int, default=2_000_000)
    ap.add_argument("--package-splats", type=int, default=1_000_000)
    ap.add_argument("--camera-height-m", type=float, default=None)
    ap.add_argument("--mapper", default="global", choices=["global", "incremental"])
    ap.add_argument("--reference-colmap", default=None, help="reference poses for ATE (public datasets)")
    ap.add_argument("--force", nargs="*", default=[], help="stages to re-run")
    ap.add_argument("--until", default="evaluate", choices=STAGES)
    a = ap.parse_args()
    work = a.work or os.path.join(ROOT, ".data", "work", a.name)
    os.makedirs(work, exist_ok=True)
    rp = os.path.join(work, "report.json")
    report = json.load(open(rp)) if os.path.exists(rp) else {"name": a.name, "input": os.path.abspath(a.input), "stages": {}}
    files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(a.input) for f in fs)
    cfg = {k: getattr(a, k) for k in ("steps", "max_splats", "package_splats", "camera_height_m", "mapper")}
    listing = "".join(f"{os.path.relpath(f, a.input)}:{os.path.getsize(f)}:{int(os.path.getmtime(f))};" for f in files)
    fp = hashlib.sha1((listing + json.dumps(cfg, sort_keys=True)).encode()).hexdigest()
    old = report.get("input_fingerprint")
    legacy_ok = "config" not in report and old == hashlib.sha1(listing.encode()).hexdigest()  # pre-config format
    if old not in (None, fp) and not legacy_ok:
        print("input or pipeline flags changed since the cached run -> all stages re-run", flush=True)
        report["stages"] = {}
    report["input_fingerprint"] = fp
    report["config"] = cfg
    cap_path = os.path.join(a.input, "capture.json")
    cap = json.load(open(cap_path)) if os.path.exists(cap_path) else {}
    paths = {"frames": os.path.join(work, "frames"), "sfm": os.path.join(work, "sfm"), "splat": os.path.join(work, "splat"),
             "pkg": os.path.join(work, "package"), "site": os.path.join(work, "site")}

    def done(stage):
        return stage in report["stages"] and report["stages"][stage].get("ok") and stage not in a.force

    def run(stage, fn):
        if done(stage):
            print(f"[{stage}] cached ({report['stages'][stage]['seconds']} s)", flush=True)
            return report["stages"][stage]
        print(f"[{stage}] running …", flush=True)
        t0 = time.perf_counter()
        res = fn()
        res = {"ok": True, "seconds": round(time.perf_counter() - t0, 1), **res}
        report["stages"][stage] = res
        for later in STAGES[STAGES.index(stage) + 1:]:  # a re-run invalidates everything downstream
            report["stages"].pop(later, None)
        json.dump(report, open(rp, "w"), indent=1)
        print(f"[{stage}] done in {res['seconds']} s", flush=True)
        return res

    from ingest.ingest import ingest
    from posing.sfm import run_sfm
    from scene_alignment.align import estimate_alignment, load_colmap
    from splat_training.train import train
    from walkable_space.walkable import build_grid, to_json

    def s_ingest():
        r = ingest(a.input, work)
        return {"n_frames": len(r["frames"]), "clips": r["clips"], "warnings": r["warnings"]}

    def s_posing():
        r = run_sfm(paths["frames"], paths["sfm"], mapper=a.mapper)
        return {k: r[k] for k in ("n_frames", "n_registered", "registration_rate", "n_points3D",
                                  "mean_reprojection_error_px", "mapper", "matcher", "timings_s")}

    colmap_dir = os.path.join(paths["sfm"], "colmap", "sparse", "0")

    def s_splat():
        r = train(os.path.join(paths["sfm"], "colmap"), paths["splat"], a.steps, a.max_splats)
        return {k: r[k] for k in ("ply_path", "n_splats", "train_seconds", "steps", "peak_memory_gb", "ply_mb", "accepted", "heldout")}

    def s_align():
        sc = load_colmap(colmap_dir)
        marker = None
        if cap.get("marker"):
            try:
                from scene_alignment.marker_scale import marker_scale
                marker = marker_scale(colmap_dir, os.path.join(paths["sfm"], "colmap", "images"),
                                      size_m=cap["marker"].get("size_mm", 150) / 1000.0)
            except Exception as e:  # noqa: BLE001
                marker = {"ok": False, "reason": f"marker step failed: {e}"}
        h = a.camera_height_m or cap.get("camera_height_m")
        al = estimate_alignment(sc, h)
        if marker and marker.get("ok"):
            T = np.array(al["T_aligned_from_colmap"])
            f = marker["scale"] / al["scale"]
            T[:3, :] *= f
            al.update({"T_aligned_from_colmap": T.tolist(), "scale": marker["scale"], "scale_source": "marker",
                       "camera_height_median_m": al["camera_height_median_m"] * f, "marker": marker})
        elif marker:
            al["marker"] = marker
        json.dump(al, open(os.path.join(work, "alignment.json"), "w"), indent=1)
        return {k: v for k, v in al.items() if k not in ("T_aligned_from_colmap",)}

    def s_walkable():
        from scene_alignment.align import apply
        sc = load_colmap(colmap_dir)
        T = np.array(json.load(open(os.path.join(work, "alignment.json")))["T_aligned_from_colmap"])
        P, C = apply(T, sc.points), apply(T, sc.centers)
        keep = np.bincount(sc.obs_pt_idx, minlength=len(P)) >= 2
        remap = -np.ones(len(P), np.int64)
        remap[keep] = np.arange(keep.sum())
        mm = keep[sc.obs_pt_idx]
        g = build_grid(P[keep], C, C[sc.obs_img_idx[mm]], remap[sc.obs_pt_idx[mm]])
        if not g["navigable"].any():
            raise RuntimeError("walkable stage produced an EMPTY navigable grid — check alignment/scale before packaging")
        os.makedirs(paths["pkg"], exist_ok=True)
        json.dump(to_json(g), open(os.path.join(paths["pkg"], "nav.json"), "w"))
        cij = np.floor((C[:, [0, 2]] - g["lo"]) / g["cell"]).astype(int)
        cij = (np.clip(cij[:, 0], 0, g["nx"] - 1), np.clip(cij[:, 1], 0, g["nz"] - 1))
        return {"area_navigable_m2": float(g["navigable"].sum() * g["cell"] ** 2), "grid": [g["nx"], g["nz"]],
                "camera_positions_on_navigable": float(g["navigable"][cij].mean()), "build_s": round(g["runtime_s"], 2)}

    def s_package():
        pois = os.path.join(paths["pkg"], "pois.json")
        if not os.path.exists(pois):
            json.dump([], open(pois, "w"))
        ply = report["stages"]["splat"]["ply_path"]
        cmd = [sys.executable, os.path.join(ROOT, "components/scene_packager/package.py"), "--ply", ply,
               "--alignment", os.path.join(work, "alignment.json"), "--nav", os.path.join(paths["pkg"], "nav.json"),
               "--pois", pois, "--out", paths["pkg"], "--name", a.name, "--max-splats", str(a.package_splats),
               "--credits", "3DGS trained with Brush v0.3.0 (Apache-2.0)|SfM: COLMAP/pycolmap 4.2 (BSD)|Viewer: three.js + Spark (MIT)"]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
        return json.loads(out)

    def s_site():
        shutil.rmtree(paths["site"], ignore_errors=True)
        shutil.copytree(os.path.join(ROOT, "components/web_viewer"), paths["site"], ignore=shutil.ignore_patterns("README.md"))
        shutil.copytree(paths["pkg"], os.path.join(paths["site"], "scene"))
        size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(paths["site"]) for f in fs)
        return {"site_dir": paths["site"], "site_mb": round(size / 1e6, 1),
                "serve": f"cd {paths['site']} && python3 -m http.server 8080  # open http://127.0.0.1:8080/"}

    def s_evaluate():
        from nav_eval_v2 import prepare
        from nav_eval_v3 import evaluate_one, reference
        d = prepare(colmap_dir, os.path.join(work, "alignment.json"), report["stages"]["splat"]["ply_path"])
        ref = reference(d, 0.25)
        nav = {s: evaluate_one(d, ref, offset=o) for s, o in (("A", 0), ("B", 4))}
        json.dump(nav, open(os.path.join(work, "nav_eval_v3_outcomes.json"), "w"))
        res = {"nav_v3": {s: {k: v for k, v in r.items() if k != "outcomes"} for s, r in nav.items()},
               "dense_proxy_splats": int(len(d["dense"]))}
        if a.reference_colmap:
            res["posing_vs_reference"] = pose_ate(os.path.join(paths["sfm"], "model"), a.reference_colmap,
                                                  os.path.join(work, "frames.json"))
        return res

    fns = {"ingest": s_ingest, "posing": s_posing, "splat": s_splat, "align": s_align, "walkable": s_walkable,
           "package": s_package, "site": s_site, "evaluate": s_evaluate}
    t_all = time.perf_counter()
    for st in STAGES:
        run(st, fns[st])
        if st == a.until:
            break
    report["total_seconds_this_run"] = round(time.perf_counter() - t_all, 1)
    report["total_seconds_all_stages"] = round(sum(s["seconds"] for s in report["stages"].values()), 1)
    json.dump(report, open(rp, "w"), indent=1)
    print(json.dumps({k: report["stages"][k]["seconds"] for k in report["stages"]}), "total", report["total_seconds_all_stages"])
    if "site" in report["stages"]:
        print("View:", report["stages"]["site"]["serve"])


if __name__ == "__main__":
    main()
