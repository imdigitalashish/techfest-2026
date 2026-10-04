# Recorded fallback (use if the live demo fails)

- `p6_demo_standalone.html` is the whole page in one file: data, styles and code inlined. Open it in any browser, offline; the badge reads **OFFLINE**. The race still works: reaction times are snapped to the exported 100 ms–2 s grid, and the machine row is labelled with the committed p50. Regenerate it with `.venv/bin/python -m demo.make_fallback`.
- `p6_demo_walkthrough.mp4` is a 21 s screen recording of the live page on this Mac at 1440×1000, 5 fps: the replay at 0.1×, a latency sweep from 10 µs to 100 ms, a race, then the strict toggle.
- Screenshots:
  - `01_overview.jpg`: live, δ = 1 ms;
  - `02_knob_5ms.jpg`: counters and frontier at 5 ms;
  - `03_race_flash.jpg`, `03_race_result.jpg`: a race;
  - `04_strict.jpg`: strict V1;
  - `05_offline_standalone.jpg`: standalone file, backend off.

**About the race in these recordings:** the browser driver (Playwright) pressed Space 250–350 ms after each flash, plus its own screenshot overhead; no human played. The live decision-step p50 in the frames (3–11 µs) was measured on a shared, loaded machine at recording time. The committed figure is 6.1 µs (`eval/results/decision_timing.md`).

The frames were captured with Playwright screenshots, encoded with Pillow (JPEG q82) and ffmpeg (H.264, CRF 30). These are one-off tools that the demo does not need at run time.
