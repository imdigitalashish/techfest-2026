# Per-component innovation notes (v0, 4 Oct 2026)

> Lead-written overnight in lean mode (research sub-agents failed on network timeouts; the Supervisor then disallowed sub-agents). Each note gives: the baseline we use, where the innovation room is, candidates, and the isolated metric. Literature and product names marked **[L]** are leads not opened tonight — **UNVERIFIED** until checked. Facts marked [P*] are from [`../landscape.md`](../landscape.md) §6.

## C6 Targeting & prioritisation engine — SPIKE A

- **Baseline in production:** blanket outreach — alerts before inoperativity and quarterly letters/SMS to all inoperative holders [P2]; campaign drives to re-KYC inactive accounts [P1, P2].
- **Our baseline (built):** T-learner uplift (one gradient-boosted classifier per arm) + Lagrangian multiple-choice knapsack under a rupee budget, women's-share floor via a bonus term, 10% holdout (contract `InterventionPlanRow`).
- **Measured (SYNTHETIC, 3 seeds, corrected evaluator, `eval/results/c6_*.json`):** normalised policy value 0.30 ± 0.04 (T-learner), 0.33 ± 0.02 with shrinkage (kept), vs best-arm-for-all 0.37, status quo 0.04, risk ranking −0.07, oracle 1.0.
- **v0.2 (pre-registered 14:00 IST, fresh SYNTHETIC seeds 10–19; `eval/preregistration/c6_v02_results.md`, ADR 002):** transparent rule 0.38 ± 0.19, learned who-only challenger 0.46 ± 0.19 (paired +0.079, 95% CI 0.058–0.100, 10/10), best-arm-only 0.29, status quo 0.03; the gate deployed the challenger in 0/10 worlds (~840 validation persons) and the rule collapsed in 2/10 worlds (pilot ranked arms wrongly). Deployed policy: the rule; the model is a gated challenger.
- **Innovation room:** (1) noise-aware allocation — shrinkage toward arm means, lower-confidence-bound allocation for expensive arms (winner's-curse control); (2) policy *selection* by doubly-robust off-policy value on a pilot split, so the system never deploys a learned policy that loses to a simple rule; (3) adaptive experimentation (Thompson sampling over arms per segment) so the holdout keeps learning [L: Kasy & Sautmann 2021; Hadad et al. 2021]; (4) person-level (not account-level) allocation, which removes double-visits to multi-account holders; (5) fairness/equity constraints with reason codes for explainability [L: Athey & Wager 2021 policy learning; Kitagawa & Tetenov 2018].
- **Metric:** normalised policy value at fixed budget, averaged over seeds; fresh-seed re-checks. Loop: [`../../components/targeting/autoresearch/`](../../components/targeting/autoresearch/).

## C10 Usage scorecard & attribution (+ C11 DP publisher) — SPIKE B

- **Baseline in production:** review of enrolment-type counts and the national FI-Index; the breakdowns needed for usage accountability are "not centrally maintained" [P1, P3].
- **Innovation room:** (1) person-level meaningful-usage rate per district/bank/BC (counts people once); (2) *incremental* usage attributable to an implementer, from holdouts (C9) or comparison with matched units, with confidence intervals; (3) gaming detectors — token credits, reactivate-then-lapse patterns, account churn; (4) differential privacy with a privacy-budget ledger and small-area pooling so district tables are publishable [L: US Census 2020 TopDown; OpenDP]; (5) Goodhart-resistant definitions (customer-induced, persistence-weighted, multi-dimensional).
- **Metric:** Spearman ρ between implementer ranking and true causal contribution in simulated worlds with injected gaming; DP MAE (pp) of district rates at ε = 1.

## C2 Usage-state classifier + Meaningful Usage Score

- **Baseline:** RBI "inoperative" = no customer-induced transaction for two years [P3]. **Built:** five-state rule set with reason codes; MUS = frequency, diversity, retention, protection.
- **Innovation room:** a "DBT pass-through" state (credits cashed out within 7 days, no other use) that today counts as "operative"; gaming guard (token credits never count); publishing the rules so anyone can recompute. **Metric:** macro-F1 vs simulated truth; gaming inflation (pp per ₹ of token credits).

## C3 Tokeniser + person linker / C4 clean room / C5 policy engine

- **C5 built v0** (`components/policy_engine/`): deny-by-default rules citing verified sources; 22/22 governance scenarios, 0 false allows; hash-chained audit log + published checkpoint, tampering detected 65/65 (`eval/results/policy_engine.json`). Scenarios were written with the rules — this shows fidelity to the published matrix, not legality.

- **Baseline:** NPCI mapper and CKYC identify accounts for DBT and KYC [L]. **Built (C3):** purpose-scoped HMAC tokens — tokens for targeting cannot be joined with tokens for statistics (tested).
- **Innovation room:** linkage *inside* a confidential-computing clean room [L: DEPA Training; cloud confidential clean rooms]; private set intersection for cross-bank duplicates [L]; policy-as-code purpose binding with a hash-chained audit log (C5) [L: Open Policy Agent; transparency logs]. **Metrics:** pairwise linkage F1; governance-scenario accuracy (C5); red-team leakage count (C4).

## C7 Fraud & safety gate

- **Baseline:** bank AML rules [L]; RBIH MuleHunter.AI [L]. **Innovation room:** reactivation-specific risk (reactivated after long dormancy + sudden high-value inflows + new device) and a "verify" path through the BC rather than a blanket hold. **Metric:** recall of injected mule accounts at 1% false-positive rate.

## C8 Last-mile orchestrator

- **Baseline:** branch camps, bulk SMS, paper BC lists. **Innovation room:** local-language IVR/voice into UPI 123PAY [L], BC Sakhi routing for women [L], route-aware BC task lists, re-KYC at the doorstep. **Metric:** completed interventions per BC-day under a fixed route budget.

## C9 Outcome & experiment service

- **Baseline:** before/after counts. **Innovation room:** standing randomised holdouts per district and arm; effect estimates by segment and implementer with CIs; CUPED-style variance reduction using pre-period usage [L]. **Metric:** RMSE of arm effects vs simulator truth; 95% CI coverage.

## C11–C13

- **C11 DP publisher:** Laplace/Gaussian mechanisms with a budget ledger; small-cell suppression. Metric: MAE at ε = 1.
- **C12 dashboards:** role-scoped views for DFS/RBI, SLBC, DLCC/LDM, bank/branch, BC, public. Metric: data latency (≤ 10 days after month-end).
- **C13 public-data gap mapper:** real state table built ([`../../eval/public_data/`](../../eval/public_data/)); next: NFHS-5 district indicators, DBT Bharat totals. Metric: coverage of validated indicators.

## C14 Simulator

- Calibrated to the official ~23% inoperative share; all other parameters are labelled ASSUMPTION in [`../../components/simulator/calibration.json`](../../components/simulator/calibration.json). **Next:** replace effect-size assumptions with ranges from published RCTs on account usage (verification backlog item 9).
