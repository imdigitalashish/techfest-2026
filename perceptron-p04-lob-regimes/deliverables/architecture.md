# Architecture (optional 1-page diagram for Round 1)

```mermaid
flowchart TB
  subgraph DATA["Market data (receive-time clock)"]
    WS["Binance USD-M BTCUSDT<br/>5-level book + trades<br/>(Tardis archive replay / live websocket)"]
    CAL["Macro calendar<br/>(FOMC/CPI release times,<br/>known in advance)"]
  end

  subgraph HOT["Online loop — one step per 1 s tick, budget ≤ 50 µs p99 (compiled)"]
    F["C2 Causal features<br/>OFI L1 & L1-5 (1/5/30 s, ÷ depth)<br/>queue/depth imbalance · micro-price<br/>spread · realised vol · msg rate"]
    N["C4 EWMA normaliser<br/>(label-free scale adaptation)"]
    H["C5 Heads<br/>static · online SGD (fast/slow)<br/>periodic refit · regime heads<br/>(low / mid / high volatility)"]
    M["C7 Fixed-Share mixer<br/>weights ∝ exp(−η·delayed loss)<br/>switch rate α ↑ on confirmed alarm"]
    S["C6 Shift monitor ⚡<br/>① rolling KS, empirical-null thresholds<br/>② CUSUM / e-detector on delayed loss (harm gate)<br/>③ calendar prior"]
    P(["P(mid up in 10 s)"])
  end

  subgraph OFF["Offline (train days only — frozen)"]
    TR["Fit scalers, heads per regime,<br/>KS reference + leave-one-day-out null"]
  end

  subgraph EVAL["C8 Evaluation (prequential, label delay enforced)"]
    E1["log-loss · AUC · edge bps vs spread+fees<br/>block-bootstrap CI · Diebold–Mariano"]
    E2["false alarms / calm day @ fixed delay<br/>(FOMC timestamps, spliced streams)"]
    E3["C9 latency p50/p99/p99.9"]
  end

  WS --> F --> N --> H --> M --> P
  F --> S
  CAL --> S
  M -- "delayed loss ℓ(t−h)" --> S
  S -- "Alarm" --> M
  TR -.-> N & H & S
  P --> E1
  S --> E2
  M --> E3
```

**Reading the diagram.** Every arrow is a typed contract (`components/contracts.py`). The label for step *t* reaches the mixer and the harm gate only at *t + h*, which is when it would be observed live. The two ⚡ components are the spikes: the shift monitor decides *whether* the world changed in a way that hurts, and the mixer decides *how much* to trust each regime head. Neither ever refits on a tiny post-shift window; on our data that hurt (+0.020 held-out log-loss for KS→refit).
