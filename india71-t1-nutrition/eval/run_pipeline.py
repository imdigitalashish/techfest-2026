"""Walking skeleton: one weekly district run of Poshan Setu, end to end, on SYNTHETIC data.

simulator → WHO z-scores → record plausibility + AWC credibility → 90-day risk (top-K per AWC)
→ alerts (SAM / MAM / RISK_HIGH / DATA_RECHECK) → tasks with owners and due dates
→ capacity-capped worklists (SMS-sized, no names) → purpose-bound access checks → audit chain.
Scored against the simulator's ground truth. Run: .venv/bin/python -m eval.run_pipeline
Writes eval/results/pipeline_demo.json.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from architecture.contracts import models as m
from components.action_router import router
from components.audit_ledger.ledger import Ledger
from components.cohort_simulator.simulate import SimConfig, simulate
from components.credibility_engine import engine
from components.early_warning import model as ew
from components.early_warning.eval import labelled
from components.frontline_worklist import render
from components.policy_gate import gate

K = 5  # home-visit capacity per AWC per week for risk alerts (assumption)
OUT = Path(__file__).parent / "results" / "pipeline_demo.json"


def main() -> dict:
    t0 = time.time()
    clf = ew.fit_logistic(labelled(21), ew.ANTHRO)  # trained on a different synthetic district

    sim = simulate(SimConfig(seed=7))
    geo = sim["geo"].set_index("awc_code")
    truth = sim["truth_monthly"].sort_values(["child_key", "month_index"])
    g = truth.groupby("child_key").true_wlz
    truth = truth.assign(fut_min=pd.concat([g.shift(-1), g.shift(-2), g.shift(-3)], axis=1).min(axis=1, skipna=False))
    feats = ew.features(sim["measurements"], sim["health_events"], truth[["child_key", "measured_on", "month_index"]])
    month = int(truth.month_index.max()) - 3  # latest month whose 3-month future is known
    cur = feats[feats.month_index == month].merge(truth[["child_key", "month_index", "true_wlz", "fut_min"]],
                                                  on=["child_key", "month_index"])
    cur["risk"] = clf.predict_proba(ew.fill(cur[ew.ANTHRO]))[:, 1]
    _, rec, units = engine.assess(sim["measurements"][sim["measurements"].measured_on <= cur.measured_on.max()])
    today = cur.measured_on.max().date()

    def geo_of(awc: str) -> m.GeoUnit:
        r = geo.loc[awc]
        return m.GeoUnit(state_code=r.state_code, district_code=r.district_code, project_code=r.project_code,
                         sector_code=r.sector_code, awc_code=awc)

    cur["status"] = np.where(cur.wlhz < -3, "sam", np.where(cur.wlhz < -2, "mam", "normal"))
    alerts: list[m.Alert] = []
    refs: dict[str, str] = {}
    for r in cur[cur.status != "normal"].itertuples():
        kind = m.AlertKind.SAM if r.status == "sam" else m.AlertKind.MAM
        alerts.append(m.Alert(alert_id=f"{kind.value}-{r.event_id}", child_key=r.child_key, geo=geo_of(r.awc_code),
                              kind=kind, severity=4 if r.status == "sam" else 3, created_on=today,
                              evidence=[f"WHZ {r.wlhz:.2f}"], recommended_action="protocol", synthetic=True))
    normal = cur[cur.status == "normal"].copy()
    normal["rank"] = normal.groupby("awc_code").risk.rank(ascending=False, method="first")
    flagged = normal[normal["rank"] <= K]
    for r in flagged.itertuples():
        alerts.append(m.Alert(alert_id=f"risk_high-{r.event_id}", child_key=r.child_key, geo=geo_of(r.awc_code),
                              kind=m.AlertKind.RISK_HIGH, severity=2, created_on=today,
                              evidence=[f"risk {r.risk:.2f}", f"WHZ {r.wlhz:.2f}"], recommended_action="home visit",
                              synthetic=True))
    for u in units[units.band == "low"].itertuples():
        alerts.append(m.Alert(alert_id=f"data_recheck-{u.unit_id}", geo=geo_of(u.unit_id), kind=m.AlertKind.DATA_RECHECK,
                              severity=2, created_on=today, evidence=[f"credibility {u.credibility:.2f}"],
                              recommended_action="re-measure sample", synthetic=True))
    for a in alerts:
        if a.child_key:
            refs[a.alert_id] = "PT-" + a.child_key[-6:]

    ledger = Ledger()
    tasks = router.route(alerts, today)
    for tk in tasks:
        ledger.append("system:action_router", "task_created", tk.task_id)
    worklists = render.build_worklists(tasks, refs, {"default": 10, "aww": 10, "ls": 15}, today)
    sms = [s for w in worklists for s in render.to_sms(w)]

    # purpose-bound access: the AWW reads her own list; a DPO tries to read named children (must be denied)
    probe = alerts[0]
    reqs = [
        (m.Role.AWW, m.ScopeLevel.AWC, probe.geo.awc_code, m.Purpose.SERVICE_DELIVERY, m.DataCategory.IDENTIFIED_CHILD),
        (m.Role.DPO, m.ScopeLevel.DISTRICT, probe.geo.district_code, m.Purpose.PROGRAMME_MONITORING, m.DataCategory.IDENTIFIED_CHILD),
        (m.Role.AWW, m.ScopeLevel.AWC, "OTHER-AWC", m.Purpose.SERVICE_DELIVERY, m.DataCategory.IDENTIFIED_CHILD),
        (m.Role.PUBLIC, m.ScopeLevel.NATIONAL, "IN", m.Purpose.PUBLIC_REPORTING, m.DataCategory.AGGREGATE),
    ]
    decisions = []
    for i, (role, lvl, scope, purpose, cat) in enumerate(reqs):
        req = m.AccessRequest(request_id=f"R{i}", actor_id=f"{role.value}-demo", actor_role=role, actor_scope_level=lvl,
                              actor_scope_id=scope, purpose=purpose, data_category=cat, subject_child_key=probe.child_key,
                              requested_at=datetime(today.year, today.month, today.day, 9, 0))
        d = gate.decide(req, {"subject_geo": probe.geo})
        decisions.append(f"{role.value}/{cat.value}/{purpose.value}: {d.decision}")
        ledger.append(req.actor_id, f"access_{d.decision}", req.request_id, decision_ref=d.rule_id)
    ok, bad = ledger.verify()

    # score against SYNTHETIC truth
    elig = cur[(cur.true_wlz >= -2) & cur.fut_min.notna()]
    pos = elig[elig.fut_min < -2]
    caught = pos.child_key.isin(set(flagged.child_key))
    sam_truth = cur[cur.true_wlz < -3]
    res = {
        "label": "SYNTHETIC district run — see docstring",
        "as_of": str(today),
        "children_measured_this_month": int(len(cur)),
        "awcs": int(cur.awc_code.nunique()),
        "records_rejected_pct_all_months": round(100 * float((~rec.usable).mean()), 2),
        "awcs_low_credibility": int((units.band == "low").sum()),
        "alerts_by_kind": dict(Counter(a.kind.value for a in alerts)),
        "tasks": len(tasks),
        "worklists": len(worklists),
        "sms_messages": len(sms),
        "sms_max_chars": max((len(s) for s in sms), default=0),
        "true_incident_wasting_next_3m": int(len(pos)),
        "incident_cases_flagged_now_pct": round(100 * float(caught.mean()), 1) if len(pos) else None,
        "risk_alert_precision_pct": round(100 * float((flagged.fut_min < -2).mean()), 1),
        "true_sam_now": int(len(sam_truth)),
        "access_decisions": decisions,
        "audit_entries": len(ledger.entries) if hasattr(ledger, "entries") else None,
        "audit_chain_verified": bool(ok),
        "runtime_s": round(time.time() - t0, 1),
        "synthetic": True,
    }
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res))
    return res


if __name__ == "__main__":
    main()
