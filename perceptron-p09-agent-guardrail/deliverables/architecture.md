# Architecture (one page) — Cite-Before-Act

Companion diagram for the Round-1 abstract. Detailed component contracts: [`../architecture/components.md`](../architecture/components.md).

```mermaid
flowchart TB
  user([Client request]) --> agent[LangGraph agent<br/>local Qwen3 via MLX]
  agent -- "proposed tool call<br/>(tool, args)" --> hook{{Pre-tool hook<br/>every write call}}
  obs[(Trust-labelled context<br/>user words · tool data · untrusted text)] --> hook
  hook --> t0

  subgraph guard [Guard — runs before execution]
    t0["Tier 0 · deterministic, ≤5 ms<br/>• provenance of each argument<br/>• pre-trade contracts: collar, size, cash, short-sale,<br/>  restricted list, duplicates, approvals"]
    kb[("Reference KB<br/>instrument master · accounts · limits<br/>restricted list · numbered policy")] --> t0
    t0 -- "unverifiable residue" --> route{"Risk router<br/>reversibility × value at stake"}
    route -- "low risk" --> fast["Tier 1 · fast model<br/>Qwen3-1.7B"]
    route -- "high risk" --> careful["Tier 2 · careful model<br/>Qwen3-8B"]
    fast --> qv["Quote verifier<br/>model's evidence must match the source verbatim"]
    careful --> qv
  end

  t0 -- "all pass" --> allow([ALLOW → execute])
  t0 -- "contradicted / violation" --> block([BLOCK → feedback to agent → repair])
  qv -- "supported" --> allow
  qv -- "contradicted" --> block
  qv -- "still unverifiable" --> human([ESCALATE → human via interrupt])
  t0 -- "needs approval (policy)" --> human
  block -. "repaired call" .-> agent
```

**Evaluation loop:** red-team mutation suite (11 hallucination classes, dev/test split by phrasing family) and τ-bench log replay → guard → catch rate, false-block rate, escalation rate, latency p50/p95. Baselines: none, schema-only, LLM-as-judge.
