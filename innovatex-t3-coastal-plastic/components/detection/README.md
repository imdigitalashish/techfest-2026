# C5 vision detector + C6 flux counter (Theme 3, coastal plastic)

Owner: child session "T3 detection + flux". Contracts: `../../architecture/contracts/contracts.py`
(`FrameDetections` for C5, `FluxEstimate` for C6). Research note: `../../research/components/detection.md`.

## Results (2026-10-04, overnight run)
All numbers are from committed code; reproduce commands are in each JSON file. **The trained YOLO11n baseline did not
finish overnight** (A1: the shared M5 was thrashing and the trainer could not complete one batch in 11 minutes). The
numbers below are therefore a **ZERO-SHOT, class-agnostic** reference: COCO-pretrained YOLO11n, no TUD-GV training.

| What | Split | Result | File |
|---|---|---|---|
| C5 zero-shot (COCO YOLO11n, class-agnostic) | TUD-GV **test** (254 img, 1,563 boxes, held out) | **mAP50 0.394 · mAP50-95 0.209 · P 0.756 / R 0.140 @ score≥0.25** · 1,087 ms/img median on the thrashing M5 (upper bound) | `results/metrics.json` |
| same, frozen `eval.py` | Groningen cross-site (63 img) | mAP50 0.405 (boot SE 0.026) · R@0.25 0.010 | `results/zeroshot_groningen_eval.json` |
| C6 flux, zero-shot detector + ByteTrack + line | **SYNTHETIC** seq02 (120 frames, 12 crossings) | counted 3 of 12 → **count error 75%** | `results/flux_synthetic.json` |
| Autoresearch ratchet | val | not run (compute); harness ready | `autoresearch/` |

Reading: the zero-shot model ranks litter-like boxes reasonably (mAP50 ≈ 0.39, from very low-score detections), but at
an operational threshold it finds only 14% of items. That is why the counter misses 75%. **Fine-tuning is required**:
the training command below is ready; on an idle machine or Azure it takes about 1 h.

## Dataset
**TUD-GV floating-litter subset** — Jia, de Vries, Kapelan, van Emmerik, Taormina (2024), *Detecting floating litter in
freshwater bodies with semi-supervised deep learning*, Water Research 266:122405, doi:10.1016/j.watres.2024.122405.
Data: https://doi.org/10.5281/zenodo.13730228 (CC BY 4.0; opened 2026-10-04). 1,501 RGB images (1920x1080) from 30
experiments at TU Delft Green Village; 8,181 boxes; one class, `litter`. Boxes are small: median box = 0.22% of the frame.
Cross-site set: **Groningen** canal (same paper), https://doi.org/10.5281/zenodo.13730384 (CC BY 4.0): 63 images (2592x1944),
383 boxes, security camera on a bridge 4 m above the canal. Neither needs credentials.

```bash
# from innovatex-t3-coastal-plastic/  (~850 MB into .data/, gitignored)
bash components/detection/data/fetch_data.sh
cd components/detection && python3.11 -m t3det.prepare      # resize to <=1280 px, YOLO export, splits
```
Checked and not used (2026-10-04): FloW-Img (ICCV 2021) needs an application on orca-tech.cn (see
github.com/ORCA-Uboat/FloW-Dataset README). HF `gonzz2026/A-dataset-of-images-of-floating-rubbish-on-the-surface-of-the-water`
is a 3.2 GB zip with no documented annotation format. TACO is not on water.

**Split.** No official split is published. We group by experiment id (`expNN_`) with seed 42, ~70/15/15 by image count,
so near-duplicate time-lapse frames of one experiment never land in two splits.
train 969 images / 6,026 boxes · val 278 / 2,092 · **test 254 / 1,563 (held out: never used for training or selection)**.
Lists are in `data/splits/*.txt` and the summary in `data/splits/split_summary.json`; `tests/` asserts the splits are disjoint
and grouped. Groningen (63 images) is a cross-site test and is never trained on.

## How to reproduce
```bash
cd innovatex-t3-coastal-plastic/components/detection
python3.11 -m t3det.train --model yolo11n.pt --imgsz 640 --epochs 40 --time 0.28 --batch 8 \
    --name baseline_yolo11n_640 --hyp warmup_epochs=0.3 mosaic=0 val=False
bash run_after_train.sh A ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt   # metrics, samples, flux
bash run_after_train.sh B ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt   # autoresearch ratchet
python3.11 -m pytest -q tests                                                                # contract tests
```
`yolo11n.pt` is fetched from `https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt` into
`.data/detection/weights/`. Weights are never committed.

## Layout
| Path | What |
|---|---|
| `t3det/prepare.py` | grouped split + YOLO export (Groningen = cross-site set) |
| `t3det/train.py` | YOLO training (MPS, seed 42) |
| `t3det/evaluate.py` | `results/metrics.json`: mAP50, mAP50-95, P, R, per-class AP, MPS latency |
| `t3det/detector.py` | **C5**: image → `FrameDetections` |
| `t3det/infer.py` | C5 inference pipeline knobs (test-time size, SAHI-style tiling, TTA, NMS): the ratchet's search space |
| `t3det/flux.py` | **C6**: ByteTrack (ultralytics) + line crossing (one count per track id) → `FluxEstimate`; mass model |
| `t3det/synth.py`, `t3det/run_flux.py` | SYNTHETIC sequence with known crossings, and the count-error evaluation |
| `t3det/samples.py` | `results/sample_detections.json` + `results/samples/*.jpg` (green = truth, red = prediction) |
| `t3det/mps_patch.py` | runs ultralytics' label assigner on CPU (MPS indexing bugs, see A3) |
| `autoresearch/` | `program.md`, FROZEN `eval.py`, `ratchet.py`, `candidates.json`, `config.json`, `results.tsv` |
| `tests/test_contracts.py` | pydantic contract tests for every output file + flux logic tests |

## C6 flux counter
Per frame, ultralytics `model.track(..., tracker="bytetrack.yaml", persist=True)`; a track is counted once, when its
box centre changes side of the counting line (optional direction filter). Mass = items × **19 g/item** (sd 37 g) with
CI90 = n·μ ± 1.645·σ·√n. Factor: van Emmerik et al. 2019, Sci. Rep. (Saigon River), PMC6753078 (opened 2026-10-04):
"each visually counted particle equals on average 1.9 × 10⁻² kg (σ = 3.7 × 10⁻² kg)" of plastic in the upper 0.5 m.
Net-sampled items alone average 1.0 × 10⁻² kg (σ 3.3 × 10⁻², N = 3057). **ASSUMPTION:** this Saigon factor is transferred
to Mumbai nullahs. Evaluation is on a **SYNTHETIC** sequence: real litter crops from the held-out test split drift
left→right across a real TUD-GV water frame (litter inpainted out), with exact ground-truth crossings; metric = count error %.

## Assumptions and caveats (overnight, no user input)
- **A1 Compute.** The shared M5 was thrashing during the run (swap 42–47 GB of 43–48 GB, load average up to ~89 on 10 cores;
  YOLO11n managed ~1 it/s at best and often stalled for minutes). The baseline therefore had a **0.28 h wall-clock budget**,
  warmup 0.3 epoch, mosaic off and no per-epoch validation (the last epoch is the model). It is **under-trained**: the
  numbers are a floor, not what YOLO11n can reach on this data. Retrain with `--time 1` (or `--epochs 50`, defaults)
  on an idle machine.
- **A2 Classes.** TUD-GV has a single class, `litter` (not plastic-only). `by_label` is `{"litter": n}`; plastic share and
  item type (film vs bottle) are downstream assumptions until a multi-class set (e.g. WADE) is added.
- **A3 MPS bug.** With torch 2.10 + ultralytics 8.4.12 on MPS, the task-aligned assigner crashed ("shape mismatch ...
  [1436] vs [1562]", then "index 192 is out of bounds"). `t3det/mps_patch.py` runs only that no-grad assignment on CPU;
  the maths is ultralytics' own `_forward`.
- **A4 Font check.** Under load, matplotlib's macOS font scan failed inside ultralytics' dataset check
  (`KeyError: '_items'`). `t3det/__init__.py` points `YOLO_CONFIG_DIR` to `.cache/ultralytics/` holding Arial.ttf.
- **A5 Latency** is end-to-end `predict()` time per image at batch 1 on the shared, loaded M5, so it is an upper bound.
- **A6 Ratchet noise floor**: keep only if Δ val mAP50 > max(0.01, bootstrap SE) (see `autoresearch/program.md`).
