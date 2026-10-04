# Results — C6 v0.3 pre-registered test (registered 2026-10-04 14:57 IST in `c6_v03.md`, pushed as `28c80bb` before the run)

- **Run:** finished 2026-10-04 15:12 IST; commands exactly as registered; no code changes, no other seeds.
- **Data:** SYNTHETIC simulator worlds, seeds 20–29, 50,000 persons, 30% pilot; Jan Dhan holders not yet in meaningful use (≈ 19,800 eligible per world); fitting on ≈ 5,900 pilot persons (≈ 1,180 per arm); gate validation ≈ 2,530. Raw: `eval/results/c6_v03_prereg.json`; analysis: `eval/results/c6_v03_prereg_analysis.json`.

| Test | Mean paired difference (share of reference gain) | 95% CI | one-sided p | Seeds positive | Verdict |
|---|---|---|---|---|---|
| **H1** challenger − rule | +0.086 | +0.057 to +0.115 | 4.1 × 10⁻⁵ | 9/10 | **PASS** |
| **H2** rule − best_arm_only | +0.161 | +0.103 to +0.219 | 7.2 × 10⁻⁵ | 10/10 | **PASS** |
| **H3** floors, budgets, holdout untouched (all 10 worlds) | — | — | — | — | **PASS** |
| S1 rule − status_quo | +0.423 | +0.397 to +0.449 | — | 10/10 | descriptive |
| S2 gated − rule | +0.008 | −0.010 to +0.026 | — | 1/10 | gate passed in **1 of 10** worlds |
| S3 challenger − rule with perfect linkage | +0.102 | +0.072 to +0.131 | — | 10/10 | descriptive |

Policy means ± s.d. (share of reference gain) and extra persons in meaningful use per world: random 0.00 (70) · status_quo 0.04 ± 0.01 (87) · risk_bc −0.08 ± 0.01 (35) · best_arm_only 0.30 ± 0.07 (202) · **rule 0.46 ± 0.03 (272)** · **challenger 0.55 ± 0.07 (310)** · gated 0.47 ± 0.04 (276) · reference 1.00 (508).

**Honest reading.** (1) With the review fixes in place — identical plans except whom to upgrade, bank-observable proxies with error, a PMJDY cohort, women's floors and a holdout — letting the model choose *whom* to upgrade beats the lottery in 9 of 10 worlds (the exception, seed 23, upgraded to the incentive arm, where the model had little to add). (2) The gate certified the gain in only 1 of 10 worlds, so the deployed system is still mostly the rule; certifying the challenger needs a larger held-out pilot. (3) The cheapest-arm-not-harmful stage 1 removed the collapses seen in v0.2 (rule s.d. 0.03 vs 0.19). (4) All of this is a property of a simulator whose effects we assumed; field evidence requires the randomised pilot in the roadmap.
