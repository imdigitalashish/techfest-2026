# C11 — Action ledger & outcome loop

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Log every action, link to the next diagnosis, estimate what worked (staggered roll-out).

**State of the art / what is deployed.** No deployed system found that links actions to rechecked outcomes (`sources/deployed-states-ngos.md`, pattern 1).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Staggered cluster roll-out as a built-in evaluation | 4·4·4·4·3 |
| Effect estimates feed C9 priors | 3·3·3·4·2 |

**Status.** Spec only (contract `ActionRecord`).

**Isolated metric.** Share of actions with an outcome measured within 6 weeks.
