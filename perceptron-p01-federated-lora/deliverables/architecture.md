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
    A["Shared anchor A (r_max × d)<br/>regenerated from a public seed<br/>(design target; the pilot Flower adapter still ships A)"]
    B["Trainable B[:, :r_k] only<br/>(active columns and uplink ∝ r_k;<br/>RAM/throughput not yet measured)"]
    M --- A --- B
  end
  subgraph Server["Server (Flower ServerApp + custom strategy) — C6 AnchorLoRA aggregator"]
    direction TB
    N["① FedNova step normalisation<br/>(partial work from deadline cut-offs is kept)"]
    W["② Macro weights + median-norm clip<br/>(caps any one device's weight)"]
    MEM["③ Memory of absent devices ≤ 4 rounds<br/>(reduces dropout bias toward always-on devices)"]
    AGG["④ Exact aggregation: B ← B + Σ_k w_k ΔB_k<br/>(Σ w_k ΔB_k·A is exact for any rank mix)"]
    AUD["⑤ Influence audit in ΔW space<br/>(projection + bounded norm share per device per round)"]
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

**Reading the diagram.** Every device runs the full global adapter but trains only as many columns of B as its memory allows. A is identical everywhere (regenerated from a seed), so the server's sum of zero-padded B-updates exactly reproduces the corresponding weight-space sum. This is an identity for the directions we choose; it is not a guarantee of unbiased averaging or convergence. Steps ①–③ are classic federated-optimisation corrections; sharing A removes the factorisation error underneath them (they keep their own assumptions, which the ablations test). ⑤ makes "quiet domination" a number every round. The evaluation swaps the server box for the baselines. Implemented baselines include the starter, FFA-LoRA, FlexLoRA and HetLoRA-style padding. The current paired sample sizes and completed scenarios are those in the generated results table (`eval/results/v2_summary.md`). Planned for the finals: FedEx-LoRA, PreLort and RoLoRA.
