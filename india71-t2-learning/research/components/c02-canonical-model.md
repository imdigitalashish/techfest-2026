# C2 — Canonical model & identity

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** One schema for every source; pseudonymise PEN/APAAR at the boundary; UDISE+ codes for schools, LGD codes for geography.

**State of the art / what is deployed.** Ed-Fi / CEDS-style entity models (UNVERIFIED in our sources — governance research agent failed; re-run before 12 Oct); UDISE+ assigns a unique educational ID per student (UDISE+ 2024-25 p. 10).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Salted SHA-256 pseudonyms (`ps_<16 hex>`) with salt held by the state | 4·2·5·5·3 |
| Probabilistic record linkage for children missing IDs (name/age/school/grade) | 3·2·4·4·2 |
| Conflict log: UDISE+ wins for master data | 3·1·5·4·1 |

**Status.** Implemented: `components/canonical/` (pseudonymise + mappers; contract tests).

**Isolated metric.** Contract-validation pass rate; linkage F1 on perturbed synthetic IDs.
