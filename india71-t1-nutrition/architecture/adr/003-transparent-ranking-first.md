# ADR 003: Spike B ships a transparent ranking rule; ML is gated on beating it

- **Status:** accepted, 4 Oct 2026 11:00 IST. Amends [ADR 001](001-spike.md) (spike B) and [ADR 002](002-measurement-diagnostics.md).
- **Trigger:** two independent cross-model reviews (GPT-6 Sol code review, GPT-6 Astra methodology review; [`reviews/`](../../reviews/)) found look-ahead (AWC credibility computed over the full history) and an oracle candidate pool in the v0 early-warning evaluator. We wrote a prediction-time-clean evaluator, [`eval_v1.py`](../../components/early_warning/eval_v1.py), with:
  - a no-look-ahead unit test;
  - an observable candidate pool;
  - observed-label training;
  - unique incident episodes;
  - a cluster bootstrap over AWCs.

## Result (SYNTHETIC, [`eval/results/early_warning_v1.json`](../../eval/results/early_warning_v1.json))
10,690 incident episodes on held-out seeds 23–24. Each method gets five list slots per AWC per month. An episode counts as caught if the child was listed 1–3 months before onset.

| Ranking | Episode recall | 95% CI (AWC bootstrap) |
|---|---|---|
| Random within AWC | 0.269 | |
| Programme rule: no weight gain in 2 months | 0.365 | |
| **Lowest current observed WHZ** | **0.429** | 0.420–0.443 |
| Logistic, anthropometry | 0.384 | 0.374–0.399 |
| Logistic + linked health events | 0.384 | 0.374–0.398 |

The model is significantly worse than the transparent rule: difference −0.054 to −0.037. Linked health events add nothing.

## Decision
1. **Spike B is the capacity-constrained worklist itself.** Each week every AWC gets K slots, filled by the *transparent rule*: children closest to the MAM line, with observed SAM/MAM going to the protocol pathway. It is explainable to an AWW in one sentence, and it beats the programme's no-gain rule (+6.4 pp) and random (+16 pp) in simulation.
2. **ML is gated.** Any model must beat the transparent rule prospectively, on real pilot data, under the frozen v1 protocol, before it replaces the rule. The auto-research loop for spike B now targets `eval_v1`, with the rule as the bar to beat.
3. **Health linkage is justified by care coordination, not prediction.** Sharing a SAM list with the ASHA/ANM within 2 days (CMAM 2023 p.20) and tracking appraisal are operational benefits. No predictive gain is claimed.

## Consequences
- Proposal v0.3 reports the rule-vs-model result honestly.
- The v0 evaluator and its numbers (0.33 vs 0.25) are retracted from all deliverables.
- The pipeline demo uses v1 features (no look-ahead) and the WHZ/MUAC/oedema classification for SAM/MAM routing.
