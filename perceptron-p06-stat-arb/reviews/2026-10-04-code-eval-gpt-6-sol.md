# P6 code and evaluation review (GPT-6 Sol, 2026-10-04)

Scope: the code frozen in `eval/PREREGISTRATION-walkforward-12d.md` (commit
`604f54d`) and the subsequent timing, reporting, and deliverable code on
`origin/main`. All P&L discussed here is simulated, not a return from trading.
Issue evidence records the original behavior; **Status** notes identify
corrections published through `9ad4ac9`.
The requested synthetic tests passed: `components/test_contracts.py` and
`components/decision/test_compiled.py` (5 tests); including the subsequently
added `components/sim/test_strict.py`, 7 tests pass. All 11 code blobs named in
the pre-registration matched the primary result commit `340d4df`; a later
docstring-only edit to `components/decision/lev.py` changes that one blob
at current `HEAD`, without changing executable logic. The current LEV input
list (`rules.LEARN_X`) uses features available at episode open plus the
specified fee and latency; it does **not** include test-day duration, closure,
outcome, or P&L. The findings below concern the replay and the claims made
from it, not an observed direct test-label leak into this LEV model.

## Issues

1. **P6-C01 - blocker - `components/sim/fills.py:42-60`; `eval/falsification.py:97-109`.**
   **Evidence:** every intent independently receives up to the full
   top-of-book quantity; the simulator never decrements available size for
   other orders at the same venue and time. With one 0.05-BTC quote on each
   side, two intents arriving simultaneously each receive 0.05 BTC and
   +$0.005: aggregate simulated fill is 0.10 BTC against 0.05 BTC displayed.
   Summing these intents' P&L can overstate executable portfolio returns;
   pre-positioned inventory does not create exchange liquidity. **Fix:** replay
   selected orders chronologically with a shared per-venue book-size and
   inventory ledger, or explicitly present the sum as independent-signal
   counterfactuals, not attainable daily trading P&L.

2. **P6-C02 - major - `components/sim/fills.py:50-52`.**
   **Evidence:** `q <= 0` is silently replaced by the 0.05-BTC cap. A
   synthetic intent with `size=0` at observation fills 0.05 BTC at arrival
   and earns +$0.005. The feed normalizer maps missing amounts to zero, so
   this fallback cannot distinguish "unknown" from no quoted liquidity.
   **Fix:** skip or explicitly flag zero/unknown observed size, and never
   infer a tradable cap from zero displayed quantity; keep distinct states
   if unknown size is to be modeled separately.

3. **P6-C03 - major - `components/sim/fills.py:26-30,54-72`.**
   **Evidence:** `LegBook.at` treats every lookup after a venue's final
   timestamp as valid and returns the last quote indefinitely. In a synthetic
   one-tick book, an order arriving 10 seconds after the last tick still
   produces a "both" fill and +$0.005. Long feed gaps have the same problem.
   The detector censors stale counter-legs, but the fill book does not.
   **Fix:** reject or censor arrivals and unwinds without a contemporaneous
   truth book (including the end of the observed period), with a documented
   maximum age; do not substitute an indefinitely stale price for a fill.

4. **P6-C04 - major - `components/sim/fills.py:56-59,73`;
   `components/decision/autoresearch/rules.py:54-57`.**
   **Evidence:** `outcome` uses the price-limit booleans rather than
   positive filled quantity. With sell displayed size zero, buy size 0.05,
   and both prices passing their limits, the simulator records `outcome=both`
   and -$0.005 from unwinding the *only* filled buy leg. The EV trainer then
   omits that loss from its `outcome != "both"` legging-loss estimate.
   **Fix:** derive outcomes from `qs` and `qb`, distinguish partial mismatches,
   and estimate legging loss from actual unmatched quantities/P&L.

5. **P6-C05 - major - `components/detector/cross.py:73-98,103-122`;
   `eval/falsification.py:60-64`.**
   **Evidence:** `_detect` stores fields when a cross opens but only emits
   a row once it closes or the input ends; the replay then backdates its
   decision to `t_start_us + feed_delay + compute`. The open-time feature
   values are causal, so this does not by itself leak test labels into LEV,
   but the implemented detector cannot feed a live decision at the measured
   reaction time. **Fix:** expose and test a streaming `open` signal with
   persistent detector state, run the same decision path in event-time replay,
   and keep closure/censoring as a separate training-label stream. Until then,
   describe the live path as planned rather than already executable.

6. **P6-C06 - major - `eval/falsification.py:55-64,72-79,197-206`.**
   **Evidence:** the clock-skew variants rewrite `ts_exch_us` before
   `cells()` builds *both* the detector stream and `truth_books(q)` from it.
   Moving ground-truth event times along with the perceived timestamps tests
   a rephased market, not an erroneous observer clock against unchanged
   physical fills. Thus the reported skew robustness is not, alone, a
   causal-clock-error test (the separate receive-time replay remains useful).
   **Fix:** preserve a separate immutable truth/arrival timeline and perturb
   only the timestamps available to detection; score orders against the
   unperturbed truth, or narrow the claim to rephased-event sensitivity.

7. **P6-C07 - major - `eval/latency_budget.py:23-33`.**
   **Evidence:** `breakeven()` returns the *first* positive-to-negative
   crossing, although the report calls it the *largest* profitable latency.
   In committed `baseline_0901_to_1001.json`, f5/`threshold_pair` P&L is
   +$1.99 at 10 ms, -$22.99 at 20 ms, +$8.81 at 50 ms, and -$29.94 at
   100 ms. The function reports **10.6 ms**, overlooking the profitable
   50-ms point. **Fix:** report all disjoint profitable intervals, or return
   the last positive-to-negative crossing with an explicit nonmonotonicity
   warning; never assume a monotone frontier without checking it. **Status:**
   `fdc067f` changes the code and prose to report the *first* crossing
   with `*` for a later positive point; `594806c` regenerates the
   budget JSON/MD with `10.6*` and explicitly labels the **first**
   crossing. The misleading "largest profitable" claim is resolved.

8. **P6-C08 - major - `eval/falsification.py:97-109,164-180`;
   `eval/PREREGISTRATION-walkforward-12d.md` (Day score).**
   **Evidence:** a "daily" total adds P&L over six mutually exclusive
   fee/latency environments on the same candidate episodes. This is the
   pre-registered score, and a constant rescaling would not change its
   paired significance test; it is *not* one portfolio's USD/day. **Fix:**
   preserve the frozen primary score for the hypothesis test, but label the
   unit "sum over six simulated cell-days" in all tables/abstract text and
   show per-cell USD/day separately. **Status:** the abstract published
   in `9ad4ac9` now explicitly states the six-scenario summed metric;
   the registered score itself is unchanged.

9. **P6-C09 - major - `eval/check_docs.py:45-61`;
   `deliverables/render.py:16-32`.**
   **Evidence:** `check_docs` renders from the already-saved
   `eval/results/headline.json` and compares the rendered files to their
   templates. It never recomputes headline values from the underlying
   baseline, walk-forward, timing, or decay JSON. Changed source results
   with an unchanged headline and unchanged deliverables can therefore
   return `check_docs: OK`, contrary to its stated drift guarantee.
   **Fix:** factor `eval.headline` into a pure value-building function and
   compare its fresh result to committed `headline.json` before checking
   rendered documents. **Status:** this direct fix landed in `fdc067f`;
   with the corrected sensitivity, headline, and rendered deliverables
   published in `9ad4ac9`, `eval.headline` reproduces the committed
   `headline.json`, and `check_docs.py` passes.

10. **P6-C10 - major - `components/decision/lev.py:5-8,18,39-45`;
    `components/decision/autoresearch/rules.py:78-84`.**
    **Evidence:** the LEV docstring says residual KM survival at latency L
    is a model input, and ADR 001 calls survival an interpretable LEV
    feature. Neither the baseline's `LEV_FEATURES` nor the walk-forward's
    frozen `LEARN_X` contains survival; neither trainer computes it. The
    `lev_edge_only` ablation removes age/spread/volatility, **not survival**,
    so it cannot establish the ADR's proposed survival-information test.
    **Fix:** correct the interpretation of the frozen run and label the
    ablation as non-edge covariates; add a separately pre-registered future
    experiment with a training-only, causally available residual-survival
    feature before claiming survival contributes to LEV. **Status:**
    `fdc067f` corrected the `lev.py` docstring; the ADR's final status
    (`9ad4ac9`) and abstract now acknowledge the absence of this input.
    The frozen models still have no survival-specific ablation; the
    original ADR synthesis remains a historical proposal, not a measured
    LEV feature.

11. **P6-C11 - minor - `eval/decay_report.py:107-115`.**
    **Evidence:** requested monthly days without cached episodes are silently
    omitted. An older cache lacking `t_start_us` is instead assigned hour
    zero, which makes the purported hour-block bootstrap a one-block
    resample with no useful uncertainty. **Fix:** fail explicitly on a
    missing/old requested day (or recompute it), and report the exact count
    and identities of processed days before quoting a multi-month interval.

12. **P6-C12 - minor - `eval/decision_timing.py:34-49`;
    `eval/latency_budget.py:41-48,65`.**
    **Evidence:** detector time is a best-of-three *day-long average*
    per event; budget `total_p99` adds this average to the decision p99,
    then labels the sum "our compute, total p99". An average detector cost
    is not its p99 and cannot establish a p99 end-to-end bound. The
    committed timing result measures 6.08 us decision p50 but 41.46 us
    p99 on the shared M5, so the stated <=10 us target is not met at p99.
    **Fix:** measure event-level detector tails in the streaming path and
    time the combined detector-plus-decision pipeline at p99; otherwise
    label the figure as average detector + p99 decision.

13. **P6-C13 - minor - `eval/run_baseline.py:169-173,231-233`.**
    **Evidence:** the row named `oracle` is simply *naive at zero
    latency*, not a hindsight-optimal or size-aware upper bound, yet
    `capture_ratio` divides by its P&L. In the committed baseline 24
    policy/cell rows have `capture_ratio > 1` (maximum 1.212), which is
    impossible for a genuine oracle upper bound. The journal notes this
    caveat, but the result field does not. **Fix:** rename it
    `zero_latency_naive` and the ratio accordingly, or build a true
    constrained upper-bound benchmark.

14. **P6-C14 - minor - `eval/falsification.py:136-145,241-244`.**
    **Evidence:** "relative uplift" divides the improvement by the signed
    baseline total. In the committed 12-day comparison,
    `threshold_pair - naive` gains +$2,898.5 per sampled day, yet the table
    presents a **-183.9%** relative uplift because naive P&L is negative.
    **Fix:** suppress percentage uplift against nonpositive baselines, or
    use a separately named absolute-denominator effect size; retain the
    registered dollar statistic and its uncertainty unchanged.

15. **P6-C15 - blocker - `components/sim/fills.py:61-65`;
    `eval/run_baseline.py:116-122`.**
    **Evidence:** for a matched pair, `pnl_usd` immediately credits
    `(bid_sell - ask_buy) - basis0_px` where `basis0_px` is the *estimated
    fair basis at signal time*. It does not close the long and short, use a
    subsequent markout, or pay exit fees. This is a basis-adjusted
    execution-surplus **estimate**, not realized trading P&L; if the spread
    fails to converge, the sign of eventual returns can differ. Reporting
    the walk-forward totals as earned USD/day makes the central headline
    stronger than the measured quantity. **Fix:** preserve the registered
    surrogate as such, rename it in every claim, and run the separately
    registered strict-fill/1 s and 10 s markout sensitivity before making
    a claim about executable trading returns. **Status:** the final
    abstract explicitly calls this a simulated, basis-adjusted surplus;
    the strict-fill and markout sensitivities have been published, but
    they are still simulated, not evidence of realized trades.

16. **P6-C16 - major (Amendment 1 sensitivity, not frozen primary) -
    `components/sim/strict.py:28-30,60-61`.**
    **Evidence:** S2 requires the first quote at or after arrival + H
    for matched-leg markouts, and S1 requires the first quote at or
    after unwind time. `mid_next` clips a past-the-end search index to
    the **last earlier quote**; the unwind calls discard `at_next`'s
    `ok=False` indicator and also price against the last quote. On a
    synthetic two-quote book with timestamps `[10, 20]`, time-30
    `mid_next` returned the time-20 mid despite `at_next` reporting
    no after-time quote. End-of-data missing marks/exits can thus be
    scored using stale prices. **Fix:** explicitly flag missing future
    quotes and specify/report their treatment and frequency, preserving
    paired day comparability when computing S1/S2 confidence bounds;
    never silently replace a required future quote with an old one.
    **Status:** the erratum was registered in `594806c` and code fix
    `9c4fe6a` now flags invalid rows and excludes them in V1-V4; its two
    synthetic tests pass. The corrected run in `9ad4ac9` reports **zero
    excluded rows across all 13 dates**, and its registered LEV-vs-threshold
    figures agree with the pre-erratum Azure run within floating-point
    tolerance. The code issue was real; it did not alter this sample.

## Reproduction of the pre-registered 12-day comparisons

After the lead's explicit `chain done` signal, I synced to `origin/main`,
copied all 13 day caches into this worktree, linked its raw-data directory
read-only, and ran the exact registered walk-forward through
`eval/run_guarded.sh` with `--out repro_walkforward_12d`. The borrowed
environment has scikit-learn 1.9.1, NumPy 2.4.6, polars 1.44.2, and
Numba 0.68.0. The tables compare **every numeric or boolean field** in
all five `comparisons` and both `unseen7` comparisons: floats match if
`abs(a-b) <= max(1e-9, 1e-12 * max(abs(a), abs(b)))`; counts and flags match
exactly. Runtime (`1,320` vs `260` s), output name, and HEAD commit are
expected to differ and are not evaluation statistics.

| Quantity | Committed value | Independent value | Match? |
|---|---:|---:|:---:|
| `comparisons/ev_kmpair - threshold_pair/ci95/0` | -141.4782491393705 | -141.47824913937043 | yes |
| `comparisons/ev_kmpair - threshold_pair/ci95/1` | -22.320689482458608 | -22.320689482458466 | yes |
| `comparisons/ev_kmpair - threshold_pair/days_positive` | 2 | 2 | yes |
| `comparisons/ev_kmpair - threshold_pair/falsified (lower bound <= 0)` | True | True | yes |
| `comparisons/ev_kmpair - threshold_pair/mean_usd_per_day` | -76.75560296783648 | -76.75560296783654 | yes |
| `comparisons/ev_kmpair - threshold_pair/median_usd_per_day` | -26.959682979818794 | -26.959682979818567 | yes |
| `comparisons/ev_kmpair - threshold_pair/n_days` | 12 | 12 | yes |
| `comparisons/ev_kmpair - threshold_pair/relative_uplift_mean` | -0.048309266357644216 | -0.04830926635764424 | yes |
| `comparisons/ev_kmpair - threshold_pair/relative_uplift_of_totals` | -0.05804034244040356 | -0.0580403424404036 | yes |
| `comparisons/ev_kmpair - threshold_pair/sign_p` | 0.996826171875 | 0.996826171875 | yes |
| `comparisons/ev_kmpair - threshold_pair/t_ci95/0` | -147.726824668287 | -147.72682466828712 | yes |
| `comparisons/ev_kmpair - threshold_pair/t_ci95/1` | -5.784381267385953 | -5.784381267385967 | yes |
| `comparisons/ev_kmpair - threshold_pair/wilcoxon_p` | 0.99755859375 | 0.99755859375 | yes |
| `comparisons/gbm_clf - threshold_pair/ci95/0` | 88.97947110804756 | 88.97947110804779 | yes |
| `comparisons/gbm_clf - threshold_pair/ci95/1` | 335.18333198430844 | 335.1833319843086 | yes |
| `comparisons/gbm_clf - threshold_pair/days_positive` | 12 | 12 | yes |
| `comparisons/gbm_clf - threshold_pair/falsified (lower bound <= 0)` | False | False | yes |
| `comparisons/gbm_clf - threshold_pair/mean_usd_per_day` | 201.01189617303723 | 201.01189617303726 | yes |
| `comparisons/gbm_clf - threshold_pair/median_usd_per_day` | 102.77754860282204 | 102.77754860282215 | yes |
| `comparisons/gbm_clf - threshold_pair/n_days` | 12 | 12 | yes |
| `comparisons/gbm_clf - threshold_pair/relative_uplift_mean` | 0.13789725458151572 | 0.13789725458151578 | yes |
| `comparisons/gbm_clf - threshold_pair/relative_uplift_of_totals` | 0.15199931780050974 | 0.15199931780050974 | yes |
| `comparisons/gbm_clf - threshold_pair/sign_p` | 0.000244140625 | 0.000244140625 | yes |
| `comparisons/gbm_clf - threshold_pair/t_ci95/0` | 54.58768876958666 | 54.587688769586805 | yes |
| `comparisons/gbm_clf - threshold_pair/t_ci95/1` | 347.43610357648777 | 347.4361035764877 | yes |
| `comparisons/gbm_clf - threshold_pair/wilcoxon_p` | 0.000244140625 | 0.000244140625 | yes |
| `comparisons/lev - lev_edge_only/ci95/0` | 153.98965073695425 | 153.98965073695453 | yes |
| `comparisons/lev - lev_edge_only/ci95/1` | 425.87680628515335 | 425.8768062851536 | yes |
| `comparisons/lev - lev_edge_only/days_positive` | 12 | 12 | yes |
| `comparisons/lev - lev_edge_only/falsified (lower bound <= 0)` | False | False | yes |
| `comparisons/lev - lev_edge_only/mean_usd_per_day` | 280.72003644269364 | 280.72003644269375 | yes |
| `comparisons/lev - lev_edge_only/median_usd_per_day` | 191.79267128240974 | 191.79267128240974 | yes |
| `comparisons/lev - lev_edge_only/n_days` | 12 | 12 | yes |
| `comparisons/lev - lev_edge_only/relative_uplift_mean` | 0.20571374515417262 | 0.20571374515417276 | yes |
| `comparisons/lev - lev_edge_only/relative_uplift_of_totals` | 0.20938887601197154 | 0.20938887601197168 | yes |
| `comparisons/lev - lev_edge_only/sign_p` | 0.000244140625 | 0.000244140625 | yes |
| `comparisons/lev - lev_edge_only/t_ci95/0` | 119.32417025386354 | 119.32417025386377 | yes |
| `comparisons/lev - lev_edge_only/t_ci95/1` | 442.11590263152374 | 442.11590263152374 | yes |
| `comparisons/lev - lev_edge_only/wilcoxon_p` | 0.000244140625 | 0.000244140625 | yes |
| `comparisons/lev - threshold_pair/ci95/0` | 165.03327791132563 | 165.03327791132577 | yes |
| `comparisons/lev - threshold_pair/ci95/1` | 450.8690456886483 | 450.8690456886473 | yes |
| `comparisons/lev - threshold_pair/days_positive` | 12 | 12 | yes |
| `comparisons/lev - threshold_pair/falsified (lower bound <= 0)` | False | False | yes |
| `comparisons/lev - threshold_pair/mean_usd_per_day` | 298.93097812944114 | 298.930978129441 | yes |
| `comparisons/lev - threshold_pair/median_usd_per_day` | 181.237769670096 | 181.23776967009564 | yes |
| `comparisons/lev - threshold_pair/n_days` | 12 | 12 | yes |
| `comparisons/lev - threshold_pair/relative_uplift_mean` | 0.22295524112706758 | 0.22295524112706758 | yes |
| `comparisons/lev - threshold_pair/relative_uplift_of_totals` | 0.2260428641795425 | 0.22604286417954234 | yes |
| `comparisons/lev - threshold_pair/sign_p` | 0.000244140625 | 0.000244140625 | yes |
| `comparisons/lev - threshold_pair/t_ci95/0` | 129.59485559315712 | 129.59485559315732 | yes |
| `comparisons/lev - threshold_pair/t_ci95/1` | 468.26710066572514 | 468.2671006657246 | yes |
| `comparisons/lev - threshold_pair/wilcoxon_p` | 0.000244140625 | 0.000244140625 | yes |
| `comparisons/threshold_pair - naive/ci95/0` | 1814.862361500605 | 1814.8623615006052 | yes |
| `comparisons/threshold_pair - naive/ci95/1` | 3974.1783554945787 | 3974.17835549458 | yes |
| `comparisons/threshold_pair - naive/days_positive` | 12 | 12 | yes |
| `comparisons/threshold_pair - naive/falsified (lower bound <= 0)` | False | False | yes |
| `comparisons/threshold_pair - naive/mean_usd_per_day` | 2898.460940438052 | 2898.460940438052 | yes |
| `comparisons/threshold_pair - naive/median_usd_per_day` | 3262.9459600371856 | 3262.945960037183 | yes |
| `comparisons/threshold_pair - naive/n_days` | 12 | 12 | yes |
| `comparisons/threshold_pair - naive/relative_uplift_mean` | -2.0884023171291046 | -2.088402317129105 | yes |
| `comparisons/threshold_pair - naive/relative_uplift_of_totals` | -1.8391152535018396 | -1.8391152535018396 | yes |
| `comparisons/threshold_pair - naive/sign_p` | 0.000244140625 | 0.000244140625 | yes |
| `comparisons/threshold_pair - naive/t_ci95/0` | 1628.406478726738 | 1628.4064787267375 | yes |
| `comparisons/threshold_pair - naive/t_ci95/1` | 4168.515402149366 | 4168.515402149367 | yes |
| `comparisons/threshold_pair - naive/wilcoxon_p` | 0.000244140625 | 0.000244140625 | yes |
| `subsets/unseen7/lev - lev_edge_only/ci95/0` | 150.99550762499834 | 150.99550762499854 | yes |
| `subsets/unseen7/lev - lev_edge_only/ci95/1` | 542.6330392501299 | 542.6330392501301 | yes |
| `subsets/unseen7/lev - lev_edge_only/days_positive` | 7 | 7 | yes |
| `subsets/unseen7/lev - lev_edge_only/falsified (lower bound <= 0)` | False | False | yes |
| `subsets/unseen7/lev - lev_edge_only/mean_usd_per_day` | 332.10396405543077 | 332.103964055431 | yes |
| `subsets/unseen7/lev - lev_edge_only/median_usd_per_day` | 305.71365845350783 | 305.71365845350897 | yes |
| `subsets/unseen7/lev - lev_edge_only/n_days` | 7 | 7 | yes |
| `subsets/unseen7/lev - lev_edge_only/relative_uplift_mean` | 0.2433449671896084 | 0.24334496718960866 | yes |
| `subsets/unseen7/lev - lev_edge_only/relative_uplift_of_totals` | 0.22774515354326055 | 0.22774515354326078 | yes |
| `subsets/unseen7/lev - lev_edge_only/sign_p` | 0.0078125 | 0.0078125 | yes |
| `subsets/unseen7/lev - lev_edge_only/t_ci95/0` | 64.82153681285831 | 64.82153681285894 | yes |
| `subsets/unseen7/lev - lev_edge_only/t_ci95/1` | 599.3863912980032 | 599.386391298003 | yes |
| `subsets/unseen7/lev - lev_edge_only/wilcoxon_p` | 0.0078125 | 0.0078125 | yes |
| `subsets/unseen7/lev - threshold_pair/ci95/0` | 155.62747605006894 | 155.6274760500692 | yes |
| `subsets/unseen7/lev - threshold_pair/ci95/1` | 553.5442614569644 | 553.5442614569631 | yes |
| `subsets/unseen7/lev - threshold_pair/days_positive` | 7 | 7 | yes |
| `subsets/unseen7/lev - threshold_pair/falsified (lower bound <= 0)` | False | False | yes |
| `subsets/unseen7/lev - threshold_pair/mean_usd_per_day` | 342.8210385460846 | 342.8210385460846 | yes |
| `subsets/unseen7/lev - threshold_pair/median_usd_per_day` | 333.56295480059475 | 333.56295480059566 | yes |
| `subsets/unseen7/lev - threshold_pair/n_days` | 7 | 7 | yes |
| `subsets/unseen7/lev - threshold_pair/relative_uplift_mean` | 0.25253575321960364 | 0.25253575321960386 | yes |
| `subsets/unseen7/lev - threshold_pair/relative_uplift_of_totals` | 0.23683513816995252 | 0.23683513816995252 | yes |
| `subsets/unseen7/lev - threshold_pair/sign_p` | 0.0078125 | 0.0078125 | yes |
| `subsets/unseen7/lev - threshold_pair/t_ci95/0` | 69.71376256045426 | 69.71376256045511 | yes |
| `subsets/unseen7/lev - threshold_pair/t_ci95/1` | 615.9283145317149 | 615.928314531714 | yes |
| `subsets/unseen7/lev - threshold_pair/wilcoxon_p` | 0.0078125 | 0.0078125 | yes |
| February labelled-cell rows (lead cache vs raw rebuild) | 38,898 | 38,898 | yes |
| February episode rows (lead cache vs raw rebuild) | 257,263 | 257,263 | yes |
| February total `pnl_usd` (lead cache vs raw rebuild) | -2285.732234190544 | -2285.7322341905437 | yes |
| `headline.json` fields | 96 | 96 regenerated from the committed result files | yes, identical |
| Rendered abstract, UTF-8 bytes | 5,904 | 5,904; byte-for-byte equal to template + regenerated headline | yes |
| `eval/check_docs.py` | OK | OK (879-word abstract body) | yes |

Beyond the 91 comparison/subset fields tabulated above, the day list (13
scalars), `per_day` (792), day-score table (84), and per-cell uplift (24)
all match. The two February Parquet files regenerated from raw quotes
are **byte-for-byte identical** to the lead's cached cells and episodes
(SHA-256 agrees for each file), not merely equal in aggregate. The lead
cache is gitignored and is not itself a committed result.

The **corrected** Amendment 1 result reports V1 strict-fill LEV-minus-
threshold +$72.64 per six-cell sampled day (t-CI +$10.44 to +$134.84,
bootstrap CI +$25.61 to +$130.56) and V2 1 s markout +$70.12 (t-CI
**+$0.18** to +$140.07, bootstrap CI +$18.25 to +$136.35). Both lower
bounds are positive in both worlds, so its **registered robustness rule
passes**, although V2's t lower bound is close to zero. No candidate
rows were excluded for unavailable after-time marks/unwinds on the 13
sampled dates. The 65 registered LEV-minus-threshold scalar fields in
the corrected and pre-erratum result files match within `1e-12`
relative/`1e-9` absolute tolerance (maximum absolute difference
`6.82e-13`); they are **not byte-for-byte identical** across platforms.
These secondary results were checked against the two committed files,
**not independently replayed from quotes**.

## Verdict

The pre-registered **statistical decision rule passes in the frozen
counterfactual**: LEV exceeds the tuned threshold on 12/12 sampled
months, mean +$298.93 per six-cell day, paired t-CI
[+$129.59, +$468.27] and bootstrap CI [+$165.03, +$450.87];
the seven previously unexamined months are also 7/7 positive.
The independent replay and raw-data cache rebuild reproduce these
numbers. The unit tests pass and current LEV features do not directly
use test-day outcomes. Neither these numerical matches nor the
pre-registered p-values establish executable trading returns: the
frozen fill model and basis-adjusted mark have the blockers above,
and Amendment 1's strict-fill/markout sensitivity must be reported
separately. The corrected strict-fill and 1 s markout analyses both
pass their registered rule, but the mean advantage shrinks to about a
quarter of the frozen score, and dropping repeated quote hits gives a
t-CI that crosses zero. This is evidence of sensitivity to execution
assumptions, not proof of realized trading returns. The regenerated
headline, documentation checker, and rendered abstract agree exactly.
