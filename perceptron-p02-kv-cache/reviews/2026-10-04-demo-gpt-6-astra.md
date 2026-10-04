# Judge-watching-the-demo review: gpt-6-astra

**Verdict: a compelling, evidence-backed replay with a credible interactive mechanism, but fix the stale T2 explanation, memory labels, and comparison layout before presenting.** The budget knob and the intentionally exposed 25% failure are stronger than a conventional happy-path demo. The live screenshot is visually convincing, but does not establish an advantage over lexical retrieval: that control also answers correctly.

Reviewed 2026-10-04 under PLAYBOOK section 11.7. Source snapshot: `346da4f4dc7805abbb53c0f0f3c9b9607a9f763d` (demo code unchanged from `6b8d8c9`). Paths are relative to `perceptron-p02-kv-cache/`.

**Method and boundaries:** this reviewer independently drove Replay using Playwright and checked its data against committed rows. Two isolated auxiliary assessments supplied unanchored design/fallback inspection (`demo-design-assessment`) and deterministic/browser quality evidence (`demo-detector-assessment`); their findings are identified below. No live inference, `--live`, model loading, or dependency installation was performed. The initial shared browser tab showed concurrent activity, so the reproducible interaction matrix below was performed in a separate browser context and that context was closed. The temporary replay server was stopped after inspection.

## PLAYBOOK 11.7 gate

| Requirement | Judgment | Evidence and limit |
|---|---|---|
| One-command start; first visual within 60 seconds | **Pass for Replay** | Ran `demo/run.sh --no-open`; server started on localhost:8502 with `allow=false`, `weights=null`. A fresh browser-context navigation to the running server recorded first contentful paint at **64 ms**, load about **123 ms**, with no external resource requests. This is page-navigation timing, not a cold-machine benchmark. The committed export avoids any model/data fetch during ordinary replay startup. |
| Core claim and baseline side by side | **Pass, with a layout caveat** | Full, RoD, lexical control, eviction implementations, quantization and the question-aware oracle are visible in the same comparison. The shared token axis explains resident versus recalled state. On a 1200px viewport, the comparison table intrudes into the sidebar; see issue 3. |
| Real evidence first; synthetic material labelled | **Pass** | Opens on committed real-model T1 outputs over WikiText-103. Planted facts are visibly marked SYNTHETIC. This is a synthetic recall task with real model outputs, not real-world QA evidence. |
| A judge-operated, striking capability | **Pass for Replay; live operation not rerun** | Budget changes update answers, recall and memory tracks. The "Show this case at 25%" control exposes a real wrong-answer transition. The recorded live X-ray visualizes which blocks the question retrieves; its successful custom-fact path is supported here by screenshots, source and the lead's reported smoke result, not a fresh inference run. |
| Every number has provenance; no unsupported claims | **Numerical provenance passes; wording needs repair** | All **4,512** exported rows and their displayed aggregates match source results. The T2 fallback explanation and peak-memory implication are exceptions in interpretation, not fabricated data. |
| Three-minute script and recorded fallback | **Present, timing/content revisions needed** | SCRIPT and all nine screenshots exist. The live minute has insufficient timing margin; the screenshots predate the expanded E6 numbers. |
| Headless smoke coverage | **Code inspected; safe replay checks independently exercised** | The script checks export equality, JS, HTTP and live behavior. I did not invoke its model-dependent regeneration path because this worktree has no haystack data and live execution was forbidden. Independent row/export equality, JS parsing, no-external-dependency, HTTP serving and replay-only rejection checks passed without those dependencies. |

## What I actually exercised

All eleven supported T1/T2/T3 and 100/50/25/10% combinations were traversed in the private Playwright context. **T3 at 50% is correctly disabled** with "no committed rows at 50%"; reference presses at 50% are explicitly "not run", rather than interpolated. No page errors occurred in this supported-state pass.

| Interaction | Observed result |
|---|---|
| T1, 100% | Full **40/48**; int8 **40/48** at about 53% stored bytes; int4 **37/48** at about 28%; int2 **0/48** at about 16%. RoD/eviction rows are explicitly not applicable at 100%. |
| T1, 50% -> 25% -> 10% | RoD overall recall changes **29/48 -> 28/48 -> 41/48**. The 25% state shows failed S7; 10% shows its non-significant difference from full. |
| T1, "Show this case at 25%" | Selects context 1, question 3 (`s=0,q=2`): wild-heron's true value is **6088743**, but RoD returns vivid-glacier's **4664860**. This is a genuine committed confusion case, not an animation inventing a failure. |
| T2, 10% and 25% | The truncation caveat and full E6 sensitivity line are adjacent to the headline. |
| T2, 50% and 100% | The page instead asserts the withdrawn "fewer look-alike records in view" explanation. This is reproducible and contradicts amendment 5. |
| T3 | Full recall **5/48**; RoD/lexical block hits **11/48 versus 35/48** at 10%. Low ceiling is shown prominently; the preregistered verdicts also record inconclusiveness. |
| Live tab on this replay-only server | Clearly says live is off. Compress and Ask buttons are disabled. `/api/compress` rejects a request with HTTP **503**; `/api/status` still reports no loaded weights. |

The data audit checked every exported answer string, correctness flag, stored/answer-state byte count, recalled-block list and needle-hit flag against the corresponding JSONL row: T1 **1,920**, T2 **1,920**, T3 **528**, S4 **144**. Per-question context length/value/position metadata, displayed table strings, headline and verdicts also match the committed renderer. This audit does **not** imply that every prose explanation in the HTML is generated or correct.

## Ranked issues

### 1. Major: T2's withdrawn explanation returns when the budget changes

**Evidence:** `demo/web/index.html:228-234`, especially the hardcoded T2 entry at line 231. At 50% and 100%, `thesis()` falls back to:

> "RoD's 10% score above it means fewer look-alike records in view"

At 10% and 25%, the other branch correctly calls `caveat()` and shows the answer-length confound. `eval/PREREG.md:142-148` explicitly withdraws that causal interpretation for T2.

**Why a judge cares:** A trivial knob movement changes the scientific explanation, not just the operating point. A correct updated data export does not fix this stale hardcoded copy; the current smoke does not catch it.

**Fix:** Use the same amendment-5/E6 explanation for **all** T2 budgets, including 100%. Add an interaction assertion over the budget states so none display the withdrawn text. Lead with full **32/48** versus RoD **36/48** in the longer-answer sensitivity, with its exploratory status; do not frame the old 33-versus-22 comparison as established superior recall.

### 2. Major: "memory actually used" is not what the running comparison process uses

**Evidence:** `demo/web/index.html:130,142,394,643` labels the knob/plot/budget check as KV memory or "memory actually used". The source calculations are valid **logical retained context-state** counts. In Live, `demo/server.py:192-205,254-259` explicitly retains full `Kf/Vf`, all comparator stores and the metadata needed to rebuild them without re-prefill. The replay's underlying measured scorer also has the separately documented transient working set (`eval/RESULTS.md:234-248`).

**Why a judge cares:** The inspector compares several counterfactual method footprints within one program. It does not demonstrate that this process fits into RoD's displayed 9.2 or 11.1 MiB, nor that the model can ingest a context that otherwise OOMs. "No evicted KV backing store" describes the RoD method's information access, not the entire inspection harness.

**Fix:** Rename the axis/table measure **"logical context state: stored + recalled KV"** and add a persistent note: **"Not peak RAM/VRAM. This comparison harness retains full-reference state; prefill and scoring workspace are excluded."** Keep the useful stored-to-answer arrows. Avoid "every method, same budget" as an unqualified table heading because full/quantization/oracle rows have different stated resource requirements.

### 3. Major: the side-by-side evidence is not reliably side by side at ordinary laptop widths

**Evidence:** Both isolated auxiliary assessments observed the same 1200x818 layout defect. The table is about **816px** wide inside a **704px** panel and extends about **111px** into the sidebar region (`demo/web/index.html:41,56-71,113`). The answer comparison begins around **y=887**, below the opening viewport. Screenshot `fallback/01-replay-T1-10pct.png` similarly crops the RoD answer row below the initial view.

**Why a judge cares:** The headline is visible, but its paired answer and memory evidence is obscured or off-screen. The 48-case grid gets prime space before the principal comparison. On the detector's 390px mobile viewport the document expands to about 977px, although phone layout is secondary to the requested Mac demo.

**Fix:** Put a compact **Full / RoD / best eviction baseline** answer-and-bytes comparison immediately beside or below the token tracks, without hiding the lexical control from the detailed table. Collapse or move the 48-case grid until requested. Stack before the two-column content ceases to fit, and contain the full table with a labelled horizontal-scroll region. Preserve the common token axis, which is the strongest visual element.

### 4. Major for a live presentation: the script's one-minute custom-fact segment is overbooked

**Evidence:** `demo/SCRIPT.md:20-21,62-84` assigns approximately one minute to judge typing, compression, a question, X-ray explanation, then a changed-budget answer. Its own timing estimates are **33 seconds** for compression and **15 seconds** for each answer: two answers plus compression already total **63 seconds**, before interaction or narration. Screenshot 08 records a different run at **26.9 s** prefill and **17.89 s** for all-six-method answering, illustrating variability rather than a guaranteed schedule.

**Fix:** Maintain a rehearsed three-minute **Replay-only route** and a separate extended live route. For a strict three-minute live slot, begin with a precompressed document and accept one fresh question/budget intervention; offer custom fact planting afterward. Time the actual sequence with realistic typing and talk, not just model calls. State which route is being shown rather than calling a recorded fallback live.

### 5. Minor: refresh the fallback with the final caveat, and narrow the script's closing claims

**Evidence:** Screenshots 05 and 08 mention amendment 5/E6 but do not include the subsequently exported **67% full / 75% RoD** sensitivity figures. The current page does. `SCRIPT.md:86-89` says "RoD recalls what the full cache recalls"; T1's similar overall rate does not establish identical successful questions or equivalence. Its 2-bit line describes this simple quantizer on this workload, not a general limitation of all 2-bit methods.

**Fix:** Refresh the relevant screenshots after the copy repair, or place a clearly recorded updated E6 results slide beside them. Close with **"41/48 versus full 40/48 on this literal-needle test; equivalence is not established"** and scope the 2-bit failure to the tested implementation. Keep T3's unsuccessful outcome and the lexical control visible. Do not turn the live mango-kulfi example into a claim that the sketch beats lexical retrieval: screenshot 08 has both correct, with lexical using slightly fewer counted bytes.

### 6. Minor: fix small comprehension/accessibility defects without changing the demo's identity

**Evidence:** The auxiliary design/detector assessments report 48 case targets only **18px** high with 3px gaps, an unnamed `role="img"` token-track SVG (`index.html:250`), and missing tab relationships/arrow-key behavior (`index.html:121-124`). In my interaction pass, T3 at 100% also renders the empty clause **"Quantising every token instead: ."** because those controls were not run.

**Fix:** Give the tracks a concise accessible description and a textual selected-block summary, offer keyboard/focus access to block details, increase case targets, and implement or simplify the tab semantics. Suppress the empty quantization sentence. Use "kept / located / reconstructed" before introducing sinks, layers and m; retain precise technical labels in the detail view.

## The "crazy" element: what earns the reaction

The best moment is not just **41 versus 3**. It is the connection between the question, a tiny highlighted historical block, and the recovered answer, followed by the surprising **more memory -> worse recall** case that the team does not conceal. The failure switch is particularly effective because it uses a committed wrong value and leads naturally to the exact-KV and top-2 diagnostics.

The live screenshot's X-ray supports that story: the drawn score selection is explicitly checked against the blocks actually recalled. Screenshot 08 shows T=2,990, B=299, 132 resident tokens, two recalled blocks, and logical RoD state **5.2 -> 9.2 MiB** versus full **93.4 MiB**. Independent arithmetic reproduces those rounded bytes: full 93.4375 MiB, RoD stored 5.171379 MiB, answer state 9.171379 MiB, cap 9.34375 MiB. The output/timing observations themselves remain recorded screenshot evidence, not a fresh measurement by this reviewer.

Do not imply that the live display proves semantic generality or the index's necessity. The lexical control is successful in that example, the main workload uses conspicuous synthetic records, and T3 failed its competence floor. A systems judge can still appreciate an honest storage/compute mechanism with a useful diagnostic interface.

## Fallback and smoke evidence boundaries

The design assessment inspected all nine files:

| Files | What they establish |
|---|---|
| `01-replay-T1-10pct.png`, `02-replay-T1-100pct.png`, `03-replay-T1-10pct-every-method.png` | Default squeeze story, quantization reference and detailed comparisons. |
| `04-replay-T1-25pct-confusion.png` | A recorded adverse operating point, not only cherry-picked successes. |
| `05-replay-T2-10pct-caveat.png`, `06-replay-T3-10pct-caveat.png` | The existence of T2/T3 limitations in the fallback; E6 numerical update still needs refreshing. |
| `07-live-compressed.png`, `08-live-answered-10pct.png`, `09-live-knob-25pct.png` | Recorded compression, real model answers/X-ray and a changed-budget state; not proof of live responsiveness in this review session. |

The lead reports a successful **20/20** live reproduction check. `demo/smoke.sh` indeed requires 20 exact rows: one T1 context, four questions, full plus StreamingLLM/RoD at two budgets. It checks answers, correctness, bytes and recalled blocks. That is a valuable bounded regression test, not 20 independent contexts or coverage of arbitrary custom facts/T2. Its new-fact test deliberately requires full-cache success but does not assert RoD success, which is the honest choice. I did not rerun either live path.

The full `SMOKE_LIVE=0` script still regenerates contexts via tokenizer/data dependencies. Instead of fetching absent data or loading those libraries, I exercised its replay assertions independently with the standard library and Node. Thus I certify the checked export/render/HTTP behavior, **not a fresh full smoke-script pass or context-text regeneration**.

## Auxiliary design-quality evidence

Independent assessment A scored the interface **23/40** on Nielsen heuristics (4 means excellent). This is a design diagnosis, **not** the official competition rubric:

| Heuristic | Score / 4 | Principal consideration |
|---|---:|---|
| Visibility of status | 3 | Replay/live distinction and disabled live state are clear. |
| Match to the real world | 2 | Technical vocabulary precedes the simple cache-miss model. |
| Control and freedom | 2 | Useful controls; keyboard/block inspection remains limited. |
| Consistency and standards | 3 | Coherent visual language, with state-dependent caveat inconsistency. |
| Error prevention | 3 | Unrun budgets and unavailable live actions are guarded. |
| Recognition rather than recall | 2 | Dense grid and jargon impose unnecessary interpretation. |
| Flexibility and efficiency | 2 | Inspection is capable but the presentation path needs staging. |
| Aesthetic/minimalist design | 2 | Strong bespoke tracks compete with dense simultaneous panels. |
| Error recovery | 2 | Source/fallback coverage exists; novice recovery is less obvious. |
| Help and documentation | 2 | Useful script, but timing and scope need repair. |

Assessment B's one CLI scan found **one warning, zero errors**: `flat-type-hierarchy`, `index.html:15`. Its mobile browser detector produced **108 rule findings in 71 element groups**: cramped padding 1, tiny text 25, text overflow 23, line length 27, body-text viewport edge 29, overused font 1, flat hierarchy 1, em-dash overuse 1. These are not 108 independently confirmed defects. Font-fallback detection, intentional segmented controls and punctuation heuristics include false positives; the verified table overlap and small case targets matter much more. Temporary detector helpers were stopped and no overlay/source edits were retained.

**Presentation recommendation:** retain the real-model replay, the lexical control, the common token axis and the failure case. Repair the state-dependent scientific copy and put the actual comparison in the first view; those changes improve judge trust more than added animation would.
