# Architecture — exact-first cascade tutor (P8)

*The one-page diagram for the Round-1 submission. Component contracts: [`../architecture/components.md`](../architecture/components.md). Numbers are rendered from committed results by `python -m eval.render_docs`.*

**Legend:** solid boxes are **built** (they run in the CLI today); `[benchmarked]` parts were evaluated standalone in `eval/`; `[planned]` parts are not built yet.

```mermaid
flowchart TB
  subgraph Turn["One tutoring turn"]
    A["Learner answers an item"] --> N["Normaliser<br/>exact rational"]
    N --> E{"Stage 1: executable engine<br/>does exactly one known misconception<br/>reproduce this answer?"}
    B["Arithmetic pack (bug switches)<br/>LTR, SQ_DOUBLE, SUB_NEG, FRAC_ADD, NEG×NEG<br/>(probability pack: prototype, stretch)"] --> E
    E -->|"yes: certificate, median {{ph.engine_ms}}, deterministic"| F["Discriminating follow-up<br/>before labelling the learner"]
    E -->|"no: abstain"| L["Stage 2: GPT-5.5, 5 codes + NONE [benchmarked]<br/>real Eedi: 0 false claims on {{real.n_neg}} negatives<br/>(exact 95% upper bound {{real.gpt-5.5.fcr_hi}})"]
    L --> TV["Teacher view<br/>out-of-pack labels [planned]"]
    L -.->|"soft evidence into tracer [planned]"| M
    F --> M["Set-level Bayesian tracer<br/>2^K joint over held misconceptions,<br/>sessions, remission and relapse"]
    M --> P{"Policy"}
    P -->|"uncertain: max expected information gain"| G
    P -->|"confident: targeted practice"| G["Generator (arithmetic)<br/>target fires; requested competitors<br/>give distinct wrong answers"]
    G --> V["Verifier<br/>SymPy key, target fires"]
    V --> Q["Next item + feedback naming the rule"]
    Q --> A
  end
  M --> S[("Learner store")]
  subgraph Eval["Evaluation"]
    E1["Pre-registered: real Eedi ({{real.n_pos}} positives, {{real.n_neg}} negatives); synthetic inversion, tracing, probability keys; cascade routing; consistency"]
    E2["Post hoc, labelled: real-data cascade cost; exact and clustered CIs"]
    E3["Planned: randomised pilot vs a GPT-5.5 tutor"]
  end
```

**Reading the diagram.**
- **Stage 1 (certificate).** A wrong answer is treated as the output of a procedure. When exactly one programmed misconception reproduces it, the system has a *certificate*: "this rule gives this answer". That is not proof of what the learner believes, so it follows up with a discriminating item before labelling.
- **Stage 2 (LLM).** Everything else goes to GPT-5.5. On our real Eedi benchmark it made no false claims, an observation on 152 selected items, not a guarantee.
- **Tracing and practice.** The tracer keeps a posterior over which *combination* of the pack's misconceptions the learner holds. Generated arithmetic practice is verified by SymPy before a learner sees it.
