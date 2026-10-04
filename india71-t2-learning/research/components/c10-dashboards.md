# C10 — Dashboards (VSK / block / SMC)

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Same numbers at every level, always with intervals and no small cells.

**State of the art / what is deployed.** VSK dashboards (Gujarat; ConveGenius toolkit).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Static, CDN-free HTML (< 300 KB) for low bandwidth | 3·2·5·4·4 |
| SMC pictorial one-pager in the local language | 4·3·4·3·4 |

**Status.** Implemented: `components/dashboard/` → `deliverables/demo/block_dashboard.html` (8 KB).

**Isolated metric.** Share of cells passing disclosure rules (must be 100 %); page weight.
