# Perceptron P2 · Squeezing long-context inference into less memory — Thought Node

> Journal for `perceptron-p02-kv-cache/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 0 done → 4 (walking skeleton + eval harness) in parallel with 1–3 docs. **LEAN MODE** (Supervisor, 05:49): no sub-agents, small requests, no downloads > 200 MB, push every 30 min.
- **Plan (to 08:15 push):** MLX harness on the *already-cached* `mlx-community/Llama-3.2-1B-Instruct-4bit` + local WikiText-103 haystack → real numbers for full cache vs StreamingLLM / H2O / SnapKV / K-norm / KV-quant, query-agnostic protocol → landscape.md (primary sources I open myself) → components + contracts → ADR 001 → selection memo → abstract + architecture.md.
- **Doing:** lead alone (7 research agents launched at 02:10 all died on model-side "408 request body" timeouts; no output survived).
- **Next:** harness smoke test → baseline grid in background → docs.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** (1) Lost 02:10–05:50 to agent failures — research depth is thinner than planned; landscape cites only what I open myself. (2) Shared 24 GB M5 with 19 sibling sessions: GPU/RAM contention can slow runs. (3) Network saturated: no model downloads; model = 4-bit weights (KV itself stays fp16).

## Phase 0 — what the judges need to see (from `_briefs/perceptron.txt`)
- **MVP bullets → evidence:** (a) one existing method applied + memory saved vs uncompressed → a table of *retained KV bytes* (counting every index/scale byte) and measured peak memory, per method and ratio; (b) accuracy drop on a small long-context recall task → needle-recall accuracy with 95% Wilson CIs vs the full cache.
- **Stretch → evidence:** a modification of an existing method (our spike) + ≥ 2 baselines (StreamingLLM, H2O, SnapKV, K-norm, KV-quant) on the same harness.
- **Round 1 (31 Oct) is plan-only:** 600–900-word abstract, 8 sections (problem & theme, understanding, approach, MVP mapping, stretch, novelty, evaluation plan, feasibility & risks) + optional 1-page diagram. Weights: understanding 20 · soundness 25 · novelty 20 · clarity 10 · evaluation 15 · team 10.
- **Rules:** team ≤ 3, one Perceptron problem per team, original work, queries only via the Techfest portal; finals need a working build (MVP + stretch).
- **Assumptions (overnight, no user):** A1 model = Llama-3.2-1B-Instruct (in the brief's 1–3B range; 4-bit MLX weights already on disk; KV in fp16). A2 primary protocol = *query-agnostic* (compress the context before the question arrives) — it matches "chat histories"; query-aware numbers reported alongside. A3 recall task = RULER-style synthetic needles in WikiText-103 text (generated with fixed seeds; labelled synthetic).

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 2 — Squeezing Long-Context Inference into Less Memory** (Theme 1: Efficient AI at Scale — teams choose Problem 1 or 2)
- **Context:** Long documents or chat histories strain GPU memory, mostly from the cache a model keeps for past tokens.
- **Challenge:** Shrink that cache significantly while barely hurting the model's ability to recall earlier content.
- **Starter resources:** Open reference implementations of existing cache-compression techniques (e.g. StreamingLLM, H2O), applied to a small model (1–3B params).
- **Minimum Viable:** apply an existing compression technique and measure memory savings vs. an uncompressed baseline; show the accuracy drop on a small, long-context recall task.
- **Stretch goals:** propose a modification to an existing method; benchmark against 2+ baselines.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Libraries: NVIDIA `kvpress` (many compression "presses" in one place), MLX-LM rotating and quantized KV caches on Apple silicon, vLLM / SGLang cache management.
- Methods: StreamingLLM, H2O, SnapKV, PyramidKV, Ada-KV, DuoAttention, Quest, KIVI / KVQuant (quantization) — and the newest 2025–2026 work that beats them.
- Benchmarks: RULER, LongBench v2, Needle-in-a-Haystack, InfiniteBench; models: Llama-3.2-1B/3B, Qwen2.5-1.5B/3B.
- What companies ship: long-context serving and prompt-caching designs from frontier labs and inference providers.

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
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 06:00 IST — Phase 0 done; switching to lean mode
- Read PLAYBOOK, seeded brief and `_briefs/perceptron.txt`; constraints and judge-facing evidence list are in *Phase 0* above.
- 02:10: launched 6 research agents (eviction papers, quant/low-rank/recompute, companies, social, benchmarks, libraries) + 1 first-principles agent. All failed or vanished with model-side "408 Timed out reading request body" (machine-wide network saturation); no output survived. Lesson: keep requests small; do research myself with compact fetches.
- Environment: Apple M5, 24 GB, macOS 26.2; project venv `perceptron-p02-kv-cache/.venv` (mlx 0.32.3, mlx-lm 0.32.0; the kvpress/torch install timed out on the network — not retried, per lean mode). Cached model `mlx-community/Llama-3.2-1B-Instruct-4bit` (16 layers, 8 KV heads × 64 dims → 32 KiB fp16 KV per token). Azure: a Visual Studio Enterprise subscription is enabled; GPU quota unknown (not needed tonight).
- Supervisor 05:49: LEAN MODE — acknowledged; working alone and sequentially.
