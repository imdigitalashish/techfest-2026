# ADR 002: Spike A becomes measurement-system diagnostics, not worker scoring

- **Status:** accepted, 4 Oct 2026 09:00 IST. Supersedes the "credibility score" framing in [ADR 001](001-spike.md); the spike choice itself (A + B) stands.
- **Trigger:** two pieces of evidence:
  - The [hostile-judge review 01](../../research/hostile-judge-01.md) rated eight objections as blocking: worker discipline, union consent, Goodhart effects, remote-AWC bias, the legal basis for child scoring, synthetic validation, gap confounders, and the lack of service readiness.
  - The first auto-research iteration was rejected because its gain did not generalise to a different fabrication pattern ([`results.tsv`](../../components/credibility_engine/autoresearch/results.tsv)).

## Decision
1. **Unit = AWC × device × month, never a worker.** The engine outputs *separately actionable diagnostics*: implausible records, digit/DOB heaping, dispersion, trajectory realism and missingness. There is no persistent scalar "credibility" shown to managers and no rank. The internal composite is used only to pick which AWCs get a *random-plus-targeted* re-measurement visit.
2. **Support before scrutiny.** First action on any flag: an equipment calibration check and a connectivity/stock review by the Lady Supervisor. A re-measurement of 10 children is the second step. Re-measurement also runs in a random sample of *unflagged* AWCs, which keeps the system honest and produces unbiased ground truth.
3. **Employment use is technically impossible.** New contract purpose `employment_action` (contract v0.2.0), denied first-match by `deny-employment-action` in [`policy.yaml`](../../components/policy_gate/policy.yaml). It is covered by red-team tests (31/31 pass) and must be mirrored in the data-sharing agreement. Workers see the same diagnostics as supervisors, can annotate them ("scale broken since 12th"), and have an appeal route.
4. **No Goodhart targets.** Removed `low_wasting_vs_peers`; prevalence "convergence to the survey" is no longer a success metric. Remote, high-migration and low-connectivity AWCs are compared only with similar AWCs, and no output is shown below a minimum sample.
5. **Child-level prediction is behind a legal go/no-go gate.** Spike B (early warning) runs only after the responsible Data Fiduciary and the exact DPDP basis for children's data (s.9 and the Rules' exemptions, or verifiable parental consent) are confirmed in writing. Verification is in progress ([`V1`](../../research/sources/V1-dpdp-verified.md)). Without that basis the deployable product is the aggregate measurement-quality and routing layer.
6. **Service readiness before SLA clocks.** An alert whose required input is missing (scale, rations, NRC bed, transport) escalates the *input gap* upward first. The AWW's clock starts only when the input exists.
7. **Evidence language.** 19.3% vs 5.46% is an *unexplained discrepancy* to be decomposed (coverage / measurement / classification / true change) by a concurrent, blinded re-measurement study in the pilot. Synthetic metrics are labelled *simulation checks*.

## Consequences
- The frozen v1 evaluator stays as a regression test. A v2 evaluator should measure the *audit value* of diagnostics: PPV of flagged AWCs for true measurement problems at a fixed re-measurement budget, false-positive rate in remote/tribal/migrant AWCs, and robustness across fabrication and equipment-failure patterns, including the simulator variants used in `holdout_check.py`.
- The proposal (v0.2) adopts this framing; union/AWW co-design and a collective protocol become pilot prerequisites in the roadmap.
