# Architecture (optional 1-page diagram for Round 1)

```mermaid
flowchart TB
  subgraph SIM["Reactive market: ABIDES rmsc04 (1 exchange + 1,117 agents)"]
    direction LR
    W1["World A: with our agent<br/>(treatment)"]
    W0["World B: null agent<br/>(counterfactual twin)"]
  end
  SEED["Same seed + synchronised random streams<br/>(re-keyed per agent wake-up)"] --> W1 & W0

  subgraph AGENT["Impact-aware execution agent (deployable: observables only)"]
    direction TB
    OBS["Book snapshot + own fills"] --> GB["Ghost-book estimator<br/>Î(t) = Σ qᵢ·G(t−tᵢ); ghost mid = mid − Î"]
    GB --> SCH["Schedule: transient-impact QP<br/>+ slow down while Î above steady state"]
    SCH --> TAC["Child orders: take ≤ touch,<br/>post the remainder, forced completion"]
  end
  W1 <-->|"orders / fills / quotes"| AGENT

  W1 & W0 --> TCA["TCA: IS = drift + own impact + instantaneous<br/>(exact per seed)"]
  W1 & W0 --> FB["Feedback analysis: who absorbed our order,<br/>MM spread/depth response, impulse response"]
  W0 -. "ground-truth labels (train seeds)" .-> GB
  TCA --> EV["Evaluation: paired ΔIS vs TWAP/VWAP/AC<br/>95% bootstrap CI, CVaR, held-out test seeds"]
  FB --> EV
  EV --> AR["Autoresearch ratchet<br/>(frozen eval; keep only significant gains)"]
  AR --> AGENT
```

**Reading it:** both worlds start bit-identical. Every difference between them is caused by our orders, which yields the exact counterfactual book (stretch goal 1) and per-agent-type feedback (stretch goal 2). The agent itself never sees World B. It learns an estimator of it from training seeds, so the same agent could run on a live venue.
