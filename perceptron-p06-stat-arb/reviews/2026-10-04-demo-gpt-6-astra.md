> ⚠️ DEGRADED: single-context (one named demo reviewer; no additional UX assessors were spawned).

# P6 finals demo review - GPT-6 Astra

**Reviewed:** 2026-10-04, 18:40-19:00 IST, as an Optiver judge and statistics professor watching the three-minute presentation. Repository revision `0e2c81f2ae1ea2608160006853a403a0cbf22dff`; latest demo commit `d170f52`. Paths below are relative to `perceptron-p06-stat-arb/` unless explicitly marked repository-root.

**Verdict: a credible, unusually well-instrumented replay benchmark, but not yet a reliable three-minute finals demo.** The live calculations work. The largest avoidable failures are a race that can consume the presentation, a scripted punchline at the wrong latency, and headline labels that omit the experimental denominator.

| Dimension | Score / 5 | Judge's reason |
|---|---:|---|
| Wow / lean-in factor | 3 | Putting the judge's measured response delay into the simulator is engaging. Human-versus-microseconds alone is unsurprising; the interesting result is selection versus acting indiscriminately. |
| Clarity in three minutes | 2 | A valid race took 95 seconds in a 50-second slot. The main result, race and scientific qualifications occupy different scroll positions. |
| Honesty and rigour | 3 | Excellent asset provenance, real quotes, visible simulated-surplus language, and an explicit fragile-LEV result. Scenario aggregation, prior looks, physical latency and lifetime-bound claims still need correction. |
| Robustness on the finals laptop | 3 | Fast first visual, successful smoke checks and a genuinely self-contained fallback. Runtime backend loss leaves a false LIVE badge; race duration is not stage-safe. |
| Fit to Problem 6 | 5 | Detection, decay and a latency-budget comparison directly address the brief. The official starter resources explicitly permit the same asset across crypto venues; BTC-only is not a scope violation. Live paper trading remains correctly identified as unfinished. |

## What I actually exercised

I fetched and rebased before reading, created the requested Python 3.11 venv from `requirements.lock`, and ran:

```bash
cd perceptron-p06-stat-arb
uv venv .venv --python 3.11
uv pip install --python .venv/bin/python -r requirements.lock
bash demo/smoke.sh
PORT=8799 bash demo/run.sh --no-browser
```

The first smoke attempt correctly reported the missing venv; after setup, **18/18 checks passed**. The smoke reported 118.3 seconds overall on this shared machine, HTML available 3.4 seconds after its backend launch, and compiled/timed readiness at 19.1 seconds. Its ten live configurations matched exported totals to at most `4.3e-14` USD, with zero outcome mismatches and at most half-cent per-opportunity export rounding. Compiled LEV matched sklearn exactly in that check.

I used the browser at **1440 x 1000** for the live flow: play at 1x, slow to 0.1x, move the latency knob through 0.01/1/5/20 ms, complete two five-trial races, switch strict/frozen and both fees, rescore existing trials, and stop the backend to exercise failure handling. Browser-driven key presses are **automation, not measurements of a human participant**. The second race deliberately included a false start and one timeout.

I also measured the actual first populated browser visual, not just an HTTP response. A second `demo/run.sh` launch used new, isolated `PYTHONPYCACHEPREFIX` and `NUMBA_CACHE_DIR` directories inside this venv to exercise cold compilation without deleting shared caches. From the timestamp immediately before launch to populated policy rows and rendered canvases was **7.12 seconds**, with the backend visibly warming. It subsequently became LIVE. This was a cold-cache run of the prepared worktree, not a second network clone; the exact cold LIVE-transition time was not instrumented.

The standalone HTML opened successfully through `file://` with its backend requests blocked; its latency, fee and strict controls updated without a server. Its contents exactly matched the current HTML/CSS/data/JS inlining recipe, checked without rebuilding it. I inspected the committed race-result screenshot and MP4 frames at 0, 10 and 20 seconds. `ffprobe` reported H.264, 1280 x 888, 5 fps, 21 seconds, with no audio stream. `demo/fallback/README.md:12` discloses that the recorded race was automated.

The deterministic static UI detector returned no findings; that does not validate the statistical wording or the interaction state machine. No training, raw-data rebuild or asset rebuild was run. Both review servers were stopped, and the review browser tabs were closed.

**UNVERIFIED:** independent reproduction from the original full raw Tardis days, real fills/order latency, human reaction-time calibration, an actual projector/audience rehearsal, and a complete five-trial run starting in standalone mode. Live races and an offline rescore were exercised; these are not substitutes for claiming that last test was run.

## PLAYBOOK section 11, item by item

| Bar | Assessment | Evidence |
|---|---|---|
| 1. One command, offline after setup, CPU-only, first visual within 60 s | **Pass in the measured environment.** | Required launcher worked on port 8799; the cold-cache populated visual took 7.12 s. Setup and the offline branch are documented in `demo/run.sh:4-18` and `demo/SCRIPT.md:3-17`. |
| 2. Core claim live on real data, baseline beside it | **Pass, with a scope qualification.** | The window's naive/threshold/LEV results recompute live; the full-day column is an exported grid, not a live full-day rerun. The detector itself ran in batch. Both are supported by `demo/app.js:117-127,145-175`, `demo/live.py:127-143` and the opening honesty strip. |
| 3. A striking capability with a judge-controlled knob | **Pass as a capability; not stage-safe yet.** | Knob, fees, strict fills and the reaction-time 2x2 all responded. The race's time budget fails under valid interaction: P6-D01. |
| 4. Every number traceable; no unsupported claims | **Partial. Numerical provenance is strong; interpretation is not fully clean.** | Seven asset hashes and fourteen source blobs passed smoke; evidence-card payloads matched committed JSON. P6-D02 through P6-D07 and P6-D09/D10 identify misleading scope, state or wording. |
| 5. Three-minute script and recorded fallback | **Artifacts pass; reviewer-proof talk track does not.** | `demo/SCRIPT.md` and standalone/screenshots/MP4 exist and were inspected. P6-D01/D02 break the advertised live sequence. The script's spoken cells contain approximately 445 whitespace-delimited words, before interruptions. |
| 6. Headless smoke asserts key outputs | **Pass.** | `demo/smoke.py:58-102,121-190` checks assets, aggregate reproduction, live/grid agreement, compiled predictions and a race API result. It does not test browser race duration, the scripted state sequence or backend-loss UI. |
| 7. Recorded independent model-family judge review | **This file supplies the requested review.** | Disposition and the `reviews/ledger.tsv` entry remain the lead's responsibility; the assignment permits this reviewer to edit only this file. |

The brief check is against repository-root `_briefs/perceptron.txt:117-130`, not an invented requirement for multiple underlying assets or an already deployed trading system.

## Honesty audit: what earns credit

The opening strip explicitly says recorded quotes, simulated basis-adjusted surplus, pre-positioned inventory, and **not earned P&L / not a live trading system** (`demo/app.js:60-64`). This is materially better than a trading-looking animation with a disclaimer hidden in the README.

Frozen and strict semantics appear beside the control, including refitting on strict training labels (`demo/app.js:134-139`). LEV's row is hatched immediately outside 1-20 ms, with a nearby explanation; the frontier marks the three training latencies and dashes extrapolation (`demo/app.js:153-164,199-213`). The publication-cadence qualification is next to the decay clocks (`demo/index.html:33-35`). The evidence card explicitly reports the collision sensitivity crossing zero instead of claiming a validated LEV edge.

I verified equality between the bundle's headline, frozen/strict/markout comparisons, collision-dropped comparison, committed timing, cadence and feed figures and their source JSON files. The builder copies them through `demo/build_assets.py:252-277`. The smoke also reproduced the **six-cell sums**, rather than merely matching hand-entered labels.

The chosen window is **not representative of every sign in the day totals**:

| Frozen, 1 bp/leg | Window naive | Window threshold | Full-day naive | Full-day threshold |
|---|---:|---:|---:|---:|
| 1 ms one-way | -$4.97 | +$25.36 | +$180.30 | +$661.62 |
| 5 ms one-way | -$92.51 | -$5.17 | -$650.40 | +$248.79 |
| 20 ms one-way | -$114.27 | +$1.22 | -$1,915.04 | +$45.95 |

These are actual live/grid values, not projected profits. The full-day column makes the difference inspectable. The densest-window rule is implemented without a P&L term (`demo/build_assets.py:222-231`), and the opening position is the busiest 30 seconds by candidate count (`demo/app.js:501-505`). **I found no code evidence of selecting the window by selector profit.** A deterministic rule introduced after prior inspection is not proof that the overall demonstration is an untouched holdout, however; do not turn "chosen by this count rule" into a stronger anti-selection claim.

Race mechanics largely match the disclosed rule: 1x was set on start; a separate play probe advanced 2,534 ms of replay in 2,537 ms of wall time. Slow mode advanced 250 ms in 2,503 ms. Five distinct opportunities were reported in each completed race; the false start remained listed and the timeout counted as 2,000 ms. The live 2x2 used the median recorded RT, exact live simulation at that RT, a nearest-grid training threshold, and the live measured machine delay (`demo/app.js:359-469`, `demo/live.py:144-168`). Its dollar totals are a **whole-window counterfactual using that response delay**, not the sum of the five trials.

## Numbered findings

### P6-D01 - major - The five-trial race can consume the finals presentation

**Evidence:** `demo/app.js:366-405`; `demo/SCRIPT.md:26`.

The script allocates 50 seconds, including explanation and interpretation. My first automated race took **44.344 s**. The second took **95.087 s**, with a deliberately false start, one legitimate timeout and four approximately 300 ms responses. Its five waits remaining when each trial was observed armed were **14.485, 4.671, 17.802, 27.379 and 19.374 s**: **83.710 s of waiting alone**. The overrun is not explained away by the false start or slow key press.

**Reproduction:** start five trials and follow the rule; in the longer run the opportunity IDs were `45320, 44501, 41451, 43271, 43445`. `armTrial` starts at a random time, then accepts the first eligible episode up to another 30 seconds after its random 1.5-4 s delay. There is no cancel control. Randomly chosen gaps change subsequent runs, but the source and this completed run establish the failure.

**Fix:** choose an eligible episode by a disclosed, outcome-independent rule first, then start its 1x lead-in 1.5-4 s before it. Keep every completed trial/false start/timeout visible. Add cancel and a presenter deadline; do not secretly accelerate replay or discard slow responses. Rehearse against a wall-clock limit, not merely five successful API calls.

### P6-D02 - major - Following the script makes the "$25 at 1 ms" punchline false

**Evidence:** `demo/SCRIPT.md:25-27`; `demo/app.js:359-365,413-420`; `demo/live.py:144-168`.

**Reproduction:** sweep 10 microseconds -> 1 -> 5 -> **20 ms**, exactly as instructed, then press Start 5 trials. Starting a race resets speed, **not latency**. My first completed race was consequently at 20 ms: the machine's threshold result was **+$1.22**, not the script's **+$25** at 1 ms. The subsequent strict toggle produced **$0 and zero selected trades** in that window. Resetting to 1 ms restored the frozen +$25.36 result.

The UI is correctly computing the chosen configuration; the presenter is being told to narrate a different one.

**Fix:** explicitly reset to 1 ms before the race, ideally through a named race setup action that snapshots and displays its fee/simulator/latency. Alternatively make the spoken punchline conditional on the current configuration. Also say the 5 ms threshold loses $5.17 **in this window** while remaining positive over the day; do not point at the red window cell while implying it is green.

### P6-D03 - major - The largest "$/day" headlines hide a six-scenario denominator

**Evidence:** `demo/app.js:479-480`; `demo/SCRIPT.md:27,37-39`; `eval/results/falsification_walkforward_12d_prereg.md:3`; `eval/results/sensitivity_amendment1.md:5`; `eval/PREREGISTRATION-walkforward-12d.md:27-28`.

The cards say **+$2,898/day**, **+$6,544/day**, and **+$299/day**. Those are means of day scores that **sum six counterfactual fee/latency scenarios**: two fees times three latencies. They are not a policy's single-config daily surplus. The nearby full-day column, by contrast, is one current configuration. "Simulated" does not repair this denominator mismatch.

**Fix:** label these as "mean day-level uplift, summed over 6 fee/latency scenarios" at the number and in the talk track. Keep the single-config day column clearly distinct. If showing a per-scenario mean instead, divide the estimate and its interval consistently and explain that averaging; do not silently change the preregistered statistic.

### P6-D04 - major - A dead backend leaves the page claiming LIVE computation

**Evidence:** `demo/app.js:95-115,119-123,169-175,350-357`.

**Reproduction:** let the badge become LIVE, stop this demo's backend, then change delta from 1 to 5 ms. After five seconds I observed all of:

- the green **LIVE** badge still saying **"committed code recomputing on this machine"**;
- **"waiting for live recompute..."** beside counters now supplied by the exported grid;
- the race status correctly saying **"offline: exported grid (RT snapped)"**;
- the race rule still describing the previous **10.9 microsecond live p50**.

`pollStatus` stops after readiness. `refreshLive` catches a failed request without clearing live state or updating provenance. This is a reproducible presentation-integrity bug, not an incorrect simulator calculation.

**Fix:** handle failed/timed-out recomputations by atomically changing the mode, counter source and timing provenance. Show an explicit offline/stale notice, clear stale "measured now" language, and retry readiness at a low frequency. Add a browser regression that stops the backend after readiness and checks every source label.

### P6-D05 - major - The demo drops the already-established prior-look disclosure

**Evidence:** `demo/app.js:479-480`; `demo/SCRIPT.md:23,27,38`; `eval/PREREGISTRATION-walkforward-12d.md:25-26,43-48`; `deliverables/round1-abstract.md:41-42`.

The audience hears "pre-registered 12-month walk-forward" without being told that these are **12 first-of-month test days, five previously inspected**. The final abstract does disclose this and gives the untouched-seven subset: 7/7 positive, +$343 with t-interval [+$70, +$616], using the same six-scenario score.

This does **not** invalidate the recorded pass of the numerical decision rule. It does make the demo's description less candid than the underlying submission.

**Fix:** put "12 sampled days across months; 5 previously inspected" directly on the evidence card and show the unseen-seven result alongside it. Call October 1 held out from fitting, not a newly blind confirmation.

### P6-D06 - major - "Bounded to 11.3-147.1 ms" overstates what the quotes establish

**Evidence:** `demo/app.js:481`; `demo/SCRIPT.md:40`; `eval/decay_report.py:72-103`; `deliverables/round1-abstract.md:30`.

The demo reinstates **"bounded to 11.3-147.1 ms by publication times."** The code perturbs observed episode endpoints to previous publications and fits curves to those endpoints. That does not establish uninterrupted executable opportunity lifetimes between sparse publications: unobserved close/reopen events and unavailable executable state remain possible.

The corrected abstract already calls this an **illustrative sensitivity range, not a bound on executable lifetime**. The published numeric endpoints can remain; the stronger interpretation cannot.

**Fix:** reuse the abstract's wording on the card and in the judge Q&A. Keep the shaded cadence region, but describe it as a publication-resolution warning, not an assurance that the true tradable lifetime lies within a certified interval.

### P6-D07 - major - Uncalibrated timestamp differences are sold as geographic latency floors

**Evidence:** `demo/app.js:65-76,482`; `eval/results/live_latency.md:3,13,21-30`.

The preset says **"this laptop (India) -> OKX, p05 ... measured"** and the evidence card calls 24-107 ms **"floors."** The source measures **local receive timestamp minus venue timestamp**, explicitly including clock offset. Its SNTP records include uncertainties of approximately 170, 320 and 554 ms, larger than the advertised lower endpoints. The arrow also labels the opposite direction from the received-feed measurement.

I verified that the displayed numbers trace to the committed JSON. What is unverified is the claimed physical interpretation; a fifth percentile is not a proven network lower bound.

**Fix:** label these "recorded receive-minus-venue timestamp p05; clock offsets unresolved." Remove the physical floor claim and misleading direction arrow. Keep hypothetical symmetric order latency as an explicitly separate simulator assumption. Show when a preset is snapped to the nearest available delta.

### P6-D08 - major - The stage layout separates the claim from the qualifications it needs

**Evidence:** `demo/index.html:20-87`; `demo/style.css:16-19,57-73`; `demo/SCRIPT.md:19,27`.

**Reproduction:** at the prescribed 1440-pixel width and a 1000-pixel-high viewport, on the initial page the race starts at **y = 1172 px**, evidence at **y = 1429 px**, and the frontier's explanatory note at **y = 1100 px**. The page is about 1762 px tall before trial rows. A full-page screenshot can show everything; a judge's viewport cannot.

The strict button lives near the top, while the "robust" and fragile-LEV cards the presenter is told to point at are below the fold. The layout is a useful exploration dashboard, not yet a controlled three-minute presentation. This is observed geometry; readability on the actual projector is UNVERIFIED.

**Fix:** add a compact stage view with explicit replay/race/evidence steps. In each step retain a short simulation/configuration/source strip. Put the strict comparison and its scenario denominator beside the changing counters; place the race result next to the stimulus instead of requiring a distant scroll. Increase emphasis on one signed comparison rather than shrinking all explanatory text.

### P6-D09 - minor - The frontier's unconditional abstention caption is false for full-day cells

**Evidence:** `demo/app.js:185,214-218,231-232`; `demo/assets/data.js` entries named below.

The caption always says **"the threshold re-tuned at human speed trades nothing."** That is true for this window's exported human grid, not universally for the **full-day** frontier it describes.

**Reproduction:** inspect `grid_day["frozen|f1|d5|D100000"].thr`: it contains **3 trades**, zero both-leg fills and **-$0.30629023151800006**. Across the exported human configurations, 54 full-day cells have nonzero threshold trade counts; none of the corresponding window cells do. At fee 2 the human band is not drawn at all, but its descriptive sentence remains.

**Fix:** derive the caption from the relevant full-day cells, distinguish "near zero" from "no trades," and remove the band explanation when the band is absent. Make the race's fixed 1 bp fee conspicuous when other panels are at 2 bp; its existing summary discloses that fee but the global-looking control does not change it.

### P6-D10 - minor - The offline ratio names 6.08 microseconds but divides by 7

**Evidence:** `demo/app.js:420,459-465`; `eval/results/decision_timing.md:7`.

**Reproduction:** after the second race, stop the backend and rescore. With recorded median RT **328.900000... ms**, the offline summary said **46,986x** the machine's decision step and identified **6.08 microseconds committed p50** in its parenthesis. The multiplier is actually RT divided by the **7 microsecond simulator allowance**, as the code shows. The parenthesis later mentions that allowance, but does not clearly assign it to the ratio.

Both input numbers are legitimate, different quantities. The live path correctly uses its measured p50; the offline presentation conflates the timing comparison and simulation parameter.

**Fix:** either compute the ratio against the named committed p50 while separately retaining 7 microseconds for simulated outcomes, or explicitly call it "times the 7 microsecond compute allowance." Display the snapped human delay used for offline outcomes separately from the measured median.

## Five changes most likely to improve the judges' reaction

These are implementation-effort estimates, not measured completion times. None requires training or new data.

| Priority | Change | Estimated effort | Why it changes the reaction |
|---|---|---|---|
| 1 | Bound the race lead-in by selecting the episode first; preserve 1x, all results and timeouts; add cancel/deadline. | 60-90 min | Removes the 95-second dead-air failure without cheating the experiment. Addresses P6-D01. |
| 2 | Add a named, visible race setup at frozen/1 bp/1 ms and revise the script to use current values and explicitly distinguish window/day. | 30-60 min | Restores the demonstrated +$25.36 punchline instead of saying it over +$1.22 or $0. Addresses P6-D02. |
| 3 | One focused evidence-copy pass: six-scenario denominator, sampled/prior-inspected days, sensitivity-not-bound wording, uncalibrated feed labels, conditional abstention and correct offline timing labels. Mirror it in SCRIPT and fallback. | 60-100 min | Prevents easy professor/Optiver challenges to otherwise traceable numbers. Addresses P6-D03/D05-D07/D09-D10. Put the existing automated-recording disclosure on the recorded media too. |
| 4 | Make live/offline/error state consistent across the badge, counters and race; add a bounded request timeout and one backend-loss browser check. | 60-90 min | A local failure becomes an honest continuation, rather than a false LIVE claim. Addresses P6-D04. |
| 5 | Add a compact three-step stage view with persistent scope labels and the relevant baseline/result/caveat visible together; retain the full dashboard for Q&A. | 90-115 min | Gives the judge one comparison to understand at each moment instead of a scrolling control room. Addresses P6-D08. |

Do not spend the next two hours making the pentagon prettier or training a larger learner. The most persuasive ending is already present in the evidence: **selection helps this replay benchmark; public quote resolution and execution assumptions limit what can honestly be claimed.**

## Re-review (f953719)

**Checked:** 2026-10-04, `6e2a7df` (demo identical to `f953719`), same single-reviewer method. One warm `PORT=8799 bash demo/run.sh --no-browser` run at **1440 x 900**, using automated, not human, reactions. Three steps, controls, race, backend loss and offline rescore exercised. No training/assets rebuilt; standalone inlining matched; static scan clean; own server/tab stopped.

**Not independently repeated:** the lead-reported fresh-clone **28/28 smoke** and **0.3 s visual / 3.4 s LIVE** timings. Projector legibility and an oral three-minute rehearsal remain **UNVERIFIED**.

**Result: nine FIXED, one PARTLY.** Citations below refer to the re-reviewed revision, not the original review's line numbers.

| Finding | Verdict | Evidence |
|---|---|---|
| P6-D01 | **FIXED** | Five trials plus a false start and one timeout finished in **26.20 s**, all six rows retained. A separate Stop kept one completed trial and logged the abandoned next trial; the source caps the race at 45 s (`demo/app.js:36,441-496`). |
| P6-D02 | **FIXED** | Starting from strict / 2 bp / 20 ms / 0.1x reset to frozen / 1 bp / 1 ms / 1x and produced **+$25.36** for the machine selector; restore-setup also worked (`demo/app.js:425-440,546-556`). |
| P6-D03 | **FIXED** | Visible headline copy names the **six-scenario sum** and separates it from the one-setup day column; the revised narration does likewise (`demo/app.js:234-235,619-622`; `demo/SCRIPT.md:34,41`). |
| P6-D04 | **PARTLY** | Heartbeat correctly changed the badge/counters to OFFLINE, but the completed race retained its live-computation claims until I changed latency. Reproduction and regression-test gap below (`demo/app.js:150-154,197,558-562`). |
| P6-D05 | **FIXED** | Cards display **12 sampled first-of-month days, five previously inspected**, plus the unseen-seven **+$343 [+$70, +$616]** result; the talk track discloses prior inspection (`demo/app.js:619-622`; `demo/SCRIPT.md:38,41,45`). |
| P6-D06 | **FIXED** | Card and script now say **illustrative sensitivity range, not a bound on executable lifetime** (`demo/app.js:625`; `demo/SCRIPT.md:68`). |
| P6-D07 | **FIXED** | Dashboard presets identify receive-minus-venue p05, unresolved clock offset and snapped delta; the card explicitly rejects a latency bound and separates the order-delay assumption (`demo/app.js:82-93,628`). |
| P6-D08 | **FIXED** | All three steps fit **1440 x 900** without scrolling: lowest panels in steps 1/2 ended at y=854; step 3's footer ended at y=785. Replay/result coexist; arrow-key navigation worked (`demo/app.js:642-658`; `demo/style.css:90-114`). |
| P6-D09 | **FIXED** | At frozen / 1 bp / 5 ms the full-day caption correctly says **at most three trades**, largest absolute surplus **$0.31**; switching to 2 bp removed the human-band caption (`demo/app.js:291-298`). |
| P6-D10 | **FIXED** | Offline rescore of **311.3 ms** displayed **51,173x**, exactly using the committed 6.083333... microsecond p50; the text separately named the 7 microsecond simulation allowance and 300 ms RT grid (`demo/app.js:497-506,586-594`). |

### Remaining P6-D04 - major - Passive backend loss leaves the completed race stale

**Reproduction:** complete a LIVE race, stop the backend, **touch nothing**. Badge/scope said OFFLINE/grid, but race status still said **"live · 19:59:28"**, the machine row **"live p50 measured on this machine"**, and the summary **"Live: committed simulator at your exact RT."** The rule had switched to the 7 microsecond allowance. Changing delta repaired the race labels.

`backendLost` clears window results/timing, not `race.result`; `renderAll` omits the 2x2. The new test **changes delta before checking those labels** (`demo/browser_check.py:120-138`), missing this case.

**Fix:** rescore on loss, or consistently label the retained last-LIVE snapshot and its original parameters. Assert all source labels **before** changing delta.

### P6-D11 - major - The rewritten talk track is over its speaking-time budget

The timed "say" cells contain **581 whitespace-delimited words**, versus approximately 445 previously (`demo/SCRIPT.md:38-46`). After the 25-second silent race, 155 seconds remain: **225 words/minute**. The rule alone is **64 words in 10 seconds** (384 words/minute). At 180 words/minute, speech plus race takes **3:39**, before clicks/questions. This is budget arithmetic, not an oral rehearsal.

**Fix:** cut to roughly 330-350 spoken words, retain the corrected on-screen disclosures, move detailed comparisons to Q&A, and give Stop an explicit talk-time cue.

| Dimension | Re-score / 5 | Reason |
|---|---:|---|
| Wow / lean-in factor | **4** | Bounded participation and adjacent counterfactuals make the interaction land. |
| Clarity in three minutes | **3** | Clearer stage sequence, but the spoken script remains over budget. |
| Honesty and rigour | **4** | Scientific scope/disclosures corrected; passive-loss race provenance remains inconsistent. |
| Robustness on the finals laptop | **4** | Bounded race, working Stop, heartbeat and offline rescore; D04 still needs closure. |
| Fit to Problem 6 | **5** | Detection, decay and latency-aware selection remain directly on brief. |

**Verdict: substantially stronger and scientifically clearer, but not yet three-minute finals-ready until the script is cut and passive-loss race provenance is fixed.**
