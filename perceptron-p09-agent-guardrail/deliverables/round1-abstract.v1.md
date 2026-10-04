# Round 1 abstract — Perceptron 2026, Problem 9

**Theme 6, AI You Can Actually Trust · Problem 9: Catching an Agent Before It Acts on a Bad Idea**
**Cite-Before-Act: pre-trade risk checks for AI agents**

*v1.0, 4 Oct 2026. Every number comes from a committed result. `python -m eval.check_docs` fails if this text drifts from `eval/results/`.*

## Problem and why we chose it
Agents now cancel orders, move money and message customers. Their worst mistakes are plausible calls, not malformed ones: a real tool, valid JSON, and one argument nobody supplied — the wrong order, an invented ticker, ten times the quantity. Trading desks solved the human version long ago with pre-trade controls that reject erroneous orders before they reach the market (SEC Rule 15c3-5). We want that discipline for agents. [TEAM: one sentence on why this matters to us.]

## Understanding of the challenge
1. **Schema checks pass hallucinated calls by construction.** The check must be on argument values and where they came from.
2. **Absence of evidence is not contradiction.** An unsupported value should trigger a question; a contradicted one, a block.
3. **The checker can hallucinate too,** so model verdicts need verifiable evidence.
4. **Every stop has a cost.** False blocks break tasks and escalations load humans, so verification effort must scale with risk.
5. **Real errors are subtle.** In real agent logs, many harmful calls were explicitly confirmed by the (simulated) user, and most of the rest are wrong-entity choices such as "like my other order".

## Proposed approach
A guard in the agent's pre-tool hook (a LangGraph node before `ToolNode`, or LangChain v1 `wrap_tool_call`) returns *allow*, *block with feedback* or *escalate* for every write call.
- **Tier 0 (deterministic, sub-millisecond).**
  - Per-argument provenance: each intent-bearing value must trace to the user's words, the reference knowledge base or trusted tool data. Text from emails or tickets is never a source of intent.
  - Each check returns *pass*, *fail* (contradicted), *unverifiable* or *needs approval*, with evidence and a policy clause.
  - The same tier runs pre-trade-style contracts: price collar, size, cash and short-sale limits, restricted list, duplicates, ownership.
- **Tiers 1–2.** Only the *unverifiable* residue goes to a model: Qwen3-1.7B (fast) or Qwen3-8B (careful), chosen by reversibility and value at stake. A model verdict counts only if the words it quotes match the source verbatim.
- **Tier 3.** A human, via LangGraph `interrupt()`. Blocked calls return their failed checks so the agent can repair the call.

## Minimum Viable
- *A checker that verifies ≥1 action class against a source:* built for four desk actions (orders, transfers, cancellations, client messages) against a synthetic instrument/account/limits/policy knowledge base. It is also ported to τ-bench retail: seven write tools checked against the live order database.
- *Catching a deliberately bad action:* a one-command demo blocks an invented ticker, a ×10 quantity, a buy/sell flip and an email-injected transfer, and escalates a price the user never gave.

## Stretch ambitions
1. **Risk-based fast/careful routing** (above), with thresholds set by conformal risk control so the miss rate is bounded at a stated level. Our error audit points here: wrong-entity choices need cross-record reasoning that rules can't do.
2. **Red-team suites** (done, below), grown into mutation testing for guards.

## Novelty versus the obvious baseline
The obvious baseline asks an LLM "is this call OK?". We differ in four ways:
1. per-argument provenance instead of one holistic judgement;
2. *unverifiable* (ask) kept separate from *contradicted* (block);
3. model verdicts admitted only with verified quotes;
4. we report the frontier of catch, false blocks, escalations and latency, not one accuracy number.

Shipping tools (pre-tool hooks, Cedar gateway policies, groundedness APIs that score response text) don't check argument values against a knowledge source.

## Evaluation plan and first results
- **Metrics:** catch rate (bad calls blocked or escalated); false-block and escalation rates on good calls; latency p50/p95; 95% CIs clustered by task.
- **Baselines:** no guard; schema-only; an LLM judge (Qwen3-1.7B) shown the same transcript and policy.

**Real agent errors.** We replayed every write call in τ-bench's published gpt-4o and Claude-3.5-Sonnet retail runs: 2,018 calls, each labelled by whether its database effect matches a ground-truth action, split by task. On the held-out half (991 calls, 167 harmful):
- Schema checks catch 0%.
- Our untuned, policy-derived checker catches **68% (95% CI 57–77)**, but blocks 7% of good calls and escalates 56%.
- A dev-tuned setting cuts false blocks to **1.8%** and escalations to 25%, while catching **36% (24–49)**.
- On a 300-call sample, the LLM judge catches [JUDGE-CATCH] of harmful calls and blocks [JUDGE-FB] of good ones.
- Guard latency is **0.2 ms** at p95.

An audit of 20 misses found:
- 8 that the simulated user explicitly requested (invisible to any transcript-based check);
- 8 wrong-entity choices — the target for Tiers 1–2.

**Independent red teams (desk domain).** [ASTRA-RESULT] Earlier, 134 cases from a separately prompted agent that never saw our rules: 94% caught, no good call blocked.

**Next:** model tiers on the τ-bench residue, calibrated thresholds, and a live LangGraph agent measuring repair rate.

## Feasibility and risks
- **Team:** [TEAM: names and skills.]
- **Compute:** everything runs on one laptop with open models; no paid APIs.
- **Milestones:** 25 Oct live agent + interceptor · 1 Nov model tier on τ-bench residue · 10 Nov calibrated thresholds · 17 Nov demo freeze · 19–25 Nov exams (no work) · 1 Dec progress report · December hardening.
- **Risks → mitigations:**
  - The catch/escalation trade-off is real → reported as a frontier.
  - Rules are brittle on paraphrase → model tier, independent suites.
  - Users confirm wrong actions → checks against the user's earlier stated wants.
