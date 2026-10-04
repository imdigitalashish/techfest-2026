"""C5 isolated metrics: governance-scenario accuracy and audit-log tamper detection.

Usage (from india71-t3-finance/): .venv/bin/python eval/policy_engine_eval.py -> eval/results/policy_engine.json
Attacks on the log: flip a decision, delete an entry, swap adjacent entries (all on the checkpointed prefix), truncate
the tail, append a forged entry without the key, and append a correctly keyed entry AFTER the checkpoint (must be
reported as unanchored, i.e. not full integrity). Scenarios were written with the rules (fidelity, not legality).
"""
import copy
import hashlib
import hmac
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "architecture" / "contracts"))
import contracts as C  # noqa: E402
from components.policy_engine.engine import AuditLog, PolicyEngine  # noqa: E402

KEY = b"test-only-audit-key"  # production: held in an HSM, never in code
sc = json.loads((ROOT / "components" / "policy_engine" / "scenarios.json").read_text())["scenarios"]
eng, rows = PolicyEngine(KEY), []
for s in sc:
    req = {"request_id": s["id"], "requester_role": s["role"], "requester_id": f"{s['role']}-1", "purpose": s["purpose"],
           "data_elements": s["data"], "granularity": s["gran"], "legal_basis": s["basis"], "own_customers_only": s["own"]}
    C.AccessRequest.model_validate(req)
    dec = eng.request(req)
    C.AccessDecision.model_validate(dec)
    rows.append({"id": s["id"], "expected": s["allow"], "got": dec["allow"], "rule_expected": s["rule"], "rule_got": dec["rule_ids"][0],
                 "ok": dec["allow"] == s["allow"] and dec["rule_ids"][0] == s["rule"]})
log = eng.log
assert len(log.entries) == len(sc), "every decision must be logged"
for e in log.entries:
    C.AuditEntry.model_validate(e)
cp = log.checkpoint()
assert AuditLog.verify(log.entries, KEY, cp)["full_integrity"]
attacks = []
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
        attacks.append((kind, es))
attacks.append(("truncate_tail", copy.deepcopy(log.entries[:-1])))
last = log.entries[-1]


def forged(key):
    seq, prev, payload = len(log.entries), last["entry_hash"], hashlib.sha256(b"fabricated allow").hexdigest()
    h = hmac.new(key, f"{prev}|{seq}|FORGED|1|{payload}".encode(), hashlib.sha256).hexdigest()
    return copy.deepcopy(log.entries) + [{"seq": seq, "request_id": "FORGED", "decision": True, "payload_sha256": payload,
                                          "prev_hash": prev, "entry_hash": h}]


attacks.append(("forged_suffix_without_key", forged(b"attacker-guess")))
attacks.append(("keyed_suffix_after_checkpoint", forged(KEY)))
detected = {k: 0 for k, _ in attacks}
counts = {k: 0 for k, _ in attacks}
for kind, es in attacks:
    counts[kind] += 1
    detected[kind] += not AuditLog.verify(es, KEY, cp)["full_integrity"]
res = {"n_scenarios": len(rows), "correct": sum(r["ok"] for r in rows), "allows": sum(r["got"] for r in rows),
       "false_allows": sum(r["got"] and not r["expected"] for r in rows), "n_mutations": len(attacks),
       "mutations_detected": sum(detected.values()), "by_attack": {k: [detected[k], counts[k]] for k in counts}, "rows": rows}
(ROOT / "eval" / "results" / "policy_engine.json").write_text(json.dumps(res, indent=1))
print(f"C5 scenarios {res['correct']}/{res['n_scenarios']} correct ({res['allows']} allows, {res['false_allows']} false allows); "
      f"log attacks detected {res['mutations_detected']}/{res['n_mutations']}: {res['by_attack']}")
