# Held-out validation of the frozen overlap gate (SIMULATOR; pre-registered)

Pre-registration: [`../preregistration_gate_holdout.md`](../preregistration_gate_holdout.md). Reproduce: `nice -n 10 .venv/bin/python eval/validate_gate_holdout.py`.
192 configurations × 8 seeds on world seeds 101 and 202 (calibration used 7). Effects positive, near-null and harmful; 10 or 40 actions; 5,000 or 20,000 rows per period. References are Monte-Carlo population values (200,000 draws).

**Pooled:** the gate answers 53% of 1536 runs. Coverage among answered: 0.943; without the gate: 0.914. Confident wrong-sign answers: 0/818 answered vs 0/1536 ungated. Coverage on the abstained runs: 0.882. **Pre-registered criteria met: YES.**

| slice | runs | answer rate | coverage (answered) | coverage (ungated) | confident wrong (answered) | confident wrong (ungated) |
|---|---|---|---|---|---|---|
| effect = harmful | 512 | 52% | 0.958 | 0.914 | 0/264 | 0/512 |
| effect = near_null | 512 | 54% | 0.935 | 0.920 | 0/278 | 0/512 |
| effect = positive | 512 | 54% | 0.935 | 0.908 | 0/276 | 0/512 |
| rows per period = 5000 | 768 | 54% | 0.938 | 0.914 | 0/416 | 0/768 |
| rows per period = 20000 | 768 | 52% | 0.948 | 0.914 | 0/402 | 0/768 |
| actions = 10 | 768 | 57% | 0.935 | 0.922 | 0/434 | 0/768 |
| actions = 40 | 768 | 50% | 0.951 | 0.906 | 0/384 | 0/768 |
