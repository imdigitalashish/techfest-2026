# P4 demo: "the alarm that cries wolf"

The demo is a live, offline page for the 10-second BTCUSDT mid-price direction forecaster. It shows four things:
- **Held-out scoreboard.** The committed results, with a status chip on every number. A "post-hoc: is it just one better head?" panel sits beside it.
- **Replay.** Real days computed live by the committed code: the static model, one EWMA head, textbook KS→refit, the regime gate, and the gate with CUSUM shrinkage. Alarm tracks and the active regime head are shown too.
- **The alarm dial.** The judge sets the textbook KS test's significance level α from 1e-1 down to 1e-300, or to "off". The judge can also pick the empirical-null mode. The replay and a 22-day held-out sweep follow the dial.
- **Execution knob.** Choose a fee tier, delay and policy to see the edge after fees.
- **Section 5, SEMI-SYNTHETIC stress test.** Two real held-out books are spliced at a time the judge picks, giving a changepoint whose time is known. The section shows who noticed the change, when, and who lost the least.

## Run

```bash
cd perceptron-p04-lob-regimes
demo/run.sh              # fetch missing data (one-off) -> page opens -> replay panels fill in
demo/smoke.sh            # headless: build, serve once, assert; exits non-zero on failure
```

What happens:
- **Fresh clone.** `run.sh` downloads only the missing days with `data/fetch_tardis.py`. These are free first-of-month Tardis.dev files and need no API key. Each file's MD5 is checked against the `x-md5` header and `data/manifest.csv`. Sixteen days are needed, about 473 MB:
  - the 12 training days, 2023-01 … 2023-12;
  - the replay days 2024-05-01, 2026-08-01, 2026-10-01 and 2026-03-01.
- **Offline after that.** The page, served on `127.0.0.1`, shows the committed scoreboard and dial sweep within seconds. The replay cache is then built on the CPU with `nice` and at most 3 workers. It takes about 3 minutes, and each day appears as soon as it is ready. Later runs reuse the cache.
- **Requirements.** Python 3.11 with numpy, scipy, polars and scikit-learn (as for `eval/`). The page vendors no JavaScript libraries; it uses plain canvas.
- **Options.** `demo/run.sh --no-open` skips opening the browser; `--build-only` builds without a server. `PORT=` and `WORKERS=` are honoured.

## Act 2: SEMI-SYNTHETIC splice (section 5)

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
| Dial: 22-day sweep, "why" inset | `demo/results/alarm_dial_sweep.json` (`build_sweep.py`) | post-hoc demo sweep, not pre-registered |
| Replay curves, alarms, per-day totals | `demo/.cache/replay_<day>.json` (`build_replay.py`, gitignored) | live-computed |
| Section 5 splice stress test | `demo/.cache/splice_*.json` (`build_splice.py`, gitignored) | live-computed, **SEMI-SYNTHETIC** |

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
- the replay cache itself holds only 10-minute aggregates (OHLC candles, bin-mean losses, regime-head shares) plus alarm timestamps;
- committed files in `demo/` hold only per-day and 22-day aggregates. `smoke.sh` checks this.

The fallback images in `fallback/` show prices only as 10-minute candles.
