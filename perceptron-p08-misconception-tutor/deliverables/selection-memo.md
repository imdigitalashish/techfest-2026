<!-- GENERATED from deliverables/templates/selection-memo.md by `python -m eval.render_docs`; edit the template, not this file. -->
_Final, 4 Oct 2026, after the pre-registered LLM-gap tests and two cross-model reviews ([responses](reviews/2026-10-04-responses.md)). Evidence: `eval/llm_gap_protocol.md`; results in `eval/results/`. Retained-response API spend was $19.75, plus at most $0.51 for discarded retry attempts. This section is rendered from `deliverables/templates/selection-memo.md`._
- **Verdict: against picking P8** as the team's one Perceptron problem, unless the user specifically wants Theme 5 *and* the team can run the pilot in November. This is a strategic judgement from the missing demonstrated differentiation; the H1–H7 results alone do not compel it (astra review).
- **Winnability: 2/5.** On real Eedi data the obvious baseline, a frontier LLM, showed no weakness that our engine fixes. GPT-5.5 diagnosed 79.4% of 131 positives with 0 false claims on 152 same-domain negatives (exact 95% upper bound 2.4%); our engine diagnosed 19.1%, also with 0. The astra judge scored the pre-revision abstract 62/100.
- **Innovation headroom: 2/5.**
  - Pre-registered gaps (H1–H7) were detected only against GPT-4.1-mini: false claims 15.8%, inversion 11.7%, probability answers 36.7%.
  - None was detected against the reasoning models: GPT-5.5 inversion 100.0%, probability answers 100.0%; tracer 64.0% vs GPT-5.4-mini 66.0%.
  - The cascade saves money only where the engine explains answers:
    - probability items: $7.32 → $5.08 per 1,000;
    - real Eedi items (post hoc): $6.50 → $6.10.
  - Executable misconceptions are prior art (MalruleLib, ACL 2026).
- **Feasibility: 5/5** for the arithmetic MVP: 12 components with contract tests, offline-reproducible results, CPU only.
- **Demo strength: 4/5.** An instant, deterministic certificate (median 0.06 ms), verified practice and a teacher view make a clear demo. The honest answer to "why not GPT-5.5?" weakens it.
- **Fit with the user's strengths: 3/5.** Evaluation rigour, LLM pipelines and Azure fit well; there is little large-scale-systems depth.
- **Biggest risk:** there is no accuracy edge. The one result judges would weigh heavily, learning gains against a GPT-5.5 tutor, needs a November pilot that overlaps the exams.
- **One-line pitch (if picked):** *Name the rule, check it, verify the practice — an exact-first cascade that answers what it can certify instantly and for free, and hands the rest to a frontier LLM.*
