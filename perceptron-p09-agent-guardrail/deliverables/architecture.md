# Architecture (one page) — Cite-Before-Act

Companion diagram for the Round-1 abstract. Component contracts: [`../architecture/components.md`](../architecture/components.md). Evaluation protocol: [`../eval/taubench/README.md`](../eval/taubench/README.md).

```mermaid
flowchart TB
  user([User request]) --> agent[LangGraph agent<br/>local Qwen3 via MLX]
  agent -- "proposed write call<br/>(tool, args)" --> hook{{Pre-tool hook<br/>every write call}}
  ctx[(Trust-labelled context<br/>user words · tool data · untrusted text)] --> hook
  hook --> t0

  subgraph guard [Guard — runs before execution]
    t0["Tier 0 · deterministic, ~0.2 ms<br/>• provenance of each argument<br/>• pre-trade contracts: collar, size, cash, short-sale,<br/>  restricted list, duplicates, ownership, approvals"]
    kb[("Reference data<br/>instruments · accounts · orders<br/>limits · restricted list · numbered policy")] --> t0
    t0 -- "unverifiable residue only" --> route{"Risk router<br/>reversibility × value at stake"}
    route -- "low risk" --> fast["Tier 1 · Qwen3-1.7B"]
    route -- "high risk" --> careful["Tier 2 · Qwen3-8B"]
    fast --> qv["Quote verifier<br/>quote must match user words / tool data verbatim;<br/>a bare 'yes' never counts"]
    careful --> qv
  end

  t0 -- "all pass" --> allow([ALLOW → execute])
  t0 -- "contradicted / violation" --> block([BLOCK → failed checks to agent → repair])
  qv -- "supported" --> allow
  qv -- "contradicted" --> block
  qv -- "still unverifiable" --> human([ESCALATE → human via interrupt])
  t0 -- "needs approval (policy)" --> human
  block -. "repaired call" .-> agent
```

```mermaid
flowchart LR
  subgraph eval [Evaluation]
    tb["τ-bench replay<br/>2,018 real write calls (gpt-4o, Claude-3.5-Sonnet)<br/>labels: DB effect vs ground truth<br/>dev/test split by task"] --> m
    rt["Independent red team<br/>160 cases by a different model family"] --> m
    sy["Synthetic mutation suite<br/>(self-authored, secondary)"] --> m
    m["Metrics · catch on harmful calls · false-block and escalation on good calls<br/>· latency p50/p95 · 95% CIs clustered by task"]
    m --> base["Baselines: no guard · schema-only · LLM judge (same transcript)"]
  end
```

**Operating points** (like a desk's hard blocks vs soft alerts vs manual review): `v0` (catch first), `strict`, `balanced` (primary) and `lenient` (fewest escalations) trade harmful-call catch against human load on good calls. All four were chosen on dev and tested once on held-out tasks.
