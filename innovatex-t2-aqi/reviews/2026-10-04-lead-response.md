# Lead response to the cross-model reviews of the final package (4 Oct 2026)

Reviews: [`2026-10-04-final-deck-gpt-6-astra.md`](2026-10-04-final-deck-gpt-6-astra.md) (hostile judge, snapshot `4758e64`) and [`2026-10-04-code-eval-gpt-6-sol.md`](2026-10-04-code-eval-gpt-6-sol.md) (code/eval, `41e391e`). The feedback is advisory; the lead decides. **A** = accepted, **P** = partly accepted, **R** = rejected. Everything below is applied in the commit that adds this file, unless marked *deferred*. Re-render and check: `python3 eval/render_docs.py && python3 eval/check_docs.py` → 0 problems.

## gpt-6-astra (max) — hostile judge

| Item | Decision | What changed / why |
|---|---|---|
| 1.1–1.8 scores | noted | Mean 2.29 (core) / 2.50 (incl. bonus). The memo now scores T2 lower than before (see `thought_node.md`). |
| 2.1 IIT Kanpur share is historical and category-specific | A | Slide 4, Q2, memo and pitch say "in that study (2013–14 data)" and note that track-out is counted as road dust. |
| 2.2 F6 fine misread | A | The lead had already found this independently at 16:03 (lead re-verification, before this review arrived). Now: ₹1–2 lakh per construction-site violation under CAQM's 2024 schedule *as reported*, with "current operative order UNVERIFIED"; the "% of a fine" ratio is removed everywhere. |
| 2.3 WAP is reporting, not the order | A | Slide 2 says "reported plan … not the operative order"; B8 says "reporting". |
| 2.4 DTE survey was Aledia's; date the figures | A | F8 row corrected; slide 4 and B8 attribute the survey to Aledia and date the rolls "Dec 2024"; the bottom line no longer implies wages DustLedger would protect. |
| 2.5 CSTEP doesn't validate our method | A | Q3 says so explicitly. |
| 2.6 "Delhi stops every site … because it can't tell them apart" | A | Replaced everywhere (deck, card, pitch, memo, one-liner) with "restrictions follow the activity and the pollution stage, not each site's measured dust"; GRAP exemptions mentioned on slide 2. Phrases added to check_docs' STALE list. |
| 2.7 Disagreement-based abstention isn't implemented | A | Q6 and slide 6 say the swirling-wind / node-disagreement check is planned, not built; "estimate … an inference, not proof of cause". |
| 2.8 0.5 vs 1 m/s; "lower bounds" unsupported | A | Slides 6–7, B4, Q4 and the card state the real 0.5 m/s threshold and coverage; "lower bound" claims removed (STALE-listed). |
| 2.9 Sequencing; "needs no permission" | A | Prototype plan and slide 9 rebuilt: nodes bench-built 13–19 Oct, side-by-side 20–26 Oct, real-site window 27–31 Oct only with a site and approvals; an approved, safety-controlled test is the default and is never called field validation. "Needs no permission" deleted. |
| 2.10 Power figures are model estimates | A | Slide 8, Q13 and the plan label them "model estimate". |
| 2.11 "where nobody is", "Nobody measures …", ADR combustion/PM10 claims | A | Removed or bounded ("we didn't find … in the product pages we reviewed"); ADR thesis table corrected. |
| 3.1 Whose coarse dust? | A | Q3: differences aren't causal proof; side-by-side, reference co-location and a blind known-source test come first. |
| 3.2 Does the error support decisions? | P | Work-hour MAE, coverage, POD and FAR are now on slide 7 / B5 (from `breakdown_v21.json`). Per-threshold rates for choosing an action threshold: *deferred* to the next ratchet. |
| 3.3 Who pays without exemptions? | A | Q10 and slide 8: willingness to pay and legal usefulness UNVERIFIED; test triage demand separately from permissions. |
| 3.4 Existing fence-line monitoring | A | Q8 adds "cost/performance vs incumbents UNVERIFIED". |
| 3.5 Manufactured clean readings | A | Q9 kept, plus "authenticated records don't prove honest exposure". |
| 3.6 What have you saved? | A | Q11: nothing measured; randomised on/off blocks, independent reference, metered water, suppression vs wetting the sensor. |
| 3.7 Evidence despite the restrictions | A | Q12 and slide 9 (see 2.9). |
| 3.8 Fog, outages, dust | A | Q13: non-condensing spec; fog performance, complete-system power and service intervals UNVERIFIED pending bench tests. |
| 4.1 Fill team fields | R | Deliberately left as ‹placeholders›: only the user can fill them (team not yet named). Listed under *Needs from user*. |
| 4.2–4.5 Slides 2–5 | A | Reworded as above; TERI's 314 ± 77 labelled "NCR sites, 2016-17 campaign". |
| 4.6 Solution arrives late | P | Forecasting moved to backup and slides 2–5 shortened: the solution now starts at 3:15 (was 3:50). Further compression would drop required context (problem, background). |
| 4.7 Move forecasting to backup | A | Now B1, with corrected claims (see sol 1). |
| 4.8 Fair comparator, threshold, coverage together | A | Slide 7 shows the 14-day reference baseline, 0.5 m/s, coverage and work-hour MAE together. |
| 4.9 Fine ratio; label power | A | See 2.2 and 2.10. |
| 4.10 Approval-dependent milestones | A | Slide 9 header "(approval-dependent)". |
| 4.11 Gaps are abstention, not zero | A | B2 notes and the demo legend. |
| 4.12 Bring built/simulated/planned forward | P | A status line is now on slide 1, and tags are on slide 6; the full table stays in backup B3 for time. |
| 4.13 Remove lower-bound claim | A | B4 rewritten. |
| 4.14 Explain truth and zero-scored abstentions | A | B5 caption. |
| 4.15 Missing essential parts | A | B6 total labelled "partial: not a build cost". |
| 4.16 Direct links; reporting vs orders | P | B8 now links the load-bearing sources and labels reporting; every source's URL is in `research/fact-check.md`. |
| 5.1 Memo arguments | A | "Most crowded" marked UNVERIFIED; demo scored on what exists; near-site value acknowledged as unsettled by city shares; T1 described with its commissioning needs (node, rain gauge, gateway), not "one node". |
| 6.1 Verdict: keep T1 | A | The memo recommends T1. |

## gpt-6-sol (max) — code, reproducibility, evaluation

| Finding | Decision | What changed / why |
|---|---|---|
| 1 (blocking) "ML adds at most 4 %" was an oracle with D+1 weather; literal bound false (4.398 %) | A | Every doc now says: without future weather the PM2.5 ML was −2.2 % to −1.3 % vs persistence; only the oracle gained 4.4 %. Figure relabelled "ORACLE"; CAMS labelled one grid point, uncontrolled vintage. New render keys (`fc_nofuture_*`, `fc_oracle_*`); the old key was removed. |
| 2 Retrospective ERA5 for day D; "two years"/"one year" wrong | P | Labelled "retrospective ERA5" and "data from Feb 2025" (B1, Q7). An as-of vintage cutoff / issued-forecast inputs are *deferred* (forecasting isn't the spike). |
| 3 Holdout not blind | A | Slide 7, B5, Q5, memo and ADR say "fresh seeds, not blind". A sealed holdout held by a separate reviewer is the plan for the next evaluation. |
| 4 All-hour MAE masks work hours (115.77) | A | New machine-written breakdown (`components/attribution/autoresearch/breakdown_v21.py` → `breakdown_v21.json`): work-hour MAE, coverage, POD/FAR, and MAE vs the identifiable contrast for all methods. **Result: self-calibration is no better than the stronger reference baseline in work hours (115.77 vs 115.05); its all-hour gain comes from quiet hours and fewer false alarms (FAR 0.145 vs 0.305).** Slide 7, Q5, memo and ADR now say this. The claim that self-calibration improves accuracy is withdrawn. |
| 5 Reference baseline too weak; 14-day median → 64.92 | A | `ring_refcal14` added to `methods.py`, reproduced at 64.92 and used as the comparator in every doc (self-calibration 57.43 vs 64.92 all hours). Logged as post-hoc in `results.tsv`. |
| 6 1 m/s / confused-wind abstention not implemented | A | Claims aligned with the code (0.5 m/s); swirling-wind gating listed as planned. |
| 7 check_docs can be fooled (₹999, substring binding); manual TSV | P | Binding now matches whole numeric tokens (the ₹500-vs-₹7,500 attack fails); ₹ amounts of any size are tokenised (the ₹999 attack is flagged); both negative tests were run. Attribution numbers now come from the machine-written `breakdown_v21.json`, and `results.tsv` is cross-checked against it. Typed value/unit claims: *deferred*. The docstring says check_docs is a binding/drift gate, not fact verification. |
| 8 Ingest can keep incomplete or mixed-unit data | A | `fetch_openaq_archive.py` now records failed listings, marks `complete=false` with a warning, and refuses mixed PM units. Existing data not re-fetched: the manifest shows one failed file for station 17, already disclosed. |
| 9 Undefined FAR printed as 0 | A | `forecast_eval.metrics` returns null for undefined POD/FAR/CSI; the walk-forward JSON was regenerated (MAE values unchanged; CAMS PM2.5 severe-day FAR is now null). |
