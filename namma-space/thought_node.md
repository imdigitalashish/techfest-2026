# Namma Space · Phone capture to 3D indoor twin with search and navigation — Thought Node

> Journal for `namma-space/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 0 — Brief (not started)
- **Plan:** _(lead fills)_
- **Doing:** _(what, and which agents/sessions)_
- **Next:** _(ordered)_
- **Needs from user:** Register by 15 Oct. Capture an indoor space (e.g. home) with your phone following `deliverables/capture-sop.md` once published, and note your phone model (LiDAR or not).
- **Risks:** _(lead fills)_

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Namma Space — Techfest IIT Bombay. Teams that complete the full pipeline including AR navigation are considered for full-time roles at Juspay. Prize pool ₹1,50,000 (top 3).
- **Official statement:** [`_briefs/namma-space.pdf`](../_briefs/namma-space.pdf) (text: [`_briefs/namma-space.txt`](../_briefs/namma-space.txt)).
- **Challenge (verbatim):** "How would you design and build a complete software pipeline that turns ordinary smartphone photos or videos of an indoor space into an interactive 3D web application: one that lets remote users freely explore the space in first person, search for a specific room or item and jump straight to it, and see the best walking path to reach it around real physical obstacles?"
- **Required pipeline:** (1) our own capture SOP + automatic 3D reconstruction — no manual 3D modelling; any market technology allowed if credited; (2) zero-install web walkthrough with smooth first-person WASD + mouse movement; (3) POI tagging — click rooms or zones to see their names; (4) desktop navigation (mandatory) — optimal walkable paths that stay on the floor and avoid obstacles; (5) bonus — mobile AR navigation through the live camera, updating as the user walks.
- **Round 1 — due 31 Oct:** Drive folder with a ≤5-page technical abstract (architecture, pipeline, SOP, approach), a working free-roam web-viewer link for our own mapped space, a 3–5 min demo video, and the code repo (setup steps + sample data in a test directory). Judged on SOP & pipeline soundness, visual quality & fidelity, web-viewer performance, documentation & video clarity. Results 10 Nov.
- **Round 2 — due 30 Nov (finish by 17 Nov because of exams):** POI labelling, spatial search, obstacle-aware desktop pathfinding; live web app + 3–5 min video. Judged on spatial indexing & POI tagging, pathfinding accuracy, search UI & transitions, code cleanliness & repo setup. Finalists 7 Dec.
- **Round 3 — 16–17 Dec at IIT Bombay:** Day 1: capture a newly assigned campus venue (e.g. the Lecture Hall Complex), reconstruct, annotate POIs and deploy within the time limit. Day 2: 10-min live pitch + demo and 5-min technical Q&A. Scoring: SOP execution & capture 20% · reconstruction & visual quality 20% · web viewer & UX 20% · spatial search & path calculation 20% · pitch & Q&A 20% · on-site AR navigation bonus 10%.
- **Rules:** students, team ≤4 (cross-institute allowed); original work; open-source with licence compliance and credit in the abstract; extra links organised in one master PDF/Doc inside the Drive folder.
- **Round-1 deliverable for the morning package:** `deliverables/capture-sop.md` (so the user can capture) + `deliverables/round1-abstract.md` (draft) + the pipeline proven end-to-end on a public indoor dataset.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Capture apps: Polycam, Scaniverse, Luma (credit if used). Reconstruction: COLMAP / GLOMAP; feed-forward models (DUSt3R, MASt3R, VGGT and newer); 3D Gaussian Splatting (gsplat, nerfstudio splatfacto; OpenSplat and Brush run on Apple silicon).
- Web viewers: Spark (World Labs), PlayCanvas SuperSplat, GaussianSplats3D.
- Geometry for navigation: 2DGS / PGSR or TSDF meshing → floor plane + occupancy → navmesh (Recast/Detour via recast-navigation-js) + A*.
- Semantic POIs: open-vocabulary 3D segmentation (LangSplat, Gaussian Grouping, CLIP features). AR: WebXR, visual relocalisation (hloc), ARKit/ARCore.
- Day-1 on-site turnaround makes pipeline speed and automation critical. What companies ship: indoor digital-twin and 3D-capture products (e.g. Matterport, Polycam, Niantic, World Labs).

## Key decisions
- _(none yet)_

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (portfolio prioritisation). Score each 1–5 with one line of evidence._
- **Winnability:**
- **Innovation headroom** (the spike, and why it beats the obvious baseline):
- **Feasibility by the deadline** on an M5 Mac (+ Azure), around the 19–25 Nov exams:
- **Demo strength** at the finals:
- **Fit with the user's strengths** (large-scale systems, frontier models):
- **Biggest risk:**
- **One-line pitch:**

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.
