"""C5 isolated metrics: governance-scenario accuracy and audit-log tamper detection.

Usage (from india71-t3-finance/): .venv/bin/python eval/policy_engine_eval.py -> eval/results/policy_engine.json
"""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "architecture" / "contracts"))
import contracts as C  # noqa: E402
from components.policy_engine.engine import AuditLog, decide  # noqa: E402

sc = json.loads((ROOT / "components" / "policy_engine" / "scenarios.json").read_text())["scenarios"]
log, rows = AuditLog(), []
for s in sc:
    req = {"request_id": s["id"], "requester_role": s["role"], "requester_id": f"{s['role']}-1", "purpose": s["purpose"],
           "data_elements": s["data"], "granularity": s["gran"], "legal_basis": "as claimed", "own_customers_only": s["own"]}
    C.AccessRequest.model_validate(req)
    dec = decide(req)
    C.AccessDecision.model_validate(dec)
    log.append(req, dec)
    rows.append({"id": s["id"], "expected": s["allow"], "got": dec["allow"], "rule_expected": s["rule"], "rule_got": dec["rule_ids"][0],
                 "ok": dec["allow"] == s["allow"] and dec["rule_ids"][0] == s["rule"]})
for e in log.entries:
    C.AuditEntry.model_validate(e)
cp = log.checkpoint()
assert AuditLog.verify(log.entries, cp)
mut, caught = 0, 0
for i in range(len(log.entries)):
    for kind in ("flip_decision", "delete", "swap_next"):
        es = copy.deepcopy(log.entries)
        if kind == "flip_decision":
            es[i]["decision"] = not es[i]["decision"]
        elif kind == "delete":
            del es[i]
        elif i + 1 < len(es):
            es[i], es[i + 1] = es[i + 1], es[i]
        else:
            continue
        mut += 1
        caught += not AuditLog.verify(es, cp)
res = {"n_scenarios": len(rows), "correct": sum(r["ok"] for r in rows), "allows": sum(r["got"] for r in rows),
       "false_allows": sum(r["got"] and not r["expected"] for r in rows), "n_mutations": mut, "mutations_detected": caught,
       "rows": rows}
(ROOT / "eval" / "results" / "policy_engine.json").write_text(json.dumps(res, indent=1))
print(f"C5 scenarios {res['correct']}/{res['n_scenarios']} correct ({res['allows']} allows, {res['false_allows']} false allows); "
      f"audit-log tampering detected {caught}/{mut}")
