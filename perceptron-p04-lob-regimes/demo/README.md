# P4 demo: "the alarm that cries wolf"

The demo is a live, offline page for the 10-second BTCUSDT mid-price direction forecaster. It has four sections:
1. **Held-out scoreboard.** The committed results, with a status chip on every number and a compact disclosure. The disclosure covers the one day seen in v1, the clean-21 sensitivity, and the fact that the loss is scored on non-zero moves while the edge includes all signals. The head-only ablation sits in a drawer.
2. **Stage.** In one 1440×900 view:
   - a real day replayed live by the committed code (static model, regime gate, and textbook KS→refit at the dial's α; 10-minute candles; alarm counts per 10 minutes; the gate's active head);
   - the **alarm dial** (KS α from 1e-1 to 1e-300, off, or an empirical-null quantile);
   - the hero alarm count and the 22-day verdict.

   A *Details* drawer holds all five policies, the live-vs-committed table, every alarm track, and the training-day rejection rates.
3. **Can you trade it?** Fee tier, delay and policy, each with its metric and policy-status chips. The section ends on "not tradable as a taker after fees".
4. **SEMI-SYNTHETIC stress test.** Two real held-out books are spliced at a time the judge picks.

## Run

```bash
cd perceptron-p04-lob-regimes
demo/run.sh              # fetch missing data (one-off) -> page opens -> replay panels fill in
demo/smoke.sh            # headless: build, serve once, data + browser assertions; exits non-zero on failure
python demo/capture_fallback.py   # regenerate the fallback deck (needs the cache)
```

What happens:
- **Fresh clone.** `run.sh` downloads only the missing days with `data/fetch_tardis.py`. These are free first-of-month Tardis.dev files and need no API key. Each file's MD5 is checked against the `x-md5` header and `data/manifest.csv`. Sixteen days are needed, about 473 MB:
  - the 12 training days, 2023-01 … 2023-12;
  - the replay days 2024-05-01, 2026-08-01, 2026-10-01 and 2026-03-01.
- **Offline after that.** The page, served on `127.0.0.1`, shows the committed scoreboard and dial sweep within seconds. The replay cache is then built on the CPU with `nice` and at most 3 workers. It takes about 3 minutes, and each day appears as soon as it is ready. Later runs reuse the cache.
- **Requirements.** Python 3.11 with numpy, scipy, polars and scikit-learn (as for `eval/`). The page vendors no JavaScript libraries; it uses plain canvas.
- **Readiness and failures.**
  - `run.sh` refuses an occupied `PORT=`. It prints "page live" only after its own server PID serves this page's marker.
  - If the replay build fails, the committed panels keep working, and the page shows the error with a pointer to `fallback/`.
  - Cache files are reused only if their schema, day, and hash of code and inputs all match. Otherwise they are rebuilt.
- **Smoke test.**
  - Data assertions: anchors, live == committed, licence resolution, and splice integrity.
  - A headless-Chromium browser stage:
    - day identity under cached switches and delayed out-of-order responses;
    - DPR 2 canvas sizes;
    - no overflow at 1280×720 and 1440×900;
    - the stage fits in one view;
    - visible failure states.

    It uses Python Playwright. If that isn't installed, smoke prints a loud **SKIPPED**.
- **Options.** `demo/run.sh --no-open` skips opening the browser; `--build-only` builds without a server. `PORT=` and `WORKERS=` are honoured.

## Act 2: SEMI-SYNTHETIC splice (section 4)

`build_splice.py` builds the splices; `run.sh` runs it after the replay, which takes about 1.5 min once.
- **Method.** Keep every snapshot of the calmest held-out day (2026-08-01) received before τ. After it, append every snapshot of the most volatile held-out day (2026-03-01) from the same time of day.
- **Price shift.** Day B's prices are shifted **additively** by an integer number of 0.1 ticks, re-rounded to the tick grid, so the mid is continuous at τ.
- **Coverage.** Both directions, at τ = 06, 09, 12, 15 and 18 UTC.

`smoke.sh` asserts, for every splice:
- features and labels before τ equal the unspliced day exactly (causality);
- labels after τ equal day B's own labels on every real mid move (shift invariance).

The one exception is an exact decimal tie whose sign comes from floating-point rounding in the committed labeler. It is reported on screen (at most 1 per splice). These are stress tests, not held-out evidence.

## Regenerate the committed aggregates

```bash
python demo/build_scoreboard.py                       # demo/results/scoreboard.json from eval/results/* (seconds)
data/fetch_batches.sh book_snapshot_5                  # all 22 held-out days are needed for the sweep
nice -n 10 python demo/build_sweep.py --workers 3      # demo/results/alarm_dial_sweep.json (~20 min)
```

## Where every number comes from

| Panel | Source | Status chip |
|---|---|---|
| Scoreboard, H1/H2, execution knob | `eval/results/v2_holdout.json` | pre-registered primary / secondary, post-dev secondary |
| One EWMA head, heads alone, head usage | `v2_holdout_posthoc_ablation.json`, `v2_holdout_posthoc_heads.json`, `head_usage.md` | post-hoc exploratory |
| Dial: 22-day sweep, training-day rejection rates (not a false-alarm rate) | `demo/results/alarm_dial_sweep.json` (`build_sweep.py`) | post-hoc demo sweep, not pre-registered |
| Replay curves, alarms, per-day totals | `demo/.cache/replay_<day>.json` (`build_replay.py`, gitignored) | live-computed |
| Section 4 splice stress test | `demo/.cache/splice_*.json` (`build_splice.py`, gitignored) | live-computed, **SEMI-SYNTHETIC** |

The demo imports `components/` and `eval/` unchanged. Each dial stop runs the committed `run_episode`, with α overridden through `dataclasses.replace(ctx, cfg=…)` or the empirical-null threshold through `dataclasses.replace(ctx, ks_thresholds=…)`.

`smoke.sh` asserts these anchors over all 22 held-out days:
- α = 1e-3 equals committed `ks_refit`, in per-day log-loss, alarm counts and the 22-day CI;
- "off" equals `static_enorm`;
- calibrated q = 0.999 equals `ksc_refit`.

On held-out replay days, every live-computed per-day log-loss must also equal the committed value to within 1e-9; the page shows ✓.

**Replay-day rule:**
- 2024-05-01 is a dev day, with the FOMC statement at 18:00 UTC. It is labelled "illustrative" and carries no held-out claim.
- The three held-out days have the lowest, lower-median and highest mean `rv_600s` in the committed `regime_by_day`.

## Data and licence

The data comes from Tardis.dev and is used for internal research and education under the Terms of Service, https://docs.tardis.dev/legal/terms-of-service, accessed 2026-10-04.

Clause 9.2 allows redistribution only of aggregated Derived Data at a resolution of 10 minutes or longer. So:
- raw files and any per-second series stay in `.data/` and `demo/.cache/`, both gitignored;
- the replay and splice caches hold only 10-minute aggregates: OHLC candles, bin-mean losses, regime-head shares, and alarm **counts** per 10-minute bin. They contain no alarm times; `smoke.sh` checks that every time field sits on a 600-s boundary;
- committed files in `demo/` hold only per-day and 22-day aggregates. `smoke.sh` checks this.

The fallback deck in `fallback/` is regenerated by `capture_fallback.py` in talk-track order. It shows prices only as 10-minute candles and alarms only as 10-minute counts.

This is a technical audit against clause 9.2, not legal clearance for external distribution: the current terms also make 9.2 subject to 9.5. The wider `eval/results/` research records are out of the demo's scope.
