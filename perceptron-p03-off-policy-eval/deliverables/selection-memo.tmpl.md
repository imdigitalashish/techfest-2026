## Selection memo
_**Final for the 12 Oct pick**, rendered from `deliverables/selection-memo.tmpl.md` + `eval/results/headline.json` by `deliverables/render.py`. Every number traces to committed results, to `reviews/scores.json`, or to another project's cited memo (`eval/check_docs.py`). Supersedes v1 (07:35)._

**Scores (1–5), each with its evidence:**
- **Winnability — {{memo_win}}/5.**
  - The hostile cross-model judge (gpt-6-astra, max) scored the abstract **{{astra_score}}/100** before fixes and **{{astra_rescore}}/100** after them: "borderline, still lean no", with no blockers left (`reviews/`).
  - Strengths a judge can verify: real data with a concurrent-arm reference, pre-registration, disclosed deviations, and all 44 abstract numbers reproduced by an independent reviewer.
  - Weakness: the headline real-data improvement is modest, and on the flagship case the gate rightly withholds the decision.
- **Innovation headroom — {{memo_innov}}/5.** This is an integration, not a new estimator: Δ-OPE, Shapley shift attribution, diagnostic protocols and non-stationary OPE are prior art. The defensible additions:
  - an auditable switch-attribution protocol that says "can't tell";
  - the finding that the deployed Thompson-sampling policy drifted (median {{a1_median_ratio}}-fold) while the standard OBD protocol evaluates one static prior.
- **Feasibility — 5/5.** Everything runs on the M5 CPU, one command per result; contract tests pass. The full OBD can be read by HTTP range requests (no 413 MB download). Nothing is gated on the user or a GPU, and the 19–25 Nov exams are kept free.
- **Demo strength — 4/5.**
  - A waterfall ("the dashboard said {{s1_naive_pp}} points; the season did it; the policy added {{s1_truth_pp}}").
  - A verdict that can say "can't tell from these logs".
  - A Γ slider for hidden confounding.
  - Less visual than the agent or market-simulation demos.
- **Fit with the user's strengths — 3/5.** Statistics and causal inference more than large-scale systems or frontier models. Bridges: range-read data engineering on the 26M-row OBD, and streaming (anytime-valid) monitoring as next work.

**Overall: {{memo_mean}}/5** (unweighted mean of the five scores).

**Honest comparison with the finished candidates** (their own final memos, read on main 4 Oct):
- **P7** (hostile judge 71/100; fit 5) scores slightly higher and fits the user better.
- **P1** (hostile judge 3.40/5; fit 5) and **P9** (hostile judge 3.10/5, 62/100; fit 5) fit the user better.
- **P4** (hostile judge 2.65/5 before fixes) is weaker.
- **P3's edge:** the closest match to its brief (MVP and both stretch goals are working), with real concurrent-arm references and a pre-registered, falsifiable evaluation.
- **P3's weakness:** lower fit, and a nuanced real-data story. OPE fails when the new policy is greedy, so the tool often abstains.
- **Recommendation:** {{memo_reco}}

**Biggest risk:** a judge reads "known parts" and "abstains often" as weak. Mitigation: lead with the real-reference evaluation and with the gate preventing confident wrong answers, then show the protocol finding.

**One-line pitch:** "The dashboard said the new policy lifted clicks {{a3A_overstate}} more than the concurrent A/B showed. Our tool separates what the policy did from what the week did, and says 'can't tell' when the logs can't support an answer."
