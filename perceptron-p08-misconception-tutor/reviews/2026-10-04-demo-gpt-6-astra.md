# P8 live-demo review - GPT-6 Astra

**Reviewed:** 2026-10-04, 22:28-22:44 IST. **Perspective:** hostile but fair Optiver/IIT Bombay judge. **Scope:** the demo and its committed evidence, not a new model benchmark or implementation change.

Audited checkout: `2d6316d2c44c2dafeb1040d08133598d644a919a`; latest change to the demo/results under review: `69eb602e`. Read PLAYBOOK sections 6 and 11, the demo README and SCRIPT, the abstract, Selection memo, prior-review responses, and `eval/numbers.py`. This is a direct, single-judge runtime/evidence review, not a delegated multi-agent design critique.

**Bottom line:** a real, unusually candid working prototype with a good conditional-prediction moment, but not yet a winning-room demonstration. The most damaging finding is that the tutor forgets a successfully disambiguating answer when asked for another prediction.

## A. PLAYBOOK section 11 checklist

| Requirement | Pass/fail | Evidence |
|---|---|---|
| One command; first visual within 60 seconds; CPU/offline runtime | **PASS**, after the documented dependency bootstrap | Started the prescribed `bash demo/run.sh --no-browser --port 8791` under `nice -n 10` from a fresh worktree with no `.venv` or `.data`. Memory level was 47. Automatic environment setup and server readiness took **2.856 s**. The browser's first contentful paint was **12.275 s after command start**, including tool/navigation delay; navigation-to-paint itself was 64 ms. No remote demo requests appeared in the browser network log. Package installation is a bootstrap dependency, not a claim that a machine without dependencies can install them offline. |
| Real data first, baseline side by side, synthetic labelled | **PASS**, with qualification finding 6 below | The initial view is the 304-entry Eedi outcome register, with engine/GPT-5.5/GPT-5.4-mini/GPT-4.1-mini scoreboards. It says REAL, replayed and pre-registered. The live questions say they are the team's own; probability and stress panels say SYNTHETIC. Probability routing is explicitly construction-guaranteed. |
| The crazy element and a judge-operated knob work live | **FAIL as a complete requirement** | The original seal/reveal works, including an independently recomputed SHA-256. All model/workload/routing buttons work. However, continuous dragging breaks the scripted budget squeeze (finding 2), and continuing a diagnosis discards the answer just observed (finding 1). A track click or keyboard/value change works around the slider problem; it does not make the prescribed drag work. |
| Every on-screen number has honest, reproducible provenance | **FAIL on population attribution**, not wholesale numerical fabrication | The main claims reconcile; see the 20 checks below. GPT-5.4-mini's L3 panel attaches all-depth token/cost averages to an L3 accuracy result (finding 4). Some displayed post-hoc recommendations also lose their label (finding 5). |
| `demo/SCRIPT.md` and recorded `demo/fallback/` | **PASS for availability and usable fallback** | Followed the talk track in order, including both optional live actions. There are 15 numbered PNGs and a standalone HTML page. The HTML equals the current page with the derived-only data inlined. With all network requests blocked and the committed HTML supplied to the browser, tabs 1/3/4 still worked and tab 2 honestly disabled marking and said the engine was offline. The automation harness blocks `file://`, so this was an isolated browser-load check, not a claim to have opened a local file URL successfully. Script wording needs finding 3 and the small routing clarification in finding 2. |
| `demo/smoke.sh` | **PASS** | Ran `nice -n 10 bash demo/smoke.sh`, memory level 49: **49 passed, 0 failed, 1.0 s**. It checked all 21 exported knob rows, live certificates, re-asks, seals, one-use tokens, and no-text refusal. Its optional local-data checks were explicitly skipped because `.data` was absent. Browser interaction and image-leak coverage are weaker than this green result suggests (finding 7). |
| Data notice | **PASS for the displayed notice; not blanket licence clearance** | The notice names Kaggle Eedi, CC BY-NC 4.0, section 7.B, derived-only exports, and own-description labels. No local-text mode was enabled. No identifiable Eedi question, answer-option or distractor text was found in the current tracked artifacts or fallback inspection. Residual label-text and audit limitations are recorded below. |

Port 8791 was already occupied by Python PID **69782**, which was not mine and was left untouched. The launcher selected **8792**; all live browser work used `http://127.0.0.1:8792/`. My server was PID **71871**, niceness 10, in `no-text` mode with zero LLM calls. I stopped that exact PID at **22:44 IST** and verified that port 8792 no longer had a listener. The launch wrapper's termination exit is intentional shutdown, not a demo crash.

### Numerical spot checks

These compare rendered content with fresh `eval.numbers.claims()`, independent counts/sums from `demo/web/data.js`, committed result files, or observed localhost responses. The embedded claims dictionary equals a fresh registry render. Paths below are relative to this project.

| # | On-screen value | Reconciliation |
|---|---|---|
| 1 | 304 real entries; 131 positives; 152 negatives | Per-item counts are 131 P + 152 N + 21 related-label entries = 304; matches `llm_gaps_real_negatives.json` and the export. |
| 2 | Engine 19.1% | 25/131; `real.exec_accP`. |
| 3 | GPT-5.5 79.4% | 104/131; `real.gpt-5.5.accP`. |
| 4 | GPT-5.4-mini 69.5%; GPT-4.1-mini 55.7% | 91/131 and 73/131; the corresponding `real.*.accP` claims. |
| 5 | GPT-4.1-mini 15.8% false claims | 24/152; `real.gpt-4.1-mini.fcr`. The negative register actually changes from 24 red squares to zero when switching to the engine. |
| 6 | Engine and GPT-5.5: zero of 152; upper bound 2.4% | Independent row counts are zero. Exact 95% interval upper endpoints are rendered from `llm_gaps_posthoc.json` by `real.exec.fcr_hi` and `real.gpt-5.5.fcr_hi`. These are sample-conditional bounds, not population-wide safety guarantees. |
| 7 | 26 certificates; 25/25 positives; GPT-5.5 agrees on 26/26 | 25 P entries plus one related-label entry; same code from GPT-5.5 on all 26. `cascade_real.json` and derived rows agree. |
| 8 | Engine repeatability 304/304; median 0.06 ms | `ph.engine_identical` and `ph.engine_ms` from the measured two-pass experiment in `llm_gaps_posthoc.json`. This timing is a benchmark median, not a newly timed per-item measurement. |
| 9 | GPT-5.5 changed 2/40 | `llm_consistency.json`; browser Run 2 highlighted `534_B`, Run 3 highlighted `290_C`. The UI correctly admits that the engine cannot parse either, so the cascade would not fix these flips. |
| 10 | 1,000/1,000 identical live re-asks | Observed `/api/rerun`: 1,000 matches, median **0.045 ms**, total **47.9 ms** on this run. Values come from `demo/live.py:rerun`, not a canned animation. |
| 11 | Real GPT-5.5 cost $6.50 -> $6.10, saving 6.2% | Routed-item sums and `casc.real.gpt-5.5.*` agree. The exported cascade value before display rounding is **6.1015**, relevant to finding 8. |
| 12 | Real cascade: 914 LLM calls per 1,000 | 278/304 routed items, scaled and rounded: 914.47 -> 914. |
| 13 | Probability: $7.32 -> $5.08, saving 30.5% | `diag.gpt-5.5.cost1000_llm`, `cost1000_cascade`, and `saving`; derived from full-precision routed costs, not from subtracting already-rounded display strings. |
| 14 | Probability: 500 calls/1,000; 100.0% of misconception answers; two false claims | 60/120 routed; 60/60 bug answers diagnosed; 2/60 slips falsely labelled by the GPT-5.5 cascade. Construction guarantee is visibly disclosed. |
| 15 | GPT-5.5 inversion 100.0%, 2,309 reasoning tokens | Correct for its 60 L3 items: 138,535 reasoning tokens / 60 = 2,308.9167. GPT-5.5 was only run on L3, per protocol section 2.4. |
| 16 | GPT-5.4-mini inversion 95.0%, 2,251 tokens, $0.011 | **Scope mismatch:** 95.0% is L3. 2,251 and $0.011 average all 180 items. Its 60 L3 rows instead average **3,270.583 tokens** and **$0.0152031**. See finding 4. |
| 17 | Tracer 64.0%; GPT-5.4-mini 66.0% | `trace.tracer_exact` and `trace.gpt-5.4-mini.exact`, each on 100 simulated learners. GPT-5.5's separate 50-learner subset and the paired tracer score are explicitly labelled. |
| 18 | Equal-rate simulation: 28.0% vs 58.4% remaining | `simulation.json`'s equal-rate setting, `sim.pess_ours_left` / `sim.pess_random_left`. Switching to optimistic visibly changes ours to 5.5% and discloses the 0.30 versus 0.10 learning-rate assumption. |
| 19 | Probability generation: GPT-4.1-mini 36.7% | `prob.gen.gpt-4.1-mini.both`: key AND misconception answer exact, not the 40.0% key-only metric. |
| 20 | Slip storm: 2,379 no claim, 21 collisions, 0.9% | Observed live on 300 generated bank items and eight fixed offsets each: 2,400 total; 21/2,400 = 0.875%, displayed as 0.9%. Runtime here was 116.1 ms. This is a deterministic synthetic offset sweep, not a measured rate of human slips. |

## B. Judge reaction

**Do I lean in? Initially, yes.** The mathematical working, visible wrong step, sealed record and browser verification are a much better object to demonstrate than a chatbot claiming insight. The marking-desk visual language fits the task; the data caveat and stronger-model results are conspicuously candid. The slide that admits GPT-5.5 wins coverage earns trust.

The scripted example worked: `3 + 4 * 2 = 14` produced an LTR certificate; the generated question was `2 - 8 * 11`; answering `-66` matched the prediction. The SHA-256 shown before answering was `8fe8f4a08971c484c7059ed80669856a26bd67c2514353ce2b9c322793613450`. Independently hashing the revealed record in the browser reproduced it exactly.

**Is it honest? The commitment is; the strongest spoken inference is not.** The hash proves that this conditional record was fixed before reveal, not that the program read a mind, discovered a human's enduring misconception, or has calibrated confidence. The UI's "if you hold LTR" and explicit failed-prediction paths are good. Instructing a judge to use the same wrong rule makes the first match an execution demonstration, not an independent prediction success. "That is not a random slip" and "the tracer is now sure" undo the otherwise careful framing.

I tried a stronger demonstration than the script: type `(-2)^2`, answer `-4`. Both SQ_DOUBLE and NEG_TIMES_NEG explain it. The tutor picked SQ_DOUBLE as its lead, then generated `(-3)^2 + 3`. I answered `-6`, deliberately following NEG_TIMES_NEG instead of the lead prediction `-3`. The page admitted the miss, verified the hash, shifted to NEG_TIMES_NEG, and generated appropriate practice. **That was the best moment in the demo.** Clicking "Seal another prediction" then forgot the evidence and selected SQ_DOUBLE again.

### Questions I would ask

| Question | Does the current demo survive? |
|---|---|
| "Why not just GPT-5.5?" | **Survives an honesty challenge, not a differentiation challenge.** GPT-5.5 has 79.4% versus 19.1% positive coverage, the same observed zero false claims, and agrees on every engine certificate here. Real cost saving is about $0.40 per 1,000 diagnoses, post hoc. Deterministic execution, offline operation and independently verified arithmetic are legitimate component benefits. The next fair comparator is GPT-5.5 with the same verifier, question bank and interface, not only a bare classifier. No comparative human learning gain is demonstrated. |
| "Does the tutor update when I prove it wrong?" | **Yes for one reveal; no on continuation.** The competing-rule test above is excellent until finding 1 resets the state. |
| "What does the displayed 1.00 mean?" | A rounded output of a specified Bayesian model with assumed parameters, not empirical certainty about this judge. Four untested rules remain at 0.30. The current script does not survive pressing this distinction. |
| "Are these 304 learners, or real student trajectories?" | Neither is established by these artifacts. They are selected, misconception-labelled Eedi question/distractor entries. Model outputs are replayed; actual learner histories and learning outcomes are not. |
| "Can I see the real questions, and can you deploy this dataset commercially?" | Correct response: do not enable local-text or expose restricted Eedi content; show the team's own questions. The displayed notice gives the non-commercial and redistribution constraints. This review is not clearance for broader distribution. |

## C. Numbered issues and concrete fixes

1. **major - Continuing a prediction discards the diagnosis just learned.**

   **Pointer:** `demo/live.py:288-345` (`predict`, especially the fresh tracer/state at 298-300); `demo/web/index.html:sealIt` and "Seal another prediction".

   **Evidence:** For `(-2)^2 = -4`, the first lead is SQ_DOUBLE. On the follow-up `(-3)^2 + 3`, answering `-6` changes SQ_DOUBLE to **0.0007** and NEG_TIMES_NEG to **0.9995**, with NEG_TIMES_NEG practice. "Seal another prediction" repeats the identical follow-up, resets both to **0.5868**, and returns to SQ_DOUBLE. The LTR case likewise resets a disconfirming answer. This is not longitudinal tracking; it is restarting the original two-answer vignette without saying so.

   **Fix:** Continue from the updated learner state and history returned by reveal, exclude already asked questions, and choose the next lead from that updated posterior. Keep reset as a separate, explicitly named action. Add a three-answer regression covering the competing-rule sequence above. If continuation is intentionally out of scope, rename the control "Restart this two-answer example" and visibly disclose the reset.

2. **major - The budget slider cannot be continuously dragged as SCRIPT instructs.**

   **Pointer:** `demo/web/index.html:878-881`, `renderCascade`; SCRIPT's 2:10-2:45 segment.

   **Evidence:** A continuous 20-step mouse drag from $8.00 toward $6.30 stopped at **$7.90**. Every `input` event replaces the slider DOM node and loses the ongoing native drag. Clicking the track at $6.30 worked and displayed the intended "fits only with the engine first" explanation.

   **Fix:** Keep the actual range element mounted while updating labels/chart, or defer the destructive rerender until the drag ends. Add a real pointer-drag browser assertion, not just a programmatic value change. Also explicitly reselect **Engine first** after returning from **LLM unplugged** in SCRIPT; returning to Real Eedi preserves unplugged routing.

3. **major - Spoken certainty exceeds what the live evidence supports.**

   **Pointer:** `demo/SCRIPT.md:11,42`; `demo/live.py:_posterior`; `demo/web/index.html:postBars`; `components/learner_model/core.py` defaults.

   **Evidence:** The script says both "not a random slip" and "the tracer is now sure". The first LTR answer already yields **0.9942** under assumed consistency 0.8, slip 0.1, epsilon 0.02 and prior 0.30. A matching follow-up displays **1.00**; even a correct disconfirming answer leaves **0.9717**. These are actual model outputs, not fabricated values, but no real-learner calibration establishes their interpretation as confidence in a person's belief.

   **Fix:** Say "compatible with this rule" and "more evidence for this hypothesis under our model". Label the posterior as assumption-dependent and not empirically calibrated, expose the emission assumptions, and avoid rounding interior probabilities to categorical 0.00/1.00. Let the judge deliberately falsify the lead prediction instead of only coaching a match.

4. **major - One stress-panel comparison uses different populations for accuracy and effort.**

   **Pointer:** `demo/web/index.html:945-951`; `eval/numbers.py:129-134`; `demo/fallback/14-stress-tests-synthetic.png` and `15-stress-tests-synthetic-2.png`.

   **Evidence:** The 4-8-operator panel shows GPT-5.4-mini's L3 accuracy with **2,251 tokens / $0.011**, averages over L1-L3. The committed 60 L3 response rows give **3,271 tokens / $0.015** when rounded the same way. GPT-5.5's 2,309 is correctly L3-only, so the cost/effort comparison is asymmetric.

   **Fix:** Add level-specific token/cost claims from the response rows and bind the panel to L3, or explicitly label each effort statistic "all levels, n=180" and separate it from the L3 comparison. Regenerate affected fallback images. Assert the population as well as the rendered numeric string in smoke checks.

5. **minor - POST HOC labels disappear while post-hoc recommendations remain visible.**

   **Pointer:** `demo/web/index.html:882-906`, especially the routing-dependent label; fallback screenshot `12-cascade-llm-unplugged.png`.

   **Evidence:** Real Eedi + LLM only, engine gate, or LLM unplugged gets a **pre-registered** heading, but the budget recommendation and scatter still show post-hoc engine-first cost/accuracy, including GPT-5.5 at $6.10. The explicit POST HOC tag only follows the currently selected routing.

   **Fix:** Put the provenance on each engine-first recommendation/point or give the entire comparison a persistent "includes post-hoc real-cascade analysis" note. Selecting another route must not remove the qualification from the results still displayed.

6. **minor - The opening omits important qualifications already accepted in the previous review.**

   **Pointer:** `demo/web/index.html:403-404`; `eval/run_llm_gaps.py:build_real`; protocol's appended Exposure clarification.

   **Evidence:** "Pre-registered before any model run" is broader than the protocol's corrected statement: 129 linked positives and earlier GPT-4.1-mini outputs had already been inspected; new-prompt outputs had not. The register also does not explain up front that negatives are parser/key-agreement-gated, while these are distractor entries rather than observed learner trajectories.

   **Fix:** Use "new-prompt comparison pre-registered on a previously inspected corpus" and "selected Eedi question/distractor entries". Add a compact population note: 131 positives, 152 parser/key-gated negatives, 21 related-label sensitivity entries; no human longitudinal validation. Do not imply backdating: none was found.

7. **minor - The green smoke test is not a complete redistribution or browser-interaction guard.**

   **Pointer:** `demo/smoke.py:265-318`, `check_server_notext`, `check_docs`.

   **Evidence:** The optional leak check did not run here. When it does run, it scans selected textual files under `demo/`, not PNG pixels or all tracked project files, and constructs needles from questions/expressions rather than a complete answer/distractor corpus. The $/% membership check also cannot detect finding 4's wrong population. HTTP checks missed finding 1 and finding 2.

   **Fix:** Add browser regressions for continuation, pointer drag and invalid input. Separate the licence audit from the local-text server check; audit all release artifacts, including image OCR/manual sign-off and answer/distractor content, without enabling local-text presentation. Make skipped licence coverage conspicuous rather than treating SMOKE PASS as release clearance.

8. **minor - Budget eligibility and displayed prices disagree at rounded boundaries.**

   **Pointer:** `demo/web/index.html:bestUnder`, `budgetInsight`, `usd`.

   **Evidence:** At a displayed budget of $6.10 the $6.10 GPT-5.5 cascade is not eligible; its internal cost is **6.1015**, so the $0.05-step slider must reach $6.15. Likewise a displayed $1.25 cascade costs **1.2505** and is excluded at $1.25. The underlying arithmetic is correct, but the judge sees an apparent contradiction.

   **Fix:** Show sufficient precision at the decision boundary or show the minimum selectable budget required. Do not silently round down the actual expense just to make the comparison pass.

9. **minor - Run 3 remains selectable for models with no third run.**

   **Pointer:** `demo/web/index.html:realCode`, `realRegister`, `askAgainNote`.

   **Evidence:** GPT-5.4-mini + Run 3 and GPT-4.1-mini + Run 3 leave zero bright data tiles, while the note still announces their disagreement count. Only GPT-5.5 has a third run.

   **Fix:** Disable unavailable runs or clearly label "not collected"; when changing models, select an available run rather than an unexplained empty register.

### Redistribution audit: no identified critical item-text leak

Inspected the current tracked project inventory (**148 files**), the derived export, relevant parser/tests/templates, real-result structures and stored response schemas. All **912** main real-model responses and **160** re-ask responses contained only a valid `{"code": ...}` payload, not item text. The inspected aggregate JSON files did not contain question/answer string fields. The standalone fallback is an exact inlining of the same no-text page/export. All **15** fallback PNGs were OCR-inspected locally, including an explicitly CPU-only pass; the high-risk marking-slip, reveal/practice, probability and stress views were also visually inspected. The marking-slip arithmetic is explicitly labelled as the team's own illustrative question, not the hidden Eedi item.

**No critical Eedi question/answer/distractor redistribution finding was identified.** This is a bounded finding about this revision, not a legal clearance or exhaustive equality comparison against the unavailable source corpus. No data was fetched and no `--local-text` mode was enabled. `components/bugs/school_math.py:EEDI_LINKS` still contains literal Kaggle label names, including names the thought node already flags as Kaggle-only. Those are not question/answer/distractor strings, but they remain a separate release-licensing issue; use identifiers and own descriptions or independently licensed graph wording before distribution.

The mechanical markup scan returned two styling advisories, not additional release defects: the exercise-book grid is intentional product-specific design, and the "single font" finding misread the system-font hierarchy. I would not dilute the functional and evidential issues above with those false positives.

## D. Verdict

**6/10 for "would this win the room".** I believe the code runs, the seal is genuine, the main arithmetic is traceable, and the team is unusually honest about GPT-5.5's strength. The deterministic certificate and adversarial competing-rule reveal can earn attention; the tiny real-data saving and synthetic learning evidence do not yet establish a winning advantage over a well-instrumented GPT-5.5 tutor. The broken drag and, more importantly, forgetting the very answer that changed the diagnosis make the product feel like a convincing two-turn vignette rather than a tutor. **The single highest-impact change is a stateful falsification climax:** let the judge disprove the initial rule, retain that revision, and generate a genuinely new third question from it. The `(-2)^2 = -4` branch already supplies the compelling first two beats; fixing finding 1 would make the final beat real.

Only this review is supplied by this reviewer. The project lead owns the acceptance decisions and `reviews/ledger.tsv` entry.
