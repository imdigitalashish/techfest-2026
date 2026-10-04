"""C7 Fraud & Safety Gate — PROTOTYPE (built for the demo, 4 Oct 2026). Transparent rules only.

There is NO risk model here and NO detection-performance claim. The gate turns signals the bank already has into an
auditable decision per planned outreach, so that outreach never reactivates an account without the checks the rules
require. Input rows (one per account the plan would contact):
  account_token, arm, in_holdout, usage_state (C2 behavioural state), regulatory_inoperative (CBS flag), kyc_due,
  on_suspect_list (an external feed, e.g. the bank's list fed by I4C's Suspect Registry [P22]; SYNTHETIC in the demo).
Rules, first match wins (ids are emitted in `reasons`):
  N0 no outreach planned (arm 'none' or holdout)      -> allow  (nothing to gate)
  H1 on the suspect list                               -> hold   (no task; the bank's risk team resolves it by
                                                                  `resolve_by`; the holder can appeal through the
                                                                  bank's grievance channel — proposal §4.3)
  V1 would reactivate a no_use_24m or regulatory-inoperative account
                                                       -> verify (KYC before activation, accepted at any branch, via
                                                                  V-CIP or an authorised BC [P8, P24, P25]; reactivated
                                                                  accounts' transactions are monitored [P8])
  V2 KYC due                                           -> verify (periodic KYC update, same routes [P25])
  A1 otherwise                                         -> allow
`risk_score` is required by the SafetyDecision contract; with no model it only carries the external flag
(1.0 = suspect-list match, else 0.0). SERVICE_DAYS is an ASSUMPTION: the proposal fixes "a fixed service time" without
a number.
"""
from __future__ import annotations

import datetime as dt

SERVICE_DAYS = 7  # ASSUMPTION: service time for resolving a hold (proposal §4.3 names no number)
INACTIVE_STATES = {"no_use_24m"}

RULES = {
    "N0": "No outreach planned (no arm or in the holdout): nothing to gate",
    "H1": "Account is on the bank's suspect list (external feed, e.g. I4C Suspect Registry [P22]): hold, no task",
    "V1": "Outreach would reactivate an inactive account: KYC before activation, at any branch, by V-CIP or through an "
          "authorised BC [P8, P24, P25]; reactivated accounts are monitored [P8]",
    "V2": "KYC is due: periodic KYC update before further outreach, including BC-facilitated self-declaration [P25]",
    "A1": "No rule requires a check: allow",
}


def decide_one(row: dict, today: dt.date) -> dict:
    """Return a SafetyDecision-shaped dict (+ prototype extras: rule, resolve_by, appeal)."""
    tok = str(row["account_token"])
    out = {"account_token": tok, "risk_score": 1.0 if row.get("on_suspect_list") else 0.0}
    if row.get("arm", "none") == "none" or row.get("in_holdout"):
        rule, decision = "N0", "allow"
    elif row.get("on_suspect_list"):
        rule, decision = "H1", "hold"
    elif row.get("usage_state") in INACTIVE_STATES or row.get("regulatory_inoperative"):
        rule, decision = "V1", "verify"
    elif row.get("kyc_due"):
        rule, decision = "V2", "verify"
    else:
        rule, decision = "A1", "allow"
    out.update(decision=decision, reasons=f"{rule}: {RULES[rule]}", rule=rule)
    if decision == "hold":
        out["resolve_by"] = (today + dt.timedelta(days=SERVICE_DAYS)).isoformat()
        out["appeal"] = "bank grievance channel"
    return out


def decide(rows: list[dict], today: dt.date) -> list[dict]:
    return [decide_one(r, today) for r in rows]


def contract_view(decision: dict) -> dict:
    """Only the SafetyDecision contract fields (architecture/contracts/contracts.py)."""
    return {k: decision[k] for k in ("account_token", "decision", "risk_score", "reasons")}
