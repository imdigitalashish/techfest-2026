# Architecture — Recall-on-Demand (one-page diagram for the Round-1 abstract)

```mermaid
flowchart TB
  subgraph Prefill["Once per document / chat history (query-agnostic)"]
    D[Long context: token ids] --> P[Prefill: frozen Llama-3.2-1B-Instruct]
    P --> R[(Resident KV<br/>4 sinks + recent window<br/>half of the KV budget)]
    P --> X[(Sketch: 4-bit keys of layer 5<br/>288 B/token = 0.88% of KV)]
    P --> W[(Context-window queries<br/>last 64 tokens, layer 5: 256 KiB)]
    D --> I[(Backing store: int32 token ids<br/>4 B/token)]
  end
  subgraph Ask["Per question (any time later; not seen at compression)"]
    Q[Question] --> QP[Run the question on the resident KV;<br/>take its own layer-5 queries]
    R --> QP
    QP --> M[softmax_lift: question attention over the sketch<br/>minus the context window's attention<br/>-> score evicted 64-token blocks]
    X --> M
    W --> M
    M --> RP[Re-prefill the top blocks from token ids<br/>at their original positions, attending to sinks + block]
    I --> RP
    RP --> A[Answer over resident + recalled KV]
    R --> A
    A --> F[Drop recalled KV: steady state = resident + sketch + ids]
  end
  subgraph Eval["Evaluation (eval/kvbench_torch.py, pre-registered in eval/PREREG.md)"]
    E1[RULER-style needles in WikiText-103; literal / paraphrased / synonym-aliased keys] --> E2[Same 4 questions per context to every method, paired]
    E2 --> E3[Recall, context-bootstrap 95% CIs, paired deltas]
    E2 --> E4[Every stored byte counted; RoD's extras charged to its own KV budget]
    E2 --> E5[Baselines: StreamingLLM, H2O, SnapKV, K-norm, int8/4/2, and NVIDIA kvpress reference presses]
  end
```

| Tier | What it holds | Bytes (Llama-3.2-1B, fp16 KV) | Lifetime |
|---|---|---|---|
| Full cache (baseline) | K, V for every layer and head | 32,768 per token | whole chat |
| Resident (ours) | K, V for 4 sinks + the most recent tokens | 32,768 × resident tokens | whole chat |
| Sketch (ours) | 4-bit keys of layer 5, 8 KV heads, group-64 fp16 scale + bias | 288 per token | whole chat |
| Window queries (ours) | layer-5 queries of the context's last 64 tokens (32 heads × 64 dims, fp16) | 262,144 per context | whole chat |
| Backing store (ours) | int32 token ids | 4 per token | whole chat |
| Recalled (ours) | re-prefilled K, V of the chosen blocks | 32,768 × recalled tokens | one answer |

Byte figures are analytic from the model config and equal the retained tensors' bytes (asserted in the harness). RoD's sketch, window queries and ids are charged to its own KV budget, so its answer-time bytes never exceed a baseline's at the same keep fraction. Measured results: [`../eval/RESULTS.md`](../eval/RESULTS.md).
