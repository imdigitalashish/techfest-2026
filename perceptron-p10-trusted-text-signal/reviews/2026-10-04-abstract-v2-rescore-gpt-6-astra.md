# P10 final abstract v2: rescore

GPT-6 Astra, 4 October 2026. Reviewed main snapshot `adb5d6b`, abstract commit `6720ba9`. Read-only source/result audit; no model reruns. The rendered abstract matches its template/results and has 888 body words. Paths below are project-relative.

## Scores

Same official Round-1 rubric and 1--5 scale as the first review; execution is evidence of feasibility, not a separate scoring category.

| Criterion | Weight | Score / 5 | Justification |
|---|---:|---:|---|
| Problem understanding and relevance | 20% | 4 | Clearly separates weak text, distribution shift and manipulation; both MVP requirements remain explicit. |
| Technical soundness and feasibility | 25% | 4 | Fixed-offset containment and ACI are correctly distinguished; bounded-domain numerics and the named stack make the plan credible. |
| Innovation / novelty | 20% | 3 | Useful document-budget specialization, with regression precedents acknowledged; the broader mechanism is established. |
| Clarity and structure | 10% | 4 | Concrete and appropriately qualified within the word budget; one new reproduction overstatement remains. |
| Impact and evaluation rigor | 15% | 4 | Preregistered comparison, exploratory labels, sensitivity controls and a price-only fallback make the plan falsifiable; practical text value remains unshown. |
| Team fit and readiness | 10% | 3 | Solo-capable scope and correct deadlines are credible; relevant statistical/finance skills and additional members remain underspecified. |

**Weighted total: 3.70/5 = 74/100**, up from 64/100. Now a plausible shortlist contender, not a confident selection across all ten problems. The gain reflects sounder claims and a better evaluation plan, not evidence of trading alpha.

## Former BLOCKING items

Original issue numbers retained.

| Item | Status | Reason |
|---|---|---|
| #1 Adaptive guarantee | RESOLVED | Abstract and current Guarantee section restrict containment to shared offsets, distinguish daily ACI coverage and explicitly disclaim separately adapted nesting. |
| #3 Leakage absolutes | RESOLVED | The statistic is now a timestamp-alignment check; encoder contamination is explicitly not excluded. |
| #4 Submission readiness | RESOLVED | Registration/submission dates are correct, and the plan explicitly does not depend on unconfirmed teammates. |
| #6 Numerical certification gap | RESOLVED | For the documented bounded-score domain, `certify.py` replaces fixed EPS with centered sums, a cardinality-dependent roundoff allowance and an enforced million-document cap; high-count regression cases are present. |
| #7 False infinity endpoint | RESOLVED | Price-only is now a separately trained zero-exposure alternative, not the limit of the fusion deletion envelope. |

## NEW blocking issue

**N1 -- Independent reproduction is claimed for the wrong version.** `deliverables/round1-abstract.md` says an independent reviewer reproduced "every headline number exactly." `reviews/2026-10-04-code-and-eval-gpt-6-sol.md` reproduces **v1** non-timing results, not all v2 headlines. The v2 clean CR-ACI width increase is **0.44017%**, versus independently reproduced v1's **0.33191%**; the beyond-budget and positive-control results are new. Even the v1 runtime did not reproduce exactly. `deliverables/render.py` itself correctly records the v1 scope.

Minimal replacement: **"The v1 non-timing results were independently reproduced; v2 changes are recorded."** This is a provenance correction, not evidence that v2 results are wrong; it requires no new compute.

**Disposition: 0 unresolved former blockers; 1 new blocking claim correction.**
