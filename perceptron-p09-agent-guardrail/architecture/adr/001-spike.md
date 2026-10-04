# ADR 001 — Spike components: argument provenance (S1) and a risk-routed, calibrated cascade (S2)

- **Status:** accepted (morning package, 4 Oct 2026). Revisit at the 12 Oct selection gate.
- **Deciders:** P9 project lead. The antithesis below was written by the lead playing adversary. An independent adversarial agent could not run tonight (Supervisor lean mode: no sub-agents), so re-run it with an independent `rubber-duck` agent before 12 Oct.
- **Evidence:** [`research/landscape.md`](../../research/landscape.md), [`architecture/components.md`](../components.md), eval results in [`eval/results/`](../../eval/results/).

## Context
The brief asks for a checker that verifies at least one class of agent action against a verifiable source before execution, plus (stretch) risk-based routing between a fast and a careful model and a red-team suite. Judges score novelty "beyond the obvious baseline named in Starter Resources", i.e. beyond LangGraph plus a small KB with an LLM checking the call. Industry ships hooks, classifiers, declarative gates (Cedar, Invariant) and human confirmation. Grounding products check **response text**, not **action arguments** (landscape §5). The closest 2026 papers are ActGov (SMT-checked policy sets), ContrAgent (LTLf contracts → DFA) and closed-world resolution (registry plus signature). None of them checks whether each argument **value** has a trusted source. Closed-world resolution explicitly leaves "borrowed arguments schema-indistinguishable from a valid call" as an irreducible residue.

## Candidates (scored 1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasible by finals | Measurable (scalar) | Demoable | Total |
|---|---|---|---|---|---|---|
| **S1 Argument provenance + three-way verdict + quote-verified LLM resolution** ("cite before you act") | 5 | 4 | 5 (Tier 0 built tonight) | 5 | 5 | **24** |
| **S2 Risk-routed fast/careful cascade with calibrated thresholds** (conformal / Learn-then-Test) | 4 (it *is* the stretch goal) | 3 | 4 | 5 | 3 | **19** |
| Closed-loop self-repair (block feedback → agent fixes call) | 4 | 3 | 4 | 4 | 5 | 20 → an **evaluation feature**, not a spike |
| Fine-tuned small judge (learned sentinel, Safiron/HiSentinel-style) | 3 | 2 | 3 | 5 | 3 | 16 |
| Dry-run / shadow execution with post-condition checks | 3 | 3 | 3 | 3 | 4 | 16 |
| Auto-formalise policy text to Cedar/SMT/LTLf | 3 | 3 (AWS AR checks, ActGov, ContrAgent exist) | 2 | 3 | 2 | 13 |

## Decision
- **Spike 1 (S1):** argument-level provenance is the core check. Every intent-bearing argument of a write call must trace to a trusted source: the user's words, the reference KB or structured tool data. Untrusted content is never a source of intent. Each check returns pass / **fail (contradicted)** / **unverifiable (no evidence)** / needs-approval, with evidence and a policy clause. Pre-trade-style contracts (SEC 15c3-5 analogues) run in the same deterministic tier. A model may resolve only *unverifiable* checks, and only by quoting the deciding words, which we verify verbatim against the source.
- **Spike 2 (S2):** route the unverifiable residue by risk (reversibility, value at stake) to a fast model, a careful model or a human. Set thresholds by calibration with a stated miss-rate target. Closed-loop self-repair is measured as part of the evaluation.
- Everything else stays best existing practice: LangGraph agent, pre-tool hook, JSON/BM25 KB, LangGraph `interrupt()` for humans.

## Six Thinking Hats (S1)
- **White (facts).** On 183 held-out test items (36 good, 147 bad; families unseen in dev), Tier 0 blocks or escalates **100%** of bad calls with **0%** false blocks and **0%** escalations, p95 **≤ 5 ms** (0.6–4.7 ms across runs on a loaded laptop). Schema-only validation catches **0%**, because every bad call is well-typed by construction. On dev, the baseline Tier 0 escalates **16.7%** of good calls, all from the deliberately hard paraphrase family. Ratchet iteration 2 brings this to 0%, but only in-sample (`components/checker/autoresearch/results.tsv`). Reproduce: `python -m eval.run_eval --guards none,schema,t0 --split test`. **LLM-judge baseline** (Qwen3-1.7B with the full KB and policy in the prompt; same 61-call test subsample): catch **71.1%**, false-block **68.8%**. Its errors are arithmetic and state slips, e.g. calling a price 0.3% from reference "outside ±5%", or missing a ×10 quantity and a duplicate (`eval/results/llm_judge_1.7b__test__every3.json`). The 8B judge was not run tonight because of memory pressure.
- **Red (gut).** An Optiver panel will recognise "pre-trade risk checks, applied to an agent that can invent the order itself" in one sentence. Seeing an invented ticker or a ×10 fat-finger stopped in under a millisecond, with the clause cited, is a memorable demo.
- **Black (risks).** (1) The suite is synthetic and its templates were written by the rule author, so 100% overstates real performance. (2) Regex mention parsing is brittle to paraphrase and multi-turn reference ("same again for my other account"). (3) Coincidental matches: an injected value that also appears in the user's text passes provenance. (4) Each new domain needs contracts (engineering cost). (5) KB staleness. (6) Close 2026 work (ActGov, ContrAgent, closed-world resolution) means novelty must be argued precisely, not claimed broadly.
- **Yellow (benefits).** Deterministic, explainable (evidence + clause), sub-millisecond, offline, auditable. Three-way verdicts avoid both silent passes and blanket blocks. The LLM is never trusted without verified evidence, which bounds checker hallucination.
- **Green (alternatives).** Distil the 8B resolver into the fast mention parser. Draft contracts from policy text with an LLM, then review them (ActGov-like). Track value flows across multi-step trajectories (a provenance graph). Replay τ-bench historical trajectories for real model errors. Package as an MCP gateway.
- **Blue (process).** S1 + S2 now. First ratchet loop on S1's dev score with a frozen evaluator. Holdout re-check on test, LLM-paraphrased requests and τ-bench replay before any claim. Re-decide at 12 Oct.

## Thesis → antithesis → synthesis
- **Thesis.** A hallucinated action is an argument without a source. Checking each value's provenance against trusted sources is precise, cheap and explainable. It catches exactly the residue that schema and registry checks cannot.
- **Antithesis.** "This is input validation with regexes. Real requests are paraphrased, multi-turn and implicit. String-match provenance will either escalate everything (approval fatigue) or be bypassed. An LLM-as-judge with retrieval is simpler and generalises. And 100% on your own synthetic suite proves nothing."
- **Synthesis.**
  - Keep deterministic provenance where hallucinations concentrate and string evidence exists: IDs, numbers, entities, side, amounts, clause citations.
  - Hand only the residue to models, under quote verification.
  - Make **escalation rate a first-class cost** next to catch rate and false blocks.
  - Evaluate where the antithesis bites: held-out phrasing families, LLM-paraphrased requests, and real model errors from τ-bench logs.
  - Compare against the LLM judge at equal latency.
  - If paraphrase escalations stay high, distil a learned mention parser. The architecture doesn't change.

## Consequences
- The ratchet target is S1's mention parser and resolver (`components/checker/`). `eval/run_eval.py` and the suite stay frozen per loop.
- The abstract leads with S1, frames S2 as the stretch goal, and states the synthetic-suite caveat openly.
- Next: τ-bench replay (MIT; ~40 MB of logs), an LLM-paraphrased test family, a LangGraph live demo with self-repair.

## Status update — 4 Oct 2026, 12:15 IST (real-error evidence)
Evidence from the held-out τ-bench replay (`eval/taubench/README.md`), the gpt-6-astra independent red team (`eval/external/astra/`) and the gpt-6-sol code review (`reviews/`):

**Confirmed**
- **S1 beats the obvious baseline at matched human load.**
  - On 300 real gpt-4o and Claude-3.5-Sonnet write calls, balanced Tier 0 stops 47.5% of harmful calls at 1.7% false blocks.
  - A gpt-4.1-mini judge reading the full transcript stops 35.0% at 11.7% false blocks. Even with its threshold tuned on the same sample, at the same good-call stop rate the judge stops 24.2%.
- **S2's cascade shape is right.**
  - Giving gpt-4.1-mini only the held residue cuts holds on good calls from 25.8% to 16.7%, with no extra false blocks.
  - Cost: $0.00036 per guarded call, against $0.0014 to judge every call.

**Refuted or weakened**
- **The synthetic 100% figure was flattering.** On real errors: 40.7% [28–55] at 2.0% false blocks and 30% holds (full held-out test); 68% at 56% holds for the untuned v0. On an independent red team: 82% stopped, 8% false blocks.
- **Dev tuning did not improve the held-out score.** The untuned v0 scores highest (0.325 vs balanced 0.235); tuning moved the operating point rather than the frontier.
- **A 1.7B model is not a usable careful tier.** It settled 11 of 85 holds, and 5 of those wrongly.
- **Thesis concession:** 8 of 20 audited misses were requested outright by τ-bench's simulated user, so no transcript-based provenance check can catch them.

**Decision**
- Keep S1 and S2.
- The careful tier is a frontier API model (gpt-4.1-mini or better) or a larger local model; the 1.7B model is demoted to an offline fallback.
- Before the next tuning round:
  - build a scenario-grouped holdout (gpt-6-sol issue 3);
  - add consent/policy labels alongside DB-effect labels (issue 2);
  - add checks for the two fixable miss classes: wrong-entity resolution (via the careful tier) and one-return-per-order sequencing.
