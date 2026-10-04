# Recorded fallback (use if the live demo fails)

- **`p6_demo_standalone.html`**: the whole page in one file, with data, styles and code inlined. Open it in any browser, offline.
  - It opens in the stage view; the badge reads **OFFLINE · exported grid**.
  - The race still works: reaction times snap to the exported 100 ms–2 s grid, and the machine is simulated at the walk-forward's 7 µs allowance. The "×" ratio is against the committed 6.08 µs p50.
  - Regenerate it with `.venv/bin/python -m demo.make_fallback`.
- **`p6_demo_walkthrough.mp4`**: a 20 s recording of the live page on this Mac (1440×900 viewport, scaled to 1280 px, 5 fps), in the stage view:
  - step 1: the replay at 0.1×, then a latency sweep 10 µs → 5 ms and the strict toggle;
  - step 2: a race;
  - step 3: the evidence.
- **Screenshots**, 1440×900:

  | file | shows |
  |---|---|
  | `01_stage1_replay_knob.jpg` | step 1, LIVE, δ = 1 ms |
  | `02_stage1_5ms.jpg` | step 1 at 5 ms: the window is −$5.17 for the threshold while the full day is +$249 |
  | `03_stage1_strict.jpg` | step 1 with strict V1 fills |
  | `04_stage2_flash.jpg`, `05_stage2_result.jpg` | a race at the named race setup: frozen · 1 bp/leg · δ 1 ms |
  | `06_stage3_evidence.jpg` | step 3: frontier and evidence cards |
  | `07_dashboard.jpg` | the full Q&A dashboard |
  | `08_backend_lost.jpg` | after the backend was stopped: every label says exported grid / backend lost |
  | `09_offline_standalone_race.jpg` | the standalone file with no backend, after a race |

**About the races in these recordings:** no human played. The browser driver (Playwright) pressed Space about 300 ms after each flash, plus its own screenshot overhead. Every race frame and race screenshot carries a banner saying so.

The live decision-step p50 in the frames was measured on a shared, loaded machine at recording time. The committed figure is 6.1 µs (`eval/results/decision_timing.md`).

The frames were captured with Playwright screenshots, the banner drawn with Pillow (JPEG quality 82), and the video encoded with ffmpeg (H.264, CRF 30). These are one-off tools that the demo does not need at run time.
