# Ghost Market: 3-minute talk track (P5)

Start: `perceptron-p05-impact-execution/demo/run.sh`. It opens Act 1 and auto-plays seed 100 at 60×. Keys: `1`–`5` switch acts, `space` plays or pauses, `←`/`→` scrub 30 s. Every screen carries the stamp **SIMULATED (ABIDES rmsc04)**: P5 has no real market data. Every number below is a key in `eval/results/claims.json` or comes from a committed results file.

## Act 1: Ghost market (0:00–1:10)
- **Say:** "We sell 4,000 shares of a $1,000 stock between 09:35 and 09:55, inside an exchange of 1,116 simulated traders. On the right is the same market and the same seed without our order. We call it the ghost."
- **Point at** the badge as the playhead crosses 09:35. It reads **"pre-trade top-5 book events identical: 738/738"**: every logged book state before our first trade is identical, field by field.
- **Point at** "book levels differing from the ghost": it reads 0/10 until 09:35, then the books split. The red strip underneath is our footprint (ghost mid − our mid), live.
- **Click** order size **16k**. "Four times the shares; the mean footprint at 09:55 goes from **3.7¢ to 12.3¢**."
- **Scroll** to *Impact vs order size*. "Impact grows roughly linearly. The registered slope is **1.01 [0.55, 1.76]**, while real markets follow a square-root law (≈0.5; the dashed line is a literature reference from Tokyo Stock Exchange data, not our result). That means a realism gate is still needed, and we show it rather than hide it."
- **Point at** *Where our 4,000 shares ended up*: "Value agents end up holding **102%** of what we sold. **No momentum amplification detected** (+70 shares, CI [−60, +204]). This is the E10 TWAP arm, n = 400."

## Act 2: Why the twin matters (1:10–1:50) — press `2`
- It opens on **Naive twins**. "Without synchronised randomness, our first trade shifts every later random draw, so the ghost wanders off. The gap std at 09:55 is **22.9¢**, against a mean footprint of a few cents."
- **Click Synchronised twins** (or press `S`). The fan collapses to **5.3¢**. "Same 30 seeds, same orders; only the coupling changed."
- **Point at** **6×** (own-impact dispersion 0.97 → 0.16 bps) and **7.7×** (tighter paired CIs). Then name the cost honestly: spreads are **13%** wider in synchronised worlds.

## Act 3: TWAP vs impact-aware (1:50–2:15) — press `3`
- "Same ghost, two strategies, one seed. The cost table splits shortfall into drift, own impact and instant."
- **Point at** the strip of 30 dots: "One seed tells you nothing. Dots land on both sides of zero, so the aggregate is in Act 4."

## Act 4: Honest scoreboard (2:15–2:45) — press `4`
- Let the rows appear in turn. "E6, with the hypothesis fixed before we looked: **−0.034 bps [−0.056, −0.013]**. E8 validation did **not reproduce** it: +0.006. E10, the strict pre-registered replication on 400 new seeds: **−0.013 [−0.029, +0.003], NOT confirmed**. Pooled, descriptive only: −0.020."
- **Point at** the headline: **"We do not claim to beat TWAP."** Then the bars on the right: "Per-seed noise without the twin is **0.97 bps**; the E6 point estimate is **0.034 bps**. Without the twin we could not even ask the question."

## Live: your seed (2:45–3:00) — press `5`
- Ask a judge for any number and type it in as the seed, then **Run twin pair** (about 5–10 s). The badge lights up ("1 new seed (live, synced)") with its own top-5 identity count, and the ring lands on the impact-vs-size chart.
- Seeds 100–129 reproduce the committed E7/E8 rows exactly; seed 101 gives −8.0¢ (TWAP) and −7.0¢ (impact-aware).
- If the status reads "live paused (memory guard)", say so and show `fallback/5-live-seed-2026.png`.

**Fallback:** `fallback/*.png` covers every screen in talk order (1a, 1b, 1c, 2a, 2b, 3, 4, 5).
