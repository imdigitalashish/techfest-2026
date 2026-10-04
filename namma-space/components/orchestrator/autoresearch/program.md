# Spike D′ — quality-qualified capture→twin turnaround (ratchet program)

**Goal:** maximise S_T = mean over trials of 𝟙[accepted] · max(0, 1 − T / 90 min).
- **T:** wall-clock minutes from the start of capture to a deployed URL, including retries and human steps (stopwatch + `report.json` stage timings).
- **Accepted:** all required rooms/doorways present in the twin (checklist), scale error ≤3% (ArUco marker vs tape), held-out PSNR ≥ threshold. The threshold is frozen after the first home capture: first-run PSNR − 0.5 dB. A failed trial scores 0.

**Trials:**
- (a) the user's home rehearsal captures;
- (b) public-scene dry runs for processing-only time (T excludes capture; labelled as such);
- (c) a Day-1 rehearsal on a new venue before the finals.

**Editable:** ingest (frame selection), posing (matcher/mapper, feature budget), splat (steps, max splats, resolution, Brush build), per-clip streaming, deploy. Contracts must not change.

**Baseline (drjohnson, processing only, shared M5):** ingest 9.9 s · own SfM 360 s (SIFT on CPU 219 s) · Brush 15k steps ≈37 min — see `.data/work/drjohnson_e2e/report.json` and the thought-node Log.

**Backlog:**
- Brush from `main` (unreleased Mip-Splatting, 4× memory cut, +10–15% speed per `research/sota-reconstruction.md`);
- fewer steps with an early-stop on held-out PSNR;
- `max_image_size` 1600 → 1024 for SIFT;
- sequential overlap 20 → 10 + loop detection;
- MapAnything (Apache-2.0) posing once MPS is verified;
- per-clip parallel SfM, merged by overlap;
- upload-while-capturing;
- an on-site QA report (blur, coverage, registration) in <2 min after each clip.
