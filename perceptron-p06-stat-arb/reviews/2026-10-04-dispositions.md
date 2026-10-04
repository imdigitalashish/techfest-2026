# Lead dispositions of cross-model review items (PLAYBOOK §10)

Feedback is advisory and the lead decides. Each item is marked ACCEPTED or REJECTED with a reason and the action taken. Numbers are not repeated here; they live in the linked result files.

## `gpt-6-astra` (max): spike / ADR / pre-registration — [`2026-10-04-spike-adr-gpt-6-astra.md`](2026-10-04-spike-adr-gpt-6-astra.md)

| ID | Severity | Disposition | Reason / action |
|---|---|---|---|
| P6-01 | blocker | ACCEPTED | The frozen label is basis-adjusted execution surplus, not portfolio P&L. It is renamed in the abstract, memo and ADR. Amendment 1 adds markouts (positions marked at mids 1 s and 10 s after arrival): worlds V2 and V3 in `eval/results/sensitivity_amendment1.md`. |
| P6-02 | blocker | ACCEPTED | Sub-cadence fills cannot be identified on 26–100 ms publication grids. Amendment 1 S1 fills at the next published quote, as an adverse bound. Decay is reported with publication-time bounds (`eval/results/decay_report.md`). The abstract states the observability limit and gives the finals fix (tick-by-tick capture near the exchanges). |
| P6-03 | blocker | ACCEPTED | The 12 test days are described as "12 sampled months, 5 of them previously inspected", with the 7-month unseen subset alongside. The registered primary stands as registered. |
| P6-04 | major | ACCEPTED (partly) | Amendment 1 reports leave-one-day-out means and the largest single-day share. A fresh, untouched holdout with a pre-declared minimum effect is future work: the next first-of-month days. |
| P6-05 | major | ACCEPTED | The score is described as "summed over six fee/latency scenarios"; the per-cell table is in the walk-forward report. |
| P6-06 | major | ACCEPTED (partly) | S1 adds next-quote fills, a 1 s staleness cap and no size-0 intents. S3 measures shared-liquidity collisions and reports totals with them dropped. Inventory caps and depth-limited unwinds are not modelled yet; they are listed as finals work. |
| P6-07 | major | ACCEPTED | The clock test is described as a one-date sensitivity check, not deployment robustness. The abstract no longer cites it as evidence. |
| P6-08 | major | ACCEPTED | The target is named "expected execution surplus, clipped at ±30 bp". An effectively unclipped LEV (S4 `lev_noclip`) is reported. |
| P6-09 | major | ACCEPTED (partly) | Exploratory attribution added: LEV vs GBM classifier, vs LEV without the latency input, and vs a ridge baseline. The threshold's abstention option is a property of the registered baseline and is disclosed here. The training-window choice is unchanged (future work on development data only). |
| P6-10 | major | ACCEPTED | Residual-survival features were never in LEV. `components/decision/lev.py` and the ADR now say so, and survival is the MVP report plus a baseline (which trails the threshold). |
| P6-11 | major | ACCEPTED (partly) | Amendment 1 strict caches are fingerprinted (source blobs, data md5, parameters) and rebuilt on mismatch. The Azure run verified data md5 against `eval/results/data_manifest_wf12.tsv`. Primary caches: the 6 rebuilt days are byte-identical, and the result was reproduced independently by `gpt-6-sol` and from scratch on Azure. The primary caches themselves predate fingerprinting. |
| P6-12 | major | ACCEPTED | Novelty is reframed as "a falsification-first decision benchmark on public data, not a new learner". |
| P6-13 | minor | ACCEPTED | Team skills and ownership are a user input; they stay `[TEAM]` and are listed under *Needs from user*. Nothing is fabricated. |

## `gpt-6-sol` (max): code, reproducibility, eval — [`2026-10-04-code-eval-gpt-6-sol.md`](2026-10-04-code-eval-gpt-6-sol.md)

Reproduction: all 91 comparison and subset fields of the pre-registered 12-day result match. The February raw rebuild is byte-identical. `eval.headline` regenerates `headline.json` identically, `check_docs` passes, and Amendment 1 V1/V2 are confirmed. Its message also corrected one of my claims: cross-platform figures agree to within 6.8e-13, not bit-for-bit, and the wording is fixed in the thought node and provenance note.

| ID | Severity | Disposition | Reason / action |
|---|---|---|---|
| P6-C01 | blocker | ACCEPTED | Shared displayed liquidity is not decremented. Amendment 1 S3 flags collisions and reports totals with them dropped (within noise); the limitation is stated in the abstract and memo. |
| P6-C02 | major | ACCEPTED | `size = 0` becomes a 0.05 BTC intent in the frozen simulator. S1 does not send size-0 intents; the frozen primary is unchanged, as registered. |
| P6-C03 | major | ACCEPTED | `LegBook.at` returns the last quote indefinitely. S1 uses the next quote with a 1 s staleness cap. |
| P6-C04 | major | ACCEPTED | The outcome label used price booleans. S1 labels outcomes from filled quantities, which also affects λ for survival EV. |
| P6-C05 | major | ACCEPTED | The detector emits episodes at close (batch replay), so there is no streaming open signal yet. The live path is described as planned in the abstract and architecture page; the compiled step is quoted as in-kernel decision timing only. |
| P6-C06 | major | ACCEPTED | The skew variants shift the truth too, so they test a rephased market, not observer clock error. A scope note is appended to `falsification_clockskew.md`; only the receive-time replay is causal, and no clock-robustness claim remains in the abstract. |
| P6-C07 | major | ACCEPTED (fixed) | Break-even is now the first crossing, with `*` marking non-monotone series. |
| P6-C08 | major | ACCEPTED | The day score is a sum over six mutually exclusive counterfactual scenarios, and is described that way in the abstract. |
| P6-C09 | major | ACCEPTED (fixed) | `check_docs` rebuilds `headline.json` from the result files and fails on any difference. |
| P6-C10 | major | ACCEPTED (fixed) | `lev.py` and the ADR no longer claim survival features. |
| P6-C11 | minor | ACCEPTED (fixed) | `decay_report` now raises on a missing day or a cache without `t_start_us`. No reported result was affected: all 13 days were present. |
| P6-C12 | minor | ACCEPTED | Detector time is a day-long amortised average, and is labelled "amortised"; no detector p99 is claimed. |
| P6-C13 | minor | ACCEPTED | "oracle" means naive at zero latency; a naming note is appended to `baseline_0901_to_1001.md`. |
| P6-C14 | minor | ACCEPTED | Relative uplift over a negative base (threshold − naive) is meaningless. The headline quotes relative uplift only for LEV − threshold, where the base is positive. |
| P6-C15 | blocker | ACCEPTED | The basis-adjusted mark credits unrealised surplus. It is renamed "simulated execution surplus"; markouts are in Amendment 1 S2; no claim of earned P&L. |
| P6-C16 | major | ACCEPTED (fixed) | Post-end markout and unwind reuse: erratum registered before the corrected run, 0 rows affected. |

## `gpt-6-astra` (max): final abstract — [`2026-10-04-abstract-gpt-6-astra.md`](2026-10-04-abstract-gpt-6-astra.md)

Score 62/100 (3.10/5), up from 53/100.

| ID | Severity | Disposition | Reason / action |
|---|---|---|---|
| P6-A01 | blocker | ACCEPTED | Reworded to "observed median … illustrative 11.3–147.1 ms sensitivity range, not a bound on executable lifetime". Next-quote fills are a "stress scenario". The finals fix is now finer channels (our recorder: `eval/results/live_cadence.md`), not proximity. |
| P6-A02 | major | ACCEPTED | Paper trading is "planned"; the abstract says replay and latency-budget analysis run and live recording works. Simulated fills are not claimed to validate fillability. |
| P6-A03 | major | ACCEPTED | The legacy top-decile LEV example is removed. The ranking sentence is labelled with one test day, nine markets, 1 bp fees and one-way latency. |
| P6-A04 | major | ACCEPTED | The uncalibrated laptop latency range is removed from the abstract and the architecture page. |
| P6-A05 | minor | ACCEPTED | Collision share is now pooled over selected intents (22%); the retained share is given for both worlds (V1 24%, V2 23%). |
| P6-A06 | minor | ACCEPTED | "A regressor trained on execution-surplus labels clipped to ±30 bp". |
| P6-A07 | major | ACCEPTED (needs user) | Team skills, motivation and ownership must come from the user; nothing is fabricated. Listed under *Needs from user*. |
| P6-A08 | major | ACCEPTED | The architecture page is regenerated: published-quote fills, the clipped-label ranker, survival as report and baseline, future work marked, sensitivity results in the table. |

## `gpt-6-astra` (max): demo, "judge watching the demo" — [`2026-10-04-demo-gpt-6-astra.md`](2026-10-04-demo-gpt-6-astra.md)

Scores: wow 3/5 · clarity in 3 minutes 2/5 · honesty/rigour 3/5 · robustness 3/5 · problem fit 5/5. Verdict: "credible, well-instrumented replay benchmark; not yet a reliable three-minute finals demo." Smoke passed 18/18 on the reviewer's own run. All findings were sent to the demo builder in priority order.

| ID | Severity | Disposition | Action (by the demo builder; verified by the lead) |
|---|---|---|---|
| P6-D01 | major | ACCEPTED | Select the race episode first by a disclosed, outcome-independent rule, then a 1× lead-in; add cancel and a presenter deadline; keep every trial, false start and timeout visible. |
| P6-D02 | major | ACCEPTED | A named race setup snapshots frozen / 1 bp / 1 ms; the script narrates current values and keeps window vs day distinct. |
| P6-D03 | major | ACCEPTED | Label $/day as "mean day-level uplift, summed over 6 fee/latency scenarios" on the cards and in the script. |
| P6-D04 | major | ACCEPTED | Make LIVE / offline / error state consistent: request timeouts, stale notice, readiness retry, regression check if feasible. |
| P6-D05 | major | ACCEPTED | "12 sampled first-of-month days, 5 previously inspected", with the unseen-7 result alongside. |
| P6-D06 | major | ACCEPTED | "Illustrative sensitivity range, not a bound on executable lifetime" (as in the abstract). |
| P6-D07 | major | ACCEPTED | Relabel the laptop presets "receive−venue timestamp p05, clock offset unresolved"; remove "floors" and the arrow. Same root cause as abstract finding P6-A04. |
| P6-D08 | major | ACCEPTED | A compact 3-step stage view (replay → race → evidence); the dashboard stays for Q&A. |
| P6-D09 | minor | ACCEPTED | Derive the abstention caption from the full-day cells; remove the band text when the band is absent. |
| P6-D10 | minor | ACCEPTED | The offline ratio is labelled against the right quantity (committed p50 vs the 7 µs allowance). |
| L1 (lead) | minor | — | Two naive break-even figures appear on screen, from different leg sets (9-leg 4.6 ms vs 5-leg 2–3 ms); name the leg set at each. |
