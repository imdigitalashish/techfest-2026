# C4 — Diagnostic engine (Spike 1, with C7/C11)

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Item responses → child level + competency mastery with confidence; adaptive item choice so a check takes minutes.

**State of the art / what is deployed.** Paper ASER/TaRL tools use a highest-level-passed rule; TaRL's evidence base: six RCTs in seven states (J-PAL). Methods: IRT/2PL, CDMs, classification CAT with SPRT stopping; knowledge tracing fits dense click-streams, not termly checks (`sources/methods-sota.md`).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Bayesian 2PL on a θ-grid + stop at P(level) ≥ 0.9 (works offline on a low-end phone) | 5·3·5·5·5 |
| Prior from the school's previous round (shrinks items further) | 4·3·4·5·3 |
| AI oral-reading (ORF) score as an extra item, validated per language | 4·3·3·4·4 |

**Status.** Implemented: `components/diagnostics/` — rule, Bayesian IRT, CAT. Baseline ledger: exact level accuracy 0.551 with the check capped at 8 items (seeds 101–105, synthetic). Autoresearch scaffold: `components/diagnostics/autoresearch/`.

**Isolated metric.** Exact level accuracy and items per child at parity with the full test (seeds 101–105; held-out 201–205).
