# Architecture — Did-It-Work (optional 1-page diagram for Round 1)

```mermaid
flowchart TB
  subgraph IN[Inputs]
    L0[Before-period logs<br/>old policy π₀ · x, a, r, propensity]
    L1[After-period logs<br/>new policy π₁ · x, a, r, propensity]
    P[Policy definitions π₀, π₁<br/>scorer / ε-greedy / Thompson priors]
  end
  subgraph CORE[Estimation core — best practice]
    PA[Policy adapter<br/>π(a·x) on logged contexts]
    RM[Cross-fitted reward model q̂(x,a)]
    EST[OPE estimators<br/>IPW · SNIPW · DM · DR · Switch-DR<br/>→ per-round influence terms]
    DLT[Δ-estimator<br/>V(π₁) − V(π₀), shared control variates]
  end
  subgraph SPIKE[Spikes]
    DEC[★ Decomposer<br/>naive = policy effect + mix shift + response drift]
    CERT[★ Robustness certificate<br/>CI / anytime-valid CS · MSM bounds · tipping point Γ*]
  end
  REP[Verdict: worked / hurt / inconclusive<br/>waterfall · intervals · ESS & max-weight diagnostics]
  subgraph EVAL[Evaluation — every number checked against truth]
    SIM[Ground-truth simulator<br/>drift · mix · overlap · hidden override]
    OBD[Open Bandit Dataset<br/>Random logs → BTS on-policy truth]
    BANK[Frozen scenario bank + held-out bank<br/>RMSE · sign accuracy · coverage · bound validity]
  end
  L0 & L1 --> RM & EST
  P --> PA --> EST & DLT
  RM --> EST --> DLT
  DLT --> DEC & CERT
  L0 --> DEC
  DEC & CERT --> REP
  SIM --> L0 & L1
  SIM -. exact counterfactuals .-> BANK
  OBD -.-> BANK
  REP --> BANK
```

**The identity the system audits.**
naive gap = Ȳ_after − Ȳ_before = **[Ȳ_after − V̂_after(π₀)]** (policy effect: OPE, with CI) + **[V̂_after(π₀) − Ȳ_before]** (environment change), where environment change = user-mix shift + response drift.

Component contracts: [`../architecture/components.md`](../architecture/components.md) · spike rationale: [`../architecture/adr/001-spike.md`](../architecture/adr/001-spike.md).
