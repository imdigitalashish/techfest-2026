from architecture.contracts.fln_contracts import AreaEstimate
from eval.sim.world import make_world
from components.trust_audit import forensic_flags, select_audit, retest, adjust
from components.area_estimation import estimate_areas, evaluate_area


def test_area_estimates_contract_and_anchor():
    w=make_world(4,{"n_schools":120,"n_clusters":12}); pub=w.public_view()
    risk=forensic_flags(pub.teacher_reports,pub.schools,pub.item_responses,pub.item_bank)
    sel=select_audit(pub.schools,risk,12,"risk_pps",seed=4)
    trust=adjust(pub.schools,risk,retest(w,sel,8,seed=5),sel)
    areas=estimate_areas(pub,trust)
    assert set(areas)=={"baseline_direct","audit_adjusted_direct","fh_benchmarked"}
    assert all(isinstance(a,AreaEstimate) for a in areas["fh_benchmarked"])
    m=evaluate_area(w,areas["fh_benchmarked"])
    # legacy path: precision-weighted (not hard) benchmarking, so the aggregate moves toward, not onto, the anchor
    assert m["aggregate_anchor_abs_diff_pp"] < 15
    assert 0 <= m["coverage90"] <= 1
