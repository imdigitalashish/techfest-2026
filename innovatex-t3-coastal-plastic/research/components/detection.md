# C5 vision detector + C6 flux counter — state of the art and innovation room

Owner: child session "T3 detection + flux". Written 2026-10-04 (overnight, short). Every source below was opened on
2026-10-04; claims are limited to what the opened page says. Our own numbers are in
`components/detection/results/` with reproduce commands.

## 1. What the field does (opened sources)

| Work | What it is | What it reports / why it matters for us |
|---|---|---|
| **FloW** — Cheng et al., ICCV 2021. [CVF open access](https://openaccess.thecvf.com/content/ICCV2021/html/Cheng_FloW_A_Dataset_and_Benchmark_for_Floating_Waste_Detection_in_ICCV_2021_paper.html), [GitHub](https://github.com/ORCA-Uboat/FloW-Dataset) | First dataset for floating waste in inland waters: FloW-Img (images) + FloW-RI (images + synchronised mm-wave radar), from unmanned surface vehicles | Abstract: small targets, strong reflections and bank-side reflections make it hard; baseline "detection accuracy is relatively low". Download needs an application on orca-tech.cn (GitHub README), so we did not use it overnight |
| **TUD-GV / Groningen** — Jia, de Vries, Kapelan, van Emmerik, Taormina, *Water Research* 266:122405 (2024). Data: [zenodo 13730228](https://doi.org/10.5281/zenodo.13730228), [zenodo 13730384](https://doi.org/10.5281/zenodo.13730384) | Semi-supervised floating-litter detection in freshwater. Fixed cameras; Groningen = security camera on a bridge 4 m up, 1 frame / 6 s | **Our training data.** The fixed-bridge-camera geometry matches a nullah-outfall deployment better than boat-mounted FloW. 1,501 + 63 labelled images, CC BY 4.0 |
| **YOLOv8-SST** — Dong, Li, He, Zhang, *PLoS One* 21(1):e0340822 (Jan 2026). [article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0340822) | YOLOv8n plus BiFormer-attention C2f, Inner-CIoU loss and the Sophia optimiser for small floating objects | On FloW-Img + WSODD + their own data: +3.1 mAP@0.5 and +5.0 mAP@0.5:0.95 over YOLOv8n. These are small architecture gains: the backbone is not the bottleneck; data and domain are |
| **WADE** — arXiv [2608.22950](https://arxiv.org/abs/2608.22950) (Aug 2026) | 2,167 images from rural Bangladesh, 13,608 boxes, 10 waste classes, with reasoning annotations; evaluates six compact VLMs (zero-shot, few-shot, fine-tuned) on detection, counting and hallucination | Closest South-Asian floating-waste benchmark, and multi-class (not just "litter"). A candidate second training set and a VLM-counting baseline |
| **PoTATO** — arXiv [2409.12659](https://arxiv.org/abs/2409.12659) (Sep 2024) | 12,380 labelled plastic bottles with polarimetric images | Polarisation can beat surface glare: a hardware lever for the glare problem (polarising filter on the camera) |
| **SAHI** — Akyon et al., arXiv [2202.06934](https://arxiv.org/abs/2202.06934) | Slicing-aided inference and fine-tuning for small objects | Our ratchet tests tiling at inference time (`t3det/infer.py`) |
| **ByteTrack** — Zhang et al., arXiv [2110.06864](https://arxiv.org/abs/2110.06864) | Associates every detection box, including low-score ones, to cut missed and fragmented tracks | Our C6 tracker (ultralytics implementation). Low-score association matters for half-submerged films |
| **YOLO-World** — Cheng et al., arXiv [2401.17270](https://arxiv.org/abs/2401.17270) | Real-time open-vocabulary YOLO | Zero-shot baseline candidate ("plastic bottle", "plastic bag"); not run overnight (compute) |
| **van Emmerik et al. 2019**, *Sci. Rep.*, "Seasonality of riverine macroplastic transport" (Saigon). [PMC6753078](https://pmc.ncbi.nlm.nih.gov/articles/PMC6753078/) | Visual counting + net sampling of floating macroplastic | Mass conversion used by C6: net-sampled items average 1.0e-2 kg (sd 3.3e-2, N = 3057); one **visually counted** item ≈ 1.9e-2 kg (sd 3.7e-2) of plastic in the upper 0.5 m. Seasonal transport varies strongly, so counts must be continuous, not campaign-based |

Not found or not opened overnight (so not claimed): FloW-Img leaderboard numbers beyond the abstract; Jia et al. 2024's
reported mAP (Elsevier page not opened).

## 2. Where the gap is for Mumbai nullahs
1. **Domain shift is the main risk, not architecture.** Public data comes from Dutch canals (TUD-GV, Groningen), Chinese
   rivers (FloW), Bangladesh (WADE) and Saigon. Mumbai nullahs have **black, anoxic water**, foam, sewage sheen and very
   **dense accumulation** behind booms. We measure the shift we can (TUD-GV test vs the Groningen cross-site set in
   `results/metrics.json`) and plan a 300–500-frame Mumbai pilot labelling set (Needs from user: a phone capture at one
   outfall).
2. **Counting ≠ detecting.** The decision-relevant quantity is items/min and kg/day crossing an outfall (C6), not mAP.
   A stable count needs a tracker that tolerates low scores (ByteTrack) and a line placed where flow is laminar.
3. **Mats and films.** At booms, litter forms mats where single-item boxes break down. Treat a dense mat as a separate
   class with **area coverage** (that is C7's fill estimate) instead of counting items. Flexible films (carry bags, MLP
   sachets) are half-submerged and low-contrast; bottles float high and are easy. Report them separately
   (`by_label` in `FluxEstimate`) once a multi-class dataset (WADE) is added.
4. **Monsoon rain and glare.** Rain streaks and specular glare cause false positives. Levers: a polarising filter
   (PoTATO), temporal consistency (a track must persist for N frames before it counts), and synthetic rain/glare
   augmentation.

## 3. Innovation candidates (for the lead's spike scoring)
| Idea | Why it could beat the baseline | How we would measure it |
|---|---|---|
| **Count-calibrated flux with uncertainty** (C6) | Detector recall < 1 under-counts. Calibrate counts with a recall model (by size, density and lighting) estimated on labelled frames; propagate it to a kg CI90 | Count error % on SYNTHETIC sequences with known truth, then a manual count at one outfall |
| Mat-aware hybrid counting | Switch from item counting to area x areal density when density exceeds a threshold | Error on dense synthetic sequences |
| Night/black-water robustness | Photometric augmentation (low-light, dark water) + IR illumination | mAP on a darkened TUD-GV test copy (synthetic) |
| Open-vocabulary prompts for rare classes | YOLO-World or compact VLMs (WADE) label sachets and thermocol without new labels | Zero-shot AP on WADE/TUD-GV |
| Edge budget | YOLO11n runs on a phone-class SoC; tiling only when density is high | ms/frame on the target device |
