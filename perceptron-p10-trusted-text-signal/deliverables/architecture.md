# P10 architecture — one page (optional diagram for the Round 1 abstract)

```mermaid
flowchart TB
  subgraph Inputs
    T["Posts / news<br/>(StockNet tweets · Kaggle DJIA headlines · FNSPID for finals)"]
    P["Daily prices (OHLCV)"]
    A["Attacker<br/>injects ≤ k posts per stock-day"]
  end
  A -.-> T
  T --> AL["Align to the 16:00 ET close<br/>look-ahead leaks = 0 (tested)"]
  AL --> SC["Text scorer<br/>frozen MiniLM-L6 + sentiment head<br/>(never sees returns)"]
  SC --> TR["Trust from the post's own account<br/>(deletion-stable)"]
  TR --> AG["Bounded-influence aggregator<br/>count · mean · trimmed mean · dispersion · trust"]
  P --> TS["Price features<br/>lags · realised vol · range · volume · market"]
  AG --> FU["Fusion: LightGBM quantiles<br/>5% · 50% · 95%"]
  TS --> FU
  FU --> CP["Minimum Viable: MAPIE<br/>split conformal · CQR"]
  FU --> ACI["ACI (own loop)<br/>long-run coverage under drift"]
  TR --> BOX["Deletion box B_k<br/>exact per-feature ranges"]
  BOX --> PROP["Interval propagation<br/>through every tree"]
  FU --> PROP
  PROP --> CR["SPIKE · CR-ACI<br/>[LB − q_t, UB + q_t]"]
  ACI --> CR
  CP --> EV
  CR --> EV["Frozen evaluator<br/>coverage · width · Winkler · Kupiec · Christoffersen<br/>day-clustered CIs · regimes · clean vs attacked · k = 0…5"]
  EV --> GATE["Text gate (pre-registered test)<br/>admit text only if it earns its certified width;<br/>otherwise use the separate price-only model"]
  GATE --> UI["Demo: band per stock-day,<br/>attack toggle, k slider,<br/>'which posts could flip this?'"]
```

**Guarantee in one line:** if at most k of a stock-day's posts are injected, the clean features lie in the deletion box, so *at a fixed offset* the certified interval contains the interval the clean model would have produced — an attacker within budget cannot add misses. ACI separately keeps long-run mean daily coverage near 1 − α under drift; separately adapted clean and attacked ACI runs need not be nested.

**Measured trade-off:** what the text channel buys (pre-registered test on unseen data) against what it costs (certified width at budget k). Results: `eval/results/text_minilm_v1.md`, `eval/results/text_utility_djia_v1.md`.
