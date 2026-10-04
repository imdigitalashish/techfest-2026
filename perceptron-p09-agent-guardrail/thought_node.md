# Perceptron P9 · Catching an agent before it acts on a bad idea — Thought Node

> Journal for `perceptron-p09-agent-guardrail/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** DEMO phase (PLAYBOOK §11). Demo built and verified from a clean clone; visual fixes and the astra demo review in progress. Round-1 package final pending [TEAM] details. Updated 12:46 IST, 4 Oct.
- **Deliverables:**
  - `deliverables/round1-abstract.md`: 877 words. All 22 quoted numbers are verified against `eval/results/` and the τ-bench README by `eval/check_docs.py`, which is part of pytest (7/7 pass).
  - `deliverables/architecture.md`: diagram.
  - `deliverables/mvp-demo-output.txt`: MVP demo (`python -m eval.demo_mvp`).
- **Evidence (all exploratory where stated; details in `eval/taubench/README.md`):**
  - **Real agent errors.** 2,018 historical τ-bench write calls (gpt-4o, Claude-3.5-Sonnet). Labels are DB-effect equivalence with ground truth, not adjudicated safety. Parity-held-out tasks within overlapping scenarios: 991 calls (702 good / 167 harmful / 122 rejected). One post-review re-run; the first run is archived.

    | Config (full test) | Stops harmful [95% CI] | Blocks / holds on harmful | Good blocked | Good held |
    |---|---|---|---|---|
    | none / schema | 0% | — | 0% | 0% |
    | v0 (untuned) | 67.7% [56.9, 77.2] | 6 / 107 | 7.3% | 55.8% |
    | **balanced** | **40.7%** [28.3, 55.1] | 3 / 65 | **2.0%** | 30.3% |

  - **300-call sample:**
    - gpt-4.1-mini judge: 35.0% stopped, 11.7% of good calls blocked.
    - Qwen3-1.7B judge: 28.3% / 26.7%.
    - Strict Tier 0: 50.8% / 1.7%.
    - Paired difference, strict minus thresholded gpt-4.1-mini judge: +14.2 pp [−3.2, +31.7], not significant. Balanced minus the 1.7B judge: +19.2 pp [3.0, 36.5].
    - Hosted cascade: good-call holds 31 → 20 of 120, but harmful catch 57 → 53 of 120 (paired −3.3 pp [−7.3, −0.8]). Cost about $0.00036 per guarded call vs $0.0014 for the judge.
  - **Independent red team** (gpt-6-astra, blinded, 160 cases), post-fix: 82/100 stopped [73, 88]; 5/60 good blocked; 14/60 held.
  - **Known gap:** all 8 audited wrong-entity misses pass Tier 0, so the model tier never sees them. Entity-binding routing and value-bound quote checks are designed but deliberately not applied before a fresh holdout.
- **Reviews** (`reviews/ledger.tsv`):
  - gpt-6-sol (code/eval): 11/11 accepted.
  - gpt-6-astra (hostile judge, abstract scored **3.10/5 = 62/100**): 21/21 accepted (12 edits applied, 2 modified).
- **Next (after Round 1, or when the Supervisor reassigns the slot):**
  1. Scenario-grouped holdout.
  2. Adjudicated consent/policy labels.
  3. Entity-binding routing + value-bound quotes.
  4. Input-matched policy-only and model-only ablations at a fixed review budget.
  5. Live LangGraph agent with closed-loop repair.
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
_Final, 4 Oct 2026 (v4). Re-scored after both cross-model reviews; supersedes v1 (4.6, synthetic only) and v3 (4.4). Every number is in `eval/results/` and checked by `eval/check_docs.py`._

- **Winnability — 3.** The gpt-6-astra hostile judge scores the final abstract **3.10/5 (62/100)**: "plausibly shortlisted, but borderline".
  - For: rare rigour for Round 1. Held-out real agent errors, task-clustered and paired CIs, frontier-model baselines, a blinded red team by a different model family, and two cross-model reviews whose 32 issues were all accepted and acted on.
  - Against:
    - modest catch on real errors (40.7% at 2% false blocks);
    - an advantage over a gpt-4.1-mini judge that is pointwise but not significant (paired CI crosses zero);
    - the reused (post-review) test.
- **Innovation headroom — 3.** Components exist in prior art: rule gates (ActGov, AgentSpec, ContrAgent), flow separation (CaMeL), argument checks (Cedar). The defensible novelty is the intent-provenance + abstention + source-checked-evidence combination, plus an isolating ablation at a fixed review budget. A concrete open target remains: wrong-entity binding.
- **Feasibility — 5.** Everything is built and reproducible with one command per stage. Local plus a metered gpt-4.1-mini (about $0.00036 per guarded call). All remaining milestones fit before 17 Nov.
- **Demo strength — 4.** The desk demo is crisp: an invented ticker, a ×10 order, a side flip and an injected transfer are stopped in under 1 ms with the clause cited. The trade-off curve against an LLM judge is a strong, honest slide.
- **Fit with the user's strengths — 5.** Agent infrastructure, evaluation at scale, frontier models; Microsoft's agent guardrails are among the shipped comparators.
- **Biggest risk:** judges reading "built from known parts, modest catch" as incremental. Mitigation: lead with the evaluation design (real errors, frontier baselines, paired CIs, blinded red team) and the falsifiable ablation plan.
- **One-line pitch:** *Pre-trade risk checks for AI agents: bind every argument to the user's request, and measure the trade-off on real agent errors. On the same 300 τ-bench calls, it stops 48% of harmful calls while blocking 1.7% of good ones; a gpt-4.1-mini judge stops 35% and blocks 11.7%.*
- **Overall: 3.8 / 5.** Recommendation: a solid, low-risk Perceptron pick whose claims are modest but survive adversarial review. Choose it over P7 if P7's spike stays unreplicated; it will not win on novelty alone.

## Log
### 2026-10-04 20:15 IST — Demo built; lead verified from a clean clone
- **Builder pushed the demo** (`f3446ba`).
- **Screens:** (1) REAL τ-bench errors: no guard (τ-bench tool DB diff) vs LIVE Tier 0 vs REPLAYED gpt-4.1-mini judge; (2) "Hijack the agent": typed ticket → SCRIPTED agent → LIVE guard, plus a benign control; (3) knob over 300 real calls against the judge's curve; (4) SYNTHETIC desk; (5) "what this does not show".
- **Lead clean-clone check:** first visual 0.2 s (recorded gallery), live page 2.3 s, `smoke.sh` 83/83 ALL PASS. Endpoints OK; the hijack engine probed with 6 tickets × 3 scenarios gave only blocks or "agent ignored", and controls allowed. Bundle 0.52 MB gz.
- **Builder's finding:** contraction tokens (I'm → "m" = size M) produce wrong reasons. Impact measured (15 decisions on balanced test) and documented as a known issue; deliberately not fixed against test data.
- **Requested two visual fixes:** the screen-1 DB-diff wrapping and the sticky-header artifact in the fallbacks. Started the gpt-6-astra "judge watching the demo" review.

### 2026-10-04 19:39 IST — Demo proposal approved
- **Builder's proposal:**
  1. REAL τ-bench harmful write: unguarded vs live Tier 0 vs replayed gpt-4.1-mini judge;
  2. crazy element "Hijack the agent": the judge types a support ticket, a SCRIPTED compromised agent obeys it, and the real committed guard runs live with the ticket as an untrusted observation, plus a benign control;
  3. operating-point knob over 300 real calls against the judge's curve, with an honesty panel;
  4. SYNTHETIC desk cases.
- **Probe results:** 0/300 mismatches for six configs; 7/7 injections over 5 real conversations blocked; benign controls allowed. Before today's fix, the address hijack and order swap were allowed.
- **Approved, with notes:** curated attack templates + honest free text (literal-value taint limit shown); a precomputed "unguarded outcome" DB diff; on-screen labels REAL/SCRIPTED/SYNTHETIC/REPLAYED/LIVE; the full §11 bar; no git stash; `pipefail`.

### 2026-10-04 19:35 IST — Demo phase started (PLAYBOOK §11)
- **19:29 Supervisor:** demo slot granted. Rules: 1 demo-builder child, CPU only, `nice -n 10` + memory guard, no git stash, replay committed judge outputs. Spawned **P9 demo builder** (autopilot) with full context and an approval gate on its proposal.
- **Bypass found and fixed while preparing the injection moment.** The retail adapter ignored trust labels: an injected ticket naming another of the user's orders made the guard ALLOW the cancellation. It now enforces the untrusted-text rule (P-1.3): a value seen in untrusted text that the user never stated → FAIL `provenance.untrusted`. All 18 committed τ-bench result files were re-run: decisions and reasons identical (no τ-bench item has untrusted observations). Regression tests in `tests/test_retail_injection.py`.
- **My mistake:** I committed while `check_docs` was failing, because a `| tail` pipe masked the exit code. Single-shot wall-clock latency under load (load average about 10) pushed v0 p95 above 1 ms. Fixed in `9b3bee3`: latency now comes from a repeat-timed benchmark (`eval/taubench/latency.py`: p95 0.5 ms wall, 0.48 ms CPU, median of 7 runs per call), and the abstract quotes that. Commit chains now use `set -o pipefail`.

### 2026-10-04 12:46 IST — Hostile-judge review applied; final package; DONE
- **gpt-6-astra hostile judge** scored the 4566887 abstract 3.10/5 (62/100) with 12 exact edits and 9 methodology demands. All 21 accepted (`reviews/2026-10-04-abstract-gpt-6-astra.md`). Key corrections:
  - the wrong-entity misses never reach the model tier;
  - Cedar *does* check arguments, so the "shipping tools don't" claim is gone;
  - the strict-vs-gpt-4.1-mini advantage has a paired CI crossing zero;
  - the stale local-judge CI was recomputed from stored rows;
  - "no paid APIs" contradicted the metered tier.
- **Supervisor (12:37):** fixed the stale README test-history line and added README claims to `check_docs`.
- **Provenance:**
  - added `code_sha256` to every result;
  - re-ran all deterministic guards on clean commit `d20d3e7`, with decisions verified identical row by row;
  - recomputed LLM-row metrics without regeneration;
  - removed three superseded morning "every3" desk results.
- **Incident (my mistake):** `git stash` is shared across worktrees. A sync of mine ran `git stash; …; git stash pop` on a clean tree, so the pop applied another session's `autostash` (P7 `eval/results/phase-v2c/episodes.csv`) into my worktree and conflicted. I restored that file to `main` in my worktree and left the shared stash entry untouched for P7. I no longer use `git stash`; syncs copy files aside instead.

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
