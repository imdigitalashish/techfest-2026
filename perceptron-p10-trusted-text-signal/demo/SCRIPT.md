# SCRIPT — "Break the band" (3 minutes)

Setup, before the judges arrive:
- Run `bash perceptron-p10-trusted-text-signal/demo/run.sh`. It prints `first visual ready in ~6 s` and opens `http://127.0.0.1:8710/`.
- Check the two green pills (top right): **scorer: MiniLM-L6 + LR (deployed, CPU)** and **live ACI 89.50% = committed ✓**. If the scorer pill is amber (VADER fallback), say so out loud.
- The page opens on **D · 2016-03-28** (17 real posts).
- If anything fails live, switch to `fallback/` (screenshots 01–08, in this order).

---

**0:00 — The problem (15 s).** *Point at the header.*
> "Problem 10 asks for a confidence bound that stays meaningful when the text is manipulated. So today you are the manipulator. Your job is to break our interval with fake posts."

**0:15 — The honest framing first (20 s).** *Point at the footer, left to right.*
> "Three things up front. First, text adds no measurable forecast value: a pre-registered test on unseen DJIA news gave p = 0.46. Second, typical fake posts barely move the forecast: a 3-post pump shifts the median by 0.094 pp against a 4.76 pp interval. Third, the days in this list are **selected**. They are the 2% of stock-days where some tested attack can flip the plain interval. So the product is not alpha. The product is the guarantee under attack."

**0:35 — One fake post breaks the plain interval (35 s).**
1. Left panel: click **Bull pump (committed template)**, then **Fresh bot**. Trust reads **0.101**, computed live by `trust_of`.
2. Set **Copies = 1** and click **Score & inject**. MiniLM scores the post live: **+0.952**.
3. Point at the red card **Plain CQR broken**, then at the **edge zoom**.
> "One post from a day-old account with zero followers. The median moved 0.004 pp, almost nothing. But the realised return sat 0.027 pp inside the upper edge, and the post pulled that edge down 0.14 pp. The plain interval now misses a return it used to cover. Attacks don't swing the forecast; they nudge an edge across a return that was already close to it."

**1:10 — The certified band does not move off it (25 s).** *Point at the green card and the dashed guide lines.*
> "The certified band is computed from the posts we observe. We never learn which ones are fake. It is guaranteed to contain the no-injection interval for any 3 injected posts. That is a theorem, not a test. Removing up to k posts keeps every text feature inside this box (*point at 'Why it can't break'*), and we bound every tree in the LightGBM model over the box. It costs +4.8% width at k = 3."

**1:35 — Let the machine try (20 s).** *Scroll to the red-team panel; click **Run red-team**.*
> "Here 2,000 random attacks are thrown at this day. Within budget, plain CQR breaks about 1,800 times; certified containment violations: **zero**. Beyond budget the counter goes non-zero, which is honest: past k we promise nothing."

**1:55 — Past the budget, the badge turns off (15 s).** *Drag the post's **copies** slider to 6.*
> "Six posts against a budget of 3. The badge goes grey: NO GUARANTEE. You choose k; the price of each k is in the panel, +2.9% to +5.5% width."
*Drag copies back to 3.*

**2:10 — Your attack on every stock-day (30 s).** *Scroll to the replay panel; click **Replay on all 16,443 stock-days**.*
> "Now the population. The same 3 pump posts go into every stock-day from July 2015 to March 2016, recomputed live with the committed code. Plain CQR falls from 86.7% to **86.4%**; 144 stock-days flip. Certified holds **89.4%** and contains the clean interval on every row. Each green tick means the live number equals our committed result file."
*Point at the ACI meter.*
> "This is our adaptive conformal loop, recomputed live: 89.50%, identical to the committed run. Under the attack, CR-ACI holds 89.7%. That is a long-run coverage promise, not a per-row one."

**2:40 — Silent stocks (15 s).** *Click **PICO · 2015-07-06** (silent). The same post breaks plain again.*
> "207 of the 327 vulnerable days are stocks nobody posted about. There, the fake post *is* the signal. The certified band still holds."

**2:55 — Close (5 s).**
> "Fake text can't buy a miss within the budget you set, and you can check every number here against our committed results."

---

Numbers to point at, and where they come from:

| On screen | Value | Source |
|---|---|---|
| Live ACI pill / meter | 89.50% | `eval/results/text_minilm_v2.json` → `ablation.fusion.cqr_aci.coverage`, recomputed live |
| Pump replay: plain → certified | 86.7% → 86.4% / 89.4% | `attack.pump`, recomputed live |
| CR-ACI under pump | 89.7% | `spike.cr_aci.cr_aci_pump`, recomputed live |
| Flippable days | 327 of 16,443 (2.0%), 207 silent | `demo/bundle/showcase.json` (committed `oracle_grid(3)`; exploratory) |
| Text value | Winkler 3.524 → 3.520, p = 0.46 | `eval/results/text_utility_djia_v1.json` |
| Typical shift | +0.094 pp mean, 0.196 pp p95 | `attack.pump` |

Likely judge questions:
- **"Isn't the selected day cherry-picked?"** Yes. The selection rule and the 2.0% population rate are on screen, and the replay shows the population.
- **"Why did a *bullish* post lower the upper edge?"** Trust and dispersion are features too. A low-trust post lowers mean trust, and the upper quantile tree reacts. The certificate covers every feature at once.
- **"What isn't covered?"** Edits of real posts, price manipulation, poisoned calibration data. The guarantee is fixed-offset certified CQR. CR-ACI only promises long-run mean daily coverage.
