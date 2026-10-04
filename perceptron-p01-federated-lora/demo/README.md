# P1 demo: pull the plug

The demo has three parts:

- **Committed results first.** These are the committed runs from `eval/results`: 4 strategies × 5 paired seeds, a real model and real text.
- **Live "pull the plug" run.** This runs on this Mac's CPU. Two federations train side by side: the starter and AnchorLoRA. The run holds after round 1; the judge pulls the tablet's plug and resumes, and both federations lose the tablet from round 2 on (the pre-validated scenario).
- **Honest costs.**

The talk track is [SCRIPT.md](SCRIPT.md).

## Fetch, run, smoke

```bash
cd perceptron-p01-federated-lora
demo/run.sh        # opens the page; committed results work with system python3 alone
demo/fetch.sh      # once, needs network: .venv (uv, Python 3.11, pinned requirements) + SmolLM2-135M into the HF cache
demo/run.sh        # now the LIVE panel is enabled; everything runs offline, CPU only
demo/smoke.sh      # headless, no GPU, under nice 10; exit 0 = pass (about 1-1.5 min)
```

- `demo/run.sh --port N --no-browser` picks the port; the next free port is used if N is busy.
- Without a venv, `SMOKE_REPLAY_ONLY=1 demo/smoke.sh` runs everything except the real-engine checks. The output says that the live path is not checked.
- The smoke's page check uses an installed Chrome/Chromium/Edge in headless mode (`--dump-dom` of `web/index.html?selftest=1`, a `file://` page, no network). It is skipped with a WARN, not a failure, if no such browser exists. No pip or npm packages are needed.

**Time to first visual (measured 4 Oct 2026, ~20:55 IST, on this Mac, from a clean copy of the committed folder):**

- The server is ready 0.55 s after `demo/run.sh`.
- The page renders in 0.06 s, with all committed charts drawn (Playwright Chromium, 1440×900).
- The browser launch comes on top of that. This needs no venv and no model.

**Fetch, with wheels already in the uv cache and the model already cached:** 2.8 s.

**`demo/smoke.sh` after the demo-review fixes (4 Oct, 22:04 IST):** PASS, 132 checks in 60 s.

**Stage flow with the real engine (same evening, browser at 1440×900):** the hold after round 1 was reached 17–22 s after Start. *Stop live and play RECORDED* switched 0.18 s after the click, and the engine process was gone.

**Live timings, measured the same evening on CPU (nice 10, 4 threads), while other projects shared the machine (load average 3–8):**

- Model load plus untuned evaluation: about 8 s with a warm cache, 20 s cold.
- Each round, covering both federations and the evaluation: 10–35 s.
- A full 6-round run: 90–205 s.
- Peak memory: 1.2–1.3 GB (one model copy).

## Stage flow (event-gated)

1. **S** (or *Start live run*) starts one engine process. It loads the model, measures the untuned model and runs round 1 of both federations.
2. The server then asks the engine to hold (its own "pause after this round"). Once round 1 is finished in both federations, the stage band reads *Round 1 complete — pull the tablet plug, then Resume*. It also shows a projection computed from the actual history, for example "its round-1 update is reused in rounds 2–5 and expires in round 6". No expiry is promised if AnchorLoRA holds no cached update.
3. The judge clicks the tablet (or presses **T**), then *Resume* (**R**). The tablet is out from round 2 in both grids: exactly the pre-validated scenario.
4. Plug changes are accepted only from round 1 on, and only while a later round remains. The server refuses the others, and the page disables the sockets and says why.
5. The panels always show the last round finished by **both** federations; device training in progress is shown separately.
6. Next to the curve, a caption compares the run with its ghost (same seed, nobody unplugged).
   - For the pre-validated history it adds the reviewers' sentence, with the ranges read from `validation/results.json`.
   - Any other history is labelled *combined intervention effect in this run*, and the band is labelled a reference for a tablet-only outage from round 2.
7. *Stop live and play RECORDED* stops the engine first. The page switches only after `/api/stop` returns and the status confirms no running engine. The Start/Stop controls and the memory banner always reflect the real engine process.
8. The memory banner shows the active reason and threshold:
   - *Waiting to start: level 29; requires ≥ 30*
   - *Paused during training: level 24; resumes at 30*

## What is real, what is live, what is simulated

| on screen | status | source |
|---|---|---|
| Tabs 1, 2, 4: per-domain gains, ledger, outage curves, round strip, costs | **REAL, committed**: SmolLM2-135M, five real-text domains, 5 seeds × 4 strategies | `eval/results/v2_canonical.json`, `v2_dropout_canonical.json`, `logs/v2_dropout_*_s*.json`. The key is printed under every number. |
| Tab 3, LIVE | **computed now** by committed code | `demo/live_engine.py` → `components/flower_adapter` (FlowerLoraStrategy, ClientApp, LocalGrid) → `components/aggregator/strategies.py` |
| Tab 3, ghosts and band | **pre-recorded** by the same engine, same config and seed; the band covers 5 validation seeds | `demo/validation/runs/`, `demo/validation/results.json` |
| Tab 3, RECORDED | **recorded**: the validation run of seed 0 with the scripted unplug, replayed from its own events | `demo/fallback/recorded_live_s0.jsonl` |
| Device classes, ranks, step budgets, availability | **SIMULATED** assumptions; all five devices run on this Mac | `components/device_simulator/profiles.py` |

### The live configuration

The live panel uses the committed configuration: strategies `fedavg_ab_homo` and `anchor_full`, ranks 16/8/4/2/4, local steps 16/8/4/2/4, lr 1e-3, LoRA r_max 16 on q/v, and the seeded dropout draws. The exceptions are:

- **Batch:** 1×64 tokens (the first 64 tokens of each committed block) instead of 4×128.
- **Evaluation:** 8 held-out blocks per domain, every 6th of the 48 blocks, 64 tokens each, at every round.
- **Rounds:** 6.
- **Outage:** the forced tablet outage is removed, so the judge supplies the outage.

Values are deltas against the untuned model on the same subset. They are not comparable in absolute terms to the committed runs.

An unplug calls `LocalGrid.kill_node` in both grids from the next round on. This is an in-process node removal, not an OS-process kill. CPU is forced by patching `components.local_trainer.trainer.pick_device` from demo code; `components/` is unchanged.

### Pre-registered validation of the live configuration

Full table: [validation/RESULTS.md](validation/RESULTS.md). Seeds 0–4 were all run; none was picked. Each seed has a ghost run (nobody unplugged) and an unplug run (tablet out in rounds 2–6). Three criteria were set in advance:

- **P1:** AnchorLoRA's man-pages loss is below the untuned model's at every live round.
- **P2:** at round 6, the starter's man-pages loss is above both the untuned model's and AnchorLoRA's.
- **P3:** the unplug's own effect at round 6 (unplug run − ghost run) is larger for the starter.

**Result: all three pass in all 5 seeds.** Round 1 was bit-identical between the ghost and unplug runs of every seed.

`demo/smoke.sh` checks the following:

- **Validation runs and verdict:** P1/P2/P3 are `true` (not merely present) and the verdict covers seeds 0–4. Each run has both strategies × rounds 1–6, the exact tablet-only outage (none for a ghost) and finite losses.
- **Fallback:** the fallback PNGs and GIF exist and are valid images.
- **Stage flow, through the server with a protocol double of the engine (`fake_engine.py`):**
  - the hold after round 1;
  - a plug refused before round 1 and refused in the final round;
  - memory reasons and thresholds;
  - an awaited stop.
- **Page self-test in headless Chrome at 1440×900:** all four tabs, the labels and key values, the stage elements inside the 1440×900 box, the hold → plug → resume flow, the last-round-both-finished panels, expiry, the caption sentence, the custom-history label, both memory banners, and the RECORDED handoff with a refused stop and an awaited stop.
- **Real engine, through the server:** it holds after round 1, takes the tablet unplug, resumes, runs round 2 and stops on request. Rounds 1–2 equal the committed seed-0 ghost and unplug runs bit for bit, and the Flower path equals the in-process harness `run_experiment` for round 1, with a maximum difference of 0.0.

In the words shown next to the live curve: "Most of this gap exists even with nobody unplugged. In the five validation seeds, removing the tablet changed the starter's final man-pages loss by +0.009 to +0.029 and AnchorLoRA's by −0.002 to +0.008. The full system was less sensitive; this comparison does not isolate memory's contribution."

## Memory guard

The engine starts only when `kern.memorystatus_level` ≥ 30. It pauses while the level is below 25 and resumes at ≥ 30, and the page then shows *Paused for memory*. There is one model copy, in one engine process. `demo/validate.py` runs one seed at a time.

## Files

- `run.sh`, `fetch.sh`, `smoke.sh` (+ `smoke_checks.py`): run, fetch and smoke-test the demo.
- `server.py`: stdlib server. It serves `web/`, starts the engine and relays its events over SSE. It runs the stage hold, gates plug changes, annotates memory events, and stops the engine on request (awaited).
- `fake_engine.py`: protocol double of the engine, with no model. Only `smoke_checks.py` uses it, via `P1_DEMO_TEST_ENGINE`.
- `live_engine.py`: the live engine. It prints JSON events on stdout and takes commands on stdin.
- `validate.py`: the pre-registered validation runner and its table.
- `export_replay.py` → `web/data.js`: every number the page shows, built from the committed sources. `--check` detects a stale `data.js`.
- `web/index.html`, `web/app.js`, `web/style.css`: one offline page, vanilla JS and SVG, no libraries, no CDN.
- `render_fallback.py` → `fallback/*.png`, `fallback/recorded_live.gif`: matplotlib frames built from the same `data.js`.
- `fallback/recorded_live_s0.jsonl`: the RECORDED run that the page can replay.
- `.live/` (gitignored): an event recording of every live session and the engine log.

## Wording

Say:

- "full-system comparison under paired availability"
- "magnitude diagnostic" (for the norm share)
- "at the evaluated rounds"
- "simulated device budgets"

Do not claim:

- "unbiased"
- "minimal upload"
- RAM or throughput savings
- a "fairness cap"
- "no spike" between checkpoints
- matched-work attribution
