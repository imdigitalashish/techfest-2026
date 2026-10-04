# Ghost Market: 3-minute talk track (P5), in 3 beats

Start: `perceptron-p05-impact-execution/demo/run.sh`. It opens on **The answer**. Keys: `1`–`5` switch screens, `space` plays or pauses, `←`/`→` scrub 30 s. Every screen carries **SIMULATED (ABIDES rmsc04)**: P5 has no real market data. Every number below is a key in `eval/results/claims.json`, or comes from a committed results file through `demo/export.py` (checked by `demo/smoke.sh`).

## Beat 1: the answer first (0:00–0:20), screen 1
- **Say:** "Answer first. We sell 4,000 shares over 20 minutes, once with TWAP and once with our impact-aware agent, on the same seeds. On 400 fresh seeds, under a rule we registered before running, the difference is **−0.013 bps, CI [−0.029, +0.003]**. That is **not confirmed**. We do not claim to beat TWAP."
- **Point at:** the **NOT CONFIRMED** label, then the highlighted **E10** row. The bars show that the mean costs are **0.455** (TWAP) and **0.442** bps (our agent).
- **Click** **Here's why you can trust that answer →**.

## Beat 2: why you can trust that answer (0:20–2:20)
**Ghost market (screen 2, 0:20–1:20).** The replay auto-plays at 120× and freezes at 09:55 (T1) after about 12 s.
- "Right panel: the same market and the same seed without our order. We call it the ghost."
- **Point at** the badge as the playhead passes 09:35: **"pre-trade top-5 book events identical: 738/738"**. Then **"book levels differing from the ghost"** jumps from 0/10. The red strip is our footprint (ghost mid − our mid).
- **Size challenge:** click **16k**. The view stays frozen at 09:55. **Point at** the readout beside the knob: **12.3¢ mean, 95% CI [+9.3, +15.2]** over 30 seeds. Click **4k** to compare: **3.7¢ [+1.8, +5.5]**.
- **Scroll** to *Impact vs order size*. "Impact grows roughly linearly. The registered slope is **1.01 [0.55, 1.76]**, with **75%** of bootstrap draws usable. The real-world law is square-root (≈0.5, a TSE literature reference, not our data), so a realism gate is needed."
- **Holdings** (an E10 aggregate, fixed at 4,000 shares): value agents end up holding **102%** of what we sold, and **no momentum amplification** is detected.

**Coupling (screen 3, 1:20–2:05).**
- "In naive twins, our first trade can desynchronise state-dependent random draws, so the ghost wanders." **Point at** the gap std at T1: **22.9¢**.
- Press **S**: the synchronised twins re-key every background agent's random stream, and the std becomes **5.3¢**.
- **Point at** **7.7×**: the paired-difference std is 7.7× smaller (median of 4 policies, same 60 seeds). **6×**: own-impact dispersion falls from 0.97 to 0.16 bps.
- Name the price: spreads are **13%** wider in synchronised worlds.
- "The twin coupling made the paired difference measurable; the ghost attributes it."

**One seed (screen 4, 2:05–2:20), optional.**
- "The same ghost and both strategies, with the cost split into drift, own impact and decision-to-fill (delay + at-fill concession)."
- **Point at** the strip of 30 dots on both sides of zero: one seed cannot establish an average advantage. That is why screen 1 uses 400 seeds.

## Beat 3: the judge's seed (2:20–3:00; keep at least 20 s)
- Press **5**. Ask a judge for any whole number from **0 to 2,147,483,647** and type it in. Press **Enter**.
- In about 5–10 s, three fresh worlds run. Invalid input is rejected and never replaced by a different seed.
- **Point at** the badge, **"1 new seed (live, synced)"**, and its own top-5 identity count, e.g. **731/731** for seed 20261004.
- Then point at the cost table with the delay/at-fill split, and at the ring on the E7 chart. Seed 20261004 makes our agent **+0.154 bps worse**: shown, not hidden.
- If the status reads "live paused (memory guard)", say so and show `fallback/5a-live-seed.png`.
- **Close:** "Simulated and model-conditional. We built the instrument, the counterfactual accounting and an honest null."

**Fallback:** `fallback/*.png` covers every screen in talk order (1, 2a–2c, 3a–3c, 4, 5a, 5b).
