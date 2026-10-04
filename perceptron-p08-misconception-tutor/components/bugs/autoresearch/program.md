# Autoresearch program — C3 bug library: reproduce real students' wrong answers

**Goal:** raise `reproduction_dev`, the share of real Eedi distractors (labelled with one of our five pack misconceptions) whose exact wrong answer our bug programs reproduce from the question text. This measures whether the executable misconceptions are *real*, not just plausible.

**Metric:** `.venv/bin/python components/bugs/autoresearch/eval.py` prints `METRIC reproduction_dev=…`. The evaluator is **frozen**: never edit `eval.py`.

**Guards** (reject the change if any is violated):
- `wrong_attribution_dev` and `wrong_attribution_holdout` must stay 0.0.
- `false_claim_rate` must stay ≤ 0.03.
- `pytest components/tests` must pass.

**Editable:** `components/bugs/eedi_parse.py` (LaTeX → expression mapping), and bug programs in `components/bugs/school_math.py` *only* if the change is a faithful reading of the Eedi misconception text. No per-item hacks; no lookup of question ids.

**Keep rule:** keep a change only if `reproduction_dev` improves by ≥ 1 item (≥ 1/n_dev) and the guards hold. The lead re-checks `reproduction_holdout` every 3 kept changes to catch overfitting.

**Idea backlog:**
1. Try every math segment and prefer the one whose clean evaluation equals Eedi's correct answer (questions often contain several segments).
2. Mixed numbers (`1 \frac{1}{2}`), decimals, `\left(…\right)`, `^{2}` on bracketed negatives.
3. Word-problem stems ("What is the value of…", "Calculate…") vs "where do the brackets go" (not evaluable: skip).
4. An LLM extracts the expression, accepted only if SymPy reproduces the correct answer (bug-compiler groundwork).
5. Composite bugs: a distractor reproduced by a *pair* of pack bugs.
