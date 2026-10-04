# α-knob — results (REAL data; pre-registered)

Implements [`preregistration_knob.md`](../preregistration_knob.md) (commit `10209ca`, registered 2026-10-04 21:07:33 IST, before any knob computation). Reproduce: `python3 demo/knob.py` (numpy). Units: clicks per 1,000 impressions. Candidate π_α = (1 − α)·BTS + α·uniform. Reference = (1 − α)·CTR(BTS arm) + α·CTR(Random arm), same period: the **concurrent A/B reference**, not ground truth (arm-balance label artefact unresolved). Gate: frozen `eval/gate_rule.json` via `components/report/gate.py`.

**Integrity:** extract sha256 matches the manifest; reproduction checks 58/58 pass; closed forms vs gate.py/per-row arrays 12/12 series pass.

## Primary summary — IPW, row-level interval

Scan away from the logging policy (BTS logs: α from 0 up; Random logs: α from 1 down). 101 grid points per row. E1 = reference inside the 95% CI. *Answered miss* = gate answers and E1 fails; *unnecessary abstention* = gate abstains and E1 holds.

| period | logs | gate first abstains at α | E1 first fails at α | answered ✓ | answered miss | unnecessary abstention | justified abstention | largest answered miss (per 1,000) |
|---|---|---|---|---|---|---|---|---|
| W · all 84 h (pre-registered window) | BTS (exact) | 0.01 | never | 1 | 0 | 100 | 0 | 0.000 |
| W · all 84 h (pre-registered window) | Random (approx. target) | never | never | 101 | 0 | 0 | 0 | 0.000 |
| W1 · first half (pre-registered) | BTS (exact) | 0.01 | never | 1 | 0 | 100 | 0 | 0.000 |
| W1 · first half (pre-registered) | Random (approx. target) | never | never | 101 | 0 | 0 | 0 | 0.000 |
| W2 · second half (pre-registered) | BTS (exact) | 0.43 | never | 43 | 0 | 58 | 0 | 0.000 |
| W2 · second half (pre-registered) | Random (approx. target) | never | never | 101 | 0 | 0 | 0 | 0.000 |
| Nov 24 · whole UTC day | BTS (exact) | 0.01 | never | 1 | 0 | 100 | 0 | 0.000 |
| Nov 24 · whole UTC day | Random (approx. target) | never | never | 101 | 0 | 0 | 0 | 0.000 |
| Nov 25 · whole UTC day | BTS (exact) | 0.01 | 0.46 | 1 | 0 | 45 | 55 | 0.000 |
| Nov 25 · whole UTC day | Random (approx. target) | never | never | 101 | 0 | 0 | 0 | 0.000 |
| Nov 26 · whole UTC day | BTS (exact) | 0.40 | 0.28 | 28 | 12 | 0 | 61 | 0.036 |
| Nov 26 · whole UTC day | Random (approx. target) | never | never | 101 | 0 | 0 | 0 | 0.000 |

Totals over 12 series × 101 points: answered ✓ 681, answered miss 12, unnecessary abstention 403, justified abstention 116.

## Secondary summaries — every estimator, endpoint and interval

Format: answered ✓ / answered miss / unnecessary abstention / justified abstention (first failing α).

| period | logs | IPW E1 row | IPW E1 hour-cluster | IPW E2 row | IPW E2 hour-cluster | SNIPW E1 row | SNIPW E1 hour-cluster | SNIPW E2 row | SNIPW E2 hour-cluster |
|---|---|---|---|---|---|---|---|---|---|
| W | SB | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/11/89 (0.12) | 1/0/100/0 (–) | 1/0/0/100 (0.01) | 1/0/100/0 (–) |
| W | SR | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) |
| W1 | SB | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/9/91 (0.10) | 1/0/100/0 (–) | 1/0/0/100 (0.01) | 1/0/100/0 (–) |
| W1 | SR | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) |
| W2 | SB | 43/0/58/0 (–) | 43/0/58/0 (–) | 43/0/58/0 (–) | 43/0/58/0 (–) | 43/0/58/0 (–) | 43/0/58/0 (–) | 43/0/58/0 (–) | 43/0/58/0 (–) |
| W2 | SR | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) |
| D24 | SB | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) |
| D24 | SR | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) |
| D25 | SB | 1/0/45/55 (0.46) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/100/0 (–) | 1/0/9/91 (0.10) | 1/0/100/0 (–) | 1/0/0/100 (0.01) | 1/0/100/0 (–) |
| D25 | SR | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 77/24/0/0 (0.23) | 101/0/0/0 (–) | 1/100/0/0 (0.99) | 101/0/0/0 (–) |
| D26 | SB | 28/12/0/61 (0.28) | 40/0/32/29 (0.72) | 1/39/0/61 (0.01) | 1/39/0/61 (0.01) | 37/3/0/61 (0.37) | 40/0/52/9 (0.92) | 40/0/61/0 (–) | 40/0/61/0 (–) |
| D26 | SR | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) | 101/0/0/0 (–) |

## Pre-registered predictions vs results

| series | item | predicted | result | grade |
|---|---|---|---|---|
| W2·SB | gate | first abstain 0.43 | first abstain 0.43 | hit |
| W2·SB | E1_IPW | holds at every alpha | holds at every alpha | hit |
| W2·SB | E2_IPW | holds at every alpha | holds at every alpha | hit |
| D26·SB | gate | first abstain 0.40 | first abstain 0.40 | hit |
| D26·SB | E1_IPW | fails from 0.28 | fails from 0.28 | hit |
| D26·SB | E2_IPW | fails at every alpha except the logging end | fails at every alpha except the logging end | hit |
| D25·SB | gate | abstain at every alpha except the logging end | True | hit |
| D25·SB | E1_IPW | fails from 0.43 | fails from 0.46 | miss |
| D25·SB | E2_IPW | holds at every alpha | holds at every alpha | hit |
| W1·SB | gate | abstain at every alpha except the logging end | True | hit |
| W1·SB | E1_IPW | holds at every alpha | holds at every alpha | hit |
| W1·SB | E2_IPW | holds at every alpha | holds at every alpha | hit |
| D24·SB | gate | first abstain 0.12 if abs(z) <= 3 | first abstain 0.01 | miss (condition abs(z) <= 3 NOT met: far-end z +4.52) |
| D24·SB | E1_IPW | holds at every alpha | holds at every alpha | hit |
| D24·SB | E2_IPW | holds at every alpha | holds at every alpha | hit |
| W·SB | all | not predicted | first abstain 0.01 | n/a |
| W·SR | gate | never | never | hit |
| W·SR | E1_IPW | holds at every alpha | holds at every alpha | hit |
| W·SR | E2_IPW | holds at every alpha | holds at every alpha | hit |
| W2·SR | gate | never | never | hit |
| W2·SR | E1_IPW | holds at every alpha | holds at every alpha | hit |
| W2·SR | E2_IPW | holds at every alpha | holds at every alpha | hit |
| D26·SR | gate | never | never | hit |
| D26·SR | E1_IPW | holds at every alpha | holds at every alpha | hit |
| D26·SR | E2_IPW | holds at every alpha | holds at every alpha | hit |
| D25·SR | gate | never | never | hit |
| D25·SR | E1_IPW | holds at every alpha | holds at every alpha | hit |
| D25·SR | E2_IPW | holds at every alpha | holds at every alpha | hit |
| W1·SR | gate | never | never | hit |
| W1·SR | E1_IPW | holds at every alpha | holds at every alpha | hit |
| W1·SR | E2_IPW | holds at every alpha | holds at every alpha | hit |
| D24·SR | gate | never | never | hit |
| D24·SR | E1_IPW | holds at every alpha | holds at every alpha | hit |
| D24·SR | E2_IPW | holds at every alpha | holds at every alpha | hit |

**P1 (logging end exact) and P2 (algebra):**

| series | P1 | IPW gap linear in λ | abs(z) constant for λ > 0 | IPW E2 constant | IPW E1 crosses at most once |
|---|---|---|---|---|---|
| W·SB | yes | yes | yes | yes | yes |
| W·SR | yes | yes | yes | yes | yes |
| W1·SB | yes | yes | yes | yes | yes |
| W1·SR | yes | yes | yes | yes | yes |
| W2·SB | yes | yes | yes | yes | yes |
| W2·SR | yes | yes | yes | yes | yes |
| D24·SB | yes | yes | yes | yes | yes |
| D24·SR | yes | yes | yes | yes | yes |
| D25·SB | yes | yes | yes | yes | yes |
| D25·SR | yes | yes | yes | yes | yes |
| D26·SB | yes | yes | yes | yes | yes |
| D26·SR | yes | yes | yes | yes | yes |

## Key grid points

Value ± 95% half-width (row-level), per 1,000. Gate: ✓ answer, ✗ can't tell (reason).

| period | logs | α | reference | IPW | SNIPW | ESS/n | effective rows | mean-weight z | gate |
|---|---|---|---|---|---|---|---|---|---|
| W | SB | 0.00 | 4.890 ± 0.056 | 4.890 ± 0.056 | 4.890 ± 0.056 | 1.0000 | 5,956,296 | +0.00 | ✓ |
| W | SB | 0.25 | 4.528 ± 0.055 | 4.493 ± 0.083 | 4.399 ± 0.086 (ref outside) | 0.0126 | 75,146 | +5.81 | ✗ ESS/n 0.0126 < 0.05; \|mean-weight z\| 5.8 > 3.0 |
| W | SB | 0.50 | 4.166 ± 0.076 | 4.097 ± 0.137 | 3.928 ± 0.142 (ref outside) | 0.0033 | 19,771 | +5.81 | ✗ ESS/n 0.0033 < 0.05; \|mean-weight z\| 5.8 > 3.0 |
| W | SB | 0.75 | 3.804 ± 0.107 | 3.700 ± 0.198 | 3.475 ± 0.199 (ref outside) | 0.0015 | 9,170 | +5.81 | ✗ ESS/n 0.0015 < 0.05; \|mean-weight z\| 5.8 > 3.0 |
| W | SB | 1.00 | 3.442 ± 0.141 | 3.303 ± 0.261 | 3.041 ± 0.253 (ref outside) | 0.0009 | 5,372 | +5.81 | ✗ ESS/n 0.0009 < 0.05; \|mean-weight z\| 5.8 > 3.0 |
| W | SR | 0.00 | 4.890 ± 0.056 | 4.969 ± 0.484 | 4.946 ± 0.481 | 0.1140 | 75,315 | +1.37 | ✓ |
| W | SR | 0.25 | 4.528 ± 0.055 | 4.587 ± 0.379 | 4.571 ± 0.377 | 0.1857 | 122,757 | +1.37 | ✓ |
| W | SR | 0.50 | 4.166 ± 0.076 | 4.206 ± 0.279 | 4.196 ± 0.278 | 0.3386 | 223,811 | +1.37 | ✓ |
| W | SR | 0.75 | 3.804 ± 0.107 | 3.824 ± 0.191 | 3.819 ± 0.191 | 0.6714 | 443,741 | +1.37 | ✓ |
| W | SR | 1.00 | 3.442 ± 0.141 | 3.442 ± 0.141 | 3.442 ± 0.141 | 1.0000 | 660,904 | +0.00 | ✓ |
| W1 | SB | 0.00 | 4.889 ± 0.077 | 4.889 ± 0.077 | 4.889 ± 0.077 | 1.0000 | 3,186,871 | +0.00 | ✓ |
| W1 | SB | 0.25 | 4.485 ± 0.074 | 4.449 ± 0.128 | 4.274 ± 0.134 (ref outside) | 0.0073 | 23,354 | +6.05 | ✗ ESS/n 0.0073 < 0.05; \|mean-weight z\| 6.1 > 3.0 |
| W1 | SB | 0.50 | 4.081 ± 0.102 | 4.009 ± 0.223 | 3.705 ± 0.225 (ref outside) | 0.0020 | 6,342 | +6.05 | ✗ ESS/n 0.0020 < 0.05; \|mean-weight z\| 6.1 > 3.0 |
| W1 | SB | 0.75 | 3.677 ± 0.143 | 3.569 ± 0.326 | 3.178 ± 0.310 (ref outside) | 0.0010 | 3,040 | +6.05 | ✗ ESS/n 0.0010 < 0.05; \|mean-weight z\| 6.1 > 3.0 |
| W1 | SB | 1.00 | 3.273 ± 0.189 | 3.129 ± 0.431 | 2.688 ± 0.389 (ref outside) | 0.0006 | 1,838 | +6.05 | ✗ ESS/n 0.0006 < 0.05; \|mean-weight z\| 6.1 > 3.0 |
| W1 | SR | 0.00 | 4.889 ± 0.077 | 4.650 ± 0.660 | 4.591 ± 0.651 | 0.0996 | 35,093 | +2.48 | ✓ |
| W1 | SR | 0.25 | 4.485 ± 0.074 | 4.305 ± 0.516 | 4.265 ± 0.511 | 0.1635 | 57,597 | +2.48 | ✓ |
| W1 | SR | 0.50 | 4.081 ± 0.102 | 3.961 ± 0.378 | 3.936 ± 0.375 | 0.3041 | 107,132 | +2.48 | ✓ |
| W1 | SR | 0.75 | 3.677 ± 0.143 | 3.617 ± 0.257 | 3.605 ± 0.256 | 0.6346 | 223,576 | +2.48 | ✓ |
| W1 | SR | 1.00 | 3.273 ± 0.189 | 3.273 ± 0.189 | 3.273 ± 0.189 | 1.0000 | 352,299 | +0.00 | ✓ |
| W2 | SB | 0.00 | 4.892 ± 0.082 | 4.892 ± 0.082 | 4.892 ± 0.082 | 1.0000 | 2,769,425 | +0.00 | ✓ |
| W2 | SB | 0.25 | 4.578 ± 0.081 | 4.545 ± 0.100 | 4.549 ± 0.101 | 0.1296 | 359,000 | -0.62 | ✓ |
| W2 | SB | 0.50 | 4.264 ± 0.114 | 4.197 ± 0.147 | 4.206 ± 0.149 | 0.0358 | 99,231 | -0.62 | ✗ ESS/n 0.0358 < 0.05 |
| W2 | SB | 0.75 | 3.950 ± 0.161 | 3.850 ± 0.204 | 3.862 ± 0.206 | 0.0162 | 44,913 | -0.62 | ✗ ESS/n 0.0162 < 0.05 |
| W2 | SB | 1.00 | 3.636 ± 0.212 | 3.503 ± 0.264 | 3.517 ± 0.268 | 0.0092 | 25,395 | -0.62 | ✗ ESS/n 0.0092 < 0.05 |
| W2 | SR | 0.00 | 4.892 ± 0.082 | 5.334 ± 0.711 | 5.357 ± 0.713 | 0.1373 | 42,386 | -0.99 | ✓ |
| W2 | SR | 0.25 | 4.578 ± 0.081 | 4.909 ± 0.559 | 4.925 ± 0.559 | 0.2210 | 68,199 | -0.99 | ✓ |
| W2 | SR | 0.50 | 4.264 ± 0.114 | 4.485 ± 0.413 | 4.495 ± 0.413 | 0.3901 | 120,397 | -0.99 | ✓ |
| W2 | SR | 0.75 | 3.950 ± 0.161 | 4.060 ± 0.286 | 4.065 ± 0.286 | 0.7195 | 222,027 | -0.99 | ✓ |
| W2 | SR | 1.00 | 3.636 ± 0.212 | 3.636 ± 0.212 | 3.636 ± 0.212 | 1.0000 | 308,605 | +0.00 | ✓ |
| D24 | SB | 0.00 | 4.813 ± 0.099 | 4.813 ± 0.099 | 4.813 ± 0.099 | 1.0000 | 1,871,061 | +0.00 | ✓ |
| D24 | SB | 0.25 | 4.457 ± 0.097 | 4.444 ± 0.199 | 4.288 ± 0.202 | 0.0087 | 16,322 | +4.52 | ✗ ESS/n 0.0087 < 0.05; \|mean-weight z\| 4.5 > 3.0 |
| D24 | SB | 0.50 | 4.100 ± 0.135 | 4.076 ± 0.362 | 3.798 ± 0.355 | 0.0024 | 4,401 | +4.52 | ✗ ESS/n 0.0024 < 0.05; \|mean-weight z\| 4.5 > 3.0 |
| D24 | SB | 0.75 | 3.744 ± 0.190 | 3.707 ± 0.534 | 3.341 ± 0.501 | 0.0011 | 2,094 | +4.52 | ✗ ESS/n 0.0011 < 0.05; \|mean-weight z\| 4.5 > 3.0 |
| D24 | SB | 1.00 | 3.388 ± 0.251 | 3.339 ± 0.708 | 2.913 ± 0.637 | 0.0007 | 1,257 | +4.52 | ✗ ESS/n 0.0007 < 0.05; \|mean-weight z\| 4.5 > 3.0 |
| D24 | SR | 0.00 | 4.813 ± 0.099 | 5.055 ± 0.924 | 5.057 ± 0.923 | 0.1046 | 21,618 | -0.07 | ✓ |
| D24 | SR | 0.25 | 4.457 ± 0.097 | 4.638 ± 0.721 | 4.640 ± 0.720 | 0.1720 | 35,546 | -0.07 | ✓ |
| D24 | SR | 0.50 | 4.100 ± 0.135 | 4.221 ± 0.526 | 4.222 ± 0.525 | 0.3186 | 65,834 | -0.07 | ✓ |
| D24 | SR | 0.75 | 3.744 ± 0.190 | 3.805 ± 0.352 | 3.805 ± 0.352 | 0.6517 | 134,649 | -0.07 | ✓ |
| D24 | SR | 1.00 | 3.388 ± 0.251 | 3.388 ± 0.251 | 3.388 ± 0.251 | 1.0000 | 206,619 | +0.00 | ✓ |
| D25 | SB | 0.00 | 4.931 ± 0.113 | 4.931 ± 0.113 | 4.931 ± 0.113 | 1.0000 | 1,479,442 | +0.00 | ✓ |
| D25 | SB | 0.25 | 4.503 ± 0.109 | 4.424 ± 0.118 | 4.219 ± 0.140 (ref outside) | 0.0066 | 9,785 | +4.61 | ✗ ESS/n 0.0066 < 0.05; \|mean-weight z\| 4.6 > 3.0 |
| D25 | SB | 0.50 | 4.075 ± 0.148 | 3.917 ± 0.152 (ref outside) | 3.570 ± 0.193 (ref outside) | 0.0018 | 2,691 | +4.61 | ✗ ESS/n 0.0018 < 0.05; \|mean-weight z\| 4.6 > 3.0 |
| D25 | SB | 0.75 | 3.648 ± 0.208 | 3.410 ± 0.199 (ref outside) | 2.976 ± 0.237 (ref outside) | 0.0009 | 1,306 | +4.61 | ✗ ESS/n 0.0009 < 0.05; \|mean-weight z\| 4.6 > 3.0 |
| D25 | SB | 1.00 | 3.220 ± 0.274 | 2.903 ± 0.253 (ref outside) | 2.430 ± 0.271 (ref outside) | 0.0005 | 799 | +4.61 | ✗ ESS/n 0.0005 < 0.05; \|mean-weight z\| 4.6 > 3.0 |
| D25 | SR | 0.00 | 4.931 ± 0.113 | 4.146 ± 0.842 | 4.061 ± 0.824 (ref outside) | 0.0985 | 16,149 | +2.73 | ✓ |
| D25 | SR | 0.25 | 4.503 ± 0.109 | 3.914 ± 0.663 | 3.854 ± 0.652 | 0.1612 | 26,439 | +2.73 | ✓ |
| D25 | SR | 0.50 | 4.075 ± 0.148 | 3.683 ± 0.494 | 3.645 ± 0.489 | 0.2997 | 49,154 | +2.73 | ✓ |
| D25 | SR | 0.75 | 3.648 ± 0.208 | 3.451 ± 0.351 | 3.433 ± 0.349 | 0.6289 | 103,130 | +2.73 | ✓ |
| D25 | SR | 1.00 | 3.220 ± 0.274 | 3.220 ± 0.274 | 3.220 ± 0.274 | 1.0000 | 163,989 | +0.00 | ✓ |
| D26 | SB | 0.00 | 4.879 ± 0.108 | 4.879 ± 0.108 | 4.879 ± 0.108 | 1.0000 | 1,611,904 | +0.00 | ✓ |
| D26 | SB | 0.25 | 4.613 ± 0.108 | 4.501 ± 0.119 | 4.519 ± 0.121 | 0.1162 | 187,381 | -1.91 | ✓ |
| D26 | SB | 0.50 | 4.347 ± 0.152 | 4.122 ± 0.161 (ref outside) | 4.156 ± 0.165 (ref outside) | 0.0316 | 50,909 | -1.91 | ✗ ESS/n 0.0316 < 0.05 |
| D26 | SB | 0.75 | 4.081 ± 0.216 | 3.743 ± 0.215 (ref outside) | 3.790 ± 0.223 (ref outside) | 0.0142 | 22,842 | -1.91 | ✗ ESS/n 0.0142 < 0.05 |
| D26 | SB | 1.00 | 3.815 ± 0.285 | 3.364 ± 0.275 (ref outside) | 3.421 ± 0.285 (ref outside) | 0.0080 | 12,822 | -1.91 | ✗ ESS/n 0.0080 < 0.05 |
| D26 | SR | 0.00 | 4.879 ± 0.108 | 5.626 ± 0.987 | 5.626 ± 0.984 | 0.1427 | 25,583 | +0.01 | ✓ |
| D26 | SR | 0.25 | 4.613 ± 0.108 | 5.173 ± 0.773 | 5.173 ± 0.771 | 0.2283 | 40,938 | +0.01 | ✓ |
| D26 | SR | 0.50 | 4.347 ± 0.152 | 4.721 ± 0.569 | 4.721 ± 0.568 | 0.3997 | 71,657 | +0.01 | ✓ |
| D26 | SR | 0.75 | 4.081 ± 0.216 | 4.268 ± 0.389 | 4.268 ± 0.389 | 0.7270 | 130,343 | +0.01 | ✓ |
| D26 | SR | 1.00 | 3.815 ± 0.285 | 3.815 ± 0.285 | 3.815 ± 0.285 | 1.0000 | 179,290 | +0.00 | ✓ |

## Reproduction checks (far-end cells and CTRs vs committed results)

| check | ours | committed | tolerance | ok | source |
|---|---|---|---|---|---|
| W2 SB far-end IPW value | 0.0035032508736352217 | 0.0035032508736352217 | 1e-09 | yes | obd_slice.json a3_halves.A_deploy_BTS IPW.policy_effect_after |
| W2 SB far-end SNIPW value | 0.003516804916224394 | 0.003516804916224394 | 1e-09 | yes | obd_slice.json a3_halves.A_deploy_BTS SNIPW.policy_effect_after |
| W2 SB far-end ESS/n | 0.009169883097078436 | 0.009169883097078432 | 1e-06 | yes | gate_obd_posthoc.json 'halves · A deploy BTS' ess_frac |
| W2 SB far-end mean-weight z | -0.6194048945772128 | -0.6194048945772127 | 1e-06 | yes | gate_obd_posthoc.json 'halves · A deploy BTS' z_mean_w |
| W2 SB far-end ESS | 25395.303496126446 | 25395.30349612644 | 1e-09 | yes | obd_slice.json a3_halves.A_deploy_BTS ess |
| D26 SB far-end IPW value | 0.0033644812338654052 | 0.0033644812338654057 | 1e-09 | yes | obd_slice.json a3_daypairs[25→26].A_deploy_BTS IPW.policy_effect_after |
| D26 SB far-end SNIPW value | 0.0034209136376081198 | 0.00342091363760812 | 1e-09 | yes | obd_slice.json a3_daypairs[25→26].A_deploy_BTS SNIPW.policy_effect_after |
| D26 SB far-end ESS/n | 0.007954431024379049 | 0.007954431024379049 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-25→2019-11-26 · A deploy BTS' ess_frac |
| D26 SB far-end mean-weight z | -1.9068592606316892 | -1.9068592606316892 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-25→2019-11-26 · A deploy BTS' z_mean_w |
| D26 SB far-end ESS | 12821.779185920686 | 12821.779185920686 | 1e-09 | yes | obd_slice.json a3_daypairs[25→26].A_deploy_BTS ess |
| D25 SB far-end IPW value | 0.0029033900418469222 | 0.002903390041846922 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS IPW.policy_effect_after |
| D25 SB far-end SNIPW value | 0.0024302953958427985 | 0.0024302953958427985 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS SNIPW.policy_effect_after |
| D25 SB far-end ESS/n | 0.0005397670823623598 | 0.0005397670823623599 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-24→2019-11-25 · A deploy BTS' ess_frac |
| D25 SB far-end mean-weight z | 4.605872522344606 | 4.605872522344607 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-24→2019-11-25 · A deploy BTS' z_mean_w |
| D25 SB far-end ESS | 798.5540918643343 | 798.5540918643346 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS ess |
| W1 SB far-end IPW value | 0.0031290264698616253 | 0.0031290264698616258 | 1e-09 | yes | obd_slice.json a3_halves.B_rollback_to_Random IPW: B1 + policy_effect_after − interaction |
| W1 SB far-end SNIPW value | 0.0026875243434353628 | 0.0026875243434353636 | 1e-09 | yes | obd_slice.json a3_halves.B_rollback_to_Random SNIPW: B1 + policy_effect_after − interaction |
| W1 SB far-end ESS | 1837.964854307708 | 1837.9648543077074 | 1e-09 | yes | obd_slice.json a3_halves.B_rollback_to_Random ess_before |
| D24 SB far-end IPW value | 0.003338746178882766 | 0.0033387461788827654 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random IPW: B1 + policy_effect_after − interaction |
| D24 SB far-end SNIPW value | 0.0029129350635344995 | 0.0029129350635344995 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random SNIPW: B1 + policy_effect_after − interaction |
| D24 SB far-end ESS | 1257.4290817882127 | 1257.4290817882127 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random ess_before |
| W SR far-end IPW value | 0.004968912709302178 | 0.004968912709302178 | 1e-09 | yes | obd_slice.json a2.P-hourly.IPW.value |
| W SR far-end SNIPW value | 0.004945554663700643 | 0.004945554663700643 | 1e-09 | yes | obd_slice.json a2.P-hourly.SNIPW.value |
| W SR far-end ESS | 75315.42278517666 | 75315.42278517668 | 1e-09 | yes | obd_slice.json a2.P-hourly.ess |
| W SR far-end mean-weight z | 1.3705335050597183 | 1.3705335050597183 | 1e-06 | yes | gate_obd_posthoc.json 'Analysis 2 Random→V(BTS) P-hourly' z_mean_w |
| W2 SR far-end IPW value | 0.005333542746240975 | 0.005333542746240975 | 1e-09 | yes | obd_slice.json a3_halves.B_rollback_to_Random IPW.policy_effect_after |
| W2 SR far-end SNIPW value | 0.005357248443277285 | 0.005357248443277284 | 1e-09 | yes | obd_slice.json a3_halves.B_rollback_to_Random SNIPW.policy_effect_after |
| W2 SR far-end ESS/n | 0.137348139677488 | 0.137348139677488 | 1e-06 | yes | gate_obd_posthoc.json 'halves · B roll back' ess_frac |
| W2 SR far-end mean-weight z | -0.9852157231444244 | -0.9852157231444242 | 1e-06 | yes | gate_obd_posthoc.json 'halves · B roll back' z_mean_w |
| W2 SR far-end ESS | 42386.32264517118 | 42386.32264517119 | 1e-09 | yes | obd_slice.json a3_halves.B_rollback_to_Random ess |
| D26 SR far-end IPW value | 0.005626249034561627 | 0.005626249034561627 | 1e-09 | yes | obd_slice.json a3_daypairs[25→26].B_rollback_to_Random IPW.policy_effect_after |
| D26 SR far-end SNIPW value | 0.00562607808289972 | 0.005626078082899719 | 1e-09 | yes | obd_slice.json a3_daypairs[25→26].B_rollback_to_Random SNIPW.policy_effect_after |
| D26 SR far-end ESS/n | 0.14269235181108728 | 0.14269235181108728 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-25→2019-11-26 · B roll back' ess_frac |
| D26 SR far-end mean-weight z | 0.005248838340118656 | 0.005248838340118656 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-25→2019-11-26 · B roll back' z_mean_w |
| D26 SR far-end ESS | 25583.311756209838 | 25583.311756209838 | 1e-09 | yes | obd_slice.json a3_daypairs[25→26].B_rollback_to_Random ess |
| D25 SR far-end IPW value | 0.004145569831865755 | 0.004145569831865755 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random IPW.policy_effect_after |
| D25 SR far-end SNIPW value | 0.004060888829800764 | 0.004060888829800764 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random SNIPW.policy_effect_after |
| D25 SR far-end ESS/n | 0.09847479536787712 | 0.09847479536787712 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-24→2019-11-25 · B roll back' ess_frac |
| D25 SR far-end mean-weight z | 2.733892256628135 | 2.7338922566281356 | 1e-06 | yes | gate_obd_posthoc.json '2019-11-24→2019-11-25 · B roll back' z_mean_w |
| D25 SR far-end ESS | 16148.7832175828 | 16148.7832175828 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].B_rollback_to_Random ess |
| W1 SR far-end IPW value | 0.00464950603329828 | 0.00464950603329828 | 1e-09 | yes | obd_slice.json a3_halves.A_deploy_BTS IPW: R1 + policy_effect_after − interaction |
| W1 SR far-end SNIPW value | 0.004591032495395186 | 0.004591032495395186 | 1e-09 | yes | obd_slice.json a3_halves.A_deploy_BTS SNIPW: R1 + policy_effect_after − interaction |
| W1 SR far-end ESS | 35092.9621969546 | 35092.9621969546 | 1e-09 | yes | obd_slice.json a3_halves.A_deploy_BTS ess_before |
| D24 SR far-end IPW value | 0.005054724024291904 | 0.005054724024291904 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS IPW: R1 + policy_effect_after − interaction |
| D24 SR far-end SNIPW value | 0.0050570718871911086 | 0.0050570718871911086 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS SNIPW: R1 + policy_effect_after − interaction |
| D24 SR far-end ESS | 21617.60067801292 | 21617.60067801292 | 1e-09 | yes | obd_slice_deviation_floor.json a3_daypairs[24→25].A_deploy_BTS ess_before |
| W2 BTS-arm CTR | 0.0048916291287902725 | 0.0048916291287902725 | 1e-12 | yes | a3_halves.cells.B2.v |
| W2 Random-arm CTR | 0.003635715558723935 | 0.003635715558723935 | 1e-12 | yes | a3_halves.cells.R2.v |
| W1 BTS-arm CTR | 0.00488912164941725 | 0.00488912164941725 | 1e-12 | yes | a3_halves.cells.B1.v |
| W1 Random-arm CTR | 0.003272788171411216 | 0.003272788171411216 | 1e-12 | yes | a3_halves.cells.R1.v |
| D26 BTS-arm CTR | 0.0048793228380846505 | 0.0048793228380846505 | 1e-12 | yes | a3_daypairs[25→26].cells.B2.v |
| D26 Random-arm CTR | 0.0038150482458586647 | 0.0038150482458586647 | 1e-12 | yes | a3_daypairs[25→26].cells.R2.v |
| D25 BTS-arm CTR | 0.004930913141576351 | 0.004930913141576351 | 1e-12 | yes | a3_daypairs[25→26].cells.B1.v |
| D25 Random-arm CTR | 0.0032197281524980336 | 0.0032197281524980336 | 1e-12 | yes | a3_daypairs[25→26].cells.R1.v |
| D24 BTS-arm CTR | 0.004812777349322122 | 0.004812777349322122 | 1e-12 | yes | deviation a3_daypairs[24→25].cells.B1.v |
| D24 Random-arm CTR | 0.0033878781719009383 | 0.0033878781719009383 | 1e-12 | yes | deviation a3_daypairs[24→25].cells.R1.v |
| W BTS-arm CTR | 0.0048902875209694075 | 0.0048902875209694075 | 1e-12 | yes | obd_slice.json a2.truth |
| W Random-arm CTR | 0.0034422548509314517 | 0.0034422548509314517 | 1e-12 | yes | obd_slice.json a2.random_ctr |

**Committed far-end S1 intervals (500-draw bootstrap SE) next to ours (analytic SE)** — same quantity, (estimate − reference) in committed sign convention, per 1,000:

| series | estimator | committed CI | committed S1 | our CI | our E2 |
|---|---|---|---|---|---|
| W2·SB | IPW | [-0.216, 0.481] | yes | [-0.206, 0.471] | yes |
| W2·SB | SNIPW | [-0.234, 0.472] | yes | [-0.223, 0.460] | yes |
| D26·SB | IPW | [0.050, 0.851] | NO | [0.054, 0.847] | NO |
| D26·SB | SNIPW | [-0.012, 0.801] | yes | [-0.009, 0.797] | yes |
| D25·SB | IPW | [-0.048, 0.680] | yes | [-0.057, 0.690] | yes |
| D25·SB | SNIPW | [0.413, 1.166] | NO | [0.404, 1.175] | NO |
| W2·SR | IPW | [-1.172, 0.289] | yes | [-1.158, 0.274] | yes |
| W2·SR | SNIPW | [-1.200, 0.269] | yes | [-1.183, 0.252] | yes |
| D26·SR | IPW | [-1.749, 0.256] | yes | [-1.739, 0.246] | yes |
| D26·SR | SNIPW | [-1.747, 0.253] | yes | [-1.736, 0.243] | yes |
| D25·SR | IPW | [-0.090, 1.661] | yes | [-0.064, 1.635] | yes |
| D25·SR | SNIPW | [0.012, 1.728] | NO | [0.039, 1.701] | NO |
| W·SR | IPW | [-0.408, 0.565] | yes | [-0.409, 0.566] | yes |
| W·SR | SNIPW | [-0.428, 0.538] | yes | [-0.429, 0.539] | yes |
