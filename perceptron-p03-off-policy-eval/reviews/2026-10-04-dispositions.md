# Review dispositions — lead decisions on the 4 Oct cross-model reviews

Raw reviews:
- [`2026-10-04-abstract-decomposer-gpt-6-astra.md`](2026-10-04-abstract-decomposer-gpt-6-astra.md): hostile judge, **59/100**, pinned to abstract `5ab7b67`.
- [`2026-10-04-code-eval-gpt-6-sol.md`](2026-10-04-code-eval-gpt-6-sol.md): code/eval review; **44/44 abstract numbers reproduced byte-identically** (the late-added ±0.27 recomputed independently).

The feedback is advisory and the lead decides (PLAYBOOK §10). Every item below is ACCEPTED, some partly or with a deferred part; none is rejected, because each was checked and found valid. "Deferred" items have a date in *Now* / *Next* of the thought node.

## gpt-6-astra (hostile judge)

| # | Severity | Decision | What changed |
|---|---|---|---|
| A1 | blocker | ACCEPTED | `eval/apply_gate_obd.py` now reports three separate endpoints: S1 non-rejection, reference inside DR's own CI, and confident wrong sign. It also reports distinct instances (day pairs sharing an after-day count once). The 25 Nov rollback row (S1 passes, CI misses the reference) is in the table. The abstract no longer says "0 wrong". |
| A2 | blocker | ACCEPTED | "Within 0.1% of its on-policy truth" is withdrawn. The static-prior and hourly comparisons are reported as approximate-target discrepancies against the BTS arm's CTR, since the deployed policy was adaptive. |
| A3 | major | ACCEPTED | Primary estimand: the after-period traffic-standardised contrast D₁. Secondary: the Shapley attribution with interaction. The ordered mix/drift split belongs to the old-policy ordering and is labelled so. `components/report/verdict.py` gates every off-policy cell the reported term needs. Abstract and diagram rewritten accordingly. |
| A4 | major | ACCEPTED | The gate design is labelled exploratory and post-OBD. A new **pre-registered held-out validation** (`eval/preregistration_gate_holdout.md`, commit d9de82e, before results) runs on unseen worlds and settings. |
| A5 | major | ACCEPTED | The inactive reward floor is stated. Absolute ESS is reported. The ungated baseline is fixed (C7). The held-out bank adds near-null and harmful effects, 10/40 actions and 5k/20k rows. |
| A6 | major | ACCEPTED | Distinct instances are counted. Results are labelled confirmatory (pre-registered), deviation, or post hoc. |
| A7 | major | ACCEPTED (partly resolved) | Raw labels were inspected in the official zip (`eval/results/obd_raw_labels.md`). In each feature, one category has a different raw label in each file, with matching shares; the other labels match. The OBD README says the data come from an A/B test. The caveat stays as **UNRESOLVED**. |
| A8 | major | ACCEPTED (partly) | Hour-block bootstrap for the headline OBD numbers, and a DM refit bootstrap (`eval/obd_block_bootstrap.py`, post hoc). User- or slate-level clustering is impossible because OBD has no user IDs; this is stated. |
| A9 | major | ACCEPTED (part deferred) | The DR mix residuals are now cross-fitted, and the before-logger restriction is documented. The 2×2 nuisance-correctness matrix (oracle reward model / oracle density ratio) is deferred to the 15 Oct protocol freeze. |
| A10 | major | ACCEPTED | Wording is now "Monte-Carlo reference" and exact counts (419/440) instead of "95%". The held-out bank uses fresh worlds. Per-condition seed counts are stated as a limitation. |
| A11 | major | ACCEPTED | Labelled an after-period Hajek-MSM analysis. Validity is quoted at Γ = 10, which is at least the proved bound e² ≈ 7.39 for κ = 1. The intervals are nested in Γ, so containment at Γ = 7 implies containment at Γ = 10. Γ\* is called a grid crossing. |
| A12 | major | ACCEPTED | Novelty is reframed as an integration/protocol claim. The abstract cites Lee et al. 2026 and OPEN (Chandak et al., NeurIPS 2022); no priority claim. |
| A13 | minor | ACCEPTED | Units are explicit (percentage points; clicks per 1,000). The body is ≤ 900 whitespace words. The maintenance preamble is dropped from the submission copy. |
| A14 | major | ACCEPTED (partly) | Explicit freezes: estimand fixes by 10 Oct, protocol freeze 15 Oct, held-out analysis 24 Oct, submission 28 Oct. Teammates' names and skills need the user (*Needs from user*). |

## gpt-6-sol (code / eval / reproducibility)

| # | Severity | Decision | What changed |
|---|---|---|---|
| C1 | blocker | ACCEPTED | "+1.26" is now called the observed concurrent arm difference: an A/B reference per the OBD README, not an established population truth. The balance caveat is kept (see A7). |
| C2 | blocker | ACCEPTED | Same as A2. |
| C3 | major | ACCEPTED | The DM refit bootstrap shows the fixed-prediction SE was about 266× too small, and DM's "NO" consistency becomes yes. The pre-registered table is unchanged; the correction is in `eval/results/obd_block_bootstrap.md`. |
| C4 | major | ACCEPTED | The abstract states that the gate abstains on the flagship deploy case. |
| C5 | major | ACCEPTED | Fixed guards (zero informative rewards, non-finite diagnostics) and the reviewer's counterexample as a test. The chosen rule is unaffected: no calibration run trips the guards. |
| C6 | major | ACCEPTED | `ground_truth` V(before, new) now uses the deployed new policy, including the override. |
| C7 | minor | ACCEPTED | `calibrate_gate.py` computes a true no-gate baseline; a correction note is added to `gate_calibration.md`; the headline reads the corrected value. |
| C8 | minor | ACCEPTED (OBD part deferred) | `shapley()` returns a paired environment interval. Adding it to the OBD tables needs a re-run of the pre-registered script, which is deferred to the next OBD run. |
| C9 | minor | ACCEPTED | The 5-cell × 48-hour distinct-propensity readout is disclosed as a deviation from the registered readout; it does not affect the 20/20 decision. |

## gpt-6-astra re-score of v3 (commit 2371208): 69/100, no blockers

| # | Severity | Decision | What changed (abstract v4) |
|---|---|---|---|
| A15 | major | ACCEPTED | The holdout's "near-null" group is renamed a *small scorer-quality-gap configuration* (its effects range up to about 10 points). The committed run is kept as is. A new, separately frozen near-zero-contrast test is planned for the 15 Oct protocol freeze. |
| A16 | major | ACCEPTED | Confident wrong sign is now reported over effect rows only: 0/4 listed, 0/3 distinct answered effect instances. Value rows show n/a (`eval/apply_gate_obd.py`). |
| A3 (residual) | major | ACCEPTED | `components/report/verdict.py` takes its primary decision only on the after-period contrast, and only when its gate passes. Otherwise the verdict is "can't tell"; the before-period and Shapley terms are secondary and never replace it. Demo: OBD deploy halves → **cant_tell** (`eval/results/demo_verdicts.md`). |
| A11 (residual) | major | ACCEPTED | The verdict attaches the MSM curve only as "after-period Hajek-MSM: the interval first includes zero at tested Γ". |
| A2/A4/A8 (residual wording) | major | ACCEPTED | The judge's safe rewrites are applied: an approximate-target comparison; the gate's design chronology; both row-level and hour-block intervals shown for the flagship case. |
| A10 (residual) | major | ACCEPTED | The diagram now says "Monte-Carlo reference" and "noisy concurrent-arm reference; policy matching & balance limits disclosed". |

## gpt-6-astra demo review (pinned f58966c): wow 7, clarity 4, credibility 6, honesty 5 (out of 10)

All 12 items are ACCEPTED; the builder is applying them (demo/ only). No item is rejected, and no threshold or analysis is re-tuned.

| # | Severity | Decision | Fix |
|---|---|---|---|
| D1 | blocker | ACCEPTED | The A/B line becomes a "noisy concurrent-A/B reference, not known truth", with its caveats under the chart. The script opens with "we re-enact a switch". "29% above the concurrent A/B point estimate". |
| D2 | blocker | ACCEPTED | E1 and E2 shown side by side; the Nov 26 cluster-mode E2 rejection is visible. Sheet 1 says "2/2 S1 rejections; 2/3 own-CI misses refused". BTS-primary counts (75/87, 519/606 refused) are shown separately from the Random side. |
| D3 | major | ACCEPTED | "Before touching OBD" and "never examined before" removed; the chronology is stated as "pre-registered reuse of OBD". |
| D4 | major | ACCEPTED | "31/33 endpoint-derived checks"; the endpoint formulas are shown; SNIPS is not called new evidence. |
| D5 | major | ACCEPTED | The 403 refusals are correlated grid locations under a noisy-reference proxy; deployment value is untested. |
| D6 | major | ACCEPTED | The script is cut to 350–400 spoken words, with a timed rehearsal and named presets. |
| D7 | major | ACCEPTED | Presets set the full state; the script restores row-level before row-level totals. |
| D8 | major | ACCEPTED | ESS is called a concentration diagnostic; the 12,500 weight is hypothetical (largest clicked weight about 139); the z-test does not prove cause. |
| D9 | major | ACCEPTED | "Monte-Carlo reference (200,000 draws)"; the S1 waterfall is labelled as a separate fixed case. |
| D10 | minor | ACCEPTED | Dynamic readouts get source keys, or the hover claim is narrowed. |
| D11 | minor | ACCEPTED | Render, same-code replay and independent checks are described separately. |
| D12 | minor | ACCEPTED | Fallback 08 re-captured through the normal controls; the fallback set matches the script. |
