# Architecture — "Find the rule you're actually using"

*One page for the Round-1 submission (optional diagram). Component contracts: [`../architecture/components.md`](../architecture/components.md).*

```mermaid
flowchart TB
  subgraph Session["One tutoring turn (< 0.5 s on a laptop)"]
    A["Learner answers item\n'1/8 + 1/8 = 1/8'"] --> N["Normaliser\nexact rational"]
    N --> D{"Diagnoser\nP(misconception set | answer)"}
    B["Bug library\nexecutable misconceptions\n(LTR, SQ_DOUBLE, SUB_NEG, FRAC_ADD, NEG×NEG, …)"] -->|"predicted wrong answer\nfor every bug and bug-set"| D
    R["Open-set retrieval + LLM rerank\nEedi catalogue (2,587 / 8,117)"] -->|"when no bug explains it"| D
    D -->|"posterior + slip / abstain"| M["Set-level Bayesian tracer\n2^K joint, sessions, relapse"]
    M --> P{"Policy"}
    P -->|"uncertain: max expected info gain"| G
    P -->|"confident: remediate top misconception"| G["Generator\nparameter search: target fires,\ncompetitors give distinct answers"]
    G --> V["Verifier\nSymPy key, target fires,\npairwise-distinct distractors"]
    V -->|"verified item"| Q["Next item + feedback naming the rule\n'that is what adding tops and bottoms gives'"]
    Q --> A
  end
  C1[("Eedi Misconceptions Graph\nCC BY 4.0")] --> B
  C1 --> R
  BC["LLM bug compiler (stretch)\nmisconception text → bug program"] -->|"accepted only if it reproduces\nreal Eedi distractors"| B
  M --> S[("Learner store\nacross sessions")]
  M --> T["Teacher view\nmisconception heat-map"]
  subgraph Eval["Evaluation harness"]
    E1["Real: Eedi 2024 distractors\nclosed-set acc, MAP@25"]
    E2["Generation: verified-targeted yield\nours vs LLM-only"]
    E3["Simulated learners (labelled synthetic)\n2×2 factorial + oracle"]
    E4["Pilot: pre/post isomorphic items\nvs random-practice control"]
  end
```

**Reading the diagram.** A wrong answer is treated as the *output of a procedure*. Every misconception in the library is an executable change to one rule of an exact interpreter, so the system knows exactly which wrong answer each misconception, or each *combination* of them, produces. Diagnosis is Bayesian inversion of those programs, with an explicit "just a slip" hypothesis. The next item is either the most informative one (while uncertain) or a targeted practice item (once confident). Each item is generated so the target misconception fires and competing misconceptions give *different* wrong answers. It is then checked independently by SymPy before any learner sees it.
