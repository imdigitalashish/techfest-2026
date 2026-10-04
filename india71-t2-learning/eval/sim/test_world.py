from eval.sim.world import make_world


def test_world_deterministic():
    cfg = {"n_schools": 80, "n_clusters": 8}
    w1 = make_world(7, cfg); w2 = make_world(7, cfg)
    assert w1.schools.equals(w2.schools)
    assert w1.children.equals(w2.children)
    assert w1.item_responses.equals(w2.item_responses)


def test_world_calibration():
    w = make_world(11, {"n_schools": 120, "n_clusters": 8})
    assert abs(w.children.read_goal.mean() - 0.25) <= 0.03
    assert abs(w.children.math_goal.mean() - 0.30) <= 0.03


def test_inflation_present_and_public_drops_truth():
    w = make_world(13, {"n_schools": 80, "n_clusters": 8})
    infl = w.truth_school[w.truth_school.inflating_school]
    assert len(infl) > 0
    assert (infl.reported_read_goal_rate - infl.true_read_goal_rate).mean() > 0.10
    pub = w.public_view()
    assert "theta_read" not in pub.children.columns
    assert pub.truth_school.empty
