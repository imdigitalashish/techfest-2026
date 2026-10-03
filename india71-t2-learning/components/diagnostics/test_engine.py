from eval.sim.world import make_world
from components.diagnostics import adaptive_test, aser_rule, bayes_irt
from architecture.contracts.fln_contracts import ChildDiagnosis


def test_diagnostics_return_contracts():
    w = make_world(4, {"n_schools": 5, "n_clusters": 2})
    ch = w.children.iloc[0]
    d1 = aser_rule(ch.student_raw_id, ch.udise_code, 3, "language", w.item_responses, w.item_bank)
    d2 = bayes_irt(ch.student_raw_id, ch.udise_code, 3, "language", w.item_responses, w.item_bank, w.cfg["read_thresholds"])
    d3, used = adaptive_test(ch.student_raw_id, ch.udise_code, 3, "language", w.item_responses, w.item_bank, w.cfg["read_thresholds"], max_items=6)
    assert isinstance(d1, ChildDiagnosis) and isinstance(d2, ChildDiagnosis) and isinstance(d3, ChildDiagnosis)
    assert len(used) <= 6
    assert 0 <= d2.meets_grade_goal <= 1


def test_bayes_reasonable_on_cohort():
    w = make_world(5, {"n_schools": 20, "n_clusters": 4})
    sample = w.children.sample(n=100, random_state=5)
    acc = []
    for _, ch in sample.iterrows():
        d = bayes_irt(ch.student_raw_id, ch.udise_code, 3, "numeracy", w.item_responses, w.item_bank, w.cfg["math_thresholds"])
        acc.append(abs(d.level - int(ch.true_math_level)) <= 1)
    assert sum(acc) / len(acc) >= 0.60
