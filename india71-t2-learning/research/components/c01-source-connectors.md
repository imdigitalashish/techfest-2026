# C1 — Source connectors

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Pull UDISE+, state assessment exports, classroom-tool events, PARAKH/ASER published tables; attach Provenance.

**State of the art / what is deployed.** State ETL into VSK dashboards (Gujarat VSK, ConveGenius VSK toolkit — `sources/deployed-states-ngos.md`). UDISE+ publishes student-wise records since 2022-23 (UDISE+ 2024-25 report p. 10).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Schema-on-read with quarantine + provenance on every row | 3·2·5·4·2 |
| Connector contract tests replayed against each state's export format | 3·2·5·5·2 |
| Headless-browser extraction of PARAKH/UDISE+ dashboards (SPAs; curl sees only a shell — `sources/datasets-agent-notes.md`) | 2·2·3·3·2 |

**Status.** Best practice, no spike. Quarantine-and-report rather than silent fixes.

**Isolated metric.** Share of source fields ingested losslessly (validation pass rate).
