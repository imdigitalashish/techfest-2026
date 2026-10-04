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
    DEC[★ Decomposer · 2×2 Shapley<br/>cells V·period, policy·: two observed, two by OPE<br/>→ policy effect · environment · interaction<br/>environment = user-mix shift ·DR density ratio· + response drift]
    GATE[★ Overlap gate<br/>ESS/n · effective rewards · mean-weight test<br/>thresholds calibrated on simulation only]
    CERT[★ Certificate<br/>intervals for the difference · MSM bounds · tipping point Γ*]
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

**The identity the system audits** (Shapley over two factors; the two counterfactual cells come from OPE):
naive = V(after, π₁) − V(before, π₀) = policy + environment, where
- policy = ½[(V(before, π₁) − V(before, π₀)) + (V(after, π₁) − V(after, π₀))];
- interaction = (V(after, π₁) − V(after, π₀)) − (V(before, π₁) − V(before, π₀)).

If the gate fails on the logs behind an OPE cell, the verdict is "can't tell from these logs".

Component contracts: [`../architecture/components.md`](../architecture/components.md) · spike rationale: [`../architecture/adr/001-spike.md`](../architecture/adr/001-spike.md).

**Figures** (regenerate with `.venv/bin/python eval/plot_waterfall.py` and `eval/run_decomposer_review.py`):
- Waterfall, simulator S1 (SYNTHETIC, 30 seeds): ![S1 waterfall](figures/S1_drift_masks_gain_waterfall.png)
- Drift sweep (SYNTHETIC): ![drift sweep](figures/drift_sweep.png)
