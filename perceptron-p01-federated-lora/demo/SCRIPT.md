# P1 demo: 3-minute talk track

**Setup, before the judges arrive (1 min):** `cd perceptron-p01-federated-lora && demo/run.sh`. The browser opens on tab **1**. If the live panel says "unavailable", run `demo/fetch.sh` once. On a screen smaller than 1440×900, zoom the browser to 90%.

Keys: **1–4** switch tabs, **S** starts the live run, **T** pulls or restores the tablet's plug.

| time | click | say | point at |
|---|---|---|---|
| 0:00 | Tab **1**, *Committed runs* | "Five simulated devices fine-tune the same real 135-million-parameter model, each on its own real text. The workstation holds 8× the data, and the Raspberry Pi can afford rank 2. These are committed runs: 4 strategies × 5 paired seeds, 12 rounds with dropouts and deadline cut-offs." | the labels *SIMULATED device budgets · real SmolLM2-135M · real text* |
| 0:15 | (same) | "Every baseline (the starter, FFA-LoRA, FlexLoRA) improves only Wikipedia, the data-rich device's domain. The other four domains end up worse than not training at all. AnchorLoRA improves all five." | orange bars below the line; teal bars above it; ledger **5/5** vs **1/5** |
| 0:30 | (same) | "On the mean loss over the five domains, AnchorLoRA beats the starter by 0.081, 95% interval 0.070 to 0.093, paired by seed. The workstation's share of the update's magnitude drops from 0.88 to 0.22. That is a magnitude diagnostic, not a fairness guarantee." | **−0.081 [−0.093, −0.070]**; **0.88** → **0.22** |
| 0:45 | **S** (starts the live run in the background: model load and round 1 take about 20–30 s) | – | the *LIVE* pill in the header |
| 0:47 | Tab **2**, *Tablet outage* | "In the committed runs the tablet goes offline for rounds 5 to 9. Under the starter its domain ends up 0.277 worse than untuned at its worst point (seed average). AnchorLoRA stays below the untuned loss at every evaluated round in every seed." | **+0.277** vs **−0.020**; teal line above 0 |
| 1:00 | **Play rounds** | "Here is why. ◐ is partial work the server keeps, where the starter's ✕ throws it away. ↺ is the server reusing an absent device's last update, for at most 4 rounds." | the tablet row: ✕ ✕ ✕ (starter) vs ◐ ◐ ◐ and ↺ (AnchorLoRA) |
| 1:15 | Tab **3**, *Live* | "This is live, on this laptop's CPU: the real model, two federations side by side, running through Flower's message API on an in-process grid. Now pull the tablet's plug." | the power strip |
| 1:20 | the judge clicks **tablet** (or **T**) during round 1 | "From the next round, both federations lose the tablet, at the same moment." | the chip *plug pulled · out from round 2* |
| 1:30–2:30 | watch rounds 2–6 (about 10–30 s each, depending on machine load) | "Watch the man-pages line. The starter's falls below the untuned model; AnchorLoRA's stays above it. Its chip says it is reusing the tablet's last update, age 1 of 4. At round 6 the memory expires and AnchorLoRA's line still holds. The dashed lines are the same run with nobody unplugged, recorded earlier by this same engine. The caption shows how closely the live run matched them before your click; 0 means bit for bit." | teal chip *reusing last update · age k/4* → *memory expired · age 5 > 4*; the caption *max \|live − ghost\| = 0* |
| 2:10 | (same) | "Most of the gap is the starter's domination, as the ghost shows. The unplug adds to the starter's damage, and AnchorLoRA's memory absorbs it. That held in all 5 pre-registered validation seeds. The band is their range." | the caption *unplug's own effect … Starter +x, AnchorLoRA +y*; the shaded band |
| 2:30 | optional knob | "Pull any other plug, even the workstation's. The system responds from the next round. Those outcomes are this run only, not pre-validated." | any socket |
| 2:35 | Tab **4**, *Costs* | "What it costs: equal weights trade the workstation's domain for the other four. The sample-weighted loss is 0.116 worse than the starter, and the worst domain is 0.057 worse. Device budgets are simulated; the model and the text are real." | **+0.116 [+0.107, +0.124]**, **+0.057 [+0.024, +0.089]** |
| 3:00 | – | "One command, offline, CPU only. Every number on screen carries its source." | the small mono keys under each number |

In the pre-registered validation (5 seeds, tablet out from round 2), the man-pages loss at round 6 relative to untuned was: starter **+0.076 to +0.140** (worse), AnchorLoRA **−0.026 to −0.040** (better). See `demo/validation/RESULTS.md`. Do not quote any other live numbers in advance.

**If live fails or is slow:** keep talking over the committed tabs. On tab 3, click **Play RECORDED run** (speed 4×). It is labelled RECORDED and replays the validation run of seed 0, the scripted version of the same unplug. Last resort: `demo/fallback/recorded_live.gif` and the PNG frames in `demo/fallback/`. A *Paused for memory* banner means the Mac is short of memory; training resumes on its own.

**Words to avoid:** unbiased, minimal upload, RAM/throughput savings, fairness cap, "no spike" between checkpoints, matched-work attribution. **Say instead:** full-system comparison under paired availability, magnitude diagnostic, at the evaluated rounds, simulated device budgets.
