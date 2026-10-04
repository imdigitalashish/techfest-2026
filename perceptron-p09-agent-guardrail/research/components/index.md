# Per-component research — innovation scan (v1, lean mode)

*One section per component from [`architecture/components.md`](../../architecture/components.md). Sources are those cited in [`../landscape.md`](../landscape.md) and [`../notes/`](../notes/). Written by the lead on 4 Oct 2026 without per-component sub-agents (Supervisor lean mode). Deeper per-component files follow once sub-agents are allowed again. Candidate scores (1–5) are for impact · novelty · feasibility · measurability · demo.*

## 2 Interceptor (pre-tool hook)
- **State of the art:**
  - Every major framework exposes a pre-tool hook: OpenAI Agents SDK tool guardrails, Claude Code `PreToolUse`, ADK `before_tool_callback`, Semantic Kernel function-invocation filters, LangChain/LangGraph middleware and `interrupt()` (landscape §5).
  - "Approval Laundering" (2609.38983) shows that approval and execution can come unbound, even at Claude Code's mediation point.
- **Innovation room:**
  - Bind each verdict to the exact arguments: hash `(tool, args)` into the verdict and re-check it at execution, which closes the "argument laundering" gap they report.
  - Measure **mediation completeness**.
  - Candidate *verdict-bound execution* — 4·3·5·5·3.

## 4 Reference KB
- **State of the art:** grounding APIs (Vertex check-grounding, Azure groundedness, Bedrock contextual grounding) score *response text* against documents.
- **Innovation room:**
  - Typed reference data with **citable locators**, so each check cites `kb:instruments/INFY.ref_price`.
  - **Freshness metadata**: "Stale Does Not Mean Unsafe" (2609.29522) shows coarse freshness rules cause 92–95% needless blocks, so we check semantic predicates, not timestamps.
  - Candidate *as-of versioned KB snapshots in evidence* — 3·3·4·4·3.

## 5 Mention parser
- **State of the art:** slot filling / intent extraction. Baseline: regex and lexicons (built). Weakness measured: the dev paraphrase family escalates 100%.
- **Innovation room:**
  - A learned parser distilled from the careful model's verified resolutions (self-training on quotes that pass verification).
  - Number words and Indian units (lakh/crore, built).
  - Multi-turn coreference ("same for my other account").
  - Candidate *distilled verified-quote parser* — 4·4·3·5·3.

## 6 Tier-0 checker (spike S1)
- **State of the art:**
  - Policy engines and DSLs: AgentSpec (2503.18666), Progent (2504.11703), ActGov (2609.24446), AgentFlow (2608.22868), Cedar in AgentCore, Invariant rules.
  - Structural resolution: closed-world registry and signature checks (2609.19425).
  - Contracts: ContrAgent's LTLf→DFA (2609.18128).
  - Pre-trade controls: SEC 15c3-5(c).
- **Innovation room:**
  - **Per-argument provenance with trust labels** and a **third verdict (unverifiable)** separate from contradiction (built).
  - **Value-flow tracking across steps**: did a quote's price flow into the order? (partly built through observation matching).
  - Candidate *provenance graph over the trajectory* — 5·4·4·5·5.

## 7 Risk router (spike S2)
- **State of the art:**
  - Cascades and routers: FrugalGPT, RouteLLM.
  - AI-control trusted monitoring and deferral (2312.06942); Ctrl-Z resampling cuts attack success "from 58% to 7% at a 5% cost" (2504.10374).
  - HiSentinel's 0.6B/1.7B sentinels (2609.39957).
- **Innovation room:**
  - Route by **action risk** (reversibility × value at stake), not only by model confidence.
  - Thresholds from **conformal risk control / Learn-then-Test** with a stated miss-rate target (notes/routing-control-cascades.md). "What Can Be Enforced?" (2607.22868) warns that calibration on benign data alone doesn't transfer and that closed-loop effects matter, so calibrate on the mutation suite and report closed-loop numbers.
  - Candidate *risk-conditional conformal thresholds* — 4·4·4·5·3.

## 8 LLM resolver + quote verifier (spikes S1/S2)
- **State of the art:**
  - LLM-as-judge guards: GuardAgent (2406.09187), ShieldAgent (2503.22738), LlamaFirewall AlignmentCheck.
  - Verifier models: HHEM-2.1, MiniCheck, Granite Guardian 3.2 with a named function-calling-hallucination risk (notes/verifier-models.md).
- **Innovation room:**
  - The model may only move a check from unverifiable to pass/fail **with a quote we verify verbatim**, which bounds checker hallucination.
  - Add an NLI entailment check of quote ⇒ claim (HHEM / DeBERTa) as a second, model-independent gate.
  - Candidate *quote + entailment double gate* — 4·4·4·5·4.

## 9 Decision + feedback / self-repair
- **State of the art:** most guards return a boolean or a tripwire; agents rarely get structured reasons.
- **Innovation room:**
  - Feedback that lists the failed checks with evidence, so the agent can repair the call.
  - Measure the **repair rate** and closed-loop task success (2607.22868 shows static scores don't identify closed-loop behaviour).
  - Candidate *repair-oriented feedback* — 4·3·4·4·5.

## 11 Red-team generator
- **State of the art:**
  - Benchmarks: AgentDojo (97 tasks / 629 security cases), ToolEmu (36 toolkits / 144 cases), τ-bench logs with ground-truth actions.
  - Taxonomies: closed-world H1–H5.
- **Innovation room:**
  - **Mutation testing for guards**: typed operators over good calls, family-split. Built: 11 classes.
  - Add LLM-paraphrased families and **τ-bench replay** (real model errors) for external validity.
  - Candidate *mutation score as a guard-quality metric* — 4·4·5·5·4.

## 13 Calibrator
- See component 7. Learn-then-Test needs a calibration set large enough for the target. The cascades note derives n ≈ 47–50 examples for α = 0.05, δ = 0.1 via Clopper–Pearson; this is the agent's own derivation and needs re-checking.
