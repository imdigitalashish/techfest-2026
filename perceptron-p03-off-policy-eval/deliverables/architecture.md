# Architecture — Did-It-Work (optional 1-page diagram for Round 1)

```mermaid
flowchart TB
  subgraph IN[Inputs]
    L0[Before-period logs<br/>old policy π₀ · x, a, r, propensity]
    L1[After-period logs<br/>new policy π₁ · x, a, r, propensity]
    P[Policy definitions π₀, π₁<br/>scorer / ε-greedy / Thompson sampling]
  end
  subgraph CORE[Estimation core — best practice]
    PA[Policy adapter<br/>π·a given x· on logged contexts]
    RM[Cross-fitted reward model q̂·x,a·]
    EST[OPE estimators<br/>IPW · SNIPW · DM · DR · Switch-DR<br/>→ per-round influence terms]
  end
  subgraph SPIKE[Spikes]
    DEC[★ Decomposer<br/>primary: after-period contrast D₁<br/>secondary: 2×2 Shapley + interaction ·OPE fills two cells·<br/>old-policy ordering: mix shift ·DR density ratio· + drift]
    GATE[★ Overlap gate · exploratory<br/>ESS/n · mean-weight test · zero-reward guard<br/>gates every OPE cell a term needs]
    CERT[★ Certificate<br/>Wald + hour-block intervals · after-period Hajek-MSM bounds · Γ*]
  end
  REP[Verdict: worked / hurt / can't tell from these logs<br/>waterfall · intervals · diagnostics]
  subgraph EVAL[Evaluation — every number checked against truth]
    SIM[Simulator, exact truth<br/>drift · mix · feedback · overlap · sparse rewards · noisy propensities · hidden override · misspecification]
    OBD[Open Bandit Dataset, real truth<br/>concurrent Random & Thompson-sampling arms<br/>pre-registered before/after re-enactments, both directions]
    CHK[Frozen banks · pre-registration · doc-drift check<br/>RMSE · sign · coverage · abstention · confident-wrong count]
  end
  L0 & L1 --> RM & EST
  P --> PA --> EST
  RM --> EST
  EST --> DEC & GATE & CERT
  GATE --> REP
  DEC & CERT --> REP
  SIM -. exact counterfactuals .-> CHK
  OBD -. concurrent arms .-> CHK
  REP --> CHK
```

**Estimands (review A3):**
- *Primary:* the after-period policy contrast on the observed traffic, D₁ = V(after, π₁) − V(after, π₀). One OPE cell is needed, from the after logs.
- *Secondary:* the Shapley attribution over two factors. Both OPE cells (V(before, π₁) from before logs, V(after, π₀) from after logs) must pass the gate.
  - naive = V(after, π₁) − V(before, π₀) = policy + environment.
  - policy = ½[(V(before, π₁) − V(before, π₀)) + D₁]; interaction = D₁ − (V(before, π₁) − V(before, π₀)).
  - Half of the interaction sits inside each main term, so it is never added as a third bar.
- *Separately:* the old-policy-ordered environment change, V(after, π₀) − V(before, π₀), splits into user-mix shift (doubly robust density ratio) and response drift. It does not partition the Shapley environment term.
- *Not identified* from these logs: the total effect when the policy changes who arrives (feedback).

If the gate fails on the logs behind a needed cell, the verdict falls back to the ordering whose cell passes, or says "can't tell from these logs".

Component contracts: [`../architecture/components.md`](../architecture/components.md) · spike rationale: [`../architecture/adr/001-spike.md`](../architecture/adr/001-spike.md).

**Figures** (regenerate with `.venv/bin/python eval/plot_waterfall.py` and `eval/run_decomposer_review.py`):
- Waterfall, simulator S1 (SYNTHETIC, 30 seeds): ![S1 waterfall](figures/S1_drift_masks_gain_waterfall.png)
- Drift sweep (SYNTHETIC): ![drift sweep](figures/drift_sweep.png)
