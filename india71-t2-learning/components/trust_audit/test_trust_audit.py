from architecture.contracts.fln_contracts import TrustAssessment
from eval.sim.world import make_world
from components.trust_audit import forensic_flags, select_audit, retest, adjust, detection_auc


def test_trust_pipeline_contracts_and_auc():
    w=make_world(3,{"n_schools":120,"n_clusters":12}); pub=w.public_view()
    risk=forensic_flags(pub.teacher_reports,pub.schools,pub.item_responses,pub.item_bank)
    assert {"risk_score","heaping_at_goal","gap_vs_classroom"}.issubset(risk.columns)
    assert risk.risk_score.between(0,1).all()
    assert detection_auc(risk,w.truth_school) >= 0.60
    sel=select_audit(pub.schools,risk,12,"risk_pps",seed=3)
    assert sel.selected_for_audit.sum()==12
    assert sel.audit_inclusion_prob.between(0,1).all()
    audit=retest(w,sel,8,seed=4)
    out=adjust(pub.schools,risk,audit,sel)
    assert len(out)==len(pub.schools)
    assert all(isinstance(x,TrustAssessment) for x in out)
    assert any(x.selected_for_audit and x.audited_pct_meeting_goal is not None for x in out)
