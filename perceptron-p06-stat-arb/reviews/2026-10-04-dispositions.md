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

## `gpt-6-sol` (max): code, reproducibility, eval — items from its messages (labels are mine; reconciled with its review file's IDs when that lands)

| Item | Disposition | Reason / action |
|---|---|---|
| A1: concurrent intents can consume the same displayed liquidity | ACCEPTED | Amendment 1 S3 flags collisions and reports totals with them dropped. The frozen primary keeps its registered semantics, and the limitation is stated. |
| A2: an arrival long after the last quote still fills (stale quote) | ACCEPTED | S1 fills at the next published quote with a 1 s staleness cap. |
| A3: `size = 0` becomes a 0.05 BTC intent | ACCEPTED | S1 does not send size-0 intents. The frozen primary is unchanged, as registered. |
| A4: outcome labelled `both` with a zero-size leg | ACCEPTED | S1 labels outcomes from filled quantities. |
| A5: `breakeven()` claimed the "largest" profitable latency but reported the first crossing | ACCEPTED | It is now defined as the first crossing, with `*` marking non-monotone series (`eval/latency_budget.py`). |
| A6: `check_docs` did not verify `headline.json` against its sources | ACCEPTED | `check_docs` now rebuilds the headline from the result files and fails on any difference. |
| A7: lev.py and ADR said survival is an LEV feature | ACCEPTED | Corrected in `components/decision/lev.py`, the ADR status and the abstract. |
| B1: `strict.py` reused the last quote for markouts and unwinds past the end of the data | ACCEPTED | Erratum registered at 15:19 before the corrected run. Such rows are censored for every policy; 0 rows were affected on all 13 days. |
| B2: collision rule should be greedy (retain later rows) | WITHDRAWN by the reviewer (no change) | The implemented rule matches the registered definition (flags against earlier selected intents, no reallocation). |
| B3: "does not transfer" overstates V4 | ACCEPTED | The wording is now "has no established advantage over the threshold under strict fills", with the CI, set automatically from the interval. |
| R: reproduction of the 12-day primary (91 fields) and a raw rebuild of Feb | — | Matches; recorded in the thought node log. |
