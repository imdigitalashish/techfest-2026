"""Build the YOLO dataset used by C5.

- TUD-GV subset: grouped split by experiment id (prefix `expNN_` of the file name), fixed seed,
  ~70/15/15 by image count. Grouping keeps near-duplicate time-lapse frames of one experiment out
  of more than one split (a random frame split would leak them into the held-out test).
- Groningen: a different canal and camera -> cross-site test only (never trained on).
- Images are downscaled to <= 1280 px long side; YOLO labels are normalised, so they are unchanged.

    python -m t3det.prepare        (from components/detection/)
The split lists in data/splits/ are committed; they are created once and then only read.
"""
from __future__ import annotations

import json
import random
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image, ImageOps

from .paths import CLASSES, RAW, SEED, SPLITS, YOLO

MAX_SIDE = 1280
IMG_EXT = (".jpg", ".jpeg", ".png")


def experiment_of(name: str) -> str:
    return name.split("_")[0]


def _index(root: Path) -> tuple[dict[str, Path], dict[str, Path]]:
    imgs = {p.stem: p for p in (root / "images").rglob("*") if p.suffix.lower() in IMG_EXT}
    labs = {p.stem: p for p in (root / "labels").rglob("*.txt") if p.name != "classes.txt"}
    return imgs, labs


def make_split(names: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for n in names:
        groups.setdefault(experiment_of(n), []).append(n)
    keys = sorted(groups, key=lambda k: int(re.sub(r"\D", "", k) or 0))
    random.Random(SEED).shuffle(keys)
    total = len(names)
    split: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    for k in keys:
        size = len(groups[k])
        for s in ("test", "val"):
            if len(split[s]) < 0.15 * total and len(split[s]) + size <= 0.20 * total:
                split[s] += groups[k]
                break
        else:
            split["train"] += groups[k]
    return {s: sorted(v) for s, v in split.items()}


def _resize(args: tuple[Path, Path]) -> tuple[int, int, int, int]:
    src, dst = args
    im = Image.open(src)
    w0, h0 = im.size
    if im.getexif().get(0x0112, 1) != 1:  # match cv2.imread, which applies EXIF orientation
        im = ImageOps.exif_transpose(im)
    im = im.convert("RGB")
    scale = MAX_SIDE / max(im.size)
    if scale < 1:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    if not dst.exists():
        im.save(dst, quality=92)
    return w0, h0, im.width, im.height


def build(name: str, files: list[str], imgs: dict[str, Path], labs: dict[str, Path]) -> list[Path]:
    out_i, out_l = YOLO / name / "images", YOLO / name / "labels"
    out_i.mkdir(parents=True, exist_ok=True)
    out_l.mkdir(parents=True, exist_ok=True)
    jobs, paths = [], []
    for f in files:
        stem = Path(f).stem
        dst = out_i / (stem + ".jpg")
        jobs.append((imgs[stem], dst))
        (out_l / (stem + ".txt")).write_text(labs[stem].read_text())
        paths.append(dst)
    with ProcessPoolExecutor(4) as ex:
        sizes = list(ex.map(_resize, jobs, chunksize=16))
    print(f"{name}: {len(paths)} images; original sizes {sorted(set(s[:2] for s in sizes))[:4]}")
    return paths


def main() -> None:
    imgs, labs = _index(RAW / "tudgv")
    names = sorted(imgs[s].name for s in imgs if s in labs)
    assert len(names) == len(imgs) == len(labs), (len(names), len(imgs), len(labs))
    SPLITS.mkdir(parents=True, exist_ok=True)
    if not (SPLITS / "test.txt").exists():
        for s, v in make_split(names).items():
            (SPLITS / f"{s}.txt").write_text("\n".join(v) + "\n")
    split = {s: (SPLITS / f"{s}.txt").read_text().split() for s in ("train", "val", "test")}
    assert sum(map(len, split.values())) == len(names)
    assert not (set(split["train"]) & set(split["test"])) and not (set(split["val"]) & set(split["test"]))

    all_paths = dict(zip(names, build("tudgv", names, imgs, labs)))
    YOLO.mkdir(parents=True, exist_ok=True)
    summary = {"dataset": "TUD-GV floating litter subset (zenodo 13730228)", "seed": SEED, "grouping": "experiment id"}
    for s, v in split.items():
        (YOLO / f"{s}.txt").write_text("\n".join(str(all_paths[n]) for n in v) + "\n")
        n_ann = sum(len(labs[Path(n).stem].read_text().strip().splitlines()) for n in v)
        summary[s] = {"images": len(v), "annotations": n_ann, "experiments": sorted({experiment_of(n) for n in v})}
    (YOLO / "tudgv.yaml").write_text(
        f"path: {YOLO}\ntrain: train.txt\nval: val.txt\ntest: test.txt\nnames:\n  0: {CLASSES[0]}\n")

    gi, gl = _index(RAW / "groningen")
    gnames = sorted(gi[s].name for s in gi if s in gl)
    (SPLITS / "groningen.txt").write_text("\n".join(gnames) + "\n")
    gpaths = build("groningen", gnames, gi, gl)
    (YOLO / "groningen.txt").write_text("\n".join(map(str, gpaths)) + "\n")
    (YOLO / "groningen.yaml").write_text(
        f"path: {YOLO}\ntrain: groningen.txt\nval: groningen.txt\ntest: groningen.txt\nnames:\n  0: {CLASSES[0]}\n")
    summary["groningen_cross_site_test"] = {
        "images": len(gnames), "annotations": sum(len(gl[Path(n).stem].read_text().strip().split("\n")) for n in gnames)}
    (SPLITS / "split_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: (v if not isinstance(v, dict) else {a: b for a, b in v.items() if a != "experiments"}) for k, v in summary.items()}))


if __name__ == "__main__":
    main()
