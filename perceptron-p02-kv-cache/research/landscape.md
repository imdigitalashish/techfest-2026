# Landscape — KV-cache compression for long-context recall (Perceptron P2)

_Lead: perceptron-p02-kv-cache · written 2026-10-04 07:50 IST in **lean mode** (network saturated; all 7 research agents died on model-side 408 errors)._

**How to read the evidence tags.** **[OPENED]** = I opened the primary source in this session (path or URL + 2026-10-04). **UNVERIFIED** = from my prior knowledge, *not* re-opened tonight. The arXiv IDs are listed so the next pass can confirm them in one API call. No UNVERIFIED claim is used to justify a number in our results.

## 1. The problem in bytes [OPENED: local `config.json` files]
KV bytes per token = 2 (K,V) × layers × KV heads × head_dim × 2 bytes (fp16/bf16).

| Model (config opened from the local HF cache) | Layers | Q / KV heads | head_dim | KV per token | KV at 32k tokens |
|---|---|---|---|---|---|
| Llama-3.2-1B-Instruct (`mlx-community/...-4bit`) | 16 | 32 / 8 | 64 | 32 KiB | 1.0 GiB |
| Qwen2.5-3B-Instruct | 36 | 16 / 2 | 128 | 36 KiB | 1.1 GiB |
| Qwen3-1.7B (`mlx-community/...-4bit`) | 28 | 16 / 8 | 128 | 112 KiB | 3.5 GiB |
| Gemma-3-1B-it | 26 | 4 / 1 | 256 | 26 KiB if every layer were global | config: `sliding_window=512`, `sliding_window_pattern=6` → most layers keep only 512 tokens (interpretation of the pattern field UNVERIFIED tonight) |

The 4-bit Llama-3.2-1B weights are ~0.7 GB, so its fp16 cache overtakes the weights past roughly 22k tokens. The cache, not the weights, is what long chats run out of. The token IDs of the same context cost 4 B/token: **8,192× less than its KV.** That ratio drives our spike (§5).

**Update 07:58 IST.** The background fetch landed. **All 25 arXiv IDs below were opened via the arXiv API, and their titles match** (`research/raw/arxiv_abstracts.md`). Numbers quoted from the abstracts **[OPENED]**:
- StreamingLLM (2309.17453): "stable and efficient language modeling with up to 4 million tokens".
- H2O (2306.14048): throughput up to "29×, 29×, and 3×" over DeepSpeed Zero-Inference, HF Accelerate and FlexGen (OPT-6.7B/30B).
- SnapKV (2404.14469): "3.6x increase in generation speed and an 8.2x enhancement in memory efficiency … inputs of 16K tokens".
- KIVI (2402.02750): "2.6× less peak memory (including model weight)".
- DuoAttention (2410.10819): memory "up to 2.55x for MHA and 1.67x for GQA models".
- DMS (2506.05345): "only requires 1K training steps to achieve 8× compression".
- SCBench (2412.10319): "sub-O(n) memory methods suffer in multi-turn scenarios".
- MiKV (2402.18096): examines "the detrimental" effects of evicting KV pairs.
- DeepSeek-V2 (2405.04434): MLA "reduces the KV cache by 93.3%".
- Gemma 3 (2503.19786): "increasing the ratio of local to global attention layers, and keeping the span on local attention short".
- Apple FM 2025 (2507.13575): "KV-cache sharing and 2-bit quantization-aware training".

Mechanism details beyond the abstracts remain UNVERIFIED.

## 2. Method families
| Family | Representative methods (arXiv ID to verify) | Needs the question at compression time? | Recall risk |
|---|---|---|---|
| Positional eviction | StreamingLLM / attention sinks (2309.17453): keep the first few "sink" tokens plus a recent window | No | Anything in the evicted middle is gone. Fails needle recall by construction. |
| Score-based eviction, query-agnostic | H2O heavy hitters (2306.14048); TOVA; K-norm, i.e. low key L2 norm (2406.11430); KeyDiff; Q-Filters; Expected Attention (NVIDIA kvpress) | No | Importance is guessed before the question exists. |
| Observation-window selection | SnapKV (2404.14469); PyramidKV, per-layer budgets (2406.02069); Ada-KV, per-head budgets (2407.11550); CAKE | Yes, if the window includes the question | Strong when the question is known. Degrades in multi-turn chat when later questions hit evicted tokens: SCBench (2412.10319); KVzip (2505.23416). |
| Head specialisation | DuoAttention (2410.10819); RazorAttention; HeadKV | No (calibrated offline) | Retrieval heads keep the full cache, so memory saving is bounded by the share of retrieval heads. |
| Keep all, select at decode | Quest (2406.10774); InfiniGen; ShadowKV (2410.21465); MagicPIG | Yes (per decode step) | Accuracy is good, but the full cache still sits in RAM, CPU or disk: a bandwidth saving more than a memory saving. |
| Quantisation | KIVI, 2-bit asymmetric (2402.02750); KVQuant (2401.18079); importance-aware mixed precision, MiKV (2402.18096); FP8 KV in engines | No | Lossless-ish at 8 bits, usable at 4. 2-bit needs care (outlier channels in keys). Saving is capped at about 8× minus scale overhead. |
| Architectural / retrofit | GQA; MLA (DeepSeek-V2, 2405.04434); sliding-window hybrids (Gemma 3, 2503.19786; gpt-oss, 2508.10925); cross-layer KV sharing (MiniCache 2405.14366; Apple Foundation Models 2025, 2507.13575); learned eviction (DMS 2506.05345) | n/a | Needs training or a new model. Out of scope for a frozen 1–3B model, but the main direction in production. |
| Reuse rather than shrink | PagedAttention / vLLM (2309.06180); RadixAttention / SGLang (2312.07104); Mooncake (2407.00079); CacheBlend (2405.16444) | n/a | Lossless; saves recompute across requests, not bytes per request. |

**What the families jointly imply.** Every method that *deletes* tokens before the question arrives bets that it can predict what will be asked. Long chats break that bet: the 2nd, 3rd and later questions target content nobody scored highly at compression time. Quantisation never deletes but stops at about 4–8×. Keep-all-and-select methods fix recall but don't cut the bytes held. The open gap is **high compression *and* robustness to questions that arrive after compression, without keeping the full cache anywhere.**

## 3. What companies ship today
| Technique | Who ships it | Evidence |
|---|---|---|
| Rotating (sink + window) KV cache and quantised KV cache on Apple silicon | Apple MLX-LM 0.32.0 | **[OPENED]** `mlx_lm/models/cache.py`: `RotatingKVCache(max_size, keep=0)`, `QuantizedKVCache(group_size=64, bits=8)` with packed weights plus scales and biases. `models/base.py` raises "Quantized SDPA does not support attention sinks". PyPI index: mlx 0.32.3, mlx-lm 0.32.0 **[OPENED]**. |
| Library of compression "presses" over HF transformers | NVIDIA kvpress | **[OPENED]** README (raw GitHub, main): 48 `*Press` class names, e.g. `SnapKVPress`, `ExpectedAttentionPress`, `KVzipPress`, `DMSPress`, `DuoAttentionPress`, `QFilterPress`, `PyramidKVPress`, `DecodingPress`. PyPI latest 0.5.5. |
| Prompt / context caching (prefix reuse) | Anthropic; Google Gemini; OpenAI | **[OPENED]** Anthropic docs: "automatic caching or explicit breakpoints with 5-minute or 1-hour TTLs"; cache reads use "the standard 0.1x multiplier"; "5-minute cache write tokens are 1.25 times" the base price. **[OPENED]** Gemini docs: "Implicit caching is enabled by default for all Gemini 2.5 and newer models." OpenAI: page fetched but no extractable text, so UNVERIFIED. |
| GQA / MQA; MLA | Meta Llama 3.2 (8 KV heads for 32 Q, **[OPENED]** config); Qwen (2 or 8 KV heads, **[OPENED]**); DeepSeek-V2 MLA | **[OPENED]** DeepSeek-V2 abstract: "reduces the KV cache by 93.3%". |
| Interleaved local/global attention | Google Gemma 3; OpenAI gpt-oss | **[OPENED]** Gemma-3-1B config: window 512, pattern 6. Gemma 3 report abstract: more local layers with short spans to curb "KV-cache memory that tends to explode". **[OPENED]** gpt-oss-20b `config.json`: 24 layers = 12 `sliding_attention` (window 128) + 12 `full_attention`, 8 KV heads, head_dim 64. |
| Cross-layer KV sharing + low-bit | Apple on-device foundation model; Character.AI | **[OPENED]** Apple FM 2025 abstract: "KV-cache sharing and 2-bit quantization-aware training". Character.AI blog: page fetched but no extractable text, so UNVERIFIED. |
| FP8 KV cache, prefix caching, paged KV | vLLM, SGLang, Mooncake | **[OPENED]** vLLM docs "Quantized KV Cache": "Supported FP8 KV-Cache Quantization Schemes", scale calibration, `kv_cache_dtype` options. PagedAttention (2309.06180), SGLang (2312.07104) and Mooncake (2407.00079) abstracts **[OPENED]** (titles verified). llama.cpp: UNVERIFIED. |

**Reading.** I found no evidence (and know of none) that a major provider ships lossy token *eviction* (H2O or SnapKV style) for general chat. Production cuts KV with architecture (GQA, MLA, sliding windows), quantisation (FP8/int8) and lossless reuse (paging, prefix caching, offload). Eviction stays a research and on-device topic. That is our opening: make eviction **safe for recall**, using the production ingredients of *quantisation* (a 2-bit sketch) and *recompute on miss* (prefix reuse in reverse).

## 4. Evaluation landscape (UNVERIFIED unless tagged)
- **RULER** (2404.06654): synthetic NIAH variants (single, multi-key, multi-value, multi-query), variable tracking, aggregation and QA at chosen lengths. Our harness generates RULER-style multi-needle tasks over WikiText-103 text **[OPENED: our code]**.
- **SCBench** (2412.10319): shared-context multi-turn evaluation. It motivates our *query-agnostic* protocol (compress once, then ask 4 questions).
- **KVzip** (2505.23416): argues for query-agnostic compression evaluated across many queries.
- Others to add once fetched: LongBench v2, InfiniteBench, NoLiMa (non-literal needles, which defeat lexical retrieval), BABILong, HELMET.

## 5. Innovation room → our spike
1. **Recall-on-demand (RoD).** Keep a small resident cache (StreamingLLM or SnapKV). For evicted spans, keep only the token IDs (4 B/token) and a 2-bit key sketch from one layer (~160 B/token, about 0.5% of full KV). When a question arrives, its own queries score the sketch, and the top evicted blocks are *re-prefilled* at their original positions before answering. Eviction becomes a cache miss rather than data loss. Nearest prior art to check: ArkVale-style page recall (it keeps evicted KV offloaded, whereas we keep none), Quest page digests, CacheBlend selective recompute, and ReadAgent-style look-ups at the text level. UNVERIFIED novelty: to be confirmed in the 12 Oct verification pass.
2. **Demote, don't delete.** Store low-score tokens at 2-bit instead of evicting them (mixed precision by importance, close to MiKV/ZipCache; incremental novelty).
3. **Isolated scorer metric.** "Needle-token retention at budget" scores any scorer without generating text. It is cheap enough to drive an autoresearch ratchet.

## 6. Sources
Opened this session (2026-10-04): `_briefs/perceptron.txt`; mlx-lm 0.32.0 source (`mlx_lm/models/cache.py`, `base.py`, `llama.py` in `.venv`); `config.json` of `mlx-community/Llama-3.2-1B-Instruct-4bit`, `google/gemma-3-1b-it`, `Qwen/Qwen2.5-3B-Instruct` and `mlx-community/Qwen3-1.7B-4bit` (local HF cache); PyPI version index for kvpress, mlx and mlx-lm; WikiText-103 raw v1 parquet (HF `wikitext`, revision b08601e).
Pending fetch (`research/raw/`, background job): the arXiv abstracts for all IDs above; Character.AI inference blog; vLLM quantised-KV docs; Anthropic, OpenAI and Gemini caching docs; gpt-oss `config.json`; kvpress README.
