# P4 demo: 3-minute talk track

**Before judges arrive:** `cd perceptron-p04-lob-regimes && demo/run.sh`, so the cache is warm. Use a full-screen browser at 1440×900. Select **2026-08-01** and leave the dial at **1e-3**.

**If live fails:** open `demo/fallback/` in file order. The deck follows this story; regenerate it with `python demo/capture_fallback.py`.

**Budget:** 35 s scoreboard + 35 s replay + 75 s dial + 35 s fees = 180 s. At roughly 150 spoken words per minute, each act's quoted speech fits its slot.

---

### 0:00–0:35 · Scoreboard (section 1) · `01_scoreboard.png`

**Say:** "We forecast the Bitcoin futures mid-price 10 seconds ahead from the order book, across regime shifts. We trained on 2023, tuned on 2024, then tested once on 22 held-out days. Textbook drift detection with retraining is worse on 21 of 22 days. Switching between volatility-regime heads is better on all 22. Our registered hypothesis, H1, failed, and the chips say which result is which."

**Point at:** the red **+0.0268, 1/22** and the green **−0.0099, 22/22**.

### 0:35–1:10 · Real replay (section 2, left) · `02_stage_2026-08-01_alpha_1e-3.png`

**Say:** "This is the calmest held-out day, computed live by the committed code. Prices are 10-minute candles. The green line says each live number matches the committed result. Red bars are the textbook test's alarms: 48, one every half hour, its cap. In the evening sell-off the gate switches to its high-volatility head, red in the band, with no alarm at all."

### 1:10–2:25 · The dial (section 2, right) · `03_…_1e-30_HERO.png`, `04_…_calibrated`, `05_…_off`

**Say:** "Maybe the test is just too twitchy, so turn it down."

**Drag the slider to 1e-30.** **Hero:** **26 alarms**.

**Say:** "Alpha is ten to the minus thirty, and it still fires 26 times today, about 29 a day across held-out days. On the 2023 training days themselves, each checked against the other eleven, it rejects a third of all windows at that level. So these windows aren't independent draws from one distribution. Detecting change doesn't mean refitting helps: the red curve stays above the green gate line at every setting."

**Click** `q 0.999 (= ksc_refit)`. **Say:** "A calibrated detector fires only 2.5 times a day, and it still loses to the gate."

**Drag to off.** **Say:** "Off, it's the plain single-head model, which the gate beats by 0.0083 on 22 of 22 days. Across these 20 tested settings, this recipe never beats the state gate. That's a post-hoc demo sweep, labelled as such, and its 1e-3 setting reproduces the committed result exactly."

### 2:25–3:00 · Fees (section 3) · `06_fees_vip9_100ms.png`

**Click** `VIP 9`, `100 ms`, then the `Regime gate` policy.

**Say:** "The signal is real, about 0.3 basis points gross. But break-even is 0.13 per side against taker fees of 1.7 or more. It is not tradable as a taker after fees. The maker number is an optimistic bound."

**Close:** "Across 20 tested settings, this KS-refit recipe never beat the state gate. Conditioning on state was better on 22 of 22 held-out days."

---

### Optional, if time allows · Stress test (section 4, SEMI-SYNTHETIC) · `07_splice_…_SEMI-SYNTHETIC.png`

**Say:** "We spliced the calm day into the most volatile one at a known time. Prices are shifted additively by whole ticks, so labels are unchanged. Textbook KS fires 12 to 36 times before anything changes. The gate takes the best post-splice loss in 10 of 10 splices. It's a stress test, not held-out evidence."

**Appendix slides:**
- `A1`: lower-median day at 1e-30.
- `A2`: most volatile day at 1e-30, where the test still fires 48 times.
- `A3`: FOMC dev day, illustrative only.
- `A4`: the details drawer, with the full sweep and the training-day rejection rates.

---

## Five hardest questions (from the demo review)

| Question | Answer |
|---|---|
| "Is 1e-30 just SciPy underflow? Are those actually false alarms?" | No window, training or held-out, has D = 1 or p = 0. The exact complete-separation probability, about 10^-218.5, is a different calculation. The inset is a *training-day rejection rate* under realistic, heterogeneous days, not a verified false-alarm rate. The operational evidence is that acting on these alarms worsens the forecast loss. |
| "Was the holdout unseen, and did your registered hypothesis succeed?" | One of the 22 days, 2025-08-01, was evaluated in our earlier v1 run. Excluding it leaves the gate/static result intact: clean-21 Δ −0.0099 [−0.0140, −0.0067]. H1 failed; H2 succeeded. The gate comparisons are pre-registered secondary, shrinkage is post-dev, and the dial and head-only ablations are post-hoc. |
| "Have you proved detect-and-retrain cannot work?" | No. We tested this frozen recipe at 16 naive levels, 3 empirical quantiles and off. All 20 lose to the gate, with 0/22 days better at each. That is consistent evidence against *this recipe on these days*, not a theorem about all detectors or retraining designs. |
| "Is the gate just one better head, or an oracle about the future?" | All heads and thresholds are fitted on 2023, and the gate selects on *trailing* 10-minute volatility. The high-vol head alone is +0.0141 worse pooled and beats the gate on 1/22 days. Head usage is 20.7/33.2/46.0%. This ablation is exploratory. The loss scores direction *given a non-zero move*: ties are excluded, and 68% of the calm day's steps are ties. |
| "What can Optiver actually trade?" | No profitable strategy is demonstrated. At 100 ms, the gate's break-even fee is 0.132 bps/side against a VIP 9 taker fee of 1.7, giving −3.14 bps/signal net. The passive +0.29 is an optimistic bound with no queue or adverse selection. Quoting value is untested. The gate + shrinkage Python reference step has p99 85.6 µs; end-to-end latency is not established. |

**Also if asked:**
- **Day choice:** the held-out days are picked by rule on committed mean `rv_600s`: the calmest, the lower median and the most volatile.
- **2024-05-01:** this is a dev day (FOMC), so it is illustrative only.
