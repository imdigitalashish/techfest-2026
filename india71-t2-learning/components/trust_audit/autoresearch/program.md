# Measurement-assurance autoresearch spike (C5 + C6)

Goal: make moderated block estimates more accurate **without losing interval coverage**, using public data and the re-test sample only.

Frozen metric (from 4 Oct 15:52 IST): `python3 components/trust_audit/autoresearch/eval.py` prints
`METRIC block_mae_pp_dev=<x>` = block MAE (pp, lower is better) of the published (`fh`) estimate on **dev seeds 1–30**, 10 % budget,
and `CONSTRAINT coverage90_dev=<c>`. A change is kept only if MAE improves beyond noise (paired over the 180 dev blocks) **and** coverage stays ≥ 0.85.

Held-out discipline: seeds 101–130 were spent by the pre-registered test (`eval/preregistration/2026-10-04-coverage.md`). Any kept change must be confirmed once on fresh seeds **201–230** (coverage ≥ 0.85, MAE not worse), and that confirmation is pre-registered before it is run.

Constraints:
- Only edit `components/trust_audit/assurance.py` and `components/trust_audit/core.py` (not `retest`, not evaluators, not tests).
- Never use hidden truth except through the simulated `retest`.
- Report negative results in `results.tsv` too.

Idea backlog:
- Allocate the re-test budget across blocks (minimum per block) instead of district-wide risk-PPS.
- Children per school vs schools per block (two-phase allocation); the 5 % budget run shows school-level estimates get too noisy for targeting.
- Covariates in the synthetic bias model that are not confounded with block performance (heaping, variance), avoiding the classroom-tool gap whose honesty is a simulator assumption.
- Studentised bootstrap intervals to reduce over-coverage (held-out coverage 0.967 at nominal 0.90).
