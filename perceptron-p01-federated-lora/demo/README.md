# P1 demo: pull the plug

The demo has three parts:

- **Committed results first.** These are the committed runs from `eval/results`: 4 strategies × 5 paired seeds, a real model and real text.
- **Live "pull the plug" run.** This runs on this Mac's CPU. Two federations train side by side: the starter and AnchorLoRA. The judge pulls a device's plug mid-training, and both federations lose that device from the next round on.
- **Honest costs.**

The talk track is [SCRIPT.md](SCRIPT.md).

## Fetch, run, smoke

```bash
cd perceptron-p01-federated-lora
demo/run.sh        # opens the page; committed results work with system python3 alone
demo/fetch.sh      # once, needs network: .venv (uv, Python 3.11, pinned requirements) + SmolLM2-135M into the HF cache
demo/run.sh        # now the LIVE panel is enabled; everything runs offline, CPU only
demo/smoke.sh      # headless, no browser, no GPU, under nice 10; exit 0 = pass (about 1 min)
```

- `demo/run.sh --port N --no-browser` picks the port; the next free port is used if N is busy.
- Without a venv, `SMOKE_REPLAY_ONLY=1 demo/smoke.sh` checks the committed-results part only. The output says that the live path is not checked.

**Time to first visual (measured 4 Oct 2026, ~20:55 IST, on this Mac, from a clean copy of the committed folder):**

- The server is ready 0.55 s after `demo/run.sh`.
- The page renders in 0.06 s, with all committed charts drawn (Playwright Chromium, 1440×900).
- The browser launch comes on top of that. This needs no venv and no model.

**Fetch, with wheels already in the uv cache and the model already cached:** 2.8 s.

**`demo/smoke.sh` in that clean copy:** PASS in 86 s.

**Live timings, measured the same evening on CPU (nice 10, 4 threads), while other projects shared the machine (load average 3–8):**

- Model load plus untuned evaluation: about 8 s with a warm cache, 20 s cold.
- Each round, covering both federations and the evaluation: 10–35 s.
- A full 6-round run: 90–205 s.
- Peak memory: 1.2–1.3 GB (one model copy).

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

`demo/smoke.sh` also checks that a fresh 2-round live run reproduces the committed ghost and unplug runs bit for bit. It also checks that the Flower path equals the in-process harness `run_experiment` for round 1, with a maximum difference of 0.0.

Most of the round-6 gap comes from the starter's domination, which the ghost shows with nobody unplugged. The unplug's own effect is small, but it went the same way in every seed.

## Memory guard

The engine starts only when `kern.memorystatus_level` ≥ 30. It pauses while the level is below 25 and resumes at ≥ 30, and the page then shows *Paused for memory*. There is one model copy, in one engine process. `demo/validate.py` runs one seed at a time.

## Files

- `run.sh`, `fetch.sh`, `smoke.sh` (+ `smoke_checks.py`): run, fetch and smoke-test the demo.
- `server.py`: stdlib server. It serves `web/`, starts the engine and relays its events over SSE.
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
