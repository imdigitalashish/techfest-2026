# Round 1 abstract — Perceptron 2026, Problem 9

**Theme 6, AI You Can Actually Trust · Problem 9: Catching an Agent Before It Acts on a Bad Idea**
**Cite-Before-Act: pre-trade risk checks for AI agents**

## Problem and why we chose it
Agents now cancel orders, move money and message customers. Their worst mistakes are plausible calls, not malformed ones: a real tool, valid JSON, and one argument nobody supplied — the wrong order, an invented ticker, ten times the quantity. Trading desks solved the human version with pre-trade controls (SEC Rule 15c3-5): hard blocks, soft alerts and manual review. We want that discipline for agents. [TEAM: why this matters to us.]

## Understanding of the challenge
1. **Schema checks pass hallucinated calls by construction.** The check must be on argument *values* and where they came from.
2. **Absence of evidence is not contradiction.** An unsupported value should be held for a question; a contradicted one, blocked.
3. **The checker can hallucinate too.** Model verdicts need verifiable evidence.
4. **Every stop has a cost.** False blocks break tasks and holds load humans, so a guard is a trade-off curve, not one accuracy number.

## Proposed approach
A guard in the agent's pre-tool hook (a LangGraph node before `ToolNode`, or LangChain v1 `wrap_tool_call`) returns *allow*, *block with feedback* or *hold for review* for every write call.
- **Tier 0 (deterministic).**
  - Bind each intent-bearing argument to the user's request or a specifically confirmed proposal; database and tool records supply facts, not authority. Email or ticket text cannot authorize actions.
  - Each check returns *pass*, *fail*, *unverifiable* or *needs approval*, with evidence and a policy clause.
  - Pre-trade-style contracts: price collar, size, cash, short-sale, restricted list, duplicates, ownership.
- **Tiers 1–2 (experimental).** Route *unverifiable* checks to gpt-4.1-mini or local Qwen3. Require substantive source-matched quotes; occurrence does not establish entailment. Ambiguous entity bindings must first reach this tier rather than pass Tier 0.
- **Tier 3.** A human, via LangGraph `interrupt()`. Blocked calls return their failed checks so the agent can repair them.

## Minimum Viable
- *Checker for ≥1 action class against a source:* four trading-desk actions against a synthetic reference knowledge base, plus τ-bench retail's seven write tools against its order database.
- *Catching a deliberately bad action:* a one-command demo blocks an invented ticker, a ×10 quantity, a buy/sell flip and an email-injected transfer, and holds a price the user never gave.

## Stretch ambitions
1. **Risk-routed fast/careful models**; attempt conformal control of harmful-call miss rate on untouched calibration scenarios, subject to exchangeability and a predeclared review budget.
2. **Red-team suites**, grown into mutation testing for guards.

## Novelty versus the obvious baseline
The starter baseline already combines a framework and KB. ActGov, ContrAgent and AgentSpec supply rule gates; CaMeL separates trusted flows; Cedar checks arguments. Our proposed contribution combines intent provenance, abstention and source-checked model evidence. We will ablate provenance and quote checking against input-matched policy-only and model-only guards at a fixed review budget on freshly adjudicated, scenario-disjoint tasks.

## Evaluation plan and first results
**Historical replay.** Published gpt-4o and Claude-3.5-Sonnet retail runs yielded 2,018 writes. Here, 'good' means ground-truth-equivalent DB effects; 'harmful' means accepted but non-equivalent, not adjudicated safety. Development-selected configurations were evaluated on parity-held-out task IDs within overlapping scenarios (991 calls: 702 good, 167 harmful, 122 tool-rejected). Code-review corrections used test evidence; these are exploratory results from one post-review rerun. The deterministic guards' 95% percentile CIs resample tasks across models.
- Schema checks catch 0%.
- Our untuned, policy-derived checker stops (blocks or holds) **68% (95% CI 57–77)** of harmful calls, but blocks 7% of good calls and holds 56%.
- Tuned: **68/167** harmful-labelled stops (**41%; 95% CI 28–55**), comprising **3 blocks/65 holds**; good-labelled calls: **14/702 blocked (2.0%)**, **213/702 held (30%)**. In-process retail p95: **0.5 ms** (median of 7 runs per call), excluding model/framework/human time.
- It does not beat the untuned checker's score; it is a different point on the curve.
- **LLM judges:** same stratified 300 calls. gpt-4.1-mini stopped 42/120 harmful calls, or 44/120 at a test-selected threshold, versus strict Tier 0's 61/120. Each stopped 41/120 good calls. Judges receive truncated transcripts; Tier 0 also reads the database. This is exploratory: the paired 95% CI for strict minus thresholded judge is −3 to +32 points.
- **Cascade:** gpt-4.1-mini released 11 good-labelled and 4 harmful-labelled holds. Good-call holds fell 31/120 to 20/120, but harmful catch fell 57/120 to 53/120; good blocks stayed 2/120. API-token cost: about $0.00036/sampled-call versus $0.0014 for the judge (estimated), excluding human/local costs. Qwen3-1.7B converted 11/85 holds to blocks, including 5 DB-good calls.

**Misses.** The first-run 20-miss audit found eight user-confirmed disagreements and eight wrong-entity choices. All eight wrong-entity calls still pass Tier 0 and never reach the resolver. Hidden-only preferences may be unobservable.

**Independent synthetic red team.** A different-family author, blinded to the checker, wrote 160 cases. After fixes, 82/100 bad calls were stopped (Wilson 95% CI 73–88); 5/60 good calls were blocked and 14/60 held. This is a designed challenge set, not a deployment sample; self-authored tests are regression checks.

## Feasibility and risks
- **Team:** [TEAM: names and skills.]
- **Compute:** laptop checks, metered gpt-4.1-mini API, local Qwen3 offline.
- **Milestones:** 25 Oct live LangGraph agent · 1 Nov entity-binding checks + model tier · 10 Nov calibrated thresholds · 17 Nov demo freeze · 19–25 Nov exams (no work) · 1 Dec progress report · December hardening.
- **Risks:** modest catch on real errors (we publish the curve); rules brittle on paraphrase (model tier, independent suites); users confirming wrong actions (check against earlier stated wants).
