from architecture.contracts.fln_contracts import AllocationDecision
from eval.sim.world import make_world
from components.trust_audit import forensic_flags, select_audit, retest, adjust
from components.allocation import allocate_camps, evaluate_allocation


def test_allocation_contract_and_oracle_not_worse():
    w=make_world(5,{"n_schools":120,"n_clusters":12}); pub=w.public_view()
    risk=forensic_flags(pub.teacher_reports,pub.schools,pub.item_responses,pub.item_bank)
    sel=select_audit(pub.schools,risk,12,"risk_pps",seed=5)
    trust=adjust(pub.schools,risk,retest(w,sel,8,seed=6),sel)
    raw=allocate_camps(pub,trust,12,"baseline_raw")
    adj=allocate_camps(pub,trust,12,"audit_adjusted")
    oracle=allocate_camps(pub,trust,12,"oracle",truth_school=w.truth_school)
    assert len(adj)==12 and all(isinstance(a,AllocationDecision) for a in adj)
    assert evaluate_allocation(w,oracle) >= evaluate_allocation(w,raw) * 0.95
