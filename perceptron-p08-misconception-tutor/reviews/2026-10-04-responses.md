# Lead responses to the 4 Oct cross-model reviews (PLAYBOOK §10)

Reviews:
- [gpt-6-sol — code and eval reproduction](2026-10-04-code-eval-gpt-6-sol.md)
- [gpt-6-astra — abstract, spike and memo](2026-10-04-abstract-spike-gpt-6-astra.md)

Feedback is advisory and the lead decides. Every item below is marked ACCEPTED or REJECTED, with the action taken. Fixes are on `main` together with this file. Reproduce them with:
- `python -m eval.analyze_gaps`
- `python -m eval.render_docs --check`
- `python -m eval.check_docs --selftest`

## gpt-6-sol (max) — 12 issues: 12 accepted (2 with stated limits), 0 rejected
Reproduction: every scored field matched the committed responses.

| # | Severity | Issue | Decision | Action |
|---|---|---|---|---|
| 1 | critical | H8 engine reads the generator's target code | **ACCEPTED (relabel)** | H8 relabelled as a construction-guaranteed accounting demonstration (result label, protocol clarification 5, abstract 'half explainable by design', c04). I did not re-implement the engine to infer the rule: each probability family has exactly one applicable rule, so inferring it from the family is equivalent. A non-generator-native workload is listed under Next. |
| 2 | critical | Cascade cost/latency use the wrong population | **ACCEPTED** | Costs are now summed over routed items; both result files were regenerated offline. Probability $7.32 → $5.08, real $6.50 → $6.10. The abstract and memo are re-rendered. |
| 3 | major | Displayed fraction brackets break FRAC_ADD under the engine parser | **ACCEPTED** | Added `parse_display` and round-trip tests over all 180 inversion and 300 bank items. All pass. The old parser differs on 26/180 (reproduced). Prompts unchanged. |
| 4 | major | Degenerate percentile CIs at 0/n and n/n | **ACCEPTED** | Exact Clopper–Pearson intervals in `eval/analyze_gaps.py`. Docs say '0 false claims (exact 95% upper bound 2.4%)'. |
| 5 | major | check_docs accepts a falsified number | **ACCEPTED** | Added: comparison against a fresh render of every artefact (the memo is now rendered into the thought node); a strict scan restricted to claim values; a committed-results check; and `--selftest`, which reproduces the reviewer's edit (CAUGHT). |
| 6 | major | Missing offline responses look like valid runs | **ACCEPTED** | Offline mode now raises on any missing response, in both runners. |
| 7 | major | Tracing composition ambiguity (SQ_DOUBLE + NEG_TIMES_NEG) | **ACCEPTED** | Post-hoc sensitivity excluding 7 learners: unchanged (tracer 64.5% vs GPT-5.4-mini 66.7%). Specifying precedence in the prompt is deferred to the next run. |
| 8 | minor | Retries not accounted; invalid non-empty replies not retried | **ACCEPTED** | Usage is now summed over attempts and requests counted; an optional `valid=` retry predicate was added. 14 retried items; unrecorded cost ≤ $0.51. |
| 9 | minor | Parser commits to the first evaluable segment | **ACCEPTED (documented)** | Limitation recorded (22 questions). The registered sample is unchanged; a parsing sensitivity analysis is listed under Next. |
| 10 | minor | Cache key omits endpoint/API version | **ACCEPTED** | Endpoint and API version are stored with each new cache record and checked on read. No secrets are stored. |
| 11 | minor | External inputs not pinned | **ACCEPTED** | Hugging Face revisions and SHA-256 hashes are pinned in `eval/data/fetch.py` and verified. |
| 12 | minor | Engine determinism asserted, not measured | **ACCEPTED** | Measured: 304/304 identical over two passes (`llm_gaps_posthoc.json`). The misleading field was replaced. |

## gpt-6-astra (max) — 23 issues: 23 accepted (2 partly), 0 rejected
Pre-revision score: 62/100, not shortlist-ready. The judge agreed that the abstract honestly reports the negative result.

| # | Severity | Issue | Decision | Action |
|---|---|---|---|---|
| 1 | major | Cost-halving headline wrong | **ACCEPTED** | As sol #2: $7.32 → $5.08; 'calls halve, routed answers cost more'. |
| 2 | major | Latency headline mixes tasks and statistics | **ACCEPTED** | Removed the cross-task comparison. Engine median reported separately (0.06 ms, 304 items); cascade mean latency kept in the results. |
| 3 | major | H8 is a construction check | **ACCEPTED** | As sol #1. |
| 4 | major | Zero observed errors promoted to safety | **ACCEPTED** | 'Safe' removed; exact upper bounds reported; follow-up/abstain path kept. |
| 5 | major | Non-detection ≠ equivalence | **ACCEPTED** | 'No pre-registered gap was detected' in the abstract, memo, landscape and ADR Revision 2. |
| 6 | major | Executable explanation ≠ proof of belief | **ACCEPTED** | 'Certificate' wording, plus a discriminating follow-up before labelling. |
| 7 | major | Evaluated classifier ≠ full fallback; tracer ignores the LLM diagnosis | **ACCEPTED** | The diagram marks built / benchmarked / planned. LLM→tracer integration is planned; out-of-pack labels go to the teacher view. |
| 8 | major | 'Guaranteed-correct' exceeds the verified contract | **ACCEPTED** | 'Guaranteed' removed. Claims scoped to arithmetic: SymPy keys and target firing, with discrimination when competitors are requested. The probability pack is labelled prototype / stretch and not SymPy-verified. |
| 9 | major | Post-hoc label lost for the real cascade | **ACCEPTED** | Labelled at the point of use. The diagram separates pre-registered, post-hoc and planned evaluation. |
| 10 | major | Item-level blindness overstated | **ACCEPTED** | Exposure statement appended (clarification 1). |
| 11 | major | Restricted, asymmetric support | **ACCEPTED** | 'Conditional benchmark' with denominators in the abstract and memo. |
| 12 | major | Item-level bootstrap; sparse HYB discordance | **ACCEPTED** | Question-clustered bootstrap (173 questions): decisions unchanged. HYB vs GPT-4.1-mini: exact sign test p = 0.125, flagged as not robust. |
| 13 | minor | Multiplicity unspecified | **ACCEPTED** | Primary family {H1, H2} × GPT-5.5; all others exploratory (clarification 2). |
| 14 | minor | Simulation headline hides the favourable assumption | **ACCEPTED** | The abstract now headlines the equal-rate setting (28.0% vs 58.4%, synthetic). 'Upper bound' → 'optimistic scenario'. |
| 15 | major | Pilot cannot isolate the differentiator | **ACCEPTED** | Pilot redesigned: randomised against a GPT-5.5 tutor with the same items, time and interface; primary outcome defined; stated as a pilot, not a powered trial. |
| 16 | minor | Probability-key number bound to the wrong metric | **ACCEPTED** | 'Key and misconception answer both exact' everywhere. Key-only 40.0% noted in components.md. |
| 17 | minor | L3 is not uniformly 7–8 operators | **ACCEPTED** | '4–8 operators', rendered from the results. |
| 18 | minor | Parser coverage presented as intrinsic | **ACCEPTED** | 'Our parser and key-agreement gate cover 29 of 131'. |
| 19 | minor | Differentiation needs a precise comparison | **ACCEPTED (partly)** | Framed as a bounded integration-and-evaluation contribution, with one falsifiable claim (vs a GPT-5.5 tutor). A capability table against prior art is deferred for word budget. |
| 20 | major | Team fit unfinished; scope too wide | **ACCEPTED (partly)** | MVP narrowed to the arithmetic pack. The placeholder now asks for owners per workstream. Names and skills cannot be invented and stay a Needs-from-user item. |
| 21 | minor | Spend excludes retries | **ACCEPTED** | As sol #8: retained-response $19.75 plus ≤ $0.51. |
| 22 | minor | Brier ≠ calibration | **ACCEPTED** | Clarification 4; ADR Revision 2 qualifies 'calibrated posteriors'. |
| 23 | minor | Conclusion-branch logic too strong | **ACCEPTED** | Clarification 3. |

## What changed in the headline claims
- **Cascade saving:** "halves the cost" ($7.32 → $3.66) was wrong. Calls halve on engine-native probability items, and cost falls $7.32 → $5.08. On real items (post hoc) it falls $6.50 → $6.10.
- **Reasoning models:** "Reasoning models match the engine on accuracy and safety" became "no pre-registered gap was detected against the reasoning models". GPT-5.5 had 0 false claims on 152 selected negatives (exact 95% upper bound 2.4%).
- **Engine output:** "proof" became "certificate", followed by a discriminating question before labelling the learner.
- **Scope:** the MVP is narrowed to the arithmetic pack. The pilot is redesigned as randomised against a GPT-5.5 tutor.
