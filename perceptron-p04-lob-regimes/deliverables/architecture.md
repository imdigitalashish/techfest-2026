# Architecture (optional 1-page diagram for Round 1)

```mermaid
flowchart TB
  subgraph DATA["Market data — receive-time clock"]
    WS["Binance USD-M BTCUSDT · 5-level book<br/>(Tardis replay or live websocket)"]
    CAL["Macro calendar<br/>(FOMC / CPI times, known in advance)"]
  end

  subgraph HOT["Online loop — one step per 1 s tick · target ≤ 50 µs p99 compiled (Python adapter step today: 4.8 µs p50 / 85.6 µs p99, features excluded — target unmet)"]
    F["C2 Causal features<br/>OFI L1 and L1–5 over 1/5/30 s ÷ depth · queue/depth imbalance<br/>micro-price · spread · realised volatility"]
    N["C4 EWMA normaliser<br/>(label-free scale adaptation)"]
    G["C7 Regime gate ⚡<br/>trailing 10-min volatility → 1 of 3 logistic heads<br/>(low / mid / high vol; fitted on training days)"]
    H["C6a Shrinkage trigger ⚡<br/>CUSUM heuristic on raw gated model's delayed (log-loss − ln 2)<br/>alarm → p moved halfway to 0.5 for 5 min (confidence shrinkage, not abstention)"]
    K["C6b Rolling KS — covariate audit only (no action)<br/>5 level-comparable features<br/>empirical leave-one-day-out thresholds (no false-alarm guarantee)"]
    Y["Delayed label y(t − 10 s)<br/>(observable only now)"]
    P(["P(mid up | mid moves within 10 s)"])
  end

  subgraph OFF["Offline — training days only, then frozen"]
    TR["Scalers · regime edges and heads<br/>KS reference + empirical null"]
  end

  subgraph EVAL["C8 Evaluation — pre-registered, prequential, label delay enforced"]
    E1["Log-loss (paired day-cluster bootstrap) · AUC<br/>vs static · textbook KS→retrain · daily retrain · GBDT"]
    E2["Alarms per day · event-window loss<br/>(FOMC times from federalreserve.gov)"]
    E3["Edge in bps: taker at +100 ms<br/>maker upper bound · official Binance fees"]
    E4["C9 latency p50 / p99 per step"]
  end

  WS --> F --> N --> G --> H --> P
  F --> K
  CAL -.-> K
  Y -- "loss of the raw gated forecast" --> H
  TR -.-> N & G & K
  P --> E1 & E3
  K --> E2
  H --> E2
  G --> E4
```

**Reading the diagram.**
- Every arrow is a typed contract (`components/contracts.py`).
- The label for step *t* reaches the CUSUM only at *t* + 10 s, when it would be observed live.
- **The regime gate (⚡) is what improves forecasts.** It beats one head on the same EWMA features by −0.0083 on held-out log-loss, better on 22/22 days (post-hoc ablation).
- **The CUSUM shrinkage trigger** makes forecasts less confident while the raw model is losing more than a coin flip. On average it costs +0.0006, and any benefit during events is unproven.
- **The rolling KS** is a label-free audit trail. It never changes a forecast.
- **What we rejected.** Refitting on post-alarm windows (KS→refit) made held-out loss worse on 21/22 days. A Fixed-Share mixture of online experts did not beat static. Both remain baselines and ablations (`eval/results/v2_holdout.md`). The dashed calendar prior is planned.

**Illustrative replay of a FOMC day (dev split, 2024-05-01; gate-only curve shown for attribution):** ![FOMC day](figures/day_2024-05-01.png)
