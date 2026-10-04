# P7 live-demo judge review

- **Model:** gpt-6-astra
- **Effort:** max
- **Date:** 2026-10-04, from `TZ=Asia/Kolkata date +%Y-%m-%d`
- **Commit reviewed:** `40e3f0ccda7895bce746ceaca8a82b1736da655d`
- **Demo's last change at that commit:** `0738aee366df3f6d10aa07a4b7dbe814acd504b7`
- **Role:** independent judge watching the finals demo, combining an Optiver quant's skepticism with an IIT Bombay professor's demand for a defensible experiment.

All paths below are relative to `perceptron-p07-multi-agent-allocation/`, except `PLAYBOOK.md`. This is a review of the pinned implementation, not a review of changes other sessions may subsequently make. No implementation files were edited.

## Verdict: 7.5/10 for making me rank this team top three

**I would lean in and shortlist this team. I would not yet confidently put it in the top three.** The computation is real, the baseline is visible, and showing a setting in which the planner loses is excellent. My arbitrary synthetic click produced **227 versus 26 losses** in its first 120 minutes; changing to L=8, P=10 and injecting another surge produced **554 versus 627**, against the planner. Those were newly computed outcomes, not selected entries in a recording. The untouched NYC replay independently reached **46 versus 1** and the week recompute matched the committed outcome metrics.

The main weaknesses are not lack of engineering or fabricated results. They are a **timing trap that can make the judge's click do nothing**, the statistically overstrong **"seed number 21"** framing, and a presentation that hides important controls/evidence at the requested 1280x720. The three-minute script also makes the strongest long-horizon demonstration optional. These are fixable without running a new research programme.

### Does it meet the brief?

| Requirement / PLAYBOOK section 11 bar | Judgment |
|---|---|
| Rule baseline versus an agent that beats it after demand changes | **Yes, live.** Reactive and MPC see the same NYC requests; the synthetic judge-controlled shock gives an unmistakable counterfactual comparison. "Best rule" means best among the implemented rules, not the best possible allocator. |
| Look-ahead, rather than a renamed moving-average rule | **Yes.** The policy solves a time-expanded LP using queues, future releases of already-busy units, an OD model and an EWMA/time-of-day forecast. Only the current action is executed, then it replans. |
| Multi-agent system | **Yes in the centralized-coordination sense.** Forty units execute per-unit targets. The honest panel correctly says centralized planning, per-unit execution. This is not a demonstration of independent negotiating agents or a learned decentralized policy. |
| Shock plus drift in one run; long horizons | **Implemented and observed.** The week includes seven shocks, a migrating hotspot and spikes. The month is committed evidence, not a live month recompute. **Not actually shown by the mandatory three-minute script:** see issue 4. |
| Real first; synthetic labelled | **Pass.** NYC is the opening tab; the green bar says real demand / simulated fleet. Stress and week have conspicuous SYNTHETIC labels. Injected NYC demand is explicitly synthetic. |
| One-command/offline operation, first visual within 60 seconds | **Pass after the documented one-time dependency setup.** See measured timings below; do not imply a cold network installation itself completed within 60 seconds. |
| A compelling judge-operated knob | **Pass technically, qualified statistically.** The shock POST changes the trace and reruns both policies. The L/P knob changes the live simulator and planner, not just a picture. See issues 1-2. |
| Headless smoke and recorded fallback | **Pass, with provenance-copy defects.** Full smoke passed; file:// replay works; nine PNGs and the MP4 exist. See issue 5. |
| Every displayed result traceable | **Numeric copying passes.** All 26 evidence tables, 213 rows and 1,307 data cells matched the export; the export matched the committed source files. This does not validate every sentence around those numbers. |

## Execution record

Started with `git fetch origin && git rebase origin/main`. Used a real, gitignored `.venv` directory, not a symlink. The three requested compute commands started only after `memory_pressure` reported at least 30% free and ran under `nice -n 10`; no GPU was used. The server's background worker inherited niceness and raised it to 19.

| Operation | Observed result |
|---|---|
| `bash demo/setup_venv.sh`, once explicitly | **68.79 s wall**, memory guard **37%**. Python **3.11.14**, highspy **1.15.1**, NumPy **2.4.6**, SciPy **1.17.1**. `.venv/` was confirmed ignored and not symlinked. |
| `bash demo/smoke.sh`, full, not `--quick` | **31/31 checks passed in 105 s** according to the test; **107.49 s** external wall time. Memory guard **32%**. |
| Smoke NYC warm-up | **272** time-lapse frames in **8.3 s**. Window losses **[46, 1]** exactly matched replicate 200. |
| Smoke judge-injected NYC surge | Zones **[7, 8, 12, 13]**; first-hour losses **[45, 7]**. |
| Smoke synthetic fixed surge | Seed **7000**, L=1, P=10, zone **12**, onset **05:00**; first-120-minute losses **[160, 17]**. |
| Smoke whole-episode recomputes | NYC: **11.09 s**, 4 allocators; week: **63.58 s**, 3 allocators; shock-day parity also passed. |
| `bash demo/run.sh --no-open --port 8794` | Memory guard **37%**; actually bound **127.0.0.1:8794**; serving after **1.0 s**. |
| First visual, Chromium at **1280x720** | Server recorded **6.96 s after run.sh started**. This includes the tool-controlled delay before navigation. Navigation-to-drawn-city measurement including screenshot was **384 ms**; first contentful paint **96 ms**. The script's "about 3 s" is not a portability guarantee, but this run comfortably passed the 60-second bar. |
| Live server background recomputes | NYC **10.24 s**, 4/4 allocators; week **63.2 s**, 3/3 allocators; outcome parity passed. |
| Normal browser operation | No console errors or warnings before deliberate backend failure. July 4 fast-forward, observed surge, custom surge, stress, L=8/P=10, week and honest panel all exercised. |
| Raw-data cross-check | **Skipped by smoke:** `.data/nyc_tlc` was absent. The 62/3.0 claim was checked against the committed research note, not freshly re-derived from the raw parquet. The committed NPZ replay was executed. |
| Cleanup | Stopped the private server and its known child; port 8794 no longer responded. Closed the review browser page. No reviewer-started service was left running. |

I inspected all nine committed fallback screenshots. The MP4 is H.264, **1280x800**, **60.307692 s**, **2,606,773 bytes**. The ten fallback files total **5,431,461 bytes**, each below 10 MB and together below 15 MB. The screenshots are 1440x900, which helps explain why their layout looks more complete than the requested live 1280x720 viewport.

### My live interventions, not population estimates

Loss pairs below are **rule, planner**. These are individual trajectories, not additional confirmatory seeds.

| Scene | Exact observation |
|---|---|
| NYC at 22:00, before my intervention | Night-window losses **9, 0**; displayed cumulative service **97.4%, 99.8%**; empty hops/served **0.39, 0.36**; rolling LP median **3.6 ms**, top shadow price **0.56**. |
| NYC at 23:30, no intervention | Window **46, 1**, difference **45**; green match-to-replicate-200 message; LP median **2.1 ms**, top shadow price **0.33**. |
| NYC after natural completion | A click returned HTTP **200**, shock `t0=2880`, `end=2880`, **0** arrivals and **0** elapsed shock steps. It could not affect anything. |
| NYC, restarted for a meaningful click | Injected at **21:19**, zones **[7,8,12,13]**, size **1**, extra rate **1.2 per zone/min**, end **24:00**. At **22:19**, losses since my surge **63, 5**; night-window losses **61, 5**. Displayed saving **58**, explicitly live-only. LP median **1.2 ms**, top shadow price **1.74**. |
| Stress, L=1/P=10 | Seed **7000**, clicked zone **13**, block **[13,14,18,19]**, onset **04:04**, end **10:04**. At **06:04**, first-120-minute losses **227, 26** and dot **-201**. Dot completed in **15.416 s** at nominal **8 simulated min/s**. Service **89.8%, 97.6%**, empty hops **0.69, 0.61**, LP median **4.9 ms**, top shadow price **2.52**. |
| Stress, L=8/P=10 | Rule changed to **greedy**, with prediction **+16.3 losses**, service difference **-0.38 [-0.89, +0.04] pp (6/20)**. Same clicked zone/block, onset **04:00**, end **10:00**. At **06:00**, losses **554, 627**, dot **+73**, service **76.5%, 74.5%**, empty hops **0.31, 0.27**. A repeated live run reproduced the loss pair; rolling median was **12.8 ms**, versus **5.7 ms** during the first run, demonstrating contention/timing variability. Top shadow price **3.00**. |
| Week at day 7, 23:59 | Day service **43.9%, 80.6%, 88.9%** for greedy/reactive/planner; cumulative service **73.5%, 87.0%, 93.6%**. These are seed 200, not the larger text's 10-seed means. |

## Numbered issues and concrete fixes

The first five are the **top five fixes, ranked by impact**. Each issue is separately numbered for ACCEPTED/REJECTED triage.

### 1. P1 - The scripted handover can deliver a dead knob

**Evidence:** `demo/SCRIPT.md:4, 11-31`; `demo/engine.py:36, 237-256`; `demo/index.html:594-604` and `NYC_VIEW`. The page starts playing before the judges arrive. Once warm-up ends, only 165 simulated minutes remain; at the default 4 min/s that is **41.25 seconds**, or about 50 seconds including the measured warm-up. The script hands over the mouse at **1:00**, after showing the complete window. There is no automatic pause at the result or guard against injecting after the trace ends.

I reproduced a success-shaped but empty injection: `{"t0":2880,"end":2880,"window":120}`, HTTP 200, zero new requests. The screen still invited "Now you try: click any cell" while another label said the run had ended. This can erase the entire "crazy" moment even when the code is healthy.

**Fix:** start in an armed/paused state; auto-pause at the unperturbed result; make a conspicuous **"Your turn: restart at 21:15"** action start a separate, clearly labelled interactive run. Reject/disable zero-duration end-of-trace shocks. Do not extend the real trace by inventing extra taxi data. Explicitly script this handover.

### 2. P1 - "Your surge is seed number 21" is not a valid replication claim

**Evidence:** `demo/SCRIPT.md:42`; `demo/index.html:736-840`; `demo/engine.py:157`; `eval/results/phase-v2/config.json`. The grey dots are frozen **720-step** episodes with a randomly selected 2x2 block and onset in **04:12-06:36**. The live city has a **1440-step** horizon and permits an arbitrary, user-selected location, time and multiple overlapping shocks. My very first click happened at **04:04**, outside the displayed reference onset range, but the same headline and reference strip remained.

The **-201** live loss difference was genuine. What is unsupported is treating that intervention as another exchangeable seed in the 20-seed experiment, or treating the **+5.62 [+5.32,+5.93] pp** confidence interval on a population mean as a prediction interval for my intervention. The small-print onset disclosure is good, but it does not repair the spoken "seed 21" claim. The map's best-rule comparison is also explicitly exploratory in the registration.

**Fix:** say **"Your live intervention, alongside 20 reference runs; not a new test seed or a calibrated prediction for this location."** Preserve the prediction-first idea as an expectation from reference conditions, not a statistical guarantee. If literal seed-21 replication is desired, add a separate frozen-protocol mode with matching horizon, onset/block sampling, size and one-shock rule. Gate/reference-label off-protocol and overlapping interventions.

### 3. P2 - At 1280x720 the story-critical evidence and failure cell are below the fold

**Evidence:** `demo/index.html:32, 50, 57, 95-114`; reviewer captures `p7-live-02-observed-surge.png`, `p7-live-06-stress-prediction.png`. At the NYC result, the observed-surge copy extended to approximately **y=804**, below the **720-pixel** viewport and behind the independently scrolling sidebar/footer. In stress, the L/P grid occupied approximately **y=636-804** while the sidebar ended at **y=668**. L=8/P=10 was not initially visible. Clicking it required sidebar scrolling, which then hid the top controls.

The big loss counters work well, but cell labels are roughly 9 pixels and there is a lot of 12-13-pixel proof text. The 1440x900 fallback shots conceal this stage-layout problem.

**Fix:** build a 1280x720 stage layout: keep the active prediction, current intervention result and all eight L/P cells visible together; move secondary receipts/legends into a drawer. Keep the raw/real-data qualification next to the main result, not below the fold. Validate the actual projector viewport, not just the taller screenshots.

### 4. P2 - The three-minute script does not actually show the long-horizon stretch

**Evidence:** `demo/SCRIPT.md`, especially **2:30-3:00** and **"If asked about long horizons"**. The mandatory script goes directly from stress to the honest panel. The week, which visibly combines repeated shocks, drift and spikes, is only shown if a judge asks. A month is only a quoted number.

**Fix:** reserve a mandatory **20-30 seconds** for the already-prewarmed week. Show the day-7 three-policy result, distinguish the live bars from the 10-seed ticks, and say the month has **four** seeds. Trim verbal recitation of p-values, not the working stretch demonstration. Keep the honest close.

### 5. P2 - Recorded and committed material is repeatedly called "live"

**Evidence:** `demo/index.html:675-708, 896-904, 1022-1035`; `demo/SCRIPT.md:55`. The file:// fallback correctly showed a red RECORDED banner and disabled click injection, but simultaneously displayed:

- **"fast-forwarding, computed live"** during recorded playback;
- **"Window over, live"** and **"(live, final)"** on recorded window counters;
- **"rings: this live run"** under the recorded strip;
- **"recomputed live"** and **"Bars: this live run"** on the offline week, where there were **zero frames and no live bars**.

The scripted close **"Everything you saw was computed live"** is also false even in a healthy live session: the CIs, population dots, map and receipts are committed evidence. This is a wording/provenance MISMATCH, not evidence of fabricated results.

**Fix:** derive every status/counter/legend from a single explicit LIVE / RECORDED / COMMITTED provenance value. Close with **"The interventions and simulations were computed live; the reference distributions and confidence intervals are committed results."** In fallback mode, call the week a committed comparison or show the existing recorded week media, not an empty live scene.

### 6. P2 - The 62-pickup anomaly and 46-loss counter are different populations and windows

**Evidence:** `research/components/real-trace-replay.md`, `demo/data/nyc_jul03-04_r200.npz`, `demo/index.html` `nycSetup`/`NYC_VIEW`. **62 versus 3.0, 20.67x** is the **unthinned**, one-cell, 30-minute anomaly. The displayed simulation contains **13** pickups in that cell in that interval. The **46 versus 1** loss counter is over **all cells for two hours**, with **1,554** thinned arrivals, not losses from those 13 pickups alone. The rule was already at **9 losses versus 0** at 22:00.

The source values are VERIFIED, but the screen/talk should not invite a causal interpretation that 45 losses were saved in that one 62-pickup burst, or that the displayed request stream itself contains 62 such pickups.

**Fix:** label the anomaly **"raw TLC cell pickups, before thinning"** and the score **"fleet-wide losses, 21:30-23:30"**. Say this is an illustrative, retrospectively chosen demand window, not a causal estimate of the effect of one detected anomaly.

### 7. P2 - The shared "6 h" surge description is false for late NYC clicks

**Evidence:** `demo/index.html` `LiveView` size-control construction; `demo/engine.py:254-256`. The same size-control hint says **"+1.2 requests/min each, 6 h"** in both live tabs. The backend truncates at the trace horizon. My NYC click at **21:19** ended at **24:00**, so lasted **161 minutes**, not 360. No NYC click after the 21:15 warm-up can last six hours. The hint is visible in the supplied 1440x900 screenshots but hidden by the compact-height stylesheet in the requested 720-pixel viewport.

**Fix:** show the returned start/end and actual duration: **"up to 6 h; this replay ends at midnight."** In synthetic mode, also qualify late-day truncation. This is distinct from the zero-length injection in issue 1.

### 8. P2 - The ordinary-days evidence caption incorrectly imports the July-4 event

**Evidence:** `eval/results/nyc-v2b/summary.md:3`, exported verbatim into the honest panel. It correctly introduces July **10-11**, train July **8-9**, then says **"Event window = July 4 21:30-23:30"** and repeats the **20.7x** anomaly. The actual comparison's event-loss entries are dashes.

**Fix:** correct the source caption to state that this ordinary-days run has no July-4 event window, then regenerate `evidence.js`. The **+1.52 [+1.43,+1.59] pp, 20/20** result itself is not a mismatch.

### 9. P2 - "Bit-identical rows" is broader than the parity assertion

**Evidence:** `demo/engine.py:382-402`, `demo/index.html:896`, `demo/SCRIPT.md:55`. `served_frac` is compared with tolerance **1e-12**; shock/event losses and **five-decimal** daily fractions are checked where present. This is a good outcome-parity test, but it does not compare every column in `episodes.csv`, all request/unit trajectories, or the bits of the full engine state. Runtime measurements cannot be bit-identical.

**Fix:** say **"Matches the committed served-fraction and loss metrics; daily fractions match at committed precision."** Keep the named endpoints already shown on the week badge. The checked values really did match here; the concern is the breadth of the guarantee, not an observed outcome-parity failure.

### 10. P2 - Mid-demo backend loss has an error chip but no stage-safe recovery mode

**Evidence:** deliberately stopped my server, then resumed the browser. The chip said **"backend error: Failed to fetch"**, but the mode still said **"live · 1 run"** and the RECORDED banner remained hidden. `BACKEND` is established at boot; `pump()` retries after failures without a user-facing recovery transition.

**Fix:** pause on connection failure, explicitly mark the live computation stopped, and offer **Retry** and **Open recorded fallback**. Do not silently turn live results into canned results. The existing manual file:// and MP4 fallback remains adequate if the presenter practices the switch.

## Honesty audit: claims and numbers

**VERIFIED** below means matching a specific committed source and/or an observed live computation. It does not mean "causally established", "representative of unseen days", or "independently regenerated from raw TLC parquet." **MISMATCH/UNSUPPORTED** denotes the particular wording/scope, not fabricated arithmetic.

This ledger covers the talk track, the requested live journey, all nine fallback screenshots, and every table rendered by the honest panel. Continuously changing counters are audited by their definitions, source code, conservation/parity checks and named snapshots, rather than pretending one fixed value represents every playback frame. The complete 26-table transcription below lists the remaining displayed numeric values without cherry-picking.

### Claim ledger

| ID | Displayed / spoken claim or number | Status and exact source/value |
|---|---|---|
| C01 | Problem 7; two fleets of 40; 5x5 cells | **VERIFIED:** `demo/engine.py` has `N_AGENTS=40`, two `Panel`s; `demo/index.html` has `G=5`, `Z=25`; smoke checked two 40-unit, 25-cell frames. |
| C02 | Centralized planning, per-unit execution | **VERIFIED:** `components/policies/policies.py:MPCPolicy.act` calls the LP, then `flows_to_targets`; the honest panel states the centralization. No independent-agent negotiation is demonstrated. |
| C03 | LP re-solved every simulated minute; uses queues and units about to free up | **VERIFIED:** `Panel.step` -> `MPCPolicy.act` -> `MPCPlanner.solve`; `s.incoming(H)`, `s.queue_len`. Default horizon **6** at L=1, otherwise **L+6**; L=8 uses **14**. |
| C04 | Neither ordinary policy can see the unannounced surge beforehand | **VERIFIED:** non-oracle policy metadata has `rates=None`; click injection changes only requests at/after current backend time; FIFO prefixes are asserted unchanged. NYC's highlighted event window is presentation metadata, not input to EWMA. No default-planner pre-positioning before an unforeseeable click was claimed/proved by the computation. |
| C05 | Learned daily cycle and drift | **VERIFIED with scope:** `EWMAForecaster` learns/uses a historical daily profile and updates per-zone levels with **alpha=0.05**. It **tracks** drift; it does not learn an explicit migration direction or extrapolate a trend. Avoid expanding the copy into "predicted this surprise". |
| C06 | Same requests on both sides | **VERIFIED:** shared `DemandTrace`, identical request destinations, and a per-step arrivals equality assertion in `LiveRun._step`; smoke checks request conservation. |
| C07 | Best rule: reactive on NYC; reactive at L=1/P=10; greedy at L=8/P=10 | **VERIFIED:** `nyc-v2/summary.md` and `phase-v2/phase_summary.csv`. Phase reference is selected by test-set mean and is exploratory; the confirmatory footer instead uses a rule fixed on tuning seeds. |
| C08 | Reactive uses last 30 minutes; greedy is local; static uses history | **VERIFIED:** `ReactivePolicy(window=30)`, `GreedyPolicy` 4-neighbour unmet-queue rule, `StaticPolicy` historical shares. |
| C09 | July 2025 public NYC TLC demand; Manhattan-internal; simulated fleet, travel, matching and patience | **VERIFIED against committed adapter/research/export:** `components/scenarios/nyc_tlc.py`, `real-trace-replay.md`, `export_nyc.py`. No operational taxi deployment or real road-travel validation is shown. |
| C10 | July 3-4 replay, trained on July 1-2, replicate 200 | **VERIFIED:** NPZ `info.test_days`, `train_days`, `seed=200`; **2,880** time steps and **28,636** actual exported requests. |
| C11 | Thinned to approximately 10 requests/min | **VERIFIED:** committed research `q=0.2012958420`; NPZ q **0.20129584198276404**; raw two-day rate **49.678125/min**; full-month kept fraction **0.7817922355251896**. This replicate is approximately **9.94/min**. |
| C12 | Fast-forward July 3 00:00 to July 4 21:15; about 5-15 seconds | **VERIFIED for live run:** `NYC_START=2715`; measured **8.3 s**, **272** sparse frames in smoke. The performance range is machine/load-dependent. **MISMATCH** when the same "computed live" label is used in file:// mode, issue 5. |
| C13 | First visual about 3 seconds | **UNSUPPORTED as an independently measured 3-second result here:** `SCRIPT.md` gives an approximate expectation; measured server readiness **1.0 s**, first visual **6.96 s** including orchestration delay, navigation-to-visual **384 ms**. The delay prevents a clean launch-only comparison. Fresh one-time setup **68.79 s** is separate. |
| C14 | 62 pickups versus 3.0, 20.67x, cell 3 / Two Bridges, 22:00-22:30 | **VERIFIED:** rank 1 in `real-trace-replay.md`; **62/3 = 20.666...**. These are raw counts; replay count is **13**, issue 6. Mapping cell **3** is bottom row, fourth cell because the renderer flips north/south. |
| C15 | Cause UNVERIFIED; not told about July 4 | **VERIFIED as an honest limitation:** no cause is assigned by the research/adapter; ordinary forecasts use training metadata and subsequent observed counts. Do not say "fireworks caused this." |
| C16 | Night window July 4 21:30-23:30; 46 reactive versus 1 planner | **VERIFIED:** `nyc-v2/episodes.csv`, seed **200**, `event_lost`; recomputed live and smoke. **45** fewer losses; whole-fleet, **120-minute** endpoint. |
| C17 | Mean window losses planner 1.40 / reactive 39.55 / greedy 111.90 / static 218.10 | **VERIFIED:** means of `nyc-v2/episodes.csv:event_lost`, **20** rows per policy. `summary.md` displays **1.4 / 39.5 / 111.9 / 218.1** at lower precision; this is not a mismatch. |
| C18 | NYC +2.52 [+2.39,+2.67] pp, 20/20 | **VERIFIED:** `nyc-v2/summary.md`, `mpc-ewma - reactive`, whole two-day served fraction; Wilcoxon **1.9e-06**. Window-loss paired difference **-38.1 [-42.4,-33.9]**. |
| C19 | Ordinary days July 10-11: +1.52 [+1.43,+1.59] pp, 20/20 | **VERIFIED:** `nyc-v2b/summary.md`, train **July 8-9**, seeds **200-219**, Wilcoxon **1.9e-06**. The appended July-4 event caption is a **MISMATCH**, issue 8. |
| C20 | Twenty replicates / grey dots | **VERIFIED:** seeds **200-219**, not twenty independent dates or cities. Exact dot values are in the per-seed appendix. NYC chart's **67 lost** upper label is a derived axis limit: max **60**, padded to **66.8**, rounded. |
| C21 | "Now you try"; live synthetic demand added to real demand; no committed NYC intervention evidence | **VERIFIED when time remains:** `inject_shock`, `LiveRun.shock`, observed changed loss counts. **MISMATCH** as an always-actionable instruction after midnight, issue 1. |
| C22 | Surge x1: 2x2 block, +3 times zone-average rate, +1.2/min per zone, 6 h | **VERIFIED for an untruncated synthetic shock:** **3 * 10 / 25 = 1.2**, duration **360** minutes; user controls **0.5, 1, 2**, hence extras **0.6, 1.2, 2.4**. NYC filters out non-demand cells and truncates at midnight; unqualified **6 h** is a **MISMATCH**, issue 7. |
| C23 | Stress L/P map: L=1,2,4,8; P=3,10 | **VERIFIED:** `phase-v2` and live configuration. L is repositioning minutes per hop; P is patience. The complete eight-cell means/CIs/wins are transcribed below. |
| C24 | At L=1/P=10: -126.8 lost; +5.62 [+5.32,+5.93] pp, 20/20 | **VERIFIED:** `phase-v2/summary.md`; loss endpoint first **120** minutes, service endpoint whole **720-step** episode. **UNSUPPORTED as a calibrated forecast for any arbitrary click**, issue 2. |
| C25 | L=8/P=10: no reliable gain, -0.38 [-0.89,+0.04] pp, 6/20; +16.3 losses | **VERIFIED:** `phase-v2/summary.md`. "No reliable gain" is not "proven zero effect" or "always loses." My live example did lose: **+73**. |
| C26 | "Your surge is seed number 21" | **UNSUPPORTED:** live seed **7000**, user-chosen block/onset, **1440**-step horizon versus the **720**-step random-shock reference. It is not appended to the committed experiment. Issue 2. |
| C27 | Yellow dot after 120 minutes, about 15 seconds | **VERIFIED:** `WIN=120`, default stress **8 min/s**; measured **15.416 s**. Key **3** selects **30 min/s** for stress, whose ideal playback time is **4 s**, subject to compute. At that speed the recorded 15-second expectation is no longer the ideal duration. |
| C28 | Demo seeds 7000+; reserved 300-329 untouched | **VERIFIED within committed episode evidence and registration:** scan found maximum result seed **229**, no **300-329** or **7000+** result rows; new-city control increments seed. NYC is explicitly replicate **200**, not a fresh demo seed. |
| C29 | Pre-registered 30 fresh seeds, +3.73 shock / +5.47 shock+drift / +5.99 shock+drift+spikes pp, 30/30 each, Holm p=1.1e-08 | **VERIFIED:** `mvp-v2/confirm.md`, seeds **200-229**, **1440 episodes**, horizon **1440**, K=40, P=10. Exact CIs **[+3.28,+4.20] / [+5.36,+5.59] / [+5.82,+6.15]**. Registration `6e58813` precedes results commit `11ad5bf`; reference chosen on tuning seeds **0-19**. These are simulator claims. |
| C30 | Queue-only did better under a pure shock: +1.19 pp | **VERIFIED:** confirm S1 **+1.19 [+1.06,+1.32] pp**, **30/30**; first-window loss difference **-62.30 [-70.47,-53.83]**, **0/30** increases, Holm **1e-05** for loss endpoint. This limits the forecast-value claim, not the look-ahead-versus-rule claim. |
| C31 | Perfect forecast can hurt: 3 of 4 long-lead cells | **VERIFIED for this LP/model:** phase true-rate minus EWMA at (4,3) **-1.09 [-1.67,-0.57] (3/20)**; (8,3) **-1.49 [-1.98,-0.99] (2/20)**; (8,10) **-1.10 [-1.45,-0.75] (1/20)**. Remaining long-lead cell (4,10) **+0.19 [+0.08,+0.28] (15/20)**. Not a general theorem that accurate information hurts optimal control. |
| C32 | Oracle is an upper bound | **NOT CLAIMED on the reviewed screens/script.** Synthetic oracle is the same approximate MPC with true expected rates, not a hindsight optimum. NYC oracle is a retrospective **15-minute centred smoother**. Advanced live oracle explicitly loses advance notice of a judge's click and is not bridged to committed oracle trials. |
| C33 | Pre-registered change-detector hypothesis did not replicate | **VERIFIED:** phase H1, Holm over **8** cells; the apparent benefit at (2,3) has Holm **0.25**; harm at (1,10) **+4.4 [+2.0,+6.8]**, Holm **0.026**, and (8,10) **+21.9 [+11.5,+31.6]**, Holm **0.011**. |
| C34 | Amber is LP shadow value of one more idle unit, not market price | **VERIFIED:** `components/planner/mpc.py:135,143,159`, negated first-step supply-row duals; renderer shades relative to median/max. Not dollars, a learned price, or a separately executed market auction. |
| C35 | A week: seven days / seven shocks / drift / spikes, seed 200 | **VERIFIED:** scenario **10080** steps, **7** shocks, **7*24=168** transient spikes; live batch uses greedy/reactive/MPC. Display speed **420 simulated min/s**. |
| C36 | Greedy 0.910 -> 0.466; planner 0.960 -> 0.912 | **VERIFIED:** `long-week-v2/summary.md` per-day **means over ten seeds**, not seed 200's bars. Reactive means **0.906 -> 0.832**. |
| C37 | Week +6.34 [+6.26,+6.43] pp, 10/10; -131.7 losses/shock | **VERIFIED:** week summary, MPC versus reactive, seeds **200-209**, Wilcoxon **0.00195**. Greedy/planner mean whole-run service **0.7242 / 0.9356** in the episode-weighted table. |
| C38 | Month +6.37 pp | **VERIFIED but exploratory/small n:** month summary **+6.37 [+6.29,+6.44]**, **4/4**, **43200** steps, **30** shocks, seeds **200-203**, Wilcoxon **0.125**. Do not describe it as an independently significant large-sample result. |
| C39 | NYC/week reproduce rows bit for bit | **VERIFIED for named outcome metrics, UNSUPPORTED as whole-row/trajectory bit identity:** issue 9. No observed mismatch in the checks actually performed. |
| C40 | Live values are one run; committed numbers have paired 95% CIs | **VERIFIED as the intended distinction.** Differences have paired CIs; descriptive per-policy averages and raw per-seed dots are not themselves paired-effect estimates. The wording should not turn either into a live-run confidence interval. |
| C41 | Half-trust / queue-only / true-rate advanced choices | **VERIFIED code paths:** forecast multipliers **0.5 / 0 / true rates**, with changed LP input; source `MPCPolicy.act`, `bridge`. Unmatched combinations and x0.5/x2 surges are labelled live-only. The exploratory trust sweep's full values are below. |
| C42 | Playback keys 1-4, space, r; speed numbers | **VERIFIED:** NYC **2,4,8,30**; stress **2,8,30,120**; space pauses, r restarts live current tab; controls are simulated minutes/second, not guaranteed throughput. |
| C43 | RECORDED fallback; clicks off; 60-second video | **VERIFIED functionality:** file:// `BACKEND=false`, conspicuous banner, clicking added no shock. Video **60.307692 s**. Mixed "live" text remains a **MISMATCH**, issue 5. |
| C44 | Every visible number computed live or copied from committed results; sources on hover | **VERIFIED for the data pipeline**, including all rendered evidence cells and raw per-seed exports. Some values are explicitly derived means, axes or live accumulations, not verbatim table strings. Literal "Everything ... computed live" is a **MISMATCH**, issue 5. |

### Definitions behind changing visual quantities

`LiveView.apply` accumulates the returned per-minute arrivals, served, lost and empty moves. Service is cumulative served divided by cumulative arrivals, including the warm-up base; empty hops/served uses the corresponding cumulative numerator and denominator. Since-surge loss starts at the backend-returned onset. The dot instead stops counting at **120 minutes**, so a later since-surge counter need not equal it. Window losses are fleet-wide expirations occurring in the window, not a cohort survival calculation for arrivals in one highlighted cell.

The LP median label uses the most recent **30** returned solve times; it is not a full-run benchmark or an SLA. Top shadow price is the maximum current supply-row dual. Queue squares and red loss counts come from each panel's current queues/losses. White request pings use the common arrivals. NYC labels/tooltips come from committed zone mapping plus NPZ training-pickup rankings, not from learned test-day geography.

### Fallback screenshot numeric inventory

The following transient readings are **VERIFIED as the contents of the named committed PNGs**, not re-run here at every exact original screenshot instant. Runtime milliseconds are historical captures, not today's timings or general performance promises. Their reusable population claims are independently covered by the ledger and table appendix.

| PNG in `demo/fallback/` | Transient values visible, apart from already-audited reference text |
|---|---|
| `01-july4-fast-forward.png` | **Thu 3 Jul 16:50**, **37%** warm-up, speed **4**, service **97.1%, 99.9%**. Loss and empty-hop fields not yet populated. |
| `02-july4-surge-live.png` | **Fri 4 Jul 22:14**, losses **16,0**, service **97.4%,99.8%**, hops **0.39,0.36**, saving **16**, median **2.6 ms**, top dual **0.74**. |
| `03-july4-window-result.png` | **Fri 4 Jul 23:38**, speed **8**, losses **46,1**, service **97.4%,99.8%**, hops **0.39,0.36**, saving **45**, median **2.6 ms**, top dual **0.59**. |
| `04-july4-now-you-try.png` | **Fri 4 Jul 22:12**, losses **14,5**, service **97.1%,99.7%**, since-surge **14,5**, saving **9**, median **5.1 ms**, top dual **1.07**. Cell-7 tooltip training counts: **12202,8312,6622,6341,5128,4128,2988,2416,2062**, in displayed zone order. |
| `05-stress-prediction-first.png` | **04:12**, seed **7000**, speed **8**, L=1/P=10; losses **0,0**, service **96.8%,99.0%**, hops **0.64,0.55**, median **3.5 ms**, top dual **0.58**. |
| `06-stress-your-surge-is-seed-21.png` | **06:46**, onset **04:18**, speed **30**, seed **7000**; since-surge losses **256,72**, service **91.2%,97.0%**, hops **0.65,0.58**, saving since onset **184**, first-120-minute dot **-149**, median **8.0 ms**, top dual **2.19**. The **184 versus 149** is different endpoint duration, not an arithmetic contradiction. |
| `07-stress-L8-P10-no-reliable-gain.png` | **04:18**, L=8/P=10, seed **7000**; no surge yet, losses since 04:00 **7,15**, service **89.4%,89.6%**, hops **0.35,0.29**, median **16.6 ms**, top dual **2.20**. |
| `08-week-greedy-collapses.png` | **Day 7 23:59**, seed **200**; day service **43.9%,80.6%,88.9%**, run service **73.5%,87.0%,93.6%**, recompute **60.12 s**, **10080** minutes x **3** allocators. Bar axis **0.4,0.6,0.8,1.0**, days **1-7**. |
| `09-evidence-honest-panel.png` | No new live-performance estimate: honest-limit claims and the first NYC tables, fully transcribed below. |

## Robustness and fallback judgment

| Threat | What is established, and what remains a rehearsal risk |
|---|---|
| Port collision | Current run really used 8794. `server.bind` tries the requested port and the next **19**, even when a port was explicitly supplied. Read the printed URL; a presenter hard-coding an occupied URL can hit the wrong page. Smoke uses an ephemeral port. Collision was inspected in code, not induced on another user's process. |
| Slow cold setup / missing Python / network | Setup needs network once and Python 3.11 or uv. It took 68.79 seconds here. Prepare the real venv before going on stage; after setup the demo fetched no external UI assets. |
| CPU contention | Warm-up is visibly labelled and background batches are separate niced processes. Observed week times were 63.2-63.58 seconds. L=8 rolling medians changed substantially across runs. The speed button is a target, not guaranteed wall-clock progress. |
| Script timing | The actual hard failure is issue 1, not merely a slower laptop. Do not leave the NYC scene playing while waiting for the judge to arrive. |
| Browser / projector | Tested Chromium at 1280x720. No Safari/Firefox result is claimed. Canvas has a roundRect fallback, but that is not cross-browser testing. The main observed usability failure is issue 3. |
| Connection loss after load | Explicit error chip observed; no automatic recorded-mode transition or recovery CTA. Issue 10. Deliberate outage caused console fetch errors; normal operation did not. |
| Too many tabs / restarts | Server retains at most **six** live sessions; older ones can expire. Keep one presentation tab. This is a documented-by-code bounded-memory tradeoff, not a failure observed in the prescribed single-tab flow. |
| Truly offline / Python unavailable | file:// replay worked, disabled injection and showed RECORDED. The week then showed committed ticks but no animated units/bars. Use screenshot 08 or the MP4 for the stretch. Correct the contradictory copy in issue 5. |
| Media fallback | All nine screenshots inspected; the short H.264 MP4 exists and has valid metadata. These are adequate to finish a presentation, not to claim the judge's new knob is live. I did not watch/decode every MP4 frame. |

## The three hardest live questions, with honest answers

### Q1. "You said look-ahead. Did you know about my surge, and why not just use the queue-only planner?"

**Answer:** "We did not know its arrival time or location. Both policies get the same requests only when they arrive. The planner looks ahead over the travel/release delay using the current queues, known releases of busy units and a learned daily pattern. The forecast is adaptive, not clairvoyant. Under our pre-registered pure-shock simulation, queue-only actually served **1.19 pp more** than the EWMA planner and lost **62.30 fewer requests** in the first shock window. Under shock plus drift, EWMA beat queue-only by **0.37 pp**; under the NYC replay it beat queue-only by **0.47 pp**. Our demonstrated claim is that coordinated look-ahead beats the chosen rule baselines, not that forecasting always helps."

### Q2. "Why should I trust this dot or these twenty wins? Is this a held-out prediction for my click?"

**Answer:** "No. Your click is an exploratory intervention in a fresh demo stream, not automatically another identically distributed test seed. Those dots are frozen reference runs under a specified random-shock protocol. The NYC twenty are thinning replicates of the same two days, not twenty different nights. We show a second ordinary-days replay, but that is still limited date coverage. The stronger confirmatory simulator comparison froze the baseline on tuning seeds, then used **30** fresh seeds and Holm correction. The CIs on those means are not prediction intervals for an arbitrary user-selected shock."

### Q3. "Is this really multi-agent, what does the amber price mean, and what would survive deployment?"

**Answer:** "It is a central coordinator assigning actions to **40** resource units, not forty independent learned negotiating agents. Amber is the LP marginal value of another idle unit at a location, not a dollar price. Real taxi pickups are replayed through a **5x5**, same-zone-matching simulator with simplified travel and patience, so these are not measured NYC operating savings. Movement is a genuine tradeoff: under the pure-shock experiment default MPC used **0.511** empty hops per served request versus greedy's **0.326**. With move-cost weight **0.5**, it used **0.413**, served **+3.16 pp** versus greedy, and still used **+0.087** more empty hops per served request. The month has only **four seeds** and Wilcoxon **p=0.125**. We would next validate the dispatcher under realistic travel, pickup matching and capacity/cost constraints rather than extrapolate this score into a deployment claim."

## Exact per-seed dot inventory

**VERIFIED:** values below were read from committed episode CSV exports and matched the displayed dot arrays. Each array is ordered by seed **200,201,...,219**. Synthetic values are planner minus best-rule losses in the first 120 minutes. They are not served-fraction differences.

```text
NYC reactive: [46,38,43,36,29,35,36,42,44,35,35,40,48,45,55,16,49,31,60,28]
NYC planner:  [1,3,0,0,4,2,0,2,1,0,3,0,1,1,3,0,3,0,2,2]

L=1 P=3  reactive: [-211,-186,-207,-175,-219,-195,-232,-215,-223,-202,-186,-220,-193,-194,-190,-201,-201,-158,-230,-215]
L=1 P=10 reactive: [-146,-125,-90,-86,-132,-96,-117,-148,-181,-126,-140,-158,-107,-128,-107,-130,-156,-83,-174,-107]
L=2 P=3  reactive: [-184,-174,-119,-131,-171,-133,-153,-158,-167,-156,-134,-209,-152,-151,-213,-201,-179,-127,-204,-138]
L=2 P=10 greedy:   [-167,-141,-202,-219,-268,-179,-161,-233,-306,-188,-199,-114,-269,-119,-41,-119,-200,-177,-243,-202]
L=4 P=3  greedy:   [-152,-235,-158,-188,-164,-90,-191,-147,-151,-100,-145,-158,-121,-157,-124,-136,-200,-115,-178,-195]
L=4 P=10 greedy:   [-24,-38,-63,-63,-124,-24,-59,-174,-70,-73,-85,-25,-95,-33,-38,-69,-56,-18,-98,-53]
L=8 P=3  greedy:   [-40,-95,-94,-142,-69,-67,-80,24,55,-111,-93,-149,-65,-152,-101,-106,-29,-91,-74,-101]
L=8 P=10 greedy:   [68,-13,15,35,-9,11,-1,121,54,2,-5,43,9,-22,6,14,11,-19,-25,31]
```

Week seed-200 bar heights, days **1-7**, from `long-week-v2/episodes.csv:daily_served`, also reproduced by the live worker:

```text
greedy:   [0.91978,0.89801,0.84019,0.73582,0.63289,0.68246,0.43923]
reactive: [0.90653,0.91261,0.87685,0.87409,0.86019,0.85472,0.80628]
planner:  [0.96929,0.98131,0.93064,0.93376,0.92521,0.92340,0.88880]
```

## Reviewer screenshot record

Reviewer-created screenshots are retained in this session's `files/` directory, not committed as additional repository files: session state **326ddbe5-f3aa-495b-ab58-f5681fd970d5**.

`p7-live-01-first-visual.png`; `p7-live-02-observed-surge.png`; `p7-live-03-window-result.png`; `p7-live-04-ended-click.png`; `p7-live-05-judge-nyc-surge.png`; `p7-live-06-stress-prediction.png`; `p7-live-07-stress-judge-dot.png`; `p7-live-08-L8-P10.png`; `p7-live-09-L8-judge-dot.png`; `p7-live-10-week.png`; `p7-live-11-honest-panel.png`; `p7-live-12-backend-stopped.png`; `p7-offline-01-recorded-fast-forward.png`; `p7-offline-02-recorded-result.png`; `p7-offline-03-week-fallback.png`.

## Complete displayed evidence-table inventory

All **26** tables below are **VERIFIED numeric/text copies of their named source tables at the reviewed commit**: **213 data rows, 1,307 data cells**. Browser DOM comparison found **zero** differing tables; `demo.export_evidence --check` passed. This is source-fidelity verification, not an independent reanalysis of every bootstrap or p-value. The actual caption mismatch in issue 8 remains a mismatch even though the exporter faithfully copied it.

The source-table transcriptions preserve their original numeric precision, signs, empty entries and comparison labels. They are included to make the requested every-number audit inspectable without promoting only favorable rows.

<details>
<summary>E1. NYC July 3-4: two tables, all values VERIFIED against nyc-v2/summary.md</summary>

Source: `eval/results/nyc-v2/summary.md`. July 3-4 2025, train July 1-2; 20 thinning replicates, seeds 200-219; K=40, P=10, L=1; displayed mean arrivals 28775. The event is July 4 21:30-23:30, with the raw 20.7x cell anomaly at 22:00-22:30. Cause unverified; NYC oracle is the retrospective 15-minute centred smoother, not a bound.

| policy | served_frac | lost_frac | mean_wait | empty_per_srv | event_lost | event_served | pending_frac |
|---|---|---|---|---|---|---|---|
| greedy | 0.9526 | 0.0449 | 2.4754 | 0.2518 | 111.9 | 0.9114 | 0.0025 |
| mpc-cusum-v1 | 0.9978 | 0.0016 | 0.7663 | 0.3531 | 1.8 | 0.9950 | 0.0006 |
| mpc-ewma | 0.9981 | 0.0015 | 0.7389 | 0.3640 | 1.4 | 0.9962 | 0.0004 |
| mpc-queue | 0.9934 | 0.0051 | 1.8532 | 0.2640 | 22.9 | 0.9779 | 0.0015 |
| oracle | 0.9981 | 0.0016 | 0.7097 | 0.3533 | 0.3 | 0.9972 | 0.0003 |
| reactive | 0.9729 | 0.0264 | 1.5286 | 0.3938 | 39.5 | 0.9700 | 0.0007 |
| static | 0.9360 | 0.0624 | 2.0154 | 0.3308 | 218.1 | 0.8475 | 0.0016 |

Best rule by mean: reactive.

| comparison | Δ served (pp) [95% paired CI] | replicates won | Wilcoxon p | Δ event lost [95% CI] |
|---|---|---|---|---|
| mpc-ewma − reactive | +2.52 [+2.39, +2.67] | 20/20 | 1.9e-06 | -38.1 [-42.4, -33.9] |
| mpc-queue − reactive | +2.05 [+1.92, +2.20] | 20/20 | 1.9e-06 | -16.7 [-21.3, -12.0] |
| mpc-cusum-v1 − mpc-ewma | -0.03 [-0.04, -0.02] | 1/20 | 0.00016 | +0.3 [-0.1, +0.9] |
| mpc-queue − mpc-ewma | -0.47 [-0.52, -0.42] | 0/20 | 1.9e-06 | +21.4 [+18.7, +24.2] |
| oracle − mpc-ewma | -0.00 [-0.01, +0.01] | 10/20 | 0.65 | -1.1 [-1.6, -0.5] |

</details>

<details>
<summary>E2. NYC July 10-11: two tables, values VERIFIED; event caption MISMATCH</summary>

Source: `eval/results/nyc-v2b/summary.md`. July 10-11 2025, train July 8-9; 20 thinning replicates, seeds 200-219; K=40, P=10, L=1; displayed mean arrivals 28743. **Issue 8:** the caption also repeats "Event window = July 4 21:30-23:30" and the 20.7x anomaly at 22:00-22:30. That portion is not a description of the ordinary-days run.

| policy | served_frac | lost_frac | mean_wait | empty_per_srv | pending_frac |
|---|---|---|---|---|---|
| greedy | 0.9605 | 0.0364 | 2.3080 | 0.2494 | 0.0031 |
| mpc-cusum-v1 | 0.9995 | 0.0001 | 0.5528 | 0.3334 | 0.0004 |
| mpc-ewma | 0.9995 | 0.0000 | 0.5312 | 0.3425 | 0.0004 |
| mpc-queue | 0.9958 | 0.0028 | 1.6311 | 0.2529 | 0.0014 |
| oracle | 0.9997 | 0.0000 | 0.5130 | 0.3319 | 0.0003 |
| reactive | 0.9843 | 0.0149 | 1.1524 | 0.3628 | 0.0007 |
| static | 0.9570 | 0.0410 | 1.6202 | 0.3177 | 0.0020 |

Best rule by mean: reactive.

| comparison | Δ served (pp) [95% paired CI] | replicates won | Wilcoxon p | Δ event lost [95% CI] |
|---|---|---|---|---|
| mpc-ewma − reactive | +1.52 [+1.43, +1.59] | 20/20 | 1.9e-06 | — |
| mpc-queue − reactive | +1.14 [+1.07, +1.21] | 20/20 | 1.9e-06 | — |
| mpc-cusum-v1 − mpc-ewma | -0.00 [-0.01, +0.01] | 6/20 | 0.53 | — |
| mpc-queue − mpc-ewma | -0.37 [-0.41, -0.35] | 0/20 | 1.9e-06 | — |
| oracle − mpc-ewma | +0.02 [+0.01, +0.02] | 18/20 | 0.00029 | — |

</details>

<details>
<summary>E3. L/P phase map: four tables, all values VERIFIED against phase-v2/summary.md</summary>

Source: `eval/results/phase-v2/summary.md`. Shock, horizon 720, units 40; seeds 200-219, CRN. Service differences are percentage points; mean, paired-bootstrap 95% CI and seeds won/n. "Best rule" comparisons are exploratory.

| L | P | best rule (served) | mpc-ewma | look-ahead vs best rule | detector vs EWMA | true-rate forecast vs EWMA | queue-only (no forecast) vs EWMA | myopic (H=L+1) vs EWMA |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 | reactive (0.746) | 0.844 | +9.82 [+9.57, +10.09] (20/20) | -0.19 [-0.29, -0.10] (3/20) | +0.15 [+0.06, +0.23] (16/20) | -10.05 [-10.75, -9.43] (0/20) | -1.46 [-1.70, -1.24] (0/20) |
| 2 | 3 | reactive (0.657) | 0.726 | +6.88 [+6.54, +7.22] (20/20) | +0.09 [-0.12, +0.30] (11/20) | +0.41 [+0.22, +0.60] (17/20) | -17.78 [-19.11, -16.49] (0/20) | -4.04 [-4.64, -3.54] (0/20) |
| 4 | 3 | greedy (0.530) | 0.610 | +7.94 [+7.41, +8.44] (20/20) | -0.98 [-1.45, -0.57] (3/20) | -1.09 [-1.67, -0.57] (3/20) | -14.27 [-15.73, -12.84] (0/20) | -2.72 [-3.42, -2.05] (0/20) |
| 8 | 3 | greedy (0.441) | 0.495 | +5.41 [+4.57, +6.18] (20/20) | -1.55 [-2.07, -1.06] (1/20) | -1.49 [-1.98, -0.99] (2/20) | -4.93 [-5.62, -4.31] (0/20) | -0.55 [-0.94, -0.22] (5/20) |
| 1 | 10 | reactive (0.863) | 0.920 | +5.62 [+5.32, +5.93] (20/20) | -0.15 [-0.26, -0.04] (3/20) | -0.21 [-0.31, -0.10] (5/20) | +1.52 [+1.27, +1.78] (20/20) | -1.87 [-2.08, -1.67] (0/20) |
| 2 | 10 | greedy (0.825) | 0.875 | +4.94 [+4.20, +5.72] (20/20) | -0.02 [-0.17, +0.10] (12/20) | +0.08 [-0.07, +0.24] (13/20) | -0.00 [-0.25, +0.23] (10/20) | -1.59 [-1.86, -1.33] (0/20) |
| 4 | 10 | greedy (0.789) | 0.812 | +2.27 [+1.84, +2.75] (20/20) | -0.01 [-0.11, +0.10] (8/20) | +0.19 [+0.08, +0.28] (15/20) | -4.32 [-5.02, -3.71] (0/20) | -1.43 [-1.72, -1.18] (0/20) |
| 8 | 10 | greedy (0.713) | 0.709 | -0.38 [-0.89, +0.04] (6/20) | -0.78 [-1.07, -0.48] (3/20) | -1.10 [-1.45, -0.75] (1/20) | -9.67 [-10.65, -8.73] (0/20) | +0.09 [-0.15, +0.33] (11/20) |

Requests lost in the 120 steps after shock onset, mean paired difference; negative means fewer lost.

| L | P | look-ahead vs best rule | detector vs EWMA | true-rate forecast vs EWMA | queue-only (no forecast) vs EWMA | myopic (H=L+1) vs EWMA |
|---|---|---|---|---|---|---|
| 1 | 3 | -202.7 | +4.0 | -11.8 | +260.4 | +54.1 |
| 2 | 3 | -162.7 | -9.3 | -29.8 | +370.9 | +119.0 |
| 4 | 3 | -155.2 | +16.8 | +11.9 | +277.4 | +67.7 |
| 8 | 3 | -79.0 | +25.9 | +16.5 | +101.2 | +8.2 |
| 1 | 10 | -126.8 | +4.4 | +1.9 | -3.6 | +61.9 |
| 2 | 10 | -187.3 | -0.6 | -6.5 | +23.2 | +63.8 |
| 4 | 10 | -64.1 | -1.8 | -14.8 | +80.2 | +51.5 |
| 8 | 10 | +16.3 | +21.9 | +20.6 | +148.8 | -6.0 |

Pre-registered H1: detector minus EWMA first-120-step losses, paired-bootstrap 95% CI, Wilcoxon and Holm over eight cells.

| L | P | Δ lost per shock [95% CI] | seeds where detector lost fewer | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| 1 | 3 | +4.0 [-0.1, +8.0] | 8/20 | 0.11 | 0.34 |
| 2 | 3 | -9.3 [-17.2, -1.4] | 13/20 | 0.044 | 0.25 |
| 4 | 3 | +16.8 [+3.9, +30.4] | 7/20 | 0.042 | 0.25 |
| 8 | 3 | +25.9 [+5.2, +49.3] | 5/20 | 0.056 | 0.25 |
| 1 | 10 | +4.4 [+2.0, +6.8] | 5/20 | 0.0037 | 0.026 |
| 2 | 10 | -0.6 [-5.9, +4.7] | 11/20 | 0.95 | 0.95 |
| 4 | 10 | -1.8 [-7.4, +4.2] | 12/20 | 0.34 | 0.69 |
| 8 | 10 | +21.9 [+11.5, +31.6] | 3/20 | 0.0013 | 0.011 |

Share of true-rate served-fraction gain captured; ratio of mean paired gains with joint seed-bootstrap 95% CI. Dashes indicate a non-reliably-positive denominator gain.

| L | P | true-rate − EWMA (pp) | detector arm captures | matched-α EWMA captures |
|---|---|---|---|---|
| 1 | 3 | +0.15 | -133% [-387%, -55%] | — |
| 2 | 3 | +0.41 | 22% [-41%, 66%] | — |
| 4 | 3 | -1.09 | — | — |
| 8 | 3 | -1.49 | — | — |
| 1 | 10 | -0.21 | — | — |
| 2 | 10 | +0.08 | — | — |
| 4 | 10 | +0.19 | -5% [-86%, 45%] | — |
| 8 | 10 | -1.10 | — | — |

</details>

<details>
<summary>E4. Week: three tables, all values VERIFIED against long-week-v2/summary.md</summary>

Source: `eval/results/long-week-v2/summary.md`. Seven simulated days, 10080 steps, seven shocks; seeds 200-209, CRN; units 40, P=10, L=1.

| policy | served fraction [95% CI over seeds] | lost per shock (120-step window) | recover steps | mean wait |
|---|---|---|---|---|
| greedy | 0.7242 [0.7185, 0.7296] | 713.0 | 112.3 | 3.71 |
| mpc-cusum-v1 | 0.9342 [0.9303, 0.9384] | 295.9 | 85.0 | 2.09 |
| mpc-ewma | 0.9356 [0.9315, 0.9398] | 290.3 | 84.4 | 2.10 |
| mpc-queue | 0.9306 [0.9273, 0.9340] | 261.1 | 66.7 | 3.06 |
| oracle | 0.9350 [0.9310, 0.9392] | 291.8 | 83.5 | 2.03 |
| reactive | 0.8722 [0.8682, 0.8763] | 422.0 | 110.8 | 3.40 |
| static | 0.7433 [0.7405, 0.7463] | 729.7 | 120.0 | 3.18 |

Best rule by mean: reactive.

| comparison | Δ served (pp) [95% paired CI] | seeds won | Δ lost per shock | Wilcoxon p |
|---|---|---|---|---|
| mpc-cusum-v1 − reactive | +6.20 [+6.10, +6.29] | 10/10 | -126.1 | 0.00195 |
| mpc-ewma − reactive | +6.34 [+6.26, +6.43] | 10/10 | -131.7 | 0.00195 |
| mpc-queue − reactive | +5.84 [+5.72, +5.94] | 10/10 | -160.9 | 0.00195 |
| oracle − reactive | +6.27 [+6.18, +6.37] | 10/10 | -130.2 | 0.00195 |
| mpc-cusum-v1 − mpc-ewma | -0.14 [-0.17, -0.12] | 0/10 | +5.6 | 0.00195 |
| greedy − oracle | -21.08 [-21.77, -20.51] | 0/10 | +421.1 | 0.00195 |
| mpc-cusum-v1 − oracle | -0.08 [-0.11, -0.04] | 1/10 | +4.0 | 0.00586 |
| mpc-ewma − oracle | +0.07 [+0.02, +0.11] | 9/10 | -1.5 | 0.0195 |
| mpc-queue − oracle | -0.44 [-0.61, -0.31] | 0/10 | -30.7 | 0.00195 |
| reactive − oracle | -6.27 [-6.37, -6.18] | 0/10 | +130.2 | 0.00195 |
| static − oracle | -19.16 [-19.52, -18.89] | 0/10 | +437.8 | 0.00195 |

Per-day service is descriptive; the source's final column uses the mean of daily fractions, which need not equal the arrival-weighted episode fraction above.

| policy | d1 | d2 | d3 | d4 | d5 | d6 | d7 | whole-run mean [95% CI over seeds] |
|---|---|---|---|---|---|---|---|---|
| greedy | 0.910 | 0.914 | 0.869 | 0.760 | 0.634 | 0.517 | 0.466 | 0.7243 [0.7184, 0.7299] |
| mpc-cusum-v1 | 0.959 | 0.950 | 0.939 | 0.938 | 0.937 | 0.906 | 0.910 | 0.9343 [0.9303, 0.9384] |
| mpc-ewma | 0.960 | 0.951 | 0.941 | 0.939 | 0.938 | 0.907 | 0.912 | 0.9357 [0.9316, 0.9399] |
| mpc-queue | 0.967 | 0.960 | 0.947 | 0.934 | 0.924 | 0.891 | 0.891 | 0.9306 [0.9274, 0.9340] |
| oracle | 0.959 | 0.951 | 0.940 | 0.939 | 0.938 | 0.905 | 0.913 | 0.9350 [0.9310, 0.9393] |
| reactive | 0.906 | 0.899 | 0.886 | 0.878 | 0.870 | 0.834 | 0.832 | 0.8723 [0.8683, 0.8764] |
| static | 0.855 | 0.841 | 0.801 | 0.749 | 0.699 | 0.638 | 0.621 | 0.7434 [0.7406, 0.7465] |

</details>

<details>
<summary>E5. Month: two displayed tables, all values VERIFIED against long-month-v2/summary.md</summary>

Source: `eval/results/long-month-v2/summary.md`. Thirty simulated days, 43200 steps, thirty shocks; four seeds 200-203, CRN; units 40, P=10, L=1. The source's separate 30-column per-day table is not rendered by this demo.

| policy | served fraction [95% CI over seeds] | lost per shock (120-step window) | recover steps | mean wait |
|---|---|---|---|---|
| greedy | 0.7356 [0.7300, 0.7394] | 655.9 | 110.0 | 3.73 |
| mpc-cusum-v1 | 0.9383 [0.9361, 0.9420] | 285.7 | 83.0 | 2.10 |
| mpc-ewma | 0.9398 [0.9375, 0.9436] | 278.1 | 79.5 | 2.11 |
| reactive | 0.8761 [0.8740, 0.8792] | 410.3 | 106.5 | 3.39 |

Best rule by mean: reactive.

| comparison | Δ served (pp) [95% paired CI] | seeds won | Δ lost per shock | Wilcoxon p |
|---|---|---|---|---|
| mpc-cusum-v1 − reactive | +6.22 [+6.15, +6.29] | 4/4 | -124.6 | 0.125 |
| mpc-ewma − reactive | +6.37 [+6.29, +6.44] | 4/4 | -132.2 | 0.125 |
| mpc-cusum-v1 − mpc-ewma | -0.15 [-0.16, -0.14] | 0/4 | +7.7 | 0.125 |

</details>

<details>
<summary>E6. Service versus movement: two tables, all values VERIFIED against pareto-v2/summary.md</summary>

Source: `eval/results/pareto-v2/summary.md`, including shock rows of `mvp-v2`. Shock, seeds 200-229, L=1, P=10; default move-cost weight 0.05. Values are not a proof of cost-free service improvement.

| policy | served fraction | empty hops / served | lost per shock |
|---|---|---|---|
| mpc-queue@c_move=0.5 | 0.9096 | 0.250 | 378.5 |
| mpc-ewma@c_move=1.0 | 0.9046 | 0.315 | 427.4 |
| greedy | 0.9057 | 0.326 | 404.5 |
| mpc-queue | 0.9549 | 0.381 | 235.0 |
| mpc-ewma@c_move=0.5 | 0.9373 | 0.413 | 320.5 |
| mpc-ewma@c_move=0.2 | 0.9424 | 0.459 | 300.7 |
| oracle | 0.9418 | 0.481 | 302.6 |
| mpc-cusum-v1 | 0.9417 | 0.489 | 305.3 |
| mpc-ewma | 0.9430 | 0.511 | 297.3 |
| static | 0.8642 | 0.512 | 573.5 |
| reactive | 0.8996 | 0.585 | 426.2 |
| mpc-myopic | 0.9337 | 0.603 | 339.9 |

| comparison | Δ served (pp) [95% CI] | seeds won | Wilcoxon p | Δ empty hops / served |
|---|---|---|---|---|
| mpc-ewma@c_move=0.5 − reactive | +3.77 [+3.55, +4.00] | 30/30 | 1.9e-09 | -0.172 |
| mpc-ewma@c_move=0.5 − greedy | +3.16 [+2.76, +3.59] | 30/30 | 1.9e-09 | +0.087 |
| mpc-queue − greedy | +4.92 [+4.52, +5.35] | 30/30 | 1.9e-09 | +0.054 |
| mpc-ewma@c_move=1.0 − greedy | -0.10 [-0.34, +0.14] | 10/30 | 0.26 | -0.012 |
| mpc-queue@c_move=0.5 − greedy | +0.39 [+0.13, +0.65] | 19/30 | 0.0062 | -0.076 |

</details>

<details>
<summary>E7. Forecast trust: one table, all values VERIFIED against trust-v2/summary.md</summary>

Source: `eval/results/trust-v2/summary.md` with `mvp-v2` extremes. Trust multiplies forecast; 0 is queue-only, 1 is EWMA. L=1, P=10, seeds 200-229, paired CRN. Exploratory: no correction across the sweep.

| scenario | trust 0 | 0.25 | 0.5 | 0.75 | 1 | best | best − max(trust 0, trust 1) (pp) [95% CI] |
|---|---|---|---|---|---|---|---|
| drift | 0.9679 | 0.9867 | 0.9954 | 0.9962 | 0.9946 | mpc-ewma@trust=0.75 | +0.16 [+0.13, +0.18] |
| shock | 0.9549 | 0.9569 | 0.9563 | 0.9511 | 0.9430 | mpc-ewma@trust=0.25 | +0.20 [+0.17, +0.23] |
| shock+drift | 0.9284 | 0.9397 | 0.9434 | 0.9394 | 0.9321 | mpc-ewma@trust=0.5 | +1.13 [+1.05, +1.21] |
| shock+drift+spikes | 0.9251 | 0.9350 | 0.9380 | 0.9332 | 0.9256 | mpc-ewma@trust=0.5 | +1.24 [+1.16, +1.33] |

</details>

<details>
<summary>E8. Planner sensitivity: one table, all values VERIFIED against phase-v2c/summary.md</summary>

Source: `eval/results/phase-v2c/summary.md`. Same seeds 200-219. Exploratory, added after phase-v2 reversed phase-v1; legacy never-abandoning backlog uses `@abandon_aware=0`, highspy. Service differences in pp with paired-bootstrap 95% CIs and wins/20.

| L | P | EWMA: legacy − new | true-rate − EWMA (new LP) | true-rate − EWMA (legacy LP) | detector − EWMA (new LP) | detector − EWMA (legacy LP) |
|---|---|---|---|---|---|---|
| 1 | 3 | +0.30 [+0.22, +0.38] (19/20) | +0.15 [+0.06, +0.23] (16/20) | +0.28 [+0.19, +0.38] (18/20) | -0.19 [-0.29, -0.10] (3/20) | +0.02 [-0.06, +0.11] (10/20) |
| 1 | 10 | -0.03 [-0.08, +0.01] (7/20) | -0.21 [-0.31, -0.10] (5/20) | -0.15 [-0.22, -0.07] (5/20) | -0.15 [-0.26, -0.04] (3/20) | -0.18 [-0.24, -0.11] (3/20) |
| 2 | 3 | +0.14 [-0.02, +0.28] (14/20) | +0.41 [+0.22, +0.60] (17/20) | +0.99 [+0.84, +1.16] (20/20) | +0.09 [-0.12, +0.30] (11/20) | +0.45 [+0.31, +0.59] (18/20) |
| 2 | 10 | -0.09 [-0.19, +0.00] (5/20) | +0.08 [-0.07, +0.24] (13/20) | +0.05 [-0.10, +0.19] (10/20) | -0.02 [-0.17, +0.10] (12/20) | -0.07 [-0.18, +0.05] (7/20) |
| 4 | 3 | -0.57 [-0.92, -0.19] (3/20) | -1.09 [-1.67, -0.57] (3/20) | +1.88 [+1.67, +2.07] (20/20) | -0.98 [-1.45, -0.57] (3/20) | +1.28 [+1.08, +1.49] (20/20) |
| 4 | 10 | +0.14 [+0.00, +0.28] (13/20) | +0.19 [+0.08, +0.28] (15/20) | +0.30 [+0.16, +0.44] (14/20) | -0.01 [-0.11, +0.10] (8/20) | +0.09 [-0.06, +0.24] (12/20) |
| 8 | 3 | -1.66 [-2.69, -0.57] (6/20) | -1.49 [-1.98, -0.99] (2/20) | +3.63 [+3.33, +3.94] (20/20) | -1.55 [-2.07, -1.06] (1/20) | +2.63 [+2.39, +2.86] (20/20) |
| 8 | 10 | +0.88 [+0.39, +1.46] (16/20) | -1.10 [-1.45, -0.75] (1/20) | +1.13 [+0.98, +1.28] (20/20) | -0.78 [-1.07, -0.48] (3/20) | +0.70 [+0.48, +0.90] (18/20) |

</details>

<details>
<summary>E9. Confirmatory experiment: nine tables, all values VERIFIED against mvp-v2/confirm.md</summary>

Source: `eval/results/mvp-v2/confirm.md`, registered in `eval/preregistration.md`. Seeds 200-229, 30 fresh test seeds; 1440 episodes; horizon 1440; K=40, P=10; highspy backend. Secondary families are not substitutes for the pre-registered primary claim.

Served fraction by policy, mean over seeds:

| scenario | greedy | mpc-cusum-v1 | mpc-ewma | mpc-myopic | mpc-queue | oracle | reactive | static |
|---|---|---|---|---|---|---|---|---|
| stationary | 0.9751 | 0.9987 | 0.9987 | 0.9975 | 0.9974 | 0.9987 | 0.9625 | 0.9528 |
| shock | 0.9057 | 0.9417 | 0.9430 | 0.9337 | 0.9549 | 0.9418 | 0.8996 | 0.8642 |
| drift | 0.7884 | 0.9940 | 0.9946 | 0.9758 | 0.9679 | 0.9949 | 0.9363 | 0.8216 |
| shock+drift | 0.7446 | 0.9300 | 0.9321 | 0.9092 | 0.9284 | 0.9317 | 0.8774 | 0.7573 |
| spikes | 0.9717 | 0.9969 | 0.9969 | 0.9945 | 0.9967 | 0.9972 | 0.9534 | 0.9396 |
| shock+drift+spikes | 0.7443 | 0.9234 | 0.9256 | 0.9046 | 0.9251 | 0.9254 | 0.8658 | 0.7452 |

Primary family: MPC-EWMA versus the pre-registered reference rule; Holm over six scenarios.

| scenario | reference | Δ served (pp) [95% paired CI] | seeds won | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | greedy | +2.36 [+2.16, +2.57] | 30/30 | 1.9e-09 | 1.1e-08 |
| shock | greedy | +3.73 [+3.28, +4.20] | 30/30 | 1.9e-09 | 1.1e-08 |
| drift | reactive | +5.83 [+5.75, +5.92] | 30/30 | 1.9e-09 | 1.1e-08 |
| shock+drift | reactive | +5.47 [+5.36, +5.59] | 30/30 | 1.9e-09 | 1.1e-08 |
| spikes | greedy | +2.51 [+2.34, +2.71] | 30/30 | 1.9e-09 | 1.1e-08 |
| shock+drift+spikes | reactive | +5.99 [+5.82, +6.15] | 30/30 | 1.9e-09 | 1.1e-08 |

Secondary S1, served fraction; Holm within family and endpoint.

| scenario | comparison | Δ served (pp) [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | mpc-myopic − mpc-ewma | -0.12 [-0.14, -0.10] | 0/30 | 1.9e-09 | 2.2e-08 |
| stationary | mpc-queue − mpc-ewma | -0.13 [-0.16, -0.10] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock | mpc-myopic − mpc-ewma | -0.93 [-1.05, -0.81] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock | mpc-queue − mpc-ewma | +1.19 [+1.06, +1.32] | 30/30 | 1.9e-09 | 2.2e-08 |
| drift | mpc-myopic − mpc-ewma | -1.88 [-2.06, -1.70] | 0/30 | 1.9e-09 | 2.2e-08 |
| drift | mpc-queue − mpc-ewma | -2.68 [-2.76, -2.59] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock+drift | mpc-myopic − mpc-ewma | -2.29 [-2.55, -2.03] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock+drift | mpc-queue − mpc-ewma | -0.37 [-0.50, -0.23] | 5/30 | 7.3e-05 | 0.00022 |
| spikes | mpc-myopic − mpc-ewma | -0.24 [-0.28, -0.20] | 0/30 | 1.9e-09 | 2.2e-08 |
| spikes | mpc-queue − mpc-ewma | -0.02 [-0.06, +0.02] | 12/30 | 0.26 | 0.52 |
| shock+drift+spikes | mpc-myopic − mpc-ewma | -2.10 [-2.36, -1.87] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock+drift+spikes | mpc-queue − mpc-ewma | -0.06 [-0.20, +0.08] | 17/30 | 0.58 | 0.58 |

Secondary S1, shock losses; Holm within family and endpoint.

| scenario | comparison | Δ lost per shock [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| shock | mpc-myopic − mpc-ewma | +42.67 [+34.53, +51.13] | 30/30 | 1.7e-06 | 1e-05 |
| shock | mpc-queue − mpc-ewma | -62.30 [-70.47, -53.83] | 0/30 | 1.7e-06 | 1e-05 |
| shock+drift | mpc-myopic − mpc-ewma | +31.73 [+23.57, +39.77] | 26/30 | 8.1e-06 | 1.6e-05 |
| shock+drift | mpc-queue − mpc-ewma | -49.90 [-57.03, -43.10] | 0/30 | 1.7e-06 | 1e-05 |
| shock+drift+spikes | mpc-myopic − mpc-ewma | +25.27 [+16.83, +33.67] | 26/30 | 5.3e-05 | 5.3e-05 |
| shock+drift+spikes | mpc-queue − mpc-ewma | -58.93 [-67.63, -50.30] | 0/30 | 1.7e-06 | 1e-05 |

Secondary S2, served fraction; Holm within family and endpoint.

| scenario | comparison | Δ served (pp) [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | mpc-cusum-v1 − mpc-ewma | +0.00 [-0.01, +0.02] | 17/30 | 0.6 | 1 |
| shock | mpc-cusum-v1 − mpc-ewma | -0.13 [-0.17, -0.09] | 5/30 | 2.4e-05 | 7.1e-05 |
| drift | mpc-cusum-v1 − mpc-ewma | -0.07 [-0.09, -0.05] | 4/30 | 5.1e-06 | 2.1e-05 |
| shock+drift | mpc-cusum-v1 − mpc-ewma | -0.21 [-0.25, -0.17] | 0/30 | 1.9e-09 | 1.1e-08 |
| spikes | mpc-cusum-v1 − mpc-ewma | +0.00 [-0.02, +0.02] | 15/30 | 0.94 | 1 |
| shock+drift+spikes | mpc-cusum-v1 − mpc-ewma | -0.22 [-0.26, -0.18] | 2/30 | 9.3e-09 | 4.7e-08 |

Secondary S2, shock losses; Holm within family and endpoint.

| scenario | comparison | Δ lost per shock [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| shock | mpc-cusum-v1 − mpc-ewma | +8.00 [+4.53, +11.47] | 23/30 | 0.00043 | 0.00043 |
| shock+drift | mpc-cusum-v1 − mpc-ewma | +14.40 [+10.83, +17.87] | 27/30 | 9.6e-06 | 2.9e-05 |
| shock+drift+spikes | mpc-cusum-v1 − mpc-ewma | +12.57 [+8.30, +16.63] | 25/30 | 4.2e-05 | 8.3e-05 |

Secondary S3, served fraction; Holm within family and endpoint.

| scenario | comparison | Δ served (pp) [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | oracle − mpc-ewma | -0.00 [-0.01, +0.01] | 14/30 | 0.72 | 0.83 |
| shock | oracle − mpc-ewma | -0.12 [-0.17, -0.07] | 5/30 | 4.4e-05 | 0.00026 |
| drift | oracle − mpc-ewma | +0.03 [+0.01, +0.04] | 20/30 | 0.041 | 0.16 |
| shock+drift | oracle − mpc-ewma | -0.04 [-0.08, -0.00] | 11/30 | 0.05 | 0.16 |
| spikes | oracle − mpc-ewma | +0.04 [+0.02, +0.05] | 25/30 | 6.3e-05 | 0.00031 |
| shock+drift+spikes | oracle − mpc-ewma | -0.02 [-0.07, +0.02] | 15/30 | 0.42 | 0.83 |

Secondary S3, shock losses; Holm within family and endpoint.

| scenario | comparison | Δ lost per shock [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| shock | oracle − mpc-ewma | +5.37 [+1.13, +9.83] | 20/30 | 0.037 | 0.11 |
| shock+drift | oracle − mpc-ewma | +3.30 [-0.90, +7.70] | 17/30 | 0.23 | 0.23 |
| shock+drift+spikes | oracle − mpc-ewma | +4.00 [+0.13, +7.70] | 21/30 | 0.046 | 0.11 |

Movement cost and shock recovery, means over seeds. Recovery steps are censored at 120; the recovery fraction is shown separately.

| scenario | policy | empty hops / served | lost per shock (120 steps) | recovered ≤120 steps | recover steps (censored at 120) |
|---|---|---|---|---|---|
| stationary | greedy | 0.346 | — | — | — |
| stationary | mpc-cusum-v1 | 0.557 | — | — | — |
| stationary | mpc-ewma | 0.583 | — | — | — |
| stationary | mpc-myopic | 0.687 | — | — | — |
| stationary | mpc-queue | 0.385 | — | — | — |
| stationary | oracle | 0.550 | — | — | — |
| stationary | reactive | 0.568 | — | — | — |
| stationary | static | 0.518 | — | — | — |
| shock | greedy | 0.326 | 404.5 | 0.13 | 115.6 |
| shock | mpc-cusum-v1 | 0.489 | 305.3 | 0.40 | 101.7 |
| shock | mpc-ewma | 0.511 | 297.3 | 0.47 | 96.1 |
| shock | mpc-myopic | 0.603 | 339.9 | 0.17 | 113.1 |
| shock | mpc-queue | 0.381 | 235.0 | 0.87 | 67.2 |
| shock | oracle | 0.481 | 302.6 | 0.43 | 100.3 |
| shock | reactive | 0.585 | 426.2 | 0.10 | 116.0 |
| shock | static | 0.512 | 573.5 | 0.00 | 120.0 |
| drift | greedy | 0.325 | — | — | — |
| drift | mpc-cusum-v1 | 0.693 | — | — | — |
| drift | mpc-ewma | 0.717 | — | — | — |
| drift | mpc-myopic | 0.767 | — | — | — |
| drift | mpc-queue | 0.509 | — | — | — |
| drift | oracle | 0.686 | — | — | — |
| drift | reactive | 0.701 | — | — | — |
| drift | static | 0.601 | — | — | — |
| shock+drift | greedy | 0.312 | 584.4 | 0.13 | 111.3 |
| shock+drift | mpc-cusum-v1 | 0.616 | 341.2 | 0.20 | 106.0 |
| shock+drift | mpc-ewma | 0.636 | 326.8 | 0.20 | 105.6 |
| shock+drift | mpc-myopic | 0.679 | 358.6 | 0.20 | 107.6 |
| shock+drift | mpc-queue | 0.489 | 276.9 | 0.63 | 84.0 |
| shock+drift | oracle | 0.607 | 330.1 | 0.30 | 102.8 |
| shock+drift | reactive | 0.689 | 448.7 | 0.00 | 120.0 |
| shock+drift | static | 0.585 | 735.7 | 0.00 | 120.0 |
| spikes | greedy | 0.347 | — | — | — |
| spikes | mpc-cusum-v1 | 0.569 | — | — | — |
| spikes | mpc-ewma | 0.588 | — | — | — |
| spikes | mpc-myopic | 0.683 | — | — | — |
| spikes | mpc-queue | 0.395 | — | — | — |
| spikes | oracle | 0.554 | — | — | — |
| spikes | reactive | 0.569 | — | — | — |
| spikes | static | 0.513 | — | — | — |
| shock+drift+spikes | greedy | 0.321 | 595.7 | 0.13 | 112.5 |
| shock+drift+spikes | mpc-cusum-v1 | 0.629 | 373.8 | 0.20 | 109.6 |
| shock+drift+spikes | mpc-ewma | 0.645 | 361.3 | 0.30 | 101.8 |
| shock+drift+spikes | mpc-myopic | 0.683 | 386.5 | 0.20 | 114.9 |
| shock+drift+spikes | mpc-queue | 0.499 | 302.3 | 0.57 | 84.9 |
| shock+drift+spikes | oracle | 0.614 | 365.3 | 0.27 | 108.0 |
| shock+drift+spikes | reactive | 0.690 | 491.7 | 0.03 | 119.4 |
| shock+drift+spikes | static | 0.585 | 771.9 | 0.00 | 120.0 |

</details>

---

## Lead decisions (2026-10-04 19:52 IST)

| # | Decision | Action (who) |
|---|---|---|
| 1 | Dead knob after the replay ends — **ACCEPTED** | Builder: start armed/paused; auto-pause at the unperturbed window result; a conspicuous "Your turn: restart at 21:15" control starts a separate, labelled interactive run; reject or disable zero-duration end-of-trace shocks (the server returns an error); SCRIPT.md scripts the handover. No invented taxi data. |
| 2 | "Your surge is seed #21" overclaims — **ACCEPTED** (frozen-protocol mode **DEFERRED**) | Builder: reword everywhere to "your live intervention, shown alongside 20 committed reference runs; not a new test seed or a calibrated prediction for this location/time". Flag off-reference clicks (onset outside 04:12–06:36, overlapping shocks, size ≠ ×1, horizon mismatch) with an "off-reference" chip. The literal seed-21 protocol mode is deferred (after Round 1). |
| 3 | 1280×720 hides story-critical evidence — **ACCEPTED** | Builder: a stage layout validated at 1280×720. The active prediction, the current intervention result and all eight (L,P) cells are visible together; secondary receipts and legends go in a drawer; the real-data qualification sits next to the main result. Fallback screenshots retaken at 1280×720. |
| 4 | Script skips the long-horizon stretch — **ACCEPTED** | Builder: a mandatory 20–30 s pre-warmed week segment (day-7 result; live seed-200 bars vs the 10-seed committed means; month = 4 seeds). Trim the p-value recitation. |
| 5 | Recorded/committed shown as "live" — **ACCEPTED** (provenance MISMATCH) | Builder: one LIVE / RECORDED / COMMITTED provenance value drives every label. Closing line: "The interventions and simulations were computed live; the reference distributions and confidence intervals are committed results." In fallback mode the week shows committed or recorded media, not an empty "live" scene. |
| 6 | 62-pickup anomaly vs 46-loss counter are different populations — **ACCEPTED** | Lead (done): the source caption now says "20.7x raw, un-thinned pickups in one cell". Builder: label the anomaly "raw TLC cell pickups, before thinning" and the counter "fleet-wide losses, 21:30–23:30"; say it is an illustrative, retrospectively chosen window, not a causal estimate. |
| 7 | "6 h" false for late NYC clicks — **ACCEPTED** | Builder: show the returned start, end and actual duration ("up to 6 h; this replay ends at midnight"), and qualify late-day truncation in synthetic mode too. |
| 8 | Ordinary-days caption imports the July-4 event — **ACCEPTED** (lead's source bug) | Lead (done): `eval/summarise_misc.py` writes the event-window sentence only when event losses exist; `nyc-v2b/summary.md` regenerated ("No event window …"), numeric tables unchanged. Builder: regenerate `demo/data/evidence.js`. |
| 9 | "Bit-identical" broader than the parity check — **ACCEPTED** | Builder: "matches the committed served-fraction and loss metrics; daily fractions match at committed precision" (SCRIPT, badges, README). |
| 10 | No stage-safe recovery on backend loss — **ACCEPTED** | Builder: on a fetch failure, pause, mark live computation stopped, and offer **Retry** and **Open recorded fallback**. Never silently relabel live as recorded. |

Score noted: 7.5/10 ("would shortlist; not yet confidently top-3"). Re-verification from a fresh clone after the fixes.
