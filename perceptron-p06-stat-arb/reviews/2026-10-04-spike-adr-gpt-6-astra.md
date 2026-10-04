# P6 raw hostile-judge review: spike, methodology and pre-registration

Reviewer: GPT-6 Astra (`gpt-6-astra`), methodology/statistics/novelty reviewer under PLAYBOOK section 10.

Evidence cut: 2026-10-04 14:35 IST, repository `99534d8`. The scientific files reviewed are unchanged from `85b508d`. Paths below are relative to `perceptron-p06-stat-arb/` unless stated otherwise. This is TASK 1, not approval of a final rendered abstract.

## Verdict

**53/100 (2.65/5). Do not claim demonstrated executable profitability or a clean, twelve-day confirmatory discovery.** The defensible current claim is narrower: a feature-rich model has promising exploratory results against a trained threshold in a particular published-quote replay.

There are three claim blockers: the economic interpretation of the simulator's labels, the unobserved market state between quote publications, and reuse of five inspected days in the nominally pre-registered primary test. More bootstrap resamples cannot fix any of these.

Round 1 explicitly judges a plan, not a completed prototype (`_briefs/perceptron.txt:305-307`). The score below is for the proposed method and the evidence supporting its claims, not a penalty for failing to deliver a production trading system already. Here, **blocker** means a stated headline cannot be supported; **major** means the design or attribution needs substantive repair; **minor** means a bounded presentation/readiness gap.

## Evidence boundaries and findings that are not accusations

- Read PLAYBOOK sections 6 and 10; the Problem 6 brief and scoring rubric; ADR 001; the registration; the four-day, clock-skew, cadence and relevant nine-leg baseline results; the abstract template; and the detector, simulator, feature, policy, training and evaluation code cited below.
- At this cut, `falsification_walkforward_5d.md` and `falsification_walkforward_12d_prereg.md` were absent after fetching/rebasing. The five-day numbers are only a disclosure in the registration, not independently reviewed results. The eventual twelve-day verdict is **UNVERIFIED**.
- Registration commit `0ca23e8` is timestamped `2026-10-04T14:24:44+05:30`, consistent with its text. All eleven registered source files match `604f54d`. This verifies the source snapshot, not the provenance of reused caches or the claim that seven days were never inspected.
- I did **not** find direct future-duration leakage into the registered LEV features. `rules.LEARN_X` is an explicit feature list; `T_ms`, `E`, `duration_us`, `edge_max_bps` and realised outcomes are not in it. Detector start features and its EWMA use past/current observations. Building labels after an episode closes is not itself look-ahead.
- A test day becoming the next fold's training day is legitimate walk-forward learning. It can induce dependence between fold scores; it is not automatically train/test leakage.
- Same-asset, multi-exchange crypto is expressly permitted as a starter resource (`_briefs/perceptron.txt:122-123`). BTC/ETH is not required to rescue MVP compliance. Do not add an unsupported cross-asset claim just to match the problem title.

## Numbered issues

### P6-01 | blocker | The label is basis-adjusted execution surplus, not realised portfolio P&L

**Evidence.** `components/sim/fills.py:62-64` subtracts an estimated basis:

```python
basis_px = g["basis0_bps"].to_numpy() * 1e-4 * mid
pnl = m * ((bid_s - ask_b) - basis_px) - m * (fs * bid_s + fb * ask_b)
```

Only mismatched quantities are subsequently unwound (`fills.py:66-72`). The matched position has no closing/rebalancing transaction. `eval/results/baseline_0901_to_1001.md:5` discloses marking against the EWMA basis; ADR 001 nevertheless calls the target expected "realised P&L".

**Why it matters.** Subtracting a modelled fair premium is not a cash flow. In spot/perpetual and USD/USDT combinations, it also does not settle funding, currency conversion or basis convergence. A positive residual can coexist with negative immediate cash proceeds or an unclosed relative-value position. This can be a useful execution-quality score, but the labels do not establish a self-financing arbitrage strategy.

**Concrete fix.** Call the existing metric **basis-adjusted simulated execution surplus** everywhere it is used. For an economic P&L claim, implement a cash/position ledger, declared marking or closing horizon, contract/FX conversion, funding and inventory rebalancing. Separate same-currency spot/spot from spot/perpetual and cross-currency lanes. Reconcile a small hand-calculated example for each lane before making profitability claims.

### P6-02 | blocker | The fast-latency experiment cannot identify the missing market state

**Evidence.** `eval/results/update_cadence.md:7-11` gives median timestamp gaps of 100.1 ms for Binance spot, 26.0 ms for Binance futures and 100.0 ms for both OKX legs; Coinbase is 3.3 ms. Registration cells are one-way 1/5/20 ms, with equal feed/order latency. `LegBook.at` (`fills.py:26-30`) carries the most recent published quote forward. The template acknowledges resolution limits but adds: "Comparisons between policies run on identical data."

**Why it matters.** A microsecond timestamp or simulated order delay does not reconstruct changes hidden inside a publication interval. A faster counter-leg can produce a genuinely observed short episode; therefore it would be wrong to say every sub-100-ms lifetime is impossible. What is unidentified is the slower leg's executable state at order arrival. Shared data do not make this bias cancel: LEV explicitly uses quote age and other features that can select publication artefacts differently from a threshold.

**Concrete fix.** Label current curves as **published-quote persistence / quote-replay sensitivity**, not matching-engine opportunity lifetimes or executable latency frontiers. Obtain sufficiently fine updates for a restricted venue pair, or demonstrate bounds/sensitivity under adverse within-interval quote changes and liquidity depletion. Report per-venue cadence on more than this one day. Merely adding jitter or interpolating quotes is not new evidence of fillability.

### P6-03 | blocker | Twelve out-of-fold days are not twelve untouched confirmatory days

**Evidence.** `eval/PREREGISTRATION-walkforward-12d.md:43-49` discloses that five of twelve test days were already examined. The seven previously unexamined days are secondary (`:36-38`); the primary mean uses all twelve (`:32-34`). `deliverables/round1-abstract.tmpl.md:48` says "Pre-registered test over {{wf_n}} held-out months".

**Why it matters.** The split is temporally out-of-fold, but part of the evaluation data has informed the research process. Fixing model hyperparameters before those looks does not by itself establish that the hypothesis, stopping/sample-size choice, aggregation and headline were independent of the outcomes. Disclosure is necessary; it does not restore a nominal confirmatory error rate. Also, these are twelve sampled days, not twelve months of tested trading.

**Concrete fix.** Run and publish the registered analysis unchanged, but describe it as a pre-specified extension of an exploratory analysis: twelve sampled days, five previously inspected. Show the registered unseen-seven analysis separately without promoting it after seeing its answer. For a fresh confirmatory claim, freeze a new independent holdout and analysis before access; if amending anything before new results are inspected, append a timestamped amendment, never rewrite the registration. Whether the seven days were genuinely unseen remains **UNVERIFIED** by this review.

### P6-04 | major | The interval rule is conditional, not a small-sample robustness guarantee

**Evidence.** `eval/falsification.py:113-152` implements the usual paired t-interval and IID percentile bootstrap of day differences. `walkforward` trains on each preceding sampled day. `eval/results/falsification_walkforward_4d.json` gives differences of approximately $649.89, $43.12, $131.94 and $166.40; its reported mean is $247.84 and t-interval is [-$186.60, +$682.27].

**Statistical assessment.**

- **Pairing/unit of replication:** pairing LEV and threshold on the same day and resampling whole days is appropriate for their within-day shared shocks. The code does not incorrectly count six cells or thousands of episodes as independent test days.
- **Dependence:** non-overlapping test dates do not establish independent fold scores. Adjacent scores share a day's data through testing/training, and market regimes can persist between monthly samples. The variance formula and IID resampling ignore this. The size/sign of actual dependence is **UNVERIFIED**, not proven harmful.
- **Tails/power:** a t-interval is exact for IID normal differences and otherwise relies on approximation; twelve observations are not a guarantee. The bootstrap cannot invent an unobserved crash. With four positive differences its lower percentile bound is necessarily positive. In the pilot, one day supplies 65.6% of total uplift and sample SD is $273.02. For scale only, an IID-normal planning approximation `(2.201 + 0.842) * 273.02 / sqrt(12)` gives an approximately $240 six-cell daily effect for 80% power. This is not exact power for the joint rule, and four selected pilot days cannot reliably estimate tail risk or the final variance.
- **Decision rule:** requiring both lower bounds to exceed zero is more restrictive than requiring either. It is not two independent confirmations or a cure for selection/dependence. Conditional on a valid t-model, its positive two-sided-95% lower bound corresponds to a one-sided 2.5% test; there is no need to Bonferroni-correct merely because both intervals must pass.
- **Secondary multiplicity:** unadjusted secondary comparisons are acceptable as explicitly descriptive. They are not a reserve supply of significant claims. Sign tests concern positive-day probability, not mean dollar uplift; signed-rank inference additionally needs symmetry for its usual location interpretation and is not a distribution-free substitute for the mean test under heavy skew.
- **Failure to establish is not falsification:** the registration's "not established" wording is appropriate. `compare` and `md_walkforward` still label a nonpositive lower bound "falsified", including secondary comparisons. A wide interval containing zero does not prove no benefit.

**Concrete fix.** Define the population and a minimum practically worthwhile effect before the next untouched test. Publish all day differences, concentration, leave-one-day-out means and downside summaries; do not claim twelve days validate a tail distribution. Collect more time blocks/regimes before depending on HAC or block-bootstrap approximations; with twelve months these are sensitivity analyses, not magic replacements. Keep one primary hypothesis, descriptive secondary wording, and "not established" labels. Use familywise/FDR control only if secondary claims become confirmatory.

### P6-05 | major | Summing six counterfactual environments is not one day's deployable return

**Evidence.** Registration `:28` defines the day score as P&L summed over six fee/latency cells. `score_policies` (`eval/falsification.py:97-110`) sums the cell totals. The same episode can therefore contribute under several mutually alternative fee and latency assumptions.

**Why it matters.** This is a legitimate predeclared benchmark aggregate, but not a portfolio that could earn the displayed USD/day at one actual fee/latency configuration. Its sign answers an equal-weight six-scenario question, not "LEV wins at our deployment budget". Duplicating or changing scenario weights changes the economic interpretation. A positive sum can hide an operationally important losing cell.

**Concrete fix.** Preserve the frozen statistic, label it **sum across six counterfactual scenarios**, and put the complete per-cell table beside it. State the target deployment cell or an externally motivated scenario distribution for the next test. Report turnover, notional/capital and return per constrained capital as well as dollar totals. Do not change the primary weights after inspecting which cells win.

### P6-06 | major | Fill, inventory and fee assumptions can change the relative winner

**Evidence.** `fills.py:51-59` caps opening quantities at displayed size, so opening partial fills really are implemented. However, intents are evaluated independently without inventory balances or displayed-liquidity consumption; `fills.py:69-72` unwinds all unmatched size at a single best price without checking unwind depth. `LegBook.at` checks only that a prior quote exists, not quote expiry or whether arrival exceeds the recorded session. `components/costs/fees.py` declares `FEES_VERIFIED = False`; the registered experiment applies the same 1/2 bps to every leg.

**Why it matters.** Pre-positioned inventory removes transfer latency, not capital limits, inventory depletion or replenishment costs. Several pair opportunities may reuse the same displayed liquidity. Thin-book forced unwinds are precisely where losses can be worse than the labels. Public Coinbase Exchange fees are 4-60 bps outside its Liquidity Program [S5]; 1/2 bps is therefore a counterfactual scenario for that leg, not a verified accessible rate. Special programme eligibility/rates are **UNVERIFIED**. Published quote replay cannot observe failed races [S3].

**Concrete fix.** Add per-venue cash/inventory and simultaneous-order caps, shared-liquidity accounting, depth-limited/slippage-stressed unwinds, and a last-valid-quote/session boundary guard. Separately sweep asymmetric official fees, order-entry/response delays and fill haircuts. Explain whether profitable scenarios are accessible to the team. Quantify policy uplift under adverse assumptions, not just both policies' absolute losses. Until then, retain the simulator-only label.

### P6-07 | major | The clock test does not establish causal deployment robustness

**Evidence.** `eval/results/falsification_clockskew.md` contains one train/test pair and three random per-venue offsets, plus exchange/receive variants. `eval/falsification.py:197-215` applies each offset to both training and test data and refits policies. In receive mode, `feed_extra=False` removes the artificial feed shift, but `cells` still assigns `L_ms = 2 * d_ms + COMPUTE_US / 1000` (`:61-67`). ADR 001 `:40` declares test 3 "passed".

**Why it matters.** This demonstrates sign stability of refitted policies under five related representations of one date, not five independent replications or robustness to arbitrary +/-5 ms errors. Collector-time detection improves the information set but does not synchronize exchange clocks used for fill truth. The receive-mode `L_ms` is a scenario code, not the measured heterogeneous feed-plus-order latency claimed by the model's interpretation. Reusing an as-of published book also retains P6-02.

**Concrete fix.** Say exactly what passed: this one-date, refitted-policy sensitivity check. Add frozen-policy tests with unseen test-only drift, calibrated timestamp-error bounds and adverse relative offsets. Separate feed, entry and response latency per venue; do not infer order latency from feed latency as an empirical fact. Fix/document the receive-mode feature semantics in a new experiment, preserve the registered run, and test causal invariants with known synthetic clocks. A stable half-life rank does not validate absolute lifetimes or fills.

### P6-08 | major | The fitted target is clipped return, not the conditional expectation advertised

**Evidence.** `components/decision/autoresearch/rules.py:84-94` fits a squared-error regressor to `np.clip(train["pnl_bps"], -30, 30)` and acts when its prediction is positive. The template/ADR advertise expected P&L. The primary statistic is unclipped dollar surplus.

**Why it matters.** The ideal target of this fit is expected **clipped bps**, not expected raw P&L. Clipping changes the decision objective, not just numerical stability. Illustration, **not observed data**: a trade returning +0.5 bps with probability 0.99 and -100 bps with probability 0.01 has mean -0.505 bps, but clipped-at-30 mean +0.195 bps. Ranking bps is also not ranking dollar value when notionals differ. A prediction above zero alone is neither a calibration guarantee nor a risk/capital constraint.

**Concrete fix.** Name the target exactly. Show out-of-sample calibration around the zero-action boundary against the *unclipped* target, clipping frequency and tail contribution, with cost/latency stress. Compare an appropriately weighted raw-value model or explicit downside/risk-constrained objective in a separately frozen follow-up. Report expected shortfall, worst day and drawdown once a portfolio ledger exists; do not advertise an untested downside-quantile companion.

### P6-09 | major | The comparison does not isolate latency information; the training schedule is narrow

**Evidence.** `rules.py:23-38` fits a separate threshold for each pair/fee/latency group and includes abstention (`best = (np.inf, 0.0)`). LEV pools rows using age, spreads, volatility and other features (`:78-89`). `EDGE_ONLY_X` still includes size, pair, latency and fee. Registration `:25-30` uses one preceding first-of-month sample, not the preceding calendar day or a rolling month.

**Why it matters.** The existing comparison is fair as a comparison of complete policies on identical candidates, labels and nominal latency. It is not a controlled demonstration that latency conditioning or survival caused the gain: the threshold is already latency-conditioned, and the full model has more information and cross-cell pooling. One sparse training day can make per-group thresholds noisy while favouring pooled estimation; the actual size of that effect is **UNVERIFIED**. A month's gap tests this sampling policy, not ordinary daily retraining.

**Concrete fix.** Retain the threshold baseline and disclose its abstention option. Add a shrunk/pooled threshold or simple age/spread-aware regression baseline, plus same-capacity LEV with and without latency conditioning; use the existing full-versus-edge model comparison only for what it measures. For latency ablations, account for the fact that `L_ms` and `delta_ms` encode the same budget. Compare training windows with nested, chronological tuning on development data; lock the choice before new test access. Treat per-opportunity latency replicas as one group for internal validation. Verify end-to-end compute, rather than assuming the fixed 7-us EV-derived allowance proves the full live path's p99.

### P6-10 | major | The survival/act-wait story is ahead of the tested model

**Evidence.** ADR 001 `:28` describes residual survival as a feature and an act-now/wait rule and downside companion alongside LEV. The registered `rules.LEARN_X` and `components/decay/survival.py:19` contain no fitted survival probability or residual survival feature; the registered `POLICIES` has no wait or quantile policy. ADR `:42` admits the matched-event permutation is unrun. The detector ends an episode when the basis-adjusted edge crosses its 1-bp threshold and censors on stale feeds/end-of-data (`cross.py:67-96`).

**Why it matters.** Features originating in a survival module are not survival-model outputs. The full/edge ablation cannot establish that survival contributes information. The fitted lifetime is that of an observed threshold-crossing episode, not the lifetime of profitable execution at a given fee, size and latency. KM handles right-censoring under assumptions; it does not repair hidden intra-publication events. Stale-feed censoring may be informative. A decreasing fitted Weibull hazard can also reflect mixtures of venue types or publication schedules; it does not establish an optimal waiting rule.

**Concrete fix.** State "survival is the descriptive MVP and a separate baseline; the tested LEV uses market-state features". Keep residual-survival, confirmation and downside models explicitly future work unless they are wired and evaluated. Define the lifetime event and censoring assumptions beside every decay curve; distinguish publication-grid uncertainty from right-censoring. Report fee/size-specific executable-survival sensitivity and censoring rates, not just pair-ranking stability.

### P6-11 | major | Source pinning does not yet bind the evaluation artefacts to those sources

**Evidence.** `cached_cells` (`eval/falsification.py:82-94`) keys files by date/tag and accepts them if the opportunity cache has `t_start_us`; it does not validate code blobs, data hashes, fees, compute or latency settings. The clock result explicitly says it began from an uncommitted tree. The nine-leg baseline uses `components/decision/lev.py` (default 300 iterations, +/-50-bps clipping, log latency and per-tier fitting), while the registered five-leg experiment uses `rules.fit_gbm_reg` (200 maximum iterations, +/-30, linear `L_ms`, pooled fee feature). The template mixes their ranking/frontier and walk-forward claims under "LEV".

**Why it matters.** Correct registration blobs are not proof that cached labels were generated by them. I have **not** established that a stale cache was actually used. Likewise, differing LEV variants are not inherently wrong, but a single label hides model/cohort changes when headline numbers are juxtaposed. The compiled timing scripts were read; their generated timing result files were absent at this cut, so actual timing numbers are **UNVERIFIED** here.

**Concrete fix.** Bind each result/cache to a complete fingerprint of input data, source blobs, config and dependencies; fail or rebuild on mismatch. Record the actual cache fingerprint with the run. Give each headline its model variant, cohort, training/test dates, fees and clock. Keep the original exploratory files immutable. Do not fill missing placeholders with numbers from another variant merely because both are called LEV.

### P6-12 | major | Novelty is applied integration, not the invention of latency-aware value

**Evidence.** The template's novelty bullets are value-at-arrival ranking, censored survival and falsification-first evaluation. `research/landscape.md`, section 5, itself distinguishes known methods from potential hackathon packaging. Opened primary sources show existing feed/order/response latency models [S1], partial-fill/replay modelling and its limitations [S2], and learned LOB fill-time survival distributions [S4].

**Assessment.** Renaming conditional-return prediction "LEV" is not a new algorithm. Kaplan-Meier, gradient boosting and clock/holdout checks are not new methods either. The LOB survival paper is an adjacent passive-fill problem, not proof that the identical cross-venue target exists. This review does **not** establish first-ever novelty or exhaust the literature; those claims remain **UNVERIFIED**.

**Concrete fix.** Claim a specific, falsifiable engineering contribution: for example, an uncertainty-aware, executable-value-versus-latency benchmark that exposes when public quote data cannot support a trading claim. Demonstrate a matched-information gain or a useful resource-constrained ranking decision beyond the already latency-tuned threshold. Cite the existing execution/survival work. Do not claim novelty for process hygiene alone.

### P6-13 | minor | Team-fit evidence is missing, not inferable from a generated prototype

**Evidence.** `deliverables/round1-abstract.tmpl.md:7,55` retains `[TEAM]` motivation/skills placeholders. Its milestone line `:57` provides dates but no member ownership. The brief explicitly asks for skills across three members and a credible route to MVP (`_briefs/perceptron.txt:299-303,338-342`).

**Concrete fix.** Have the lead obtain truthful member-specific skills, relevant work and ownership of data/systems, modelling and evaluation/demo. Add a short critical path: realistic-label gate, untouched evaluation gate, then demo integration. Do not infer human readiness from code that agents produced or invent team credentials.

## Round-1 scoring

Weights and 1-5 scale are from `_briefs/perceptron.txt:313-354`. This scores the current plan/template; unresolved numeric placeholders are not scored as fabricated results.

| Criterion | Weight | Score / 5 | Weighted points / 100 | Evidence |
|---|---:|---:|---:|---|
| Problem understanding and relevance | 20% | 4 | 16 | ADR targets value at arrival; the same-asset multi-exchange MVP is explicitly allowed by the brief, but observed persistence is still conflated with execution. |
| Technical soundness and feasibility | 25% | 3 | 15 | Detector, supervised ranker and IOC simulator form a buildable plan; `fills.py:62-72` does not establish the economic target it advertises. |
| Innovation / novelty | 20% | 2 | 8 | Template novelty bullets mostly combine established prediction, survival and execution ideas; the incremental contribution is not isolated (P6-09/P6-12). |
| Clarity and structure | 10% | 3 | 6 | The template gives concrete components and MVP mapping, but "held-out months", "P&L" and the single "LEV" label obscure important distinctions. |
| Impact and evaluation rigour | 15% | 2 | 6 | A trained threshold and explicit gate exist, but the primary sample mixes inspected days, unresolved fill assumptions and only twelve fold scores. |
| Team fit and readiness | 10% | 1 | 2 | Skills and motivation remain `[TEAM]`; dates alone do not establish the three-member skill mix required by the rubric. |
| **Total** | **100%** | **2.65 weighted / 5** | **53** | **Plan score, not a probability of selection.** |

## The five changes with the highest expected credibility/score gain

1. **Repair the economic claim before adding models (P6-01/05/06/08).** Immediately rename the present output and six-cell aggregate honestly. Make one restricted trading lane reconcile to a cash/inventory ledger with credible fees and unwind costs; calibrate the raw target near the action boundary.
2. **Make the latency experiment identifiable (P6-02/07).** Use a sufficiently resolved restricted pair or explicit adverse missing-state bounds. Separate feed/entry/response delays and show where published data cannot support a fine-latency conclusion.
3. **Protect the inferential boundary (P6-03/04/11).** Publish the frozen twelve-day run without calling it twelve untouched months. Preserve the unseen-seven analysis, bind source/data/cache provenance, and predeclare an actually fresh holdout, practical effect and dependence-aware sensitivity plan.
4. **Earn attribution against the strong simple baseline (P6-09/10).** Keep the trained threshold; add pooling/age-aware controls and matched-capacity latency ablations. Test training-window choice only on development data. Remove survival/wait/downside claims not present in the registered model.
5. **Rewrite the submission around the defensible contribution and actual team (P6-12/13).** Lead with a narrowly scoped, uncertainty-aware latency decision experiment, not a new trading algorithm or validated profitability. Attribute prior art, assign three real owners, and make realism/evaluation/demo gates explicit.

## External sources actually opened

All accessed 2026-10-04. These support only the specific statements above; no proprietary Optiver capability or production-speed claim was verified.

- **[S1] HftBacktest, Latency Models:** https://hftbacktest.readthedocs.io/en/latest/latency_models.html. Distinguishes feed, order-entry and order-response latency; describes constant and measured/interpolated models.
- **[S2] HftBacktest, Order Fill:** https://hftbacktest.readthedocs.io/en/latest/order_fill.html. Explicitly warns that market-data replay cannot change the market, including after simulated liquidity-taking fills.
- **[S3] BIS Working Paper 955, Quantifying the high-frequency trading arms race:** https://www.bis.org/publ/work955.htm (redirected to https://www.bis.org/publications/working-paper-955-quantifying-high-frequency-trading-arms-race). The opened abstract explains why failed trade/cancel attempts in message data reveal race losers unavailable in ordinary book data. It is equities evidence, not a measured crypto race rate.
- **[S4] Arroyo, Cartea, Moreno-Pino and Zohren, Deep Attentive Survival Analysis in Limit Order Books: Estimating Fill Probabilities with Convolutional-Transformers (2023):** https://arxiv.org/abs/2306.05479. The opened HTML citation metadata/abstract describes modelling fill-time distributions from time-varying LOB features. No claim here depends on an unexamined numerical result from the paper.
- **[S5] Coinbase Exchange, Trading Fees:** https://help.coinbase.com/en/exchange/trading-and-funding/exchange-fees. The opened table lists 60-bps base and 4-bps highest published standard taker tier, with an explicit separate-Liquidity-Program qualification.
