# POST-HOC — frozen overlap gate applied to the real OBD cases

Rule (from `eval/gate_rule.json`, calibrated on the simulator only at 2026-10-04 13:39:26 IST, commit b4e95ae): abstain if ESS/n < 0.05 or effective rewards < 0 or |mean-weight z| > 3.0. **Post hoc:** the OBD outcomes and ESS values below were seen before the gate was calibrated.

**Result:** 6 of 10 cases answered, 0 of them wrong. 3 of the 3 cases where DR's interval missed the truth were abstained on. Cost: 1 abstention(s) where DR would have been right.

| source | case | ESS/n | effective rewards | mean-weight z | gate | DR CI ∋ truth | verdict |
|---|---|---|---|---|---|---|---|
| pre-registered | Analysis 2 Random→V(BTS) P-static | 0.1619 | 435 | +2.1 | answer | yes | answered, correct |
| pre-registered | Analysis 2 Random→V(BTS) P-hourly | 0.1140 | 405 | +1.4 | answer | yes | answered, correct |
| pre-registered | halves · A deploy BTS | 0.0092 | 677 | -0.6 | ABSTAIN: ESS/n 0.0092 < 0.05 | yes | abstained (would have been right) |
| pre-registered | halves · B roll back | 0.1373 | 216 | -1.0 | answer | yes | answered, correct |
| deviation | 2019-11-24→2019-11-25 · A deploy BTS | 0.0005 | 504 | +4.6 | ABSTAIN: ESS/n 0.0005 < 0.05; |mean-weight z| 4.6 > 3.0 | NO | abstained (would have been wrong) |
| deviation | 2019-11-24→2019-11-25 · B roll back | 0.0985 | 93 | +2.7 | answer | yes | answered, correct |
| deviation | 2019-11-24→2019-11-26 · A deploy BTS | 0.0080 | 575 | -1.9 | ABSTAIN: ESS/n 0.0080 < 0.05 | NO | abstained (would have been wrong) |
| deviation | 2019-11-24→2019-11-26 · B roll back | 0.1427 | 125 | +0.0 | answer | yes | answered, correct |
| deviation | 2019-11-25→2019-11-26 · A deploy BTS | 0.0080 | 575 | -1.9 | ABSTAIN: ESS/n 0.0080 < 0.05 | NO | abstained (would have been wrong) |
| deviation | 2019-11-25→2019-11-26 · B roll back | 0.1427 | 125 | +0.0 | answer | yes | answered, correct |
