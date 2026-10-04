# Real public-data state-level learning checks

Command: `python3 scripts/extract_parakh2024_state.py && python3 scripts/extract_udise2425_state.py && python3 scripts/real_data_analysis.py`

Caveat: ASER is a rural household oral assessment of fixed reading/arithmetic levels, while PARAKH is a school-based written assessment reporting average percent correct. These are different constructs and populations; this is a state-level concordance check, not an individual-score equivalence claim.

## ASER 2024 vs PARAKH 2024

| Pair | n | Pearson r | Spearman rho | Mean absolute rank difference |
|---|---:|---:|---:|---:|
| ASER govt Std III reading vs PARAKH Grade 3 Language | 27 | 0.552 | 0.437 | 6.56 |
| ASER govt Std III subtraction vs PARAKH Grade 3 Mathematics | 27 | 0.339 | 0.255 | 6.96 |

Top rank disagreements: ASER reading vs PARAKH Language

| state       | aser_rank | parakh_rank | abs_rank_diff |
| ----------- | --------- | ----------- | ------------- |
| Rajasthan   | 23        | 4           | 19            |
| Nagaland    | 25        | 11          | 14            |
| West Bengal | 6         | 19          | 13            |
| Gujarat     | 11        | 23          | 12            |
| Bihar       | 14        | 25          | 11            |

Top rank disagreements: ASER subtraction vs PARAKH Mathematics

| state          | aser_rank | parakh_rank | abs_rank_diff |
| -------------- | --------- | ----------- | ------------- |
| Rajasthan      | 27        | 4           | 23            |
| Madhya Pradesh | 26        | 7           | 19            |
| West Bengal    | 5         | 22          | 17            |
| Sikkim         | 6         | 22          | 16            |
| Kerala         | 17        | 3           | 14            |

## Linking check: PARAKH state average to ASER state percentage

| Link | n | LOSO linear MAE (pp) | LOSO mean-baseline MAE (pp) |
|---|---:|---:|---:|
| PARAKH Language -> ASER reading | 27 | 9.21 | 10.46 |
| PARAKH Mathematics -> ASER subtraction | 27 | 7.55 | 7.86 |

## UDISE+ covariates vs learning

| covariate                   | outcome                 | n  | r     | rho   |
| --------------------------- | ----------------------- | -- | ----- | ----- |
| Single-teacher school share | ASER 2024 govt reading  | 27 | -0.13 | -0.16 |
| Single-teacher school share | PARAKH Grade 3 Language | 27 | -0.11 | -0.19 |
| PTR                         | ASER 2024 govt reading  | 27 | 0.05  | 0.15  |
| PTR                         | PARAKH Grade 3 Language | 27 | -0.18 | -0.18 |

## ASER government-school change, 2022 to 2024

Reading: top 5 gains

| state            | 2022  | 2024  | change_pp |
| ---------------- | ----- | ----- | --------- |
| Himachal Pradesh | 23.00 | 49.70 | 26.70     |
| Uttarakhand      | 22.10 | 35.60 | 13.50     |
| Kerala           | 31.60 | 44.40 | 12.80     |
| Mizoram          | 13.20 | 25.00 | 11.80     |
| Uttar Pradesh    | 16.40 | 27.90 | 11.50     |

Reading: bottom 5 changes

| state             | 2022  | 2024  | change_pp |
| ----------------- | ----- | ----- | --------- |
| Nagaland          | 9.10  | 7.10  | -2.00     |
| Telangana         | 6.30  | 6.80  | 0.50      |
| West Bengal       | 32.60 | 34.00 | 1.40      |
| Gujarat           | 23.20 | 24.70 | 1.50      |
| Jammu and Kashmir | 4.30  | 6.70  | 2.40      |

Subtraction: top 5 gains

| state            | 2022  | 2024  | change_pp |
| ---------------- | ----- | ----- | --------- |
| Mizoram          | 35.30 | 55.30 | 20.00     |
| Tamil Nadu       | 9.30  | 27.60 | 18.30     |
| Himachal Pradesh | 31.30 | 49.50 | 18.20     |
| Punjab           | 31.10 | 45.80 | 14.70     |
| Maharashtra      | 18.50 | 31.60 | 13.10     |

Subtraction: bottom 5 changes

| state             | 2022  | 2024  | change_pp |
| ----------------- | ----- | ----- | --------- |
| Gujarat           | 22.90 | 16.50 | -6.40     |
| Kerala            | 32.70 | 26.90 | -5.80     |
| Jammu and Kashmir | 26.10 | 22.70 | -3.40     |
| Sikkim            | 36.10 | 35.10 | -1.00     |
| Tripura           | 29.00 | 28.00 | -1.00     |
