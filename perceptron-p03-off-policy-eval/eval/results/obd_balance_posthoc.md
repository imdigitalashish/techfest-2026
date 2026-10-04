# POST-HOC balance diagnostic (W2; not pre-registered)

The pre-registered check (TVD over hashed categories) flagged ~0.36 for every user feature. This diagnostic asks whether that is a population difference or a labelling difference between the two files.

| feature | categories R / B / shared | TVD on shared labels (+ other) | label-free TVD (sorted shares) | sorted shares R | sorted shares B |
|---|---|---|---|---|---|
| user_feature_0 | 4 / 4 / 3 | 0.0016 | 0.0016 | [0.528, 0.361, 0.106, 0.005] | [0.53, 0.359, 0.106, 0.005] |
| user_feature_1 | 6 / 6 / 5 | 0.0027 | 0.0027 | [0.527, 0.361, 0.058, 0.046, 0.009, 0.0] | [0.529, 0.359, 0.058, 0.045, 0.009, 0.0] |
| user_feature_2 | 10 / 11 / 9 | 0.0028 | 0.0028 | [0.361, 0.157, 0.149, 0.101, 0.098, 0.09, 0.033, 0.009, 0.0, 0.0, 0.0] | [0.359, 0.157, 0.15, 0.101, 0.099, 0.091, 0.032, 0.009, 0.0, 0.0, 0.0] |
| user_feature_3 | 9 / 10 / 8 | 0.0044 | 0.0044 | [0.361, 0.235, 0.225, 0.072, 0.059, 0.035, 0.01, 0.002, 0.0, 0.0] | [0.359, 0.233, 0.227, 0.072, 0.06, 0.037, 0.01, 0.002, 0.0, 0.0] |

Reading: if the label-free TVD is near 0 while the hashed TVD is ~0.36, one category carries a different hash in each file, and the populations match in distribution. The pre-registered caveat is then a data-labelling artefact rather than an imbalance; the pre-registered result is still reported as is.
