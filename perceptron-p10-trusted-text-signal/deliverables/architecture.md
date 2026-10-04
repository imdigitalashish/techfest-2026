# P10 architecture — one page (optional diagram for the Round 1 abstract)

```mermaid
flowchart TB
  subgraph Inputs
    T["Tweets / news<br/>(StockNet now · FNSPID finals)"]
    P["Daily prices<br/>(OHLCV)"]
    A["Attacker<br/>injects ≤ k posts per ticker-day"]
  end
  A -.-> T
  T --> AL["Align to 16:00 ET close<br/>look-ahead leaks = 0"]
  AL --> SC["Text scorer<br/>VADER → FinBERT"]
  SC --> TR["Trust scorer<br/>age · followers · copy-paste · spam"]
  TR --> AG["Bounded-influence aggregator<br/>count · mean · trimmed mean · std · trust"]
  P --> TS["Price features<br/>lags · realised vol · Parkinson · volume · market"]
  AG --> FU["Fusion model<br/>LightGBM quantiles 5% · 50% · 95%"]
  TS --> FU
  FU --> CP["Minimum Viable: MAPIE<br/>split CP · CQR"]
  FU --> ACI["Adaptive Conformal Inference<br/>(drift)"]
  TR --> BOX["Deletion box B_k<br/>exact per-feature ranges"]
  BOX --> PROP["Interval propagation<br/>through every tree"]
  FU --> PROP
  PROP --> CR["SPIKE · CR-ACI interval<br/>[LB − q_t, UB + q_t]"]
  ACI --> CR
  CP --> EV
  CR --> EV["Frozen evaluator<br/>coverage · width · Winkler · Kupiec · Christoffersen<br/>by regime · clean vs attacked · k = 0…5"]
  EV --> UI["Demo: band per stock-day,<br/>attack toggle, k slider, 'which posts could flip this?'"]
```

**Guarantee in one line:** if at most k of a ticker-day's documents are injected, the clean feature vector lies in the deletion box, so the CR-ACI interval contains the interval the clean model would have produced; ACI keeps long-run coverage at 1 − α under drift.
