**Method: dual-agent frontend critique** (isolated visual and detector/browser assessments), supplemented by GPT-6 Astra's source, statistical, extract and live numerical-state audit. Scientific judgments and the scores below are the reviewer's.

# Hostile finals-demo review: GPT-6 Astra

**Reviewed snapshot:** `f58966cc70bfe1706d67b455c7b208b478ae18bc`, after the requested fetch/rebase. **Evidence timestamp:** 2026-10-04 22:02:18 IST, read with `TZ=Asia/Kolkata date`. This review concerns that snapshot, not subsequent repairs.

All paths below are relative to `perceptron-p03-off-policy-eval/`, except `PLAYBOOK.md`. JSON citations specify keys because the result files are serialized onto long lines. Severity **blocker** means a claim that must not be presented unchanged to a technically competent panel; it does not mean the HTML fails to launch.

## (d) Verdict and scores

**Working real-data MVP: yes. Top-three finals demo: no, as presented.** The refusal stamp is a good piece of communication. The numerical implementation is substantially better than the story told about it. You have built an inspectable illustration of OPE and a frozen diagnostic rule, not demonstrated an evaluator that reliably knows when it is right.

| Dimension | Score /10 | Hostile-panel assessment |
|---|---:|---|
| Wow factor | **7** | Real data, a genuinely responsive control, two logging regimes and a visible refusal are memorable. The moment is an explanation of existing statistics, not an unexpected new capability. |
| Clarity in three minutes | **4** | Too many numbers, qualifications and states. The script skips the clean standard-OPE sheet, races through the important failure, then narrates row-level counts while the screen is in cluster mode. |
| Technical credibility | **6** | Reproducible extracts, correct core weight algebra and an independently reproducible paired interval deserve credit. The claims about truth, validation and the gate's operating value do not follow. |
| Honesty | **5** | Negative results and post-hoc labels are unusually well documented. The headline, script and Q&A repeatedly undo those disclosures, including an endpoint switch that makes a failure appear to disappear. |

These are demo judgments, not the abstract rubric and not a statistically estimated competition ranking. Other teams' final demos were not available. On the evidence here, I would not advocate a top-three placement.

## What I actually checked

I read PLAYBOOK section 11, the demo source and documentation, the manifest and structured results, and viewed **all twelve** fallback PNGs. I did not change demo code or run the large OBD extraction or simulator banks.

The supplied interpreter was:

```text
/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-effective-funicular/perceptron-p03-off-policy-eval/.venv/bin/python
```

I checked `sysctl -n kern.memorystatus_level` before the requested commands: **43**, above the required 30. Both commands used `nice -n 10` and the supplied `P3_PYTHON`.

| Check | Observed result |
|---|---|
| `P3_NO_OPEN=1 ... bash demo/run.sh` | Success; page ready in **0.2 seconds**; identical generated page. This measures launcher/build readiness, not a human opening a browser. |
| `... bash demo/smoke.sh` | **23/23 PASS**; knob replay **4.2 seconds**, byte-identical JSON and Markdown; 58 endpoint/CTR checks and 12 series cross-checks passed. |
| Local browser, numerical states | W2 0.42 answers; one right-arrow to 0.43 refuses; Nov 26 0.33 changes E1 status under clustering; Nov 25 0.05, SNIPS toggle and both simulator positions respond. No page exceptions in this direct pass. |
| Independent result inspection | Exported estimator values/SEs and packed E1/E2/gate flags match the committed grid, subject to the builder's documented numeric rounding. |
| Independent contested calculation | Standard-library aggregation of the vendored counts, without importing project code, reproduced the Nov 26, alpha 0.33 IPS row and hour-cluster SEs, including paired E2, exactly to float precision. |
| Scope | Worktree remained clean after the requested runs. Only this review is an authorized edit. |

This is a clean-worktree check with the supplied installed environment, **not** a fresh-clone dependency installation. The manifest and hashes were checked; rebuilding the extract from the original remote zip and independently re-verifying its licence were **UNVERIFIED in this review**. `data/NOTICE.md` does contain attribution, a licence statement, modifications and a no-endorsement statement. No external paper or web source is asserted as independently opened for this demo review.

**Frontend evidence:** the visual assessor inspected all four sheets at 1920x1080 without seeing detector findings. Its verdict was a distinctive interactive research exhibit, not a dependable three-minute presentation; it independently found the script/state mismatch. The deterministic detector raised two generic flags, `codex-grid-background` and `single-font`; both were discarded because the computation grid is intentional and the page has separate display/body/monospace hierarchy. No actionable detector finding was accepted. This is not an accessibility certification. The documented 1280x720/90%-zoom projection setup remains **UNVERIFIED**; no human timed rehearsal was performed. Owned browser pages and the temporary local server were closed after inspection.

## (a) Does it show the requested MVP?

**Yes.** Sheet 1 opens on real OBD data, explicitly calls the switch a re-enactment, and puts naive **+1.62**, concurrent A/B reference **+1.26**, and DR **+1.40** in the same calculation. Sheet 2 supplies IPW, SNIPW, DM and DR, with the reconstructed-target and DM-uncertainty caveats. Simulation is last and visibly stamped **SYNTHETIC**. This meets the real-first/baseline requirement in `PLAYBOOK.md:169-173`; see `demo/index.html:226-303` and fallback images 01-03.

Do not inflate that pass. The DR interval **[+1.13, +1.67]**, and the hour-block interval **[+0.93, +1.78]**, both also contain the naive number. The page commendably says so (`demo/index.html:251`). This demonstrates a different point estimate and a plausible correction, not statistically established superiority on this case. In the reverse switch the naive estimate is closer to the reference than DR, also disclosed on sheet 1 (`demo/index.html:278`). Keep those qualifications.

The presentation also jumps from sheet 1 to sheet 3 at 1:00, never giving sheet 2 a scheduled beat (`demo/SCRIPT.md:19-30`). The MVP exists; the three-minute talk does not make its strongest standard-OPE comparison especially easy to see.

## (b) Is the alpha-knob striking and correct?

**Striking as an interactive explanation; largely correct as arithmetic; oversold as validation and decision intelligence.**

For BTS logs, with `x_i = (1/80)/ps_i`, the code uses `w_i = (1-alpha) + alpha*x_i`. For Random logs the far-end share is instead `lambda = 1-alpha`, and the far-end target is an hourly BTS reconstruction. Those are the declared policies, not a new OPE estimator (`demo/preregistration_knob.md:16-44`; `demo/knob.py:91-124,128-176`).

The IPS and SNIPS computations and same-arm cancellation in E2 are coherent for the stated analysis. The hour-cluster calculation aggregates the two arms jointly by hour for E2 rather than incorrectly treating their reused pieces as independent. The problems are how these quantities are interpreted and which of them the presentation chooses to show.

Here is the operating point the panel should see. Each entry counts **grid locations, not independent tests or deployments**:

| IPS endpoint / scope | Answer, reference inside | Answer, reference outside | Refuse, reference inside | Refuse, reference outside |
|---|---:|---:|---:|---:|
| E1 row-level, **BTS primary only** | **75** | **12** | **403** | **116** |
| E1 row-level, Random secondary only | 606 | 0 | 0 | 0 |
| E1 row-level, pooled | 681 | 12 | 403 | 116 |
| E1 hour-cluster, pooled | 693 | 0 | 490 | 29 |
| E2 row-level, pooled | 654 | 39 | 458 | 61 |
| E2 hour-cluster, pooled | 654 | 39 | 458 | 61 |

For E2, "inside/outside" means whether the **difference interval contains zero**, not point containment in the estimator's own interval. Counts were independently summed from `demo/results/knob_results.json -> series[*].summary`; the per-series evidence is in `demo/results/knob_summary.md:12-47`.

The registered primary was **IPS, row-level, BTS logs** (`demo/preregistration_knob.md:78`). On that primary analysis the gate answers only **87/606 = 14.4%** of grid locations, and E1 holds for **75/87 = 86.2%** of answers. Pooling in the 606 Random-side successes produces the much more flattering **681/693 = 98.3%**. Both calculations are arithmetically valid; they tell very different stories.

## Numbered issues: claims, evidence and safe replacements

### D1 - BLOCKER: the noisy reference becomes "true value" on the main screen

> "Its true value is a straight line between the two A/B arms"

The wording is on sheet 3 (`demo/index.html:315`) and in the 1:00 narration (`demo/SCRIPT.md:22`). The protocol explicitly says the empirical concurrent-arm reference is **never ground truth**, and notes unresolved arm balance and the Random-side target approximation (`demo/preregistration_knob.md:50-55`). The raw-label investigation explicitly does not establish that the differently anonymized categories are equivalent (`eval/results/obd_raw_labels.md`, closing paragraph).

Value is linear in a mixture of fixed policies **on the same evaluation distribution**. That theorem does not make a line through two sampled CTRs population truth. Nor does it identify the result of deploying a new adaptive mixture, which would change the sampler's future history. The BTS side uses a per-impression mixture along the realized history; the Random side uses a different, approximate target. "Blue asks the same question" (`demo/SCRIPT.md:25`) suppresses that difference.

The opening "A team switched recommendation policy" (`demo/SCRIPT.md:19`) also invents a historical rollout that this analysis re-enacts from concurrent arms.

**Safe replacement:** "We re-enact a switch using concurrent A/B logs. The black line mixes the arms' observed click rates: a noisy reference, conditional on comparable traffic, not known truth. BTS weights use logged propensities; the Random-side target is an hourly approximation."

Put the qualification next to the line, not exclusively in a footer after four sheets. Replace "overstates the policy by 29%" with "is 29% above the concurrent A/B point estimate" (`demo/index.html:247`).

### D2 - BLOCKER: the screen merges endpoints that the results correctly separated

There are two manifestations of the same error.

**First, sheet 1:** "4/5 interval held the check" is **reference-in-own-CI**, while "2/2 failures refused" is **S1 paired-consistency rejection** (`demo/index.html:273-275`; the `data-src` keys identify the different endpoints). Under the former endpoint there are **three** distinct misses, only **two** refused. The displayed sequence invites the interpretation that all interval misses were caught. They were not. The results document explicitly says "Three endpoints, never merged" (`eval/results/gate_obd_posthoc.md:5-8`).

**Second, the live negative example:**

> "With hour-cluster intervals, those misses disappear."

This is true for E1 point containment, not for E2 consistency (`demo/SCRIPT.md:27,52`). At **Nov 26, BTS logs, alpha 0.33**, the committed and independently reproduced numbers, per 1,000, are:

| Quantity | Value |
|---|---:|
| IPS estimate | 4.379425 |
| Concurrent reference | 4.528112 |
| IPS hour-cluster own interval | [4.091233, 4.667617] |
| Estimate minus reference | -0.148687 |
| Joint-hour E2 interval for that difference | **[-0.289526, -0.007848]** |

The reference is inside the first interval, but **zero is outside the difference interval**. There remain **39 answered E2 rejections** on Nov 26, in both interval modes, over alpha 0.01-0.39. These are correlated locations along one failure curve, not 39 independent discoveries.

The browser carries E2 bits and summaries, but the readout, strips and totals are driven by E1 (`demo/page.template.html:409-410,431,479-538`; `demo/build.py:294-305,325-330`). E2 appears in the prediction table, not as a selectable/current consistency verdict. "Nothing hidden" therefore does not mean every registered endpoint is visible.

**Safe replacements:** "Two of two **S1 rejections** were refused; two of three **reference-in-own-CI misses** were refused." And: "Clustering removes these own-CI point-containment misses. The paired consistency test still rejects here; a green E1 is not a validation certificate."

Expose E1 and E2 beside each other. Do not fix this by renaming the surviving E2 failures out of the story.

### D3 - MAJOR: the preregistration chronology is documented honestly, then misrepresented orally

> "It was calibrated on the simulator only, before touching OBD."

That Q&A answer (`demo/SCRIPT.md:50`) contradicts both the same script's 0:40 disclosure and `eval/results/gate_obd_posthoc.md:3`: the **diagnostics, simulator knobs and selection criterion** were chosen after seeing OBD failures. Simulator-only threshold fitting is not independence of the calibration design from OBD.

The sheet-3 registration is real in the narrower, inspectable sense: `10209ca` precedes result commit `3919858` in ancestry; the recorded commit times are 21:07:34 and 21:15:58 IST; the registration file is unchanged. That does not turn previously inspected data into held-out data.

The Q&A also calls Nov 24 and the full window "two periods never examined before" (`demo/SCRIPT.md:44`). Nov 24 far-end values had already been used for predictions; the full-window Random endpoint was already committed. The protocol itself identifies the narrower additions: full-window **BTS aggregation** and specific previously unrecorded z-statistics (`demo/preregistration_knob.md:92-105`).

**Safe replacement:** "The rule was selected using simulator runs after OBD failures had informed its design. We later froze the knob protocol before calculating its curves, while disclosing the endpoints already seen. This is preregistered reuse of OBD, not an untouched real-data holdout."

The held-out simulator result is useful and can be quoted separately: 818/1,536 answered, 771/818 covered versus 1,404/1,536 ungated. Both had zero confident wrong signs (`eval/results/gate_holdout.md:3-5`; `demo/SCRIPT.md:51`). Do not present it as a demonstrated reduction in wrong-sign decisions.

### D4 - MAJOR: "31/33 predictions" and nonlinear SNIPS do not create new evidence

The protocol deserves credit for forecasting failures as well as successes. Nevertheless, predicting a curve from already observed sufficient statistics mostly tests algebra and implementation.

Let `lambda` be the far-end share, `p` the logging-arm CTR, `u` the far-end IPS estimate and `m` the far-end mean weight:

```text
IPS(lambda)   = (1-lambda)*p + lambda*u
SNIPS(lambda) = [(1-lambda)*p + lambda*u] / [(1-lambda) + lambda*m]
```

Here `m = IPS(far)/SNIPS(far)` because the far-end estimates are nonzero. I reconstructed **every SNIPS point in all 12 series from endpoint values alone**, with maximum absolute discrepancy **1.74e-18**. Nonlinear does not mean informationally new. The algebra is also visible directly in `demo/knob.py:137-140,157-168`.

Thus "The genuinely new evidence is SNIPS" and "two periods never examined before" are not defensible descriptions (`demo/SCRIPT.md:41-45`; `demo/page.template.html:537`). Hour-cluster sufficient statistics are an actual additional analysis; they still reuse these observations. Exact grid crossings are useful implementation checks, not independent discoveries.

"We predicted 0.43 from one committed number" is also too strong: `demo/prereg_predictions.py:56-73` uses far-end ESS, z and n. And the generic on-screen "alpha times the error at alpha=1" statement applies to BTS logs; Random logs use `lambda=1-alpha` and their far endpoint is alpha=0.

**Safe replacement:** "31/33 endpoint-derived checks matched. IPS and SNIPS curves are determined by endpoint statistics; new work includes hour-cluster uncertainty and the disclosed additional aggregates. The novelty here is the inspectable diagnostic interface, not a new estimator or 33 independent forecasts."

### D5 - MAJOR: the gate's usefulness is not established by 403 "unnecessary" refusals

> "403 refusals that weren't needed. It is a conservative auditor."

The **403 count is correct under the registered E1 definition** (`demo/SCRIPT.md:28`; `demo/results/knob_summary.md:26`). It is not 403 known-safe opportunities that the system mistakenly rejected. Containing a noisy reference point does not establish truth or decision quality. Likewise, "justified abstention" is a descriptive label against this endpoint, not proof that abstention maximizes value.

The six periods overlap heavily; the 101 alpha values are deterministic functions of the same observations. A finer grid would manufacture more counts without adding evidence. The favorable pooled headline also hides the weak primary operating point: **85.6% of BTS grid locations refused, with 12 E1 misses among only 87 answers**. Even under its own proxy, this is not a high-availability reliable oracle.

The 5% ESS/n threshold is a frozen heuristic chosen on a simulator. Its reproducible crossing is not a statistically identified boundary between "knowable" and "unknowable." No business loss for wrong answers versus refusals, accepted-error tolerance, or general real-data guarantee is established here.

**Safe replacement:** "Under the registered point-containment diagnostic, 403 refused grid locations contain the reference. These are correlated locations, not independent decisions. The gate trades fewer answers for a lower observed miss fraction; deployment value remains untested."

Report the BTS primary and Random secondary separately, show the ungated comparison on the same scope, and label green **diagnostic pass**, not safe-to-deploy. Do not retune the rule on this plot.

### D6 - MAJOR: the three-minute claim is not a credible presentation plan

The visual assessment counted **500 whitespace-delimited words in the spoken column alone**, excluding caveats and Q&A. That is **3:20 at 150 words/minute**, before pauses or interactions. The 0:40 beat contains **93 words in 20 seconds**, requiring 279 words/minute, while the 2:50 closing beat needs **47 words in ten seconds**, or 282 words/minute (`demo/SCRIPT.md:21,30`). Expanding long numbers aloud only makes this worse. A practical delivery of roughly four to five minutes is an estimate, not a measured rehearsal.

The 0:40 beat alone combines the refusal, a seven-digit row count, an ESS equivalence, an extreme-weight anecdote, a different day, two estimates, three track-record ratios, post-hoc disclosure and a new test before the 1:00 beat. These are not speaking notes for a calm three-minute demonstration.

The fallback images show the same density: controls, two confidence bands, ESS, two selected-period strips, two long readouts, a full-period strip and prediction table all compete on sheet 3. The desktop assessment found the chart starting roughly **447 pixels down** the sheet, with the full-period strip below the fold; the decisive readout stamp is **17px** (`demo/page.template.html:485`). The strongest caveats live below the immediate chart or in later prose. An engineering-pad visual language is distinctive; an engineering report is not automatically a presentation.

**Change:** reduce the spoken script to roughly **350-400 words**, time a rehearsal including clicks, and schedule explicit states rather than hoping the audience can read everything. Keep one real baseline/OPE/reference comparison, one refusal transition, one unresolved negative, and a brief labelled simulation. Put the forest plot, full grid, prediction ledger and detailed caveats into deliberate Q&A views. Do not remove the caveat that changes the meaning of the main claim.

### D7 - MAJOR: following the script makes the spoken totals disagree with the live screen

At 2:10 the presenter presses `c`, changing to hour-cluster mode. At 2:15 the instruction is only "Scroll to the strip," while the narration gives **681 / 12 / 403** (`demo/SCRIPT.md:27-28`).

I followed that state transition in the browser. It actually displays **693 answered with the check inside / 0 outside / 490 refused with the check inside / 29 outside**. The source confirms that totals follow the current interval mode (`demo/page.template.html:523-528`). Fallback 10 shows row-level totals, so the live and fallback paths are not the same.

**Exact fix:** insert "press `c` again; verify row-level is selected" before the row-level totals, or speak the cluster totals and explicitly contrast them with the primary result. Better: create three named presentation presets that set period, alpha, estimator, interval and visible sources together.

The period instruction "`]` to Nov 26" is also underspecified: from W2 the order is Nov 24, Nov 25, Nov 26 (`demo/knob.py:38-44`; `demo/page.template.html:600-602`). Say "click Nov 26" or "press `]` three times." Avoid stateful shortcuts for the central negative example.

### D8 - MAJOR: the explanatory diagnostics are scientifically stronger than their definitions

Three statements need narrowing:

| Claim | Problem | Safe replacement |
|---|---|---|
| Logged rows "are worth ... rows logged by the candidate itself" (`demo/page.template.html:490`; also sheet 1) | Weight ESS is a concentration diagnostic, not an exact reward-variance-equivalent sample size, especially under dependence and for DR. | "Weight ESS is approximately 25,395, or 0.92% of rows; this measures weight concentration, not guaranteed precision." |
| "one click counts 12,500 times" (`demo/SCRIPT.md:21`) | 12,500 is the maximum weight over **all** W2 rows, not clicked rows. Independently inspecting the extract found no clicked row at that weight; the maximum clicked-row weight in W2 is **138.889**. | "A click at the smallest logged propensity would receive weight 12,500; the largest observed clicked-row weight here is about 139." |
| "the logged propensities don't add up for the items actually shown" (`demo/SCRIPT.md:56`) | A mean-weight z departure is not a proof that action probabilities fail to normalize. Dependence, heavy tails, probability estimation and model assumptions matter. | "The iid mean-weight diagnostic flags this log slice; it does not identify the cause or prove the recorded propensities invalid." |

The second claim is a legitimate **hypothetical** in the more qualified on-screen sentence, but the talk turns it into an observed anecdote. Large weights on non-clicks can still matter, particularly to DR; this is not an argument to ignore them.

The novelty should be making uncertainty comprehensible, not replacing a precise diagnostic with a stronger, incorrect everyday analogy.

### D9 - MAJOR: the simulator says "exact" and visually combines two different experiments

> "exact ground truth (Monte Carlo)"
>
> "This is the simulator, where the truth is known exactly."

These are adjacent on-screen claims (`demo/index.html:345,349`). `ground_truth()` averages over sampled contexts and latent variables (`components/simulator/sim.py:94-112`); the two runners use **200,000 Monte Carlo draws**, not an analytic population integral (`eval/run_decomposer_review.py:160`; `eval/run_sim_bank.py:108`).

There is also a presentation mismatch, visible in fallbacks 11-12 and reproduced live. The headline and waterfall remain the fixed S1 case: **naive -5.6, policy +7.5, 30 seeds**. At the slider's default drift -1.00, the readout instead says **naive -8.10, reference +6.25, 20 seeds**; at +0.50 it says **naive +16.30, reference +7.79** while the headline still declares a seasonal drop and -5.6.

Both results can be correct: the sweep has `mix_shift=0`, whereas S1 has `mix_shift=0.5` (`eval/run_decomposer_review.py:29-33`; `eval/run_sim_bank.py:28-35`). The interface does not make that separation sufficiently explicit for a three-minute viewer.

**Safe replacement:** "Synthetic benchmark; population reference approximated with 200,000 Monte Carlo draws." Label the waterfall "Separate fixed S1 case: mix shift 0.5, 30 seeds; not controlled by this slider." Prefer hiding that fixed case during the sweep rather than making apparently contradictory numbers share a headline.

### D10 - MINOR: the centerpiece does not support "hover any number"

> "`build.py` writes each number on the page with a `data-src` ... shown on hover."

That README claim (`demo/README.md:59`) and the 2:50 instruction (`demo/SCRIPT.md:30`) are false as interface descriptions. There are **83** static `data-src` spans, but the knob's generated estimates, intervals, ESS, weights and checks have none; neither do its totals and prediction counts (`demo/page.template.html:479-510,525-538`). The source table and committed JSON make the numbers traceable in the repository, but a judge cannot perform the promised interaction on them.

Static hover/focus tooltips work. The mechanical assessment found no `aria-describedby` association with the tooltip, and Escape did not dismiss it. Those are secondary accessibility issues, not reasons to dismiss the whole demo.

**Exact fix:** give each dynamic readout a source key such as `series['D26\u00b7SB'].rows[33].IPW.se_cl`, include the active endpoint/interval in the source display, and make it available on focus as well as hover. Until then say "Dotted numbers have hover sources; full provenance is in the README and result files."

### D11 - MINOR: replay and independent recomputation are different claims

> "One command rebuilds the page from a 0.76 MB vendored extract."
>
> "`demo/smoke.sh` re-derives the extract numbers with no shared code."

The launcher runs `build.py`, which reads committed result JSON/CSV and the manifest, not the extract's row counts (`demo/run.sh:22-30`; `demo/build.py:364-381`). The separate smoke command invokes `knob.py` to replay the grid from the extract using **the same implementation**. Its genuinely independent standard-library portion recomputes five core CTR/effect quantities, not every interval and decision (`demo/smoke_check.py:58-85`).

Caching is expressly acceptable for this demo (`PLAYBOOK.md:180-182`), and the byte-identical replay is real. Do not turn it into a second independent implementation or claim that moving the browser slider runs OPE over raw data.

**Safe replacement:** "The page renders committed results offline. The smoke command recomputes the grid from the 0.76 MB extract with the analysis code and independently checks five basic quantities."

The builder also rounds embedded values to six significant digits. Re-deriving integer ESS from those rounded fractions disagreed with rounding the full-precision ESS at 119 grid locations, generally by a few rows. This is harmless display precision, not fabricated evidence; do not call the displayed integers exact.

### D12 - MINOR: one fallback captures an internally inconsistent selected period

`demo/fallback/08_knob_Nov25_a0.05_mean_weight_z_refusal.png` has **Nov 26 selected** in the period buttons but a **Nov 25** readout and Nov 25 data. I viewed it, then selected Nov 25 normally in the live page; the live control correctly selected Nov 25.

This is a stale/inconsistent capture, not evidence that the normal period control is broken. It is exactly the sort of avoidable contradiction a judge spots while the presenter claims every state is auditable.

**Exact fix:** re-capture 08 using the ordinary controls or a fresh valid deep link after the page has settled. Verify selected period, estimator, interval, readout and filename together. Also make the fallback sequence match the actual shortened talk rather than saying all twelve files have the same click path as the script (`demo/SCRIPT.md:13`).

## (c) Overall honesty assessment

**The principal displayed numerical values are sourced; their interpretations and per-number inspection promises are not uniformly sound.** The real before/after, standard-OPE, knob and simulator figures trace to the stated result files. The extract checks, observed alpha crossing and disclosed negative rows are genuine. I found no basis to allege invented numerical results.

The serious problems are more specific: empirical reference called truth; reused data called fresh; E1 success standing in for E2 consistency; grid counts sounding like independent validations; ESS sounding like exact precision; and a script that contradicts its current UI state. Detailed disclosures in a README do not rescue an opposite sentence spoken over the plot.

## (e) Five highest-impact changes feasible in one day

1. **Repair the claim contract, everywhere.** Use D1's noisy-reference wording on sheet 3 and in the opening; delete "before touching OBD," "two periods never examined before," and simulator "exact" claims. Keep a readable line under the chart: "Fixed-history comparison; Random target approximate; arm comparability unresolved." This is a copy edit, not a new experiment.
2. **Expose the endpoints and the primary scope.** Add current E1 and paired E2 statuses; export the already-computed difference SEs if needed. Show BTS-primary **75/87 answered E1 holds, 519/606 refused**, with Random secondary separate. Label sheet-1 "2/2" as S1, and show **2/3** for own-CI misses. At Nov 26 alpha 0.33, explicitly show the surviving cluster E2 rejection. Do not refit the threshold.
3. **Make a rehearsable three-minute path with deterministic state.** Cut to 350-400 spoken words and a handful of timed actions. Put baseline, OPE, reference and gate on one presentation viewport; move the ledger into Q&A. Use named W2/0.42, W2/0.43 and Nov26/0.33 presets. Explicitly restore row-level mode before speaking row-level totals. Measure a full rehearsal, not just reading speed.
4. **Replace forecast theatre with an honest boundary explanation.** Show the two endpoint formulas from D4 and state what really required additional computation. Explain that 5% is a frozen heuristic, not a theorem. Replace the ESS and clicked-row anecdotes using D8. A judge should leave understanding what the system does *not* establish, not remembering "31/33" as predictive discovery.
5. **Finish the audit affordances and fallback states.** Attach file/key/endpoint provenance to dynamic numbers; distinguish result rendering, same-code replay and independent checks. Clearly separate the static S1 case from the sweep. Re-capture 08 and the shortened fallback sequence through normal controls, checking active period and interval. No large download, new simulator bank or GPU is needed.

These are ranked for this demo, not a demand to complete a new research programme before presenting. A three-student team can divide copy/story, endpoint/readout wiring, and rehearsal/capture work.

## (f) Three live questions and what a strong answer must contain

### 1. "You already have both A/B arms. What did OPE identify that the A/B test did not, and would your line remain correct after a real deployment?"

A strong answer separates the data used to estimate from the held-as-reference arm, writes the BTS importance weight, and names the estimand: a one-step/fixed-history mixture on the observed evaluation distribution. It admits that the empirical A/B line is noisy, arm balance is unresolved, the Random-side target is reconstructed, and a newly deployed adaptive mixture could change subsequent histories. It must also concede that the displayed DR interval includes the naive number. "We recovered the true policy effect" is not an acceptable answer.

### 2. "You pressed `c` and the failure turned green. Did you resolve the problem or change the test?"

A strong answer says: "We changed the interval model, and the green status is E1, not the paired E2 test." Show **4.379 versus 4.528** and the joint-hour difference interval **[-0.290, -0.008] per 1,000**. Explain shared-arm covariance and why common variation cancels in a difference. Admit that E2 still rejects at all nonzero answered Nov 26 IPS grid points. State that hour clustering was predeclared, but does not prove independence across hours or solve adaptive-target uncertainty. No claim that all failures vanished.

### 3. "Why should we trust or pay for this gate? Most of your plots follow from endpoints and the rule rejects most of the primary cases."

A strong answer begins with the limitation, not the stamp. IPS/SNIPS are standard; the curve algebra is largely predetermined; 31/33 is mainly a reproducibility check. Give **87/606** primary answers, **75/87** E1 holds and the separate E2 result, with an explicit warning that these are dependent grid counts. State how OBD informed calibration design, what the later simulator holdout actually showed, and that wrong-sign benefit was not demonstrated there because both versions had zero such errors. Defend the product as an inspectable diagnostic aid, then specify a future held-out, cost-sensitive test of errors versus refusals rather than promising a universal 5% safety boundary.

## Fallback-image inspection record

| Image | What I saw |
|---|---|
| 01 | Real-data headline and worked naive/reference/DR comparison; refusal begins below the main calculation. |
| 02 | Large refusal stamp, post-hoc wording, mixed-endpoint track record, start of standard-OPE sheet. |
| 03 | Eight-estimator forest plot, approximate-target caveat and static-DM refit illustration. |
| 04 | W2 alpha 0.25; both sources answer, with separate bands and ESS/readouts. |
| 05 | W2 alpha 0.43; BTS refuses while its own interval still contains the reference. |
| 06 | Nov 26 alpha 0.33; E1 miss visibly red although the gate answers. |
| 07 | Same location, clustered E1 green; the surviving E2 rejection is not displayed. |
| 08 | Nov 25 readout but Nov 26 selected: D12. |
| 09 | Full-window alpha 1; BTS refuses, Random endpoint equals its own empirical reference by construction. |
| 10 | Row-level full-grid counts and 31/33 ledger; not the live state reached after the script's cluster toggle. |
| 11 | Drift -1.00 sweep, 20 seeds, beside a different fixed S1 illustration with 30 seeds. |
| 12 | Drift +0.50 sweep becomes positive while the fixed negative headline/waterfall remains. |

**Bottom line:** keep the real data, the offline implementation and the refusal interaction. Remove the implied epistemic guarantee. An Optiver judge will respect a tool that exposes a limitation; they will not confuse a green interval, a frozen threshold or a deterministic forecast with knowing the answer.
