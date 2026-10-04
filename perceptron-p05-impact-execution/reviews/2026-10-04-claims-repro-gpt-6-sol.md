# Claims pipeline and E10 reproduction review (2026-10-04)

Scope: P5 result code at `db4ed95` (doc gate rechecked after `e252cda`),
Python 3.11.14, committed CSVs; no project code changed. I paired policies
by **numeric seed**, bootstrapped the paired mean
with 10,000 resamples and `RandomState(0)`, and checked SELL signs against
`is_bps = 1e4 * (arrival_mid - average_fill_price) / arrival_mid`. Thus
negative (IA - TWAP) means IA sold for more and was cheaper.

| Quantity | Quoted | Independently recomputed | Result |
|---|---:|---:|---|
| E10/H2 paired IS, 400 seeds 1260-1659 | -0.013 bps [-0.029, +0.003] | -0.012651 bps [-0.028501, +0.002586] | Matches at quoted precision |
| E10/H2 one-sided 95% upper, registered 10k/seed order | H2 not confirmed | +0.000193 bps; bootstrap fraction >= 0 is 0.0524 | Not confirmed; bound is positive |
| E6 + E10 paired IS, 600 seeds | -0.020 bps [-0.032, -0.007] | -0.019780 bps [-0.032178, -0.007115] | Matches; seed sets disjoint |
| Pooled saving at a $1,000/share reference price | 0.20 cents/share | 0.1978 cents/share | Sign and rounding match |
| E10 QP main effect on own impact | -0.014 bps [-0.025, -0.002] | -0.013557 bps [-0.025203, -0.002227] | Matches from raw E10 CSV |
| E12 touch-only at-fill benefit vs TWAP | 0.041 bps [0.036, 0.046] | 0.040650 bps [0.035766, 0.045578] | Matches; saving is positive |
| E12 pre-trade equality | 180/180 | 180/180 `pre_window_exact` and `arrival_exact` | Matches recorded flags |
| E11 spread, volume, trades (synced/native) | +13%; within +/-10% for volume/trades | 1.134417, 0.979990, 0.985850; independent 95% spread CI [1.025, 1.261] | Matches raw E11 CSV |
| Simulator rerun, seeds 1260-1261 | E10 five arms x two seeds | 10/10 rows match **all 25 shared deterministic serialized fields**, including IS, own, instant, drift and filled | Exact at CSV precision |

The two-seed run used `nice -n 10`, one worker, and synced twins after
`kern.memorystatus_level` returned 44 (minimum 30). Its four *new* E12-era
fields are absent from the older E10 CSV; `wall_s` is nondeterministic.
Generated rerun outputs were removed. E10 uses seeds 1260-1659 and E6 uses
1060-1259, each with exactly one of every expected policy per seed; there
is no overlap or duplicate pair. Literal CSV equality is not proof of
equality beyond its six significant printed digits.

## Findings

1. **BLOCKER - The claimed documentation gate currently fails.**
   `eval/check_docs.py:43-60` exits 1 on clean main with
   `selection-memo.template.md: claims missing for placeholders:
   ['astra_final']`. The placeholder is at
   `deliverables/selection-memo.template.md:9`, but
   `eval/claims.py:214-222` can produce it only from a final Astra row in
   `reviews/ledger.tsv`; that ledger still has only the *draft* row,
   although `reviews/2026-10-04-abstract-final-gpt-6-astra.md:5` now
   records an actual final score of 3.25/5.
   `eval/render_docs.py:43-55` would write `claims.json`, the abstract and
   architecture **before** raising at the missing memo placeholder.
   **Impact:** the advertised enforcement cannot pass on this revision;
   rendering can leave a partially updated tree. **Minimal fix:** add
   the existing final review's real score to the ledger and rerender;
   preflight all templates/claims/sources before any writes.

2. **MAJOR - The abstract pairs different policies and seed sets to
   explain the touch-cap benefit.**
   `deliverables/round1-abstract.template.md:26` pairs the **E12
   TWAP_touch_limit** at-fill saving (-0.040650 bps cost) with
   `{{touch_drift}}` (+0.026 bps), sourced by
   `eval/claims.py:35,48-51` from **E6 IA_full**, a different policy on
   different seeds. On the *same E12 touch-only arm*, drift is
   +0.022795 bps, own impact +0.014893 bps, and fill delay +0.003801
   bps; together they offset the -0.040650 at-fill cost, leaving paired
   total IS **+0.000839 bps**, not a saving. Calling the loss solely
   "timing (+0.026)" therefore misattributes it. **Impact:** the E12
   fill-price benefit itself is real, but its claimed offset has the
   wrong provenance and misses the own-impact contribution. **Minimal
   fix:** render the offset from the matching E12 touch-only rows,
   separating drift, own impact, and fill delay; report the net IS.

3. **MAJOR - Cached attribution and market-statistics JSON can drift
   independently of the committed raw CSV without detection.**
   `eval/claims.py:170-187,227-238` takes E10 QP-attribution and E11
   ratios from generated JSON, not from their committed CSVs;
   `eval/check_docs.py:43-65` only checks `claims.json` and rendered text
   against these claims, not whether the JSON still reflects raw runs.
   In an in-memory check (no files edited), increasing every E10
   `QP_only.own_impact_bps` by **+1.000** should increase the QP main
   effect by **+0.500** bps. **Every key** in `claims.compute()` instead
   remained unchanged, including `e10_A_own = -0.014`. **Impact:** a
   stale derived JSON can certify materially wrong attribution while
   the doc gate (once issue 1 is fixed) reports no drift. **Minimal fix:**
   recompute these claims from CSV, or regenerate/compare the derived
   JSON deterministically from CSV as part of the gate.

4. **MAJOR - Three distinct H2 bootstrap procedures are in use near
   the decision boundary.** `eval/preregistration.md:86` fixes **10k**
   draws, `RandomState(0)`, paired seeds sorted. The independent
   registered computation gives upper95 **+0.000193** bps. However
   `eval/claims.py:163-169` sorts the *effect values*, not the seeds,
   before drawing 10k (upper95 **+0.000349**); the committed verdict is
   generated with **20k** draws by `eval/h1_verdict.py:1-7,17-19`
   (published upper95 **+0.0004**). **Impact:** H2 is *not confirmed*
   under all three, but the reported confirmatory threshold and interval
   do not reproduce the registered procedure; the decision is close
   enough to zero that ordering and Monte Carlo precision matter.
   **Minimal fix:** make both claims and verdict use the preregistered
   10k/seed-order rule, and label any additional 20k sensitivity
   estimate separately without silently replacing the frozen rule.

5. **MINOR - Bare integer results bypass the number-tracing gate.**
   `eval/check_docs.py:18,30-40` matches decimals, percentages and
   multipliers, but not plain integers. For example,
   `untraced("exact in 180/180 runs; 400 test seeds")` returns `[]`.
   The actual abstract template hard-codes E8's "**100** validation
   seeds" at `deliverables/round1-abstract.template.md:33`, despite
   `claims.py` computing `e8_n`. **Impact:** that sample size could
   become stale while an updated template/render and `claims.json` pass
   the gate. **Minimal fix:** use `{{e8_n}}` and explicitly classify
   remaining fixed integer literals; check all empirical counts, not
   only decimal-like forms.

6. **MINOR - "Books match event-by-event" overstates the verified
   scope.** `components/tca/tca/metrics.py:77-84` compares event times
   and only the best bid/ask price and quantity, with
   `world.py:97-101` logging depth 1. The 180/180 E12 equality is
   valid for this **top-of-book event log**, not for all levels or
   queues of the exchange book. **Impact:** no demonstrated error in
   the paired H2 IS, but the abstract's full-book wording is stronger
   than the evidence. **Minimal fix:** say "top-of-book event logs"
   unless a full-depth/order-queue check is added.

The negative E10 H2 contrast and the pooled gain are numerical facts of
the committed runs; neither the positive H2 upper bound nor the
non-reproduction on E8 validation seeds supports a replicated claim
that this execution policy beats TWAP.
