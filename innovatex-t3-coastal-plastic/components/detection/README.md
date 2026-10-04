# C5 vision detector + C6 flux counter (Theme 3, coastal plastic)

Status (2026-10-04 06:58 IST): data + split + code committed; baseline training in progress (see Log).
Owner: child session "T3 detection + flux". Contracts: `../../architecture/contracts/contracts.py` (`FrameDetections`, `FluxEstimate`).

## Dataset
**TUD-GV floating-litter subset** — Jia, de Vries, Kapelan, van Emmerik, Taormina (2024), *Detecting floating litter in
freshwater bodies with semi-supervised deep learning*, Water Research 266:122405, doi:10.1016/j.watres.2024.122405.
Data: https://doi.org/10.5281/zenodo.13730228 (CC BY 4.0; opened 2026-10-04). 1,501 RGB images (1920x1080) from experiments
at TU Delft Green Village, 8,181 boxes, one class `litter`. Cross-site set: **Groningen** canal, same paper,
https://doi.org/10.5281/zenodo.13730384 (CC BY 4.0; 63 images 2592x1944, 383 boxes; bridge camera 4 m high).
Both downloadable without credentials.

Download + build (about 850 MB, under `.data/`, gitignored):
```bash
bash components/detection/data/fetch_data.sh          # from innovatex-t3-coastal-plastic/
cd components/detection && python3.11 -m t3det.prepare
```

Why not the others (checked 2026-10-04): FloW-Img (ICCV 2021) needs an application on orca-tech.cn
(README of github.com/ORCA-Uboat/FloW-Dataset); HF `gonzz2026/A-dataset-of-images-of-floating-rubbish-...` is a 3.2 GB zip
with unclear annotations; TACO is not on water. TUD-GV is real floating litter on water, CC BY 4.0, with boxes.

**Split** (no official split is published): grouped by experiment id (`expNN_`), seed 42, ~70/15/15 by image count, so
near-duplicate time-lapse frames of one experiment never sit in two splits. train 969 img / 6,026 boxes; val 278 / 2,092;
test 254 / 1,563 (held out: never used for training or selection). File lists: `data/splits/*.txt`, summary:
`data/splits/split_summary.json`.

## Layout
- `t3det/prepare.py` split + YOLO export · `t3det/train.py` training · `t3det/evaluate.py` metrics.json
- `t3det/detector.py` C5 → `FrameDetections` · `t3det/infer.py` inference pipeline (tiling/TTA knobs)
- `t3det/flux.py` C6 ByteTrack + line crossing → `FluxEstimate` · `t3det/synth.py` SYNTHETIC flux sequence
- `t3det/mps_patch.py` workaround for MPS indexing bugs in ultralytics' label assigner (runs it on CPU)
- `autoresearch/` ratchet (program.md, frozen eval.py, results.tsv) · `tests/` contract tests · `results/` outputs

## Assumptions (overnight, no user input)
- A1 Compute: the shared M5 was swapping (45.7/47 GB swap used; ~8 s/iteration for YOLO11n at batch 8), so the baseline
  is trained for a 0.35 h wall-clock budget, with warmup 0.3 epoch, mosaic off (fewer JPEG decodes per batch) and no per-epoch
  validation (the last epoch is the model). These are compute-forced deviations from ultralytics defaults.
- A2 Label: TUD-GV has a single class `litter` (not plastic-only). We report it as "floating litter"; plastic share is
  a downstream composition assumption (C6 mass factor).
