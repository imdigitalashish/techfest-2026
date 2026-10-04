# C9 Evaluator — component research

**Contract:** global adapter + eval blocks → `EvalReport` (per-domain loss, macro, worst). **Isolated metric:** determinism (identical re-run) and 95 % CI half-width across seeds.

- **Today:** next-token cross-entropy (nats/token) on 48 held-out 128-token blocks per domain; macro = mean over domains (each device's domain counts equally); worst domain; min relative gain vs base; evaluated every 3 rounds.
- **Gaps:** single seed so far (seed 1 queued); no centralised upper bound yet (pooled training at equal compute) — needed for the E1 "converges near centralised" claim; no downstream task accuracy yet (add classification accuracy on the finance task).
