# Results — C6 v0.2 pre-registered test (registered 2026-10-04 14:00 IST in `c6_v02.md`)

- **Run:** 2026-10-04 14:03 IST (registration pushed at 14:00 IST as `9a092e9`, before the run). Commands exactly as registered; no code changes, no other seeds.
- **Data:** SYNTHETIC simulator worlds, seeds 10–19. Raw: `eval/results/c6_v02_prereg.json`; analysis: `eval/results/c6_v02_prereg_analysis.json` (from `eval/prereg_c6_v02_analysis.py`).

| Test | Mean paired difference (normalised value) | 95% CI | one-sided p | Seeds positive | Verdict |
|---|---|---|---|---|---|
| **H1** challenger_who − rule | +0.079 | +0.058 to +0.100 | 6.3 × 10⁻⁶ | 10/10 | **PASS** |
| **H2** rule − best_arm_only | +0.092 | +0.053 to +0.132 | 2.5 × 10⁻⁴ | 10/10 | **PASS** |
| S1 rule − status_quo | +0.346 | +0.216 to +0.475 | — | 9/10 | descriptive |
| S2 challenger (model picks arm) − rule | +0.026 | −0.015 to +0.066 | 0.093 | 7/10 | descriptive |
| S3 gated − rule | 0.000 | — | — | 0/10 | gate passed in **0 of 10** seeds |

Policy means ± s.d. over the 10 seeds: random 0.000 · status_quo 0.035 ± 0.009 · risk_bc −0.056 ± 0.014 · best_arm_only 0.288 ± 0.138 · **rule 0.380 ± 0.187** · uplift_v01 0.303 ± 0.058 · challenger 0.406 ± 0.162 · **challenger_who 0.459 ± 0.191** · gated 0.380 ± 0.187 · oracle 1.000.

**Honest reading.**
1. Within these SYNTHETIC worlds — where effects are heterogeneous by our own assumptions — letting the model choose *whom* to upgrade (with the arm fixed by the transparent rule) beats the lottery, in every world. Letting the model also choose *which* arm does not reliably help (S2), consistent with the Hillstrom real-RCT check.
2. **The gate never deployed the challenger** (0/10): about 850 validation persons per world is too few to detect a +0.08 gain with a one-sided 90% bound. In these worlds the deployed system therefore *is* the transparent rule. The challenger's gain is realised only with a larger pilot validation set — a pilot-sizing requirement, not a free win.
3. **Small pilots break arm ranking:** in 2 of 10 worlds (seeds 12 and 15) the pilot picked the wrong stage-1 arm and the rule captured ≤ 0.08. Pilot size per arm is therefore a first-order design input.

**Consequence for the documents (per the registered decision rule):** the default stays the transparent rule; the model is a gated challenger. Documents may state H1 with its CI, labelled SYNTHETIC, together with points 2 and 3.

## Dated note — 2026-10-04 15:12 IST (code review, issue 1)
The registered numbers above are reproduced exactly by the gpt-6-sol review, but in seeds 12 and 15 the stage-1 arm cost more than the per-person budget, the rule made no upgrades, and `challenger_who` differed from the rule only by choosing stage-1 recipients by model score — not the "same stage 1, model chooses whom to upgrade" policy described in `c6_v02.md`. H1's interpretation is therefore qualified for those two seeds. The corrected test is `c6_v03.md` (results `c6_v03_results.md`). Registered text above is unchanged.
