- **Would this win the room? 7/10.** A judge will lean in for the real training and unusually inspectable evidence; the current three-minute act is less convincing than the implementation.
- **Working scope:** Five heterogeneous simulated nodes, real SmolLM2/text, baseline comparisons and a genuine live node-removal control satisfy the practical MVP/stretch demonstration, not physical-device feasibility or a convergence theorem.
- **Evidence:** The sampled numbers are traceable and correct; my six-round live run reproduced all 60 committed validation domain losses exactly.
- **Stage readiness:** Not yet reliable as scripted: a fast run misses the promised intervention round, the outage explanation is below the viewport, and recorded playback can conceal a still-active engine.
- **Findings:** 0 BLOCKING, 5 MAJOR, 3 MINOR. Review only; no implementation changes.

Reviewer: GPT-6 Astra, independent hostile judge under PLAYBOOK sections 10-11. Reviewed revision: `fbdf3aa8c3a8afe531eb741cc64d82008c4f8f52`, after the requested fetch/rebase. All paths below are relative to `perceptron-p01-federated-lora/`, except `PLAYBOOK.md` and `_briefs/perceptron.txt`. The runtime observations are from 4 October 2026, approximately 21:13-21:19 IST; source/robustness checks continued afterward.

## Numbered issues and exact fixes

### 1. MAJOR - Wall-clock choreography misses the validated unplug and can offer a knob after training has finished

**Evidence:** `demo/SCRIPT.md:12,16-19` starts training at 0:45, asks for the tablet click at 1:20 "during round 1", promises removal from round 2 and memory expiry in round 6, then offers another plug at 2:30. Those events are not synchronized to the engine.

In my actual seed-0 run, relative to Start, round 1 began at **5.797 s**, round 2 at **17.638 s**, round 3 at **29.529 s**, and all six rounds finished at **77.726 s**. At that observed execution rate, the script's click 35 seconds after Start lands in round 3, giving removal from **round 4**, not round 2. That later intervention permits additional tablet updates and does not support the promised round-6 memory expiry; the pre-validated band describes a different intervention. The optional 2:30 knob would already be disabled at this run's speed: completion corresponds to talk time about 2:03. Conversely, the committed 205-second validation run corresponds to about 4:10 with the same start time. Exact timings will vary, which is precisely why neither choreography is safe.

I deliberately clicked during the observed round 1 instead: the acknowledgement was at 5.897 s and specified `effective_round: 2`. The engine's next-round semantics are correct (`demo/live_engine.py:141-147,290-315`); the script is the fault.

**Exact fix:** Make the standard presentation event-gated: automatically hold after the first completed round, show "Round 1 complete - pull the tablet plug, then Resume", and resume both federations with the acknowledged round-2 removal. Rewrite the talk track around that state, not 1:20. Offer extra plugs only while a subsequent round remains; otherwise say the run has finished. Set an explicit talk-time cutoff, for example 2:10, to stop live and play the labelled recorded run at 16x, leaving time for costs. Do not promise the round-6 expiry unless the actual outage/last-update history supports it.

### 2. MAJOR - "Memory absorbs it" attributes a small system-level effect to an unisolated mechanism

**Evidence:** `demo/SCRIPT.md:18` correctly says most of the gap is domination, then says "AnchorLoRA's memory absorbs it. That held in all 5 ... seeds." The ghost comparison in `demo/web/app.js:493-509` and `demo/validate.py:81-103` changes availability; it does **not** toggle AnchorLoRA's memory while holding its other ingredients fixed. Tab 4 explicitly says no single ingredient is credited (`demo/web/index.html:156`), contradicting this spoken attribution.

The round-6 man-pages loss deltas in my live run were **+0.075494** for the starter and **-0.033554** for AnchorLoRA. Their difference is **0.109048**. In the same-seed, nobody-unplugged ghost, the difference is already **0.101402**: **93.0% of the displayed gap exists without the judge's intervention**. Across the five committed validation seeds, that fraction is 80.5%-96.7%. The unplug's own effects are only **+0.0088 to +0.0288** for the starter and **-0.0017 to +0.0084** for AnchorLoRA.

There is an especially revealing early moment: in seed 0, the starter's unplug effect is **exactly zero in rounds 2 and 3** because it would discard the tablet's partial work anyway. At round 3, AnchorLoRA is **0.002419 worse than its ghost**. At round 6 it is **0.008405 worse**. "Absorbs" must not imply no harm, an immediate loss discontinuity, or proof that memory caused the resilience. The memory-age chips do truthfully show cached-update reuse and expiry.

Sources: `demo/validation/runs/{ghost,unplug}_s0.json`, `records[round=2,3,6].delta.manpages`; corresponding files for seeds 1-4; `demo/validation/RESULTS.md:17-23`.

**Exact fix:** Replace the sentence with: "Most of this gap exists even with nobody unplugged. In the five validation seeds, removing the tablet changed the starter's final man-pages loss by +0.009 to +0.029 and AnchorLoRA's by -0.002 to +0.008. The full system was less sensitive; this comparison does not isolate memory's contribution." Put that distinction directly beside the live curve, not only in the spoken caveat. Keep the memory chip as mechanism visibility, not causal proof. If another plug or a restore changes the intervention history, label the ghost difference "combined intervention effect in this run" and the band "reference for tablet-only outage from round 2"; do not imply that custom history passed P3.

### 3. MAJOR - Switching to RECORDED hides memory pressure and disables Stop without stopping live computation

**Evidence:** `demo/web/app.js:565-585,678-680` changes the displayed state to recorded playback without calling `/api/stop`. `renderStatus()` then takes its memory state from the recorded run (`:547-548`) and defines "running" using `view === 'live'` (`:552-556`). Thus it hides the actual engine's memory banner, disables its Stop control, and re-enables Start even when the real process is still running or memory-paused.

I reproduced the UI transition in an isolated browser response fixture, without starting another model run: a memory-paused live state had Stop enabled; clicking **Play RECORDED run** issued **zero POST requests**, hid the memory banner, disabled Stop and enabled Start. This is a fixture-based lifecycle check, not a claim that my successful live run encountered memory pressure. The source confirms that the real process would remain untouched.

This matters precisely when `demo/SCRIPT.md:25` tells a presenter to switch to recorded playback because live is slow or memory-constrained. The fallback can retain roughly a model's worth of memory and resume hidden CPU work when pressure clears.

**Exact fix:** Make the fallback action explicitly "Stop live and play RECORDED" when a live process exists; await and check `/api/stop` before changing the displayed mode. Alternatively retain independent, visible live-process status and Stop controls throughout playback. Derive Start availability from actual live-process state, not which recording is displayed. Cover memory-paused and slow-running transitions in the smoke/browser checks.

### 4. MAJOR - The scripted outage explanation is not on the projector screen

**Evidence:** At the documented **1440x900, 100% zoom**, tab 2 was **1677 CSS pixels high**. The **Play rounds** button began at **y=1113**, and the starter/Anchor tablet rows were at **y=1319 / y=1519**. None is visible when the loss curve is being presented. `demo/SCRIPT.md:14` expects the presenter to click Play rounds and explain partial work/reuse at 1:00; the layout makes that an unmentioned scroll away from the evidence it supposedly explains.

`demo/web/index.html:12` says tabs fit one projector viewport, but the strip is placed after the whole two-column grid (`:72-99`); its vertical position is determined by the tall right-hand ledger (`demo/web/style.css:108,140`). The live view also grows to about 1007 pixels with explanatory text, pushing the crucial ghost/effect qualification below a 900-pixel viewport. In the visible live comparison, one panel can also be round 4 while the other is round 3; those round labels exist, but are small footnotes beneath the bars.

**Exact fix:** Give the stage view a compact, dedicated tablet strip adjacent to its curve, with the full five-device ledger available as a drill-down. Keep the intervention state, last completed paired round and causal-effect caption visible together at 1440x900 without scrolling. Present the two loss panels at the last round completed by **both** federations, while showing current device training separately. On tab changes, explicitly restore the intended scroll position. If a lower-resolution projector requires a different layout, document and test that layout rather than relying on a 90% zoom hint that applies only below 1440x900.

### 5. MAJOR - Smoke proves much of the data path, but can pass failed validation criteria and never executes the presentation

**Evidence:** The required full `bash demo/smoke.sh` passed in **83 seconds** with zero failures. It genuinely checks canonical export equality, raw replay summaries, 147 key expansions, a fresh two-round Flower run, unplug/memory state, and round-1 parity with the in-process harness. This is substantial coverage.

However, `demo/smoke_checks.py:151` checks `all(v is not None ...)`, not that P1/P2/P3 are true. A consistent validation table containing `P1: false` is still "complete" and does not fail that check. Only seed 0 is freshly rerun. `demo/validate.py:86,103` uses the last available round and five non-missing files without enforcing complete six-round records for both strategies or the intended outage in every seed. The current artifacts **are** complete and pass; this is a regression hole, not an allegation that the present results failed.

The HTTP checks at `demo/smoke_checks.py:200-205` accept JavaScript/CSS/data responses by status and byte length. They do not execute `app.js`, inspect the DOM, validate the live-control lifecycle, or check the PNG/GIF fallback files. That is why the interaction and layout defects above coexist with PASS.

**Exact fix:** Assert exactly the expected criteria and `all(value is True ...)`; validate seeds 0-4, both strategies' rounds 1-6, the exact tablet-only outage, and finite values before evaluating P1/P2/P3. Add a bounded browser smoke using committed recorded/SSE fixtures: all four tabs render; source labels, values and mode labels are correct; the essential stage controls fit; switching to fallback stops or visibly retains control of live; the six fallback frames and GIF exist. Keep the current CPU numerical checks. Do not require an additional full training run for UI coverage.

### 6. MINOR - The outage chart's printed provenance has the subtraction backwards

**Evidence:** Tab 2 plots **untuned minus trained loss**, correctly making improvement positive (`demo/web/app.js:165-174`). Its source caption says `eval.per_domain_loss.manpages` **minus** the untuned file (`demo/web/index.html:79`). The fallback repeats the reversed formula (`demo/render_fallback.py:113-115`). A judge trying to reproduce the displayed curve from the printed instructions gets the opposite sign.

**Exact fix:** Reverse the operands in both captions: `base_per_domain_smollm2-135m.json.manpages - log.eval.per_domain_loss.manpages`. Leave the separate "worst point above untuned" ledger as trained minus untuned, and explicitly retain its opposite sign convention.

### 7. MINOR - The startup memory banner can literally claim that 29 is less than 25

**Evidence:** The start guard waits below **30**, while the running guard pauses below **25** (`demo/live_engine.py:39,158-167`). Both use the same banner with hardcoded `(< 25)` (`demo/web/index.html:117`). A no-training guard probe at levels 29, 26, 30 correctly waited and resumed; the corresponding browser fixture rendered **"memory level is 29 (< 25)"**. The waiting behavior is correct, but the explanation is false.

**Exact fix:** Carry the active threshold/reason in the memory event and render either "Waiting to start: level 29; requires at least 30" or "Paused during training: level 24; resumes at 30". Keep the real memory state visible when switching presentation modes, as in issue 3.

### 8. MINOR - The persistent header sounds like a guarantee that the caveat later disclaims

**Evidence:** `demo/web/index.html:26` promises that one data-rich device "cannot quietly dominate". The measured 0.88-to-0.22 norm share is an average magnitude diagnostic under one fixed setting, not a universal bound or proof of causal influence. The later caveat is correct (`:157`), but the unqualified claim remains above every tab.

**Exact fix:** Use: "Federated LoRA with simulated weak-device budgets, live dropout handling, and transparent update-share diagnostics." Keep the measured norm-share reduction in the ledger and call it a round-and-seed mean. Do not replace this with another universal "fairness" or "no dominance" promise.

## Numerical provenance audit

`C` below means the committed `eval/results/v2_canonical.json`; `O` means `eval/results/v2_dropout_canonical.json`. These are exact JSON keys, not slide-derived estimates. I independently recomputed per-domain gains/Bonferroni lower bounds, paired macro intervals, norm-share means and outage peaks from the 20 committed per-round log files; the checked values agreed within 1e-12 before page rounding. The full live run matched the committed seed-0 unplug run bit for bit.

| On-screen number/display | Committed source or committed live computation | Judgment |
|---|---|---|
| 4 strategies x 5 seeds x 12 rounds | `demo/export_replay.py:20-30`; all `eval/results/logs/v2_dropout_<strategy>_s<seed>.json`, each 12 records | Correct; committed replay, not live training |
| Workstation 8x data; Pi rank 2 | `components/device_simulator/profiles.py:19-28`: 2400/300 blocks; c3 rank 2 | Correct and explicitly simulated |
| Starter comparison -0.081 | `C["dropout.spike_vs_fedavg_ab_homo.macro_mean"]` = -0.08149111588796006 | Correct |
| Its CI [-0.093, -0.070] | Same prefix, `macro_lo` = -0.09302679915170844; `macro_hi` = -0.06995543262421167 | Correct paired-seed interval |
| FFA comparison -0.050; Flex comparison -0.083 | `C["dropout.spike_vs_ffa_lora.macro_mean"]`; `C["dropout.spike_vs_flexlora.macro_mean"]` | Correct |
| Wikipedia +0.375 starter / +0.119 Anchor | `C["dropout.fedavg_ab_homo.wiki.gain_mean"]`; `C["dropout.anchor_full.wiki.gain_mean"]` | Correct untuned-minus-final gains |
| Anchor Python +0.013 | `C["dropout.anchor_full.pycode.gain_mean"]` = 0.013324419657389352 | Correct |
| Anchor C headers +0.006 | `C["dropout.anchor_full.cheaders.gain_mean"]` = 0.006484166781107614 | Correct; a small effect, not a large practical benefit established by itself |
| Anchor READMEs +0.027 | `C["dropout.anchor_full.readmes.gain_mean"]` = 0.02699154218037947 | Correct |
| Anchor man pages +0.040 | `C["dropout.anchor_full.manpages.gain_mean"]` = 0.0395665168762207 | Correct |
| Anchor 5/5; starter 1/5 better domains | `C["dropout.anchor_full.domains_ci_pos_bonf"]`; `C["dropout.fedavg_ab_homo.domains_ci_pos_bonf"]`; denominator is the five domains | Correct, Bonferroni criterion |
| Starter four worse domains | Count of `C["dropout.fedavg_ab_homo.<domain>.gain_hi_bonf"] < 0`, `demo/web/app.js:143-146` | Correct computed count |
| Workstation norm share 0.88 / 0.22 | `C["dropout.fedavg_ab_homo.c0_norm_mean"]` = 0.8832130985310116; `C["dropout.anchor_full.c0_norm_mean"]` = 0.2154573168368036 | Correct means; not caps |
| Equal-share reference 0.20 | Five profiles; `demo/web/app.js:155` displays 1/5 as a reference | Correct reference, not measured fairness |
| Mean losses 2.706 / 2.665 / 2.747 | `C["base.macro"]`, `C["dropout.anchor_full.macro_mean"]`, `C["dropout.fedavg_ab_homo.macro_mean"]` | Correct untuned / Anchor / starter |
| Outage peaks +0.277 / -0.020 | `O["dropout.fedavg_ab_homo.outage_peak_rise_mean"]`; `O["dropout.anchor_full.outage_peak_rise_mean"]` | Correct means of each seed's maximum across evaluated checkpoints |
| Worst-seed peaks +0.305 / -0.019 | Same prefixes, `outage_peak_rise_max` | Correct; not an assertion about unmeasured rounds |
| Tablet 3.4 starter; 5.4 + 5.4 memory Anchor | `O["dropout.fedavg_ab_homo.c4.rounds_used_mean"]`; Anchor's `c4.rounds_used_mean` and `c4.rounds_memory_mean` | Correct; memory is not fresh device computation |
| Micro cost +0.116 [+0.107, +0.124] | `C["dropout.spike_vs_fedavg_ab_homo.micro_mean"]`, `micro_lo`, `micro_hi` | Correct, Anchor worse |
| Worst-domain cost +0.057 [+0.024, +0.089] | Same prefix, `worst_mean`, `worst_lo`, `worst_hi` | Correct, Anchor worse |
| Live batch 1x64, eval 8x64/domain, 6 rounds | `demo/live_engine.py:36-38,189-191,282` | Correct reduced configuration; not the committed 4x128 evaluation |
| Tablet reuse age 1/4, then expired age 5 | `demo/live_engine.py:247-254`; current round minus `mem_round`, membership in `used_memory_for`; maximum age asserted at `:210` | Observed live; not a scripted UI animation |
| Pre-unplug max difference 0 over 10 values | `demo/web/app.js:493-511`: two strategies x five domains at round 1 compared with `demo/validation/runs/ghost_s0.json` | Observed bit-identical |
| Live final man-pages bars -0.075 / +0.034 | Negative of live round-6 `delta.manpages`, computed at `demo/live_engine.py:257-260`, rendered at `demo/web/app.js:402-406` | Observed; also exactly matches `demo/validation/runs/unplug_s0.json` |
| Unplug effect +0.016 / +0.008 | `demo/web/app.js:501-506`: live loss delta minus same-seed ghost delta at the same round | Correct for my tablet-only history; not memory attribution |
| Range over five validation seeds | `demo/validate.py:104-113`, `results.json["band"]["unplug.<strategy>"]`; min/max, not a confidence interval | Correct and labelled pre-recorded |
| Live round-6 fresh updates 3/5 vs 4/5 | `demo/live_engine.py:260`: length of aggregation `reporters`; round events for starter/Anchor | Correct full-system comparison; admitted work differs |

No invented scientific value was found in these sampled displays. Live, committed replay, prerecorded ghosts, the validation range and RECORDED mode are visibly distinguished. The exceptions concern interpretation and the reversed source formula, not fabricated measurements.

## Run, offline behavior and failure-path evidence

- The worktree initially lacked `.venv`. `UV_OFFLINE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 bash demo/fetch.sh` restored the cached packages and found the cached model. The required unmodified full `bash demo/smoke.sh` then passed in 83 seconds. Its own two-round/parity training checks are separate from the single interactive run below.
- `nice -n 10 bash demo/run.sh --no-browser` selected the next free port, **8766**. Its server printed readiness in **0.056 s** and returned the first page in **0.061 s**. Chromium's first contentful paint was **0.084 s after navigation**, with assets loaded and charts populated; browser-process launch time was not measured. Initial navigation used 1200x1038; the subsequent projector review used 1440x900. The first-visual requirement is comfortably met.
- I opened every tab, played the committed round strip, started exactly **one interactive six-round live run**, and clicked the tablet in round 1. Memory level immediately before Start was **36**, above the required 30. Both grids removed c4 from round 2; reuse advanced through age 4 and expired at age 5 in round 6. Both federations began identically. The run finished in **77.7 s**, with no engine error or real memory pause. It emitted 12 round-result events, covering 60 domain losses, all identical to the committed seed-0 unplug validation. The server was launched at nice 10; its engine adds another nice 10, so the observed child priority was 20. No GPU was used.
- Browser requests were all loopback: HTML, CSS, JS, status and SSE; there were no external browser requests or console errors/warnings. The model/tokenizer loaders explicitly use `local_files_only=True` (`components/local_trainer/trainer.py:49`, `components/orchestrator/simulate.py:48`). This is evidence for offline operation after fetch, not a claim that I globally disabled this shared Mac's network.
- Missing-model behavior was checked with an absent-cache preflight probe and an isolated browser status fixture: Start was disabled, the fetch instruction was visible, and RECORDED remained available. Memory guard probes tested start at 29 and training at 24, each resuming only at 30, without loading another model. The UI fixture exposed issues 3 and 7. I did not deliberately exhaust the shared machine's memory.
- Browser RECORDED playback at 16x completed all six rounds with conspicuous "RECORDED, not live" labelling and matching losses/reuse expiry. I inspected the committed gains/outage/final-live fallback images and their rendering code. The GIF is a six-frame, 933x493 loop with 1600 ms per frame. This is a real, usable fallback; its live-process handoff is the defect.
- The read-only interface detector reported no findings; that does not override the directly observed stage-layout defects. After the checks, I killed only my server's specific PID, **18363**, and verified that it exited and port 8766 no longer responded. Its engine had already exited successfully. No server was left running by this review.

## Judge impact and what is strong

**The baseline gap is visible well within 30 seconds.** Tab 1 is the best part of the act: real-model results first, four named strategies, all five domains, uncertainty and the 5/5 versus 1/5 distinction in one view. It does not ask the judge to trust a decorative progress bar or a synthetic toy loss. The orange/teal comparison is readable, and the source keys make the result challengeable rather than merely impressive.

**The first hostile question would be: "Would the starter fail anyway if I never touched the plug?"** The answer is yes for the demonstrated late-run man-pages pattern, and the ghosts already expose it. That transparency is a strength. The presenter should volunteer the small incremental effect before being challenged. The next question is "Why credit memory rather than weights, clipping or admitted work?" The honest answer is that this live comparison does not isolate them. Tab 4 has the right full-system caveat; the spoken explanation should match it.

**The knob changes something real.** It removes a Flower node from both in-process grids at the next round, changes the updates actually admitted, and visibly exercises reuse and expiry. This is useful engineering theatre because it is inspectable and deterministic. It is not a physical device crash, an OS-process kill or an isolated demonstration that the cached update saved the model; those distinctions are mostly already labelled correctly.

**The cost disclosure earns trust.** Showing that macro improvement comes with worse sample-weighted and worst-domain loss prevents a misleading "better at everything" story. The explicit simulation label, CPU-only path, reduced-live-config qualification, checkpoint-only claims, prerecorded-range label and fallback assets are all strong. The small holdout, fixed baseline settings, simulated resource budgets and lack of matched-work attribution remain limits, not findings that this review requires the team to solve with new expensive experiments.

An Optiver engineer is likely to lean in at the real paired run and deterministic control; an IIT Bombay professor is likely to lean in at the paired intervals and ghost counterfactual, then immediately test the causal wording. Make the stage sequence event-driven, keep the live/fallback controls truthful, and lead with "transparent, less-sensitive full system" rather than "the plug proves memory saves it." That would make this a much stronger finals-room demonstration without changing a single committed result.

---
## Lead dispositions (Claude Opus 5.5 lead, 2026-10-04 21:31 IST)
All 8 findings **ACCEPTED** and sent to the demo builder with exact fixes; none rejected.
| # | Sev. | Disposition |
|---|---|---|
| 1 | MAJOR | ACCEPTED. Event-gated stage flow: auto-hold after round 1 so the validated round-2 unplug always happens; extra plugs only while rounds remain; SCRIPT rewritten around states with a cutoff to RECORDED; no round-6 expiry promise unless the history supports it. |
| 2 | MAJOR | ACCEPTED. "Memory absorbs it" is replaced with the reviewer's exact full-system sentence, shown beside the live curve with values from `demo/validation/results.json`; custom histories are labelled "combined intervention effect in this run". |
| 3 | MAJOR | ACCEPTED. "Stop live and play RECORDED" awaits /api/stop; live-process status (memory banner, Stop) stays truthful; Start follows the actual process state. |
| 4 | MAJOR | ACCEPTED. 1440×900 stage layout: compact tablet strip beside the tab-2 curve; live intervention state, last paired round and effect caption visible without scrolling; panels at the last round both federations completed. |
| 5 | MAJOR | ACCEPTED. Smoke asserts P1/P2/P3 are True and that the validation records are complete; a bounded headless UI self-test (skipped with WARN if no browser), with no new dependencies; fallback files checked. |
| 6 | MINOR | ACCEPTED. Provenance formula on tab 2 and in the fallback corrected to untuned − trained. |
| 7 | MINOR | ACCEPTED. Memory banner shows the active reason and threshold. |
| 8 | MINOR | ACCEPTED. Header reworded to the reviewer's text; no "cannot quietly dominate". |
