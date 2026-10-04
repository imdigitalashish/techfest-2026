# Frozen autoresearch program: C4 diagnostics

Goal: improve child-level FLN diagnostic efficiency and reliability for the simulator-backed C4 component while preserving the public component contracts.

Frozen metric: `c4_level_acc_at_8_items`, the exact ASER-style level accuracy of `adaptive_test` capped at 8 classroom-tool items, averaged over seeds 101..105 and both subjects by `components/diagnostics/autoresearch/eval.py`.

Constraints:
- Only edit `components/diagnostics/engine.py` item-selection, stopping, or prior logic.
- Never edit `components/diagnostics/evaluate.py`, `components/diagnostics/autoresearch/eval.py`, `eval/sim/world.py`, or tests during an autoresearch run.
- Keep a change only if it improves seeds 101..105 by more than 1 baseline standard deviation and does not worsen held-out seeds 201..205.
- Preserve pydantic contract outputs and deterministic behavior for a fixed seed.

Idea backlog:
- Tune stopping rule confidence thresholds by subject and posterior entropy.
- Compare Fisher-information item selection with KL/expected-posterior-variance item selection.
- Choose start items from a Grade-3 prior instead of a zero-theta prior.
- Use school-level prior from the previous assessment round when available.
- Add content balancing so the CAT does not over-sample one competency band.
