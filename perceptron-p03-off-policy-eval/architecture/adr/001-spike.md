# ADR 001 — Spike components: the before/after Decomposer (C9) and the Robustness Certificate (C8 + C7)

- **Status:** accepted (v1, 2026-10-04 07:00 IST). To be re-reviewed by an *independent* adversarial agent once lean mode lifts. Tonight the antithesis was written by the lead, which is weaker than the PLAYBOOK asks.
- **Context:** [`../../research/landscape.md`](../../research/landscape.md), [`../components.md`](../components.md). Round-1 judging gives 20% to innovation beyond the starter baseline ("apply IPW/DR on OBD") and 15% to the rigour of the evaluation plan.

## Candidates and scores (1–5)

| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasibility by Dec | Measurability (scalar) | Demoability | Total |
|---|---|---|---|---|---|---|
| **A. C9 Decomposer**: attribute Ȳ_after − Ȳ_before to policy effect (OPE), user-mix shift and response drift | 5: it *is* MVP bullet 2, done properly | 4: closest prior art attributes *model* performance changes (arXiv:2210.10769) or forecasts future value (arXiv:2506.20417); none we found attributes a policy switch | 5 | 5: RMSE and sign accuracy of the policy-effect term against simulator truth | 5: a waterfall chart | **24** |
| **B. C8+C7 Robustness Certificate**: Δ̂ with a CI, MSM bounds joint with sampling error, tipping point Γ\*, Γ benchmarked against observed covariates | 5: covers both stretch goals | 4: the pieces exist (Kallus & Zhou 2018; Zhao et al. 2017; Dorn & Guo 2022; Chernozhukov et al. 2026); we found no joint version *for Δ* with covariate-benchmarked Γ\* (absence not proven) | 4: Hajek/IPW bounds are easy; DR-sharp bounds are harder | 4: validity and width on confounded scenarios with known Γ_true | 4 | **21** |
| C. Ratchet on the Δ-estimator (auto-research) | 3 | 3: GrowthHacker (arXiv:2511.00802) already lets LLM agents edit OPE code | 5 | 5 | 3 | 19 → **process, not spike** |
| D. Anytime-valid monitoring of Δ as logs arrive | 4 | 3: off-policy confidence sequences exist (arXiv:2102.09540, 2210.10768) | 4 | 4 | 5 | 20 → folded into B as a C7 option |
| E. Large action spaces (MIPS/OffCEM) | 2 | 2 | 3 | 4 | 2 | 13 → parked |
| F. Future-OPE under non-stationarity | 3 | 3 | 3 | 4 | 3 | 16 → parked; cited as related work |

**Decision:** spikes are **A (C9)** and **B (C8 + C7)**. Everything else uses best practice behind the contracts (obp-equivalent IPW/SNIPW/DM/DR/Switch-DR; cross-fitted reward model). The auto-research ratchet runs on **C6** (Δ-estimator RMSE on a frozen scenario bank) and later on C7 (interval score); it is process innovation, not the pitch.

## Six Thinking Hats (on A + B)
- **White (facts):** The MVP asks for IPW/DR and "a concrete case where this estimate differs from a naive before/after number". OBD has logged propensities and two concurrent logging policies (Random, BTS), so OBD alone has no before/after period. A simulator is explicitly allowed by the starter resources.
- **Red (gut):** "Your dashboard said +X%; the policy actually did −Y%" is the sentence judges will remember. A waterfall makes it visual.
- **Black (risks):** (1) On synthetic data the decomposition can look rigged. Mitigation: a semi-synthetic version on real OBD logs (inject a known drift into real clicks) and report results across a *bank* of scenarios, including ones where naive happens to be right. (2) The mix/drift split relies on a reward model (DM), so it is model-dependent. We state this and report the doubly robust policy term separately; only that term carries a CI claim. (3) MSM bounds for DR are subtle. We start with IPW/Hajek (Zhao et al. 2017) and label DR-sensitivity as stretch. (4) "Γ\*" can be misread; we benchmark it against observed covariates so it reads as "a confounder 1.8× as strong as `age`".
- **Yellow (benefits):** It answers the brief's *actual* question ("did it work, or did it just look like it?") rather than "what is V(π)". It maps 1:1 onto MVP bullet 2 and both stretch goals. CPU-only, so it is feasible around exams.
- **Green (alternatives):** use OBD timestamps for a real temporal split; an LLM-written policy as π₁ (OPE for LLM policies is active: OTROPE, arXiv:2609.36264); a trading-flavoured toy (quote-skew policy, markout reward) as a second domain for the Optiver judges; anytime-valid monitoring for a live demo.
- **Blue (process):** freeze the scenario bank and `eval.py` before any tuning; hold out a second bank; keep only ratchet wins that beat noise across seeds.

## Thesis → antithesis → synthesis
- **Thesis:** naive before/after conflates policy effect with environment change; OPE gives the missing counterfactual "old policy in the after period". Decomposing the gap and certifying the sign under sampling error and hidden confounding is the decision-grade answer.
- **Antithesis (lead-written; independent review pending):**
  - "This is just OPE plus accounting. The decomposition is an identity, and its environment term is a residual."
  - "With logged propensities there is no confounding, so stretch 2 is artificial."
  - "On a simulator you control the answer."
- **Synthesis:**
  - The identity is the point. It makes the *naive* number auditable, and only the OPE term needs identification. We report its CI and validate the residual terms against ground truth.
  - Confounding is real exactly where before/after analyses live (estimated propensities, overrides, legacy deterministic rules; Jeunen & London, arXiv:2309.04222). We exercise C8 on scenarios with *unlogged* propensities, and show it is unnecessary (Γ\* undefined) when propensities are logged.
  - Simulator scepticism is answered with a frozen bank including adversarial cases, the OBD Random→BTS protocol (real ground truth), and a semi-synthetic OBD before/after.

## First principles
1. The quantity people look at, Ȳ_after − Ȳ_before, is not identified as a causal effect: the counterfactual "π₀ during the after period" is never observed.
2. With logged, overlapping propensities it *is* identified, by importance weighting: E[(π₀/π₁)·R] over after-period logs.
3. A decision needs a sign plus error bars plus the assumptions that could flip it. Hence a CI for Δ and Γ\*.
4. The binding constraint is variance from large weights (overlap). Hence DR, shared control variates for Δ, and diagnostics (ESS, max weight) that can force an "inconclusive" verdict.

## Consequences
- C8 and C9 get research files and ratchet programs; C5, C6 and C7 baselines must exist first (walking skeleton).
- The scenario bank (C11) is the most important piece of infrastructure: frozen, versioned, with a held-out copy.

---

## Addendum v2 — 2026-10-04 13:50 IST: what the evidence changed

**Status:** accepted with changes. The independent antithesis is now delegated to a cross-model hostile judge (gpt-6-astra, max; `reviews/`), which replaces the lead-written antithesis above.

1. **C9 Decomposer → 2×2 Shapley.** The v0 policy term was the environment-first ordering (the effect in the after period). A hostile reading ("your attribution depends on order") is correct whenever policy and season interact.
   - v1 reports the Shapley policy term, the environment term and their **interaction**. OPE fills both unobserved cells. Simulated coverage is 0.95 for the Shapley term and 0.93 for the interaction (`eval/results/decomposer_review.md`).
   - On real OBD the interaction is not negligible: truth −0.36 ± 0.31 per 1,000 in the deploy direction (`eval/results/obd_slice_summary.md`).
2. **Mix term → doubly robust option.** When the reward model is misspecified along the mix-shift direction, the DM mix term is biased (+0.57 points against a true +1.79). The DR density-ratio version is unbiased (−0.01).
3. **Identification limit.** With policy-induced audience change (feedback), OPE on after-period logs identifies the *direct* effect only. In simulation the total effect exceeds it by 5.7 points at feedback 1.0. We state this as a limitation rather than claim the total effect.
4. **New spike element: the overlap gate (C10).** Real OBD showed DR intervals missing the truth when the after-policy is greedy (deploy direction, ESS/n 0.05–0.8%). The product answer is "can't tell from these logs".
   - Thresholds were calibrated on the simulator only (`eval/gate_rule.json`, frozen at commit b4e95ae).
   - Applied post hoc to OBD: no confident wrong answers, at the cost of one unnecessary abstention.
   - This turns the method's main failure mode into a visible, testable feature. It directly answers the brief's "did it work, or did it just look like it did?"
5. **Kept as is:** the MSM sensitivity layer (C8). In the hidden-override scenario it holds the truth at Γ_true in 10/10 runs and flags fragility (Γ\* = 1.25). Covariate benchmarking of Γ\* remains the next step.
