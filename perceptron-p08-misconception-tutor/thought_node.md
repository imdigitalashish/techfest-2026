# Perceptron P8 · A tutor that finds the real reason you're stuck — Thought Node

> Journal for `perceptron-p08-misconception-tutor/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- 2026-10-04 09:40 (Supervisor): package and self-correction accepted; next, find where the LLM baseline fails (harder packs, slips, consistency across sessions); if there is no gap, say so plainly in the memo. → Started; plan below.
- 2026-10-04 09:55 (Supervisor): **PAUSE** (user's decision; only Namma Space, P7 and EV C2 run; P7 is the Perceptron pick unless the user overrides). → Paused at 10:00 IST. No jobs were running.

## Now
- **Phase:** 5–6 — **ACTIVE again since 14:58 IST, 4 Oct** (Supervisor batch slot). Goal: find out honestly whether and where the LLM baseline fails, then finalise.
- **Definition of done (Supervisor 14:58):**
  1. Pre-register `eval/llm_gap_protocol.md` and commit it before any run. Then run `real_negatives` (real data), `inversion` and `tracing` (+ `prob_pack` if time) against gpt-4.1-mini **and** gpt-5.4-mini (gpt-5.5 on the decisive parts). If there is no gap, say so plainly.
  2. Re-frame the pitch on that evidence.
  3. Final Round-1 abstract with numbers rendered from committed results, plus a doc-drift check (`eval/check_docs.py`) and the diagram.
  4. Cross-model reviews as child sessions: gpt-6-astra (max) as hostile judge on abstract + spike; gpt-6-sol (max) on code/eval, reproducing the headline numbers → `reviews/` + `reviews/ledger.tsv`.
  5. Final selection memo; push; message the Supervisor "DONE — slot free".
- **Plan:** protocol → runner (`eval/run_llm_gaps.py`; responses saved to committed JSONL so scoring reproduces offline) → runs (bounded; tokens and cost logged per part) → analysis → pitch/abstract/memo → 2 reviews → triage → DONE.
- **Doing:** lead (Opus 5.5) writing the pre-registration. No child sessions (cap 2; reviewers come last). No background jobs.
- **Rules in force:** no `task` sub-agents; ≤2 child sessions; never `git stash`/`--autostash`; timestamps from `TZ=Asia/Kolkata date`; heavy jobs `nice -n 10`, CPU only, start only when `kern.memorystatus_level` ≥ 30; small API batches; poll long jobs ≥10 min apart; Azure keys in env only.
- **Needs from user:**
  - Register by 15 Oct (after the 12 Oct selection).
  - Teammates' names and skills for the team-fit section (abstract has [TEAM] placeholders).
  - A Kaggle login to download the official Eedi 2024 files and confirm the mirror's fidelity.
  - In Nov: ~30 learners for a consented pilot.
  - FYI: Azure OpenAI resource in the VS Enterprise subscription (rg `rg-tf26-p08`; deployments gpt-4.1-mini, gpt-5.4-mini, gpt-5.5). Pay-per-token; delete when no longer needed: `az group delete -n rg-tf26-p08`.
- **Risks:**
  1. The LLM baseline is strong (gpt-4.1-mini 86.0% vs exec→TF-IDF 45.7% on the real 5-category set); reasoning models may close every remaining gap. If so, the memo says P8 has no defensible edge.
  2. Synthetic parts (inversion, tracing) favour the executable side, which shares the generative model (home-field advantage). They must be labelled and weighted below the real-data part.
  3. Simulated learning ≠ real learning.
  4. LaTeX parser covers ~45% of real items.
  5. Eedi 2024 data via an unofficial mirror.
  6. Uplink congestion / Azure flakiness.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 8 — A Tutor That Finds the Real Reason You're Stuck** (Theme 5: AI That Teaches — the theme's only problem)
- **Context:** Struggling with quant reasoning, math, or code usually isn't about missing facts — it's one specific misunderstanding producing the same class of mistake repeatedly.
- **Challenge:** Build a tutoring system that traces a learner's wrong answers back to a likely root misunderstanding and generates targeted follow-up problems.
- **Starter resources:** A public dataset of student errors (e.g. ASSISTments, or a coding-error dataset), or a small hand-built taxonomy of 3–5 common misconceptions if no dataset fits.
- **Minimum Viable:** classify a wrong answer into one of 3–5 misconception categories; automatically generate a new practice problem targeted at that category.
- **Stretch goals:** track a learner's misconceptions across multiple sessions; show some evidence the targeted problems actually reduce that error type over time.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: Eedi "Mining Misconceptions in Mathematics" (Kaggle, 2024 — wrong-answer distractors labelled with misconceptions), ASSISTments, EdNet, student coding-error datasets.
- Learner models: knowledge tracing via `pyKT` (BKT, DKT, SAKT, AKT and newer).
- Methods: LLM retrieval + rerank for misconception classification (see the Eedi winning solutions); generated problems verified by SymPy or code execution; simulated learners to test the "reduces errors over time" stretch.
- What companies ship: AI tutors from ed-tech companies and labs — check their published evaluations.

## Key decisions
- 2026-10-04 — **Spikes:** (A) executable misconceptions → exact diagnosis + SymPy-verified *discriminative* generation; (B) set-level Bayesian tracer + expected-information-gain policy. Retrieval + LLM rerank is kept as the open-set fallback. [ADR 001](architecture/adr/001-spike.md)
- 2026-10-04 — **MVP taxonomy (assumption, not asked):** 5 school-arithmetic misconceptions linked to exact Eedi names: LTR (Kaggle-2024 id 1507), SQ_DOUBLE (2316; graph 15012), SUB_NEG (2566), FRAC_ADD (217), NEG_TIMES_NEG (1597; graph 14310). Probability/EV pack (Optiver-relevant) is the next pack.
- 2026-10-04 — **Data:** label space = Eedi Misconceptions Graph v1.0 (CC BY 4.0). Real eval = Kaggle Eedi 2024 data via HF mirror `cdtmc/eedi-ir` (research use, not redistributed, fidelity UNVERIFIED).
- 2026-10-04 — **Novelty claim narrowed** after finding MalruleLib (ACL 2026): we claim real-distractor validation, discriminative verified generation, set-level EIG tracing, and slip abstention — *not* "executable misconceptions" in general.
- 2026-10-04 — **LLM backend:** Azure OpenAI `tf26-p08-aoai-1004` (rg `rg-tf26-p08`, swedencentral, deployment gpt-4.1-mini 2025-04-14). The key is read at runtime via `az`, never stored. GitHub Models is unusable from this network.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Catalogue | id → Misconception | Eedi graph (CC BY) | — | built | link coverage 5/5 |
| C2 | Normaliser | raw → NormalizedAnswer | Fraction parsing | — | built | canonicalisation acc 8/8 cases |
| C3 | Bug library | Item → PredictedAnswer[] | mal-rules (Sleeman, MalruleLib) | **A** | built (5 bugs); autoresearch loop | reproduction_dev 0.155 → 0.190 (loop iter 2); wrong attribution 0% |
| C4 | Diagnoser | DiagnosisRequest → Diagnosis | LLM zero-shot; retrieval+rerank | **A** | built | closed-set acc (real, n=129): LLM 86.0%, exec→LLM 86.8%, exec→TF-IDF 45.7%, TF-IDF 38.0%, majority 30.2% |
| C5 | Verifier | Item → VerificationReport | none / LLM self-check | — | built | fault detection (mutation suite: to do) |
| C6 | Generator | GenerationRequest → GeneratedItem[] | LLM-only | **A** | built | verified-targeted yield: ours 400/400 (by construction); LLM-only 40/40 |
| C7 | Learner model | state+obs → LearnerState | BKT / pyKT | **B** | built | exact-set acc 0.836 (synthetic) |
| C8 | Policy | NextItemRequest → NextItemDecision | random practice | **B** | built | misconceptions still held after 4 sessions: 5.5% vs 58.4% (synthetic) |
| C9 | Feedback | Diagnosis → text | generic "answer is X" | — | template built | rubric pass rate (to define) |
| C10 | Simulated learners | Item → Response | prompted LLM students | — | built | fidelity vs Eedi option stats (to do) |
| C11 | Tutor + store | CLI → session | — | — | built (CLI) | end-to-end demo across sessions |
| C12 | Open-set retrieval | text → ranked ids | BM25 / Eedi winners | — | baseline | MAP@25 0.326 (kNN, 904 held-out pairs) |

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (a team can submit only one of the 10 Perceptron problems; the Supervisor ranks all 10 from these memos). Score each 1–5 with one line of evidence._
- **Winnability: 3/5** (revised 07:45 from 4 after the LLM baselines). We already have a differentiated, working, evaluated core on day 1. It runs end to end on a laptop (`components/tutor/cli.py`) and has real-data numbers on Eedi distractors (`eval/results/diagnosis.json`). Theme 5 has a single problem, so competition is spread differently (UNVERIFIED how many teams pick it).
- **Innovation headroom: 3/5** (revised 07:45 from 4). GPT-4.1-mini zero-shot already gets 86.0% on our real 5-category set, and LLM-only generation was 40/40 valid on simple arithmetic, so the edge must come from set-level tracing + information gain, exactness/verification, and harder packs. Spike = executable misconceptions validated on *real* distractors → discriminative, SymPy-verified generation → set-level Bayesian tracing with information-gain item choice and slip abstention. The obvious LLM-prompt baseline can't verify its items or tell a slip from a misconception. Also, executable mal-rules exist (MalruleLib ACL 2026; Sleeman), so the claim must stay narrow.
- **Feasibility by the deadline: 5/5.** ms per turn on the M5, no GPU. The LLM is used only for the open-set leg and the bug compiler (Azure OpenAI now provisioned). 12 components behind tested contracts. Exams 19–25 Nov fall after the core milestones.
- **Demo strength at the finals: 5/5.** A judge types a wrong answer; the tutor names the exact rule ("1/8 is what adding tops and bottoms gives"), asks the most informative next question, and shows a verified item and a teacher heat-map. A quant pack (probability/EV misconceptions) speaks to Optiver.
- **Fit with the user's strengths: 3/5.** Evaluation rigour, LLM pipelines and Azure fit. Less large-scale-systems depth than P1/P2. Microsoft ships adjacent products (Math Progress, Study and Learn Agent), which is useful context.
- **Biggest risk:** stretch goal 2 (evidence that targeted practice reduces errors) is convincing only with real learners. Today it is simulation (labelled synthetic). A ~30-learner pilot must happen in Nov, around the exams. Secondary risk: the LaTeX parser covers only 41% of real Eedi items.
- **One-line pitch:** *Wrong answers are outputs of wrong rules — we execute the rules, so we can name the one you used, prove it with the next question, and verify every practice problem we generate.*

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05 IST — Phase 0 done, Phase 1 launched
- Brief verified against `_briefs/perceptron.txt` (matches the seeded Brief). What we must show: MVP = (a) wrong answer → one of 3–5 misconception categories, (b) auto-generated practice problem targeted at that category; stretch = cross-session tracking + evidence the targeted problems reduce that error type. Round 1 is plan-only (600–900 words); finals need a working build.
- Env: Apple M5, 24 GB, 70 GB free disk; Python 3.11 + uv; no Kaggle credentials; HF token present; Azure VS Enterprise subscription active. **Correction (06:30):** I first logged "GitHub Models API works". That was wrong: `models.github.ai` answers every request with HTTP 200 `text/plain` "OK" (a stub, probably network interception), so no GitHub Models result exists anywhere in this project.
- Found official Eedi data on HF: `Eedi/Eedi-Misconceptions-Graph` v1.0 (CC BY 4.0; 8,117 misconceptions, 2,258 constructs, updated 2026-09-16) and `Eedi/Question-Anchored-Tutoring-Dialogues-2k` (CC BY-NC). Kaggle Eedi 2024 data via community mirror `cdtmc/eedi-ir` (4,370 labelled question–distractor pairs, 2,587 misconceptions, 5 folds; no licence stated → research use only, fidelity UNVERIFIED).
- 7 research sub-agents launched.

### 2026-10-04 03:35 IST — Outage
Model API returned "408 Timed out reading request body" for most agents (network saturated; Supervisor confirmed portfolio-wide). 5 of 7 research agents died with no output; relaunched narrower ones that write incrementally. Lost ~85 min.

### 2026-10-04 05:45 IST — Skeleton up
- Assumption (recorded, not asked): MVP domain = school arithmetic with 5 categories linked to exact Eedi misconception names: LTR (Kaggle-2024 id 1507), SQ_DOUBLE (2316; graph 15012), SUB_NEG (2566), FRAC_ADD (217), NEG_TIMES_NEG (1597; graph 14310). Chosen because each is executable, frequent in Eedi's catalogue, and they produce *distinct* wrong answers on shared problem families.
- Built: contracts v0.1.1 (`architecture/contracts/`), bug pack (`components/bugs/school_math.py`: one exact interpreter + 5 composable bug switches), normaliser, SymPy verifier, template-discriminative generator, Bayes diagnoser + LLM zero-shot baseline, set-Bayes tracer with EIG, policies, simulated learners. `pytest components/tests` → 8 passed.
- Supervisor LEAN MODE received 05:45: no new sub-agents; sequential work; push every 30 min.

### 2026-10-04 07:10 IST — Morning package assembled
- **Real-data results** (`python -m eval.run_diagnosis`, Kaggle Eedi 2024 via mirror):
  - Open set: 904 held-out pairs from 388 questions; 27.9% of test labels unseen in train. MAP@25: BM25 0.093, TF-IDF 0.120, kNN-over-train-labels 0.326. Recall@25 TF-IDF+kNN 0.654.
  - MVP closed set (129 distractors labelled with our 5 misconceptions): majority 30.2%, TF-IDF 38.0%, exec→TF-IDF hybrid 45.7%.
  - Executable reproduction 16.3% (39.6% where the LaTeX parses; parse rate 41.1%); wrong attribution 0%; false claims 1.8% of 165 other-labelled distractors (2 of 3 are Eedi near-synonyms of our rules).
- **Generation** (`python -m eval.run_generation`): 400/400 template items SymPy-verified, target fires, discriminative — true by construction. LLM-only baseline running now on Azure.
- **Simulation** (`python -m eval.run_simulation --seeds 3 --learners 150`, SYNTHETIC): share of initial misconceptions still held after 4×8 items — random+generic 58.4%, random+named 32.2%, EIG+generic 27.4%, **EIG+named 5.5%**, oracle 1.1%. Pessimistic setting (naming no better): EIG 28.0% vs random 58.4%.
- **Docs:** landscape.md, components.md, 12 per-component research docs, ADR 001 (six hats, thesis/antithesis/synthesis; independent adversarial review pending), deliverables (abstract v1 + architecture), tutor CLI demo across sessions.
- **Network:** GitHub Models stub (see correction above). Azure OpenAI provisioned 06:40; connections aborted until 07:06, then OK.

### 2026-10-04 07:50 IST — LLM baselines, autoresearch, honest re-scoring
- Azure OpenAI reachable from 07:06. `python -m eval.run_diagnosis --llm-n 129` (with `AZURE_OPENAI_ENDPOINT` set; responses cached in `.cache/llm`): on the real 5-category set, **GPT-4.1-mini zero-shot 86.0%** (95% bootstrap CI 79.8–92.2); exec→LLM hybrid 86.8% (80.6–92.2); exec→TF-IDF 45.7%; TF-IDF 38.0%; majority 30.2%. The exec path is right 21/21 when it fires (LLM 20/21 on those).
- `python -m eval.run_generation --n 40 --llm-n 8`: LLM-only generation 40/40 valid, targeted and discriminative on this simple pack.
- **Lesson:** on simple arithmetic the LLM baseline is strong. Re-scored the selection memo (winnability 4→3, innovation 4→3); updated the abstract's novelty to claim exactness, competitor separation, set-level tracing + information gain, and slip abstention — not accuracy over the LLM.
- Autoresearch C3 (`components/bugs/autoresearch/`): baseline reproduction_dev 0.1552 → iter 1 (prefer key-matching segment) neutral, reverted → iter 2 (trailing "=?", leading minus before a bracket) **0.1897**, kept; holdout unchanged 0.1690; guards OK.
- Abstract v1 trimmed to ≤900 words (by word count).
- Derived numbers (hybrids, 95% bootstrap CIs, exec precision 21/21) are now reproducible: `python -m eval.analyze_diagnosis` → `eval/results/diagnosis_derived.json`. The CIs replace the ad-hoc ones in my 07:52 message to the Supervisor (LLM upper bound 92.2, not 91.5). Contract JSON Schemas exported: `python -m architecture.contracts.export_schemas` (17 schemas).


### 2026-10-04 10:00 IST — Paused by the Supervisor
- 09:40: resumed for "where does the LLM baseline fail?". Azure reachable. Listed deployable models: swedencentral offers up to gpt-5.5 and gpt-5.6. Deployed `gpt-5.4-mini` (2026-03-17) and `gpt-5.5` (2026-04-24) next to `gpt-4.1-mini`, so the gap tests can include strong reasoning baselines. No experiments run yet, so no new numbers.
- 09:55: Supervisor PAUSE (only 3 projects run; P7 is the Perceptron pick unless the user overrides). Nothing was running. Exact resume plan is in *Now → Resume point*.

### 2026-10-04 15:00 IST — Resumed by the Supervisor (batch slot)
- 14:58 message: P8 active again; definition of done = LLM-gap experiments (pre-registered) → re-framed pitch → final abstract with rendered numbers + doc-drift check → gpt-6-astra / gpt-6-sol reviews → final memo → "DONE — slot free". Now rewritten.
