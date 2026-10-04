# DustLedger: independent code and evaluation review (GPT-6 Sol)

2026-10-04 16:02 IST

Reviewed source at `41e391e`. I ran the tracked Python sources in a temporary mirror of `innovatex-t2-aqi/`, linked to the lead's `.data` read-only; no tracked inputs, results, or deliverables were edited. All runs below were sequential, after `sysctl -n kern.memorystatus_level` was at least 30. Commands are relative to the mirror's `innovatex-t2-aqi/` root.

| Exact command | Claimed | Reproduced | Result |
|---|---|---|---|
| `cd eval && OMP_NUM_THREADS=1 nice -n 10 python forecast_walkforward.py` | PM2.5 persistence 23.8 (n=1,034); CAMS 53.6; best GBM gain <=4% | 23.801 (n=1,034); 53.561; **4.398%** (display rounds to 4%) | **FAIL** literal gain bound; other values pass. Generated JSON byte-identical. |
| `cd components/attribution/autoresearch && OMP_NUM_THREADS=1 nice -n 10 python eval_v2.py all --holdout` | Pair 95.84; ring 69.12; ring_refcal 69.43; ring_selfcal 57.43 | 95.84; 69.12; 69.43; 57.43 | **PASS** (`results.tsv` v2.1 rows 9-12). |
| `OMP_NUM_THREADS=1 nice -n 10 python eval/calm_wind.py` | Nov-Jan ERA5 wind <1 m/s: 16.17% | 16.17%; <0.5 m/s: 4.02% | **PASS**; JSON byte-identical. |
| `OMP_NUM_THREADS=1 nice -n 10 python deliverables/bom/bom_total.py` | Kit ₹60,711; one node ₹10,032 | ₹60,711; ₹10,032 | **PASS**; independent CSV sum and JSON agree. |
| `OMP_NUM_THREADS=1 nice -n 10 python deliverables/bom/power_budget.py` | 10.2 Wh/day; December margin 2.09x; autonomy 12.1 days | 10.2; 2.09x; 12.1; independently calculated unrounded 10.1664 Wh/day, 21.203 Wh/day solar, 12.087 days | **PASS** arithmetic, conditional on stated duty-cycle/solar assumptions. |
| `OMP_NUM_THREADS=1 nice -n 10 python eval/render_docs.py`<br>`OMP_NUM_THREADS=1 nice -n 10 python eval/check_docs.py` | Five rendered docs; zero problems | Five; zero; all rendered files byte-identical to tracked versions | **PASS** drift check, not claim truth. |
| `OMP_NUM_THREADS=1 nice -n 10 python components/ingest/fetch_openaq_archive.py --ids 6929 --start 2025-11-01 --end 2025-11-07 --out /tmp/t2review.xl835E/ingest-check --workers 2` | Same hours as lead's parquet | Seven files fetched; 153 hourly rows overlap, zero missing/extra hours or differing cells | **PASS** one-week ingest spot check. |

**Positive controls:** `eval/forecast_eval.py:68-85` aligns calendar-day targets and lags correctly; all 11 folds in `eval/forecast_walkforward.py:43-47` had training targets strictly before the test month. All four `components/attribution/methods.py` outputs were unchanged when future observations were truncated at two separate cutoffs. Actual OpenAQ PM units are µg/m³; Open-Meteo's IST timestamps and km/h wind are handled consistently by this data/eval path.

1. **Blocking — the advertised forecasting gain is not a deployable gain.** `eval/forecast_eval.py:80-84`, `eval/forecast_walkforward.py:39-53`, `eval/render_docs.py:48`, `deliverables/zonal-deck.md:141-145`: the only PM2.5 GBM beating persistence uses **D+1 ERA5 reanalysis**, unavailable when issuing the D+1 forecast. Its 4.398% gain is rounded to "at most 4%"; both no-D+1-met GBMs instead lose 1.283% and 2.212%. CAMS is one central-grid, uncontrolled-vintage reference, not an equal-lead-time station forecast. **Fix:** distinguish oracle/reference curves, quote the negative retrospective no-D+1-met skill and approximate 4.4% oracle value; evaluate archived forecast vintages at matched lead times.

2. **Major — even the "no future met" variant lacks an as-of data guarantee.** `eval/forecast_eval.py:50-56,80-83`, `components/ingest/fetch_openmeteo.py:44-50`: `met0_*` comes from retrospective ERA5 for all of day D; the code establishes timestamp order, not whether reanalysis for D was published at the forecast issue time. The presenter also says "two years" and "one year of history" (`deliverables/zonal-deck.md:145`), though these monitors start 2025-02-19 and the first November fold trains only February-October. **Fix:** enforce release-time/vintage cutoffs or use issued weather forecasts; state actual training coverage.

3. **Major — the holdout is fresh-seeded, not demonstrably blind.** `components/attribution/autoresearch/eval_v2.py:39-46,153-167`, `components/attribution/autoresearch/results.tsv:2-12`, `components/attribution/autoresearch/program.md:4-10`: TEST was inspected during v0/v1 keep/revert; v2 seeds and the allegedly hidden rectangle are in the evaluator visible beside the method. This does not negate the reproduced v2.1 result, but it does not establish independent site generalization. **Fix:** freeze methods first; have a separate reviewer seal new seeds, site geometries and preferably real-site data until the final evaluation.

4. **Major — the 57.43 all-hour error masks the hours that matter.** `components/attribution/autoresearch/eval_v2.py:81-83,99-100,134-142`: only 36.1% of TEST hours are regular work hours; on those hours, self-cal MAE averages **115.77** across the same scenarios/seeds. Abstentions become zero predictions, including when actual site contribution is high. The target is maximum node exposure, but the evaluated ring measures wind-aligned contrast: even the true contrast has **14.30 MAE** against maximum exposure in hard-rect. **Fix:** publish work-hour/high-emission/calm MAE, coverage and CSI separately; report exposure and identifiable contrast as different targets.

5. **Major — the "fair" reference baseline is unnecessarily weak.** `components/attribution/autoresearch/eval_v2.py:111,127`, `components/attribution/methods.py:44-65`: refcal uses one noisy, dust-conditioned Wednesday 11:00 visit until the next week, versus self-cal's robust 14-day median of many idle samples. A causal 14-day median of the *same past reference visits* improves refcal from 69.43 to **64.92**; self-cal still wins at 57.43, but by about 11.5%, not 17%. This is exploratory, not a new registered baseline. **Fix:** pre-register equally robust reference schedules, visits and costs, then re-score on a sealed holdout.

6. **Major — the promised 1 m/s/confused-wind abstention is not implemented.** `components/attribution/methods.py:29-35`, `deliverables/zonal-deck.md:149-155`, `deliverables/zonal-pitch.md:11`: `_ring` abstains only below **0.5 m/s** (ERA5 Nov-Jan: 4.02%), not below 1 m/s (16.17%), and never tests "confused"/swirling wind. ERA5 grid shares also cannot be asserted as site-vane lower bounds without site measurements. **Fix:** align slide claims with the actual threshold, or implement/evaluate directional-variability gating on site wind.

7. **Major — zero doc-check problems do not imply validated facts.** `eval/check_docs.py:25,53-80`, `research/fact-check.md:14`: unmarked `₹999` is not tokenized; a false `{{v:F6|flat fine ₹500}}` passes because `500` is a substring of F6's `₹7,500`, even though F6 says the flat fine is ₹5 lakh. `eval/render_docs.py:54-66` also trusts manually entered TSV test scores. **Fix:** compare typed claim values/units exactly to verified source records; treat rendering/drift and factual or rerun verification as separate gates.

8. **Minor — ingest can preserve incomplete or mixed-unit datasets.** `components/ingest/fetch_openaq_archive.py:36-38,77-103`: failed month listings are silently skipped; failed daily fetches still produce parquet, existing parquet is subsequently skipped, and units are recorded but not checked before averaging. The lead's station 17 manifest records one failed file; the checked 6929 week matched and the four PM units currently agree. **Fix:** fail on any missing listing/fetch, validate units before aggregation and verify requested time bounds/completeness before accepting cached output.

9. **Minor — undefined false-alarm ratios print as zero.** `eval/forecast_eval.py:95-98`: `fa/max(1,hits+fa)` reports CAMS severe-day FAR=0 despite zero positive predictions and 89 observed events. **Fix:** emit `null`/N/A when there are no predicted positives.

**Post-hoc probe for findings 4-5 (same public simulation, not a new holdout):** from `components/attribution/autoresearch/`, after the memory check:

```sh
OMP_NUM_THREADS=1 nice -n 10 python - <<'PY'
import eval_v2 as e, methods as m, numpy as np
frame=e.load(); active=[]; ref14=[]; rect_oracle=[]
for name, sc in dict(e.SCENARIOS,**e.HIDDEN).items():
    for seed in e.HOLDOUT_SEEDS:
        obs,tmax,tdiff,geom=e.simulate(frame,np.random.default_rng(seed),sc)
        test=(obs.index>=e.TEST[0])&(obs.index<=e.TEST[1]+' 23:00')
        work=(obs.index.hour>=8)&(obs.index.hour<18)&(obs.index.dayofweek<6)
        pred,ab=m.ring_selfcal(obs,geom)
        active.append(e.score(pred,ab,tmax,tdiff,test&work)['mae'])
        vals={}
        for node in m.NODES:
            gain=obs[f'refvisit_{node}'].shift(1).rolling('14D',min_periods=1).median().ffill().fillna(1).clip(.2,5)
            vals[node]=(obs[f'raw_{node}']/gain).values
        pred,ab=m._ring(vals,obs,geom)
        ref14.append(e.score(pred,ab,tmax,tdiff,test)['mae'])
        if name=='hard-rect': rect_oracle.append(np.mean(np.abs(tdiff[test]-tmax[test])))
print(f'work_share={work[test].mean():.3f} active_MAE={np.mean(active):.2f} ref14_MAE={np.mean(ref14):.2f} rect_oracle_gap={np.mean(rect_oracle):.2f}')
PY
```

**Verdict:** Stored outputs reproduce and BOM/power arithmetic is correct, but the literal <=4% claim fails; no direct chronological or method-causality leak surfaced. **Do not present oracle GBM skill as operational or the fixed-simulator holdout as field validation.** The attribution ranking survives this audit, but its active-hour accuracy, reference comparison and calm/variable-wind behavior need corrected claims and an independent field test.
