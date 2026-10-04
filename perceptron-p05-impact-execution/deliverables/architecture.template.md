# Architecture (1-page diagram for Round 1)

Status tags: **[built]** code exists · **[evaluated]** measured in committed runs · **[unresolved]** measured but not yet working · **[planned]**. Numbers on this page are rendered from `eval/results/` (`eval/render_docs.py`, checked by `eval/check_docs.py`).

```mermaid
flowchart TB
  subgraph SIM["Reactive market [built]: ABIDES rmsc04, 1 exchange + {{n_trading_agents}} trading agents, 35-min session"]
    direction LR
    W1["World A: our execution agent<br/>(treatment)"]
    W0["World B: null agent, no orders<br/>(counterfactual twin)"]
  end
  SEED["Same seed; random streams re-keyed per agent wake-up<br/>(common-random-numbers coupling) [evaluated]"] --> W1 & W0

  subgraph AGENT["Execution agent: sees only its own fills and the book"]
    direction TB
    OBS["Book snapshot + own fills"] --> CF["Counterfactual-mid estimator [unresolved]<br/>Î(t) = Σ qᵢ·G(t−tᵢ); SELL: no-order mid ≈ observed mid + Î"]
    CF --> SCH["Schedule [built]: propagator-QP<br/>(+ front-loading variant)"]
    SCH --> TAC["Child orders [built]: market or touch-capped;<br/>forced completion at the deadline"]
  end
  W1 <-->|"orders / fills / quotes"| AGENT

  W1 & W0 --> TCA["Cost accounting [evaluated]: IS = drift + own impact (twin − ours)<br/>+ cost vs decision mid (= delay + at-fill cost)"]
  W1 & W0 --> FB["Inventory redistribution by agent type [evaluated, descriptive];<br/>response paths and ablations [planned]"]
  W0 -. "training targets (train seeds)" .-> CF
  TCA --> EV["Evaluation [evaluated]: paired ΔIS vs TWAP / VWAP / front-loaded TWAP,<br/>pre-registered fixed-n blocks + replication"]
  SC["Realism scorecard [evaluated]: impact-vs-size slope, permanence,<br/>market statistics; recalibration gate [planned]"] --> EV
  FB --> EV
  EV --> AR["Policy search [planned]: paired candidate vs incumbent,<br/>untouched confirmation seeds; PPO deferred"]
  AR --> AGENT
```

**Reading it:** both worlds share a seed and a random-number coupling; their pre-trade top-of-book logs match exactly. Afterwards, differences between them measure our footprint *within this simulator under the coupling*, which itself widens spreads (E11). The agent never sees World B; the estimator that is meant to stand in for it live has not yet passed its held-out test.
