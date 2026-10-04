# Architecture — exact-first cascade tutor (P8)

*The one-page diagram for the Round-1 submission. Component contracts: [`../architecture/components.md`](../architecture/components.md). Numbers are rendered from committed results by `python -m eval.render_docs`.*

```mermaid
flowchart TB
  subgraph Turn["One tutoring turn"]
    A["Learner answers an item"] --> N["Normaliser<br/>exact rational"]
    N --> E{"Stage 1 — executable engine<br/>does exactly one known misconception<br/>reproduce this answer?"}
    B["Misconception packs (bug switches)<br/>arithmetic: LTR, SQ_DOUBLE, SUB_NEG, FRAC_ADD, NEG×NEG<br/>probability: EQUIPROB, INDEP, ADD_PROB, INVERSE, JENSEN"] --> E
    E -->|"yes: name it with exact evidence<br/>{{cons.engine_ms}}, deterministic, no cost"| D["Diagnosis + posterior"]
    E -->|"no: abstain"| L["Stage 2 — frontier LLM (GPT-5.5)<br/>5 codes + NONE, catalogue retrieval<br/>real data: {{real.gpt-5.5.fcr}} false claims"]
    L --> D
    D --> M["Set-level Bayesian tracer<br/>2^K joint over held misconceptions,<br/>sessions, remission and relapse"]
    M --> P{"Policy"}
    P -->|"uncertain: max expected information gain"| G
    P -->|"confident: targeted practice"| G["Generator<br/>target fires; competitors give<br/>pairwise-distinct wrong answers"]
    G --> V["Verifier<br/>SymPy key, target fires, distractors distinct"]
    V --> Q["Next item + feedback naming the rule"]
    Q --> A
  end
  C1[("Eedi Misconceptions Graph<br/>CC BY 4.0")] --> L
  M --> S[("Learner store")]
  M --> T["Teacher view: misconception heat-map"]
  subgraph Eval["Pre-registered evaluation (eval/llm_gap_protocol.md)"]
    E1["Real Eedi: {{real.n_pos}} positives, {{real.n_neg}} same-domain negatives<br/>vs GPT-4.1-mini, GPT-5.4-mini, GPT-5.5"]
    E2["Synthetic inversion, tracing, probability keys"]
    E3["Cascade: LLM calls, cost, latency per 1,000; consistency"]
    E4["Learning: simulation, then a consented pilot"]
  end
```

**Reading the diagram.** A wrong answer is treated as the output of a procedure.
- **Stage 1.** Every misconception in a pack is an executable change to one rule of an exact interpreter. So when one of them reproduces the learner's answer, the system can say so with proof, instantly and identically every time.
- **Stage 2.** Everything else goes to a frontier LLM. On real Eedi data GPT-5.5 made no false claims on same-domain negatives, so it is a safe second stage.
- **Tracing and practice.** The tracer keeps a posterior over which *combination* of misconceptions the learner holds. Generated practice is built so that the targeted misconception and its competitors give different wrong answers, and SymPy verifies every key before a learner sees it.
