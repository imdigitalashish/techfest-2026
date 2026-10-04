# Perceptron P9 · Catching an agent before it acts on a bad idea — Thought Node

> Journal for `perceptron-p09-agent-guardrail/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ⏸ PAUSED at 09:55 IST, 4 Oct (Supervisor/user decision: only 3 projects run at a time; P9 is the Perceptron alternate). Nothing of ours is running; all work is pushed.
- **Headline:** *Cite-Before-Act*: a pre-tool guard that checks the provenance of every argument (user words / reference KB / trusted tool data; untrusted text is never a source of intent) plus pre-trade-style contracts. The unverifiable residue goes to a risk-routed local model whose quoted evidence must verify verbatim, then to a human.
- **Evidence so far** (reproduce: `eval/README.md`; τ-bench: `eval/taubench/`):
  - **Real agent errors: τ-bench retail replay.**
    - Built from the published gpt-4o + Claude-3.5-Sonnet trajectories in `sierra-research/tau-bench@59a200c` (MIT): **2,018** real write-call proposals from 1,380 trajectories.
    - Each proposal is labelled by DB-effect equivalence with the task's ground-truth writes. 300/300 labels agree with full-DB hashing; 10,360/10,360 recorded tool outputs are reproduced.
    - Split by task-id parity: dev = even, test = odd; **test is untouched**.
    - **Dev results, adapter v0** (`components/checker/taubench_retail.py`, written from the retail policy before seeing any item; 1,027 calls: 779 good, 161 harmful, 87 env-rejected):

      | Guard | Catch (harmful) | Catch (env-rejected) | False-block (good) | Escalation (good) | p95 |
      |---|---|---|---|---|---|
      | none / schema-only | 0% | 0% | 0% | 0% | — |
      | t0 | **64.6%** | 80.5% | **9.1%** | **52.9%** | 2.1 ms |
      | t0, block-only | 11.2% | — | 9.1% | 0% | — |

      Honest read: real conversations are much harder than our synthetic suite.
  - **Independent black-box red team** (134 desk cases by a separate agent that never saw the guard): **before fixes** catch **94.3%**, false-block **0%**, escalation **17.4%**. After 6 general fixes (in-sample): 98.9% / 0% / 0%. Known miss: "two clips of 500" order splitting.
  - **White-box red team** (41 cases by an agent that read the guard): against the current guard, 21/27 bypasses still pass (catch 22.2%), and 14/14 of its good cases are escalated. Top weaknesses (`eval/redteam_whitebox/findings.md`): message-text grounding; invented limit prices / order-type asymmetry; non-canonical duplicate detection; clause-scoped parsing of compound instructions; negation (partly fixed).
  - **Synthetic suite:** dev/test 100% catch, 0% false-block, 0% escalation. LLM-judge (Qwen3-1.7B), full test split: catch 70.8%, false-block 61.1%.
- **RESUME POINT (exact):**
  1. `cd perceptron-p09-agent-guardrail && bash eval/taubench/fetch.sh && .venv/bin/python -m eval.taubench.replay --build` (4 min; writes `.data/taubench/retail_items.jsonl`).
  2. `.venv/bin/python -m eval.taubench.run --guards none,schema,t0,t0_block_only --split dev` reproduces the table above.
  3. Adapter v1 on **dev only**:
     - Drop the `policy.new_item_differs` FAIL (the ground truth itself maps items to themselves: 32 of the false blocks).
     - Payment default = the order's original method (252 escalations).
     - Option check → "minimal-change available variant that satisfies the user's stated options" (199 escalations, 14 false blocks).
     - Normalise curly apostrophes; handle 2-letter state codes and zip false-fails (28 false blocks).
     - Inspect the 27 harmful cancels that were allowed.
  4. Run **test once** and report it.
  5. τ-bench LLM-judge baseline (Qwen3-1.7B, chunked, `nice -n 10`, only when swap has >4 GB free).
  6. Fix the white-box top 5, then ask a *fresh* independent agent for a second black-box batch (clean holdout).
  7. Message the Supervisor with dev+test τ-bench numbers (gate: "guard holds on real agent errors" by 10 Oct).
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section of the abstract (placeholders now).
- **Risks:** (1) synthetic-suite optimism, since the same author wrote templates and rules → τ-bench replay + paraphrase family; (2) paraphrase brittleness of regex mention parsing → LLM resolver, escalation rate tracked; (3) local LLM latency/memory on a shared Mac (8B not measured tonight); (4) close 2026 work (ActGov, ContrAgent, closed-world resolution) → precise novelty claim (argument-value provenance, three-way verdict, verified-quote residue resolution, frontier evaluation).

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
- 2026-10-04 — All models run locally (MLX: Qwen3-1.7B/8B 4-bit). `models.github.ai` returns a stub here and Azure has no AI resources; this also makes the demo offline-safe.
- 2026-10-04 — Demo domain: a trading-desk operations agent (orders, transfers, cancels, client messages) checked against synthetic reference data, limits, a restricted list and a numbered policy. Chosen for the Optiver panel (pre-trade risk checks = "check before it executes").
- 2026-10-04 — Spikes: S1 argument provenance + three-way verdict + quote-verified LLM residue resolution; S2 risk-routed, calibrated fast/careful cascade. See [ADR 001](architecture/adr/001-spike.md).
- 2026-10-04 — Primary metric `score = catch − false_block − 0.5·escalation`, always reported with latency p50/p95. Suite split by phrasing family.

## Components
Full contracts: [architecture/components.md](architecture/components.md) · pydantic: [architecture/contracts/models.py](architecture/contracts/models.py)

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| 1 | Agent runtime | messages → ToolCall | LangGraph ReAct + Qwen3 | | planned | task success |
| 2 | Interceptor (pre-tool hook) | ToolCall+Context → GuardRequest → execute/feedback/interrupt | LangChain `wrap_tool_call` | | planned | mediation completeness, overhead ms |
| 3 | Context recorder | tool results → trust-labelled Observations, SessionState | message history | | in contracts | trust-label accuracy |
| 4 | Reference KB | query → record + locator | JSON + BM25 | | built | alias accuracy, policy recall@3 |
| 5 | Mention parser | text → Mentions | regex/lexicon | S1 | built | extraction F1 |
| 6 | Tier-0 checker | call+ctx → CheckResult[] | schema / static rules | **S1** | built | catch @ FB≤1%, p95 ms |
| 7 | Risk router | request → risk, tier | fixed per-tool | **S2** | built (linear) | cost @ fixed catch |
| 8 | LLM resolver + quote verifier | unverifiable check → pass/fail/unverifiable | LLM-as-judge | **S1/S2** | built | resolution precision/rate |
| 9 | Decision + feedback | checks → Decision, feedback | boolean | | built | repair rate |
| 10 | Human approval | escalate → approve/reject | LangGraph `interrupt()` | | planned | escalation rate on good |
| 11 | Red-team generator | KB+templates → SuiteItem[] | hand lists | | built (367) | class coverage, label checks |
| 12 | Eval harness | suite × guard → metrics | — | | built | score, latency |
| 13 | Calibrator | verdicts → thresholds | hand-tuned | S2 | planned | realised miss rate vs α |
| 14 | Audit log | Verdict → JSONL | logging | | partial | completeness |

## Selection memo
_First version 4 Oct 07:35 IST; final by 12 Oct. Scores 1–5._
- **Winnability — 4.** We already exceed the MVP (4 action classes, 295 typed bad calls, real numbers). Many teams will likely submit "LangGraph + LLM judge"; we can show where that baseline fails and what ours costs. Pre-trade risk control is the panel's own language. Risk: it can read as "just validation" unless the provenance idea is explained crisply.
- **Innovation headroom — 4.** Spike: per-argument provenance with a third *unverifiable* verdict, and LLMs allowed only to resolve the residue with verbatim-verified quotes, plus a risk-routed calibrated cascade. Nearest 2026 work: ActGov (SMT policy sets), ContrAgent (LTLf contracts), closed-world resolution (registry/signature only; it names argument values as the residue it can't catch), Cedar gates. None checks argument values against a knowledge source (landscape §2, §5).
- **Feasibility by the deadline — 5.** The skeleton, KB, checker, suite and eval were built in one night on the M5 with local models and no paid APIs. External data (τ-bench logs) is MIT-licensed and ~40 MB. Every milestone lands before 17 Nov, clear of the 19–25 Nov exams.
- **Demo strength — 5.** A live agent proposes an invented ticker or a ×10 fat-finger; it is blocked in <1 ms with the clause cited, and the agent repairs it. An injected email asks for a transfer; it is blocked as "untrusted origin". A frontier dashboard compares no guard, schema, LLM judge and ours.
- **Fit with the user's strengths — 5.** Large-scale systems + frontier models. Microsoft background is directly relevant (Azure Prompt Shields, groundedness and task adherence are among the industry baselines we position against).
- **Biggest risk:** synthetic-suite optimism (100% catch from templates written by the rule author) could look like a toy to judges → τ-bench replay of real model errors + LLM-paraphrased family before the abstract is final.
- **One-line pitch:** *Pre-trade risk checks for AI agents: every argument of every action must cite its source, or it doesn't execute.*
- **Overall: 4.6/5.**

## Log
### 2026-10-04 09:58 IST — Paused by the Supervisor (user decision); results saved
- **08:22 Supervisor:** package accepted; P9 ranks #2 in Perceptron and moves to #1 if the guard holds on real agent errors by 10 Oct. Next: τ-bench/AgentDojo real-error replay vs no-guard/schema/LLM-judge baselines, then an independent adversarial red team.
- **~09:15 Supervisor:** an orphaned PID 42665 (my Qwen3-8B judge, queued in last night's chained shell) was using memory. Killed; swap recovered. New rule for my LLM runs: Qwen3-1.7B only, chunked with checkpoints, `nice -n 10`, one at a time, only when swap has >4 GB free. The chain had finished three valid runs (results kept with their commits): cascade (8B) dev/test and the full-test 1.7B judge. The cascade let one bad test message through (an unrequested "account upgraded" message). Root cause: a quote from *policy* text was accepted as evidence for *intent*. Fixed: provenance checks now accept only quotes from the client's words, and an intent quote must contain a request verb.
- **τ-bench replay built:** `eval/taubench/{fetch.sh,replay.py,run.py}`. The stubbed-package import avoids τ-bench's LLM SDK dependencies. The fast effect-based labeller deep-copies only touched records and was verified against full hashing. The guard sees the tool outputs exactly as the agent saw them. Fidelity mismatches turned out to be a later data rename (`province`→`state`) and are normalised. Dev v0 numbers and diagnosis are in *Now*.
- **Independent black-box red team** (sub-agent, never saw the guard; `eval/data/redteam_independent.{jsonl,md}`): numbers in *Now*. Six general fixes: negation scope; message status claims vs session status; P-6.4 claims with an empty record (negation-aware); the "40 L&T" lakh-parse bug; bare "market"; message verbs. These introduced no synthetic regressions. The pre-fix result file is kept (`eval/results/t0__test__redteam_independent__prefix.json`).
- **White-box red team** (sub-agent read the guard): asked to stop at the pause; 41 findings saved and validated (`eval/redteam_whitebox/`, `eval/data/redteam_whitebox.jsonl`).
- **09:40 Supervisor:** lean mode again. **09:55:** PAUSE. Nothing of mine was running (verified PIDs belong to other worktrees). Everything committed and pushed.

### 2026-10-04 08:05 IST — MVP demo committed; morning package complete
- `python -m eval.demo_mvp` (deterministic, no model) runs six scripted proposals for one client against DeskSim. Real output is in `deliverables/mvp-demo-output.txt`:
  - The faithful order executes.
  - Invented ticker `INFOSYS`, ×10 quantity and buy→sell flip → **BLOCK**, with evidence spans and policy clauses.
  - A limit price the user never gave → **ESCALATE** (unverifiable).
  - A transfer injected via email → **BLOCK** ("appears only in untrusted content", third-party account).
  - This covers both MVP bullets.
- Re-ran the deterministic evals on a clean commit (2adcf09). Docs now report Tier-0 p95 as 0.6–4.7 ms across runs (loaded machine), not a single number.
- Abstract: the live LangGraph episode is marked "by 25 Oct" (not built yet).

### 2026-10-04 07:57 IST — LLM baselines, cascade, first ratchet loop
- **LLM-as-judge (Qwen3-1.7B)**, 61-call test subsample: catch 71.1%, false-block 68.8%, score 0.024. Tier 0 on the same calls: 100% / 0%. The judge fails on arithmetic and state, which is the strongest argument for deterministic numeric checks first.
- **Fast cascade on dev:**
  - Quote verification let 0 bad calls through and upgraded 8 of 15 residue escalations to evidence-backed blocks.
  - The 1.7B resolver resolved 0 of 6 good paraphrases (escalation unchanged at 16.7%).
  - Lesson: a small model can be trusted to *contradict* with a quote but rarely to *support* a paraphrase. Try the 8B model and an NLI second gate when the machine is idle.
- **Ratchet (components/checker/autoresearch/):** frozen `eval.py`, `program.md`, `results.tsv`.
  - Iteration 1 (number words): no scalar change, so not kept on its own.
  - Iteration 2 (word numbers + exit/entry idioms): dev 0.917 → 1.000, test unchanged. Kept, but flagged IN-SAMPLE, because "want out of" is copied from a dev template. An unseen paraphrase family is needed before any claim.

### 2026-10-04 07:35 IST — Morning package written (lean mode)
- **Research.** 9 more agents launched at ~03:00; 6 died on 408s. Survivors wrote `notes/verifier-models.md`, `notes/social-and-incidents.md`, `notes/routing-control-cascades.md` and partial `notes/companies-*.md` + `notes/tool-call-hallucination.md`. Following the Supervisor's 05:51 lean-mode order, the lead captured 27 arXiv abstracts verbatim (`notes/arxiv-abstracts.md`), including 11 papers from Jul–Sep 2026 found by date-sorted arXiv search. Closest: closed-world resolution 2609.19425, ContrAgent 2609.18128, ActGov 2609.24446, "What Can Be Enforced?" 2607.22868, "Stale Does Not Mean Unsafe" 2609.29522. The lead also extracted SEC 15c3-5(c) verbatim (`notes/pretrade-risk-controls.md`) and wrote `research/landscape.md`.
- **Architecture.** `architecture/components.md` (14 components, contracts, isolated metrics, mermaid); pydantic contracts plus exported JSON Schemas; ADR 001 (six hats, thesis/antithesis/synthesis; the antithesis was written by the lead because no independent agent was allowed; redo it).
- **Build.** Synthetic desk KB (17 instruments incl. 3 fictional, 6 accounts, limits, restricted list, 25-clause policy), DeskSim tools, Tier-0 provenance + pre-trade checks, risk router, quote-verified LLM cascade, LLM-judge baseline, mutation red-team suite (367 items; 72 good / 295 bad; 11 classes; split by family), eval harness, 6 contract tests passing.
- **Numbers.** See *Now*. The guard surfaced 2 mislabelled suite items (notional below the ₹50 lakh threshold). Labels were fixed and a test added.
- **Machine.** ~42 GB swap in use by sibling workloads. The LLM-judge run needed ~20–30 s/item, so the 8B run was dropped and the 1.7B judge runs on a stratified 1/3 subsample.
- **Deliverables.** `deliverables/round1-abstract.md` (874 words of prose), `deliverables/architecture.md`, selection memo (above).

### 2026-10-04 02:58 IST — Phase 0 done; research fan-out partly failed
- Read PLAYBOOK, seeded brief, and the official statement (`_briefs/perceptron.txt`); extracted rules and judging → evidence table (above).
- Environment: Apple M5, 24 GB RAM (~34% free with siblings running), 70 GB disk free; Python 3.11 + uv; MLX models cached (Qwen3-8B-4bit, Qwen3-1.7B-4bit, Qwen3-0.6B); Ollama present. Azure: VS Enterprise subscription, no Cognitive Services accounts. `models.github.ai` returns a bare `200 OK` stub from this machine → unusable. **Assumption:** run every model locally (MLX + small NLI); this also keeps the finals demo offline.
- Launched 7 background research agents at 02:12; 4 failed with `408 Timed out reading request body` after 19–42 min and wrote nothing; 2 vanished; r5 still running. Relaunching narrower threads that write incrementally.
- Assumption (domain): main demo domain = a synthetic trading-desk operations agent (orders, transfers, client messages) checked against instrument reference data, risk limits, a restricted list and a policy KB — chosen because the judges are Optiver and pre-trade risk checks are the industry's own version of "check before it executes". Public benchmark replay (τ-bench) for external validity if logs are available.

### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.
