```mermaid
flowchart TB
  subgraph Devices["Devices: data never leaves them; one Flower ClientApp per device"]
    direction LR
    D0["c0 workstation<br/>8× data · rank 16 · 16 steps"]
    D1["c1 laptop<br/>rank 8 · 8 steps"]
    D2["c2 phone<br/>rank 4 · 4 steps"]
    D3["c3 Raspberry Pi<br/>rank 2 · 2 steps"]
    D4["c4 tablet<br/>rank 4 · 4 steps · outage"]
  end
  subgraph Local["On each device (C4 local trainer)"]
    direction TB
    M["Frozen base LLM<br/>SmolLM2-135M → Qwen2.5-0.5B / TinyLlama-1.1B"]
    A["Shared anchor A (r_max × d)<br/>regenerated from a public seed, never sent"]
    B["Trainable B[:, :r_k] only<br/>(rank fits the device's memory)"]
    M --- A --- B
  end
  subgraph Server["Server (Flower ServerApp + custom strategy) — C6 AnchorLoRA aggregator"]
    direction TB
    N["① FedNova step normalisation<br/>(partial work from deadline cut-offs is kept)"]
    W["② Macro weights + median-norm clip<br/>(no device can dominate)"]
    MEM["③ Memory of absent devices ≤ 4 rounds<br/>(dropouts don't bias the objective)"]
    AGG["④ Exact aggregation: B ← B + Σ_k w_k ΔB_k<br/>(Σ w_k ΔB_k·A is exact for any rank mix)"]
    AUD["⑤ Influence audit in ΔW space<br/>(share s_k per device per round)"]
    N --> W --> MEM --> AGG --> AUD
  end
  Devices -->|"ΔB_k: r_k·d_out floats per layer + steps done"| Server
  Server -->|"global B (+ seed)"| Devices
  subgraph Eval["C9 evaluator + harness"]
    E["Held-out loss per domain → macro, worst, weak-device gain<br/>dominance index · aggregation error · loss spikes · bytes · memory"]
  end
  Server --> Eval
  SIM["C2 device simulator: seeded offline rounds, deadline cut-offs, mid-run outage<br/>(identical schedule for every strategy → paired comparison)"] -.-> Devices
```

**Reading the diagram.** Every device runs the full global adapter but trains only as many columns of B as its memory allows. A is identical everywhere (regenerated from a seed), so the server's sum of B-updates is exactly the sum of the devices' weight updates ΔW_k = ΔB_k·A. Steps ①–③ are classic federated-optimisation corrections that become exact for LoRA because of this, and ⑤ makes "quiet domination" visible every round. The baselines in the evaluation swap the server box for FedAvg over A and B (the starter), HetLoRA-style zero-padding, FFA-LoRA, exact ΔW averaging + SVD (FlexLoRA-style), FedEx-LoRA and RoLoRA.
