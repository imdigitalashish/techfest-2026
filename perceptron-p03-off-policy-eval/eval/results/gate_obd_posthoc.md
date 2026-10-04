# POST-HOC — frozen overlap gate applied to the real OBD cases (endpoints separated per review A1/A6)

Rule (from `eval/gate_rule.json`, calibrated on the simulator only at 2026-10-04 13:39:26 IST, commit b4e95ae): abstain if ESS/n < 0.05 or effective rewards < 0 (inactive at 0) or |mean-weight z| > 3.0. **Post hoc and exploratory:** the gate's diagnostics, simulator knobs and selection criterion were chosen after the OBD failures below had been seen.

Three endpoints, never merged: **S1** = the pre-registered consistency test (CI of estimate − reference contains 0; a non-rejection, not proof of accuracy); **ref ∈ CI** = the reference point lies inside DR's own 95% interval; **confident wrong sign** = DR's interval excludes 0 on the opposite side of the reference.

**Listed rows (10):** answered 6 — S1 non-rejections 6/6, reference inside DR's CI 5/6, confident wrong sign 0/4 answered effect rows (n/a for value rows); abstained 4 (of which S1 rejected 3).
**Distinct evaluation instances (8; day pairs sharing an after-day counted once):** answered 5 — S1 5/5, ref ∈ CI 4/5, confident wrong sign 0/3 answered effect instances; abstained 3, covering 2 of the 2 S1 rejections. Instances still share observations.

| source | case | ESS/n | ESS (absolute) | mean-weight z | gate | S1 non-rejection | ref ∈ DR CI | confident wrong sign |
|---|---|---|---|---|---|---|---|---|
| pre-registered | Analysis 2 Random→V(BTS) P-static | 0.1619 | 106,990 | +2.1 | answer | yes | yes | n/a (value row) |
| pre-registered | Analysis 2 Random→V(BTS) P-hourly | 0.1140 | 75,315 | +1.4 | answer | yes | yes | n/a (value row) |
| pre-registered | halves · A deploy BTS | 0.0092 | 25,395 | -0.6 | ABSTAIN: ESS/n 0.0092 < 0.05 | yes | yes | no |
| pre-registered | halves · B roll back | 0.1373 | 42,386 | -1.0 | answer | yes | yes | no |
| deviation | 2019-11-24→2019-11-25 · A deploy BTS | 0.0005 | 799 | +4.6 | ABSTAIN: ESS/n 0.0005 < 0.05; |mean-weight z| 4.6 > 3.0 | NO | NO | no |
| deviation | 2019-11-24→2019-11-25 · B roll back | 0.0985 | 16,149 | +2.7 | answer | yes | NO | no |
| deviation | 2019-11-24→2019-11-26 · A deploy BTS | 0.0080 | 12,822 | -1.9 | ABSTAIN: ESS/n 0.0080 < 0.05 | NO | NO | no |
| deviation | 2019-11-24→2019-11-26 · B roll back | 0.1427 | 25,583 | +0.0 | answer | yes | yes | no |
| deviation | 2019-11-25→2019-11-26 · A deploy BTS | 0.0080 | 12,822 | -1.9 | ABSTAIN: ESS/n 0.0080 < 0.05 | NO | NO | no |
| deviation | 2019-11-25→2019-11-26 · B roll back | 0.1427 | 25,583 | +0.0 | answer | yes | yes | no |
