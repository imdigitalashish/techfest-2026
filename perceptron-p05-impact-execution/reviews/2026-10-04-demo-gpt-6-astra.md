# Hostile finals demo review: GPT-6 Astra

Reviewed `ef608074` against PLAYBOOK section 11, the reviewed abstract, `claims.json`, and `eval/preregistration.md`. Lens: Optiver quant researcher / IIT Bombay professor.

**Overall: 3.5/5, core-task weighted.** A compelling measurement instrument, not yet a demonstrated solution to the slippage-reduction objective. The ghost earns attention; the execution agent arrives too late.

## What actually ran

Created the requested Python 3.11 venv and fetched pinned ABIDES. Memory level was 50 at launch; the server ran at nice 10, CPU-only. Walked all five acts using 1440x1000 and 1280x800 viewports. Exercised all five sizes, both coupling states, and multiple replay seeds.

Fresh live seed **20261004**, 4,000 shares: **4.8 s** server time, **7.3 s** click-to-green-badge, **731/731** pre-trade events identical. Both arms completed; TWAP/agent T1 footprints were **+2.5/+6.5 cents**, and agent-minus-TWAP shortfall was **+0.154 bps**: worse, without being hidden.

`bash demo/smoke.sh` passed, including seed 101's -8/-7-cent reproduction. READY took **0.9 s**; browser first contentful paint took **100 ms after navigation**. Reloaded with non-local requests blocked: all assets local, all acts functional. Direct `file://` inspection was blocked by the browser tool, not the demo. All eight fallback images carry SIMULATED; four review screenshots are gitignored. Killed server PID 70971 and verified shutdown.

## Scores

| Criterion | /5 | Evidence |
|---|---:|---|
| You did what we asked | 3 | TWAP and agent costs/schedules are side by side in Act 3/live, but only at 1:50 in the script; confirmed total-slippage superiority remains unmet. |
| Crazy element | 4 | Identical pre-trade books diverging after intervention, then the 22.9-to-5.3-cent fan collapse, is a genuine reveal. |
| Knob responsiveness | 4 | Size buttons responded in 31-35 ms; coupling animates smoothly and fresh computation works. The headline quantity does not follow the knob. |
| Honesty | 3 | SIMULATED everywhere, CSV-backed numbers, and prominently failed E10 replication; several labels nevertheless claim more than their statistics establish. |
| Robustness | 5 | Fast startup, passing smoke/live checks, offline-local operation, eight recorded fallbacks, no browser console errors. |
| Three-minute clarity | 3 | Clear click instructions, but five acts and many metrics bury the requested agent. At 60x, the 35-minute replay finishes in 35 seconds inside a 70-second opening act. |

## On-screen corrections and missing qualifications

No fabricated result number found. Traceability does not make the following interpretations or bindings correct:

1. **Act 1: "We sell 4,000 shares"** remains after selecting 1k, 2k, 8k or 16k. Bind this quantity to the selection. Keep the separate, explicitly 4,000-share holdings panel labelled as a fixed E10 aggregate.
2. **Act 1: "registered slope 1.01 [0.55, 1.76]"** omits that only **75%** of bootstrap draws were usable (`realism_scorecard.json`). Add that qualification beside the interval, not merely a preregistration link. The point estimate is not a clean rejection of realistic concavity.
3. **Act 2: "our first trade shifts every later random draw" / "re-key every agent's random stream"** overgeneralise. `world.py` re-keys background agents, not the exchange or execution agent. Say "can desynchronise state-dependent draws" and "background agents."
4. **Act 2: "7.7× tighter paired confidence intervals"** is actually the median paired-shortfall **standard-deviation ratio across four policies**, calculated in `eval/claims.py:g_ci_tightening`. Label that statistic accurately; it is not a measured bootstrap-CI-width ratio.
5. **Act 2: "33¢" ... "against a mean impact of 3.2¢"** mixes horizons. `gap_mean_300` is the five-minute mean; the same E1 JSON's 20-minute mean is **-2.288 cents**. State both horizons, or compare like with like.
6. **Act 3: "single-seed differences are noise"** and live **"1 seed: noise"** assert what cannot be identified from one observation. Replace with "one seed cannot establish an average advantage."
7. **Act 3: "instant (spread and book-walking)"** mislabels the displayed term in both cost tables. `tca/metrics.py` includes decision-to-fill mid movement. Rename it "decision-to-fill cost (delay + at-fill concession)," or expose the existing split.
8. **Act 3 strip: "−0.43"/"+0.43"** edge labels actually sit at approximately **-0.470/+0.470 bps**: `drawA3` expands the scale by 1.1 but not its labels. Relocate the ticks or label the expanded endpoints.
9. **Act 4: "Why sub-tick claims need the twin" / "The twin made a 0.034 bp difference measurable"** confound RNG coupling with the no-order world. Total paired shortfall can be measured without a post-trade ghost; the ghost enables attribution. **"the result does not replicate"** should say "E10 did not confirm superiority," not imply proven absence. Apply these corrections to the fallback's older **"0.03 bp"** wording too.
10. **Live: "Type any seed."** The client silently clamps values. State the integer range 0-2147483647 and reject invalid input rather than substituting another seed.

## Most likely judge question

**"Where is the evidence that your agent actually reduces total slippage?"**

Best honest answer: "Not established. E10's 400 fresh seeds gave -0.013 bps [-0.029, +0.003], failing confirmation. We built the schedule and reproducible counterfactual accounting, not a proven TWAP-beater. Even our coupling changes mean spreads by 13%; these are model-conditional results, not real-market performance."

## Three highest-impact changes

1. Open with TWAP/agent costs and the E10 verdict; make the ghost the explanation, not a two-minute detour.
2. Correct the labels above and distinguish coupling, counterfactual attribution, and unconfirmed execution performance.
3. Freeze the size challenge at 09:55, show aggregate T1 impact beside the knob, and simplify to three beats with at least 20 seconds reserved for the judge's live seed.
