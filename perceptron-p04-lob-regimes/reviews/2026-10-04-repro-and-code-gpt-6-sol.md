# Independent v2 holdout reproduction and code review (2026-10-04)

## Verdict
- **Exact reproduction:** all 17 policy summary objects and all 374 per-day non-timing records match the committed holdout JSON; only run metadata and timings differ.
- **Forecast conclusion unchanged:** the registered `spike` does not beat static at the specified CI level, but beats `ks_refit`; post-dev `spike_gate` beats both and trails plain `regime_gated`.
- **Holdout caveat:** 2025-08-01 was previously reported in the v1 holdout, so the full 22-day set was not untouched; excluding that day in a post-hoc paired-day sensitivity check leaves these conclusions unchanged.
- **Edge caveat:** `summary.*.edge_bps` excludes zero-move ties and overstates all-signal gross edge by about 32%; the separate 100 ms trading-edge table includes ties and is correctly negative after taker fees.
- **Causality:** no look-ahead found in the current receive-time features, 10 s labels, or online updates; the availability contract, last-day execution boundary, and number checker have smaller gaps below.

## Environment + exact commands run

Darwin 25.2.0 arm64 (macOS 26.2); Python 3.11.14, NumPy 2.2.6, SciPy 1.17.0, scikit-learn 1.8.0, Numba 0.65.0, pytest 9.1.1. The code/configuration at reproduction commit `8c183b9` is unchanged from the reported run's `a9b310b` for `components/`, `eval/run_v2.py`, and `eval/config_v2.py`. Data came from the existing linked cache, without downloading anything.

```sh
# From the repository root:
ln -s /Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-bookish-potato/perceptron-p04-lob-regimes/.data perceptron-p04-lob-regimes/.data
cd perceptron-p04-lob-regimes
for day in 2023-01-01 2024-07-01 2026-10-01; do
  actual="$(md5 -q ".data/raw/tardis/binance-futures/book_snapshot_5/${day}_BTCUSDT.csv.gz")"
  expected="$(awk -F, -v day="$day" '$3==day {print $7}' data/manifest.csv | tr -d '\r')"
  test "$actual" = "$expected" || exit 1
done
PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' nice -n 10 python3 -m pytest -q tests
sysctl -n kern.memorystatus_level
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 eval/run_v2.py --stage holdout --tag repro_v2_holdout_sol --workers 3
mkdir -p reviews/repro
mv eval/results/repro_v2_holdout_sol.md eval/results/repro_v2_holdout_sol.json reviews/repro/
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 eval/check_numbers.py
```

The three raw MD5s matched `data/manifest.csv`: 2023-01-01 `5246f1649a0840869dbc7ca38a38e4c7`, 2024-07-01 `1c1a0c5a3a55d20d6ef595ac103401fb`, 2026-10-01 `08b4ba38d0793be088b5f9ef8eb8c778`. Tests: **8 passed**, with six numerical `RuntimeWarning`s. `kern.memorystatus_level` was **25** immediately before the single three-worker run; the run exited 0 in **582.1 s** (the reported run took 246.6 s on the shared machine), with 858 numerical warnings during fitting/refitting. `check_numbers.py`: **163 quotations across five documents, OK**. Outputs are `reviews/repro/repro_v2_holdout_sol.{json,md}`; `eval/results/v2_holdout.{json,md}` was not modified.

## Reproduction table

Values are displayed to six decimals; **Exact** means equality at full JSON numeric precision, not merely equality after rounding (zero tolerance). "CI" is the two-sided 97.5% paired day-cluster bootstrap interval; comparisons also give days better out of 22. Edge quantities are bps of mid, ordered gross / taker before fees / entry spread / break-even fee per side.

| Metric | Reported | Reproduced | Match? |
|---|---|---|---|
| `static_snorm` pooled log-loss / AUC | 0.651830 / 0.666119 | 0.651830 / 0.666119 | Exact |
| `ks_refit` pooled log-loss / AUC | 0.678633 / 0.638741 | 0.678633 / 0.638741 | Exact |
| `regime_gated` pooled log-loss / AUC | 0.641903 / 0.675239 | 0.641903 / 0.675239 | Exact |
| `spike` pooled log-loss / AUC | 0.650830 / 0.664665 | 0.650830 / 0.664665 | Exact |
| `spike_gate` pooled log-loss / AUC | 0.642490 / 0.674578 | 0.642490 / 0.674578 | Exact |
| `static_gbdt` pooled log-loss / AUC | 0.646640 / 0.671123 | 0.646640 / 0.671123 | Exact |
| `static_wf` pooled log-loss / AUC | 0.650913 / 0.666108 | 0.650913 / 0.666108 | Exact |
| `spike` minus static: delta [CI], days better | -0.001000 [-0.004351, +0.001986], 10/22 | -0.001000 [-0.004351, +0.001986], 10/22 | Exact |
| `spike` minus KS: delta [CI], days better | -0.027803 [-0.031607, -0.024529], 22/22 | -0.027803 [-0.031607, -0.024529], 22/22 | Exact |
| `spike_gate` minus static: delta [CI], days better | -0.009339 [-0.012862, -0.006240], 22/22 | -0.009339 [-0.012862, -0.006240], 22/22 | Exact |
| `spike_gate` minus KS: delta [CI], days better | -0.036143 [-0.040375, -0.032609], 22/22 | -0.036143 [-0.040375, -0.032609], 22/22 | Exact |
| Alarms/day: `static_snorm`, `regime_gated`, `static_gbdt`, `static_wf` | 0 each | 0 each | Exact |
| Alarms/day: `ks_refit` rolling KS | 48.000000 | 48.000000 | Exact |
| Alarms/day: `spike` harm / calibrated KS | 81.136364 / 0.727273 | 81.136364 / 0.727273 | Exact |
| Alarms/day: `spike_gate` harm / calibrated KS | 12.363636 / 0.727273 | 12.363636 / 0.727273 | Exact |
| `static_snorm`, 100 ms: gross / taker / spread / fee | +0.291809 / +0.259393 / 0.012569 / +0.129697 | +0.291809 / +0.259393 / 0.012569 / +0.129697 | Exact |
| `regime_gated`, 100 ms: gross / taker / spread / fee | +0.297406 / +0.263927 / 0.012569 / +0.131963 | +0.297406 / +0.263927 / 0.012569 / +0.131963 | Exact |

All 374/374 per-day records match after omitting wall-clock and latency fields; regime descriptors, policy specifications, and configuration also match exactly. The only different top-level metadata fields are creation timestamp, Git commit, command tag, and runtime. No requested numeric metric needed a tolerance or mismatched.

## Code issues

| ID | Severity | File:line | Evidence | Suggested fix |
|---|---|---|---|---|
| S1 | major | `eval/config.py:10`; `eval/config_v2.py:15`; `eval/results/baseline.md:29,45` | The earlier v1 holdout explicitly includes and reports 2025-08-01 before v2 pre-registration, but v2 includes it again among its 22 nominal holdout days. Thus `eval/PREREGISTRATION.md:95` ("the holdout had not been ... read") does not hold for the whole set; prior model choices had access to that day's outcomes. Exploratory exclusion of that day gives `spike` vs static -0.000874 [-0.004511, +0.002096] and `spike_gate` vs static -0.009274 [-0.013345, -0.006158] (21-day paired bootstrap), so conclusions appear robust but the untouched-22-day claim is incorrect. | Disclose the overlap; report the 21-day clean-set sensitivity explicitly and reserve a fully unseen set for any new confirmatory claim. |
| S2 | major | `components/evaluator/__init__.py:24-40`; `eval/run_v2.py:139` | `score()` computes `edge_bps` using the non-tie label mask, contrary to the registered rule that ties count as zero moves. Holdout `static_snorm` JSON reports 0.384558 bps over 1,432,164 non-ties while `trading_edge()` correctly gives 0.291809 gross bps over 1,887,363 signals (about 32% inflation). The separate fee-aware edge table is **not** affected. | Give `edge_bps` its own finite-move/signal mask, include zero-move ties, and align its abstention convention with `trading_edge()`; add a tie-heavy regression test. |
| S3 | minor | `components/adapter/__init__.py:258-259`; `components/contracts.py:65-71` | `run_episode()` uses `j = t - H` without reading `labels.avail_step`. This matches the current labeler (always `t+H`), so it does not leak in this run, but violates the declared `Labels` contract for delayed labels: a toy label declared available at step 7 changes the forecast at step 3. | Either enforce/assert `avail_step[j] <= t` before consuming a label, or restrict the contract to fixed `t+H` availability and test that invariant. |
| S4 | minor | `components/features/__init__.py:57`; `components/evaluator/__init__.py:119-123` | The grid includes the *next* midnight, and `out_ok` checks grid index only. The last accepted horizon can end at midnight; the 100 ms exit then lies beyond the day's last receive timestamp, yet `searchsorted(...)-1` returns a stale quote. For example, 2025-01-01's last receive was 0.2046 s before midnight, so this exit uses a quote about 0.3046 s old. This affects at most the final eligible signal per day. | Exclude next midnight from the same-day grid and/or mask delayed exit timestamps outside the UTC day or after the last available receive. |
| S5 | minor | `eval/check_numbers.py:18,47-48,71` | The checker passed 163 current quotes, but pools *all* results together and strips the sign of stored numbers. An incorrect `+0.0093` can pass using a result containing `-0.0093`; matching an unrelated policy also passes. Thus `OK` is a lexical check, not full provenance or sign validation. | Preserve signs for signed effects and check important claims against explicit result file/policy/field references rather than a global set of numerals. |

## Things verified OK

- `components/ingest` stable-sorts receive timestamps; feature as-of joins use `side="right"` and only trailing observations. The 10 s direction label excludes ties from forecast scores, and the current adapter predicts before consuming `y[t-10]`; the feature and delayed-label perturbation tests pass.
- Walk-forward contexts in `run_v2.py:86-90` use only days strictly earlier than the evaluated day. Harm-gated shrink computes its CUSUM from delayed **raw** forecasts (`adapter:271`), not its own shrunken output.
- Fast KS agrees with SciPy over 200 randomized cases including ties; empirical KS thresholds leave each training day out and use no dev/holdout observations. HarmCUSUM accumulates delayed loss minus `ln(2)`.
- Paired bootstrap resamples whole days and recomputes the pooled ratio of loss sums to valid-label counts. An unequal-size two-day toy yields pooled mean 0.5 rather than an incorrect equal-day mean 0. Long/short taker signs, optimistic passive-fill maker bounds, and per-side fee subtraction agree with the declared formulas.
- The top-decile cutoffs come from committed dev JSONs (`v2_dev*.json`), not holdout predictions; selected dev specs match the effective holdout specs. The pre-registration and Amendment 1 commits precede the reported v2 run, subject to S1. No verified event occurs in the v2 holdout, so alarm rates cannot establish holdout detection delay.
