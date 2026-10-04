# P4 live-demo review - GPT-6 Astra

**Verdict: NOT FINALS-READY at the reviewed revision.** The empirical result is strong enough to make an Optiver judge lean in. The live interface can, however, display another day's results with five green honesty checks, and repeated redraws break the Retina layout. These are demonstrated blockers, not aesthetic preferences. Preserve the experiment; repair the demonstration.

**Reviewer:** independent GPT-6 Astra, acting as an Optiver market maker and IIT Bombay professor. Single-context review; no sub-agents, author-code changes or additional sessions. Review record dated **2026-10-04 22:25:32 IST**, using `TZ=Asia/Kolkata date`.

**Scope:** `demo/` at core commit `dbc0c68041c136d92121e51c70d47d6137ceb796`, unchanged in review checkout `eadf2e48a0007ed5cb58551aad2e812c2d32c174`. At the initial check, **22:07:44 IST**, remote `main` was `49c9472afb161dd5ea34bcb286e951a0c75b19a9` and had the same four-section demo. **Section 5 / SEMI-SYNTHETIC splice was absent and was NOT REVIEWED**, including any version added subsequently. All paths below are relative to `perceptron-p04-lob-regimes/`, except the repository-root `PLAYBOOK.md`.

## Scores

| Criterion | Score / 5 | Judge's reason |
|---|---:|---|
| Wow factor | 4 | Turning alpha down to `1e-30` and still seeing 26 alarms on the calm day is striking, reproducible and relevant. |
| Honesty | 3 | Excellent committed evidence and an explicit failed H1; wrong-day checks, incomplete protocol disclosures and an overbroad closing claim undermine it. |
| Clarity | 2 | This is a dense research dashboard, not yet a controlled three-minute presentation. |
| Robustness | 2 | Fast initial serving, useful fallbacks and passing numerical smoke; broken Retina redraws, asynchronous identity and error recovery. |
| Real-data-first | 5 | Opens with real held-out results, then real replay; the development day is explicitly illustrative. No simulation is substituted. |
| Knob quality | 3 | Twenty genuine computed settings alter alarms and loss. Stale state and separation from the replay weaken the experience. |
| **Total** | **19 / 30** | **Strong experiment; do not approve the current live surface for finals.** |

## What I actually ran and watched

I read `PLAYBOOK.md` section 11; all requested demo source, documentation and result files; all five named evaluation result documents; `eval/PREREGISTRATION.md`, including both amendments; and `deliverables/qa-prep.md`. I traced the relevant ingest, detector, context, adapter and execution-export code. I viewed **all 11 committed fallback PNGs**.

The lead's supplied `.data` was symlinked read-only in use. All 16 raw files and their existing ingest caches were present; no data or package downloads occurred. The demo replay cache started absent. Commands ran under `nice -n 10`, with `WORKERS=1`, after checking memory level was at least 30. An external monitor could pause the owned process group below 25; the sampled minimum during the build was 28, so no such pause was needed. Only one owned heavy job ran at a time.

| Observation | Measured result |
|---|---|
| `demo/run.sh --no-open` launch | Started **22:10:20 IST**, with memory level 41; served on loopback port 62010. |
| First visual, requested curl criterion | Correct `/index.html`, HTTP success and expected title, in **2.518 s**. This satisfies the 60-second first-visual bar with data/dependencies available. |
| First locally computed replay | Development day ready at **169.732 s**. |
| Remaining days ready | Calm: **274.312 s**; lower median: **362.636 s**; most volatile: **469.235 s**. |
| Complete cold replay cache | **469.236 s**, with one worker. This is not a measurement of the documented three-worker runtime. |
| `demo/smoke.sh`, after that build | **PASS**, exit 0, **5.023 s** external wall time; 81 successful check/GET output lines. Warm replay cache, not a second cold build. |
| Browser checks | Chromium: **28 sequential day/knob combinations** and **20 policy/delay/fee combinations** agreed with their data and rendered values. Separate adverse-state tests found D1, D2 and D6. |
| Shutdown | Owned demo server PID 58566 stopped explicitly; port 62010 no longer responded at **22:25:01 IST**. The collision-test server was also stopped by PID. |

Live screenshots covered all four replay days, the extreme-alpha, calibrated and off states, and the fee control. Normal browser resource requests were loopback-only. The bundled read-only UI detector returned `[]`; that did **not** detect the runtime defects below.

The true no-data download path and missing-dependency installation path were **not executed**, respecting the no-download instruction. Their ordering and failure handling were inspected. Raw-data/ingest caches were warm; only `demo/.cache` was cold. I did not rerun the entire 22-day sweep. The smoke assertions, committed aggregate inspection, code trace and fresh four-day replay are the evidence here. The supplied symlink and this review's generated replay cache were removed afterward; tracked source stayed unchanged.

### Observable replay behaviour

These are per-day alarm counts, not inferred false-alarm counts. The calibrated column is `q=0.999`.

| Replay day | Role | `1e-3` | `1e-30` | Calibrated | Off |
|---|---|---:|---:|---:|---:|
| 2024-05-01 | Development/FOMC, illustrative | 48 | 47 | 6 | 0 |
| 2026-08-01 | Held-out, calmest | 48 | 26 | 0 | 0 |
| 2026-10-01 | Held-out, lower median | 48 | 37 | 4 | 0 |
| 2026-03-01 | Held-out, most volatile | 48 | 48 | 3 | 0 |

The day-selection rule matches the committed volatility ordering. On the calm day, changing `1e-3` to `1e-30` changes KS-refit loss from **0.593946 to 0.708569**, while the gate remains **0.525500**. Off gives **0.548189**, identical to the single EWMA head. These are real policy changes, not a cosmetic slider. All five displayed policies and all 20 stops on each of the three fresh held-out replays passed the backend match checks.

## Scientific and numerical audit

**The main numbers hold.** KS-refit is `+0.0268` versus static and worse on 21/22 days. The regime gate is `-0.0099`, CI `[-0.0136, -0.0068]`, better on 22/22. H1 is correctly called unsupported; H2 is supported. The gate-plus-shrinkage revision adds **+0.0006** loss versus the gate, not an average improvement. The head-only and usage panels agree with their post-hoc sources: low/mid/high usage **20.7/33.2/46.0%**, and head-only pooled losses are worse. The high-volatility head nevertheless beats the gate on **one** day; "every head alone is worse" must mean the pooled comparison, not every day.

**The literal finite-dial claim holds.** In `demo/results/alarm_dial_sweep.json`, all **20** stops have positive mean loss differences and positive lower 97.5% CI endpoints versus the gate, with **0/22 days better at every stop**. The best pooled gap is **+0.008345788**, CI approximately `[+0.005953, +0.011680]`, attained by off and also by the zero-alarm naive settings from `1e-150` downward. The headline is valid for this finite, post-hoc menu; it is not a theorem about every alpha or retraining algorithm.

**The training-day inset agrees with the committed construction.** There are **34,080** leave-one-training-day-out windows; rejection shares are **99.3985%** at `1e-3` and **33.0839%** at `1e-30`; median log10 Bonferroni p is **-22.892575**. The code uses 600-second windows, subsamples every 10 seconds and checks overlapping windows every 30 seconds. Calling these simply "1-second windows" is imprecise. More importantly, heterogeneous training days are an empirical reference population, not verified samples from a no-shift null.

**The separation calculation is correct, but is not the observed mechanism.** Independently computing `log10(2 / C(m+n,m))` using an integer binomial coefficient gives **-218.5463717691424** for `m=60`, `n=102959`, agreeing with the displayed `10^-218.5`. This is the continuous/exchangeable, per-feature two-sample complete-separation calculation for the held-out reference size, not SciPy's returned p-value or a calibrated seven-feature daily alarm probability. SciPy's effective-one-sample asymptotic calculation returns **0 at D=1**. Crucially, the sweep records **zero D=1 windows and zero zero-p windows among 62,480 held-out windows**, and none in the training inset. An observed floating-point-underflow explanation would be false.

**The taker ending is correct for the stated experiment.** For the gate, gross is **+0.297406 bps** per signal. At 100 ms, taker before fees is **+0.263927**, break-even fee per side **0.131963**, and VIP 9 taker net **-3.136073**. All 20 displayed policy/delay/tier combinations have negative taker net; exported fee arithmetic and browser values match. The VIP 9 maker number, approximately **+0.289064**, is explicitly an optimistic two-passive-fill upper bound. This supports "not tradable as a taker after fees" for this signal/hold rule, not a profitability claim for market making, a capacity estimate or a proof about every trading rule.

## Findings

### D1 - BLOCKER: a day switch can attach the wrong market day to green honesty checks

**File/quote:** `demo/index.html:166-168`: `if(RP[DAY]){drawReplay();return;}` and `RP[DAY]=await r.json()`.

Two browser reproductions:

- Ordinary cached navigation: select calm day at `1e-30`, then the already-loaded development day. The replay correctly shows **47** alarms, but the dial still says **26 alarms on 2026-08-01**.
- Delay only the calm-day replay response by 500 ms, select calm, immediately return to development. After the response, `DAY` is `2024-05-01` but `RP[DAY].day` is `2026-08-01`. The development tab displays the calm day's **0.525500** gate loss with **five green match checks**.

The values themselves are authentic; their displayed identity is not. A professor can invalidate the live verification column with two clicks.

**Concrete fix:** capture the requested day before either await; store the response under that captured key; validate the payload's day; render only for the currently selected day. Redraw both replay and dial on cached selection. Add browser assertions for cached switching and delayed out-of-order responses, including displayed day, payload day and reference day, not just equal floating-point values.

### D2 - BLOCKER: Retina redraws repeatedly multiply canvas height

**File/quote:** `demo/index.html:124-125`: `h=+cv.getAttribute("height")`, followed by `cv.height=h*r`.

The function reads its previous device-pixel backing height as the next logical height. In a fresh Chromium context at device-pixel ratio 2, the replay began at **620 CSS pixels**, then reached **2480** at `1e-30` and **4960** at off, with an intervening replay-load redraw. The page grew from **3008 to 9595 pixels**. The sweep and explanatory charts grow too. DPR 1 testing conceals this.

**Concrete fix:** preserve an immutable logical height independently of the canvas backing dimensions; derive backing dimensions from that logical size and DPR on every draw. Add a DPR-2 test that changes controls repeatedly and resizes the viewport while asserting constant logical heights and usable charts.

### D3 - MAJOR: the visible provenance and target disclosures are incomplete

**Files/quotes:** `demo/build_scoreboard.py:71` assigns the whole execution export `"status": PRE2`; `demo/index.html:100,314` always shows `"pre-registered secondary"`. `demo/SCRIPT.md:11` says the test was run once on "22 held-out days."

Selecting **One EWMA head** leaves both execution chips pre-registered even though that policy/result comes from the post-hoc ablation. Gate-plus-shrinkage likewise loses its post-dev policy provenance there. Keeping a pre-registered *metric* label is defensible only if the selected *policy/result* status is also visible.

Neither the page nor the script surfaces Amendment 2's prior exposure of **2025-08-01**. The page also omits that forecast loss estimates **P(up | non-zero 10-second move)**, excluding ties, while the edge calculation includes all signals. The chosen calm day has a **0.680 tie rate** in the committed results; that distinction is material.

**Concrete fix:** propagate per-policy provenance into the execution panel; add a compact visible disclosure for the one previously evaluated day, the clean-21 sensitivity and the non-tie scoring mask. Keep the existing H1-failure and post-dev labels. Do not silently rewrite the frozen analysis. Sources: `eval/PREREGISTRATION.md` Amendment 2 and `eval/results/v2_holdout_sensitivity.md`.

### D4 - MAJOR, distribution gate: the licence check exempts fine-grained derived timelines

**Files/quotes:** `demo/smoke_check.py:92` uses `skip=("alarms", "alarm_s")`; line 102 checks list length rather than temporal resolution. `demo/build_replay.py` emits second-resolution alarm times, and the alarm-track loop in `demo/index.html` places each at its exact position. Those tracks are committed visually in `demo/fallback/08...10*.png`.

No raw quotes or sub-10-minute price/book series were found in the committed demo JSON. Prices really are 600-second OHLC, and both demo JSON files contain aggregates. The remaining issue is **market-derived event timing**, not raw prices: the calm replay's CUSUM events include a **298-second** gap. The wider committed evaluation artifacts also contain `alarm_utc` times down to **60-second** spacing (`eval/run_v2.py:104`); for example, `v2_dev_amend1.json` contains 16,120 exact alarm times.

Under the brief's strict requirement that redistributed Derived Data be aggregated at at least 10 minutes, this is **not an established clean licence pass**. Non-reconstructability and a small file/list size do not establish the required aggregation.

**Concrete fix:** publish 600-second alarm-count bins and regenerate the affected fallback images; keep finer timelines internal or obtain explicit permission. Audit published evaluation artifacts as well as `demo/`; preserve frozen research records privately rather than altering their history without disclosure. The [current Tardis terms](https://docs.tardis.dev/legal/terms-of-service), checked on 2026-10-04, also make clause 9.2 subject to 9.5's AI/distribution restrictions. This technical audit is not a legal clearance for external distribution.

### D5 - MAJOR: the explanation overshoots the demonstrated claim

**Files/quotes:** `demo/SCRIPT.md` closes with "at any sensitivity"; `demo/index.html:292` says "The i.i.d. null is the problem"; `demo/PROPOSAL.md:11` attributes the effect to underflow and says no positive alpha switches the alarm off.

The actual displayed finite-dial verdict is supported, as established above. The broader closing sentence is not. This is 20 post-hoc settings of a fixed KS/refit recipe, not all thresholds, dependence-aware detectors, refit windows or adaptation methods. Cross-day distribution changes can be real covariate shifts: excessive rejection relative to nominal alpha on heterogeneous training days is not a measured false-positive rate, nor an isolation of autocorrelation as the sole cause. The proposal's underflow account is superseded by zero observed D=1 cases and zero alarms at `1e-150`.

**Concrete fix:** say **"Across these 20 tested settings, this KS-refit recipe never beats the state gate."** Label the inset "training-day rejection rate; not a ground-truth false-alarm rate." Explain that detecting covariate change does not establish that refitting helps. Mark the proposal's underflow hypothesis as rejected/superseded; retain the correct exact-probability calculation only as a clearly separate mathematical aside.

### D6 - MAJOR: readiness and failure handling can claim success without a page

**Files/quotes:** `demo/run.sh:60-62` exits its curl loop without asserting success, then prints `"page live at"`. `demo/build_replay.py:126` regards an existing cache file as ready. `demo/index.html:166-168,318-330` suppresses replay errors and lacks a scoreboard boot-error view.

I occupied an otherwise separate port with an owned HTTP server whose `/index.html` returned 404. `run.sh` still printed **"page live"** after seven seconds and **"serving"** before exiting 1; total **10.053 s**. No competing user's server was touched.

Browser fault injection of a missing scoreboard gave an unhandled JSON error and an empty scoreboard with no visible error/fallback. A missing replay whose status said ready produced no totals and no visible error. Cache existence without content/version validation also permits stale or broken artifacts to be reused.

**Concrete fix:** verify the owned server is alive and the expected page is actually served; fail explicitly on occupied ports. Surface boot/replay failures, provide an immediately reachable fallback, and validate cache schema/day/code-and-input identity before reusing it. Keep committed panels available when optional replay computation fails. Extend smoke with real browser assertions for these states; substring presence is not frontend validation.

### D7 - MAJOR: the presentation layout makes the judge work to see cause and effect

**Files/quotes:** `demo/index.html:22` fixes `.grid2` to `1.6fr 1fr`; `#rp` is a 620-pixel canvas, while `#dial-range` lives in the next section.

At **1440x900 / DPR 1**, the scoreboard, replay and dial sections are approximately **703, 1008 and 815 pixels** high. The slider is **934 pixels below the top of the price canvas**: the price scene, control and complete sweep verdict do not fit together. At **1280x720**, page width becomes **1361 pixels**, clipping content horizontally. The low-head percentage is partially overwritten in the usage bar even in the committed scoreboard fallback. The range also has no accessible name/value explanation.

**Concrete fix:** add a compact stage layout: control and current-day alarm count beside the replay, two primary comparison traces, and the 22-day conclusion in the same view. Put the full tables, head ablations and probability derivation behind an explicit details view. Repair grid min-width/overflow and label placement; give the range an accessible name and alpha-valued text. Verify at both 1440x900 and 1280x720, including DPR 2.

### D8 - MINOR: the script and fallback order are not a rehearsed three-minute path

**Files/quotes:** `demo/SCRIPT.md:9-19` allocates 30 seconds to approximately **109 quoted spoken words**, before reading the pointed-at numbers. Line 5 says to show fallback PNGs in "numeric order," but the script's calm-day act uses **08/09**, after the fee ending **07** in that order. The three supplied "If asked" answers mostly explain day selection.

The first act alone requires roughly **218 words/minute** before gestures. The complete talk can fit three minutes if rebalanced; the current per-act budget cannot be followed naturally. The fallbacks are legible as individual panels at native size, not as the downscaled full-page image. There is no committed calibrated-state or lower-median-day fallback.

**Concrete fix:** make **26 alarms at `1e-30`** the single hero readout; move head ablations and most statistical detail to Q&A. Rehearse a 35-second scoreboard, 35-second real replay, 75-second dial, 35-second fee ending. Order the fallback deck by that story, including calibrated and off states, rather than by screenshot capture history. Carry the five answers below.

## Five hardest live questions and defensible answers

| Judge's question | Answer to give |
|---|---|
| "Is `1e-30` just SciPy underflow? Are those actually false alarms?" | No observed window has D=1 or p=0. The exact complete-separation probability is about `10^-218.5`, a different calculation. The training inset measures rejection under realistic heterogeneous days, not a verified false-alarm rate. The operational evidence is that acting on these alarms worsens forecast loss. |
| "Was the holdout unseen, and did your registered hypothesis succeed?" | One of 22 days, 2025-08-01, was previously evaluated in v1. Excluding it leaves the gate/static conclusion intact: clean-21 delta `-0.0099`, 97.5% CI `[-0.0140, -0.0067]`. Original H1 failed; H2 succeeded. Gate comparisons are secondary; shrinkage was post-dev; the dial and head-only ablations are post-hoc. |
| "Have you proved detect-and-retrain cannot work?" | No. We tested this frozen recipe at 16 naive levels, three empirical quantiles and off. All 20 lose to the gate on every evaluated day. That is unusually consistent evidence against this recipe on these days, not a theorem about all detectors or retraining designs. |
| "Is the gate just one better head, or an oracle about the future?" | All heads and thresholds are fitted on 2023; selection uses trailing volatility, not future outcomes. High-vol-only is `+0.0141` worse pooled and wins just 1/22 days; usage is 20.7/33.2/46.0%. The ablation is exploratory. Also disclose that loss forecasts direction conditional on a non-zero move; it is not unconditional up probability. |
| "What can Optiver actually trade?" | This is not a demonstrated profitable strategy. At 100 ms the gate's break-even fee is 0.132 bps/side versus VIP 9 taker fees of 1.7; net is -3.14 bps/signal. Passive +0.29 is an optimistic bound without queues or adverse selection. Quoting value remains untested; gate-plus-shrinkage reference step p99 is 85.6 microseconds and end-to-end latency is not established. |

## Top five changes with the highest demo return

1. **Make the verification column trustworthy:** fix D1's day identity and cached redraws, with the delayed-response browser test.
2. **Make the actual Mac display safe:** fix D2, then ship D7's projector-sized stage view with the knob beside its visible consequence.
3. **Close the honesty gap without weakening the result:** add D3's provenance/target/prior-exposure disclosure and D5's finite-recipe wording. The measured story is already strong enough.
4. **Make distribution demonstrably compliant with the stated aggregation rule:** resolve D4's event timelines and regenerate the public fallback images; do not equate a passing size check with licence clearance.
5. **Make failure boring and the talk rehearsable:** fix D6's readiness/error states and follow D8's reordered fallback/Q&A path. Retain the excellent numerical anchor checks and add the missing browser checks.

**Final judge reaction:** I would lean in at the genuine 26-alarm result and respect the negative after-fee ending. I would not accept a demonstration whose green checks can certify the wrong displayed day. Fix that presentation contract before adding another act.

---

## Lead response (Claude Opus 5.5, project lead) — 2026-10-04 22:35 IST
The review is advisory and the lead decides. All eight findings are **ACCEPTED**. Fixes are delegated to the demo builder, in this order: D1 → D2 → browser smoke stage → D6 → D3 → D5 → D4 → D7 → D8. Section 5 (Act 2, which this review did not cover) gets the same D1/D2/D4/D6 treatment.

| ID | Decision | Action |
|---|---|---|
| D1 | **ACCEPTED (blocker)** | Key responses by the requested day; validate payload.day; render only for the selected day; redraw both replay and dial on a cached switch. New browser smoke assertions: cached switch and an out-of-order delayed response. |
| D2 | **ACCEPTED (blocker)** | Keep the logical canvas height immutable and derive backing = logical × DPR. DPR-2 browser assertion with repeated controls and a resize. |
| D3 | **ACCEPTED** | Per-policy status chips in the execution panel. Visible disclosure of 2025-08-01's prior exposure, the clean-21 sensitivity, and the conditional (non-tie) target versus the all-signal edge. |
| D4 | **ACCEPTED** | Demo: alarms drawn and exported as 600-s counts; fallbacks regenerated; smoke checks temporal resolution. Lead: the external abstract now says "within 10 minutes / within 20" instead of exact times. README states that  are internal research records (some contain second-resolution detector times) and must not be redistributed outside the team. No legal clearance is claimed. |
| D5 | **ACCEPTED** | Finite-recipe wording ("across these 20 tested settings"); inset relabelled "training-day rejection rate — not a ground-truth false-alarm rate"; PROPOSAL's underflow hypothesis marked superseded. |
| D6 | **ACCEPTED** | run.sh confirms its own server serves the page and fails on an occupied port; visible boot/replay errors; cache validated by schema, day and code/input hash. |
| D7 | **ACCEPTED** | Stage layout: the dial and alarm count beside the replay, and the verdict in the same viewport at 1440×900; details view; overflow fixed at 1280×720; accessible range. |
| D8 | **ACCEPTED** | 3-minute budget (35/35/75/35 s), hero readout "26 alarms at 1e-30", story-ordered fallback deck including calibrated and off states, and the five Q&A answers. |
