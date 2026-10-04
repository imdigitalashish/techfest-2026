# SCRIPT — the 3-minute live demo (P3 · "the evaluator that says I don't know")

**Measured rehearsal: 2:52 (172.0 s), clicks included, for 375 spoken words** (method under "Rehearsal"). The talk track is the spoken part; everything else is for preparation and Q&A.

## Before you go on

- **Check the build.** Run `perceptron-p03-off-policy-eval/demo/smoke.sh` the same morning; it must end with `PASS`.
- **Start the demo.** Run `demo/run.sh`. It opens `demo/index.html` offline in the default browser.
- **Screen.** Full screen at 100% zoom. The knob view fits 1280×720, 1440×900, 1600×900 and 1920×1080.
- **Presets** each set the period, α, estimator (IPS), interval (row-level), endpoint (E1) and both log sources together, then scroll to the knob:
  - <kbd>5</kbd> W2 · α 0.42 (answers)
  - <kbd>6</kbd> W2 · α 0.43 (can't tell)
  - <kbd>7</kbd> Nov 26 · α 0.33 (the negative)
- **Other keys:**
  - <kbd>1</kbd>–<kbd>4</kbd> switch sheets; on sheet 3 a second <kbd>3</kbd> shows the knob.
  - <kbd>c</kbd> switches row-level / hour-cluster intervals; <kbd>e</kbd> switches the endpoint shown (E1 / E2); <kbd>i</kbd> switches IPS / SNIPS.
  - <kbd>←</kbd> <kbd>→</kbd> move α by 0.01 (<kbd>Shift</kbd>: 0.05); <kbd>[</kbd> <kbd>]</kbd> step through the periods.
  - Clicking the buttons does the same.
- **Hover** a dotted number to show its source file and key.
- **If the live page fails:** show `demo/fallback/01…09` in order; the beat numbers match the table below. Files 10–11 are Q&A views. Every file's selected state is checked against its name in `fallback/states.json`.

Units: clicks per 1,000 impressions (percentage points on sheet 4).

## Talk track

| # | start (measured) | do (exact clicks) | say | fallback |
|---|---|---|---|---|
| 1 | 0:00 | Page open at the top of sheet 1. | "We re-enact a switch using concurrent A/B logs from ZOZOTOWN's Open Bandit Dataset: uniform-random logs before, Thompson-sampling logs after. The dashboard says plus 1.62 clicks per thousand. The concurrent A/B estimate says plus 1.26: the dashboard is 29% above it, because the old policy's own click rate rose anyway. From the logs alone, doubly robust estimation gives plus 1.40, with an interval that holds the A/B reference, and also the dashboard number." | `01_b1_…` |
| 2 | 0:34 | Scroll down to the big CAN'T TELL stamp. | "Yet our evaluator says: can't tell from these logs. Reweighting greedy logs toward random concentrates the weights; weight ESS is under 1% of rows. We designed this gate after seeing OBD failures, so this sheet is post hoc: it refused 2 of 2 consistency failures, and 2 of 3 interval misses." | `02_b2_…` |
| 3 | 0:55 | Press <kbd>2</kbd>. | "When the logs explore, the same evaluator answers: DR 4.936 against the Thompson arm's observed 4.890, an approximate target, because that policy kept learning." | `03_b3_…` |
| 4 | 1:08 | Press <kbd>5</kbd> (preset W2 · α 0.42). | "So we pre-registered a knob before computing it. Alpha mixes the deployed policy with uniform random. The black line mixes the two arms' observed click rates: a noisy reference, not known truth. Orange is IPS from the Thompson logs; at alpha 0.42 the gate answers and the reference is inside." | `04_b4_…` |
| 5 | 1:29 | Press <kbd>6</kbd> (preset W2 · α 0.43). | "One step further, weight ESS drops below the frozen 5% floor: can't tell, while plain IPS still prints a tidy interval. Blue, from the Random arm's logs, an approximate target, answers everywhere. The logs you keep decide which questions you can answer." | `05_b5_…` |
| 6 | 1:47 | Press <kbd>7</kbd> (preset Nov 26 · α 0.33). | "Now the negative. On 26 November the gate answers while IPS's interval misses the reference, from alpha 0.28 to 0.39." | `06_b6_…` |
| 7 | 1:58 | Click **hour-cluster**. | "With hour-cluster intervals the reference is inside, but the paired test still rejects. A green point check is not validation." | `07_b7_…` |
| 8 | 2:07 | Click **row-level** and check it is highlighted; scroll down to the strip. | "Back to row-level, the registered primary. On Thompson logs the gate answered 87 of 606 grid points, with the reference inside 75; it refused 519. These are correlated grid locations, not independent decisions; deployment value is untested." | `08_b8_…` |
| 9 | 2:26 | Press <kbd>4</kbd>. | "In the simulator, against a Monte-Carlo reference, a downward drift of 0.75 or more makes the dashboard's sign wrong in every seed, while DR's RMSE stays at most 0.6 points." | `09_b9_…` |
| 10 | 2:40 | Stay on sheet 4. | "Everything here renders committed results; one smoke command replays the grid from a 0.76-megabyte extract. An evaluator that says I don't know, and shows the evidence for each answer." | `09_b9_…` |

**What to point at, beat by beat:**
1. The boxed **+1.62** and **+1.26**; "The week" row; the **+1.40** box.
2. The stamp; the POST HOC stamp; "2/2 S1 rejections refused" and "2/3 own-CI misses refused".
3. The **4.936** and **4.890** boxes.
4. The black reference line, its caveat under the chart, the orange band, and the readout's "✓ answers".
5. The stamp landing in the readout; the hollow and filled triangles at 0.43.
6. The red pencil on the orange curve; the readout's "E1 outside … E2 rejects".
7. The readout's "**E1 inside; E2 still rejects (difference CI −0.290 … −0.008)**".
8. The bold "Registered primary" paragraph.
9. The red "wrong sign" zone.

## Rehearsal

- **Measured** at 23:26 IST on 4 Oct 2026, on the committed page: **2:52.0 (172.0 s)** for the whole path, clicks included. The start column above is that measured timeline.
- **How:**
  - `demo/rehearsal/speech.py` counts the talk track's spoken words (375) and times each beat with macOS `say -r 150`: 150 words per minute, default voice, rendered to a file, not played. Speech total: 160.8 s.
  - `demo/rehearsal/drive.js` performs every click and key in the "do" column in Chromium at 1600×900, with a 1 s presenter pause before each action. It waits each beat's speech time in real time and asserts the state each beat must show (for example beat 7's readout). Result: `demo/rehearsal/result.json`.
  - The browser tool limits a request to about 3 minutes, so the run took two calls: beats 1–5 (107.2 s) and 6–10 (64.8 s). The clock stopped only at that beat boundary, where nothing happens on screen.
- **Limits:** this is a synthetic voice at a steady 150 wpm, not a human run-through. At 140 wpm the same path would take about 3:04. Rehearse aloud once with a stopwatch; if it runs long, drop beat 10's first sentence (15 words, 7.2 s by the same `say` timing).

## Honest caveats (say them if asked; they are on the page)

- **The black line is a noisy concurrent-A/B reference, not known truth.**
  - It is the arms' observed click rates mixed by α.
  - The BTS-side weights use logged propensities along the realised history.
  - The Random-side target is an hourly approximation of an adaptive policy.
  - Arm comparability is unresolved (a raw-label artefact, `eval/results/obd_raw_labels.md`).
  - Deploying a new adaptive mixture could change later histories, which no line here captures.
- **The gate's chronology.** The rule was selected using simulator runs after OBD failures had informed its design, then frozen. Sheet 1 is post hoc. The knob protocol was registered before its curves were computed, while disclosing the endpoints already seen: this is pre-registered reuse of OBD, not an untouched real-data holdout.
- **"31/33" are endpoint-derived checks.** IPS(λ) = (1 − λ)·p + λ·u and SNIPS(λ) = [(1 − λ)·p + λ·u] / [(1 − λ) + λ·m], so the curves are determined by endpoint statistics. The checks mainly test algebra and implementation. Computed beyond the endpoints: hour-cluster uncertainty, the full-window BTS aggregation and previously unrecorded z statistics.
- **Counts are correlated grid locations, not decisions.** Under the registered point-containment diagnostic, 403 refused BTS grid locations contain the reference. The gate trades fewer answers for a lower observed miss fraction (12/87 answered vs 128/606 ungated); deployment value remains untested. The 5% floor is a frozen heuristic, not a theorem.
- **Weight ESS measures weight concentration, not guaranteed precision.**
  - The 12,500 weight is hypothetical: a click at the smallest logged propensity would get it. The largest weight on an actual click in that window is about 139.
  - The mean-weight z-test flags a log slice; it does not identify the cause or prove the recorded propensities invalid.
- **Sheet 4 is synthetic.** Its reference is approximated with 200,000 Monte-Carlo draws. The S1 waterfall is a separate fixed case (mix shift 0.5, 30 seeds) that the slider does not control.
- **What runs where.** The page renders committed results. `smoke.sh` replays the grid from the extract with the same analysis code, and independently re-checks five basic quantities with separate standard-library code.

## The three hardest questions

**1. "You already have both A/B arms. What did OPE identify that the A/B test did not, and would your line stay correct after a real deployment?"**
- The arm we score is held out as the reference; the estimate uses only the other arm's logs.
- BTS-side weight: (1 − α) + α / (80 × logged propensity).
- The estimand is a fixed-history mixture on the observed traffic. The line is a noisy reference, arm balance is unresolved, the Random-side target is reconstructed, and a newly deployed adaptive mixture could change later histories.
- On sheet 1, DR's interval also contains the dashboard number. We do not claim to have recovered the true policy effect.

**2. "You pressed c and the failure turned green. Did you fix the problem or change the test?"**
- We changed the interval model. The green status is E1; the paired E2 test still rejects.
- At Nov 26, α 0.33: IPS 4.379 against a reference of 4.528, with a joint-hour difference interval of −0.290 … −0.008 per 1,000.
- The difference interval accounts for the shared arm's covariance. For IPS, E2 rejects at every answered nonzero α on Nov 26, in both interval modes. SNIPS's E2 is consistent at all 39 of those points (press <kbd>e</kbd>, then click **SNIPS**); we report both.
- Hour clustering was pre-declared, but it does not prove independence across hours or remove the uncertainty from the adaptive target.

**3. "Why should we trust, or pay for, this gate? The curves follow from the endpoints and it refuses most primary cases."**
- IPS and SNIPS are standard, and the curve algebra is largely predetermined; 31/33 is mainly a reproducibility check.
- **Primary scope:**
  - 87/606 BTS grid points answered; E1 holds at 75/87. Six of the 87 are at α = 0, the logging end, inside by construction; at α > 0 it is 69/81.
  - E2 consistent at 48, rejecting at 39.
  - These are dependent grid counts.
- **Calibration:** OBD failures informed the gate's design.
- **Simulator holdout (separately pre-registered):**
  - 818/1,536 runs answered; 771/818 answered intervals held the reference, against 1,404/1,536 ungated.
  - Neither version had a confident wrong sign, so no wrong-sign benefit was shown.
- **The claim:** an inspectable diagnostic aid. A held-out, cost-sensitive test of errors against refusals comes next; there is no universal 5% safety boundary.

**Spare: "Is this a computation or a judgement?"**
- Hover any dotted number, including the knob readouts, for its file and key.
- The page renders committed results.
- `smoke.sh` replays all 1,212 knob points from the 0.76 MB extract with the same code, byte for byte, and independently re-checks five basic quantities.
- It also asserts that the page's headline numbers equal the abstract's `headline.json`.
