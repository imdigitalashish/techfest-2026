# Architecture — Recall-on-Demand (one-page diagram for the Round-1 abstract)

```mermaid
flowchart TB
  subgraph Prefill["Once per document / chat history"]
    D[Long context tokens] --> P[Prefill: frozen Llama-3.2-1B, MLX]
    P --> S[Score tokens: StreamingLLM sinks+recent or SnapKV]
    S --> R[(Resident KV<br/>~10% of tokens, fp16 or 4-bit)]
    P --> X[(Index: 2-bit keys of 1 layer<br/>~160 B/token = 0.5%)]
    D --> I[(Backing store: token IDs<br/>4 B/token)]
  end
  subgraph Ask["Per question (may arrive any time later)"]
    Q[Question] --> QP[Run question on resident KV<br/>take its own attention queries]
    R --> QP
    QP --> M[Match queries against the 2-bit index<br/>score evicted 64-token blocks]
    X --> M
    M --> RP[Re-prefill top blocks from token IDs<br/>at original positions]
    I --> RP
    RP --> A[Answer over resident + recalled KV]
    R --> A
    A --> F[Drop recalled KV: steady state = resident only]
  end
  subgraph Eval["Evaluation harness (eval/kvbench.py)"]
    E1[RULER-style multi-needle tasks, WikiText-103 text] --> E2[Same 4 questions to every method, paired]
    E2 --> E3[Recall accuracy, Wilson 95% CI]
    E2 --> E4[Every byte counted: KV + scales + sketch + IDs; peak memory; latency]
  end
```

| Tier | What it holds | Bytes/token (Llama-3.2-1B) | Lifetime |
|---|---|---|---|
| Full cache (baseline) | K,V for every layer and head, fp16 | 32,768 | whole chat |
| Resident (ours) | K,V for the kept tokens | 32,768 × keep fraction | whole chat |
| Index (ours) | 2-bit keys, 1 layer, 8 KV heads, group-64 scales | ≈ 160 | whole chat |
| Backing store (ours) | token IDs | 4 | whole chat |
| Recalled (ours) | re-prefilled K,V of chosen blocks | 32,768 × recalled tokens | one answer |

Byte figures are analytic from the model config ([`research/landscape.md` §1](../research/landscape.md)); measured numbers will come from `eval/results/`.
