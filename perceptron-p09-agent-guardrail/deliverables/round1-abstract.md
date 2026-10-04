# Round 1 abstract (draft) — Perceptron 2026, Problem 9

**Theme 6, AI You Can Actually Trust · Problem 9: Catching an Agent Before It Acts on a Bad Idea**
**Working title: *Cite-Before-Act* — pre-trade risk checks for AI agents**

*Draft v0.1, 4 Oct 2026. Numbers come from committed runs (reproduce commands in `eval/README.md`). Team details are placeholders until teammates are confirmed.*

## Problem and why it interests us
Agents now place orders, move money and message clients. Their dangerous mistakes are plausible calls, not malformed ones: a real tool, valid JSON, and one value nobody supplied. Examples: a ticker that doesn't exist, ten times the quantity asked for, an account the user never named, a fee the policy never states. Trading solved the human version of this long ago with pre-trade risk checks that run before an order reaches the market. SEC Rule 15c3-5 requires rejecting orders that "exceed appropriate price or size parameters" or "indicate duplicative orders". We want that discipline for agents, plus one thing traders never needed: an agent can invent the order itself.

## Understanding of the challenge
1. **Schema checks pass hallucinated calls by construction.** A 2026 study of tool hallucination finds that registry and signature checks cannot separate "borrowed arguments" from a valid call. The check has to be on argument *values*.
2. **Absence of evidence is not contradiction.** An unverifiable value should trigger a question; a contradicted one, a block. Collapsing both into allow/deny gives either silent passes or approval fatigue.
3. **The checker can hallucinate too.** An LLM judge can approve an invented value.
4. **Checks have costs.** Latency and false blocks both hurt users, so verification effort must scale with risk (reversibility, value at stake).

## Proposed approach
A guard sits in the agent's pre-tool hook (a LangGraph node before `ToolNode`, or LangChain v1 `wrap_tool_call` middleware). It returns *allow*, *block with feedback*, or *escalate* for every write call.
- **Tier 0: provenance plus contracts (deterministic, ≤5 ms).**
  - For each intent-bearing argument, find its source: the user's words, the reference knowledge base (instrument master, accounts, limits, restricted list, numbered policy), or trust-labelled tool results.
  - Each check returns *pass*, *fail* (contradicted), *unverifiable*, or *needs approval*, with evidence and a policy clause.
  - Text from emails or tickets is never accepted as a source of intent; this is the prompt-injection defence.
  - The same tier runs the pre-trade analogues: a price collar against the reference price, size and cash/notional limits, a short-sale check, the restricted list, and duplicate detection.
- **Tiers 1–2: risk-routed resolution.** Only *unverifiable* checks reach a model: Qwen3-1.7B for low risk, Qwen3-8B for high risk, both run locally with MLX. The model must quote the words that settle the question. We match that quote verbatim against the request or the cited clause; if it doesn't match, the check stays unverifiable.
- **Tier 3: human.** Unresolved or approval-required calls pause through LangGraph `interrupt()`. Blocked calls return their failed checks so the agent can repair the call.

## Minimum Viable mapping
- *A checker that verifies ≥1 action class against a source:* we cover four classes (orders, fund transfers, cancellations, client messages), all checked against the reference KB. This runs today.
- *Catching ≥1 deliberately bad action:* a red-team suite of 295 bad calls in 11 classes (fabricated entity, entity swap, numeric drift, side flip, duplicate, injection, unrequested action, hallucinated policy claim, policy violation and more), plus (by 25 Oct) a live LangGraph episode where an invented ticker is blocked and the agent repairs it.

## Stretch ambitions
1. **Risk-based fast/careful routing (above).** Thresholds will be set with conformal risk control / Learn-then-Test so the miss rate is bounded at a stated α.
2. **The red-team suite as mutation testing for guards.** Operators turn good calls into typed bad ones. The suite is split by phrasing family, so evaluation uses wording the rules never saw.

## Novelty versus the obvious baseline
The obvious baseline asks an LLM "is this tool call OK?" with retrieved context. We differ in four ways:
1. Per-argument provenance with trust labels, instead of one holistic judgement.
2. A separate *unverifiable* verdict (ask the user), distinct from *contradicted* (block).
3. Models resolve only the residue, and only with verified quotes, which limits checker hallucination.
4. We report the trade-off frontier (catch rate, false blocks, escalations, latency), not a single accuracy number.

Shipping tools (pre-tool hooks, Cedar gateway policies, groundedness APIs that score response text) don't check argument values against a knowledge source.

## Evaluation plan
- **Metrics:** catch rate, false-block rate, escalation rate, latency p50/p95, and closed-loop task success after self-repair.
- **Baselines:** no guard, schema-only, and an LLM judge (1.7B and 8B) given the same KB.
- **Data:**
  - our suite, split into dev and test by phrasing family;
  - LLM-paraphrased requests;
  - τ-bench's published gpt-4o and Claude trajectories, replayed offline with every proposed write labelled against ground truth (real model errors).
- **First numbers** (synthetic test split, 183 calls): Tier 0 catches 100% of 147 bad calls, blocks none of 36 good calls, and adds under 5 ms at p95 on a loaded laptop. Schema-only validation catches 0%. On a 61-call subsample, an LLM judge (Qwen3-1.7B) given the same KB catches 71% but blocks 69% of good calls, mostly through arithmetic slips. Test data is template-generated by the rules' author, so the τ-bench replay is the real test.

## Feasibility and risks
- **Team:** Ashish (systems, LLM engineering); [member 2: TBD]; [member 3: TBD].
- **Compute:** everything runs on one laptop with open models; no paid APIs.
- **Milestones:** 25 Oct live agent + interceptor · 1 Nov τ-bench replay · 10 Nov calibrated cascade · 17 Nov demo freeze · 19–25 Nov exams (no work) · 1 Dec progress report · December hardening and stretch goals.
- **Risks → mitigations:** paraphrase brittleness → resolver, tracked as escalation rate; a flattering synthetic suite → τ-bench replay; local-model latency → prompt caching, smaller resolvers.
