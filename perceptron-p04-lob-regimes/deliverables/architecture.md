# Architecture (optional 1-page diagram for Round 1)

```mermaid
flowchart TB
  subgraph DATA["Market data — receive-time clock"]
    WS["Binance USD-M BTCUSDT · 5-level book<br/>(Tardis replay or live websocket)"]
    CAL["Macro calendar<br/>(FOMC / CPI times, known in advance)"]
  end

  subgraph HOT["Online loop — one step per 1 s tick · budget ≤ 50 µs p99 compiled (Python reference: 4.8 µs p50)"]
    F["C2 Causal features<br/>OFI L1 and L1–5 over 1/5/30 s ÷ depth · queue/depth imbalance<br/>micro-price · spread · realised volatility"]
    N["C4 EWMA normaliser<br/>(label-free scale adaptation)"]
    G["C7 Regime gate ⚡<br/>trailing 10-min volatility → 1 of 3 logistic heads<br/>(low / mid / high vol; fitted on training days)"]
    H["C6a Harm gate ⚡<br/>CUSUM of delayed (log-loss − ln 2)<br/>alarm → shrink p toward 0.5 for 5 min"]
    K["C6b Calibrated rolling KS ⚡ (audit)<br/>5 level-comparable features<br/>empirical leave-one-day-out null"]
    Y["Delayed label y(t − 10 s)<br/>(observable only now)"]
    P(["P(mid up in 10 s)"])
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
- **Typed contracts.** Every arrow is a typed contract (`components/contracts.py`).
- **Label delay.** The label for step *t* reaches the harm gate only at *t* + 10 s, when it would be observed live.
- **The spike components (⚡):**
  - the **regime gate** decides *which* model applies to the current state, conditioning on the variable the theory names (volatility);
  - the **harm gate** decides *whether to trust it right now*: it abstains while the model is demonstrably worse than a coin flip;
  - the **calibrated KS** is the label-free audit trail of covariate shift.
- **What we rejected.** Refitting on tiny post-alarm windows (textbook KS→retrain) made held-out log-loss worse on 21 of 22 days. Mixing many online experts (Fixed-Share) did not beat a static model. Both remain in the code as baselines and ablations (`eval/results/v2_holdout.md`).
- **Not drawn yet.** The calendar prior (dashed) is planned and not built yet.

**Replay of a FOMC day (dev split, 2024-05-01):** ![FOMC day](figures/day_2024-05-01.png)
