# C12 — Governance, consent & access

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Purpose-bound, role-scoped access; pseudonyms; small-cell suppression; school-level moderation data only for the moderation team.

**State of the art / what is deployed.** DPDP Act 2023 on disk (`.data/dpdp_act.txt`); DPDP Rules and NDEAR details UNVERIFIED (governance research agent failed; re-run before 12 Oct). NIPUN requires child-wise IT monitoring within NDEAR standards (NIPUN document p. 29).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Table-driven policy engine with a test suite (100 % pass required) | 4·2·5·5·3 |
| Differential privacy for published block tables | 3·3·3·4·2 |

**Status.** Implemented: `components/governance/` — 36/36 policy tests pass (`python3 components/governance/evaluate.py`); ADR 001 rule for school-level trust data being added.

**Isolated metric.** Policy test-suite pass rate; published cells with n < 10 (must be 0).
