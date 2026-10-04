# C5 — Measurement assurance (Spike 2)

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Calibrate teacher-administered results with a small rotating re-test sample with known inclusion probabilities; block estimates with intervals.

**State of the art / what is deployed.** Deployed verification is brute force or pass/fail: Haryana Saksham Ghoshna third-party test in all 119 blocks; Gujarat Gunotsav external evaluation of ~9,000 schools (25 % per block); UP NIPUN RFP with audit subsamples; Assam Gunotsav sample-checks (`sources/methods-sae-audit.md`). MP Pratibha Parv audit: teacher-graded census tests misled (Singh, RISE WP). Methods: Horvitz–Thompson / GREG, risk-limiting audits (SHANGRLA, ALPHA), IRS random + risk audits. Bounded novelty check found no prior combination (UNVERIFIED globally).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Uncertainty/decision-value sampling with a random floor; rotation each term | 4·4·4·5·3 |
| Model-assisted (GREG) bias correction using forensic features as auxiliaries | 4·4·4·5·3 |
| Sequential (RLA-style) verification of threshold claims, e.g. 'block ≥ 80 % NIPUN' | 4·5·3·4·4 |

**Status.** Implemented and **pre-registered**: `components/trust_audit/assurance.py`; test `eval/preregistration/2026-10-04-coverage.md`. Held-out seeds 101–130 (180 blocks, SYNTHETIC): coverage 0.967 of nominal 90 % intervals (conservative), ±6.0 pp, block MAE 2.16 vs 4.31 pp raw; budget curve ±8.3 / ±6.0 / ±4.2 pp at 5 / 10 / 20 %; detection AUC 0.777. Novelty check: adaptation/combination of moderation, back-checks, misclassification correction and SAE (`research/sources/novelty-check-measurement-assurance.md`).

**Isolated metric.** Block MAE (pp) at a 10 % budget (frozen: `components/trust_audit/autoresearch/eval.py`).
