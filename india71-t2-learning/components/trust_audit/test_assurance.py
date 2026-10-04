import numpy as np

from components.trust_audit.assurance import Design, anchor_summary, misclassification_rate, run_assurance, tau2_adjusted
from components.trust_audit.core import forensic_flags, retest, select_audit
from eval.sim.calibration import ASER2024_GOVT_STD3
from eval.sim.world import make_world


def test_misclassification_rate_inverts_disagreement():
    eps = 0.03
    d = 2 * eps * (1 - eps)
    assert abs(misclassification_rate(10_000, d * 10_000) - eps) < 1e-6
    assert misclassification_rate(0, 0) == 0.0


def test_anchor_summary_ratio_and_positive_variance():
    p, v = anchor_summary(np.array([10, 10, 10]), np.array([2, 3, 4]))
    assert abs(p - 0.3) < 1e-9 and v > 0


def test_tau2_adjusted_is_strictly_positive():
    assert tau2_adjusted(np.zeros(6), np.full(6, 0.001)) > 0


def test_pipeline_outputs_valid_intervals_and_retest_double_checks():
    w = make_world(3, {**ASER2024_GOVT_STD3, "n_schools": 150, "n_clusters": 12})
    pub = w.public_view()
    risk = forensic_flags(pub.teacher_reports, pub.schools, pub.item_responses, pub.item_bank)
    sel = select_audit(pub.schools, risk, 15, "risk_pps", seed=20)
    aud = retest(w, sel, 12, seed=34)
    assert {"n_meeting_goal_obs", "n_double", "n_disagree"}.issubset(aud.columns)
    assert (aud.n_double <= aud.n_audited_children).all()
    ctx, fit, iv = run_assurance(pub, risk, sel, aud, Design(budget=15), R=50, seed=56, bias_model="mean")
    assert len(iv) == 2 * len(ctx.blocks)
    assert ((iv.lo <= iv.estimate + 1e-12) & (iv.estimate <= iv.hi + 1e-12)).all()
    assert iv[["lo", "hi", "estimate"]].stack().between(0, 1).all()
    assert 0 <= fit.eps <= 0.2 and fit.extras["tau2"] > 0


def test_public_inputs_only_except_retest():
    # the estimator must not see hidden truth: public_view drops truth tables
    w = make_world(4, {"n_schools": 40, "n_clusters": 4})
    pub = w.public_view()
    assert pub.truth_school.empty and "read_goal" not in pub.children.columns
