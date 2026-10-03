from pathlib import Path
import shutil
from eval.sim.world import make_world
from components.trust_audit import forensic_flags, select_audit, retest, adjust
from components.area_estimation import estimate_areas
from components.allocation import allocate_camps
from components.dashboard import build_dashboard


def test_dashboard_writes_html_and_json():
    w=make_world(6,{"n_schools":80,"n_clusters":10}); pub=w.public_view()
    risk=forensic_flags(pub.teacher_reports,pub.schools,pub.item_responses,pub.item_bank)
    sel=select_audit(pub.schools,risk,8,"risk_pps",seed=6)
    trust=adjust(pub.schools,risk,retest(w,sel,6,seed=7),sel)
    areas=estimate_areas(pub,trust)
    alloc=allocate_camps(pub,trust,8,"audit_adjusted")
    out_dir=Path("deliverables/demo/test_dashboard_out")
    if out_dir.exists(): shutil.rmtree(out_dir)
    p=build_dashboard({"trust":trust,"areas":areas,"allocations":alloc,"schools":pub.schools,"metrics":{"block_mae_pp_at_10pct_budget":"test"}}, out_dir)
    text=p.read_text()
    assert "SYNTHETIC DATA" in text
    assert len(text.encode()) < 300_000
    assert (out_dir/"block_dashboard_outputs.json").exists()
    shutil.rmtree(out_dir)
