# Final abstract review: gpt-6-astra

**Verdict: technically credible Round-1 proposal, but not submission-ready as worded. Score: 70/100.** The numerical results reproduce; the principal defects are the promise in the title, the resource being claimed, and the presentation of confirmatory versus exploratory evidence. Fixing those does not require another scorer sweep or hiding the negative result.

Reviewed 2026-10-04 against snapshot `6b8d8c9804d3bf492d097d41d8a1dee22491dda8`, including PREREG amendments 2-5 and the phase-1 triage. Paths below are relative to `perceptron-p02-kv-cache/`. The official rubric is `../_briefs/perceptron.txt:308-354`. This is an independent hostile-reviewer score, not a prediction of the panel's score.

## What is now established

The registered quarter-budget comparison beats StreamingLLM and the additional specified eviction baselines. The primary also replicates on T2. The registered five-point non-inferiority claim against full KV **fails** at quarter budget: this is not merely an underpowered positive trend; the paired interval is entirely below zero. The smaller-budget T1 result is promising but exploratory. The T2 output-length sensitivity substantially reduces the apparent advantage over full KV. T3 is inconclusive by its predeclared full-cache floor.

The phase-1 response is substantive: explicit loss margins, row-derived contrasts, missing-baseline/halo analyses, approximate-KV oracles, and adverse outcomes are now recorded. The surviving contribution is a useful, testable storage/recomputation design, not established general semantic recall or near-lossless GPU inference.

## Number audit

I independently read the JSONL rows, checked unique context/question keys, recomputed counts and paired context-bootstrap intervals (2,000 resamples, seed 0), and checked the retained-byte caps. I also regenerated the document strings **in memory**, without rewriting the abstract or results. They exactly match the committed renderer output. `python3 eval/wordcount.py` reports **886**, inside the suggested 600-900 range.

| Abstract claim | Independent check and verdict |
|---|---|
| 1B model, 32 KiB/token; 32k tokens about 1 GiB | `results/T1_literal_s0.json` identifies the dequantized `mlx-community/Llama-3.2-1B-Instruct-4bit` snapshot. Every row has `full_bytes = T * 32768`. Exactly 32,768 tokens give 1 GiB; "32k" is rounded shorthand. This is fp16 KV, not fp32 compute-state memory. |
| Layer 5; 4-bit index; 288 B/token; 0.88%; last 64 queries; 256 KiB; 4-byte IDs; 64-token blocks | Consistent with the frozen config and `eval/kvbench_torch.py`: `8*(64*4/8+4)=288`; `288/32768=0.0087890625`; `32*64*64*2=262144`. Index bytes apply to indexed/evicted tokens, not a second full KV copy. |
| 12 contexts, 48 questions, about 4k tokens | All tested configurations have 48 rows on 12 contexts. T1 context lengths: 4,044-4,293; T2: 4,036-4,289; T3: 4,013-4,181. Four questions per context are not four independent clusters. |
| Development selection: best of 322 | `components/recall_on_demand/autoresearch/dev_sweep.json` has 322 unique variants, each evaluated at two fractions. The old 0.95 surrogate is appropriately absent from the final abstract. |
| T1 full 83%; RoD at 25%: 58% | Full **40/48**, RoD **28/48**. Correct rounding. |
| Ten query-agnostic baselines at 25%: 0%-35% | Own StreamingLLM plus the nine S1 comparators span **0/48 to 17/48**. These are ten tested implementations, including related own/reference policies, not ten independent algorithm families. |
| Primary: +0.40, 95% CI +0.25 to +0.54 | RoD **28/48** versus own StreamingLLM **9/48**: difference **19/48 = 0.395833**, interval **[0.25, 0.541667]**. Matches. |
| RoD at 25% is 0.25 below full | **-12/48 = -0.25**, CI **[-0.416667, -0.083333]**. The five-point non-inferiority test fails. |
| T1 RoD at 10%: 85%; baselines at most 6% | RoD **41/48**; best tested eviction baseline, kvpress TOVA, **3/48**. Correct. RoD minus full is only **+1/48**, CI **[-0.145833, +0.1875]**; neither equivalence nor superiority to full follows. |
| T2 at 10%: RoD 69%, full 46%; +0.23, CI +0.10 to +0.38 | RoD **33/48**, full **22/48**; difference **11/48 = 0.229167**, CI **[0.104167, 0.375]** under the original 10-token rule. Numerically correct but confounded. |
| 12 of 26 full-cache misses cut off | **26** misses is exact. The **12** count reproduces `render_docs.trunc_stats`: no seven-digit number and answer length at least 30 characters. That is a truncation **heuristic**, not a recorded finish reason; see issue 4. |
| E6, 32 tokens, strict first-number scoring: full 67%, RoD 75% | `e6_maxnew32_T2.rows.jsonl`: full **32/48**, RoD at 0.10 **36/48**. Re-extracted first numbers match all stored strict flags; lenient and strict totals agree. The exploratory paired difference is **+4/48 = 0.083333**, CI **[-0.020833, +0.229167]**. |
| RoD minus lexical at 25%: +0.04 [-0.04,+0.12] T1; +0.27 [+0.10,+0.44] T2 | T1: **28 versus 26** correct, difference **0.041667**, interval **[-0.041667, 0.125]**. T2: **28 versus 15**, difference **0.270833**, interval **[0.104167, 0.4375]**. Matches the renderer's rounding. T2's contrast remains under the old decoding cap; E6 did not rerun `rodlex`. |
| Accuracy conditional on a recalled needle: 98% at 10%, 55% at 25% | T1: **41/42** versus **24/44** among rows with a needle-block hit. These are conditional subsets, not 48-question overall recall. At 25%, **16/20** wrong answers contain another needle's value. |
| Exact KV gives 90%; top-2 gives 85% | T1 at 0.25: E2 **43/48**, E5 **41/48**, verified from `posthoc_T1.rows.jsonl`. These are unconditional answer accuracies, unlike the preceding 55% conditional measure. Both are exploratory; E2 needs full backing KV and is not a deployable same-memory competitor. |
| T3 full recall 10%; block hit 23% versus lexical 73% | Full **5/48**; RoD **11/48** versus lexical **35/48** needle-block hits at 0.10. The full-cache floor is below 0.5, so semantic retrieval success is not established. |
| CPU answer time 6.2 times StreamingLLM | T1 at 0.25: mean **2.8928125 s / 0.4638125 s = 6.23703**. Correct at that operating point, not a general GPU or all-budget overhead. At 0.10, the corresponding ratio is about **3.38**. |
| 50%, 25%, 10% memory; existing int8/4/2 controls | The fractions are configured **retained-state caps**, with RoD often below the cap, not measured process peaks. Quantization controls store all tokens at their selected precision rather than running at all three keep fractions. Reference presses at 0.50 are explicitly unrun. RoD cap violations: **0/36** cells in T1, **0/36** T2, **0/24** T3. |
| 2+ baselines, 3B next, 16-32k next, weeks and exam dates | Multiple baselines are implemented. The larger model, context lengths, and milestone weeks are future commitments, not experimental results. No inference is drawn from them. The three-person team is still a stated plan with missing names. |

Sources for the table are the named row files under `eval/results/`, corresponding metadata JSON, `eval/RESULTS.md`, the frozen harness, and the dev JSON. No model inference was rerun for this review.

## Ranked issues and concrete fixes

### 1. Major: the title promises the property the registered test failed to demonstrate

**Evidence:** `deliverables/round1-abstract.md:3`: "so that eviction stops causing forgetting." At the registered 25% point, RoD loses 25 percentage points versus full, with CI [-41.7,-8.3] points (`eval/RESULTS.md:9`).

**Fix:** Rename it to a bounded mechanism claim, for example **"Recall-on-Demand: token-backed selective recomputation after KV eviction."** In the results, explicitly say that five-point non-inferiority failed at 25%. Do not let the 85% point at 10% read as a substitute near-losslessness proof: its T1 interval permits a 14.6-point loss, and that operating point was selected for follow-up after seeing T1.

### 2. Major: "25% of the KV memory" still risks being read as a demonstrated memory-capacity improvement

**Evidence:** Abstract lines 24-25 and 49; PREREG amendment 2 explicitly limits "answer-time bytes" to persistent state plus recalled KV. `RESULTS.md:234-248` reports unchunked transient scoring sets around 70-89 MiB. Prefill still builds full KV first. The abstract says "after prefill" once but never explicitly excludes peak memory or GPU measurements from its headline.

**Fix:** Add one sentence near the first fraction: **"Budgets are logical post-prefill context state including recalled KV, not peak RAM/VRAM; all current timings are CPU measurements."** Say "within a 25% state budget," rather than literally equal memory. The streamed-scorer check is valuable but does not itself measure a whole-program peak or prove a bounded-memory prefill.

### 3. Major: the corrected T2 result belongs ahead of the confounded apparent win

**Evidence:** Abstract line 49 leads with 69% versus 46% and a positive CI, then places the 32-token sensitivity in parentheses. E6 restores **10 additional full-cache answers**, shrinking the apparent gap from 11 to four questions. The E6 paired CI includes zero: [-2.1,+22.9] percentage points.

**Fix:** Lead with **"On a longer-answer sensitivity check, RoD scored 36/48 versus full 32/48; superiority is not established"**, labelled exploratory. Keep the original R1 result as the registered-protocol outcome with its confound, not as the best evidence of increased recall. Specify that R1 used a lenient 15-point margin, not the five-point S7 margin. T1's 10% operating-point discovery should also be called exploratory. This preserves the successful primary while avoiding a misleading rescue narrative.

### 4. Major: "pre-registered before running" overstates the chronology; "12 cut off" overstates the logging

**Evidence:** Abstract lines 41-45 group all comparisons under "before running." Amendment 3 added S7 at 15:35 while T1 was already running; amendment 4 added R1 at 16:21 after T1 outcomes and after T2 started, with the explicit assurance that no T2 outcomes had been seen. Amendment 5 is post hoc. Separately, `eval/render_docs.py:151-156` counts likely truncations using a character-length heuristic; original rows retain only `text.strip()[:48]` (`kvbench_torch.py:522`) and no generated-token count or finish reason.

**Fix:** Say **"Primary registered before execution; dated amendments before the relevant outcomes, with post-hoc diagnostics labelled separately."** There is no evidence here of concealed test peeking; the problem is the abstract's blanket wording. Change the truncation count to **"12 full-cache misses look truncated by our heuristic; extending generation recovered 10 of them."** If retaining an exact termination claim later, log token counts and stop reasons. E6 supports the truncation confound without authenticating all 12 termination events.

### 5. Major for submission readiness: human team evidence is unfinished

**Evidence:** `deliverables/round1-abstract.md:56` still contains "[names to be added]." The rubric asks whether the actual three-member skill mix supports execution, not whether three suitable role labels can be invented.

**Fix:** The lead should fill confirmed member names, one relevant capability per member, and owned milestones before submission. Do not fabricate credentials. Replace relative weeks with dates if needed to ensure the demo/compute work is finished before the stated 19-25 November exam window.

### 6. Minor: the MVP mapping overgeneralizes the evaluation grid and the ten-baseline count

**Evidence:** Abstract lines 24-27 suggest each method's recall drop is available at 50%, 25%, and 10%; kvpress presses were not run at 0.50, and int8/4/2 are full-token precision configurations. The ten eviction baselines include own/reference versions of related methods.

**Fix:** Say **"Eviction at 10/25/50% state budgets, reference presses at 10/25%, plus full-token quantization controls."** Use "ten tested policy implementations" or simply "tested eviction baselines." The missing cells are already honestly marked in RESULTS; make the abstract agree.

### 7. Minor: distinguish current backend and empirical diagnostics from broader mechanism/novelty claims

**Evidence:** Abstract line 21 calls MLX the demo tool, while the shipped demo imports the PyTorch harness (`demo/server.py:140-142`). Line 35 calls the evaluation a contribution even though context-only multi-query evaluation already appears in the cited kvpress/KVzip work. Line 52 uses the categorical causal close "so approximately recomputed extra blocks cause the loss."

**Fix:** Identify the current artifact as a **PyTorch CPU demo**, with MLX as a separate/planned path. Describe the protocol and controls as rigorous evaluation, not novel in isolation. The matched exact-KV and top-2 interventions are good evidence: say they **implicate approximate multi-block reconstruction on these T1 contexts**, not that all larger-budget or general-context losses have one established cause. Also identify the four-bit-weight checkpoint so results are not mistaken for the original unquantized Llama release.

## Official rubric, 1-5

| Criterion | Weight | Score | One-line reason |
|---|---:|---:|---|
| Problem understanding and relevance | 20% | **4** | Clear account of eviction under unknown future questions, with realistic small-model scope; title/resource wording outruns it. |
| Technical soundness and feasibility | 25% | **4** | Working frozen-model prototype, reference comparisons and matched reconstruction diagnostics make the proposal credible; peak-memory and longer-context work remain planned. |
| Innovation / novelty | 20% | **3** | A useful combination and contrastive scorer, properly related to prior art, but not yet differentiated by semantic retrieval or strong task-general gains. |
| Clarity and structure | 10% | **3** | All required sections fit in 886 words, but dense result paragraphs and mixed evidence status can mislead a rapid reader. |
| Impact and evaluation rigor | 15% | **4** | Unusually strong negative-result disclosure, paired rows, registered decisions and sensitivity checks; only 12 clusters and a narrow synthetic task limit generality. |
| Team fit and readiness | 10% | **2** | Responsibilities and milestones exist, but the actual members and evidence of their skills are still placeholders. |

**Weighted total: 3.50/5 = 70/100** (`4*.20 + 4*.25 + 3*.20 + 3*.10 + 4*.15 + 2*.10`).

The proposal earns serious consideration on technical discipline, not on the unqualified "forgetting stops" story. Its most defensible pitch is **a memory/compute tradeoff with a diagnosed failure mode and an explicit plan to improve it**.

## Reproducing the additional E6 interval

This reviewer-derived interval is exploratory, not a new registered outcome. Run from `perceptron-p02-kv-cache/`:

```bash
python3 - <<'PY'
import json, random
from pathlib import Path
rows = [json.loads(s) for s in Path("eval/results/e6_maxnew32_T2.rows.jsonl").read_text().splitlines()]
a = {(r["sample"], r["q"]): r["strict"] for r in rows if r["method"] == "rod" and r["frac"] == 0.1}
b = {(r["sample"], r["q"]): r["strict"] for r in rows if r["method"] == "full"}
assert a.keys() == b.keys() and len(a) == 48
d = [sum(int(a[(s, q)]) - int(b[(s, q)]) for q in range(4)) / 4 for s in range(12)]
rng = random.Random(0)
boot = sorted(sum(d[rng.randrange(12)] for _ in range(12)) / 12 for _ in range(2000))
print(sum(d) / 12, boot[50], boot[1949])
PY
```
