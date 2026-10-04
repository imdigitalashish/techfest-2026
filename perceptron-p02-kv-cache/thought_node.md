# Perceptron P2 · Squeezing long-context inference into less memory — Thought Node

> Journal for `perceptron-p02-kv-cache/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ▶ RESUMED 14:36 IST → measuring. Pre-registration committed 15:14 IST ([eval/PREREG.md](eval/PREREG.md); amendment 1 at 15:18 adds T3 with synonym-aliased keys).
- **Doing:**
  - **VM** `p02-kv-1`, resized to D16ds_v5: T1 (literal, seed 0) is running, about 6.3 min per context, ETA 16:31. Then T2 (paraphrase, seed 1) → S4 (halo 64) → T3 (alias, seed 2), one job at a time; ETA about 18:30.
  - **Reviewers** (child sessions): [P2 review · code+eval (gpt-6-sol)](ghapp://sessions/377140bc-8a99-47d1-bed3-2b53e4b22b70) (static review now, reproduction after `grid2.done`); [P2 review · hostile judge (gpt-6-astra)](ghapp://sessions/97e5f61d-3add-4e44-9c65-d77e119bfb8a) (spike + PREREG now, final abstract later).
- **Done since resume:**
  - MLX CPU too slow (3.5 GFLOP/s), so I pivoted to a PyTorch twin harness on the same weights. It passes logit parity (2e-5 with fp32 KV); the MLX vs torch difference is 5e-5.
  - Dev sweep of 322 scorer variants: `softmax_lift`/content/4-bit/layer 5 reached hit@3 0.95, vs 0.24 for the a-priori config and 0.91 for lexical (exploratory).
  - kvpress 0.5.5 presses run on CPU as reference baselines.
  - Final abstract skeleton (761 words plus rendered blocks, about 873 in total).
  - `render_docs.py` / `check_docs.py` / `wordcount.py`.
- **Next:** fetch T1 → render → astra phase 2 on the abstract → memo v2 (P2 vs P1, honest) → T2/S4/T3 → final render → sol reproduction → ledger → deallocate VM → "DONE — slot free".
- **Needs from user:** register by 15 Oct (if P2 is chosen over P1; the brief allows only one of P1/P2). Teammates' names and skills for the team-fit section.
- **Risks:**
  1. Re-prefilled blocks see only sinks + the block (approximate KV); S4 measures this.
  2. Lexical needles flatter retrieval; T3 and `rodlex` test this.
  3. CPU timings ≠ GPU timings: only relative overhead is reported.
  4. Novelty hedged ("to our knowledge"; ArkVale's mechanism is UNVERIFIED).

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
_v2 (final for the 12 Oct gate) will be written to [deliverables/selection-memo.md](deliverables/selection-memo.md) once the pre-registered runs finish; its numbers are rendered from committed results by `eval/render_docs.py`._
- **v1 (4 Oct, 08:10; superseded):** winnability 3 · innovation 4 · feasibility 5 · demo 4 · fit 5. At the time there were no measured numbers; v1 described the RoD design before tuning.
- **Pre-registered results so far:**
<!-- p2:verdicts:begin -->
- **Primary** (RoD − StreamingLLM, keep 0.25, T1): pending → pending
- **S1** (RoD vs each query-agnostic baseline, keep 0.25, T1): pending
- **S2** (RoD − RoD-lexical, keep 0.25, T1 literal): pending
- **S2** (RoD − RoD-lexical, keep 0.25, T2 paraphrase): pending
- **S3** (primary replicated on T2 paraphrase): pending
<!-- p2:verdicts:end -->

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

### 2026-10-04 15:27 IST: Resumed; harness ported to PyTorch; dev sweep; pre-registration; reviewers
- **14:36.** Supervisor resumed P2 (P3 freed a batch slot). Definition of done: measured numbers on the Azure VM, honesty (halo, paraphrase, CPU timings), final abstract with rendered numbers and a doc-drift check, cross-model reviews, final memo, VM deallocated.
- **VM.** Started `p02-kv-1`.
  - MLX on Linux CPU is unusable: 4-bit forward of 512 tokens unfinished after 4.5 min; fp32 GEMM 3.5 GFLOP/s.
  - PyTorch CPU reaches 599 GFLOP/s. Ported the harness to `eval/kvbench_torch.py` on the *same* weights (MLX 4-bit, dequantised → fp16 safetensors).
  - KV stored fp16 (the MLX model computes in fp16, not bf16 as I first assumed).
  - Parity: engine vs HF 2e-5 (fp32 KV) / 0.011 (fp16 KV); MLX vs torch 5e-5.
  - Pinned the chat-template date: the Llama 3.2 template inserts today's date.
  - Resized the VM to D16ds_v5 (quota 20 vCPU/region).
- **Smoke (seed 0, 1k tokens, 2 needles; disclosed in PREREG).** full/int8/int4/oracle 2/2; int2 0/2 (garbage); StreamingLLM 1/2 (answered with the visible needle's value). The **a-priori RoD failed 0/2:** block 0 (system prompt) soaked up the sketch attention.
- **Dev sweep** (seeds 100–109, 80 evicted-needle questions; frozen evaluator `components/recall_on_demand/autoresearch/eval_torch.py`):
  - Best of 322: `softmax_lift`/content/4-bit/layer 5, hit@3 0.95 (a-priori 0.24; lexical 0.91).
  - Layer 5 dominates; 2-bit sketches top out at 0.60.
  - Logged in `results.tsv`. Exploratory, so selection-biased; the test seeds decide.
- **Supervisor 14:56** (use kvpress reference baselines; report memory both analytic and measured): agreed and done.
  - kvpress 0.5.5 needs transformers < 5.3, so it lives in a separate venv `~/venv_kvp`; mlx-lm 0.32 conflicts with it.
  - All six presses run on CPU through the same answer path.
  - Memory: analytic bytes equal the retained tensor bytes (asserted for the full cache); peak RSS is reported as context.
- **Pre-registration 15:14 IST** (`eval/PREREG.md`, commit 3263e9f, time matches).
  - Primary: RoD − StreamingLLM at keep 0.25 on T1.
  - Why 0.25: at 0.10, RoD's charged extras leave about 2 recall blocks on 4k contexts.
- **Supervisor 15:17 spot-check.** Agreed on exploratory labelling and confirmation on fresh seeds. Pushed back: T2 paraphrases only the templates, so lexical retrieval won't fall off there. **Amendment 1, 15:18:** T3 with synonym-aliased keys plus a lean method set; the code change is additive, and the T1/T2/S4 files are unchanged (md5 7402…).
- **Chain on the VM:** T1 → T2 → S4 → T3 (`grid.sh`, `grid2.sh`), one job at a time. T1 takes about 6.3 min per context.
- **Reviewers:** gpt-6-sol (code/eval + reproduction after `grid2.done`) and gpt-6-astra (hostile judge on spike + PREREG; abstract later).
- **Docs.**
  - ADR 001 v2 update.
  - Final-design abstract: 761 words plus rendered blocks, about 873 in total.
  - Architecture tiers updated (4-bit, layer 5, 288 B/token, window queries).
  - `render_docs.py` / `check_docs.py` (drift + superseded-number check) / `wordcount.py`.
