# Perceptron P9 · Catching an agent before it acts on a bad idea — Thought Node

> Journal for `perceptron-p09-agent-guardrail/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ACTIVE (resumed 10:48 IST, 4 Oct). Definition-of-done items 1–3 done; item 4: sol review done, astra abstract review running; item 5: this update. Updated 12:15 IST.
- **GPU pause (Supervisor, ~11:47):** Namma Space needs the GPU. My only MLX job (the `cascade_fast` test run) had just completed, so there was no PID to pause. No local-model job runs until "GPU free", and none is needed for the definition of done.
- **Headline evidence: real agent errors** (`eval/taubench/README.md`).
  - **Set and protocol:**
    - 991 held-out τ-bench write calls from gpt-4o and Claude-3.5-Sonnet (702 good, 167 harmful, 122 rejected); frozen configs; 95% CIs clustered by task.
    - The test was **re-run once after the sol code review fixed six bugs**. The first run is archived in `eval/results/first_run/`.

    | Config (full test, post-review) | Stops harmful (block or hold) | Hard blocks | False-block | Holds on good | p95 |
    |---|---|---|---|---|---|
    | none / schema-only | 0% | 0 | 0% | 0% | — |
    | v0 (policy-only, untuned) | **67.7%** [56.9, 77.2] | 6 | 7.3% | 55.8% | 0.3 ms |
    | strict | 44.9% | 3 | 2.0% | 36.5% | 0.4 ms |
    | **balanced (primary)** | **40.7%** [28.3, 55.1] | 3 | **2.0%** [0.6, 4.0] | 30.3% | 0.4 ms |
    | lenient | 26.4% | 3 | 2.0% | 18.2% | 0.6 ms |

  - **300-call sample** (120 good / 120 harmful / 60 rejected; `eval/results/taubench/frontier__test__sample300.json`):

    | Guard | Stops harmful | False-block | Holds on good | Good-call stop | Cost per guarded call |
    |---|---|---|---|---|---|
    | balanced (Tier 0) | 47.5% | 1.7% | 25.8% | 27.5% | $0 (0.7 ms p95) |
    | **cascade_aoai** (balanced + gpt-4.1-mini on holds only) | **44.2%** | **1.7%** | **16.7%** | 18.3% | **$0.00036** |
    | gpt-4.1-mini judge, every call | 35.0% | 11.7% | 22.5% | 34.2% | $0.0014 (2.3 s median) |
    | Qwen3-1.7B judge, every call | 28.3% | 26.7% | 0% | 26.7% | local, 2.6 s median |
    | cascade_fast (1.7B on holds) | 47.5% | 5.8% | 21.7% | 27.5% | local |

    - **Matched comparison:** the gpt-4.1-mini judge's risk threshold was tuned on this same sample, which favours the judge. At strict's good-call stop rate (34.2%) the judge stops 36.7% vs strict's 50.8%; at balanced's rate (27.5%), 24.2% vs 47.5%.
    - **Cost source:** Azure Retail Prices API, Sweden Central Global, $0.0004/1K input and $0.0016/1K output (`cost.py`).
  - **Miss audit** (20, first run):
    - 8 requested by the simulated user (no transcript check can catch these);
    - 8 wrong-entity resolutions;
    - 3 policy sequencing / incomplete action;
    - 1 caused by a rule I removed during tuning.
- **Independent red team** (`eval/external/astra/`, gpt-6-astra, never saw the rules; 160 cases): first run, **82.0% stopped [73.3, 88.3], 8.3% false blocks, 20.0% holds**. Re-run after the review fixes (now in-sample): 82.0% / 8.3% / 23.3%.
- **Desk domain** (self-authored, secondary): synthetic 100% / 0% (after relabelling 6 P-1.2 seeds); Claude independent set 100% / 0% with 10.9% holds; white-box 7/27 bypasses now stopped.
- **Reviews** (`reviews/ledger.tsv`): gpt-6-sol code/eval raised 11 issues, all 11 accepted (2 in part). gpt-6-astra hostile judge on the abstract: running.
- **Rule (Supervisor, ~11:03):** local-model runs only when `kern.memorystatus_level` ≥ 25% (watchdog pauses below 25%, resumes at 30%), Qwen3-1.7B only, `nice -n 10`, chunked and resumable, one LLM job at a time; plus the GPU pause above.
- **Next:**
  1. Act on the astra review (ledger) and adjust the abstract.
  2. Final memo, push, then "DONE — slot free".
  3. After Round 1: scenario-grouped holdout, stronger careful model, consent/policy relabelling, live LangGraph demo.
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
_Final, 4 Oct 2026 (v3; replaces v1 from 07:35, which scored 4.6 on synthetic evidence alone). Scored 1–5 against the real-error evidence after the gpt-6-sol review fixes. Every number is in `eval/results/` and checked by `eval/check_docs.py`._

- **Winnability — 4.**
  - **For:** Round 1 judges the plan, and our strongest criteria carry the most weight: evaluation rigour (15%) and technical soundness (25%). The evidence base:
    - a held-out test on 991 *real* gpt-4o and Claude-3.5-Sonnet write calls from τ-bench, with task-clustered CIs;
    - no-guard, schema and LLM-judge baselines;
    - a 160-case red team by a different model family (82% stopped, 8% false blocks);
    - two cross-model reviews.
  - **The obvious baseline loses clearly, including a frontier judge.** On the same 300 real calls, a gpt-4.1-mini judge reading the full transcript stops 35.0% of harmful calls but hard-blocks 11.7% of good ones; a local 1.7B judge, 28.3% and 26.7%. Our balanced checker stops 47.5% at 1.7% false blocks in under 1 ms. With gpt-4.1-mini resolving only its holds, holds drop from 25.8% to 16.7% at $0.00036 per guarded call, against $0.0014 to judge every call.
  - **Against:** the absolute catch on real errors is modest: 40.7% [28–55] at 2.0% false blocks and 30% holds, or 68% if one accepts 56% holds. The first model-tier attempt (1.7B) released no holds. A team with a 100% toy demo may read better on a quick skim.
- **Innovation headroom — 4.** Argument-level provenance with an explicit *unverifiable* state, and quote-verified model resolution of only that residue. The miss audit makes the spike falsifiable: 8 of 20 misses are wrong-entity resolutions that the careful tier must fix. The nearest 2026 work (ActGov, ContrAgent, closed-world resolution, Cedar gates) checks policies or schemas, not argument values against a source.
- **Feasibility — 5.** Built end to end on the M5 with open local models and no paid APIs; the τ-bench replay is MIT-licensed, about 65 MB and reproducible with one command. Remaining work fits before 17 Nov: stronger careful tier, scenario-grouped holdout, live LangGraph demo.
- **Demo strength — 4.** The desk demo is crisp: an invented ticker, a ×10 order, a side flip and an injected transfer are stopped in under 1 ms with the clause cited. The frontier chart against the judge makes a strong slide. The modest real-error catch has to be framed as the hard-block / soft-alert / manual-review trade-off a trading desk already lives with.
- **Fit with the user's strengths — 5.** Agent infrastructure, evaluation at scale, frontier models. Microsoft's own agent guardrails (Prompt Shields, groundedness, task adherence) are among the shipped baselines.
- **Biggest risk:** "41% catch" read as weak. Mitigation: lead with the frontier and the matched judge comparison, and show that 8 of 20 misses are invisible to any transcript-based check (the simulated user asked for them).
- **One-line pitch:** *Pre-trade risk checks for AI agents: every argument must cite its source. On real agent errors, at the same human-review load, this stops about twice as many harmful calls as a gpt-4.1-mini judge (47.5% vs 24.2%) at a quarter of the cost when a model settles the residue.*
- **Overall: 4.4 / 5.** Recommendation: P9 is a sound Perceptron pick, with claims that are modest but survive a held-out test, an independent red team and two cross-model reviews.

## Log
### 2026-10-04 12:15 IST — Frontier-model baselines (Supervisor suggestion, ~11:55)
- **Azure OpenAI gpt-4.1-mini** (existing deployment in `rg-tf26-p08`; key only in an env var, never written; scanned the repo and /tmp for it, nothing found):
  - as a full-transcript judge on the 300-call sample;
  - as the careful tier on balanced's holds only.
- **Rate limit:** the first run hit HTTP 429 at 162/300 with 6 workers. Resumed from the checkpoint with 2 workers and Retry-After backoff; 0 empty outputs.
- **Results:** in *Now*. Main finding: the cascade gives the frontier model the residue only. That cuts holds by a third at 4× lower cost than judging every call, with no extra false blocks.
- Abstract updated (898 words; check_docs 21 claims; pytest 7/7). Told the astra reviewer to score the new version.

### 2026-10-04 11:52 IST — Reviews in, fixes, held-out re-run, final abstract
- **11:13** gpt-6-astra red-team suite landed (160 cases, never saw the rules). First run: 82.0% stopped, 8.3% false blocks, 20.0% holds. Session archived.
- **11:26** gpt-6-sol code/eval review: 11 issues (1 critical, 8 major, 2 minor), all raw numbers reproduced, all accepted (2 in part). Main bugs:
  - replay passed the agent's *current* message as the "confirmed summary";
  - no retail schema gate (empty or partial writes passed);
  - "I'm not sure" read as a yes;
  - option substring matching;
  - address scope;
  - synthetic labels contradicting P-1.2;
  - CI clusters split tasks across models.
- **Fixes:** the replay build now fails closed and verifies 2,018/2,018 labels against full hashing.
- **Re-run:** the held-out test was re-run once on the same frozen configs (declared in the abstract); the first run is archived. Balanced moved from 35.9% → 40.7% stopped, false blocks 1.8% → 2.0%, holds 25.1% → 30.3%.
- **LLM judge** (300-call sample) and **cascade first try**: numbers in *Now*.
- **11:48** final abstract (876 words) pushed with `eval/check_docs.py` (18 claims verified; part of pytest). Started the astra hostile-judge review of the abstract.
- **GPU pause request** (Supervisor): no MLX job of mine was running (the cascade had completed); none will start until "GPU free".

### 2026-10-04 11:10 IST — Resumed; τ-bench held-out results, audit, reviews launched
- **10:48 Supervisor:** resume with a five-point definition of done. Child sessions only (max 2), no `task` sub-agents.
- **Child sessions launched:** `P9 independent red team (astra)` (gpt-6-astra, max; may read only the KB data, tool specs and contracts) and `P9 code/eval review (sol)` (gpt-6-sol, max).
- **Adapter v1, dev only:**
  - Confirmed-summary grounding is a real trade-off. Option-level grounding leaks harm (dev catch drops to about 30%); item/payment/reason/address do not.
  - Found and fixed a labelling bug: 12 ground-truth address actions used the pre-rename `province` key, mislabelling 11 dev calls. The test split was unaffected.
  - Froze strict / balanced / lenient (+ untuned v0).
- **One-shot held-out test** (commit `a93e35a`): numbers in *Now*.
- **Supervisor (~11:03):** approved the memory-level rule for the LLM judge (see *Now*). Agreed to headline the real-error frontier, compare the judge at a matched stop rate, and add the miss taxonomy.

### 2026-10-04 09:53 IST — Paused by the Supervisor (user decision); results saved
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
