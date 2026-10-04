# Final abstract: hostile re-score

**GPT-6 Astra, 4 October 2026.** P5 evidence cutoff: `db4ed95`; checkout: `84f4e65`. References are relative to `perceptron-p05-impact-execution/`; **A** = `deliverables/round1-abstract.md`, **D** = `deliverables/architecture.md`.

**Weighted rubric 3.25/5 (65/100).** The minimum viable total-slippage win remains unmet. Reporting H2's failure does not establish the replacement explanation that the simulator leaves no scheduling opportunity. Accepted review decisions are not evidence that every correction reached the final.

## Rubric

| Criterion | Weight | Score / 5 | Weighted | Justification |
|---|---:|---:|---:|---|
| Problem understanding | 20% | 4 | 0.80 | Understands endogenous costs, but wrongly infers near-optimality from size scaling and an unresolved decay measurement. |
| Technical soundness / feasibility | 25% | 3 | 0.75 | Instrument works within a modified market; useful estimator, robust execution advantage and empirical recalibration remain unresolved. |
| Innovation beyond starter | 20% | 3 | 0.60 | An engineering/evaluation contribution beyond TWAP, not a new counterfactual method or demonstrated superior execution algorithm. |
| Clarity | 10% | 3 | 0.30 | Status labels help, but pooled cohorts, component meanings and primary-versus-descriptive findings still blur. |
| Evaluation rigor | 15% | 4 | 0.60 | Explicit non-replication and new diagnostics; post-hoc physics selection and secondary-mechanism language still overreach. |
| Team fit | 10% | 2 | 0.20 | Two unconfirmed teammates do not establish the capacity required by the roadmap. |
| **Total** | **100%** | | **3.25 / 5** | **65 / 100** |

## Remaining overclaims and unsupported qualifications

### 1. [blocker] Physics is being used to explain away a failed primary result

**A:13:** “In the default market our impact is near-linear in size (log-log slope 0.87 [0.57, 1.35]; square-root law: δ ≈ 0.5) and fully transient, so TWAP is near-optimal and scheduling gains are tiny.”

**A:37:** “We do not yet claim to beat TWAP: with near-linear impact the headroom is tiny, so the realism gate comes first.”

`eval/results/realism_scorecard.json` labels 0.87 explicitly **post hoc**, using only three selected sizes. The registered five-size estimate is 1.006 [0.546, 1.760], with only 75% valid bootstrap slopes. This is the synchronized market, not unmodified default ABIDES. No detectable gap ten minutes later is not proof of full transience: at 4,000 shares the post-window CI is approximately [-8.70, +2.78] cents. Size scaling alone establishes neither TWAP optimality nor an upper bound on attainable savings.

**Fix:** disclose the registered estimate, selected-size sensitivity and unresolved permanence; remove the optimality/headroom explanation.

### 2. [major] E12 measures relative at-fill cost, and the sentence combines different experiments

**A:26:** “Touch-capped orders improve the fill price by 0.041 bps [0.036, 0.046] vs TWAP (genuine price improvement, not decision-to-fill movement; E12), but give it back in timing (+0.026 bps).”

The 0.041 is a reduction relative to each arm's own pre-fill mid, not a demonstrated improvement in unconditional average sale price. The +0.026 comes from **E6 IA_full**, whereas the first number is **E12 TWAP_touch_limit** (`eval/claims.py:35-51,240-249`). Recomputed same-arm E12 differences: at-fill -0.04065, delay +0.00380, drift +0.02280, own impact +0.01489; total IS **+0.00084 [-0.03210, +0.03277]** bps.

**Fix:** call it an at-fill concession reduction and report offsets/net IS from that same arm and seed block.

### 3. [major] A descriptive component finding is promoted to a replicated mechanism

**A:35:** “What replicated is smaller: the QP schedule lowers own impact (-0.014 bps [-0.025, -0.002]) but pays part back in instantaneous cost; front-loading is negligible.”

This is E10's factorial QP main effect, not a replicated QP-only result. E6 tested QP plus legacy feedback; E8's QP main-effect CI included zero. Amendment A1 explicitly makes attribution **descriptive**. “Negligible” means its CI lies within the selected **±0.02 bps** margin, not universally irrelevant (`eval/preregistration.md:110-123`; E10 attribution table).

**Fix:** say “E10 descriptive attribution detected a QP-associated own-impact reduction”; state the equivalence margin and task scope.

### 4. [major] Exact touch-log equality is still called book equality

**A:19:** “Re-keying every agent's random stream per wake-up (a common-random-numbers coupling) keeps them aligned; pre-trade books match event-by-event in 180/180 runs checked exactly.”

`components/tca/tca/metrics.py::pre_window_exact` compares timestamps, best bids/asks and their quantities. It does not compare full depth, queues, agent state or oracle state. E12 confirms those **top-of-book logs** on 60 seeds across three arms, not 180 independent markets. Nor does the check establish alignment after intervention.

**Fix:** name the exact checked object, sample structure and pre-trade interval.

### 5. [minor] Dispersion and market-preservation claims need their experimental scope

**A:20:** “Own-impact dispersion falls 6× (0.97 → 0.16 bps); paired CIs tighten 7.7×.”

These describe E4/E3/E5, not universal factors. E4's early-horizon dispersion increased. Give the seed counts and component/comparison definition.

**A:21:** “The coupling keeps volume and trade counts within ±10% but widens mean spreads by 13% (E11), so it describes a slightly different market.”

The two equivalence results are supported; “slightly” understates unknowns. Return volatility, autocorrelation and depth are **unresolved**, not preserved (`eval/results/E11_market_laws.md`). Say “a measurably altered market; other properties unresolved.”

### 6. [minor] The estimator score lacks the crucial averaging qualifier

**A:24:** “held-out R² is 0.15 (TWAP) and -0.02 (random slicing), per-seed RMSE 5.0¢ vs 19.7¢ with naive twins.”

Those R2 values score the **seed-mean path**. Per-seed R2 is approximately 0.010 and -0.004 (`eval/results/calibration_sync.json:139-149`). Label the averaging explicitly; lower RMSE against a less dispersed target does not independently establish better live identification.

### 7. [major] “Vanishes” repeats the absence-of-evidence error

**A:41:** “The amplification that naive twins suggested vanishes.”

The earlier momentum CI already included zero; the new +70 [-60, +204] also does. Different blocks and different couplings do not establish disappearance of a mechanism. The adjacent “value agents absorb 102% of our 4,000 shares” should instead say **net inventory rises by an amount equal to 102%**, not imply direct counterparties.

**Fix:** “No momentum amplification was detected; reported quantities are net inventory differences.”

### 8. [major] The diagram claims an incumbent-comparison ratchet that is not implemented

**D:28:** “paired vs incumbent, untouched confirmation seeds”

**A:27:** “Policy search: a development-time ratchet with paired comparisons and untouched confirmation seeds; PPO deferred.”

`components/execution_agent/autoresearch/eval.py` still compares each candidate against TWAP. `autoresearch/program.md:7` retains the incumbent-half-CI heuristic and recycled validation block. The claimed correction has not reached this implementation.

**Fix:** mark the incumbent-comparison search **planned**, or implement the specified direct comparison and update the protocol.

### 9. [minor] Simulator identification and calibration language remains too strong

**A:11:** “so no backtest can say what the price would have been without us. ABIDES can”

Say historical replay cannot identify the counterfactual; ABIDES supplies a **model-conditional trajectory**, not the uniquely correct missing price.

**A:23:** “recalibrate the agent mix ... until impact is concave and partly permanent”

This risks choosing physics to manufacture execution headroom. Predeclare external calibration targets and held-out realism criteria, rather than tuning until the desired story appears. The cited [2607.04280](https://arxiv.org/abs/2607.04280v1), opened through the official abstract API, establishes mechanisms **within its model**, not transfer to ABIDES.

## Top three fixes

1. Remove the post-hoc physics/optimality narrative; use unresolved scaling/permanence and externally anchored calibration targets.
2. Repair the result sentences: same-arm E12 accounting, descriptive E10 attribution, explicit equivalence margins and no “amplification vanishes.”
3. Enforce implementation/evidence boundaries: top-of-book rather than full-book identity, mean-path rather than per-seed R2, planned rather than built incumbent search; confirm staffing before promising the roadmap.

**Doc check:** the abstract body is 898 words. `python3 -B eval/check_docs.py` fails because the selection-memo template requires missing `astra_final`. This is pending review-ledger wiring, not an abstract-number mismatch; the lead must update the ledger/rendered artifacts and rerun. No simulations were run. Only this review file was written.
