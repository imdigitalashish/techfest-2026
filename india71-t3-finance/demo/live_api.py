"""Live "try to break it" API for the Sakriya demo — thin wrappers over COMMITTED components.

C5: components.policy_engine.engine.PolicyEngine and AuditLog (decide-and-log in one call, HMAC chain, checkpoints).
C11: components.dp_publisher.dp.Ledger and release_rates (validated, persistent, file-locked privacy budget; Laplace).
Nothing here re-implements a decision: every allow/deny, chain verdict and budget refusal comes from that code. This
module builds requests, applies tamper mutations to COPIES of the log, starts two clients for the race, and formats
results. The demo server calls it live; demo/export.py runs the same SCRIPT with a fixed replay key and seeded noise to
record the REPLAY transcripts the page falls back to.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
import os
import pathlib
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
for _p in (ROOT, ROOT / "architecture" / "contracts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd  # noqa: E402

import contracts as C  # noqa: E402
from components.dp_publisher.dp import Ledger, release_rates  # noqa: E402
from components.policy_engine.engine import AuditLog, PolicyEngine  # noqa: E402

SCENARIOS = ROOT / "components" / "policy_engine" / "scenarios.json"
TOTAL_EPS = 1.0   # one budget for all overlapping tables per period: eval/scorecard_eval.py (Ledger(1.0)); C5 rule A3 dp_epsilon
TABLE_EPS = 0.5   # per table, as in eval/scorecard_eval.py (two overlapping tables at 0.5 each)
MIN_CELL = 20     # C5 rule A3 obligation min_cell_size

# C5 attack script (also replayed). Fields follow contracts.AccessRequest; request ids are assigned by the session.
C5_SCRIPT = [
    ("bc_other_bank", "A BC Sakhi of Bank A asks for a Bank E customer's task list and claims she is her customer",
     dict(requester_role="bc", requester_id="bc-1", purpose="outreach", data_elements=["target_list"], granularity="person",
          legal_basis="bank_bc_agreement", own_customers_only=True, subject_bank_id="PVT_E")),
    ("bc_own_bank", "The same BC asks for her own bank's customer",
     dict(requester_role="bc", requester_id="bc-1", purpose="outreach", data_elements=["target_list"], granularity="person",
          legal_basis="bank_bc_agreement", own_customers_only=True, subject_bank_id="PSB_A")),
    ("bc_as_bank", "The BC presents herself as the bank to get the full targeting view",
     dict(requester_role="bank", requester_id="bc-1", purpose="targeting", data_elements=["target_list", "person_usage_state"],
          granularity="person", legal_basis="rbi_inoperative_review", own_customers_only=True, subject_bank_id="PSB_A")),
    ("bc_aadhaar", "The BC asks for the customer's Aadhaar number with the task list",
     dict(requester_role="bc", requester_id="bc-1", purpose="outreach", data_elements=["target_list", "aadhaar_number"],
          granularity="person", legal_basis="bank_bc_agreement", own_customers_only=True, subject_bank_id="PSB_A")),
    ("slbc_bc_scores", "The SLBC asks for a performance table of individual BCs",
     dict(requester_role="slbc", requester_id="slbc-1", purpose="accountability_statistics", data_elements=["implementer_scores"],
          granularity="bc_area", legal_basis="dpdp_s17_2_b_statistics", own_customers_only=False, subject_bank_id=None)),
    ("dfs_person_list", "DFS asks for a person-level target list",
     dict(requester_role="dfs", requester_id="dfs-1", purpose="targeting", data_elements=["target_list"], granularity="person",
          legal_basis="dpdp_s17_2_b_statistics", own_customers_only=False, subject_bank_id=None)),
    ("researcher_district", "A researcher asks for district usage rates",
     dict(requester_role="researcher", requester_id="researcher-1", purpose="research", data_elements=["aggregate_usage_rates"],
          granularity="district", legal_basis="dpdp_s17_2_b_statistics", own_customers_only=False, subject_bank_id=None)),
]
TAMPER_KINDS = {
    "delete": "Delete the entry",
    "flip": "Flip its decision to ALLOW",
    "swap": "Swap it with the next entry",
    "truncate": "Cut the newest entry off the log",
    "forge": "Append a fabricated ALLOW without the key",
    "keyed_suffix": "Insider with the key appends an ALLOW after the last published checkpoint",
}
DP_TABLES = ("district_usage", "district_usage_women", "district_usage_60plus")


def short(e: dict) -> dict:
    return {"seq": e["seq"], "request_id": e["request_id"], "decision": bool(e["decision"]),
            "prev": e["prev_hash"][:12], "hash": e["entry_hash"][:12]}


def _forged(entries: list[dict], key: bytes) -> list[dict]:
    """Mirror of eval/policy_engine_eval.py `forged`: append an ALLOW entry chained to the head, keyed with `key`."""
    last = entries[-1]
    seq, prev, payload = len(entries), last["entry_hash"], hashlib.sha256(b"fabricated allow").hexdigest()
    h = hmac.new(key, f"{prev}|{seq}|FORGED|1|{payload}".encode(), hashlib.sha256).hexdigest()
    return copy.deepcopy(entries) + [{"seq": seq, "request_id": "FORGED", "decision": True, "payload_sha256": payload,
                                      "prev_hash": prev, "entry_hash": h}]


def averaging_baseline(true_count: int, eps: float, k_max: int, seed: int) -> dict:
    """Noise without a budget vs with Sakriya's ledger, both through the committed release_rates.
    'Without': a ledger whose total never binds (today's practice has no cumulative budget for FI tables), released
    k_max times; the attacker averages the noisy counts. 'With': TOTAL_EPS caps the releases."""
    counts = pd.DataFrame({"numerator": [true_count], "denominator": [true_count]}, index=["cell"])
    open_ledger, noisy = Ledger(1e12), []
    for k in range(k_max):
        noisy.append(float(release_rates(counts, eps, open_ledger, f"r{k}", min_cell=0, seed=seed + k)
                           ["noisy_denominator"].iloc[0]))
    capped, allowed = Ledger(TOTAL_EPS), 0
    for k in range(k_max):
        try:
            release_rates(counts, eps, capped, f"r{k}", min_cell=0, seed=seed + k)
            allowed += 1
        except PermissionError:
            break
    running = [sum(noisy[: i + 1]) / (i + 1) for i in range(k_max)]
    return {"true_count": true_count, "eps": eps, "noisy": noisy, "running_mean": running, "allowed_with_ledger": allowed,
            "estimate_with_ledger": running[allowed - 1] if allowed else None, "estimate_without": running[-1]}


class Session:
    """One demo period: a policy engine with its audit log, published checkpoints, and one privacy-budget ledger file."""

    def __init__(self, key: bytes, ledger_path: str, dp_tables: dict, seed: int | None = None):
        spec = json.loads(SCENARIOS.read_text())
        self.registry = spec["registry"]
        self.key, self.engine, self.published, self.n = key, PolicyEngine(key, self.registry), [], 0
        self.ledger_path, self.seed = ledger_path, seed
        self.dp_tables = {t: pd.DataFrame(rows).set_index("unit") for t, rows in dp_tables.items()}
        self.lock = threading.Lock()
        if os.path.exists(ledger_path):
            os.remove(ledger_path)

    # ---------- C5 ----------
    def c5_request(self, fields: dict) -> dict:
        with self.lock:
            self.n += 1
            req = {"request_id": f"J-{self.n:03d}", **fields}
            try:
                req = C.AccessRequest.model_validate(req).model_dump()
            except Exception as e:  # the contract refuses malformed requests before the engine sees them
                return {"ok": False, "error": "contract", "message": str(e).splitlines()[0], "request": req}
            dec = self.engine.request(req)
            cp = self.engine.log.checkpoint()
            self.published.append(cp)  # SIMULATED external publication (a production requirement, not claimed)
            return {"ok": True, "request": req, "decision": dec, "entry": short(self.engine.log.entries[-1]),
                    "checkpoint": {"length": cp["length"], "head": cp["head"][:12]}}

    def c5_log(self) -> dict:
        with self.lock:
            es = self.engine.log.entries
            cp = self.published[-1] if self.published else None
            return {"entries": [short(e) for e in es], "verify": AuditLog.verify(es, self.key, cp),
                    "checkpoint": {"length": cp["length"], "head": cp["head"][:12]} if cp else None}

    def c5_tamper(self, kind: str, seq: int | None = None) -> dict:
        if kind not in TAMPER_KINDS:
            return {"ok": False, "error": "unknown tamper kind"}
        with self.lock:
            es = copy.deepcopy(self.engine.log.entries)
            cp = self.published[-1] if self.published else None
        if not es:
            return {"ok": False, "error": "the log is empty"}
        i = len(es) - 1 if seq is None else int(seq)
        if not 0 <= i < len(es):
            return {"ok": False, "error": "no such entry"}
        if kind == "delete":
            del es[i]
        elif kind == "flip":
            es[i]["decision"] = not es[i]["decision"]
        elif kind == "swap":
            if i + 1 >= len(es):
                return {"ok": False, "error": "no next entry to swap with"}
            es[i], es[i + 1] = es[i + 1], es[i]
        elif kind == "truncate":
            es = es[:-1]
        elif kind == "forge":
            es = _forged(es, b"attacker-guess")
        else:
            es = _forged(es, self.key)
        v = AuditLog.verify(es, self.key, cp)
        broken_at = next((k for k in range(1, len(es) + 1) if not AuditLog.verify(es[:k], self.key)["valid"]), None)
        return {"ok": True, "kind": kind, "label": TAMPER_KINDS[kind], "seq": i, "verify": v,
                "chain_broken_at": None if broken_at is None else broken_at - 1, "tampered_length": len(es),
                "real_log_untouched": True}

    # ---------- C11 ----------
    def _ledger(self, total: float = TOTAL_EPS) -> Ledger:
        return Ledger(total, self.ledger_path)

    def _state(self) -> dict:
        lg = self._ledger()
        return {"spent": lg.spent, "total": lg.total, "entries": [list(e) for e in lg.entries]}

    def c11_release(self, table: str, eps: float = TABLE_EPS) -> dict:
        if table not in self.dp_tables:
            return {"ok": False, "error": "unknown table"}
        counts = self.dp_tables[table][["numerator", "denominator"]]
        seed = None if self.seed is None else self.seed + DP_TABLES.index(table)
        try:
            rel = release_rates(counts, float(eps), self._ledger(), table, min_cell=MIN_CELL, seed=seed)
        except (PermissionError, ValueError) as e:
            return {"ok": False, "error": type(e).__name__, "message": str(e), **self._state()}
        true = counts["numerator"] / counts["denominator"]
        rows = [{"unit": str(u), "rate": None if pd.isna(r) else round(float(r), 4), "true_rate": round(float(true[u]), 4),
                 "noisy_denominator": int(d)} for u, r, d in zip(rel.index, rel["rate"], rel["noisy_denominator"])]
        err = [abs(r["rate"] - r["true_rate"]) for r in rows if r["rate"] is not None]
        return {"ok": True, "table": table, "eps": float(eps), "rows": rows,
                "mae_pp": round(100 * sum(err) / len(err), 3) if err else None,
                "suppressed": sum(r["rate"] is None for r in rows), **self._state()}

    def c11_race(self, eps: float = TABLE_EPS, clients=("SLBC", "DFS")) -> dict:
        """Two clients, each with its own Ledger object and its own handle on the ledger file, released at the same
        instant by a barrier. The committed check-and-charge transaction (exclusive file lock + re-read) must let exactly
        one of them spend the last epsilon. (flock excludes separate open() handles, across threads as across processes.)"""
        barrier, results, starts = threading.Barrier(len(clients)), {}, {}

        def client(name: str) -> None:
            lg = Ledger(TOTAL_EPS, self.ledger_path)
            barrier.wait(timeout=10)
            starts[name] = time.perf_counter()
            try:
                lg.charge(float(eps), name)
                results[name] = {"client": name, "ok": True}
            except (PermissionError, ValueError) as e:
                results[name] = {"client": name, "ok": False, "error": type(e).__name__, "message": str(e)}

        threads = [threading.Thread(target=client, args=(c,)) for c in clients]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)
        res = [results.get(c, {"client": c, "ok": False, "error": "timeout"}) for c in clients]
        gap = round(1000 * (max(starts.values()) - min(starts.values())), 2) if len(starts) == len(clients) else None
        return {"ok": True, "eps": float(eps), "results": res, "winners": sum(r["ok"] for r in res), "start_gap_ms": gap,
                **self._state()}

    def c11_charge(self, eps) -> dict:
        try:
            val = float(eps)
        except (TypeError, ValueError):
            return {"ok": False, "error": "ValueError", "message": f"not a number: {eps!r}", **self._state()}
        try:
            self._ledger().charge(val, "manual charge")
        except (PermissionError, ValueError) as e:
            return {"ok": False, "error": type(e).__name__, "message": str(e), "asked": repr(val), **self._state()}
        return {"ok": True, "asked": repr(val), **self._state()}

    def c11_restart(self) -> dict:
        """A new Ledger object over the same file, as after a server restart; then try one more table's charge."""
        st = self._state()
        try:
            self._ledger().charge(TABLE_EPS, "after restart")
            after = {"ok": True}
        except (PermissionError, ValueError) as e:
            after = {"ok": False, "error": type(e).__name__, "message": str(e)}
        return {"ok": True, "reloaded": st, "charge_after_restart": after, **self._state()}

    def c11_reopen(self, total) -> dict:
        try:
            lg = Ledger(float(total), self.ledger_path)
        except (TypeError, ValueError) as e:
            return {"ok": False, "error": "ValueError", "message": str(e), "asked_total": total, **self._state()}
        return {"ok": True, "asked_total": total, "spent": lg.spent, "total": lg.total}

    def c11_state(self) -> dict:
        return {"ok": True, **self._state(), "table_eps": TABLE_EPS, "tables": list(self.dp_tables)}


def run_script(sess: Session) -> list[dict]:
    """The scripted attack sequence used for REPLAY transcripts and the smoke test's live round-trip."""
    out = []
    for name, label, fields in C5_SCRIPT:
        out.append({"step": f"c5:{name}", "label": label, "result": sess.c5_request(fields)})
    target = next(s["result"]["entry"]["seq"] for s in out if s["step"] == "c5:bc_other_bank")
    for kind in ("delete", "flip", "forge", "keyed_suffix"):
        out.append({"step": f"tamper:{kind}", "label": TAMPER_KINDS[kind], "result": sess.c5_tamper(kind, target)})
    out.append({"step": "c5:log", "label": "The real log after the attacks", "result": sess.c5_log()})
    out.append({"step": "c11:release:district_usage", "label": "SLBC district table", "result": sess.c11_release("district_usage")})
    out.append({"step": "c11:race", "label": "Two forums spend the last epsilon at once", "result": sess.c11_race()})
    out.append({"step": "c11:release:district_usage_60plus", "label": "One more table", "result": sess.c11_release("district_usage_60plus")})
    out.append({"step": "c11:charge:refund", "label": "Refund with a negative epsilon", "result": sess.c11_charge(-0.5)})
    out.append({"step": "c11:charge:nan", "label": "Charge NaN", "result": sess.c11_charge("nan")})
    out.append({"step": "c11:restart", "label": "Restart and try again", "result": sess.c11_restart()})
    out.append({"step": "c11:reopen", "label": "Reopen the ledger with a bigger total", "result": sess.c11_reopen(2.0)})
    return out


def summarize(steps: list[dict]) -> list[dict]:
    """Key-independent view of a transcript (decisions, rules, verdicts, budget outcomes) for live-vs-replay checks."""
    out = []
    for s in steps:
        r, k = s["result"], s["step"]
        if k.startswith("c5:") and k != "c5:log":
            out.append((k, r["ok"], r["decision"]["allow"], r["decision"]["rule_ids"][0]) if r["ok"] else (k, False, r["error"]))
        elif k.startswith("tamper:"):
            out.append((k, r["verify"]["valid"], r["verify"]["full_integrity"], r["verify"]["unanchored"]))
        elif k == "c5:log":
            out.append((k, len(r["entries"]), r["verify"]["full_integrity"]))
        elif k == "c11:race":
            out.append((k, r["winners"], r["spent"]))
        elif k == "c11:restart":
            out.append((k, r["reloaded"]["spent"], r["charge_after_restart"]["ok"]))
        else:
            out.append((k, r["ok"], r.get("error"), r.get("spent")))
    return [list(x) for x in out]
