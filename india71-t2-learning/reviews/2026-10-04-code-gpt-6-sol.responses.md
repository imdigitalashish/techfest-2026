# Lead responses — code + eval review (gpt-6-sol, max)

Review: [`2026-10-04-code-gpt-6-sol.md`](2026-10-04-code-gpt-6-sol.md). Reproduction confirmed by the reviewer: held-out coverage 174/180 = 0.967, MAE 2.157 vs 4.310 pp, half-width 5.974 pp; `headline.json` and seven other generated files byte-identical; 57 tests passed.

**Integrity rule applied:** fixes outside the frozen coverage path were made directly. Inside the frozen estimator only fail-closed validation was added, and the pre-registered held-out command was re-run afterwards: JSON (excluding runtime/command) and per-block CSV are **identical** to the committed results. Design-level fixes (#5, #6, #10) are a separate **v2** method with its own pre-registration on fresh seeds 201–230; the frozen v1 result is not reinterpreted.

| # | Severity | Issue | Decision | Fix / evidence |
|---|---|---|---|---|
| 1 | BLOCKING | Caller text authorises raw responses | ACCEPTED | `components/governance/policy.py`: fail-closed `TrustedContext` (server-side audit registry + cell counts); annotations in `target_scope` are ignored; auditor raw access now pseudonymised; aggregates without a trusted count are suppressed. 5 adversarial tests (forged `selected_for_audit=false`, fabricated flag, forged `n`, missing count). Reviewer's command now returns `False suppress`. Policy suite 42/42. |
| 2 | MAJOR | Dashboard bypasses small-cell control | ACCEPTED | `components/dashboard/core.py` routes every block through C12 with server-side counts; suppressed cells lose all numbers in HTML **and** JSON; n=8 integration test. |
| 3 | MAJOR | C4 thresholds from held-out truth | ACCEPTED | Frozen cut-points from development worlds 1–5 (`components/diagnostics/cutpoints.py` → `cutpoints.json`); evaluator and demo use them; worlds use the ASER calibration; `public_view()` drops truth-derived thresholds. C4 numbers regenerated (see `eval/results/headline.json`). |
| 4 | MAJOR | Missing audit still yields intervals | ACCEPTED | `assurance.py` raises `AssuranceUnavailable` unless every selected school is re-tested with children, has an inclusion probability, and double checks exist; tests for empty and partial audits. Never triggered in registered runs (identical re-run). |
| 5 | MAJOR | Recorded risk-PPS π ≠ sampler's π | ACCEPTED (v2) | New `select_audit(design="pps_systematic")`: fixed-size systematic PPS with certainty units — recorded π are exact first-order inclusion probabilities (test under the reviewer's skewed case). v1 left frozen; v2 evaluated under a new pre-registration. |
| 6 | MAJOR | FPC removes assessor-error variance | ACCEPTED (v2) | `meas_var_mode="v2"`: FPC on true-status sampling **plus** ε(1−ε)/(m(1−2ε)²) assessor term. |
| 7 | MAJOR | `truth_block` is a school mean | ACCEPTED | `world.py` now children-weighted; does not affect registered results (re-run identical). |
| 8 | MINOR | `risk_score` called a probability | ACCEPTED | Contract text: "relative risk score … NOT a calibrated probability"; schemas regenerated. |
| 9 | MINOR | Allocation API oracle fallback | ACCEPTED | Strategy dispatched first; oracle requires truth (evaluation-only); unknown/missing inputs raise. |
| 10 | MINOR | "20 % double-assessed" vs realised 16.9 % | ACCEPTED | Proposal states the realised protocol (2 of 12 per school, ≈ 17 %); dated clarification appended to the pre-registration; v2 draws checks across all re-tested children (`double_check_mode="pooled"`). |
| 11 | MINOR | "District average" was an equal-block mean | ACCEPTED | Post-hoc separation recomputed against the child-weighted district share, flagged denominator reported, plus a matched raw-report baseline. |
| 12 | MINOR | Registered minute vs committer minute | ACCEPTED | Dated correction appended to the pre-registration (author 15:44:58; committer 15:45:07 from the rebase before push; held-out results committed 15:48). Registered text not edited. |

Totals: 12 findings — 12 accepted (2 delivered as the separately pre-registered v2 method), 0 rejected.
