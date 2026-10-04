# P10 abstract and spike: hostile-panel review

GPT-6 Astra, 4 October 2026. Reviewed `5744e5b` (abstract: `e314608`). Advisory; source/evidence audit, no model reruns. Paths below are project-relative. BLOCKING means resolve before submission.

## Scores

Official rubric: [`_briefs/perceptron.txt`](../../_briefs/perceptron.txt), including the plan-only Round 1 requirement.

| Criterion | Weight | Score / 5 | Justification |
|---|---:|---:|---|
| Problem understanding and relevance | 20% | 4 | Identifies weak text, drift and manipulation; explicitly maps both MVP requirements. |
| Technical soundness and feasibility | 25% | 3 | Sound real-arithmetic core, but adaptive-containment and implementation-certainty claims exceed the argument. |
| Innovation / novelty | 20% | 3 | Useful document-budget specialization, not a new general robust-conformal principle. |
| Clarity and structure | 10% | 4 | Concrete, readable 813-word body; consequential qualifications are missing. |
| Impact and evaluation rigor | 15% | 3 | Honest preregistration and useful metrics; no demonstrated advantage over rejecting text. |
| Team fit and readiness | 10% | 2 | One broad skill profile, two unknown teammates, and an ambiguous submission milestone. |

**Weighted total: 3.20/5 = 64/100.** Plausible reserve-list candidate, not a comfortable top-25--30 choice across all ten problems. Correcting the claims and strengthening the planned comparison could make it competitive; prototype completeness alone does not earn execution credit in Round 1. Competitor quality is unknown.

## Mathematics

The deletion extrema in `components/robust_conformal/certify.py` are correct in real arithmetic: mean/trimmed-mean monotonicity; count by retained size; independently sorted trust; contiguous minimum-variance subsets and prefix-plus-suffix maximum-variance subsets. Empty/singleton cases are handled. The variance-change expression in `research/components/robust_conformal.md` omits a factor `1/m`; its sign argument survives.

Coordinate extrema are exact, **not the joint feasible set or ensemble envelope**. Summing tree-wise extrema is a sound relaxation for the current numerical LightGBM configuration. Quantile crossing is handled. The previous context-dependent-trust bug is fixed. However, empirical `EPS=1e-6` is not a proved floating-point enclosure for all supported document counts and threshold comparisons.

For a **shared offset**, containment is correct, including negative offsets when inverted endpoints remain empty sets. This assumes injection only, finite features, fixed scoring/existing-document metadata and unchanged price inputs. Nominal split-CQR coverage additionally requires the usual clean, exchangeable calibration/test scores and independent fitting. The recorded 86.7% floor is retrospective on this test set, not a universal future coverage probability.

`components/conformal/methods.py` now correctly uses unclipped ACI updates and whole-line/empty-set boundaries. Its telescoping argument applies to **mean daily miscoverage**, not per-stock, per-regime or per-prediction 90% coverage. At 189 days and gamma 0.01, the stated worst-case error bound is **0.4815**, not a useful finite-horizon calibration guarantee.

Crucially, `eval/run_baselines.py` calibrates CR-ACI on certified bounds and updates attacked/clean runs separately. Their offsets and score histories differ. Same-offset containment does **not** establish containment of an independently adapted clean ACI interval, or that an attacker cannot add misses along that counterfactual trajectory.

## Novelty

The narrow application gap is plausible and appropriately hedged by "in our searches"; priority is unestablished, and R2's explicit search-log section remains pending. Primary abstracts rechecked:

- [VRCP](https://arxiv.org/abs/2405.18942): verification-based robust CP already supports regression.
- [Zargarbashi et al., ICML 2024](https://arxiv.org/abs/2407.09165): worst-case conformity-score bounds, discrete data, evasion and poisoning.
- [RCP1](https://arxiv.org/abs/2506.16553): classification and regression, procedure-level certification.
- [Text-CRS](https://arxiv.org/abs/2307.16630): certified word insertion/deletion, not this document-fusion CP task.

A reviewer will ask why this is more than robust-CP composition with a particular uncertainty set. Claim the tractable document-deletion geometry and implementation, not invention of robust coverage or verified first-in-literature status.

## Evaluation

The preregistration is credible in the committed record: `dd8bcd1` at 12:55:28 precedes result commit `a491f00`; analysis code and relevant model dependencies remain unchanged. The one-sided moving-block test matches the plan. Its null is not evidence of equivalence or that text never helps.

Day-block intervals appropriately address same-day dependence and short-range temporal dependence; pooled Kupiec/Christoffersen p-values do not. There are 189 StockNet dates, not 16,443 independent observations. Need paired score/width differences, regime/attack-day uncertainty and block-length sensitivity. The 2014-only ratchet fix is present; previous test looks still make StockNet exploratory.

The 53-variant oracle is a finite score-space stress search, not a global worst case or demonstrated raw-document attack. Burst timing is fixed, but its payload is selected using test outcomes. Robust-aggregation-only and adversarial-training comparisons are absent.

A quant's decisive question: **why retain text?** Clean CR-ACI width/Winkler are 5.237/7.534 versus price-only ACI 5.235/7.521, both covering about 89.5% (`text_minilm_v1.json`). Price-only is injection-immune. Honest reframing is convincing as a channel-admission audit, not demonstrated financial value. DJIA's acknowledged opening-price anomaly further limits deployment interpretation; sharing that feature between arms does not establish external validity.

## Claim-vs-results check

No stale rendered numeric placeholders found. Matches:

| Evidence under `eval/results/` | Abstract claims checked |
|---|---|
| `prepare_stats_minilm_v1.json` | 0/119,641 timestamp-cutoff violations; not a comprehensive leakage audit. |
| `text_scorer_isolated_v1.json` | F1 0.6914/0.4885; 20%/40% noise gives 0.6621/0.6062. |
| `text_minilm_v1.md` and `.json` | 87 stocks; stated splits; 16,443 rows; 90% target; 81.6%/76.9% split coverage; CQR 86.6%; ACI 89.5%, CI 87.5--91.2%; pinball 0.3508/0.3513. |
| Same StockNet files | 53 variants; oracle 84.7%; clean floor 86.7%; worst tested fixed attack 85.7%/89.5%; CR-ACI 89.5%/89.7%; width increases 0.3319%/0.9698%. |
| `text_utility_djia_v1.json` | 505 days; improvement 0.0034307, or 0.09736%; p=0.4629; null decision. |

The 86.6% MAPIE result and 86.7% symmetric-CQR floor are different variants, not inconsistent rounding. `baseline_v1.md` is VADER, not the abstract's MiniLM run; no improper numerical mixing found. Twelve price features and named model/MVP components match code. The 140-point incident is sourced in `research/notes/R4b-manipulation-attacks-detection.md`.

**Mismatches/qualification gaps:** `deliverables/round1-abstract.md` says "interval score +0.1%"; the DJIA score actually **decreases**, 3.52392 to 3.52049. Only DJIA has a formal text-utility test: StockNet's near-equal point estimates do not establish the two-dataset "no measurable accuracy" claim. Its "full" 59-second runtime is the cached-feature evaluator's 59.2 seconds, excluding data preparation/initial embedding. Its final-abstract milestone extends to **1 November**, whereas the official deadline is **31 October**. Mathematical and leakage absolutes are unsupported as detailed above.

## Top 10 issues

Ranked by expected score impact; **5 BLOCKING**.

1. **BLOCKING -- Adaptive guarantee.** Replace the spike's last sentence: "At the same conformal offset, every budget-compliant injection preserves clean-input coverage. ACI separately targets long-run average daily coverage; independently adapted clean and attacked runs need not be nested."
2. **NON-BLOCKING -- No admission benefit.** Preregister a paired proper-score comparison against price-only, at matched coverage, on untouched data; include a labelled synthetic useful-text positive control. State: "If text fails the admission criterion, the channel stays off."
3. **BLOCKING -- Leakage absolutes.** Replace "cannot memorise outcomes": "The sentiment head receives no return labels; pretrained-encoder temporal contamination remains unexcluded." Call 0/119,641 a timestamp-alignment check, not proof of zero look-ahead.
4. **BLOCKING -- Submission readiness.** Put registration by 15 October and abstract submission by 30 October in the schedule. Supply actual committed members/roles and relevant evidence, or explicitly scope a solo deliverable; do not invent teammates.
5. **NON-BLOCKING -- Novelty attribution.** Say: "We specialize robust conformal verification to document-injection budgets using tractable deletion ranges." Explicitly acknowledge VRCP/RCP1 regression and complete the bounded prior-art search log.
6. **BLOCKING -- Numerical certification gap.** Distinguish the real-arithmetic theorem from the empirical implementation. For an unconditional software certificate, specify input/count limits and derive conservative roundoff bounds; fixed EPS plus random brute-force cases is insufficient.
7. **BLOCKING -- False infinity endpoint.** Deleting all observed documents under a fixed fusion model does not recover a separately trained price-only model; increasing k produces an envelope. Replace with: "Price-only is a separate zero-exposure alternative, compared alongside the budget curve."
8. **NON-BLOCKING -- Inference/holdout claims.** Replace pooled significance with day-block uncertainty; label StockNet exploratory and freeze the next holdout before further selection. Write: "StockNet estimates are close; the DJIA test did not establish incremental interval-score value." Regime calibration and short-horizon protection remain evaluation goals.
9. **NON-BLOCKING -- Attack realism/comparators.** Add raw-text replay, prospectively selected concentrated attacks and actual budgets above certified k; compare with trimmed-aggregation-only and adversarial training. Keep oracle searches distinct from certificates.
10. **NON-BLOCKING -- Reporting precision.** Write "Winkler improvement +0.1%, p=0.46", "worst of 53 tested variants", and "cached StockNet evaluation: 59 s"; explicitly label symmetric CQR in the attack comparison.

---
## Lead decisions (P10 lead, 4 Oct 2026 ~14:00 IST; v2 = commit after this review)
| # | Item | Decision | What changed |
|---|---|---|---|
| 1 | Adaptive guarantee (BLOCKING) | ACCEPTED | Per-row containment is claimed only at a fixed offset. CR-ACI is claimed for long-run mean daily coverage only. Non-nesting is documented by a test (`tests/test_review_fixes.py`). Abstract, ADR, `robust_conformal.md` and the diagram are reworded. |
| 2 | No admission benefit | ACCEPTED (partly done) | Admission rule in the abstract ("if text fails, the channel stays off"). Positive control run: the test detects a +11.1% Winkler gain (p = 0.019) and misses +3.9% (p = 0.11). FNSPID pre-registration is in the plan. |
| 3 | Leakage absolutes (BLOCKING) | ACCEPTED | Now "timestamp-alignment check"; "the head receives no return labels; contamination of the pretrained encoder is not excluded". |
| 4 | Submission readiness (BLOCKING) | ACCEPTED | Milestones show registration by 15 Oct and submission by 30 Oct (deadline 31 Oct). The team line no longer invents teammates; names are a *Needs from user* item. |
| 5 | Novelty attribution | ACCEPTED (wording); search log deferred | "We specialise robust conformal verification to document-injection budgets…"; VRCP/RCP1 regression acknowledged. Completing R2's search log is due before 12 Oct. |
| 6 | Numerical certification gap (BLOCKING) | ACCEPTED | Centred sums plus a derived round-off budget, with a document cap (`MAX_DOCS`). sol's 50,003-post counterexample and random large-n cases are regression tests. |
| 7 | False k = ∞ endpoint (BLOCKING) | ACCEPTED | Price-only is described as a separate zero-exposure alternative everywhere. |
| 8 | Inference / holdout claims | ACCEPTED | StockNet is labelled exploratory; the two-dataset claim is reworded; the next holdout (FNSPID) will be pre-registered. |
| 9 | Attack realism / comparators | ACCEPTED (partly done) | Budgets beyond k added (10 posts: certified 86.9% vs plain 86.2%). Raw-text replay, trimmed-aggregation-only and adversarial-training comparators are deferred to the finals plan. Burst payloads were chosen from test outcomes; they are an attack stress test, not evidence for the certificate. |
| 10 | Reporting precision | ACCEPTED | "Winkler 3.524 → 3.520, p = 0.46"; "worst of 53 tested variants"; "cached StockNet evaluation"; symmetric CQR labelled. |
| — | Missing 1/m in the variance-change formula | ACCEPTED | Fixed in `research/components/robust_conformal.md`. |
| — | ACI worst-case bound ≈ 0.48 at T = 189 | ACCEPTED | Stated in the report and in `robust_conformal.md`. |

No item rejected.
