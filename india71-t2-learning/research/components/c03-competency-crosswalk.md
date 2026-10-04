# C3 — Competency framework & item crosswalk

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Machine-readable NIPUN-aligned competency ladder + Q-matrix tagging every item of every instrument.

**State of the art / what is deployed.** NIPUN Lakshya Soochi: Grade 3 reads with meaning ≥ 60 wpm, numbers to 9,999, simple multiplication; Grade 2: 45–60 wpm, numbers to 999 (NIPUN launch document p. 12, `sources/official-udise-nipun.md`). Linking practice: UIS policy linking to the Global Proficiency Framework, AMPL, IEA Rosetta Stone, Harmonized Learning Outcomes (`sources/methods-sota.md`).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| ASER-style ladder as the shared spine, mapped to NIPUN goals (current proxy) | 4·2·5·4·4 |
| Policy-linking workshops (SCERT teachers) to set ladder cut-points per language | 4·3·3·3·2 |
| LLM-assisted item tagging with expert confirmation; metric = κ vs experts | 3·3·4·5·3 |

**Status.** Skeleton uses the ASER ladder (`components/competency/framework.json`); NIPUN mapping to be finalised against the Lakshya Soochi.

**Isolated metric.** Agreement (κ) with an expert Q-matrix; model-fit gain.
