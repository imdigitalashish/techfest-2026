# SCRIPT — the 3-minute live demo (P3 · "the evaluator that says I don't know")

**Before you go on**
- Run `perceptron-p03-off-policy-eval/demo/smoke.sh` the same morning; it must end with `PASS`.
- Start the demo with `demo/run.sh`. It opens `demo/index.html` offline.
- Set full screen and 100% zoom at 1920×1080; use 90% at 1280×720.
- Keys:
  - <kbd>1</kbd>–<kbd>4</kbd> switch sheets.
  - <kbd>←</kbd>/<kbd>→</kbd> move α by 0.01; hold <kbd>Shift</kbd> for 0.05.
  - <kbd>[</kbd>/<kbd>]</kbd> change period.
  - <kbd>i</kbd> switches IPS/SNIPS; <kbd>c</kbd> switches row-level/hour-cluster.
- Hover any dotted number to show its source file and key.
- **If the live demo fails:** open `demo/fallback/01…12*.png` in order. The talk track is the same; screenshot names match the beats below.

Units are clicks per 1,000 impressions throughout (percentage points on sheet 4).

| time | do | say | point at |
|---|---|---|---|
| 0:00 | Sheet 1, top (`01_…`) | "Real data: ZOZOTOWN's Open Bandit A/B test. A team switched recommendation policy. The dashboard said **+1.62**. But both policies were running side by side the whole time, so we have a real A/B check: **+1.26**." | headline boxes |
| 0:20 | — | "The old policy's own click rate rose **11%** with no switch at all. The dashboard booked the week as the policy, so it overstates the policy by **29%**. From the logs alone, with no A/B test, doubly robust OPE says **+1.40**, interval **+1.13 … +1.67**. That interval holds the check." | "The week" and "Logs only" rows; waterfall |
| 0:40 | Scroll to the stamp (`02_…`) | "And yet our evaluator refuses to sign off: **can't tell from these logs**. The 2,769,425 BTS impressions are worth only **25,395** random ones for this question, and one click counts **12,500** times. Honestly, here the refusal cost us an answer. But on 26 Nov the same estimate failed, **+1.48** against a check of **+1.06**, and it refused that too. Track record: **5/8** answered, **4/5** held the check, **2/2** failures refused. This gate was designed after we saw these failures, so it is *post hoc* on these cases. So we pre-registered a fresh test." | CAN'T TELL stamp; POST HOC stamp; track record |
| 1:00 | <kbd>3</kbd> (`04_…`) | "Registered tonight at **21:07:33 IST**, before computing anything. The candidate mixes the deployed sampler with uniform random. Its true value is a straight line between the two A/B arms, so we have a real check at every α." | PRE-REGISTERED stamp; black line |
| 1:15 | Drag α from 0 to 0.42 | "Orange is IPS from the BTS logs: tight, and on the line. Watch the effective rows fall, from 2.77 million to **138,643**." | orange band; readout "overlap" |
| 1:30 | One more step, to 0.43 (`05_…`) | "There. ESS/n crosses the frozen 5% floor, and the stamp lands: **can't tell**. We predicted **0.43** from one committed number before we computed this. IPS still prints **4.295** with a tidy interval. Ours says it can't tell." | stamp; hollow vs filled triangles |
| 1:45 | — | "Blue asks the same question from the **Random** arm's logs, nine times fewer rows. It answers at every α, and IPS holds the check at every α on all six periods. Which logs you keep decides which questions you can ever answer." | blue band; Random rows of the strip |
| 2:00 | <kbd>]</kbd> to Nov 26, α 0.33 (`06_…`) | "Now the honest negative. On 26 Nov, between α **0.28** and **0.39**, IPS's interval misses the check while our gate still answers. The worst miss is **0.036** per 1,000. The gate is late here." | red pencil on the curve; red cells in the strip |
| 2:10 | <kbd>c</kbd> (`07_…`) | "Rows within an hour are not independent. With hour-cluster intervals, those misses disappear." | readout "check is inside" |
| 2:15 | Scroll to the strip (`10_…`) | "Every period, every α: 12 series × 101 points, pre-registered, nothing hidden. **681** answered with the check inside, **12** answered misses, all on that one day, and **403** refusals that weren't needed. It is a conservative auditor. **31 of 33** predictions made before computing hit." | strip; totals; predictions table |
| 2:35 | <kbd>4</kbd> (`11_…`, `12_…`) | "In the simulator, the truth is exact. A seasonal drop makes the dashboard read **−5.6** points while the switch added **+7.5**. DR recovers **+7.5**; the dashboard has the wrong sign in **30/30** seeds. Drag the drift: naive is right only when the season cooperates." | SYNTHETIC stamp; red shaded zone |
| 2:50 | Hover any number | "Every number here has a source: hover it. One command rebuilds the page from a 0.76 MB vendored extract, and a smoke test recomputes every knob value from it. This is the evaluator that says 'I don't know', and shows you when that was the right call." | tooltip |

## Honest caveats to say before a judge asks
- **The "A/B check" is the concurrent arm difference, not ground truth.** The pre-registered balance check flagged a total-variation distance of about 0.36 per user feature. A post-hoc look at the raw labels found one category per feature with a different hash in each file. The label-free distance is ≤ 0.0044 (`eval/results/obd_balance_posthoc.md`). It is unresolved, and we say so on screen.
- **The gate is post hoc on OBD.** It was designed after we saw the failures on sheet 1. The knob analysis on sheet 3 is pre-registered, except at endpoints that were already committed.
- **The Random-logs side of the knob scores an approximate target**, an hourly reconstruction of the adaptive sampler, as on sheet 2.
- **Sheet 4 is synthetic.**

## The hardest questions
**1. "Isn't the knob trivial? IPS is linear in α."**
Yes, and the page says so. IPS's error is exactly α × its error at α = 1, and the gate's mean-weight z does not change with α. That is why we pre-registered predictions from the committed α = 1 cells; 31 of 33 hit.
The genuinely new evidence is:
- SNIPS, which is nonlinear: 24 answered misses on Nov 25 Random logs with row-level intervals, 0 with hour-cluster;
- the hour-cluster intervals;
- two periods never examined before, Nov 24 and the full window;
- the exact crossings.

The claim is not new estimator maths. It is showing, on real data against a real check, where an evaluator should stop answering.

**2. "Your gate was tuned after seeing these failures, and it still fails on Nov 26. Why trust it?"**
It was calibrated on the simulator only, before touching OBD (36 configurations; it answers 47% with coverage 0.96). It was frozen at commit b4e95ae.
- A pre-registered simulator holdout: it answered 818/1,536 runs, and 771/818 answered intervals held the truth (1,404/1,536 ungated).
- On the pre-registered knob it is conservative: 403 unnecessary refusals against 12 answered misses. Those misses are at most 0.036 per 1,000, all on one day, and none survive hour-cluster intervals.
- The fix we would test next is a dependence-aware diagnostic. We won't retune the frozen rule after the fact.

**3. "Why does it refuse a 1% change on Nov 25?"**
On that day the BTS logs' mean importance weight is significantly above 1 (z = +4.6): the logged propensities don't add up for the items actually shown. That is a property of the logs, not of α, so the frozen rule refuses at every α > 0.
At α = 0.05, IPS was in fact fine: 4.830 against a check of 4.845 (`08_…`). That refusal cost an answer, and we report it rather than tune it away.

**Spare: "Is this a judgment, or a computation?"** Hover the number. `demo/smoke.sh` re-derives the extract numbers with no shared code. It recomputes all 1,212 knob points from the extract and checks them against the committed results byte for byte. It also checks that the page's numbers equal the abstract's `headline.json`.
