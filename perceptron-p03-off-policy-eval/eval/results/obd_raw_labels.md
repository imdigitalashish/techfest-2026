# POST-HOC: raw user-feature labels in the official OBD zip (review A7)

Reproduce: `.venv/bin/python eval/obd_raw_labels.py` (reads the first ~1.5 MB compressed of each member by HTTP range request; labels read as raw strings, `keep_default_na=False`).

## user_feature_0

| label (first 12 chars) | Random share | BTS share |
|---|---|---|
| 81ce123cbb5b | 0.513 | 0.534 |
| 574464659df0 | 0.367 | 0.000 |
| 8ca3f3c62ebd | 0.000 | 0.347 |
| cef3390ed299 | 0.115 | 0.114 |
| 4ae385d792f8 | 0.005 | 0.004 |

## user_feature_1

| label (first 12 chars) | Random share | BTS share |
|---|---|---|
| 03a5648a7683 | 0.519 | 0.543 |
| a05b66683c9a | 0.367 | 0.000 |
| e07fc4436e7c | 0.000 | 0.347 |
| 2d03db5543b1 | 0.067 | 0.067 |
| f1c2d6a32ec3 | 0.039 | 0.034 |
| 6ff54aa8ff7a | 0.007 | 0.008 |
| 8b50621825ff | 0.000 | 0.000 |

## user_feature_2

| label (first 12 chars) | Random share | BTS share |
|---|---|---|
| 3a845d98884c | 0.367 | 0.000 |
| 1e58eb4fb1a0 | 0.000 | 0.347 |
| 2723d2eb8bba | 0.153 | 0.162 |
| c2e4f76cdbab | 0.145 | 0.150 |
| 9b2d331c329c | 0.099 | 0.105 |
| 7bc94a2da491 | 0.099 | 0.095 |
| 719dab53a756 | 0.095 | 0.096 |
| 302deff13f83 | 0.033 | 0.036 |
| 9f4e8271d3d3 | 0.009 | 0.009 |
| 7ae37150e596 | 0.000 | 0.000 |
| c7cce49040b6 | 0.000 | 0.000 |

## user_feature_3

| label (first 12 chars) | Random share | BTS share |
|---|---|---|
| 397559c512c5 | 0.367 | 0.000 |
| fe64471cf5b1 | 0.000 | 0.347 |
| 9bde591ffaab | 0.233 | 0.238 |
| c39b0c7dd5d4 | 0.228 | 0.236 |
| f97571b9c14a | 0.069 | 0.077 |
| 06128286bcc6 | 0.057 | 0.054 |
| 05b76f5e97e5 | 0.034 | 0.036 |
| 270b3e1c052b | 0.011 | 0.011 |
| 3aef83d33730 | 0.001 | 0.001 |
| ec6cfbbf6c92 | 0.000 | 0.000 |
| 1f5491ca5913 | 0.000 | 0.000 |

Reading: labels present in only one file with matching shares are consistent with one category being anonymised differently in each file. The data cannot prove they are the same category, so the pre-registered balance caveat stays open (labelled UNRESOLVED), not dismissed.
