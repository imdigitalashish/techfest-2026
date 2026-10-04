# Perceptron P2 · Squeezing long-context inference into less memory — Thought Node

> Journal for `perceptron-p02-kv-cache/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ⏸ **PAUSED** (Supervisor 09:55, user's decision: only 3 projects run at once; P7 is the Perceptron pick unless the user overrides). Nothing is running locally or on Azure.
- **Delivered:** landscape (cited), per-component scan, RoD prior-art report, components + contracts, ADR 001, selection memo v1, Round-1 abstract (843 words), architecture diagram, harness v2, Azure runner, C7 autoresearch scaffold.
- **Not done (be honest):** **no measured numbers.** `eval/kvbench.py` v2 and `components/recall_on_demand/autoresearch/eval.py` have **never executed end to end**. Local runs starved (GPU 67% busy from other sessions, 35.7 GB swap); the Azure probe was stopped at pause.
- **Resume point (in order):**
  1. **Start the VM.** `az vm start -g p02-kvcache-rg -n p02-kv-1`.
     - It is a Standard_D8ds_v5 in centralindia: 8 vCPU (Xeon 8370C), 32 GiB, now *deallocated*.
     - The disk keeps a uv Python 3.11 venv (mlx[cpu] 0.32.3, mlx-lm 0.32.0) and `~/p02/.data/haystack.txt`, which is identical to the local one (3,521 paragraphs, 2,289,620 chars).
     - SSH key: `.data/azure_p02` (gitignored). If it is lost, reset it with `az vm user update`.
  2. **Speed probe:** 4-bit vs dequantised forward over 1,024 tokens on the CPU. It hadn't finished after 5 min; the model download may have been part of that. If 4-bit is slow, add a `--dequant` flag. Check first that `mlx_lm.utils.dequantize_model` exists (UNVERIFIED).
  3. **Smoke run:** `eval/azure/run_on_azure.sh run "--ctx 1024 --n 1 --needles 2 --fracs 0.25 --name smoke_az"`, then `status`, then `fetch`. Fix bugs.
  4. **Grid, one job at a time:** `--ctx 4096 --n 12 --seed 0 --style literal`, then `--style paraphrase`, then `--halo 64` (re-prefill context ablation).
  5. **C7 ratchet:** `components/recall_on_demand/autoresearch/eval.py --layer {2,4,8,12,15}`, logged to `results.tsv`.
  6. **Update the abstract, ADR and memo with measured numbers.** Apply the remaining hostile-review fixes (Log 10:05). Message the Supervisor with memo v2.
  7. **Cleanup:** `eval/azure/run_on_azure.sh delete` removes the resource group.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section (the hostile review scored team fit 1/5 without them).
- **Risks:**
  1. No numbers, so the project ranks low in selection.
  2. Re-prefilled blocks see only sinks + the block, so their KV is approximate. The halo ablation is pending.
  3. Lexical needles flatter retrieval. The `rodlex` control and paraphrase style are in v2; key aliasing is not yet.
  4. Novelty is plausible but not airtight: ArkVale's digest mechanism is UNVERIFIED, and SpeCache's sketch scope is unconfirmed.

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
- 2026-10-04 — Model: Llama-3.2-1B-Instruct (MLX 4-bit weights, fp16 KV) on the M5. Primary protocol: query-agnostic, multi-question. Recall task: RULER-style needles in WikiText-103.
- 2026-10-04 — Spike A = recall-on-demand (C7); spike B candidate = query-agnostic scorer (C3). Rationale: [ADR 001](architecture/adr/001-spike.md).

## Components
See [architecture/components.md](architecture/components.md). C1 workload · C2 prefill engine · C3 scorer (spike B) · C4 budget · C5 selector · C6 KV codec · **C7 recall-on-demand (spike A)** · C8 answerer · C9 memory meter · C10 evaluator. All are baseline-implemented in `eval/kvbench.py`; status: written, not yet measured.

## Selection memo
_First version 08:10 IST, 4 Oct; final by 12 Oct. Score 1–5, one line of evidence each._
- **Winnability — 3/5.** A well-trodden problem: kvpress alone ships 48 press classes ([README, opened](research/raw/src_kvpress_readme.md)), so the "obvious" entry (StreamingLLM/H2O on a 1B model plus a needle chart) will be common. We win only on the spike and on evaluation rigour (query-agnostic multi-question protocol, every byte counted, 95% CIs).
- **Innovation headroom — 4/5.** The spike is *recall-on-demand* (RoD): eviction becomes a cache *miss*, not data loss. For evicted spans we keep token IDs (4 B/token) plus a 2-bit key sketch of one layer (≈160 B/token, about 0.5% of the 32 KiB/token fp16 KV). The question's own queries pick evicted blocks to re-prefill. It targets the failure SCBench documents: "sub-O(n) memory methods suffer in multi-turn scenarios" ([2412.10319, opened](research/raw/arxiv_abstracts.md)). Prior-art check (ArkVale, Quest, CacheBlend) is pending.
- **Feasibility by the deadline — 5/5.** Everything runs on the M5 in MLX with a 4-bit 1B model already on disk and local WikiText. The harness is written ([eval/kvbench.py](eval/kvbench.py)). No GPU, data access or user action is needed before the 19–25 Nov exams.
- **Demo strength — 4/5.** A live laptop chat over a long document with a memory meter: StreamingLLM forgets the needle and RoD recalls it at the same answer-time bytes, plus a recall-vs-bytes Pareto chart.
- **Fit with the user's strengths — 5/5.** It is a systems problem: a cache hierarchy (resident KV / sketch index / backing store of token IDs, recompute on miss), matching large-scale-systems and frontier-model inference experience.
- **Biggest risk:**
  1. Novelty: a close prior art may exist (keep-and-recall designs such as ArkVale; "evict + recompute" papers from 2025–26). Verify by 12 Oct.
  2. Recompute latency per question.
  3. No measured numbers yet: tonight's smoke run was starved by machine-wide memory pressure (16% free, ~42 GB swap per the Supervisor). First numbers come after 08:30.
- **One-line pitch:** "Treat the KV cache as a cache, not a store: keep a 0.5% sketch plus the raw token IDs, and when a question arrives, recompute only the passages it needs. StreamingLLM-level memory, aiming at full-cache recall."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 06:00 IST — Phase 0 done; switching to lean mode
- Read PLAYBOOK, seeded brief and `_briefs/perceptron.txt`; constraints and judge-facing evidence list are in *Phase 0* above.
- 02:10: launched 6 research agents (eviction papers, quant/low-rank/recompute, companies, social, benchmarks, libraries) + 1 first-principles agent. All failed or vanished with model-side "408 Timed out reading request body" (machine-wide network saturation); no output survived. Lesson: keep requests small; do research myself with compact fetches.
- Environment: Apple M5, 24 GB, macOS 26.2; project venv `perceptron-p02-kv-cache/.venv` (mlx 0.32.3, mlx-lm 0.32.0; the kvpress/torch install timed out on the network — not retried, per lean mode). Cached model `mlx-community/Llama-3.2-1B-Instruct-4bit` (16 layers, 8 KV heads × 64 dims → 32 KiB fp16 KV per token). Azure: a Visual Studio Enterprise subscription is enabled; GPU quota unknown (not needed tonight).
- Supervisor 05:49: LEAN MODE — acknowledged; working alone and sequentially.

### 2026-10-04 08:10 IST — Landscape, components, memo pushed; harness written, numbers pending
- **Harness.** `eval/kvbench.py` (MLX, explicit-cache forward over the frozen 4-bit Llama-3.2-1B):
  - Protocol: one prefill per context; query-agnostic compression; 4 paired questions per context.
  - Methods: full, quant8/4/2, streaming, h2o, snapkv, knorm, snapkv_qa (query-aware reference) and rod (spike).
  - Accounting: every byte counted, Wilson CIs reported.
  - Smoke run (`--ctx 1024 --n 1`) sat at ~2% CPU for 6+ min while the system had 16% memory free. It is starved, not crashed, and will be retried after 08:30. **No numbers yet; none are claimed.**
- **Sources.** One background `curl` job fetched all 25 arXiv abstracts (titles verified) plus Anthropic, Gemini and vLLM docs, the gpt-oss config and the kvpress README. Landscape claims are upgraded to [OPENED] where verified; Character.AI and OpenAI stay UNVERIFIED.
- **Worker report.** The late `res-companies-ship` report survived (`research/raw/companies-ship-today.md`, 53 sources). Headline: no production stack defaults to lossy eviction; kvpress is research tooling.
- **Pushed so far.** `components.md` with C1–C10 and isolated metrics, `contracts.py`, and selection memo v1.

### 2026-10-04 08:05 IST — ADR 001, abstract and diagram pushed; harness diagnosed
- **Pushed.** `architecture/adr/001-spike.md` (scores, six hats, self-adversarial thesis/antithesis/synthesis, gates for 12 Oct); `deliverables/round1-abstract.md` (833 words, all 8 sections; no result claims); `deliverables/architecture.md` (mermaid diagram + tier byte table).
- **Harness diagnosis.** The pipeline is not hung, just starved: Metal init 7.8 s, `import mlx_lm` 56 s, model load 91 s (663 MiB active), first 6-token forward done at 140 s. The cause is machine-wide swap. The smoke run (`--ctx 1024 --n 1 --needles 2`) is running in the background; the real grid waits until compute is staggered after 08:30.
- **Gate.** Selection memo v1 written; Supervisor notified.

### 2026-10-04 10:05 IST — Hostile review, prior art, harness v2, Azure; then PAUSED
- **Supervisor messages.**
  - 08:22: package accepted, ranked 7th for lack of numbers.
  - 09:40: lean mode back on.
  - 09:55: **PAUSE** (user's decision). Acknowledged; idle after this push.
- **Local compute is unusable tonight.** The MLX GPU smoke run blocked in `Event::wait` (Metal) for 25+ min, with the GPU 67% busy from other sessions and swap at 35.7/48 GB. The CPU run under `nice -n 10` got about 10% CPU at load average 51. Both were killed. **No numbers exist.**
- **Azure.** Quota check: 20 vCPU per region in centralindia and eastus (Dv5/Ev5); no GPU quota. Created `p02-kv-1` (D8ds_v5) through `eval/azure/run_on_azure.sh`, with a project-local SSH key that is gitignored.
  - Ubuntu 22.04's Python 3.10 has no mlx-lm 0.32.0 wheel, so setup now uses a uv Python 3.11 venv.
  - Setup works and the haystack is identical to the local one.
  - The CPU speed probe was stopped at pause. The VM is **deallocated**, with its disk kept.
- **Hostile-judge review** (rubber-duck, 10 issues; abstract scored **54/100**: understanding 4, soundness 2, innovation 3, clarity 4, evaluation 2, team 1). Fixed in harness v2 (`eval/kvbench.py`, untested):
  - (1) RoD answers from a persistent store (resident KV + *packed* sketch + int32 ids), never from the full cache.
  - (2) Quantised methods keep packed arrays.
  - (4) The RoD KV budget is reduced by the sketch + id bytes, so answer-time bytes ≤ baselines'; `snapkv_qa` is labelled an oracle.
  - (5) Honest method names, plus `random` and `rodlex` (IDF lexical block retrieval) controls.
  - (6) The protocol is renamed "shared-context multi-query" (not multi-turn).
  - (7) Added a `--style paraphrase` needle variant.
  - (8) Context-clustered bootstrap CIs and paired deltas.
  - (9) Realised token depth is recorded.
  - (10) One store at a time.

  Still open:
  - True multi-turn evaluation.
  - Key aliasing (fully non-literal needles).
  - Quest/page-digest baseline.
  - Engine logit-parity test.
  - Halo ablation (flag exists).
  - Team names.

  Docs: "KIVI-style" corrected to "per-token group quantisation" in the abstract, `components.md` and the component scan.
- **Prior art** (research agent; `research/components/recall-on-demand-prior-art.md`, 19 papers opened). No paper found combines all three of: zero KV kept for evicted tokens, a single-layer 2-bit sketch used only to score, and re-prefill of flagged blocks at original positions. Recall elsewhere means fetching offloaded KV (ArkVale, InfiniGen, ShadowKV, RetroInfer, SpeCache…). Recompute from tokens appears in CacheBlend (RAG fusion) and as a costly baseline in HCache. Gaps: ArkVale's digest mechanism is UNVERIFIED (OpenReview blocked); SpeCache's sketch scope is unconfirmed. The novelty claim stays hedged: "to our knowledge".
