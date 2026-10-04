# Round 1 abstract — Perceptron 2026, Problem 9

**Theme 6, AI You Can Actually Trust · Problem 9: Catching an Agent Before It Acts on a Bad Idea**
**Cite-Before-Act: pre-trade risk checks for AI agents**

*Final draft, 4 Oct 2026. Every number comes from a committed result; `python -m eval.check_docs` fails if this text drifts from `eval/results/`.*

## Problem and why we chose it
Agents now cancel orders, move money and message customers. Their worst mistakes are plausible calls, not malformed ones: a real tool, valid JSON, and one argument nobody supplied — the wrong order, an invented ticker, ten times the quantity. Trading desks solved the human version with pre-trade controls (SEC Rule 15c3-5): hard blocks, soft alerts and manual review before an order reaches the market. We want that discipline for agents. [TEAM: why this matters to us.]

## Understanding of the challenge
1. **Schema checks pass hallucinated calls by construction.** The check must be on argument *values* and where they came from.
2. **Absence of evidence is not contradiction.** An unsupported value should be held for a question; a contradicted one, blocked.
3. **The checker can hallucinate too.** Model verdicts need verifiable evidence.
4. **Every stop has a cost.** False blocks break tasks and holds load humans, so a guard is a trade-off curve, not one accuracy number.

## Proposed approach
A guard in the agent's pre-tool hook (a LangGraph node before `ToolNode`, or LangChain v1 `wrap_tool_call`) returns *allow*, *block with feedback* or *hold for review* for every write call.
- **Tier 0 (deterministic, sub-millisecond).**
  - Every intent-bearing argument must trace to the user's words, the reference database or trusted tool data. Email or ticket text is never a source of intent.
  - Each check returns *pass*, *fail*, *unverifiable* or *needs approval*, with evidence and a policy clause.
  - Pre-trade-style contracts: price collar, size, cash, short-sale, restricted list, duplicates, ownership.
- **Tiers 1–2.** Only the *unverifiable* residue goes to a model (Qwen3-1.7B, or 8B for high-risk calls). A verdict counts only if the user words or tool data it quotes are found verbatim, and a bare "yes" never counts.
- **Tier 3.** A human, via LangGraph `interrupt()`. Blocked calls return their failed checks so the agent can repair them.

## Minimum Viable
- *Checker for ≥1 action class against a source:* four trading-desk actions against a synthetic reference knowledge base, plus τ-bench retail's seven write tools against its order database.
- *Catching a deliberately bad action:* a one-command demo blocks an invented ticker, a ×10 quantity, a buy/sell flip and an email-injected transfer, and holds a price the user never gave.

## Stretch ambitions
1. **Risk-routed fast/careful models**, with hold thresholds set by conformal risk control so the miss rate is bounded at a stated level.
2. **Red-team suites**, grown into mutation testing for guards.

## Novelty versus the obvious baseline
The obvious baseline asks an LLM "is this call OK?". We differ in four ways:
1. per-argument provenance instead of one holistic judgement;
2. *unverifiable* (hold) kept separate from *contradicted* (block);
3. model verdicts admitted only with verified quotes;
4. evaluation on real agent errors, reporting the catch / false-block / hold trade-off with confidence intervals.

Shipping tools (pre-tool hooks, Cedar gateway policies, groundedness APIs that score response *text*) don't check argument values against a source.

## Evaluation plan and first results
**Real agent errors.** We replayed every write call in τ-bench's published gpt-4o and Claude-3.5-Sonnet retail runs: 2,018 calls, labelled by whether each call's database effect matches the task's ground truth. Rules were tuned on half the tasks and tested on held-out tasks (991 calls, 167 harmful). The test was re-run once after an external code review fixed six bugs. 95% CIs are clustered by task.
- Schema checks catch 0%.
- Our untuned, policy-derived checker stops (blocks or holds) **68% (95% CI 57–77)** of harmful calls, but blocks 7% of good calls and holds 56%.
- The tuned setting cuts false blocks to **2.0%** and holds to 30%, stopping **41% (28–55)**, at **0.4 ms** at p95. Only 3 of its stops are hard blocks.
- It does not beat the untuned checker's score; it is a different point on the curve.
- **LLM judge** (Qwen3-1.7B, same transcript and policy), on a 300-call sample: at almost the same good-call stop rate (27% vs our 28%), the judge stops 28% of harmful calls and ours 48%. The judge's stops are hard blocks; ours are mostly holds.
- **Model tier, first try:** a 1.7B resolver with verified quotes settled 11 of 85 held calls (6 harmful correctly blocked, 5 good calls wrongly blocked) and released none. Tiers 1–2 need a stronger model.

**Misses.** In 20 audited misses, 8 were explicitly requested by τ-bench's simulated user (invisible to any transcript check) and 8 were wrong-entity choices ("like my other order") — the target for Tiers 1–2.

**Independent red team.** 160 cases written by a different model family that never saw our rules: the checker stops 82% (73–88) of 100 bad calls, but blocks 8% and holds 20% of 60 good ones. Our own synthetic suite scores 100% caught, 0% false blocks; self-written tests flatter.

## Feasibility and risks
- **Team:** [TEAM: names and skills.]
- **Compute:** one laptop, open models, no paid APIs.
- **Milestones:** 25 Oct live LangGraph agent · 1 Nov model tier on τ-bench residue · 10 Nov calibrated thresholds · 17 Nov demo freeze · 19–25 Nov exams (no work) · 1 Dec progress report · December hardening.
- **Risks:** modest catch on real errors (we publish the curve); rules brittle on paraphrase (model tier, independent suites); users confirming wrong actions (check against earlier stated wants).
