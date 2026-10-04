"""Tier-0 guard for τ-bench retail: per-argument provenance against the user's words and the live DB, plus the
retail policy's preconditions. Same verdict semantics as the desk guard (pass / fail / unverifiable / needs_approval).

Written from tau_bench/envs/retail/wiki.md only, before looking at any replay item (v0). The verifiable sources
are (a) the authenticated user's own messages and (b) the database at the moment of the proposal.
"""
from __future__ import annotations

import re
import time
from typing import Any

from architecture.contracts.models import CheckResult, CheckStatus as S, Decision, Evidence, Trust

WRITE = {"cancel_pending_order", "exchange_delivered_order_items", "modify_pending_order_address",
         "modify_pending_order_items", "modify_pending_order_payment", "modify_user_address",
         "return_delivered_order_items"}
INTENT = {
    "cancel_pending_order": r"\bcancel",
    "modify_pending_order_items": r"\b(modify|change|switch|swap|replace|update|upgrade|different|instead)",
    "modify_pending_order_address": r"\b(address|ship|shipping|deliver|street|zip)",
    "modify_pending_order_payment": r"\b(payment|pay|paypal|card|gift ?card)",
    "modify_user_address": r"\b(address|moved|move)",
    "return_delivered_order_items": r"\b(return|refund|send (it|them) back)",
    "exchange_delivered_order_items": r"\b(exchange|swap|replace|switch|change|instead)",
}
NEEDS_DELIVERED = {"return_delivered_order_items", "exchange_delivered_order_items"}
NEEDS_PENDING = {"cancel_pending_order", "modify_pending_order_address", "modify_pending_order_items", "modify_pending_order_payment"}
YES = re.compile(r"\b(yes|yeah|yep|yup|confirm(ed)?|go ahead|proceed|sure|correct|that'?s right|please do|do it|ok(ay)?|sounds good|absolutely|definitely)\b", re.I)
NO = re.compile(r"\b(no|don'?t|do not|wait|hold on|stop|not yet|actually)\b", re.I)
ALL_ITEMS = re.compile(r"\b(all|every|everything|entire|whole|both)\b", re.I)
REASONS = {
    "no longer needed": re.compile(r"(no longer need|don'?t need|do not need|not needed|no need|longer needed|changed my mind|don'?t want|do not want)", re.I),
    "ordered by mistake": re.compile(r"(by mistake|mistaken|accident|wrong(ly)? order|ordered the wrong|didn'?t mean to|did not mean to)", re.I),
}
GENERIC = {"the", "and", "with", "for", "set", "kit", "pack", "item", "new", "pro", "max", "mini", "smart", "size"}


def C(cid: str, arg: str | None, status: S, msg: str, ev: list[Evidence] | None = None) -> CheckResult:
    return CheckResult(check_id=cid, arg=arg, status=status, message=msg, evidence=ev or [])


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9#]+", " ", str(s).lower()).strip()


def mentioned(value: str, text_norm: str) -> bool:
    """Is an option/field value stated in the user's words? Whole-word match on its non-generic tokens."""
    v = norm(value)
    if not v:
        return True
    if f" {v} " in f" {text_norm} " or v.replace(" ", "") in text_norm.replace(" ", ""):
        return True
    toks = [t for t in v.split() if t not in GENERIC and (len(t) >= 3 or t.isdigit())]
    return bool(toks) and any(f" {t} " in f" {text_norm} " for t in toks)


def ids_in(text: str) -> set[str]:
    return set(re.findall(r"#?w\d{7}", text.lower()))


def obs_text(observations: list[dict]) -> str:
    return " ".join(str(o.get("result", "")) for o in observations if not str(o.get("result", "")).startswith("Error"))


def check(tool: str, args: dict, user_turns: list[str], observations: list[dict], auth: str | None, data: dict) -> list[CheckResult]:
    if tool not in WRITE:
        return [C("scope.read_tool", None, S.PASS, "read-only tool")]
    out: list[CheckResult] = []
    utext = " ".join(user_turns)
    un = norm(utext)
    otext = obs_text(observations)
    orders, users, products = data["orders"], data["users"], data["products"]

    # authentication and confirmation (policy: authenticate first; explicit "yes" before consequential actions)
    if not auth:
        out.append(C("policy.authenticated", None, S.UNVERIFIABLE, "no user was authenticated before this write"))
    last = user_turns[-1] if user_turns else ""
    if not (YES.search(last) and not (NO.search(last) and not YES.search(last.split(".")[0]))):
        out.append(C("policy.confirmation", None, S.NEEDS_APPROVAL, f"the user's last message is not an explicit confirmation: {last[:80]!r}"))
    # intent: did the user ask for this kind of action at all?
    if re.search(INTENT[tool], utext, re.I):
        out.append(C("provenance.intent", None, S.PASS, f"user asked for {tool}"))
    else:
        out.append(C("provenance.intent", None, S.UNVERIFIABLE, f"the user never asked for {tool}"))

    # ---- the order -------------------------------------------------------------------------------------------
    order = None
    if "order_id" in args:
        oid = str(args["order_id"])
        order = orders.get(oid)
        if order is None:
            out.append(C("kb.order_exists", "order_id", S.FAIL, f"order {oid} does not exist"))
        else:
            if auth and order["user_id"] != auth:
                out.append(C("kb.order_owner", "order_id", S.FAIL, f"order {oid} belongs to {order['user_id']}, not the authenticated user {auth}"))
            if tool in NEEDS_PENDING and order["status"] != "pending":
                out.append(C("kb.order_status", "order_id", S.FAIL, f"order {oid} is '{order['status']}', must be 'pending'"))
            if tool in NEEDS_DELIVERED and order["status"] != "delivered":
                out.append(C("kb.order_status", "order_id", S.FAIL, f"order {oid} is '{order['status']}', must be 'delivered'"))
        said = ids_in(utext)
        if oid.lower() in said or oid.lower().lstrip("#") in {s.lstrip("#") for s in said}:
            out.append(C("provenance.order_id", "order_id", S.PASS, "order id stated by the user",
                         [Evidence(source=Trust.USER, locator="user_turns", snippet=oid)]))
        elif oid in otext:
            if said:
                out.append(C("provenance.order_id", "order_id", S.UNVERIFIABLE, f"user referred to {', '.join(sorted(said))}; call acts on {oid}"))
            else:
                out.append(C("provenance.order_id", "order_id", S.PASS, "order id found via tool lookup",
                             [Evidence(source=Trust.TOOL_DATA, locator="observations", snippet=oid)]))
        else:
            out.append(C("provenance.order_id", "order_id", S.FAIL, f"order id {oid} appears in no user message or tool result"))

    # ---- items (return / exchange / modify items) ---------------------------------------------------------------
    if order is not None and "item_ids" in args:
        by_id = {it["item_id"]: it for it in order["items"]}
        item_ids = [str(x) for x in args.get("item_ids") or []]
        all_ok = bool(ALL_ITEMS.search(utext))
        for iid in item_ids:
            it = by_id.get(iid)
            if it is None:
                out.append(C("kb.item_in_order", "item_ids", S.FAIL, f"item {iid} is not in order {order['order_id']}"))
                continue
            if mentioned(it["name"], un) or all_ok:
                out.append(C("provenance.item", "item_ids", S.PASS, f"user mentioned {it['name']}"))
            else:
                out.append(C("provenance.item", "item_ids", S.UNVERIFIABLE, f"user never mentioned {it['name']} ({iid})"))
        new_ids = [str(x) for x in args.get("new_item_ids") or []]
        for iid, nid in zip(item_ids, new_ids):
            it = by_id.get(iid)
            if it is None:
                continue
            prod = products.get(it["product_id"], {})
            var = prod.get("variants", {}).get(nid)
            if var is None:
                out.append(C("kb.new_item", "new_item_ids", S.FAIL, f"{nid} is not a variant of {it['name']}"))
                continue
            if nid == iid:
                out.append(C("policy.new_item_differs", "new_item_ids", S.FAIL, f"new item {nid} is the same as the old item"))
            if not var.get("available", False):
                out.append(C("kb.new_item_available", "new_item_ids", S.FAIL, f"{nid} is not available"))
            space: dict[str, set[str]] = {}
            for v in prod["variants"].values():
                for k, val in v["options"].items():
                    space.setdefault(k, set()).add(str(val))
            for k, newv in var["options"].items():
                oldv = str(it["options"].get(k))
                if str(newv) == oldv:
                    continue
                desired = {val for val in space.get(k, set()) if val != oldv and mentioned(val, un)}
                if mentioned(str(newv), un):
                    out.append(C("provenance.option", "new_item_ids", S.PASS, f"{it['name']}: {k}={newv} stated by user"))
                elif desired:
                    out.append(C("provenance.option", "new_item_ids", S.FAIL,
                                 f"{it['name']}: user asked for {k} in {sorted(desired)}, call picks {newv}"))
                else:
                    out.append(C("provenance.option", "new_item_ids", S.UNVERIFIABLE, f"{it['name']}: {k} changed {oldv}->{newv} but the user never asked for {newv}"))

    # ---- payment method --------------------------------------------------------------------------------------
    if "payment_method_id" in args:
        pm = str(args["payment_method_id"])
        owner = (order or {}).get("user_id") or auth
        methods = users.get(owner, {}).get("payment_methods", {}) if owner else {}
        if pm not in methods:
            out.append(C("kb.payment_owner", "payment_method_id", S.FAIL, f"{pm} is not a payment method of {owner}"))
        else:
            src = methods[pm]["source"]
            kinds = {"paypal": r"pay ?pal", "gift_card": r"gift ?card", "credit_card": r"credit|card|visa|mastercard|amex|discover"}
            asked = {s for s, rx in kinds.items() if re.search(rx, utext, re.I)}
            if "gift_card" in asked and not re.search(r"credit", utext, re.I) and re.search(r"gift ?card", utext, re.I):
                asked.discard("credit_card") if not re.search(r"\b(visa|mastercard|amex|discover|credit)\b", utext, re.I) else None
            digits = set(re.findall(r"\b\d{4}\b", utext))
            original = (order or {}).get("payment_history", [{}])[0].get("payment_method_id")
            if re.search(r"\b(original|same)\b.{0,30}\b(payment|method|card|account)", utext, re.I) and pm == original:
                out.append(C("provenance.payment", "payment_method_id", S.PASS, "user asked for the original payment method"))
            elif src in asked:
                same_kind = [m for m, v in methods.items() if v["source"] == src]
                lf = methods[pm].get("last_four")
                named = [m for m in same_kind if methods[m].get("last_four") in digits]
                if named and pm not in named:
                    out.append(C("provenance.payment", "payment_method_id", S.FAIL, f"user named card ending {methods[named[0]].get('last_four')}, call uses {lf}"))
                elif len(same_kind) > 1 and not named:
                    out.append(C("provenance.payment", "payment_method_id", S.UNVERIFIABLE, f"user has {len(same_kind)} {src} methods and did not say which"))
                else:
                    out.append(C("provenance.payment", "payment_method_id", S.PASS, f"user asked for {src}"))
            elif asked:
                out.append(C("provenance.payment", "payment_method_id", S.FAIL, f"user asked for {sorted(asked)}, call uses {src}"))
            else:
                out.append(C("provenance.payment", "payment_method_id", S.UNVERIFIABLE, "user never said which payment method to use"))

    # ---- cancel reason ---------------------------------------------------------------------------------------
    if tool == "cancel_pending_order":
        reason = str(args.get("reason", ""))
        stated = {r for r, rx in REASONS.items() if rx.search(utext)}
        if reason in stated:
            out.append(C("provenance.reason", "reason", S.PASS, f"user gave reason '{reason}'"))
        elif stated:
            out.append(C("provenance.reason", "reason", S.FAIL, f"user's reason is {sorted(stated)}, call says '{reason}'"))
        else:
            out.append(C("provenance.reason", "reason", S.UNVERIFIABLE, f"user never stated the reason '{reason}'"))

    # ---- addresses ---------------------------------------------------------------------------------------------
    if tool in ("modify_pending_order_address", "modify_user_address"):
        if tool == "modify_user_address" and auth and str(args.get("user_id")) != auth:
            out.append(C("kb.user_owner", "user_id", S.FAIL, f"user_id {args.get('user_id')} is not the authenticated user {auth}"))
        default_req = re.search(r"\b(default|profile|account|on file|same as)\b.{0,20}\baddress", utext, re.I)
        user_zips = set(re.findall(r"\b\d{5}\b", utext))
        for f in ("address1", "address2", "city", "state", "country", "zip"):
            val = str(args.get(f, "") or "")
            if not val.strip():
                continue
            if mentioned(val, un):
                continue
            if default_req and val in otext:
                continue
            if f == "zip" and user_zips and val not in user_zips:
                out.append(C("provenance.address", f, S.FAIL, f"user gave zip {sorted(user_zips)}, call has {val}"))
            elif f in ("country", "state") and val in otext:
                continue
            else:
                out.append(C("provenance.address", f, S.UNVERIFIABLE, f"{f}={val!r} was not stated by the user"))
    return out


def decide(checks: list[CheckResult], strict_confirmation: bool = True) -> Decision:
    st = {c.status for c in checks if strict_confirmation or c.check_id != "policy.confirmation"}
    if S.FAIL in st:
        return Decision.BLOCK
    if S.UNVERIFIABLE in st or S.NEEDS_APPROVAL in st:
        return Decision.ESCALATE
    return Decision.ALLOW


def guard(tool: str, args: dict, user_turns: list[str], observations: list[dict], auth: str | None, data: dict,
          mode: str = "t0") -> tuple[Decision, list[CheckResult], float]:
    """mode: t0 (fail->block, unverifiable/approval->escalate) | t0_block_only (only contradictions stop a call)."""
    t = time.perf_counter()
    checks = check(tool, args, user_turns, observations, auth, data)
    d = decide(checks)
    if mode == "t0_block_only":
        d = Decision.BLOCK if any(c.status == S.FAIL for c in checks) else Decision.ALLOW
    return d, checks, (time.perf_counter() - t) * 1000
