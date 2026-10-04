# Hostile-judge review 01: Poshan Setu (4 Oct 2026, 08:45 IST)

> Produced by an independent adversarial agent (`rubber-duck`) briefed as a hostile Round-2 juror: a public-health researcher who has worked with Anganwadi unions and the Right to Food campaign. It read the proposal draft v0.1, ADR 001, the first 60 lines of `engine.py` and landscape §1 and §3. The agent could not write files, so the lead saved its review here, condensed but faithful. Legal claims it made (e.g. a commencement date for DPDP s.9) are **UNVERIFIED** until checked in [`sources/V1-dpdp-verified.md`](sources/V1-dpdp-verified.md).

## Eight questions, ranked by damage (all rated "blocking" by the judge)
1. **Legal authority to track and score named children.** Pseudonymisation is not anonymisation; DPDP s.9(3) restricts tracking and behavioural monitoring of children. Which Data Fiduciary, purpose and exemption authorises child-level risk scoring? The s.7 State-service ground does not by itself answer s.9.
   - *Honest answer:* not yet established; child-level scoring is a research prototype until counsel confirms an exemption or consent route.
   - *Change:* a legal go/no-go gate before any child-level model runs, plus a field-by-field purpose, retention and access map. If no valid route exists, ship only aggregate measurement-quality support.
2. **Why isn't this algorithmic discipline of AWWs?** The ADR says "AWC/worker-level"; an AWC score is effectively a named-worker score; "never punitive" is a sentence, not a system property.
   - *Change:* no worker identifiers and no persistent scalar score. Use temporary AWC/device/month diagnostic flags, equipment and process support first, and hard-deny HR, pay and disciplinary purposes in policy-as-code *and* the data-sharing agreement. Workers see the evidence, can correct it and can appeal before any supervisory action.
3. **How much of 19.3% vs 5.46% is actually under-detection?** Age bounds, timing, season, weighting, registered vs measured children and selection are not harmonised. Matching stunting is not a valid control.
   - *Change:* delete the "6 lakh per point" extrapolation and call it an *unexplained discrepancy*. The pilot's first task: a concurrent, independently measured, age/month/geography-matched sample that decomposes coverage, measurement and classification effects.
4. **Synthetic AUROC is the code recognising its own generator.**
   - *Change:* present synthetic figures as *simulation checks*, not validation. Pre-register a blinded validation (independent enumerators, calibrated equipment, random AWCs) reporting PPV, false positives, calibration and subgroup errors. Freeze thresholds first.
5. **Which workers or unions agreed to be scored?** Six unions are litigating FRS.
   - *Change:* paid co-design with union nominees and AWWs from tribal, migrant and low-connectivity areas. A written protocol on prohibited uses, workload, access, correction and grievance. Worker seats in pilot governance; no field pilot without agreement.
6. **Workers will learn to add fake noise (Goodhart).** `low_wasting_vs_peers` penalises low recorded wasting, and "convergence to survey prevalence" as a success metric is self-fulfilling.
   - *Change:* remove both. Keep diagnostics transparent and separately actionable. Random independent re-measurement in flagged *and* unflagged AWCs. Red-team with AWWs asked to game it.
7. **Hard-to-reach AWCs will be labelled untrustworthy.** Batch entry after outages, broken or coarse scales, civil-registration DOB practices and migration all mimic "low credibility".
   - *Change:* separate missingness, device, connectivity and epidemiology diagnostics. No output below a minimum effective sample, and uncertainty shown. Compare like with like. Equipment, connectivity and staffing review come first. Publish false-positive rates by remoteness, tribal status, migration burden and caseload.
8. **What changes after detection?** If rations, scales, NRC beds, transport or ANM time are missing, an SLA only documents AWW failure. ICDS-CAS improved visits, not feeding practices.
   - *Change:* a service-readiness gate. Missing inputs escalate upward *before* an AWW SLA clock starts. Measure workload, harms, independent anthropometry and completed treatment, not dashboard closure.

## Verdict: changes required before 1 Nov
1. Replace worker credibility scoring with transparent AWC/device measurement-system diagnostics. Equipment first, random re-measurement, correction and appeal; employment and disciplinary use prohibited technically and contractually.
2. Rights governance before rollout: union/AWW co-design, a collective protocol, independent grievance, workload caps, and a DPDP legal go/no-go for child-level prediction (disable it if no basis).
3. Rewrite the evidence story: an unresolved discrepancy, not proven under-detection. Synthetic metrics are unit tests. Pre-register concurrent blinded validation with subgroup false-positive analysis.

## Lead's response
All three accepted. See [ADR 002](../architecture/adr/002-measurement-diagnostics.md) and proposal v0.2.
