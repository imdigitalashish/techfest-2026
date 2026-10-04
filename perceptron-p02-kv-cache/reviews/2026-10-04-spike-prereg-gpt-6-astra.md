# Phase 1: hostile-judge review of RoD and its preregistration

Reviewer: **gpt-6-astra**, methodology/statistics/novelty role, PLAYBOOK section 10. Reviewed 2026-10-04; clock checked at 15:28 IST. Snapshot: `63e76941187b5ccde609b89f5f35cd887cdbaec1`. Paths below are relative to `perceptron-p02-kv-cache/` unless prefixed by `../`.

**Verdict: credible MVP experiment, not yet evidence for near-lossless long-context inference under a real memory cap.** The registered primary can answer its narrow question: does RoD outperform a StreamingLLM-style policy on this synthetic shared-context workload at a specified logical-state budget? It cannot, by itself, establish the brief's "barely hurting" requirement, a GPU-capacity improvement, semantic retrieval, or a first-in-literature claim. No T1/T2/T3 confirmation results were committed in the reviewed snapshot; this is not a judgment of their eventual outcomes. The dev winner is insufficient grounds to displace P1; I have not independently reviewed P1 here.

**Credit where due.** The explicit primary, paired questions, context-level resampling, disclosed tuning, lexical control, full-cache baseline, CPU qualification, and additive T3 amendment are good practice. Registration commit `3263e9f` is timestamped 15:14:59 IST; amendment `0b0ffa6` is 15:18:10 IST. The registered harness's MD5 matches `74029553e051e0b93d56af5cd51b3267`. Those checks verify provenance, not independently the claim that nobody saw test outcomes. The 32 KiB/token and 288 B/sketched-token arithmetic is correct.

Severity: **critical** blocks a proposed headline interpretation; **major** materially limits validity, novelty, or feasibility; **minor** is a bounded reporting/readiness correction. Preserve the original preregistration and running tests. Any repair below must be an explicitly dated amendment or a new follow-up, not a retrospective rewrite.

## Numbered issues

### 1. Critical: superiority to eviction does not establish "barely hurting recall"

**Evidence:** `../_briefs/perceptron.txt:36-53` asks for substantial cache reduction while barely hurting recall. `eval/PREREG.md:37-43` tests only RoD minus StreamingLLM; the full-cache comparison is merely descriptive at lines 55 and 64. StreamingLLM deliberately discards the middle where many needles reside.

**Consequence:** A materially lossy RoD could pass the primary by beating an even lossier policy. A positive CI is not a near-losslessness certificate, and a non-significant difference from full would not establish equivalence either.

**Concrete fix:** Keep the primary claim narrow. Add an explicitly justified non-inferiority margin against full on the same model and contexts, for example at most five percentage points of absolute recall loss, and require the lower bound for RoD minus full to exceed the negative margin. Report absolute recall, paired loss, uncertainty, and the specified memory measure together. If that analysis is chosen after outcomes are visible, label it exploratory and confirm it on newly frozen contexts.

### 2. Critical: the byte ledger is logical retained state, not answer-time peak memory

**Evidence:** `eval/PREREG.md:57-61`; `eval/kvbench_torch.py:292-310,335-370,469-471,511-520`. The reported answer bytes are `stored_bytes + rec`. The harness retains full `Kf/Vf` while comparing methods; retrieval expands the sketch and materializes question/window attention scores; `torch.cat` creates augmented KV while resident and recalled inputs remain live. Query/decode tails, recomputation workspace, and halo storage are outside that metric.

**Consequence:** Charging packed sketches, IDs, and window queries is commendable but does not prove the program fits in the quoted answer-time bytes. At an **illustrative exact T=4096**, keep 0.25, the formula yields about **30.54 MiB** of logical RoD state under a **32 MiB** cap; the window-score `lw` tensor alone is about **28.18 MiB** in fp32. These are analytic shape calculations, not measured peaks. Additionally, `snapkv_qa` reports only its selected cache (`kvbench_torch.py:503-509`), although its question-conditioned selection needs the full cache.

**Concrete fix:** Label the present metric "logical retained context-state bytes," and use "same byte cap," not literally equal observed bytes. Keep stored and maximum recalled-state compression separate; `compression_x` currently uses **stored**, not answer-time, bytes (`kvbench_torch.py:537-540`). Measure each method in isolation, including build, retrieval, recomputation, and answer peaks; separate host and accelerator allocations and count shared storage once. Mark `snapkv_qa` as an unconstrained selection oracle with its full backing-state requirement, not a deployable compressed-memory competitor.

### 3. Major: original positions preserve RoPE positions, not original contextual KV

**Evidence:** `eval/kvbench_torch.py:357-367` rebuilds each chosen block against four sinks plus that block, then splices it into resident KV. `architecture/adr/001-spike.md:33,61-63,97` acknowledges approximate KV but also uses "position-faithful." S4 in `eval/PREREG.md:53` compares only halo 64 against halo 0.

**Consequence:** Hidden states in deeper layers depend on the omitted prefix. A correct rotary position cannot recover those dependencies. A self-contained code sentence is unusually tolerant of this approximation; cross-block coreference, multi-hop facts, and evidence crossing a block boundary need not be. Halo improvement measures the value of that particular extra context, not the remaining error against exact KV.

**Concrete fix:** Call this **position-preserving approximate re-prefill**. For identical selected blocks and resident state, compare exact full-prefill KV gathering with isolated and halo recomputation; label the exact-KV version an analysis oracle requiring extra backing storage. Also use oracle evidence-block selection to separate retrieval failure from reconstruction/readout failure. Include at least one cross-block task, verify complete evidence spans rather than just the first numeric token, and charge halo workspace/compute.

### 4. Major: the 322-way dev result uses a different budget from the frozen method

**Evidence:** `components/recall_on_demand/autoresearch/eval_torch.py:99-101` computes every variant's resident/recall allocation using a **2-bit** sketch and **no window-query bytes**. The loop then evaluates both 2- and 4-bit variants at lines 116-124. In contrast, `eval/kvbench_torch.py:317-323` charges the chosen 4-bit sketch and window queries. The ledger and JSON report the selected `softmax_lift/content/4/5` at 0.9500 versus lexical 0.9125 on 80 evicted-needle questions; at 0.25 both reach 0.9730 on 74.

**Consequence:** At illustrative T=4096 and keep 0.10, the dev evaluator recalls **three** blocks while the registered configuration recalls **two**. Its resident state also differs. Thus 0.95 is neither deployed-config recall nor an equal-actual-byte win over lexical retrieval. It is a selected hit-rate surrogate; the apparent lead at 0.10 is only three additional hits among 80, after searching 322 variants.

**Concrete fix:** Label that sweep as fixed-allocation, exploratory localization, including its budget mismatch. Re-evaluate the frozen winner and lexical control on dev using the deployment accounting without using test results to retune. Do not promote hit@m to answer accuracy. Importantly, **322-way dev selection does not itself require a 322-fold correction on a genuinely untouched, fixed primary test**; the holdout is the remedy. Keep the disclosed seed-0 smoke caveat and use fresh seeds for later confirmation.

### 5. Major: 12 contexts give little protection against tail failures or narrow non-inferiority claims

**Evidence:** `eval/PREREG.md:20-22,39-41`; `eval/kvbench_torch.py:396-408`. Four questions share one context; the correct resampling unit is the context, so the primary has **12 clusters**, not 48 independent replications. The percentile bootstrap resamples only those 12 clusters 2,000 times.

**Consequence:** Resampling more often reduces Monte Carlo noise, not uncertainty about unseen context types. With identical observed context deltas, this bootstrap returns a zero-width interval. For perspective, observing zero bad contexts out of 12 still permits an approximately **22.1% bad-context probability** at an exact one-sided 95% bound under independent context draws. That illustrative context-event bound is not an estimate of this experiment's recall loss.

**Concrete fix:** Publish all 12 paired context deltas and discordant question counts, not only the aggregate CI. Treat the registered bootstrap as a small-sample screening result, especially near ceilings. Size a separate confirmation set against the chosen loss margin using dev-only variance assumptions, sample more independent documents/contexts, and freeze its size and stopping rule before outcomes. Do not quietly pool styles as independent replicas: dev literal/paraphrase runs reuse the same seed-generated underlying examples.

### 6. Major: T2 is not a semantic-retrieval test, and T3 is not yet a clean mechanism test

**Evidence:** `eval/kvbench_torch.py:53-67,146-181` uses fixed templates and self-contained synthetic codes. Both literal and paraphrase templates already appear in dev (`autoresearch/eval_torch.py:74,91-93`). T1/T2 use different seeds; `eval/PREREG.md:67` nevertheless proposes attributing a relative T2 drop to lexical overlap. Amendment 1 preserves common template words across all four alias needles.

**Consequence:** T2 is held-out by sampled examples, not by template family, and keys remain verbatim. A cross-seed T1/T2 difference cannot isolate the effect of wording. T3 removes intended key-word overlap, but template matching can locate the small set of code-bearing blocks without identifying which synonym pair the question means. At the larger budget, the recall allowance can cover all four needles. A win over this one lexical control is not sufficient to prove retrieval "by meaning."

**Concrete fix:** Keep T2 described as an in-family template replication. For a follow-up, pair literal/alias questions on identical contexts, assert tokenized key non-overlap, add more equally formatted distractor records than the recall budget, and randomize their positions. Report correct-target block selection before generation, strict single-value accuracy as a sensitivity to the substring grader, and full-cache competence. Include a separately held-out non-literal or multi-hop family with a stated no-retuning rule. Retain T3's predeclared full-cache floor as an honest inconclusive gate.

### 7. Major: secondary inference and emitted analyses need tighter boundaries

**Evidence:** `eval/PREREG.md:45-54,89-91` declares unadjusted secondary CIs; S6 permits the semantic claim if **a** lower bound is positive at either of two fractions. `eval/kvbench_torch.py:546-554` omits the RoD-versus-`kvp_tova` pair required by S1. S4 is a separate file/run with no cross-run delta emitted here. S5 says "all of the above" at 0.50, but reference presses are only run at 0.10 and 0.25.

**Consequence:** Choosing any successful secondary contrast is a multiplicity problem. Conversely, S1's fixed claim that **all specified baselines** lose is an intersection-union claim: requiring every lower bound to exceed zero does **not** inherently need Bonferroni correction, provided the component intervals are calibrated and none are omitted. It does not grant simultaneous coverage for every reported CI or authorize cherry-picked individual wins.

**Concrete fix:** Preserve the one primary. Choose one confirmatory S6 fraction or adjust its two opportunities; keep other contrasts exploratory unless a prospective hierarchy/family is specified. Produce the missing TOVA and paired halo analyses from committed rows, assert identical context/question keys and expected sample counts, and explicitly mark unrun fraction/method cells unavailable. Do not silently narrow "every baseline" to the subset printed by the harness.

### 8. Major: the protocol fits the brief, but the comparator set does not support broad superiority

**Evidence:** The brief allows documents or histories and asks for an existing method plus full baseline (`../_briefs/perceptron.txt:38-53`). `eval/PREREG.md:19` correctly says shared-context multi-query, **not dialogue**. NVIDIA's cached README explicitly supports context-only compression and multiple later questions (`research/raw/src_kvpress_readme.md:55,277`). KVzip is described as query-agnostic, multi-query compression in `research/raw/arxiv_abstracts.md:69-70`, but is absent from the registered methods.

**Consequence:** This protocol is legitimate, not a trick requiring the question to be supplied to eviction baselines. It is also **not a novel evaluation protocol**, and it does not test growing conversations, corrections, dependency on earlier answers, or repeated eviction. Beating the selected older policies is not beating query-agnostic compression generally. The `int2/int4` controls are explicitly simple per-token quantizers, not KIVI; they cannot settle superiority over strong quantization. CPU-backed recall methods can genuinely shrink **GPU** memory, so dismissing them as "bandwidth saving more than memory saving" (`research/landscape.md:41`) changes the brief's resource objective.

**Concrete fix:** Say "tested query-agnostic eviction policies on a fixed reusable context." Add KVzip as a planned strong baseline, retain ExpectedAttention, and show accuracy/bytes/latency Pareto points for quantization, RoD, and `rodlex`, rather than selecting only RoD-favorable fractions. Separate total-state reduction from GPU-resident reduction and acknowledge the host-backed alternative. Add actual multi-turn evaluation only if claiming dialogue robustness.

### 9. Major: defensible novelty is a narrow combination, not "first recall" or "no KV footprint"

**Evidence:** `research/components/recall-on-demand-prior-art.md:33-39` claims "zero resident bytes" and "first" while retaining quantized keys; it still describes 2 bits and an "arbitrarily-chosen" layer. The deployed layer was chosen by the sweep. `architecture/adr/001-spike.md:63` also includes the evaluation protocol among novelty claims.

**Consequence:** A key sketch is KV-derived retained information, even if it cannot directly service full multilayer attention. Query-guided compact indices, recall, and token recomputation are all prior art. The precise conjunction may be a useful hackathon contribution, but the abstract-only search does not establish precedence. ArkVale's digest mechanism is **now directly verified** through its official NeurIPS abstract; the previous OpenReview blockage is no longer an unresolved factual gap.

**Concrete fix:** Prefer: "We investigate token-backed selective recomputation: a single-layer 4-bit key index chooses blocks whose approximate multilayer KV is rebuilt at original positions, without a backing store of full evicted KV." Attribute the constituent ideas, describe `softmax_lift` as the tested design modification, and reserve semantic/general superiority for its controls. Remove absolute "first," "zero footprint," and "arbitrarily-chosen" claims. Check the closest method sections before asserting narrower precedence.

### 10. Major: CPU correctness is useful, but the memory-capacity and latency feasibility story remains untested

**Evidence:** `eval/PREREG.md:10-16,68` explicitly uses fp32 CPU compute and about 4k contexts. `eval/kvbench_torch.py:231-238,469-471` first constructs full-context KV; the compressed state is derived afterward. Reference-press build timing includes a fresh model prefill (`kvbench_torch.py:379-393,499-501`), whereas own-policy build timing follows the shared prefill.

**Consequence:** CPU evaluation is allowed by the brief and entirely reasonable for a Round-1 plan; logit parity is useful implementation evidence. It is not evidence that a context which otherwise OOMs can be ingested, that GPU peak falls, or that GPU recomputation is cheap. Four questions also do not characterize the amortization tradeoff between expensive build and expensive per-question recall. The current shared-prefill and reference build timings cannot simply be added in the same way for end-to-end comparisons.

**Concrete fix:** Describe current evidence as a CPU algorithmic prototype. Either limit deployment claims to **post-prefill retention**, or plan a genuinely memory-bounded construction path and measure it. Include a scheduled accelerator experiment with longer contexts, isolated peak allocations, TTFT, per-answer/decode latency, and amortization over stated query counts. Measure each method end-to-end from a consistent starting boundary; do not extrapolate these CPU timings to production GPU serving.

### 11. Minor: stale numbers and terminology can unnecessarily damage credibility

**Evidence:** ADR lines 37 and 42 call an O(T) sketch "sub-linear in practice" and say steady-state footprint is resident KV only. The prior-art report and landscape retain the old 2-bit cost. ADR line 88 and `autoresearch/results.tsv:3` say the next-best layer reaches 0.69; the JSON contains `max_logit/all/4/1` at **0.7000** for fraction 0.10. Its best 2-bit figure at fraction 0.25 is **0.8378**, so "top out at 0.60" needs a fraction qualifier. ADR's v2 heading says 15:25 although its commit `75d1152` is 15:20:16 IST.

**Concrete fix:** Make the current configuration unambiguous while preserving historical records; append dated corrections where required. Say linear storage with a small coefficient, count resident KV **plus** the index/IDs/window, qualify every dev number by budget/metric, and use actual clock/commit provenance. Do not copy the old 2-bit pitch into the final abstract.

### 12. Minor: Round-1 readiness must describe the human team, not the agent work already completed

**Evidence:** `../_briefs/perceptron.txt:299-303,338-342` requires relevant skills across three members and a credible route to MVP. The reviewed ADR gives next experiments and a selection gate, but no named three-person responsibility/skill mapping.

**Concrete fix:** The final abstract should name confirmed responsibilities for inference implementation, evaluation/statistics, and reproducibility/demo, with feasible milestones and compute risks. Do not invent team members or convert AI-worker activity into human expertise. This is an evidence gap in the reviewed package, not a claim about the actual team's competence.

## Prior-art calibration

Primary evidence used here is deliberately small: committed arXiv abstract extracts and the following opened primary pages/API entries, not an exhaustive full-paper survey. In particular, implementation details absent from those sources remain unverified.

| Prior art | Established overlap and the surviving distinction |
|---|---|
| **Quest** | The cached primary abstract (`research/raw/arxiv_abstracts.md:48-49`) explicitly uses per-page min/max keys and live query vectors to select pages. Query-aware proxy scoring and page selection are not new; RoD replaces fetching retained KV with approximate token recomputation. |
| **ArkVale** | The [official NeurIPS abstract](https://neurips.cc/virtual/2024/poster/96635), opened in this review, explicitly describes CPU/external backup pages, bounding-volume key digests, importance scoring, and recall. Its [README](https://raw.githubusercontent.com/pku-liang/ArkVale/main/README.md) exposes separate device/CPU budgets. The backing representation, not recall itself, is RoD's distinction. |
| **InfiniGen** | [Primary abstract](https://arxiv.org/abs/2406.19707v1), read through the arXiv API: partial query-weight/key rehearsal predicts important next-layer entries and prefetches them from host memory. RoD removes that full backing KV but introduces recomputation and approximation. |
| **SpeCache** | [Primary abstract](https://arxiv.org/abs/2503.16163v1), read through the API: a low-bit VRAM copy scores a complete CPU KV backing store, with speculative fetching. Low-bit selection proxies are already prior art. Whether its copy spans all layers is not established by this abstract. |
| **ShadowKV** | Cached primary abstract (`research/raw/arxiv_abstracts.md:15-16`): low-rank keys plus offloaded values and sparse reconstruction. It demonstrates why compressed reconstruction is not identical to re-running tokens, but also why GPU-memory savings cannot be dismissed merely because host state exists. |
| **RetroInfer** | [Primary abstract](https://arxiv.org/abs/2505.02922v3), read through the API: attention-aware vector indexing and a heterogeneous GPU/CPU buffer. A compact query-aware index is not itself new; RoD's backing-state/compute tradeoff differs. |
| **CacheBlend** | Cached primary abstract (`research/raw/arxiv_abstracts.md:30-31`): reuses chunk KV and selectively recomputes tokens to repair missing cross-attention. This both anticipates selective recomputation and supplies a reason to distrust "faithful" isolated blocks. It is not evidence that its exact recomputation scope matches RoD. |
| **HCache** | [Primary abstract](https://arxiv.org/abs/2410.05004v1), read through the API, explicitly identifies token recomputation after eviction as existing practice; HCache instead restores from intermediate activations. "Recompute on a cache miss" is not a first claim. |
| **KVzip** | Cached primary abstract (`research/raw/arxiv_abstracts.md:69-70`): context-reconstruction-based, query-agnostic compression with reuse across queries. It is a closer task-level competitor than a universal claim based on StreamingLLM alone acknowledges. |
| **kvpress ExpectedAttention** | The opened [v0.5.5 implementation](https://raw.githubusercontent.com/NVIDIA/kvpress/v0.5.5/kvpress/presses/expected_attention_press.py) models future queries using mean/covariance and future RoPE positions to score existing KV. It is not RoD's live-question contrastive score, but query-distribution-based importance and reusable context compression are established ingredients. |

The four new arXiv abstracts were opened together at [this API query](https://export.arxiv.org/api/query?id_list=2503.16163,2410.05004,2406.19707,2505.02922). No full PDFs were downloaded.

## Provisional official-rubric scores

These score the reviewed plan/evidence package, **not the still-awaited final abstract**, using `../_briefs/perceptron.txt:308-354`. They are reviewer judgments, not measured competition outcomes.

| Criterion | Weight | Score / 5 | Reason |
|---|---|---|---|
| Problem understanding and relevance | 20% | **4** | Correctly targets irreversible eviction and future questions; retained-state versus GPU-capacity scope needs narrowing. |
| Technical soundness and feasibility | 25% | **3** | Concrete, runnable small-model design; approximate reconstruction and bounded-memory construction are not yet validated. |
| Innovation / novelty | 20% | **3** | Plausible useful combination, but recall/indexing/recomputation precedents are strong and scorer differentiation remains exploratory. |
| Clarity and structure | 10% | **3** | The mechanism and protocol are understandable; stale bits, "faithful," and ambiguous memory/first claims obscure the exact promise. |
| Impact and evaluation rigor | 15% | **3** | Preregistration, pairing, references, and lexical controls are strengths; loss margin, effective sample size, and semantic/peak-memory tests remain gaps. |
| Team fit and readiness | 10% | **2** | Prototype progress is credible, but confirmed three-member skills/responsibilities and execution milestones are absent from the reviewed materials. |

**Weighted total: 3.10 / 5 = 62 / 100**, calculated as `4*.20 + 3*.25 + 3*.20 + 3*.10 + 3*.15 + 2*.10`. The highest-value improvement is not another scorer sweep: it is a bounded claim supported by full-cache loss, honest memory accounting, a stronger task-aligned comparator, and a discriminating follow-up workload.

## Reproducing this review's numerical spot-checks

The dev values come from the committed JSON, not a new model run. The memory and small-sample examples above are analytic checks. This command needs only Python's standard library and runs from the repo root:

```bash
python3 - <<'PY'
import ast, json, math, random
from pathlib import Path
p = Path("perceptron-p02-kv-cache")
rows = json.loads((p / "components/recall_on_demand/autoresearch/dev_sweep.json").read_text())["rows"]
print("rows, variants:", len(rows), len({r["variant"] for r in rows}))
for f in (0.1, 0.25):
    rr = [r for r in rows if r["frac"] == f]
    for v in ("softmax_lift/content/4/5", "lexical/content"):
        print(next(r for r in rr if r["variant"] == v))
    print("best 2-bit:", max((r for r in rr if "/2/" in r["variant"]), key=lambda r: r["hit"]))
    print("best non-layer5:", max((r for r in rr if not r["variant"].startswith("lexical") and not r["variant"].endswith("/5")), key=lambda r: r["hit"]))
    T, per, B = 4096, 32768, round(f * 4096)
    for tag, extra in (("dev", 164*T), ("registered", 292*T + 262144)):
        kv = B - math.ceil(extra / per)
        res, m = kv // 2, (kv - kv // 2) // 64
        print(tag, f, "resident/blocks:", res, m)
        if tag == "registered":
            en = T - res
            stored = res*per + 288*en + 4*T + 262144
            print("logical answer/cap MiB:", (stored + m*64*per)/2**20, B*per/2**20)
            print("window-score tensor MiB:", 32*64*en*4/2**20)
tree = ast.parse((p / "eval/kvbench_torch.py").read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "boot_delta")
ns = {"random": random}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "<review>", "exec"), ns)
print("bootstrap, 12 zero deltas:", ns["boot_delta"]([0.0]*12))
print("zero bad contexts/12, one-sided95 upper probability:", 1 - 0.05**(1/12))
print("weighted rubric:", 4*.20 + 3*.25 + 3*.20 + 3*.10 + 3*.15 + 2*.10)
PY
```
