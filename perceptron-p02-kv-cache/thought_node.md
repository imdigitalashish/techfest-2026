# Perceptron P2 · Squeezing long-context inference into less memory — Thought Node

> Journal for `perceptron-p02-kv-cache/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ▶ measuring and reviewing. T1 done (16:18); T2 running; then S4, T3, post-hoc E1–E5, sol reproduction. PREREG plus 4 amendments, all committed before the outcomes they govern.
- **Results so far (T1, rendered in [eval/RESULTS.md](eval/RESULTS.md)):**
  - **Pre-registered primary passed:** RoD − StreamingLLM +0.40 (CI +0.25 to +0.54) at 25% memory.
  - RoD beats all 9 query-agnostic baselines, including kvpress's.
  - **S7 non-inferiority vs full not shown** (−0.25).
  - Exploratory: at 10% memory RoD 0.854 vs full 0.833 (baselines ≤ 0.06). Replication R1 on T2 is pre-registered.
  - Mechanism: block hit ↑, accuracy given hit ↓ (0.98 → 0.55): key–value confusion with more recalled needle blocks.
  - Identity checks I1–I3 pass.
- **Doing:**
  - VM chain T2 → S4 → T3 → post-hoc (ETA about 18:45).
  - [gpt-6-sol](ghapp://sessions/377140bc-8a99-47d1-bed3-2b53e4b22b70) waits for `posthoc.done` to reproduce.
  - [gpt-6-astra](ghapp://sessions/97e5f61d-3add-4e44-9c65-d77e119bfb8a) waits for the final abstract (phase 2).
- **Next:** T2 → R1 → memo scores update by rule → T3/S4/post-hoc → final render → astra phase 2 → sol reproduction → ledger → deallocate VM → "DONE — slot free".
- **Needs from user:** register by 15 Oct (if P2 is chosen over P1; only one of P1/P2 is allowed). Teammates' names and skills for the team-fit section.
- **Risks:**
  1. R1 may not replicate.
  2. Approximate re-prefill (E2 decides).
  3. Synthetic task and n=12.
  4. CPU timings only.
  5. Narrow novelty.

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
_v2 source of truth: [deliverables/selection-memo.md](deliverables/selection-memo.md). Scores are rendered by pre-fixed rules from committed results (`eval/render_docs.py`). v1 (4 Oct, 08:10, before any measurement) is superseded._
<!-- p2:memo-scores:begin -->
| Criterion | Score | Evidence |
|---|---|---|
| **Winnability** | 4 | Pre-registered primary passed: RoD − StreamingLLM +0.40 (95% CI +0.25 to +0.54) at 25% memory, and RoD beats all nine tested query-agnostic baselines there, including NVIDIA kvpress's reference presses. Non-inferiority vs the full cache at 25% was not shown. The 10% observation replicated on fresh contexts (R1). |
| **Innovation headroom** | 4 | A narrow but real combination: token-backed selective recomputation guided by a single-layer 4-bit key index with a contrastive scorer. Its constituents are prior art (hostile judge: 3/5). At 10% memory the sketch beats a lexical index over the same ids by +0.42 (95% CI +0.31 to +0.52). Headroom: precision-first recall, a streamed scorer, per-channel sketches, multi-turn. |
| **Feasibility** | 4 | The whole pre-registered evaluation runs end to end on one CPU VM, with logit parity, identity checks, reference baselines and reviews. The Apple-silicon (MLX) demo path is not yet validated; CPU answer time is 6.2× StreamingLLM's at 25% memory. The 19–25 Nov exams are left free. |
| **Demo strength** | 4 | Live: a 1B model answers questions about a long document holding 10% of its KV. RoD 85% vs ≤6% for every tested eviction baseline (full cache 83%), with a memory meter. Synthetic needles are less visual than a real chat. |
| **Fit with the user** | 5 | Inference systems: cache hierarchy, recompute vs memory trade-off, kernels. This is core Microsoft-style systems work. |

**Overall: 4.2 / 5**, the unweighted mean (4 + 4 + 4 + 4 + 5 = 21).
<!-- p2:memo-scores:end -->
- **One-line pitch:**
<!-- p2:memo-pitch:begin -->
"Treat the KV cache as a cache: keep one layer's keys at 4 bits plus the token ids, and recompute only the blocks a question asks for. With a tenth of the memory, every tested eviction method forgets the needle; RoD finds it, on two independent test splits."
<!-- p2:memo-pitch:end -->
- **Pre-registered results so far:**
<!-- p2:verdicts:begin -->
- **Primary** (RoD − StreamingLLM, keep 0.25, T1): +0.396 (95% CI +0.25 to +0.54, 12 contexts) → **SUCCESS** (lower bound > 0)
- **S7** (RoD − full cache, keep 0.1, T1) (descriptive): +0.021 (95% CI -0.15 to +0.19, 12 contexts)
- **S7** (RoD − full cache, keep 0.25, T1) (confirmatory, margin −0.05): -0.250 (95% CI -0.42 to -0.08, 12 contexts) → non-inferiority **not shown**
- **S7** (RoD − full cache, keep 0.5, T1) (descriptive): -0.229 (95% CI -0.40 to -0.06, 12 contexts)
- **S1** (RoD vs each query-agnostic baseline, keep 0.25, T1): beats **all** 9 baselines; weakest margin kvpress TOVA +0.229 (95% CI +0.04 to +0.40, 12 contexts)
- **S2** (RoD − RoD-lexical, keep 0.25, T1 literal): +0.042 (95% CI -0.04 to +0.12, 12 contexts) → no evidence the sketch beats lexical retrieval
- **S2** (RoD − RoD-lexical, keep 0.25, T2 paraphrase): +0.271 (95% CI +0.10 to +0.44, 12 contexts) → sketch beats lexical
- **R1** (replication on T2: RoD − full at keep 0.10, margin −0.15): +0.229 (95% CI +0.10 to +0.38, 12 contexts) → **replicated** (lower bound > −0.15)
- **R2 mechanism T1** (RoD): keep 0.1: block hit 0.88, accuracy given hit 0.98, 4/7 wrong answers name another needle's value; keep 0.25: block hit 1.00, accuracy given hit 0.55, 16/20 wrong answers name another needle's value; keep 0.5: block hit 1.00, accuracy given hit 0.53, 10/19 wrong answers name another needle's value
- **R2 mechanism T2** (RoD): keep 0.1: block hit 0.85, accuracy given hit 0.82, 0/15 wrong answers name another needle's value; keep 0.25: block hit 0.93, accuracy given hit 0.59, 10/20 wrong answers name another needle's value; keep 0.5: block hit 1.00, accuracy given hit 0.35, 15/26 wrong answers name another needle's value
- **S3** (primary replicated on T2 paraphrase): +0.375 (95% CI +0.23 to +0.54, 12 contexts) → replicated
- **S5** (RoD − baseline, keep 0.1, T1): StreamingLLM (ours) +0.833 (95% CI +0.71 to +0.94, 12 contexts); SnapKV-variant (ours, +4 sinks) +0.854 (95% CI +0.73 to +0.96, 12 contexts); H2O-style (ours) +0.854 (95% CI +0.73 to +0.96, 12 contexts); RoD-lexical (control) +0.417 (95% CI +0.31 to +0.52, 12 contexts); kvpress ExpectedAttention +0.854 (95% CI +0.73 to +0.96, 12 contexts)
- **S5** (RoD − baseline, keep 0.5, T1): StreamingLLM (ours) +0.167 (95% CI +0.02 to +0.31, 12 contexts); SnapKV-variant (ours, +4 sinks) +0.375 (95% CI +0.21 to +0.56, 12 contexts); H2O-style (ours) +0.333 (95% CI +0.15 to +0.50, 12 contexts); RoD-lexical (control) +0.000 (95% CI -0.08 to +0.08, 12 contexts); kvpress ExpectedAttention not run
- **Byte check T1**: RoD answer-time bytes > a baseline's stored bytes in 0 of 36 (context, keep) cells
- **Byte check T2**: RoD answer-time bytes > a baseline's stored bytes in 0 of 36 (context, keep) cells
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

### 2026-10-04 16:31 IST: T1 results, reviews triaged, identity checks, memo v2 by rule
- **Reviews.**
  - gpt-6-sol static review: 8 issues (6 major, 2 minor), all accepted (2 partly). Led to amendment 2 (15:30), environment pins (`setup_kvp.sh`, sha256 + freeze) and renderer checks.
  - gpt-6-astra phase 1 (provisional 62/100): 12 issues (2 critical), all accepted. Led to amendment 3 (15:35): S7 non-inferiority vs full, S6 single confirmatory fraction, exploratory E1–E3, and novelty/wording rewrites.
  - Triage: `reviews/2026-10-04-triage.md`; ledger: `reviews/ledger.tsv`.
- **Streamed scorer** (`components/recall_on_demand/streamed.py`): matches the unchunked scorer to 8e-6 on random tensors (local check). E1 verifies identical block choices on T1.
- **T1 (16:18).**
  - Primary passed (+0.40, CI +0.25 to +0.54). S1: RoD beats all 9 query-agnostic baselines at 25%; the weakest margin is TOVA, +0.23 (CI +0.04 to +0.40).
  - **S7 failed:** RoD − full at 25% = −0.25.
  - S2: RoD vs lexical at 25%, +0.04 (ns). S5: at 10%, RoD vs lexical +0.42.
  - Full cache 0.833; int8 0.833, int4 0.771, int2 0.000.
  - Byte check: 0 violations in 36 cells.
- **Diagnosis.** RoD finds the needle's block more often as the budget grows (0.88 → 1.00), but accuracy given a hit drops (0.98 → 0.55). 16 of 20 wrong answers name another needle's value.
- **Amendment 4 (16:21, before T2 outcomes).** R1 replication of the 10% observation on T2 (margin −0.15); R2 mechanism; E5 top-2 cap (queued in the post-hoc job).
- **Supervisor 16:24** asked for an identity check: done on dev seed 100. I1, I2 and I3 pass at keep 0.10, 0.25, 0.50 and 1.0, so this is not a plumbing artifact.
- **Selection memo v2:** scores rendered by rules fixed before T2/T3 (`deliverables/selection-memo.md`). Currently 3.8/5 with R1 pending.

