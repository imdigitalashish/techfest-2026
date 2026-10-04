## Selection memo
_**Final for the 12 Oct pick**, rendered from `deliverables/selection-memo.tmpl.md` + `eval/results/headline.json` by `deliverables/render.py`. Every number traces to committed results, or to the cited memo of another project (`eval/check_docs.py`). Supersedes v1 (07:35)._

**Scores (1–5), each with its evidence:**
- **Winnability — {{memo_win}}/5.**
  - The hostile cross-model judge (gpt-6-astra, max) scored the abstract **{{astra_score}}/100** before fixes (`reviews/`).
  - The entry is backed by real data with real ground truth, which is rare: on the Open Bandit Dataset, pre-registered, DR recovered the Thompson-sampling click rate within {{a2_static_dr_relerr}}.
  - A re-enacted switch shows the dashboard overstating the lift by {{a3A_overstate}} while DR's interval holds the truth.
  - Failures are disclosed (DR missed in {{dayA_dr_fail}} deploy day pairs) and handled by the overlap gate: post hoc, {{gate_obd_answered}} answered, {{gate_obd_wrong}} wrong.
- **Innovation headroom — {{memo_innov}}/5.** The parts are known (DR, Shapley attribution, ESS diagnostics, MSM bounds). The defensible novelty is the combination:
  - attributing a policy switch with a 2×2 Shapley decomposition (OPE fills the two counterfactual cells) plus the interaction term;
  - an abstention gate calibrated on simulation and tested on real truth;
  - a protocol finding: obp's static prior is not the policy that ran (propensities drifted by a median factor of {{a1_median_ratio}}).
- **Feasibility — 5/5.** Everything runs on the M5 CPU, one command per result; contract tests pass. The full OBD can be read by HTTP range requests without downloading the 413 MB zip. Nothing is gated on the user or on a GPU, and the 19–25 Nov exams are kept free.
- **Demo strength — 4/5.**
  - A waterfall ("the dashboard said {{s1_naive_pp}}; the season did it; the policy added {{s1_truth_pp}}").
  - A live verdict that can say "can't tell from these logs".
  - A Γ slider for hidden confounding.
  - Less visual than the agent or market-sim demos.
- **Fit with the user's strengths — 3/5.** Statistics and causal inference more than large-scale systems or frontier models. Bridges: the 26M-row OBD read by range requests, streaming (anytime-valid) monitoring as next work, and evaluation of LLM-generated policies as a stretch.

**Overall: {{memo_mean}}/5** (unweighted mean of the five scores).

**Honest comparison with the finished candidates** (their own final memos, read on main 4 Oct):
- **P7** (hostile judge 71/100; fit 5) is stronger on fit and demo.
- **P1** (3.40/5 hostile judge, 68/100; fit 5) and **P9** (62/100; fit 5) fit the user better.
- **P4** (2.65/5 before fixes, 53/100) is weaker.
- **P3's edge** is tight alignment with the brief's MVP and both stretch goals, demonstrated on real data with real truth, plus a pre-registered, falsifiable evaluation. Optiver judges may value that most (our hypothesis, UNVERIFIED).
- **P3's weakness** is lower fit with the user's strengths and a nuanced real-data story (OPE fails when the new policy is greedy, so the product often abstains).
- **Recommendation:** {{memo_reco}}

**Biggest risk:** a judge reads "known parts" and "abstains often" as weak. Mitigations: lead with the real-truth evaluation, show that the abstention prevents confident wrong answers, and show the protocol finding.

**One-line pitch:** "Your dashboard says the new policy lifted clicks by {{a3A_overstate}} more than it really did. We show what the policy caused, what the season did, and when the logs simply can't tell."
