"""C8 Last-mile Orchestrator — PROTOTYPE (built for the demo, 4 Oct 2026). No field data, no performance claim.

Turns plan rows that the C7 gate has cleared into channel tasks (architecture §2: "fraud-gated task list (visit · IVR ·
UPI 123PAY onboarding · re-KYC)"):
  bc_visit    -> channel 'bc_visit'              doorstep visit by the person's BC / BC Sakhi
  upi_onboard -> channel 'bc_assisted_upi123pay' BC-assisted UPI 123PAY onboarding on a feature phone [P10]
  sms_ivr     -> channel 'ivr_sms'               local-language IVR call or SMS
  incentive   -> channel 'incentive_notice'      first-use incentive notice
C7 'hold' -> no task (listed for the bank's risk team with its resolve-by date). C7 'verify' -> a re-KYC step is added.
A BC's list is produced only if C5 allows it: `authorize(bc_id)` must return an AccessDecision (the demo calls
PolicyEngine.request, rule A2), and the decision's `masked_fields` are removed from what the BC sees.
Per-BC daily cap: a design requirement the code review deferred (reviews/2026-10-04-decisions.md, sol #5). The value is an
ASSUMPTION; visits beyond the cap roll to the next day.
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict
from typing import Callable

CAP_PER_BC_DAY = 8  # ASSUMPTION: visits per BC per day (no committed figure)
CHANNEL = {"bc_visit": "bc_visit", "upi_onboard": "bc_assisted_upi123pay", "sms_ivr": "ivr_sms", "incentive": "incentive_notice"}
BC_ARMS = {"bc_visit", "upi_onboard"}
STEP = {  # wording follows the Arm contract comments (architecture/contracts/contracts.py)
    "bc_visit": "Doorstep visit by the BC / BC Sakhi: first transaction with the holder",
    "upi_onboard": "Assisted UPI 123PAY onboarding by the BC on a feature phone (app, missed call, IVR or proximity sound) [P10]",
    "sms_ivr": "Voice/IVR or SMS nudge in the local language",
    "incentive": "Small first-transactions incentive",
}
KYC_BC = "Re-KYC before activation through the BC: self-declaration recorded after biometric e-KYC [P24, P25]"
KYC_REMOTE = "Tell the holder that activation needs KYC first: any branch, V-CIP or an authorised BC [P8, P24]"


def build_tasks(rows: list[dict], decisions: list[dict], start: dt.date,
                authorize: Callable[[str], dict] | None = None, cap_per_bc_day: int = CAP_PER_BC_DAY) -> dict:
    """rows (plan order = priority): account_token, arm, bc_id, reason_codes, language, plus any bank-internal fields.
    decisions: C7 output aligned with rows. Returns ChannelTask contract dicts, BC-facing cards, holds and C5 decisions."""
    if len(rows) != len(decisions):
        raise ValueError("rows and gate decisions must align")
    tasks, cards, held, access, denied = [], [], [], {}, []
    per_bc_day = defaultdict(int)
    n = 0
    for row, dec in zip(rows, decisions):
        arm = row.get("arm", "none")
        if arm == "none" or dec["rule"] == "N0":
            continue
        if dec["decision"] == "hold":
            held.append({"account_token": row["account_token"], "resolve_by": dec["resolve_by"], "appeal": dec["appeal"],
                         "reasons": dec["reasons"]})
            continue
        bc = row.get("bc_id") if arm in BC_ARMS else None
        masked: list[str] = []
        if bc is not None:
            if bc not in access:
                access[bc] = authorize(bc) if authorize else {"allow": False, "rule_ids": ["NO_POLICY_ENGINE"],
                                                              "obligations": {"masked_fields": []}}
                if not access[bc]["allow"]:
                    denied.append(bc)
            if not access[bc]["allow"]:
                continue
            masked = list(access[bc]["obligations"].get("masked_fields", []))
            day = per_bc_day[bc] // max(1, cap_per_bc_day)
            per_bc_day[bc] += 1
        else:
            day = 0
        n += 1
        task = {"task_id": f"T{n:06d}", "account_token": row["account_token"], "arm": arm, "channel": CHANNEL[arm],
                "assigned_bc_id": bc, "language": row.get("language", "holder's language (bank record)"),
                "due_date": (start + dt.timedelta(days=day)).isoformat()}
        steps = [STEP[arm]]
        if dec["decision"] == "verify":
            steps.append(KYC_BC if bc is not None else KYC_REMOTE)
        visible = {k: v for k, v in row.items() if k not in masked}
        tasks.append(task)
        cards.append({**task, "reason_codes": row.get("reason_codes", ""), "steps": steps, "gate": dec["decision"],
                      "gate_rule": dec["rule"], "masked": masked, "visible_fields": sorted(visible)})
    return {"tasks": tasks, "cards": cards, "held": held, "access": access, "denied_bcs": denied}
