# Routing / Control / Cascade Papers — Protocol Definitions & Headline Numbers

Sources: arXiv abstract pages (fetched via arxiv.org/abs and the official export.arxiv.org/api/query mirror, same abstract text as the HTML abs page). All accessed 2026-10-04.

---

## 1. AI Control: Improving Safety Despite Intentional Subversion

- **URL**: https://arxiv.org/abs/2312.06942 (accessed 2026-10-04); appendix text also pulled from https://arxiv.org/html/2312.06942v5 (accessed 2026-10-04)
- **Date**: Submitted 2023-12-12; this version (v5) updated 2024-07-23
- **Authors**: Ryan Greenblatt, Buck Shlegeris, Kshitij Sachan, Fabien Roger

**Mechanism** (quoted/paraphrased from the abstract I opened): the paper "develop[s] and evaluate[s] pipelines of safety techniques (\"protocols\") that are robust to intentional subversion," in a scenario solving "a sequence of programming problems, using access to a powerful but untrusted model (in our case, GPT-4), access to a less powerful trusted model (in our case, GPT-3.5), and limited access to high-quality trusted labor," aiming "to never submit solutions containing backdoors, which we operationalize here as logical errors that are not caught by test cases." Two protocols are explicitly named and defined in the abstract: **trusted editing** — "asks GPT-4 to write code, and then asks GPT-3.5 to rate the suspiciousness of that code. If the code is below some suspiciousness threshold, it is submitted. Otherwise, GPT-3.5 edits the solution to remove parts that seem suspicious and then submits the edited code"; and **untrusted monitoring** — "asks GPT-4 to write code, and then asks another instance of GPT-4 whether the code is backdoored, using various techniques to prevent the GPT-4 instances from colluding." Quote: "These protocols improve substantially on simple baselines."

**Guarantee / numbers**: The abstract gives no explicit numeric safety/usefulness score or audit-budget percentage. **UNVERIFIED**: the specific terms "trusted monitoring" (as distinct from "untrusted monitoring"), "defer to trusted," and an exact "audit budget" value (e.g., a top-X% audited) are standard terms associated with this paper but were **not found** in the text segments I actually opened this session (abstract + an appendix fragment on the "Black-box Protocol Assumption," which discusses train/validate/deploy and black-box vs. malign-init evaluation, not the main protocol-definition section). I could not retrieve the methods/results section within the call budget — flagging rather than filling from memory.

---

## 2. Ctrl-Z: Controlling AI Agents via Resampling

- **URL**: https://arxiv.org/abs/2504.10374 (accessed 2026-10-04)
- **Date**: 2025-04-14
- **Authors**: Aryan Bhatt, Cody Rushing, Adam Kaufman, Tyler Tracy, Vasil Georgiev, David Matolcsi, Akbir Khan, Buck Shlegeris

**Mechanism**: "the first control evaluation performed in an agent environment." The authors "construct BashBench, a dataset of 257 challenging multi-step system administration tasks, and evaluate whether various safety measures can prevent an adversarially constructed AI agent from covertly downloading and executing malicious code." They "introduce a class of control protocols called **resample protocols** that dynamically take additional samples of certain actions," which "significantly improve on existing techniques by selectively blocking the AI agent from executing suspicious code and incriminating the agent by generating additional examples of dangerous behavior."

**Guarantee / numbers (exact quote)**: "our best protocol combines resampling with analysis of previous steps, reducing the success rate of attacks from 58% to 7% at a 5% cost to the performance of a non-malicious agent."

---

## 3. FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance

- **URL**: https://arxiv.org/abs/2305.05176 (accessed 2026-10-04)
- **Date**: 2023-05-09
- **Authors**: Lingjiao Chen, Matei Zaharia, James Zou

**Mechanism**: Reviews three cost-reduction strategies for using paid LLM APIs: "1) prompt adaptation, 2) LLM approximation, and 3) LLM cascade." FrugalGPT is introduced as "a simple yet flexible instantiation of LLM cascade which learns which combinations of LLMs to use for different queries in order to reduce cost and improve accuracy" — i.e., a learned cascade/routing order over LLM APIs rather than always calling the most expensive one.

**Guarantee / numbers (exact quote)**: "FrugalGPT can match the performance of the best individual LLM (e.g. GPT-4) with up to 98% cost reduction or improve the accuracy over GPT-4 by 4% with the same cost."

---

## 4. RouteLLM: Learning to Route LLMs with Preference Data

- **URL**: https://arxiv.org/abs/2406.18665 (accessed 2026-10-04)
- **Date**: v1 2024-06-26; this version (v4) updated 2025-02-23
- **Authors**: Isaac Ong, Amjad Almahairi, Vincent Wu, Wei-Lin Chiang, Tianhao Wu, Joseph E. Gonzalez, et al. (author list truncated in the retrieved API response after this point — **UNVERIFIED** full author list, e.g. remaining co-authors not confirmed this session)

**Mechanism**: Proposes "several efficient router models that dynamically select between a stronger and a weaker LLM during inference, aiming to optimize the balance between cost and response quality," with "a training framework for these routers leveraging human preference data and data augmentation techniques to enhance performance."

**Guarantee / numbers (exact quote)**: "our approach significantly reduces costs—by over 2 times in certain cases—without compromising the quality of responses." Also: "our router models also demonstrate significant transfer learning capabilities, maintaining their performance even when the strong and weak models are changed at test time."

---

## 5. Conformal Risk Control

- **URL**: https://arxiv.org/abs/2208.02814 (accessed 2026-10-04)
- **Date**: v1 2022-08-04; this version (v4) updated 2025-06-13
- **Authors**: Anastasios N. Angelopoulos, Stephen Bates, Adam Fisch, Lihua Lei, Tal Schuster

**Mechanism**: "We extend conformal prediction to control the expected value of any monotone loss function. The algorithm generalizes split conformal prediction together with its coverage guarantee." Extensions mentioned: "distribution shift, quantile risk control, multiple and adversarial risk control, and expectations of U-statistics." Worked examples "bound the false negative rate, graph distance, and token-level F1-score" in CV/NLP tasks.

**Guarantee (exact quote)**: "Like conformal prediction, the conformal risk control procedure is tight up to an O(1/n) factor." (n = calibration-set size). Exact formal theorem statement (the precise inequality on E[loss]) was not retrieved this session — abstract-level only; **UNVERIFIED** beyond this quoted description.

---

## 6. Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control

- **URL**: https://arxiv.org/abs/2110.01052 (accessed 2026-10-04)
- **Date**: v1 2021-10-03; this version (v5) updated 2022-09-29
- **Authors**: Anastasios N. Angelopoulos, Stephen Bates, Emmanuel J. Candès, Michael I. Jordan, Lihua Lei

**Mechanism (exact quote)**: "We introduce a framework for calibrating machine learning models so that their predictions satisfy explicit, finite-sample statistical guarantees. Our calibration algorithms work with any underlying model and (unknown) data-generating distribution and do not require model refitting." Applications listed: "false discovery rate control in multi-label classification, intersection-over-union control in instance segmentation, and the simultaneous control of the type-1 error of outlier detection and confidence set coverage in classification or regression." Key method insight: "reframe the risk-control problem as multiple hypothesis testing, enabling techniques and mathematical arguments different from those in the previous literature."

**Guarantee / numbers**: finite-sample, distribution-free statistical risk-control guarantee (framework level, per above quote). No specific α/δ numeric worked example was present in the abstract text itself — **UNVERIFIED** for a concrete numeric instance beyond the general finite-sample claim.

---

## 7. Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners (KnowNo)

- **URL**: https://arxiv.org/abs/2307.01928 (accessed 2026-10-04)
- **Date**: v1 2023-07-04; this version (v2) updated 2023-09-04
- **Authors**: Allen Z. Ren, Anushri Dixit, Alexandra Bodrova, Sumeet Singh, Stephen Tu, Noah Brown, Peng Xu, Leila Takayama, Fei Xia, Jake Varley, Zhenjia Xu, Dorsa Sadigh, Andy Zeng, Anirudha Majumdar

**Mechanism (exact quote)**: "we present KnowNo, which is a framework for measuring and aligning the uncertainty of LLM-based planners such that they know when they don't know and ask for help when needed. KnowNo builds on the theory of conformal prediction to provide statistical guarantees on task completion while minimizing human help in complex multi-step planning settings."

**Guarantee / numbers (exact quote)**: "Experiments across a variety of simulated and real robot setups that involve tasks with different modes of ambiguity (e.g., from spatial to numeric uncertainties, from human preferences to Winograd schemas) show that KnowNo performs favorably over modern baselines (which may involve ensembles or extensive prompt tuning) in terms of improving efficiency and autonomy, while providing formal assurances. KnowNo can be used with LLMs out of the box without model-finetuning." No specific numeric success-rate/α target is stated in the abstract itself — **UNVERIFIED** for an exact number (e.g., target task-success probability) beyond "statistical guarantees on task completion" / "formal assurances."

---

## Applying this to a fast → careful → human escalation cascade (guardrail design)

1. **Pick the risk**: define a monotone per-action loss (e.g., `1` if a *bad* action is approved/not escalated, `0` otherwise); the target is a calibrated threshold λ on the fast model's suspicion/uncertainty score such that the expected miss-rate R(λ) ≤ α, following the Learn-then-Test / Conformal Risk Control split-calibration recipe (abstracts above: "finite-sample statistical guarantees," "tight up to O(1/n)").
2. **Two-threshold cascade**: fast/cheap model scores every call; scores below λ_low auto-pass, scores above λ_high escalate straight to a human verifier, and the band in between is deferred to the slower/careful model (mirroring AI Control's "trusted editing"/defer-style protocols and Ctrl-Z's resample-on-suspicion idea) — pick λ_low, λ_high on a held-out calibration set of labeled (action, bad/benign) pairs, not on training data.
3. **Finite-sample safety bound**: using a Clopper–Pearson/Hoeffding-Bentkus-style one-sided bound on a held-out calibration set with zero observed misses at the chosen λ, the minimum calibration-set size n satisfies (1−α)^n ≤ δ, i.e. **n ≥ ln(1/δ)/α** (this is my own derivation from the general finite-sample risk-control logic in entries 5–6 above, not a quoted number from either paper).
4. **Worked size for α=0.05, δ=0.1**: n ≥ ln(10)/0.05 ≈ 2.303/0.05 ≈ 46.1 → **use n ≈ 47–50 labeled calibration examples with zero tolerated misses** at the selected threshold (round up for safety margin; if any misses occur in calibration, λ must be tightened and n increased, e.g. via a Clopper–Pearson upper bound at k>0 observed failures).
5. **Operational caveat**: this bound guarantees the *calibration-set* miss-rate estimate, not distribution shift at deploy time — re-calibrate (new n-sized draw) whenever the action distribution, the fast model, or the careful/human verifier changes, per the "distribution shift" extension flagged in Conformal Risk Control (entry 5).
