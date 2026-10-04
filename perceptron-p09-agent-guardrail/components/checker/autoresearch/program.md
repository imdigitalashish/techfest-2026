# Ratchet loop — Tier-0 checker + resolver (spike S1)

Adapted from karpathy/autoresearch: edit → run the frozen evaluator → keep only if the scalar improves and nothing regresses → log every attempt in `results.tsv`.

## Goal
Raise the **dev score** `catch − false_block − 0.5·escalation` of guard `t0` (later `cascade`). Hard constraints: test-split catch must not drop, test false-block must not rise, p95 latency ≤ 5 ms for Tier 0.

## Rules
- Only `components/checker/*.py` may change. `eval/run_eval.py`, `components/redteam/`, `eval/data/suite.jsonl` and this `eval.py` are **frozen** during a loop.
- Contract tests must pass (`python -m pytest`).
- The evaluator is deterministic for `t0` (no seeds needed). LLM tiers need ≥3 seeds or a fixed decode; we use greedy decoding.
- **Anti-gaming:**
  - Dev phrasing families are visible to the editor. A gain that comes only from lexicon entries copied from a dev template is logged as *in-sample* and needs an unseen family before it counts in any claim.
  - The lead re-checks on test, an LLM-paraphrased family (to build) and τ-bench replay.

## Run
```bash
.venv/bin/python -m components.checker.autoresearch.eval          # prints the dev score, then a JSON line of secondaries
```

## Idea backlog (lead-maintained)
1. Quantities written in words ("two hundred", "fifty") — general capability.
2. Exit/entry idioms for side and intent ("want out of", "get out of", "load up on") — *in-sample risk*.
3. Multi-turn references ("same again", "my other account") using session state.
4. Value-flow provenance: a limit price must equal a quote seen **after** the user's request.
5. Second gate for resolver quotes: NLI entailment quote ⇒ claim (HHEM / DeBERTa-v3).
6. Prompt-cache the policy prefix for the resolver (latency).
