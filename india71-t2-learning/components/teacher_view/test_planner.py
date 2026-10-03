from datetime import date
from eval.sim.world import make_world
from components.diagnostics import bayes_irt
from components.teacher_view import make_plan, render_ivr_script, sms_segments


def _diagnoses():
    w = make_world(6, {"n_schools": 2, "n_clusters": 1})
    kids = w.children[w.children.udise_code == w.schools.iloc[0].udise_code].head(20)
    ds = [bayes_irt(k.student_raw_id, k.udise_code, 3, "language", w.item_responses, w.item_bank, w.cfg["read_thresholds"]) for _, k in kids.iterrows()]
    roster = {d.student: f"R{i+1}" for i, d in enumerate(ds)}
    return ds, roster


def test_whatsapp_hindi_payload_and_ivr():
    ds, roster = _diagnoses()
    plan = make_plan(ds, roster, date(2026, 10, 5), "whatsapp", "hi")
    assert plan.payload_bytes < 4096
    assert "सप्ताह" in plan.message_text
    assert "Namaste" in render_ivr_script(plan)


def test_sms_within_three_segments():
    ds, roster = _diagnoses()
    plan = make_plan(ds, roster, date(2026, 10, 5), "sms", "en")
    assert sms_segments(plan) <= 3
