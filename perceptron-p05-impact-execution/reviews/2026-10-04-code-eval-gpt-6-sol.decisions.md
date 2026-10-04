# Lead decisions on the gpt-6-sol code/eval/reproduction review (written 2026-10-04 13:10 IST)

Raw review: [2026-10-04-code-eval-gpt-6-sol.md](2026-10-04-code-eval-gpt-6-sol.md), commit ad57fa0.

Reproduction result accepted as evidence: 12/12 re-run rows matched on 25 stable CSV fields; H1 paired IS −0.034039 bps.

| # | Severity | Finding (short) | Decision | Reason / action |
|---|---|---|---|---|
| 1 | major | Calibration fit/holdout used lexicographic file order (seeds 20–26 in the fit half) | **ACCEPTED** | `eval/calibrate.py` now sorts numerically and records `fit_seeds`/`oos_seeds`. E9 was recomputed on the registered split (fit 0–19, OOS 20–39): r2_mean_path TWAP +0.15, PROBE −0.02, so the criterion is still not met. E1 was recomputed on the same split for comparison (`calibration_e1_numeric_split.json`). The frozen `calibration.json` that the policies use is kept: its fit set {0,1,2,10–26} is train-only, so there is no test leakage, and changing it would break E3–E10 reproducibility. |
| 2 | major | Passive fills put decision-to-fill movement into `instant_bps` | **ACCEPTED** | Docs now say "cost vs the decision-time mid (includes decision-to-fill movement for passive fills)" instead of "spread/book-walking cost". A 4-way split (drift / own impact / delay / at-fill cost) will be added to `tca` after E10 finishes (its workers import that module). Existing CSVs are unchanged. |
| 3 | major | E7 bootstrap conditions on positive draws; formal "square-root-like" label misleading | **ACCEPTED** | The registered verdict text is preserved, but every deliverable states the conclusion as near-linear. Added post hoc: δ over resolved sizes = 0.87 [0.57, 1.35] with 100% of draws valid. Future registered tests will specify a failure rule for non-positive draws. |
| 4 | minor | QP diagonal has inst_cost + ½·g_tr, but the docstring omits the ½·g_tr term | **ACCEPTED (documentation)** | The ½·g_tr·x² term is the intended self-impact of a block trade: a trade walking a linear book pays, on average, half of its own end-impact. Docstring fixed. Schedule unchanged, to keep E5–E10 reproducible. |
| 5 | minor | `pre_window_identical` is `np.allclose` on 1-s mids, not bit identity | **ACCEPTED** | Docs now say "pre-trade mids equal (1-s sampling, ≈1¢ tolerance)", not "bit-identical". An exact check (array equality on every pre-trade book update, plus equal arrival mids) is added for runs after E10. |
| 6 | minor | Ratchet `eval.py` bootstrap depends on worker completion order | **ACCEPTED** | v2 sorts seeds before resampling. It is re-frozen; v1 never completed a run. |
| 7 | minor | Four-decimal H1 verdict had no committed generator; tail fraction called a p-value | **ACCEPTED** | Committed `eval/h1_verdict.py` (reproduces −0.0340 [−0.0563, −0.0127], one-sided upper bound −0.0160). The canonical file is `eval/results/E6_confirm_sync_H1_verdict.md`. "p ≈ 0.0006" is replaced by "bootstrap tail fraction". |
