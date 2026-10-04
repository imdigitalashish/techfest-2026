# Pre-registration — real Open Bandit Dataset check (P3 step 1)

- **Registered:** 2026-10-04 13:06:47 IST (clock from `TZ=Asia/Kolkata date`, written just before the commit that adds this file). Written before any of the analyses below were run on the slices.
- **Already seen before registering (disclosed):**
  - The 10k-row repo sample: Random CTR 0.00380, BTS CTR 0.00420. The static ZOZOTOWN-prior Monte Carlo correlates 0.074 with the BTS logs' own propensities (`eval/results/obd_sample_summary.md`).
  - The full Random log (campaign All): 1,374,327 rows, sorted by timestamp (row count and sortedness only; no CTR or other statistic computed).
  - Nothing from the BTS slice has been seen.
- **Script:** `eval/run_obd_slice.py`, written after this registration and before its first run. Output: `eval/results/obd_slice_summary.md` + `eval/results/obd_slice.json`.

## Data
- **R** = full Random log, campaign All, read from the official zip (https://research.zozo.com/data_release/open_bandit_dataset.zip) by `eval/obd_zip_slice.py --member open_bandit_dataset/random/all/all.csv --budget_mb 30`.
- **B** = the time-ordered first 100 MB (compressed) of the BTS log, campaign All: `eval/obd_zip_slice.py --member open_bandit_dataset/bts/all/all.csv --budget_mb 100`.
- **Window W** = [max(first R ts, first B ts), last B ts floored to the hour). R and B are both restricted to W. Hours with fewer than 1,000 B rows are dropped from both R and B, everywhere.
- Timestamps are UTC as in the data. A "day" is a UTC calendar day.

## Policies
- **Random:** uniform over items at each position; its logged propensity is used as is.
- **BTS, two reconstructions**, using only B's (timestamp, item, position), never B's clicks:
  - *P-static*: the static ZOZOTOWN prior (`prior_bts.yaml`, campaign all), Monte Carlo with 400,000 draws (the obp protocol's evaluation policy).
  - *P-hourly*: for each hour h, the empirical frequency of (item, position) among B rows in h, normalised per position.

## Analysis 1 — Did the deployed BTS change during the window?
- Cells: the 20 (item, position) cells with the most B rows in W.
- Statistic: the median logged propensity per 6-hour bucket, per cell.
- **Decision rule:** "BTS changed within W" if at least 10 of the 20 cells have (max bucket median)/(min bucket median) ≥ 1.5.
- Also reported:
  - Spearman ρ between bucket index and the bucket median, per cell.
  - The number of distinct propensity values per cell-hour.
  - The correlation of the W-average empirical (item, position) frequency with P-static.

## Analysis 2 — Standard protocol: estimate V(BTS) from R, truth = BTS on-policy CTR (same window)
- Estimators:
  - IPW, SNIPW and DR (as in `eval/run_obd.py`).
  - DM: per-(item, position) CTR shrunk toward the position CTR with 200 pseudo-impressions, 2-fold cross-fitted.
  - Both evaluation policies, P-static and P-hourly.
- **Truth:** the CTR of B in W.
- **Metric:** relative error |V̂ − truth|/truth.
- **Consistency test:** the 95% CI of (V̂ − truth) contains 0. Its variance is the bootstrap variance of V̂ (500 resamples) plus the binomial variance of the truth.

## Analysis 3 — Real before/after with real truth, both directions
Split W at its time midpoint into W1 (before) and W2 (after). Because R and B ran concurrently, all four cells V(period, policy) are observed on-policy. This is the truth.

- **Direction A — "deploy BTS"** (old = Random, new = BTS). Before logs = R∩W1; after logs = B∩W2.
  - Naive = CTR(B∩W2) − CTR(R∩W1).
  - Truth = CTR(B∩W2) − CTR(R∩W2).
  - OPE estimate = CTR(B∩W2) − V̂_Random(W2), where V̂ is computed from B∩W2 with B's logged propensities. The DR reward model is per-cell CTR from B∩W2, cross-fitted.
- **Direction B — "roll back to Random"** (old = BTS, new = Random). Before logs = B∩W1; after logs = R∩W2.
  - Naive = CTR(R∩W2) − CTR(B∩W1).
  - Truth = CTR(R∩W2) − CTR(B∩W2).
  - OPE estimate = CTR(R∩W2) − V̂_BTS(W2), from R∩W2 with P-hourly.
- **Estimators:** IPW, SNIPW and DR. DR is the primary estimator, fixed now; no switching after seeing results.
- **2×2 Shapley decomposition**, per direction. OPE fills the two unobserved cells, and each term is compared with the all-on-policy truth:
  - policy = ½[(V(W1,new) − V(W1,old)) + (V(W2,new) − V(W2,old))]
  - env = ½[(V(W2,old) − V(W1,old)) + (V(W2,new) − V(W1,new))]
  - interaction = (V(W2,new) − V(W2,old)) − (V(W1,new) − V(W1,old))
- **CIs:** Wald for on-policy CTRs; 500-resample bootstrap for OPE terms; independent pieces' variances add.
- **Pre-registered readouts** (all reported, whatever they show):
  - (S1) whether the 95% CI of (DR estimate − truth) contains 0, per direction;
  - (S2) |naive − truth| versus |DR − truth|, and whether naive's 95% CI contains the truth point.
- **Secondary:** the same two directions for every ordered pair of whole UTC days (d1 < d2) inside W, with W1 = d1 and W2 = d2. All pairs are reported; none are selected.
- **Balance check:** within W2, the total-variation distance between R and B in the distribution of each `user_feature_k` (top 50 categories + "other"). If any TVD > 0.05, add the caveat "arm assignment may not be randomised by user".

## What would change our claims
- If S1 fails for DR in either direction, the abstract may not claim that OPE recovers the effect on real data, and the failure is reported.
- If naive ≈ truth on OBD, the abstract says so ("on OBD the drift between halves was small; naive happened to be right") and uses the simulator for the sign-flip case. The simulator case must not be dressed up as real.
