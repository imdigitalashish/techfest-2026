# P4 demo: 3-minute talk track

**Setup:** run `cd perceptron-p04-lob-regimes && demo/run.sh` before the judges arrive, so the replay cache is warm. Use a full-screen browser at about 1440 px wide.

**Fallback:** if anything fails, show the PNGs in `demo/fallback/` in numeric order. Each step below names its screenshot.

---

**0:00–0:30 · Scoreboard (section 1)** · `fallback/01_scoreboard.png`

**Say:** "The task is to forecast whether the Bitcoin futures mid-price is higher in 10 seconds, using the 5-level order book, and to survive regime shifts. We trained on 2023 and tuned on 2024. We then pre-registered the test and ran it once on 22 held-out days in 2025 and 2026. An independent session reproduced it exactly."

**Point at:**
- Textbook KS → refit, **+0.0268, worse on 21/22 days**.
- Regime gate, **−0.0099 [−0.0136, −0.0068], better on 22/22 days**.

**Say:** "The textbook recipe, 'detect drift and retrain', makes the model worse on 21 of 22 days. Conditioning on the volatility regime makes it better on all 22. Our registered Fixed-Share hypothesis, H1, was *not* supported, and we say so; each chip tells you which numbers were pre-registered."

**Point right, "Is it just one better head?":**
- Every head alone is worse than the gate: high-vol +0.0141, mid +0.0138, low +0.0526.
- All three heads are used: 21 / 33 / 46%.

**0:30–1:15 · Replay a real day (section 2)** · `fallback/08…09_replay_2026-08-01_*.png`

**Click** `2026-08-01` (held-out, the calmest day by rule).

**Say:** "This is computed live on this laptop by the same committed code. Prices are 10-minute candles, and the ✓ column proves each live number equals the committed result."

**Point at:**
- the red ticks, where the textbook KS fires 48 times, every 30 minutes;
- the yellow KS audit track, which stays quiet;
- the evening sell-off around 17:00. The head band turns from blue (low-vol) to red (high-vol). In the bottom pane the red KS → refit curve climbs, while green (gate) keeps falling.

**1:15–2:30 · The dial (section 3), the crazy part** · `fallback/03`, `05`, `06_dial_*.png`, `10_replay_2026-08-01_alpha_1e-75.png`

**Say:** "Maybe the textbook detector is just too twitchy. Turn its significance level down."

**Drag the slider** from 1e-3 to **1e-30**. **Point at the readout:** 26 alarms on this day, 28.7 per day across 22 held-out days.

**Say:** "α is ten to the minus thirty, and it still fires 26 times. Why? Look at the right panel. On the 2023 training days themselves, each checked against the other eleven, the test rejects **33%** of 10-minute windows at that α, and **99.4%** at the default 1e-3. The median p-value is 10^-22.9. One-second windows overlap, are autocorrelated and drift, so the i.i.d. null behind the p-value is simply false. The i.i.d. null is the problem, not α."

**Point at the left chart:** the red curve stays above the green regime-gate line at **every** setting, with 0/22 days better at any stop.

**Drag to 1e-75, then to "off".** **Say:** "Turn it until it stops crying wolf. What's left is the un-adapted single EWMA head, which the regime gate still beats by **0.0083 on 22/22 days**." Point at the verdict box.

**Optional:** click `q = 0.999 (committed ksc_refit)`. The calibrated detector fires only 2.5 times a day and is still +0.0208 behind the gate.

**Honesty line:** "The dial is a post-hoc demo sweep, not pre-registered. The chip says so. Its 1e-3 setting reproduces the committed result on all 22 days, and the smoke test asserts that."

**2:30–3:00 · Can you trade it? (section 4)** · `fallback/07_exec_vip9_100ms.png`

**Click** `VIP 9`, then `100 ms`.

**Say:** "The forecast is real, at +0.297 bps gross per signal. Break-even is about 0.13 bps per side, against taker fees of 1.7 to 5 bps."

**Point at the bottom line:** "Not tradable as a taker after fees." "The maker number is an optimistic upper bound, which we label as such."

**Close:** "Detect-and-retrain fails under real high-frequency dependence at any sensitivity; conditioning on state works, on 22 of 22 held-out days."

**Optional, +45 s · Stress test (section 5, SEMI-SYNTHETIC)** · `fallback/11_splice_calm_to_volatile_12h.png`

**Say:** "Real data has no labelled changepoints, so we made one. We spliced the calmest held-out day into the most volatile one at a time the judge picks. Day B's prices are shifted additively by whole ticks, so labels are unchanged, and the smoke test asserts that."

**Click** `calm → volatile`, then any time.

**Point at:**
- the textbook KS firing 12–36 times on the calm half, before anything changed;
- the head band flipping to high-vol within minutes;
- the gate family ranked first after the splice, in 10/10 splices.

**Say:** "This is labelled semi-synthetic; it's a stress test, not held-out evidence."

---

**If asked:**
- **"Why is the dev day here?"** 2024-05-01 is the FOMC day. It is a dev day, labelled "illustrative", and carries no held-out claim.
- **"How were the days picked?"** By a rule on the committed mean `rv_600s`: calmest, lower median and most volatile held-out day.
- **"Most volatile day?"** On 2026-03-01 even α = 1e-30 fires 48 times, and 99.9% of windows reject. The dial cannot silence it there.
