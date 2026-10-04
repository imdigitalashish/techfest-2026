# Hostile-judge review: Round-1 abstract and AnchorLoRA spike

**Reviewer:** GPT-6 Astra, independent methodology/novelty review under PLAYBOOK section 10. **Date:** 2026-10-04. **Reviewed snapshot:** `09692c56f19082a408cb8fa0e0b75d9abb5c4d40`, after fetching and rebasing on `origin/main`. Paths and line numbers below refer to that snapshot and are project-relative unless stated otherwise.

**Verdict: 3.40/5, or 68/100.** A credible, unusually concrete Round-1 plan with a promising pilot, not yet a convincing demonstration of the proposed causal mechanism or weak-device usefulness. The principal mathematical over-claim is "unbiased under partial participation"; the principal empirical vulnerability is that a much larger bundle of interventions is compared with a differently trained starter. The combination is defensible as an engineering investigation, not as a substantial new aggregation primitive.

**Findings: 1 BLOCKING, 8 MAJOR, 3 MINOR.** BLOCKING means a claim must change before submission, not that the team must finish the finals experiments before Round 1. MAJOR includes consequential gaps in the evaluation plan; an explicitly scoped, true pilot observation is not called false merely because stronger evidence is still needed. Team-name placeholders are intentional and are not penalized.

This is a review of the **provisional** rendered abstract: Anchor/starter seeds 0,1,2; FFA-LoRA/FlexLoRA seeds 0,1. A later automatic five-seed render supersedes the numbers, not the methodological findings. I read the requested abstract/template, diagram, ADR, novelty/landscape, v1/v2 summaries, dropout analysis, manifest, earlier review and dispositions, plus the relevant trainer, simulator, aggregator and reporting paths. No implementation or deliverable was changed; no new model training was run.

## Official scoring

Weights and scale are from `../_briefs/perceptron.txt`, "Evaluation Criteria"; Round 1 judges the plan, not a finished prototype.

| Criterion | Weight | Score / 5 | One-sentence evidence |
|---|---:|---:|---|
| Problem Understanding & Relevance | 20% | 4 | It identifies heterogeneous work, availability and quantity skew, but incorrectly reduces useful weak-device participation and stability to three aggregation properties. |
| Technical Soundness & Feasibility | 25% | 3 | Shared-A delta aggregation is valid and the stack is buildable, but unbiasedness is unproved and the current masked-rank simulator does not establish the advertised resource behavior. |
| Innovation / Novelty | 20% | 3 | The system goes beyond the named starter, but freezing A, nested ranks, uniform weights and the corrections are established ingredients whose combination has not yet shown a distinctive benefit. |
| Clarity & Structure of Abstract | 10% | 4 | The 865-word body maps cleanly to the brief, although guarantee-like terminology and inconsistent current-versus-planned status obscure an otherwise concrete design. |
| Impact & Rigor of Evaluation Plan | 15% | 3 | Paired runs, per-domain results and the disclosed micro trade-off are strong, but matched-work attribution, independent factor variation and document-level generalization are not yet adequately specified. |
| Team Fit & Readiness | 10% | 4 | Three complementary ownership roles and a dated, exam-aware milestone plan are credible, with hardware deployment still a material readiness risk rather than a demonstrated capability. |
| **Weighted total** | **100%** | **3.40** | **0.80 + 0.75 + 0.60 + 0.40 + 0.45 + 0.40 = 3.40/5 = 68/100.** |

## Numbered findings, evidence and exact fixes

### 1. BLOCKING - Exact aggregation does not imply unbiased optimization or the full macro objective

**Evidence.** Abstract lines 12-16 culminate in "exact, unbiased under partial participation, balanced"; ADR first-principles item 1 says the design "turns FL theory back on." The algebra only says that a linear combination of B directions maps to the same linear combination in weight space, with a common A and consistent LoRA scaling.

`Anchor.aggregate` (`components/aggregator/strategies.py:196-258`) divides an AdamW displacement by completed steps, clips in B space, replays old directions, renormalizes over available/recent clients and multiplies by a planned-step average. These are not an unbiased estimator of the current all-device gradient. Clipping is itself nonlinear. In all three committed Anchor runs, c4's memory expires at round 9: c4 has zero weight and c0's coefficient rises from 0.20 to 0.25. No information about c4's current gradient has magically been restored.

There is a second, independent issue: **uniform client weights do not make heterogeneous coordinate masks an unbiased gradient of the full-model macro loss.** Even with one SGD step, no clipping and full participation, the direction is an average of *masked* client gradients. For B columns 9-16, only c0 is allowed to update; the other clients' losses still depend on those columns because they run the full global adapter. Their derivatives in those columns are missing. The macro loss is a sensible evaluation target, but exact optimization of that target is not established.

**Exact replacement for the sentence at abstract line 16:**

> We target affordable, useful participation, resilience to interrupted work and transparent influence. Shared A makes the chosen mixed-rank update combination exact; the participation corrections and equal-client weights are heuristics whose utility and bias require separate evaluation.

**Exact replacement for the algebra's interpretation at line 20 and in the ADR:**

> With common A and LoRA scaling, summing zero-padded B deltas exactly reproduces the corresponding weight-space sum, up to floating-point error. This remains an identity for the normalized, clipped or replayed directions we choose; it is not a guarantee of unbiased current-client averaging or convergence.

Keep "FedNova-style" and "MIFA-style"; do not transfer those methods' guarantees to this optimizer, truncation policy and finite-age memory without a separate argument.

### 2. MAJOR - The novelty distinction survives these papers, but the claimed advance is easy to dismiss as obvious

I opened the papers myself, including the following full-text sections, on 2026-10-04:

| Primary source | What the inspected method actually does | Consequence for the claim |
|---|---|---|
| [CF-LoRA, Method, Stages I-III, equations 5 and 9-12](https://arxiv.org/html/2609.36986v1#Sx3) | Learns shared A while retaining local B, clusters by B similarity, freezes learned A, then averages B within clusters; its displayed aggregation weights are already uniform within the relevant group. | Frozen-shared-A exactness and equal-client aggregation are not ours; its inspected formulation does not supply a heterogeneous-prefix-rank scheme. |
| [PreLort, sections 4.1-4.3, equations 5-7 and Algorithm 1](https://arxiv.org/html/2606.15963v1#S4) | Trains both factors under multiple prefix-rank losses, then averages factor pseudo-gradients segment by segment over the owners of each segment. | It supplies more than prefix slicing: it explicitly trains useful prefixes; it does not freeze a shared random A or make the general two-factor product average exact. |
| [FFA-LoRA, section 4, equation 4; section 5.1; appendix A.8](https://arxiv.org/html/2403.12313#S4) | Freezes initialized A, trains/aggregates B, and establishes the same linear identity; it also investigates A initialization and tunes learning rates. | FFA-LoRA is the most direct algebraic ancestor; generating its shared random initialization from a seed is not a new learning principle. |
| [FlexLoRA, section 3.2 and appendix B](https://arxiv.org/html/2402.11505#S3.SS2) | Averages heterogeneous-rank products, then uses SVD for rank-specific redistribution. | Exact mixed-rank product aggregation already exists; the trade-off is representation, communication and truncation cost. |

**Judgment.** Neither CF-LoRA nor PreLort, as inspected, describes precisely this frozen-seed-A plus B-prefix recipe. A bounded "we did not find this exact combination" statement is defensible against those two papers. Two papers and the recorded search cannot establish a universal absence claim. A skeptical professor can reasonably regard freezing one factor and zero-padding prefix deltas as an immediate composition of known ideas. That does not disqualify a hackathon system, whose innovation criterion is beyond the starter rather than publication-level priority.

Do not describe PreLort merely as the other "half." Its multi-prefix training is absent here, including in `anchor_full_seg`, which changes aggregation coefficients only. PreLort section 5.1 also samples clients each round; "neither considers participation" would be too broad. The distinction is *device-dependent availability, deadline truncation and outage handling*, not any participation at all.

"Minimal upload" is unsupported as a universal or theorem-level claim. `r_k*d_out` is this parameterization's uncompressed payload count, not a lower bound over compression, alternative parameterizations or methods. Even the pilot's homogeneous FFA baseline sends less logical uplink overall than Anchor (5.68 versus 6.59 MB/device), although their rank/work configurations differ.

**Strongest honest replacement for the novelty claim:**

> We extend FFA-LoRA's frozen-A design to prefix-masked device updates and evaluate participation handling and update-share diagnostics for one shared model. CF-LoRA learns A before freezing it for clustered B aggregation; PreLort trains both factors with a multi-prefix objective and segment-wise aggregation. Our contribution is the evaluated systems recipe and its cost/utility trade-offs, not a new exactness primitive or a minimum-communication theorem.

The decisive novelty experiment is whether this recipe improves the cost/utility frontier over a **matched-rank frozen-A control with the same weights and admitted work**. Be prepared for the honest outcome that most of the improvement comes from the participation/objective policy.

### 3. MAJOR - Active coordinates and logical upload are being allowed to stand in for actual weak-device resources

**Evidence.** Abstract line 20 says every device regenerates A, never transmits it, and its trainable parameters scale with rank. The diagram says it trains as many columns "as its memory allows." In reality, `trainer.py:44-60,80-108` creates a rank-16 PEFT module and full-sized trainable B tensors/optimizer state; it masks gradients. `Anchor.client_view` retains the full adapter. `flower_adapter/server_app.py:60-90` serializes full A and B for clients, rather than deploying seed-only A transport. The earlier review correctly identified this; the narrowed interpretation is not yet unambiguous in all deliverables.

Effective updated coordinates and the sliced uplink really do scale with `r_k`. That does **not** establish a smaller resident adapter, lower peak RAM, shorter local step or phone/Pi feasibility. The full backbone's forward/backward cost also remains. This is not a demand for physical hardware at Round 1: label what the pilot measures and make the missing implementation an explicit milestone.

The 2.5x payload ratio is valid **at matched ranks for this model's q/v adapter collection**, from 1,920 versus 768 values per rank per q/v pair. It is not a model-independent per-layer ratio, nor measured total network savings. The observed starter/Anchor total logical-uplink ratio is about 2.15x because admitted work and ranks differ. Downloads, protocol overhead and setup are excluded.

**Exact replacement for the resource assertion:**

> The pilot updates only each client's B prefix and uploads r_k*d_out fp32 values per layer; active coordinates and logical uplink, not measured RAM or throughput, scale with rank. Seed-only A transport and resource-real local adapters are finals milestones.

**Exact replacement for the cost comparison:**

> At matched ranks, this model's q/v adapters use 2.5 times fewer logical uplink values than A+B; total communication remains to be measured.

**ADR corrections:** replace "no extra server memory beyond B" with "the server also caches a recent B-direction per remembered client"; replace "nothing is padded or diluted" with "the server zero-pads deltas; non-owner directions are zero under the selected weighting policy." No dense-product SVD is needed, but aggregation and memory are not free.

### 4. MAJOR - The pilot compares systems, not the causal value of the proposed aggregation or of weak devices

**Evidence.** Recounting `eval/results/logs/v2_dropout_*_s*.json` for the three shared starter/Anchor seeds gives:

| Quantity over seeds 0,1,2 | Anchor | Starter |
|---|---:|---:|
| Fresh accepted client-rounds | 143 | 115 |
| Of those, partial client-rounds | 28 | 0 |
| Actual local optimizer steps | 1,007 | 958 |
| Additional cached-direction reuses | 32 | 0 |

The allowed schedule is paired; the actual admitted work is not equal. Accepting partial work is a legitimate systems advantage, not cheating. But the comparison also changes rank, trainable factors, weights, normalization, clipping and replay. Thus the 0.083 macro advantage cannot be attributed to frozen A, mixed ranks, replay or the 5.7% factor error separately. In v1's seed-0 dropout result, `anchor_naive` has *worse* macro loss than the starter (2.7616 versus 2.7346), despite algebraic exactness. This is particularly damaging to "exactness is why weak devices count."

The 5.7% figure itself is supported, but is a round-and-seed mean relative Frobenius residual, normalized by the intended **round delta**, not a prediction-error percentage or error relative to the whole adapter. **Exact replacement:** "The starter's mean relative round-update aggregation residual was 5.7% in this pilot; its effect on task loss is not isolated."

Likewise, lower loss on a weak device's domain is **benefit received**, not proof its updates **contributed useful information**. Other devices or merely suppressing wiki specialization could produce that improvement. Crediting a cached update again is not additional device computation.

The paper-derived baselines are reasonable implementations, but not tuned reproductions: the nominal rank-8 baselines are masked within rank 16 with effective scale `32/16 = 2`, and all use fixed AdamW learning rate 0.001. FFA-LoRA's experiments tune its learning rate separately. A global alpha-64 sensitivity alone does not establish equal-budget tuning or actual rank-8 resource behavior. The direction of any resulting bias is unknown.

**Exact addition to the pilot paragraph:**

> This is a full-system comparison under paired availability, not matched completed work; matched-work, rank-matched and leave-one-mechanism-out controls will identify which choices help.

**Exact baseline label:**

> Paper-derived baselines under one fixed optimizer/scale; budget-matched tuning is planned.

**Operational definition to add to the MVP/evaluation plan:**

> Meaningful participation means fresh updates completed within a measured device budget that improve held-out utility versus a paired run withholding that client's updates.

For that test, retain the same evaluation population, initialization, other-client schedules and capacity; specify whether weights and replay slots are held fixed. Otherwise the exclusion changes the policy as well as removing the information. Report both the client's domain and macro loss, with a predeclared practically useful effect and uncertainty; do not count replay as fresh work.

### 5. MAJOR - The influence number is a mean magnitude diagnostic, not a per-round fairness guarantee

**Evidence.** Abstract line 56 calls 0.88 to 0.22 the share "of each update," against a "fair share of 0.2." The code first averages each run's per-round shares, then averages runs. Across the 36 Anchor rounds, c0's norm share ranges from **0.1888 to 0.2880**, with mean **0.2163**. The quoted 0.22 is not a cap or a per-round value.

`product_space_report` measures normalized norms of the constructed product-space contributions, not causal benefit. For the inexact A/B baseline those contributions do not even sum exactly to the applied product update. Projection shares are a separate signed, potentially ill-conditioned diagnostic. Neither metric says whose data improved predictions.

Uniform weights do not imply equal vector norms; 0.2 is an equal-share reference for five clients, not a definition of fair outcomes. Some rounds have fewer included clients. The median clip in B space also imposes no universal product-space influence cap: with two reporters and B-direction norms 100 and 1, the upper median is 100 and a 2x threshold clips neither. With common scalar A, the larger direction has norm share `100/101`, approximately 0.9901. Only c0 owns the highest rank segment regardless of its total norm share.

The micro trade-off is correctly disclosed: Anchor minus starter is **+0.1121** nats/token, paired 95% CI **[+0.0974, +0.1268]**. Also, the raw worst-domain loss is not lower: **3.5142 versus 3.4524**, paired difference **+0.0619 [-0.0208, +0.1445]**. That is not proof of worse fairness either: raw NLLs across text domains have different baselines, and the identity of the worst domain changes. Equal-domain mean loss, worst absolute loss and equal influence are distinct goals.

**Exact replacement:**

> The data-rich client's round-and-seed mean normalized product-update norm share falls from 0.88 to 0.22. This is a magnitude diagnostic, not a fairness cap or causal influence estimate; leave-one-client-out and identity-splitting tests will assess the latter.

**Exact trade-off wording:**

> Anchor improves macro loss but worsens sample-weighted loss by 0.112 nats/token; it does not establish a worst-domain-loss improvement.

Describe sample weighting as a different objective, not intrinsically erroneous: an organization might legitimately value pooled-token performance. The brief does not uniquely mandate uniform weights.

### 6. MAJOR - Correct paired t intervals are being asked to carry more inference than this pilot supports

**Evidence.** I independently recomputed the differences and intervals from `v2_dropout.jsonl`; the arithmetic is correct:

| Anchor minus comparator, macro nats/token | Shared seeds | Mean difference | Two-sided 95% paired t interval |
|---|---|---:|---|
| Starter | 0,1,2 | -0.082662 | [-0.110929, -0.054395] |
| FFA-LoRA | 0,1 | -0.051343 | [-0.079080, -0.023606] |
| FlexLoRA | 0,1 | -0.079752 | [-0.187677, +0.028174] |

The results table's lead-in says "3 paired seeds," but two comparisons have only two pairs; the introductory team note is too easy to omit from the submission. Put shared n on each comparison. The FFA interval has one degree of freedom: it is mathematically valid under its assumptions, not convincing evidence that run variability or transfer performance is understood. FlexLoRA's interval crosses zero; do not claim a demonstrated win over it.

These are intervals for the mean over training randomness **conditional on the fixed data, allocation, hyperparameters and implementation**, with independent, approximately normal paired differences assumed. They do not quantify variation over institutions or documents. At n=2 or 3, normality/tail behavior cannot be meaningfully diagnosed. Even five same-sign paired differences have minimum two-sided sign-test p=0.0625; that observation does not invalidate a t test, but demonstrates why "five seeds" is not a distribution-free certificate.

The Bonferroni fix is correct. All five Anchor mean gains are positive, but only four five-domain simultaneous intervals exclude zero; cheaders is **+0.006887 [-0.003065, +0.016839]** after adjustment. The starter's four non-wiki gains are negative even under the same adjustment. Thus the abstract's four-domain count and pilot harm direction are supported; a claim of improvement in *every* domain with simultaneous confidence is not. Bonferroni across five domains does not cover searching methods, metrics, baselines or ratchet candidates. The pilot informed development, so designate a future untouched confirmatory evaluation rather than retroactively treating all pilot comparisons as confirmatory.

**Exact table lead-in/header replacement:**

> Exploratory 12-round SmolLM2-135M pilot on fixed text blocks; paired t intervals describe seed variability only. Shared pairs: starter n=3, FFA-LoRA n=2, FlexLoRA n=2.

**Exact domain statement:**

> On this fixed holdout, all five mean domain losses decrease; four five-domain Bonferroni-adjusted 95% seed intervals exclude zero. The starter's only positive domain gain is the data-rich one.

**Exact protocol replacement:**

> Freeze the primary macro comparison before a fresh holdout; choose paired seed count for target precision, report shared n, and adjust the prespecified domain family.

Render the actual shared-seed counts, not a promised target. Re-rendering at n=5 improves precision but does not remedy selection, corpus or configuration uncertainty.

### 7. MAJOR - 6,144 tokens is a small, correlated holdout, and the provenance repair is not retrospective proof

**Evidence.** `eval/results/data_manifest.json` reports 48 blocks of 128 input tokens per domain from just **2-3 source documents**. Those are not 6,144 independent observations or a broad sample of a domain. Repeating training seeds on the same blocks cannot enlarge that sample. These are local real-text proxies, not an evaluation of distributed finance or medical deployments.

The exact committed token blocks are a valuable repair. However, `readmes.matches_cached_blocks` is false: the manifest was rebuilt after the installed source pool changed, and its document inventory is not demonstrated to describe all the original cached blocks. Zero exact whole-document duplicates in the rebuilt inventory does not certify the original README holdout or exclude near-duplicate passages. This is an audit limitation, **not a finding that leakage occurred**.

All ten provisional v2 rows also lack `env.data_digest` and `env.model_revision`, despite new runs now recording those fields. All six shared v1/v2 starter/Anchor final domain-loss dictionaries are identical, and the inspected historical training-path diff adds strategy registrations rather than altering those default paths; that supports numerical continuity, but the repeats are not independent evidence. `summarize.validate` rejects duplicates/dirty rows but does not itself enforce identical config/data/model provenance.

**Exact risk replacement:**

> This is a 12-round fixed-corpus pilot, not evidence of convergence or deployment generalization: each domain has only 6,144 input tokens, with the manifest reporting 2-3 source documents. Finals evaluation will use a larger, untouched document-level holdout and immutable run/data/model manifests.

**Exact provenance qualification for the supporting report:**

> Provisional runs predate per-run data/model digests; archived token blocks and matching reruns support continuity, but original document provenance is incomplete for the rebuilt README inventory.

Plan uncertainty over genuinely held-out documents/partitions as well as seeds; do not bootstrap individual adjacent tokens as if independent. Keep the development/ratchet holdout separate from the final test set.

### 8. MAJOR - A domain-to-budget Latin square does not remove all the stated confounding

**Evidence.** Abstract line 66 says rotating domains across device budgets means "budget, domain and data size aren't confounded." In `device_simulator/profiles.py:18-28`, the workstation always has 8x data, rank 16, 16 steps and no dropout; the tablet always carries the forced outage. Rotating only domain labels breaks domain-versus-profile confounding but leaves **data size versus compute/rank/availability** coupled. A fast data-rich client's advantage could still be credited to either factor.

There is also a population issue: one domain per device makes device-macro equal domain-macro in the pilot. With Dirichlet finance splits, multiple devices may share labels/domains; those two macro averages are no longer interchangeable.

**Exact replacement for the Latin-square bullet:**

> Rotate domains across budgets, and independently vary data quantity and outage assignment, including outages of the data-rich client; report client-macro and task/domain metrics separately.

A full factorial is not mandatory. A balanced small design with an independently assigned quantity-skew factor and outage target is enough to avoid claiming that a single rotation solves everything.

### 9. MAJOR - The checkpoint observation is true; dropout resilience and convergence still need discriminating tests

**Evidence.** `v2_dropout_analysis.md` supports the narrowed abstract sentence: in each of the three Anchor seeds, c4's manpages loss is below the untuned loss at rounds **3,6,9,12**. The mean maximum excess over all those checkpoints is **-0.0210** for Anchor and **+0.2794** for the starter. Do not retract those observations.

But `dropout_analysis.py:39-44` takes a maximum across the whole run, not a loss jump caused by the outage. Anchor's maximum is at round 3, **before** the forced round-5-to-9 outage; the starter is already worse than untuned at round 3. Remaining below the untuned model is not the same as avoiding degradation relative to the pre-outage model or a no-outage counterfactual. There are only two evaluation checkpoints within the forced outage and none at its onset or immediate rejoin.

The v2 snapshot has no matched Anchor no-outage/no-replay result. Nor does four observed decreases in macro loss establish convergence. The simulator skips wholly offline rounds and preselects a completed-step count for partial work; this is not an abruptly killed trainer salvaging its state over a network. The proposed real Flower kill is correctly future work.

**Exact observation wording:**

> In all three pilot seeds, the outage client's domain loss stayed below untuned at rounds 3,6,9,12; this sampled observation does not exclude intervening spikes or identify the causal effect of dropout.

**Exact evaluation-plan addition:**

> Measure per-round loss changes and recovery versus paired no-outage and no-replay controls around onset and rejoin, then repeat with a real mid-round process failure.

Retain "show convergence" as an MVP goal, but label the existing evidence "short-horizon loss improvement." Fresh/remembered contributions must remain separate during the outage analysis.

### 10. MINOR - Square-root weights are not a Sybil-robust solution

**Evidence.** Abstract line 78 lists square-root weights and registration as the mitigation; ADR antithesis disposition 7 calls square-root weights a "Sybil-robust middle ground." Splitting a dataset of size n into m identities changes its total unnormalized square-root weight from `sqrt(n)` to `m*sqrt(n/m) = sqrt(m*n)`. It still gains weight. It may be less identity-sensitive than uniform weighting, but it is not identity-invariant.

**Exact replacement:**

> Equal-client and square-root weights remain identity-sensitive; authenticate participants and test data-preserving identity splits.

Use the Sybil experiment to quantify the vulnerability, not to imply robustness by naming a different exponent.

### 11. MINOR - Supporting deliverables still contradict the provisional evidence

**Evidence.** `deliverables/architecture.md:36` says all named baselines were "implemented and run on 5 paired seeds." At this snapshot the v2 summary has 3/3/2/2 runs and no v2 HetLoRA-style row. Some original ADR statements are historical, but without explicit supersession they invite judges to read "every domain improves," "no extra server memory," no padding, and inherited exactness guarantees as current conclusions. Several survive despite the earlier review's accepted dispositions.

**Exact replacement for the architecture evidence sentence:**

> Implemented baselines include the starter, FFA-LoRA, FlexLoRA and HetLoRA-style padding; the current paired sample sizes and completed scenarios are those in the generated results table.

Add an explicit "superseded by the current decision below" marker to the original ADR claims, and use the narrowed wording in findings 1-3. An automatic abstract re-render does not update this prose. Do not advertise five completed baseline runs until the relevant shared pairs actually exist.

### 12. MINOR - Remove an unsupported cost superlative and keep the problem statement operational

**Evidence.** The opening says LoRA "is the cheapest way" to specialize the model and calls this "a systems problem disguised as an optimisation problem." No comparison establishes cheapest, and the rest of the proposal relies substantially on optimization choices. The brief asks for a lightweight useful system, not a lowest-cost theorem. Keeping raw text local is also not by itself a formal privacy guarantee; do not let the hospital/jurisdiction examples imply otherwise.

**Exact replacement for the opening's last two sentences:**

> We target collaborative specialization of a small model without pooling raw text. The challenge couples device resource limits, interrupted work and conflicting local objectives.

This is more precise and makes room for the operational meaning of "meaningfully contribute."

## Three highest-value abstract edits, within the word cap

These are **section replacements, not additions**. Applying the following three replacements in memory to the reviewed rendered abstract produces **776 body words**, using the repository's word-count rule (headings and table text count; Markdown-only tokens do not). That leaves room for the shared-n table labels and the shorter risk/protocol corrections above. Update the template, preserve result placeholders, and re-render; the numeric literals here refer to the reviewed pilot only.

1. **Replace "Understanding of the challenge" with the actual problem, rather than an implied theorem:**

   > Weak devices must supply useful fresh updates within limited resources; availability bias and quantity skew must not silently decide whose text the shared model serves. These are separate systems and statistical requirements, not consequences of exact aggregation. We choose equal-device held-out loss as our primary target and report the sample-weighted trade-off. Sharing a frozen A removes LoRA factor-averaging error; unequal work, dropout bias and domination require separate controls and evidence.

2. **Replace "Proposed approach" with a clear current/planned boundary:**

   > **Pilot:** HF PEFT on SmolLM2-135M, simulated sequentially on one shared model. Clients update nested B prefixes of ranks 2/4/8/16 under a shared frozen A and common LoRA scale. Their zero-padded deltas aggregate exactly in weight space; this identity also holds after the stated corrections, not necessarily for the raw current-client average.
   >
   > **Cost:** each payload contains r_k*d_out fp32 values per layer. At matched ranks, the pilot's q/v adapters require 2.5 times fewer uplink values than A+B. Active coefficients and logical uplink shrink; measured RAM, total communication and device throughput are not yet established.
   >
   > **Heuristics:** retain partial work, step-normalise, reuse absent clients' clipped directions for up to four rounds, and weight included clients equally. These do not guarantee unbiased optimisation.
   >
   > **Finals:** Flower ServerApp/ClientApp processes with seed-only A transport, real resource measurements, and FlowerTune-Finance accuracy on FPB/FiQA/TFNS with non-IID splits; scale to 0.5-1.7B after the controls pass.

3. **Replace "Novelty / differentiation" with the strongest honest systems claim:**

   > We extend FFA-LoRA's frozen-A design to prefix-masked device updates and evaluate participation handling and update-share diagnostics for one shared model. CF-LoRA learns A before freezing it for clustered B aggregation; PreLort trains both factors with a multi-prefix objective and segment-wise aggregation. Our contribution is the tested systems recipe and its cost/utility trade-offs, not a new exactness primitive or a minimum-communication theorem. In this pilot, the data-rich client's round-and-seed mean norm share falls from 0.88 to 0.22; this diagnoses update magnitudes, not causal benefit or a guaranteed fairness cap.

## Three highest-value experiments before the finals

1. **Matched-work attribution and weak-client removal, before expanding the model/baseline list.** Start on 135M with common accepted-step schedules, explicit effective scale and a small equal-budget learning-rate search. Compare full Anchor with the queued no-partial/no-memory/no-normalization/no-clipping/n-weight controls, starter-plus-partial, and a rank-matched frozen-A control sharing the same weights and admitted work. Remove each weak client's fresh information in paired runs while retaining the same evaluation population and explicitly fixed policy slots. Report macro and that client's domain effect against completed steps, bytes and time, plus rank-specific ownership. A small train-both-factors versus frozen-A, single-prefix versus multi-prefix control would directly test the PreLort differentiation once the simpler controls are understood. **Decision:** if a simpler partial-work/uniform-weight system explains the gain, present that result rather than crediting exactness or replay. Predeclare the primary contrast and practical effect; the current paired macro SD of 0.01138 would suggest about eight seeds for a 0.01 unadjusted t-interval half-width if that SD persists, not a guaranteed sample size.

2. **One resource-real Flower run with a weak client and recoverable failures.** Implement a genuine resource-limited local representation, accounting explicitly for the frozen higher-rank global residual; compare rank 2/4 with rank 16 at a fixed batch and sequence length. Measure process peak RAM, fresh tokens/second, round deadline completion, serialized upload/download bytes and server replay memory. Verify seed regeneration instead of transmitting A. Kill a weak client after partial work and separately interrupt the data-rich client; preserve only checkpoints actually transmitted before failure. Evaluate each round around onset/rejoin versus paired no-outage and no-replay controls, logging fresh work separately from cached reuse. **Decision:** demonstrate positive incremental held-out utility from affordable fresh weak-device work and quantified recovery, or narrow the device/deadline claim. A sequential MPS rank mask is not a substitute for this experiment.

3. **Fresh finance/generalization test with independently balanced sources of heterogeneity.** Freeze the selected system before opening a larger, content-deduplicated document/example-level holdout. Use FlowerTune-Finance metrics, multiple non-IID partitions, domain-to-budget rotations, and independently assigned data-size skew and outage targets; do not keep "rich = strongest = always online." Include local-only and centralized references as informative comparisons, not guaranteed mathematical bounds. Report client-macro, sample-weighted, task/domain and baseline-relative worst-client outcomes with paired-seed and document/partition uncertainty; reserve multiplicity correction for a stated family. Include a data-preserving c0 identity split to distinguish uniform-weight policy behavior from true anti-domination. **Decision:** establish that the favorable trade-off persists beyond the particular few source documents and workstation/wiki pairing; scale to larger models only after that survives.

## Audit notes

The rendered file exactly matches an in-memory render of its template and canonical results. Its reviewed body has 865 words. The paired macro/micro/worst intervals, Bonferroni bounds, checkpoint maxima, work counts and norm-share extrema above were recomputed from committed JSON/JSONL rather than accepted from narrative summaries. The two-sided t calculation uses paired differences and sample standard deviation; for the five-domain, three-seed intervals the critical value is 9.9248432.

Existing reproduction commands, from the project directory, are `python -m eval.summarize --tag v2`, `python -m eval.dropout_analysis --tag v2`, and `python scripts/check_numbers.py deliverables/round1-abstract.md`. They regenerate reports; I did not run the report-writing commands against the review worktree. The additional work/share counts can be reproduced without training:

```python
import json
from pathlib import Path
from statistics import mean

root = Path("eval/results/logs")
for method in ("anchor_full", "fedavg_ab_homo"):
    rounds = []
    for seed in (0, 1, 2):
        rounds += json.loads((root / f"v2_dropout_{method}_s{seed}.json").read_text())
    updates = [u for r in rounds for u in r["updates"]]
    shares = [r["aggregation"]["norm_share"]["c0"] for r in rounds]
    print(method, {
        "fresh": sum(u["status"] in ("ok", "partial") for u in updates),
        "partial": sum(u["status"] == "partial" for u in updates),
        "steps": sum(u["steps_done"] for u in updates),
        "replays": sum(len(r["aggregation"]["used_memory_for"]) for r in rounds),
        "c0_norm_mean_min_max": (mean(shares), min(shares), max(shares)),
    })
```

## What is strong

- **The central identity is sound.** A common frozen A with consistently scaled, zero-padded B deltas removes factor-product mismatch without a dense-product SVD; this is a useful engineering substrate even though it is not a new theorem.
- **The pilot is real and unusually inspectable for Round 1.** Committed per-round records, canonical rendering, paired schedules and explicit provisional sample sizes make substantive review possible.
- **The favorable macro direction is not a transcription artifact.** All three shared starter comparisons favor Anchor; the current four-domain Bonferroni statement and checkpoint-only dropout observation survive independent arithmetic checks.
- **The team exposes an inconvenient trade-off.** Reporting worse micro loss rather than hiding it is exactly the right foundation for an honest objective-selection argument.
- **The literature positioning is repairable, not demolished.** The inspected CF-LoRA and PreLort formulations do not duplicate this exact recipe; a budgeted, attribution-aware system evaluation can still go meaningfully beyond the hackathon starter.
- **The plan is feasible if it prioritizes the hard questions.** Complete matched controls, one authentic weak-client/failure path and a fresh holdout before accumulating more model sizes and named baselines. The earlier review's actual fixes and candid dispositions are evidence of iteration; this review asks that the claims catch up with their limits.

---
## Lead dispositions (Claude Opus 5.5 lead, 4 Oct 2026 12:25 IST)
All 12 findings **ACCEPTED**; none rejected. Abstract v3 (889 words, rendered, number check PASS) applies the three section replacements and the exact wordings below.
| # | Sev. | Disposition and where |
|---|---|---|
| 1 | BLOCKING | ACCEPTED. "Unbiased under partial participation" was removed. The Understanding section now ends with the reviewer's requirement framing; Approach says the identity holds for the chosen directions; ADR first principles 1 is marked superseded. |
| 2 | MAJOR | ACCEPTED. The novelty section now uses the reviewer's systems-recipe framing. `research/novelty.md` claim revised; PreLort's multi-prefix training noted as absent (`anchor_full_seg` ≠ PreLort); "neither considers participation" and "minimal upload" removed. |
| 3 | MAJOR | ACCEPTED. The abstract says "active coefficients and logical uplink shrink; measured RAM, total communication and throughput not yet established". The 2.5× claim is limited to matched ranks on this model's q/v adapters. ADR server-memory and padding statements are marked superseded; the diagram labels A transport as a design target. |
| 4 | MAJOR | ACCEPTED. The abstract now says "full-system comparison under paired availability, not matched completed work" and "paper-derived baselines, one fixed optimiser and scale". It gains an operational definition of meaningful participation and the residual wording "its effect on task loss is not isolated". Matched-work and attribution controls are queued (P2) and are the first finals experiment. |
| 5 | MAJOR | ACCEPTED. The share is described as a "round-and-seed mean norm share … a magnitude diagnostic, not a fairness cap or causal estimate"; the worst-domain non-improvement is stated. |
| 6 | MAJOR | ACCEPTED. Per-comparison shared n is rendered in the table; the pilot is labelled exploratory; the domain statement uses the reviewer's wording with the rendered Bonferroni count; the protocol text is replaced. |
| 7 | MAJOR | ACCEPTED. Risk wording now states 6,144 tokens from 2–3 documents per domain; provenance qualification added to the thought node (provisional runs predate per-run data/model digests). |
| 8 | MAJOR | ACCEPTED. The protocol now says domains rotate across budgets *and* data quantity and outages vary independently, including outages of the data-rich client. |
| 9 | MAJOR | ACCEPTED. The checkpoint observation is worded as sampled checkpoints; per-round recovery against no-outage/no-replay controls is added as the next step. |
| 10 | MINOR | ACCEPTED. √n is no longer called Sybil-robust (abstract risk, ADR synthesis 7 superseded). |
| 11 | MINOR | ACCEPTED. The architecture evidence sentence was replaced; the ADR supersession table was added. |
| 12 | MINOR | ACCEPTED. The opening no longer says "cheapest"; it uses the reviewer's operational problem statement. |
