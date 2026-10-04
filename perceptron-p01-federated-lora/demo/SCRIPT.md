# P1 demo: 3-minute talk track (event-gated)

**Before the judges arrive (1 min):**
- Run `cd perceptron-p01-federated-lora && demo/run.sh`. The browser opens on tab **1**. Present it at 1440×900 and 100% zoom.
- The pill in the header should read *LIVE · ready*. If it says *unavailable*, run `demo/fetch.sh` once, or use the RECORDED run (see below).

**Keys:** **1–4** switch tabs, **S** starts the live run, **T** pulls or restores the tablet's plug, **R** resumes (only while the run is holding).

**How the live run moves.** It is event-gated, not timed. After **S**, the engine loads the model and runs round 1 of both federations. Then it **holds**, and the stage band reads *Round 1 complete — pull the tablet plug, then Resume*. Nothing advances until you resume.

A plug change takes effect from the next round, so the page accepts one only while a later round remains. The stage band says when plug changes are closed.

Act on what the screen shows, never on the clock.

| state on screen | do | say | point at |
|---|---|---|---|
| tab 1, *LIVE · ready* | – | "Five simulated devices fine-tune one real 135-million-parameter model, each on its own real text. The workstation holds 8× the data; the Raspberry Pi can afford rank 2. These are committed runs: 4 strategies × 5 paired seeds, 12 rounds with dropouts and deadline cut-offs." | the labels *SIMULATED device budgets · real SmolLM2-135M · real text* |
| tab 1 | – | "Every baseline (the starter, FFA-LoRA, FlexLoRA) improves only Wikipedia, the data-rich device's domain. The other four domains end up worse than not training at all. AnchorLoRA improves all five." | orange bars below the line, teal bars above it; ledger **5/5** vs **1/5** |
| tab 1 | press **S** (the model loads and round 1 runs in the background) | "On the mean loss over the five domains, AnchorLoRA beats the starter by 0.081, 95% interval 0.070 to 0.093, paired by seed. The workstation's share of the update's magnitude falls from 0.88 to 0.22, as a round-and-seed mean. That is a magnitude diagnostic, not a guarantee." | **−0.081 [−0.093, −0.070]**; **0.88** → **0.22**; the pill turns to *LIVE · loading*, then *round 1/6* |
| tab **2** | **Play rounds** | "In the committed runs the tablet is offline for rounds 5 to 9. Under the starter its domain peaks 0.277 above the untuned loss (mean of 5 seeds). AnchorLoRA stays below the untuned loss at every evaluated round in every seed. ◐ is partial work that AnchorLoRA keeps; the starter's ✕ throws it away. ↺ is the server reusing the tablet's last update, for at most 4 rounds." | the tablet strip next to the curve; **+0.277** vs **−0.020** |
| the pill reads *LIVE · HOLD after round 1* (wait for it; tab 2 can run longer) | key **3** | "This is live, on this laptop's CPU: the real model, two federations side by side, running through Flower's message API on an in-process grid. Round 1 is done in both, and the run is holding for you." | the stage band |
| HOLD | the judge clicks **tablet** (or **T**) | "The tablet is out from round 2 in both federations. That is the scenario we pre-registered and checked on five seeds." Then read the projection line exactly as it is displayed, for example "its round-1 update is reused in rounds 2–5 and expires in round 6". Never promise an expiry the line does not show. | the chip *plug pulled · out from round 2*; the projection line |
| HOLD, plug pulled | **Resume** (or **R**) | – | – |
| rounds 2–6 running | – | "Watch the man-pages line: the starter's falls below the untuned model, and AnchorLoRA's stays above it. The chip shows the server reusing the tablet's last update; the age counts up to 4." If the chip then shows *memory expired · age 5 > 4*, say so. | the teal chip *reusing last update · age k/4*; both panels say *after round N* (the last round both federations finished) |
| the effect caption next to the curve shows *pre-validated scenario* | – | Read the caption's sentence: "Most of this gap exists even with nobody unplugged. In the five validation seeds, removing the tablet changed the starter's final man-pages loss by +0.009 to +0.029 and AnchorLoRA's by −0.002 to +0.008. The full system was less sensitive; this comparison does not isolate memory's contribution." | the dashed ghost lines (same seed, nobody unplugged); the caption |
| **cutoff: talk time 2:10, if the stage band does not yet say *Live run finished*** | click **Stop live and play RECORDED** (speed **16×**) | "We stop the live engine here. This is the same pre-registered scenario, recorded earlier by the same engine, labelled RECORDED." | the purple *RECORDED, not live* band |
| optional, only while the band says a later round remains | pull or restore any other plug | "Any device can be pulled or restored. The system responds from the next round. Such a history was not pre-validated, and the caption calls it the combined intervention effect in this run." | the caption's *not pre-validated* tag |
| 2:20, tab **4** | – | "What it costs: equal weights trade the workstation's domain for the other four. The sample-weighted loss is 0.116 worse than under the starter, and the worst domain is 0.057 worse. The device budgets are simulated; the model and the text are real." | **+0.116 [+0.107, +0.124]**, **+0.057 [+0.024, +0.089]** |
| 3:00 | – | "One command, offline, CPU only. Every number on screen carries its source." | the small mono keys under each number |

**Validation numbers (from `demo/validation/RESULTS.md`):** the pre-registered validation covered 5 seeds, with the tablet out from round 2. Man-pages loss relative to untuned at round 6 was:
- starter **+0.076 to +0.140** (worse)
- AnchorLoRA **−0.026 to −0.040** (better)

Do not quote any other live numbers in advance.

**If live is unavailable, slow, or the yellow banner says *Paused during training* or *Waiting to start*:**
1. Click **Stop live and play RECORDED**. It stops the engine first and switches only after the server confirms the stop.
2. If the stop fails, the band says so and the live controls stay active.
3. Last resort: `demo/fallback/recorded_live.gif` and the PNG frames in `demo/fallback/`.

**Words to avoid:** unbiased, minimal upload, RAM/throughput savings, fairness cap, "no spike" between checkpoints, matched-work attribution. Also avoid claiming that memory "absorbs" or "saves" anything: the comparison does not isolate it.

**Say instead:** full-system comparison under paired availability, magnitude diagnostic, at the evaluated rounds, simulated device budgets.
