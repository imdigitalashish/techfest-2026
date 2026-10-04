# Code, evaluation and reproducibility review — 2026-10-04

**Scope:** `eval/kvbench_torch.py`, `eval/parity_torch.py`, the frozen C7 dev evaluator and sweep, `eval/PREREG.md`, and `eval/azure/*.sh`. Findings 1–8 record the static snapshot `7be832f`; later commits addressed several of them without changing the registered T1/T2 configuration. Findings 9–13 incorporate the committed test rows and post-hoc sensitivities. The independent rerun below used the same Azure VM and its registered venv. No critical flaw in the explicit-cache attention engine was established.

## Numbered findings

1. **MAJOR — the dev sweep scores variants with the wrong recall/resident budget.** `components/recall_on_demand/autoresearch/eval_torch.py:92-107` always subtracts a **2-bit sketch without window queries**, then uses the same `B_res` and `m` for the 4-bit lift variants and the sketch-free lexical control. The deployed builder instead charges each variant's bits, full token IDs and the 256 KiB query window (`eval/kvbench_torch.py:312-340`). At `T=4096`, keep `0.10`, the sweep grants the selected `softmax_lift/content/4/5` **three** 64-token recall blocks and 194 resident tokens; deployment grants **two** blocks and 182 residents. At keep `0.25`, the sweep grants `rodlex` seven blocks, but deployment grants eight. Thus the reported dev hit@3 = 76/80 is genuine **for the sweep's budget**, not a 10%-budget hit rate of the deployed 4-bit method, and comparisons between scorer variants are not equal-byte comparisons. **Fix:** calculate each variant's resident/recall budgets and eviction boundary using the production `rod_build` logic (including window queries and IDs), then rerun/report a production-aligned dev table; leave the registered test protocol unchanged.

2. **MAJOR — “equal answer-time bytes” measures a logical retained store, not peak answer memory.** The reported number is `st["stored_bytes"] + rec` (`eval/kvbench_torch.py:329-333,518-537`), while the scorer materializes `st["sketch"].dense().float()` plus query/window-by-all-evicted-key score and softmax tensors (`eval/kvbench_torch.py:292-309,349-359`), and block re-prefill temporarily holds sink, halo and new KV (`:360-369`). Question KV tails are equal-length across methods, but **decode** tails vary with the generated answer/EOS; neither is charged (`:243-255,518-535`). A ten-token tail can hold 327,680 bytes of fp16 KV, exceeding the smallest observed RoD-vs-baseline logical-byte slack of 204,908 bytes on T1. This does **not** prove an actual inequality violation, but the omitted tails are not fully symmetric. The harness also keeps the original full `Kf,Vf` alive while every compressed method answers (`:454-457,479-537`); global peak RSS (`:567-575`) cannot isolate a method's peak. At 4k, the 64-query-window score tensor alone can occupy roughly 28 MiB at 32 query heads. **Fix:** state the comparison strictly as *persistent store plus recalled KV*, independently measure per-method incremental peak working memory including variable decode tails (or stream the sketch scorer), and reserve total-memory-equality claims for a measured peak comparison.

3. **MAJOR — the checked-in VM scripts do not recreate the preregistered environment.** `eval/azure/run_on_azure.sh:25-30,32-36` builds `~/venv` with MLX but never calls `setup_torch.sh`, installs `kvpress`, or runs the PyTorch grid from `~/venv_kvp`; its `run` action actually launches `~/venv/bin/python`. `eval/azure/setup_torch.sh:5-9` installs Transformers **5.8.0** while `eval/PREREG.md:10-15` specifies **5.2.0** and `kvpress 0.5.5`; `eval/results/parity_torch.json` was produced under 5.8.0 on a D8ds_v5 rather than the stated grid environment. **Fix:** add a reproducible, pinned `venv_kvp` setup/run path, run parity with the actual grid environment, and record the versions and hardware in the new result.

4. **MAJOR — some preregistered contrasts are absent from the emitted analysis.** `eval/PREREG.md:45-56` requires RoD-vs-*each* reference press, including `kvp_tova`, and S5 at both 0.10 and 0.50. The paired-delta list omits `("rod","kvp_tova")` (`eval/kvbench_torch.py:549-562`); the preregistered command gives kvpress only `--kvp_fracs 0.1,0.25` (`eval/PREREG.md:70-77`; `eval/kvbench_torch.py:445-450`). The S4 halo-only run likewise cannot itself emit a paired halo-vs-no-halo CI (`eval/PREREG.md:53-54,76`; `eval/kvbench_torch.py:549-562`). **Fix:** derive *all* registered comparisons from rows joined by `(sample,q,frac)` across the relevant runs, run the missing 0.50 kvpress cells if S5 is to cover them, and mark any unrun contrasts explicitly rather than claiming “every baseline.”

5. **MAJOR — the benchmark is not a sequential multi-turn chat.** The preregistration explicitly calls it “shared-context multi-query” and “not a multi-turn dialogue” (`eval/PREREG.md:17-21`). Every question forks and discards the same compressed store (`eval/kvbench_torch.py:119-123,243-255,511-537`). That is a valid test of *later independent questions*, but not of maintaining a chat KV cache over the second, third and tenth turns as suggested by `deliverables/round1-abstract.md:8-17,32-34`. **Fix:** confine result claims to independently answered questions after one query-agnostic compression, or add a separate sequential-chat experiment before claiming multi-turn durability.

6. **MINOR — the blanket byte guarantee can fail for shorter contexts against kvpress rounding.** The own-method budget uses `round(f*T)` (`eval/kvbench_torch.py:473-477`), while kvpress 0.5.5's `compute_n_kept` uses `int(T*f)` ([upstream source](https://github.com/NVIDIA/kvpress/blob/v0.5.5/kvpress/utils.py)); `rod_build` fills from the former (`eval/kvbench_torch.py:312-333`). For `T=559`, keep `0.25`, 16 layers/8 KV heads/64 dimensions, the selected RoD config permits 4,568,764 answer-time bytes versus kvpress's 139-token store of 4,554,752 bytes: **14,012 bytes over**. At `T=4096`, computed RoD margins against kvpress are instead positive (1.46 MiB at keep 0.25); no in-scope 4k failure was observed in the smoke data. **Fix:** budget against `floor(f*T)` for press comparisons and assert the per-row inequality against actual baseline bytes.

7. **MINOR — the locally named SnapKV is a sink-augmented variant of the reference.** `eval/kvbench_torch.py:259-279,493-505` pools over *all* context keys including the 64-token observation window and forces four sinks plus that window. [kvpress 0.5.5 SnapKV](https://github.com/NVIDIA/kvpress/blob/v0.5.5/kvpress/presses/snapkv_press.py) drops the observation window's scores **before** pooling, then forces that window; it does not force four sinks. Both use a 64-token window and width-5 average pool. This distinction matters near the window edge and for judging the “SnapKV” baseline, although `kvp_snapkv` separately provides the published reference. **Fix:** label the local variant explicitly, or match the reference's pooling and sink policy.

8. **MINOR — artifacts do not pin the model export, and parity covers only a short full cache.** `eval/azure/setup_torch.sh:12-22` loads the moving model ID and takes the first cached `snapshots/*/config.json`; `eval/kvbench_torch.py:410-424,435-440` loads that export without checking a revision or file digest, despite the snapshot named in `eval/PREREG.md:10-13`. `eval/parity_torch.py:35-64` checks one 75-token full-prefix final logit, not 4k, a pruned reference cache, or block re-prefill. **Fix:** pin and hash the model revision, exported weights, config and haystack; add long-prompt, compressed-cache/absolute-position and block-reprefill parity cases. The already committed preregistered harness revision *is* verified: `git show 3263e9f:perceptron-p02-kv-cache/eval/kvbench_torch.py | md5` equals its stated `74029553e051e0b93d56af5cd51b3267`.

9. **MAJOR — the lexical control does not isolate the retrieval scorer.** `rod_build` removes sketch/window-query overhead for `rodlex`, changing **both** resident size and recall-block count (`eval/kvbench_torch.py:312-333`); both methods then use their own `m` (`:335-355`). At 10% on T1, RoD recalled **2** blocks for all 48 questions and `rodlex` **3**: RoD hit the needle block in 42/48 vs lexical 44/48, yet answered 41/48 vs 21/48. More recalled blocks can *hurt* answer accuracy: on T1 at 25%, the post-hoc top-two-block RoD answers 41/48 versus 28/48 with the default approximately seven blocks (`eval/results/posthoc_T1.json:17-24`). The T2 S2 effect of +0.2708 (95% CI +0.1042 to +0.4375; `eval/RESULTS.md:12-13`) is a valid **system-level comparison under the same nominal byte cap**, not proof the attention scorer alone beats IDF; actual mean logical answer-time bytes differ slightly (RoD 31.035 MiB, lexical 31.192 MiB). **Fix:** also compare the scorers with matched resident KV and identical block counts; report unused lexical bytes, and do not attribute the registered S2 delta solely to sketch quality.

10. **MAJOR — the ten-token answer limit confounds T2 comparisons to the full cache.** `Engine.answer(..., max_new=10)` ends decoding after at most ten tokens (`eval/kvbench_torch.py:243-255`); correctness looks only for the value substring (`:530-535`). In committed T2 rows, the full cache had 26 wrong answers, 17 with no seven-digit number and 12 with a cut-off preamble; RoD at 10% had 15 wrong, nine with no number and four cut off (`eval/PREREG.md:142-149`; independently counted from `eval/results/T2_paraphrase_s1.rows.jsonl`). With 32 tokens, full rises from 22/48 to **32/48** and RoD@10% from 33/48 to **36/48**; first-number and substring scores agree on all E6 rows (`eval/results/e6_maxnew32_T2.json:2-17`). Thus the original +0.2292 T2 RoD-minus-full difference is arithmetic, but its magnitude is not an unconfounded measure of recall. T1's eight full-cache misses all named another needle, not a truncated preamble. **Fix:** keep the 10-token registered result but pair every T2 full-cache comparison with the labelled 32-token sensitivity; do not claim the original 23-point advantage survives unchanged.

11. **MINOR — kvpress and local baselines prefill with different KV precision.** The explicit engine rounds each layer's K/V to fp16 **before** using them in context attention (`eval/kvbench_torch.py:196-225`); `kvp_store` performs an HF fp32-context forward and only converts the resulting compressed cache to fp16 *afterwards* (`:379-392`). This can change later-layer hidden states even when both answer with fp16 K/V. A local 160-token toy Llama gave a maximum later-layer key difference of `0.0004883` and question hidden-state difference `0.0005077`; the direction of any 4k recall effect is unknown. **Fix:** either match the reference's prefill precision to the explicit engine or score with kvpress then gather its selected positions from a common fp16-prefilled cache; quantify long-context numerical sensitivity before treating tiny baseline margins as architectural effects.

12. **MINOR — the dev-only seed guard was not amended for T3.** `components/recall_on_demand/autoresearch/eval_torch.py:76-82` rejects seeds 0–1 but allows seed **2**, which became the T3 test seed in `eval/PREREG.md:80-89`. The committed sweep actually used `100-109` (`components/recall_on_demand/autoresearch/dev_sweep.json:2`), so **no leakage was observed**. **Fix:** reject all registered test seeds or enforce the documented dev range for subsequent exploratory reruns, without retroactively changing the frozen test.

13. **MAJOR — the pre-registered primary win does not meet the low-recall-harm requirement.** S7 requires the lower paired 95% bound of RoD − full at 25% logical memory to exceed −0.05 (`eval/PREREG.md:112-116`). T1 has full **40/48**, RoD **28/48**, a `−0.2500` gap and CI `[−0.4167,−0.0833]` (`eval/RESULTS.md:8-9,209`; independently recomputed from `eval/results/T1_literal_s0.rows.jsonl`), failing even on its upper bound. RoD's 41/48 at 10% is exploratory and its paired CI vs full `[−0.1458,+0.1875]` does not establish five-point non-inferiority. **Fix:** keep primary eviction-baseline success separate from S7 failure; only claim "barely hurting recall" after a separately frozen, held-out configuration passes the same S7 margin under the counted logical budget.

**Disposition on current `main`:** `eval/PREREG.md:100-108` narrows memory and protocol language, distinguishes exploratory dev hit@3, labels the local SnapKV variant, and requires per-cell byte checks; `eval/render_docs.py:107-145,215-232` supplies the previously missing `kvp_tova` and cross-run halo contrasts and marks unrun 50% kvpress cells. `eval/azure/setup_kvp.sh` and `eval/results/env_artifacts.json` now pin the grid environment, model-export/config/haystack hashes, and original/amended harness digests. `eval/results/parity_torch_venv_kvp.json` records parity under the grid's Transformers 5.2.0. Amendment 5 and E6 disclose finding 10, and the results document separately reports the S7 failure in finding 13. Findings 1 and 6 remain budget/rounding caveats; long/pruned **full-model** parity and the matched-block control in finding 9 remain to be measured. The lead owns final acceptance/triage.

## Checks that passed statically or in small local probes

- `eval/kvbench_torch.py:196-232,233-255,335-369`: RoPE uses absolute context positions during prefill, `T` for the question and `hs` for re-prefill; its causal boolean mask has `True` at permitted positions, consistent with PyTorch SDPA. A self-contained 2-layer toy Llama compared chunked last-token and question logits with HF full-forward at maximum absolute errors `6e-7` and `7e-7`; sink-plus-positioned-block re-prefill matched HF at `0.0`. No model weights or Azure compute were needed for this probe.
- `eval/kvbench_torch.py:196-232,259-284`: `repeat_interleave(nh/nkv)` matched HF `repeat_kv` exactly in the probe; H2O adds each chunk's attention mass to earlier keys, and the local SnapKV window mask/pool apply over the intended axes. Packed 2/4/8-bit codes round-tripped exactly through pack/unpack; retained bytes include code bytes **and** fp16 scale/bias (`:75-107`).
- `eval/kvbench_torch.py:312-369,379-392`: stored RoD bytes charge resident K/V, packed sketch, 256 KiB window queries and int32 token IDs; recalled KV is charged separately. The tagged kvpress 0.5.5 [post-attention hook](https://github.com/NVIDIA/kvpress/blob/v0.5.5/kvpress/presses/base_press.py) and [scorer gather](https://github.com/NVIDIA/kvpress/blob/v0.5.5/kvpress/presses/scorer_press.py) physically prune equally many K/V slots per head, retaining their already-rotated original-position keys rather than masked phantom slots. `E.answer(..., pos=T)` supplies the correct next absolute position even though the compressed cache is shorter. An additional toy test with unsorted per-head pruned keys matched an HF continuation using explicit original `position_ids`/`cache_position=T` at maximum error `0.0`; using HF's compressed-length default positions instead diverged. The byte inequality held for all **2,880** same-question RoD-vs-eviction comparisons in committed T1/T2/T3 rows (smallest T1 logical margin 204,908 bytes).
- `eval/kvbench_torch.py:395-408,539-562`: recall CIs resample contexts, and deltas pair methods by sample before context-bootstrap; each registered context has four questions. The dev file records seeds `100-109`; the preregistered tests use seeds `0,1,2` (`eval/PREREG.md:19-34,80-97`). The earlier seed-0 smoke is disclosed, and the additive T3 harness change leaves T1/T2 generation and RNG draws unchanged. Secondary comparisons disclose that no multiplicity correction is claimed. Every T1/T2/T3 positive substring score was also a standalone seven-digit value in its saved answer; no score was inflated by a substring embedded in a longer number in these runs.

## Independently recomputed results and headline determinations

I parsed the committed per-question rows without importing either evaluation or rendering module. For every method/fraction I grouped questions by context and recalculated accuracy, both context-bootstrap CI bounds, stored/answer-time/full MiB, compression and seconds/answer (eight numerical fields per table row), plus needle-block hit and evicted-needle count for RoD/lexical. Against the committed JSON summaries, **790/790 independently calculated fields matched**: T1 332, T2 332, T3 96, S4 30. The paired bootstrap resamples **12 contexts together**, 2,000 times with Python `Random(0)`; percentile indices 50 and 1949 match the registered rule. The independent code used for the primary and the accuracy/byte table is:

```python
import json, random
from collections import defaultdict
from pathlib import Path
from statistics import mean

rows = [json.loads(s) for s in Path("perceptron-p02-kv-cache/eval/results/T1_literal_s0.rows.jsonl").open()]
by = defaultdict(lambda: defaultdict(list))
for r in rows:
    by[r["method"], r["frac"]][r["sample"]].append(r)
for (method, frac), contexts in sorted(by.items()):
    rs = [r for q in contexts.values() for r in q]
    print(method, frac, mean(r["correct"] for r in rs),
          mean(r["stored_bytes"] for r in rs) / 2**20,
          mean(r["answer_time_bytes"] for r in rs) / 2**20)
d = [mean(r["correct"] for r in by["rod", .25][s]) -
     mean(r["correct"] for r in by["streaming", .25][s])
     for s in sorted(by["rod", .25])]
rng = random.Random(0)
draws = sorted(mean(d[rng.randrange(len(d))] for _ in d) for _ in range(2000))
print("paired delta, 95% CI:", mean(d), draws[50], draws[1949])
```

**T1 independent accuracy counts** (four questions per context, 48 per method/fraction; `—` = unrun):

| Method | Full-context (1.0) | Keep 0.10 | Keep 0.25 | Keep 0.50 |
|---|---:|---:|---:|---:|
| full | 40/48 | — | — | — |
| int8 | 40/48 | — | — | — |
| int4 | 37/48 | — | — | — |
| int2 | 0/48 | — | — | — |
| streaming | — | 1/48 | 9/48 | 21/48 |
| random | — | 0/48 | 0/48 | 6/48 |
| h2o | — | 0/48 | 4/48 | 13/48 |
| snapkv | — | 0/48 | 3/48 | 11/48 |
| knorm | — | 0/48 | 0/48 | 6/48 |
| snapkv_qa (question-aware oracle) | — | 40/48 | 40/48 | 41/48 |
| rod | — | 41/48 | 28/48 | 29/48 |
| rodlex | — | 21/48 | 26/48 | 29/48 |
| kvp_streaming | — | 1/48 | 9/48 | — |
| kvp_snapkv | — | 0/48 | 3/48 | — |
| kvp_observed | — | 0/48 | 0/48 | — |
| kvp_knorm | — | 0/48 | 0/48 | — |
| kvp_expected | — | 0/48 | 2/48 | — |
| kvp_tova | — | 3/48 | 17/48 | — |

| Headline number or decision | Independent determination |
|---|---|
| 32,768 fp16 KV bytes/token | **CONFIRMED:** `16 × 8 × 64 × 2 (K/V) × 2 bytes`; the full-cache row asserts `full_bytes = T × 32768` (`eval/kvbench_torch.py:458-462`). |
| fp32 `2e-5` and fp16 `0.01058` maximum logit differences, same argmax | **CONFIRMED:** independent grid-venv parity rerun reproduced both values and top-5 overlap `5/5`. The earlier MLX-vs-torch `5e-5` is **UNVERIFIED** in this venv because MLX is not installed there. |
| Dev winner `0.9500` hit@3, a-priori `0.2375`, lexical `0.9125` | **CONFIRMED** as `76/80`, `19/80`, `73/80` under the frozen *sweep* budget; **REFUTED as deployed 10% hit@3**, since the selected 4-bit method recalled **2 blocks in all 12 T1 contexts**. |
| T1 full-cache recall `0.8333`; RoD and StreamingLLM at 0.25 `0.5833` and `0.1875` | **CONFIRMED:** `40/48`, `28/48`, `9/48`. |
| Pre-registered primary RoD − StreamingLLM at 0.25: `+0.3958`, paired 95% CI `[+0.2500,+0.5417]` | **CONFIRMED:** all 12 paired context deltas recomputed; the lower bound exceeds zero. |
| T1 RoD beats each tested query-agnostic eviction baseline at 0.25 | **CONFIRMED for the nine registered S1 baselines and the separately tested primary StreamingLLM, per-comparison 95% CIs only:** the weakest is `kvp_tova`, delta `+0.2292`, CI `[+0.0417,+0.3958]`; every other lower bound is positive. No familywise multiplicity adjustment is claimed. This excludes the labelled `snapkv_qa` oracle and full-context quantizers. |
| Near-lossless at 25% memory (S7 margin −0.05) | **REFUTED:** RoD − full is `−0.2500`, paired CI `[−0.4167,−0.0833]`, below the non-inferiority margin (`eval/PREREG.md:112-116`). Passing the primary is not passing this brief-level target. |
| Exploratory T1 RoD at keep 0.10 `0.8542` vs full `0.8333` | **CONFIRMED:** `41/48` vs `40/48`, delta `+0.0208`, CI `[−0.1458,+0.1875]`; no superiority or five-point non-inferiority inference follows. |
| T2 replication S3 RoD − StreamingLLM at 0.25 `+0.3750`, CI `[+0.2292,+0.5417]` | **CONFIRMED** on 12 fresh paraphrased contexts. |
| T2 R1 RoD@0.10 `0.6875` vs full `0.4583`, delta `+0.2292`, CI `[+0.1042,+0.3750]` | **CONFIRMED as a 10-token-score result; REFUTED as an unconfounded 23-point recall advantage.** Twelve of full's misses were truncated preambles; exploratory 32-token/first-number E6 yields full `32/48=0.6667`, RoD `36/48=0.7500` (difference `+0.0833`). |
| Sketch vs lexical S2 at keep 0.25 | **CONFIRMED:** T1 `+0.0417`, CI `[−0.0417,+0.1250]` (not statistically separated); T2 `+0.2708`, CI `[+0.1042,+0.4375]` (system-level win, scorer confounded by finding 9). |
| S4 halo 64 − halo 0 on T1 | **CONFIRMED:** keep 0.10 `+0.0000` CI `[0,0]`; 0.25 `−0.0833` CI `[−0.1667,+0.0000]`; 0.50 `−0.0625` CI `[−0.1667,+0.0417]`, pairing the same contexts. |
| T3 meaning-based retrieval / S6 confirmatory at keep 0.10 | **REFUTED as a supported claim:** full-cache recall `5/48=0.1042` is below the preregistered `0.5` ceiling; S6 is inconclusive. RoD − lexical `+0.0625`, CI `[−0.0208,+0.1458]`; evicted-needle block hits are `0.2292` vs lexical `0.7292`. |
| Exploratory reconstruction/precision result at T1/0.25 | **CONFIRMED as post-hoc arithmetic:** exact full-prefill KV for the same blocks answers `43/48=0.8958` vs frozen approximate RoD `28/48=0.5833`; capping recalls to two blocks answers `41/48=0.8542` (`eval/results/posthoc_T1.rows.jsonl`). All 144 streamed scorer block lists equal the original unchunked lists. Exact-KV requires a full backing cache and is **not** a deployable equal-byte method. |
| CPU answer-time overhead `6.2×` StreamingLLM at T1/0.25 | **CONFIRMED:** mean `2.8928` s versus `0.4638` s, ratio `6.237×`, excluding shared prefill/build time. |
| Memory and quantization table | **CONFIRMED:** T1/0.10 RoD stored `7.072` MiB, logical answer-time `11.072` MiB; at 0.25 it stored `16.651` MiB and used logical answer-time `30.817` MiB vs StreamingLLM `32.206` MiB (full `128.833` MiB). At full context int8 is `40/48` at `68.443` MiB/`1.88×`, int4 `37/48` at `36.234` MiB/`3.56×`, and int2 `0/48` at `20.130` MiB/`6.40×` stored compression; packed codes themselves round-trip exactly. |

## Independent Azure reproduction

No heavy reproduction work started before the lead's final `~/p02/e6.done` gate (which also followed `grid2.done` and `posthoc.done`). Reran `HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 ~/venv_kvp/bin/python eval/parity_torch.py` without creating a file: the output matched committed `eval/results/parity_torch_venv_kvp.json` exactly for the fp32/fp16 checks. The VM's harness SHA-256 was `22f88b98b72017d9c2e3219be873b42449ff5679d85e1cad1fc6e611daf3aaae` (the additive T3 amendment); the original registered T1 harness hash is `d9d01f1870ec90939d3755b51543f2657218bf3bc8ee0aefc511f96781798299`. The additive diff does not change literal samples, and the exact-match check below verifies the first two.

From `~/p02` on the VM, using only new `REPRO_*` outputs:

```bash
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 nohup ~/venv_kvp/bin/python -u eval/kvbench_torch.py --ctx 4096 --n 2 --needles 4 --seed 0 --style literal --fracs 0.1,0.25,0.5 --kvp_fracs 0.1,0.25 --methods full,int8,int4,int2,streaming,random,h2o,snapkv,knorm,snapkv_qa,rod,rodlex,kvp_streaming,kvp_snapkv,kvp_observed,kvp_knorm,kvp_expected,kvp_tova --rod_scorer softmax_lift --rod_qsel content --rod_layer 5 --rod_bits 4 --lex_qsel content --name REPRO_T1_n2 > run_REPRO_T1_n2.log 2>&1 < /dev/null &
```

Compared rows keyed by `(sample,q,method,frac)` to `eval/results/T1_literal_s0.rows.jsonl` for samples 0–1. Values and presence of all five requested fields matched, as did `T`, needle position/value, budget `B`, full bytes and relevant environment metadata (apart from the expected run name, sample count, wall time, peak RSS and command). In the Blocks column, `—` means the field is absent in **both** rows, not that block lists were compared.

| Method | Rows | Correct | Answer | Stored | Answer-time | Blocks | All requested fields |
|---|---:|---:|---:|---:|---:|---:|---:|
| full | 8 | 8/8 | 8/8 | 8/8 | 8/8 | — | 8/8 |
| int8 | 8 | 8/8 | 8/8 | 8/8 | 8/8 | — | 8/8 |
| int4 | 8 | 8/8 | 8/8 | 8/8 | 8/8 | — | 8/8 |
| int2 | 8 | 8/8 | 8/8 | 8/8 | 8/8 | — | 8/8 |
| streaming | 24 | 24/24 | 24/24 | 24/24 | 24/24 | — | 24/24 |
| random | 24 | 24/24 | 24/24 | 24/24 | 24/24 | — | 24/24 |
| h2o | 24 | 24/24 | 24/24 | 24/24 | 24/24 | — | 24/24 |
| snapkv | 24 | 24/24 | 24/24 | 24/24 | 24/24 | — | 24/24 |
| knorm | 24 | 24/24 | 24/24 | 24/24 | 24/24 | — | 24/24 |
| snapkv_qa | 24 | 24/24 | 24/24 | 24/24 | 24/24 | — | 24/24 |
| rod | 24 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 |
| rodlex | 24 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 |
| kvp_streaming | 16 | 16/16 | 16/16 | 16/16 | 16/16 | — | 16/16 |
| kvp_snapkv | 16 | 16/16 | 16/16 | 16/16 | 16/16 | — | 16/16 |
| kvp_observed | 16 | 16/16 | 16/16 | 16/16 | 16/16 | — | 16/16 |
| kvp_knorm | 16 | 16/16 | 16/16 | 16/16 | 16/16 | — | 16/16 |
| kvp_expected | 16 | 16/16 | 16/16 | 16/16 | 16/16 | — | 16/16 |
| kvp_tova | 16 | 16/16 | 16/16 | 16/16 | 16/16 | — | 16/16 |
| **Total** | **320** | **320/320** | **320/320** | **320/320** | **320/320** | **48/48 actual lists** | **320/320** |

**Overall verdict:** the pre-registered **RoD > StreamingLLM at 25% logical answer-time KV** result is supported, independently reproduced on the first two contexts, and accompanied by valid context-paired CIs and complete byte accounting for the defined *retained* store. It does **not** meet the registered near-lossless-at-25% requirement; 10% keep is promising but exploratory, and T2's full-cache comparison is truncated under the registered ten-token limit. Neither true sequential chat nor meaning-based retrieval is established. The remaining matched-block, production-budget dev and full-model long-context parity checks are necessary before attributing the gains specifically to the sketch or generalizing them.
