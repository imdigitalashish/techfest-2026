# Round-1 demo video — script v1 (target 4:30, hard limit 3–5 min)

**Goal:** show the four judged criteria in order — (1) SOP & pipeline soundness, (2) visual quality & fidelity, (3) web-viewer performance, (4) clarity — on **our own home**, with real numbers on screen.
**Record:**
- Phone footage: the capture itself (a second phone or a tripod films the person capturing).
- Screen: QuickTime screen recording at 1080p60. Chrome full screen, viewer HUD visible (fps / p95).
- Terminal: large font.
- Voice-over recorded separately; captions burned in.
**Rule:** every number shown must come from `report.json` / `eval/results/*.json` of the same run. No mock-ups.

| Time | Shot (what is on screen) | Narration (voice-over) | On-screen caption |
|---|---|---|---|
| 0:00–0:15 | Front door → cut to the finished twin in the browser, walking in | "This is my home — not a video, a 3D twin you can walk through in any browser. It was made from one phone video, with no 3D modelling." | Namma Space · phone video → walkable 3D twin |
| 0:15–0:35 | The brief's challenge question; the pipeline diagram (components.md mermaid) | "The challenge: turn ordinary phone captures into an interactive twin with first-person movement, search and obstacle-aware paths. Our pipeline is one command, with eight stages, each timed." | capture → ingest → SfM → 3D Gaussian Splatting → alignment → walkable map → viewer |
| 0:35–1:20 | **Capture (SOP):** marker on the floor, 4K30 HDR-off setting, AE/AF lock, slow inward loop, outward tilted loop, slow doorway crossing with a pause, saying "Kitchen" | "Capture follows our SOP. Lock exposure, film 4K with HDR off, and walk slowly. Each room gets two loops — one facing in, one tilted down so the floor and furniture legs are visible. Doorways get crossed slowly, because that's where reconstructions break. A printed marker gives true scale. Saying a room's name records a voice tag; turning it into a searchable label automatically is our Round-2 step." | SOP: 2 loops/room · slow doorways · marker = metric scale · voice tags |
| 1:20–1:55 | Terminal: `./process_capture.sh ~/capture_home home`; stage lines appear; speed-ramp; final timing table | "One command processes it. Keyframe extraction with a blur filter; camera poses with COLMAP's global SfM — <reg>% of frames registered; Gaussian splatting on the laptop GPU; then gravity, floor and metric scale; and a walkable map of the floor." | total <T> min on an Apple M5 · <reg>% frames registered · PSNR <psnr> dB (held-out) |
| 1:55–2:50 | **Viewer:** click to start, WASD walk through 2–3 rooms; look at detail (bookshelf text, a plant); walk into a wall → slide along it; HUD fps visible | "The viewer is a static web page — nothing to install. You move like in a game: WASD and the mouse. It renders <N> million Gaussians at <fps> frames per second here, and you can't walk through walls or furniture, because movement is checked against the walkable map." | zero-install · <fps> fps median · collisions on |
| 2:50–3:30 | Fidelity: side-by-side of a held-out photo vs the render from the same pose (from the eval renders) | "To keep ourselves honest, we hold out every eighth photo from splat training and compare the render with that real photo." | held-out PSNR <psnr> dB · SSIM <ssim> |
| 3:30–4:05 | Preview of Round 2: search "sofa" → the route appears on the floor around the coffee table → press G to auto-walk; minimap | "Search and navigation are already wired in. Search for the sofa, and the path stays on the floor and goes around the coffee table." | Round-2 preview: search · obstacle-aware path |
| 4:05–4:25 | Repo README + test data folder; the abstract PDF | "The source code, setup steps and sample data are in the repository, and the abstract explains the design." | github · setup.sh · process_capture.sh · test_data/ |
| 4:25–4:30 | Logo / team names | "Namma Space — walk any space from a link." | Team · Techfest 2026 × Juspay |

**Checklist before export:** captions spelled correctly · all numbers match `report.json` · audio levels −16 LUFS · 1080p H.264 · length 4:00–4:45 · no personal documents or faces visible in the twin.
