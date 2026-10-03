# Perceptron P9 · Catching an agent before it acts on a bad idea — Thought Node

> Journal for `perceptron-p09-agent-guardrail/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 0 done → 1 (research) + 2 (components) + 4 (walking skeleton) in parallel. Updated 02:58 IST.
- **Plan (to 08:30):** (1) research fan-out → `research/landscape.md`; (2) component map + typed contracts; (3) walking skeleton: trading-desk agent with real tools + reference KB, pre-execution checker, red-team suite → real catch rate / false-block rate / latency numbers vs baselines; (4) ADR 001 spike via six hats + adversarial review; (5) abstract + architecture diagram + selection memo; (6) first ratchet loop on the spike.
- **Doing:** lead: contracts + skeleton. Research sub-agents: r5 (routing/AI control/pre-trade rules) running; r1/r2/r4/r6/r7 relaunching with narrower scope (first batch died on API 408 timeouts, 0 output).
- **Next:** relaunch research → build env + checker + eval → baselines → ADR → deliverables.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** sub-agent API instability (4 of 7 research agents failed on 408s) → lead does critical research directly, agents write incrementally; shared 24 GB Mac with 19 sibling projects → small local models (Qwen3-1.7B/8B 4-bit MLX), NLI models <500 MB; GitHub Models endpoint returns a stub "OK" here and Azure has no AI resources → everything runs locally (also makes the finals demo offline-safe).

## Phase 0 — constraints and "what we must show" (from `_briefs/perceptron.txt`, read 4 Oct 02:05 IST)
- **Hard rules:** team ≤3 students; one problem per team (P9 *or* P10 within Theme 6, and one of the 10 overall); original work; submission only by the team leader via the Techfest portal; queries only via the portal's Doubt section. Round 1 is plan-only ("code, results, or working prototypes" not required) — but real numbers make the plan credible. Finals need a working build demonstrating the MVP (+ stretch goals attempted); scores normalised across all ~30 finalist teams, top 3 overall win.
- **Judging → evidence we must be able to show:**
  | Criterion (weight) | What we show |
  |---|---|
  | Problem understanding (20%) | The crux in our words: an action can be well-formed yet ungrounded; absence of evidence ≠ contradiction; the checker itself can hallucinate; every check costs latency and false blocks cost utility; irreversible actions need stronger evidence than reads. |
  | Technical soundness (25%) | Named stack that runs on a laptop: LangGraph agent, typed tool contracts, deterministic checks + NLI + local LLM tiers, a policy engine; measured overhead. |
  | Novelty (20%) | Beyond "LLM-as-judge on the tool call": argument-level provenance (every argument must cite a source span) + risk-tiered cascade with calibrated thresholds — the pre-trade-risk-check discipline applied to agents. |
  | Clarity (10%) | One diagram, concrete metrics, no buzzwords. |
  | Evaluation rigor (15%) | Red-team suite with typed hallucination classes; catch rate, false-block rate, latency p50/p95, cost; baselines: no guard, schema-only, LLM-judge; held-out split; public benchmark replay if feasible. |
  | Team fit (10%) | Week-by-week milestones avoiding the 19–25 Nov exams; roles for 3. |
- **MVP mapping:** (a) checker verifying ≥1 action class against a source before execution → order/transfer actions checked against instrument reference data, limits and policy KB; (b) demo catching ≥1 deliberately bad action → red-team suite + live agent episode. **Stretch:** risk-routed fast/careful verifier cascade; red-team suite.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 9 — Catching an Agent Before It Acts on a Bad Idea** (Theme 6: AI You Can Actually Trust — teams choose Problem 9 or 10)
- **Context:** Agents that call tools and take multi-step actions can hallucinate a plausible but ungrounded action.
- **Challenge:** Build a guardrail layer that checks a proposed action against a verifiable source before it executes.
- **Starter resources:** An existing agent framework (LangChain/LangGraph or similar) plus a small reference knowledge base for grounding checks.
- **Minimum Viable:** build a checker that verifies at least one class of agent action against a source before execution; demonstrate it catching at least one deliberately bad/hallucinated action.
- **Stretch goals:** add routing between a fast/cheap model and a slower/careful one based on risk; a small red-teaming test suite.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Frameworks: LangGraph interrupts / pre-tool hooks, NeMo Guardrails, Guardrails AI, Llama Guard, Invariant Labs' trace analyzer, MCP tool schemas.
- Benchmarks: AgentDojo, τ-bench / τ²-bench, ToolEmu, AgentHarm — plus 2025–2026 agent-safety work.
- Ideas: retrieval + entailment grounding, typed pre/post-conditions (design by contract), dry-run simulation of side effects, two-phase commit for actions, risk-based routing between cheap and careful models.
- What companies ship: agent-security products and the guardrail designs published by frontier labs and agent-platform companies.

## Key decisions
- _(none yet)_

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (a team can submit only one of the 10 Perceptron problems; the Supervisor ranks all 10 from these memos). Score each 1–5 with one line of evidence._
- **Winnability:**
- **Innovation headroom** (the spike, and why it beats the obvious baseline):
- **Feasibility by the deadline** on an M5 Mac (+ Azure), around the 19–25 Nov exams:
- **Demo strength** at the finals:
- **Fit with the user's strengths** (large-scale systems, frontier models):
- **Biggest risk:**
- **One-line pitch:**

## Log
### 2026-10-04 02:58 IST — Phase 0 done; research fan-out partly failed
- Read PLAYBOOK, seeded brief, and the official statement (`_briefs/perceptron.txt`); extracted rules and judging → evidence table (above).
- Environment: Apple M5, 24 GB RAM (~34% free with siblings running), 70 GB disk free; Python 3.11 + uv; MLX models cached (Qwen3-8B-4bit, Qwen3-1.7B-4bit, Qwen3-0.6B); Ollama present. Azure: VS Enterprise subscription, no Cognitive Services accounts. `models.github.ai` returns a bare `200 OK` stub from this machine → unusable. **Assumption:** run every model locally (MLX + small NLI); this also keeps the finals demo offline.
- Launched 7 background research agents at 02:12; 4 failed with `408 Timed out reading request body` after 19–42 min and wrote nothing; 2 vanished; r5 still running. Relaunching narrower threads that write incrementally.
- Assumption (domain): main demo domain = a synthetic trading-desk operations agent (orders, transfers, client messages) checked against instrument reference data, risk limits, a restricted list and a policy KB — chosen because the judges are Optiver and pre-trade risk checks are the industry's own version of "check before it executes". Public benchmark replay (τ-bench) for external validity if logs are available.

### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.
