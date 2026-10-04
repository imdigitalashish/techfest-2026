#!/usr/bin/env python3
"""Ingest (component 2): capture folder -> sharp, ordered keyframes + FrameSet (frames.json).

Input : a folder with phone videos (*.mov|*.mp4|*.m4v) and/or photos (*.jpg|*.jpeg|*.png|*.heic),
        in any subfolder, plus optional capture.json (SOP §8; its "clips" list fixes the clip order).
Output: <out>/frames/fCC_KKKKK.jpg (clip CC, sequence KKKKK; name order = capture order)
        <out>/frames.json  (contract FrameSet in architecture/contracts/contracts.ts)
Video : ffmpeg extracts at --fps (default 4) with long side <= --max-side; the sharpest frame of each
        window of --keep-every frames is kept; frames below --min-sharp-ratio x clip median are dropped.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile
import time

import cv2
import numpy as np

VIDEO_EXT = (".mov", ".mp4", ".m4v")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".heic")


def sharpness(path):
    g = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if g is None:
        return 0.0
    s = 640.0 / max(g.shape)
    if s < 1:
        g = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    return float(cv2.Laplacian(g, cv2.CV_64F).var())


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,color_transfer,codec_name:format=duration",
                          "-of", "json", path], capture_output=True, text=True)
    j = json.loads(out.stdout or "{}")
    st = (j.get("streams") or [{}])[0]
    return {"width": st.get("width"), "height": st.get("height"), "fps": st.get("r_frame_rate"),
            "codec": st.get("codec_name"), "color_transfer": st.get("color_transfer"),
            "duration_s": float((j.get("format") or {}).get("duration", 0) or 0)}


def find_inputs(root):
    files = sorted(f for f in glob.glob(os.path.join(root, "**", "*"), recursive=True) if os.path.isfile(f))
    vids = [f for f in files if f.lower().endswith(VIDEO_EXT)]
    imgs = [f for f in files if f.lower().endswith(IMAGE_EXT)]
    return vids, imgs


def ingest(root, out, fps=4.0, keep_every=2, max_side=1600, min_sharp_ratio=0.3):
    t0 = time.perf_counter()
    fdir = os.path.join(out, "frames")
    shutil.rmtree(fdir, ignore_errors=True)
    os.makedirs(fdir)
    vids, imgs = find_inputs(root)
    cap = {}
    if os.path.exists(os.path.join(root, "capture.json")):
        cap = json.load(open(os.path.join(root, "capture.json")))
        order = cap.get("clips") or []
        vids.sort(key=lambda v: order.index(os.path.basename(v)) if os.path.basename(v) in order else len(order))
    frames, clips, warnings = [], [], []
    for ci, v in enumerate(vids):
        info = probe(v)
        if info["color_transfer"] in ("arib-std-b67", "smpte2084"):
            warnings.append(f"{os.path.basename(v)}: HDR video ({info['color_transfer']}); SOP asks for HDR off")
        tmp = tempfile.mkdtemp(prefix="ns_ingest_")
        vf = f"fps={fps},scale=w='min(iw,{max_side})':h='min(ih,{max_side})':force_original_aspect_ratio=decrease"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", v, "-vf", vf, "-q:v", "2",
                        os.path.join(tmp, "%06d.jpg")], check=True)
        raw = sorted(glob.glob(os.path.join(tmp, "*.jpg")))
        sh = np.array([sharpness(p) for p in raw])
        med = float(np.median(sh)) if len(sh) else 0.0
        kept = 0
        for w in range(0, len(raw), keep_every):
            j = w + int(np.argmax(sh[w:w + keep_every]))
            if sh[j] < min_sharp_ratio * med:
                continue
            name = f"f{ci:02d}_{j:05d}.jpg"
            shutil.move(raw[j], os.path.join(fdir, name))
            frames.append({"name": name, "clip": os.path.basename(v), "t_s": round(j / fps, 3),
                           "sharpness": round(float(sh[j]), 1)})
            kept += 1
        shutil.rmtree(tmp, ignore_errors=True)
        clips.append({"clip": os.path.basename(v), **info, "extracted": len(raw), "kept": kept,
                      "sharpness_median": round(med, 1)})
    if imgs:
        ci = len(vids)
        for k, p in enumerate(imgs):
            name = f"f{ci:02d}_{k:05d}.jpg"
            dst = os.path.join(fdir, name)
            if p.lower().endswith(".heic"):
                subprocess.run(["sips", "-s", "format", "jpeg", p, "--out", dst], capture_output=True, check=True)
                im = cv2.imread(dst)
            else:
                im = cv2.imread(p)
            if im is None:
                warnings.append(f"unreadable image {p}")
                continue
            s = max_side / max(im.shape[:2])
            if s < 1:
                im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
                cv2.imwrite(dst, im, [cv2.IMWRITE_JPEG_QUALITY, 95])
            elif p.lower().endswith((".jpg", ".jpeg")):
                shutil.copy2(p, dst)
            else:
                cv2.imwrite(dst, im, [cv2.IMWRITE_JPEG_QUALITY, 95])
            frames.append({"name": name, "clip": "photos", "t_s": None, "sharpness": round(sharpness(dst), 1),
                           "source": os.path.basename(p)})
        clips.append({"clip": "photos", "count": len(imgs)})
    fs = {"frames": frames, "voice_tags": [], "clips": clips, "warnings": warnings,
          "params": {"fps": fps, "keep_every": keep_every, "max_side": max_side, "min_sharp_ratio": min_sharp_ratio},
          "capture": cap, "seconds": round(time.perf_counter() - t0, 2)}
    with open(os.path.join(out, "frames.json"), "w") as f:
        json.dump(fs, f, indent=1)
    return fs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=4.0)
    ap.add_argument("--keep-every", type=int, default=2)
    ap.add_argument("--max-side", type=int, default=1600)
    a = ap.parse_args()
    r = ingest(a.input, a.out, a.fps, a.keep_every, a.max_side)
    print(json.dumps({"frames": len(r["frames"]), "clips": r["clips"], "warnings": r["warnings"], "seconds": r["seconds"]}))
