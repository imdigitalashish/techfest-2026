"""Tier 0: deterministic checks. Per-argument provenance + pre-trade-style preconditions from the KB.

Every check returns PASS / FAIL / UNVERIFIABLE / NEEDS_APPROVAL with evidence and the policy clause.
"""
from __future__ import annotations

import re
from typing import Any

from architecture.contracts.models import CheckResult, CheckStatus as S, Context, Evidence, ToolCall, Trust
from components.checker.provenance import Mentions, find_in_observations, trusted
from components.kb.kb import ReferenceKB

GUARANTEE = re.compile(r"\b(guarantee[sd]?|assured|risk[- ]free|sure[- ]shot|certain to|will definitely|cannot lose)\b", re.I)
WAIVER = re.compile(r"\b(waive[sd]?|waiver|refund(?:ed)?|free of charge|no charges?)\b", re.I)
STATUS_CLAIM = re.compile(r"\b(placed|filled|executed|cancell?ed|transferred)\b", re.I)
STATUS_WORDS = {"filled": "filled", "executed": "filled", "cancelled": "cancelled", "canceled": "cancelled",
                "open": "open", "pending": "open", "placed": "open"}
STATUS_RE = re.compile(r"\b(filled|executed|cancell?ed|open|pending|placed)\b", re.I)
NUM_CLAIM = re.compile(r"(₹\s?\d[\d,]*(?:\.\d+)?|\d+(?:\.\d+)?\s?%)")


def C(cid, arg, status, msg, ev=None, tier=0) -> CheckResult:
    return CheckResult(check_id=cid, arg=arg, status=status, message=msg, evidence=ev or [], tier=tier)


def kb_ev(locator: str, snippet: str) -> Evidence:
    return Evidence(source=Trust.KB, locator=locator, snippet=snippet[:160])


def user_ev(m: Mentions, span: tuple[int, int]) -> Evidence:
    return Evidence(source=Trust.USER, locator=f"user_request[{span[0]}:{span[1]}]", snippet=m.text[span[0]:span[1]])


def _intent(tool: str, m: Mentions) -> CheckResult:
    if tool in m.tool_intents:
        return C("provenance.intent", None, S.PASS, f"user request asks for {tool}")
    return C("provenance.intent", None, S.UNVERIFIABLE, f"the user's request does not ask for {tool} (P-1.2)")


def _injected(ctx: Context, value: Any, arg: str) -> CheckResult | None:
    evs = find_in_observations(ctx, value)
    if evs and not trusted(evs):
        return C(f"provenance.{arg}", arg, S.FAIL,
                 f"{arg}={value!r} appears only in untrusted content ({evs[0].locator}); not a client instruction (P-1.3)", evs[:1])
    return None


def _excluded(value: str, m: Mentions, arg: str) -> list[CheckResult]:
    if value in m.excluded:
        return [C(f"provenance.{arg}", arg, S.FAIL, f"the user explicitly excluded {value}")]
    return []


def check_account(acct: str, ctx: Context, kb: ReferenceKB, m: Mentions, arg: str, role_hint: str | None = None) -> list[CheckResult]:
    out = _excluded(acct, m, arg)
    rec = kb.accounts.get(acct)
    if rec is None:
        out.append(C("pretrade.account_exists", arg, S.FAIL, f"account {acct} does not exist in the account master"))
    elif rec["owner_id"] != ctx.principal.user_id:
        out.append(C("pretrade.account_owner", arg, S.FAIL,
                     f"account {acct} is not owned by {ctx.principal.name} (P-1.1/P-5.1)", [kb_ev(f"kb:accounts/{acct}", f"owner={rec['owner_id']}")]))
    elif rec["status"] != "active" and arg != "to_account":
        out.append(C("pretrade.account_active", arg, S.FAIL, f"account {acct} is {rec['status']}", [kb_ev(f"kb:accounts/{acct}", f"status={rec['status']}")]))
    # provenance
    said = [(a, sp) for a, sp in m.accounts]
    if role_hint:
        rm = re.search(role_hint + r"\s+(?:account\s+)?(A-\d{4})", m.text, re.I)
        if rm:
            said = [(rm.group(1), rm.span(1))]
    hit = [sp for a, sp in said if a == acct]
    if hit:
        out.append(C(f"provenance.{arg}", arg, S.PASS, f"{arg} stated by user", [user_ev(m, hit[0])]))
    elif said:
        out.append(C(f"provenance.{arg}", arg, S.FAIL, f"user said {', '.join(a for a, _ in said)}; call uses {acct}", [user_ev(m, said[0][1])]))
    else:
        inj = _injected(ctx, acct, arg)
        if inj:
            out.append(inj)
        else:
            owned = [a for a in kb.accounts_of(ctx.principal.user_id) if a["status"] == "active"]
            if len(owned) == 1 and owned[0]["account_id"] == acct and arg != "to_account":
                out.append(C(f"provenance.{arg}", arg, S.PASS, "client's only active account",
                             [kb_ev(f"kb:accounts?owner={ctx.principal.user_id}", acct)]))
            else:
                out.append(C(f"provenance.{arg}", arg, S.UNVERIFIABLE, f"user never named account {acct}; agent chose it (P-1.2)"))
    return out


def check_place_order(call: ToolCall, ctx: Context, kb: ReferenceKB, m: Mentions) -> list[CheckResult]:
    a, L = call.args, kb.limits
    out = [_intent("place_order", m)]
    out += check_account(str(a.get("account_id")), ctx, kb, m, "account_id")
    sym, side, qty = str(a.get("symbol", "")).upper(), a.get("side"), a.get("quantity")
    out += _excluded(sym, m, "symbol")
    otype, px = a.get("order_type"), a.get("limit_price")
    rec = kb.instruments.get(sym)
    if rec is None:
        out.append(C("pretrade.instrument_exists", "symbol", S.FAIL, f"{sym} is not in the instrument master (P-2.1)"))
    else:
        if rec["status"] != "active":
            out.append(C("pretrade.instrument_active", "symbol", S.FAIL, f"{sym} is {rec['status']} (P-2.1)", [kb_ev(f"kb:instruments/{sym}", f"status={rec['status']}")]))
        if sym in kb.restricted:
            out.append(C("pretrade.restricted", "symbol", S.FAIL, f"{sym} is on the restricted list (P-2.2)", [kb_ev(f"kb:restricted/{sym}", kb.restricted[sym]["reason"])]))
    said_syms = [(s, sp) for s, sp in m.instruments]
    hit = [sp for s, sp in said_syms if s == sym]
    if hit:
        out.append(C("provenance.symbol", "symbol", S.PASS, "instrument named by user", [user_ev(m, hit[0])]))
    elif said_syms:
        out.append(C("provenance.symbol", "symbol", S.FAIL, f"user asked about {', '.join(sorted({s for s, _ in said_syms}))}; call trades {sym}", [user_ev(m, said_syms[0][1])]))
    else:
        out.append(_injected(ctx, sym, "symbol") or C("provenance.symbol", "symbol", S.UNVERIFIABLE, f"user never named an instrument; call trades {sym}"))
    # side
    if m.side == side:
        out.append(C("provenance.side", "side", S.PASS, f"user asked to {side}"))
    elif m.side:
        out.append(C("provenance.side", "side", S.FAIL, f"user asked to {m.side}; call would {side}"))
    else:
        out.append(C("provenance.side", "side", S.UNVERIFIABLE, "user's request does not state buy or sell"))
    # quantity
    qn = [n for n in m.numbers if n.kind == "qty"] or [n for n in m.numbers if n.kind == "unknown"]
    if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
        out.append(C("pretrade.quantity_valid", "quantity", S.FAIL, f"quantity {qty!r} is not a positive integer"))
        qty = 0
    hitq = [n for n in qn if abs(n.value - qty) < 1e-9]
    if hitq:
        out.append(C("provenance.quantity", "quantity", S.PASS, "quantity stated by user", [user_ev(m, hitq[0].span)]))
    elif qn:
        out.append(C("provenance.quantity", "quantity", S.FAIL, f"user said {qn[0].text}; call has {qty}", [user_ev(m, qn[0].span)]))
    else:
        out.append(C("provenance.quantity", "quantity", S.UNVERIFIABLE, f"user never stated a quantity; call has {qty}"))
    if qty > L["max_order_qty"]:
        out.append(C("pretrade.max_qty", "quantity", S.FAIL, f"{qty} shares exceeds the {L['max_order_qty']}-share order limit (P-3.2)"))
    # order type and price
    pn = [n for n in m.numbers if n.kind == "price"]
    ref = rec["ref_price"] if rec else None
    if otype == "market":
        if pn and not m.market:
            out.append(C("provenance.order_type", "order_type", S.FAIL, f"user gave a limit price ({pn[0].text}); call is a market order", [user_ev(m, pn[0].span)]))
        elif m.market:
            out.append(C("provenance.order_type", "order_type", S.PASS, "user asked for a market order"))
        else:
            out.append(C("provenance.order_type", "order_type", S.UNVERIFIABLE, "user did not choose market vs limit (P-1.2)"))
        if qty > L["max_market_order_qty"]:
            out.append(C("pretrade.market_qty", "quantity", S.FAIL, f"market orders are limited to {L['max_market_order_qty']} shares (P-3.5)"))
        px_eff = ref
    else:
        if px is None:
            out.append(C("pretrade.limit_price_present", "limit_price", S.FAIL, "limit order without a limit price"))
            px_eff = ref
        else:
            px = float(px)
            px_eff = px
            hitp = [n for n in pn if abs(n.value - px) < 1e-6]
            if hitp:
                out.append(C("provenance.limit_price", "limit_price", S.PASS, "limit price stated by user", [user_ev(m, hitp[0].span)]))
            elif pn:
                out.append(C("provenance.limit_price", "limit_price", S.FAIL, f"user said {pn[0].text}; call has {px}", [user_ev(m, pn[0].span)]))
            else:
                obs = [e for e in trusted(find_in_observations(ctx, px, rel_tol=1e-9)) if e.source == Trust.TOOL_DATA]
                if obs:
                    out.append(C("provenance.limit_price", "limit_price", S.PASS, "limit price taken from a quote", obs[:1]))
                else:
                    out.append(_injected(ctx, px, "limit_price") or C("provenance.limit_price", "limit_price", S.UNVERIFIABLE, f"price {px} was neither stated by the user nor seen in a quote"))
            if rec:
                dev = abs(px - ref) / ref * 100
                if dev > L["price_collar_pct"]:
                    out.append(C("pretrade.price_collar", "limit_price", S.FAIL, f"{px} is {dev:.1f}% from the reference price {ref} (collar ±{L['price_collar_pct']}%, P-3.1)", [kb_ev(f"kb:instruments/{sym}.ref_price", str(ref))]))
                t = rec["tick_size"]
                if abs(round(px / t) * t - px) > 1e-6:
                    out.append(C("pretrade.tick", "limit_price", S.FAIL, f"{px} is not a multiple of tick {t} (P-3.6)"))
    # account-level limits
    acct = kb.accounts.get(str(a.get("account_id")))
    if acct and rec and px_eff and qty:
        notional = qty * px_eff
        if notional > acct["max_order_notional"]:
            out.append(C("pretrade.max_notional", None, S.FAIL, f"order value ₹{notional:,.0f} exceeds the account's max order value ₹{acct['max_order_notional']:,} (P-3.4)"))
        if side == "buy" and notional > acct["cash_available"]:
            out.append(C("pretrade.cash", None, S.FAIL, f"order value ₹{notional:,.0f} exceeds available cash ₹{acct['cash_available']:,} (P-3.4)"))
        if side == "sell" and qty > acct["positions"].get(sym, 0):
            out.append(C("pretrade.no_short", "quantity", S.FAIL, f"sell {qty} > position {acct['positions'].get(sym, 0)} {sym} (P-3.3)"))
        if notional >= L["order_approval_notional"]:
            out.append(C("policy.second_approver", None, S.NEEDS_APPROVAL, f"order value ₹{notional:,.0f} needs a second approver (P-4.2)"))
    for o in ctx.state.orders:
        if (o.get("account_id"), o.get("symbol"), o.get("side"), o.get("quantity"), o.get("limit_price")) == (a.get("account_id"), sym, side, a.get("quantity"), a.get("limit_price")):
            out.append(C("pretrade.duplicate", None, S.FAIL, f"identical order {o.get('order_id')} already submitted this session (P-4.1)"))
            break
    return out


def check_transfer(call: ToolCall, ctx: Context, kb: ReferenceKB, m: Mentions) -> list[CheckResult]:
    a, L = call.args, kb.limits
    out = [_intent("transfer_funds", m)]
    src, dst, amt = str(a.get("from_account")), str(a.get("to_account")), a.get("amount")
    out += check_account(src, ctx, kb, m, "from_account", role_hint=r"\bfrom")
    out += check_account(dst, ctx, kb, m, "to_account", role_hint=r"\b(?:to|into)")
    if src == dst:
        out.append(C("pretrade.same_account", None, S.FAIL, "source and destination are the same account"))
    try:
        amt = float(amt)
    except (TypeError, ValueError):
        return out + [C("pretrade.amount_valid", "amount", S.FAIL, f"amount {amt!r} is not a number")]
    an = [n for n in m.numbers if n.kind in ("amount", "unknown")]
    hit = [n for n in an if abs(n.value - amt) < 1e-6]
    if hit:
        out.append(C("provenance.amount", "amount", S.PASS, "amount stated by user", [user_ev(m, hit[0].span)]))
    elif an:
        out.append(C("provenance.amount", "amount", S.FAIL, f"user said {an[0].text}; call moves ₹{amt:,.0f}", [user_ev(m, an[0].span)]))
    else:
        out.append(_injected(ctx, amt, "amount") or C("provenance.amount", "amount", S.UNVERIFIABLE, f"user never stated an amount; call moves ₹{amt:,.0f}"))
    acct = kb.accounts.get(src)
    if acct and amt > acct["cash_available"]:
        out.append(C("pretrade.cash", "amount", S.FAIL, f"₹{amt:,.0f} exceeds available cash ₹{acct['cash_available']:,} (P-5.2)"))
    if amt >= L["transfer_approval_amount"]:
        out.append(C("policy.supervisor", "amount", S.NEEDS_APPROVAL, f"transfer of ₹{amt:,.0f} needs supervisor approval (P-5.3)"))
    return out


def check_cancel(call: ToolCall, ctx: Context, kb: ReferenceKB, m: Mentions) -> list[CheckResult]:
    oid = str(call.args.get("order_id"))
    out = [_intent("cancel_order", m)] + _excluded(oid, m, "order_id")
    order = next((o for o in ctx.state.orders if o.get("order_id") == oid), None)
    if order is None:
        out.append(C("state.order_exists", "order_id", S.FAIL, f"{oid} is not in this session's order record"))
    else:
        acct = kb.accounts.get(order["account_id"], {})
        if acct.get("owner_id") != ctx.principal.user_id:
            out.append(C("pretrade.order_owner", "order_id", S.FAIL, f"{oid} belongs to another client (P-8.2)"))
        if order.get("status") != "open":
            out.append(C("state.order_open", "order_id", S.FAIL, f"{oid} is {order.get('status')}; only open orders can be cancelled (P-8.1)"))
    said = [(o, sp) for o, sp in m.orders]
    hit = [sp for o, sp in said if o == oid]
    if hit:
        out.append(C("provenance.order_id", "order_id", S.PASS, "order id stated by user", [user_ev(m, hit[0])]))
    elif said:
        out.append(C("provenance.order_id", "order_id", S.FAIL, f"user said {said[0][0]}; call cancels {oid}", [user_ev(m, said[0][1])]))
    elif re.search(r"\b(last|latest|previous|that|the)\s+order\b", m.text, re.I) and order is not None:
        mine = [o for o in ctx.state.orders if kb.accounts.get(o["account_id"], {}).get("owner_id") == ctx.principal.user_id]
        ok = bool(mine) and mine[-1]["order_id"] == oid
        out.append(C("provenance.order_id", "order_id", S.PASS if ok else S.FAIL,
                     "user referred to their most recent order" if ok else f"user's most recent order is {mine[-1]['order_id'] if mine else 'none'}, not {oid}"))
    else:
        out.append(C("provenance.order_id", "order_id", S.UNVERIFIABLE, f"user never identified order {oid}"))
    return out


def check_message(call: ToolCall, ctx: Context, kb: ReferenceKB, m: Mentions) -> list[CheckResult]:
    acct, text = str(call.args.get("account_id")), str(call.args.get("text", ""))
    out = [_intent("send_client_message", m)]
    rec = kb.accounts.get(acct)
    if rec is None or rec["owner_id"] != ctx.principal.user_id:
        out.append(C("pretrade.account_owner", "account_id", S.FAIL, f"{acct} is not an account of {ctx.principal.name} (P-1.1/P-6.3)"))
    for cid in set(re.findall(r"\bP-\d+\.\d+\b", text)):
        if cid not in kb.clauses:
            out.append(C("claims.citation", "text", S.FAIL, f"message cites policy {cid}, which does not exist"))
    g = GUARANTEE.search(text)
    if g:
        out.append(C("claims.guarantee", "text", S.FAIL, f"message promises an outcome ('{g.group(0)}') (P-6.1)", [kb_ev("kb:policy/P-6.1", kb.clauses["P-6.1"].text)]))
    w = WAIVER.search(text)
    if w:
        out.append(C("claims.waiver", "text", S.UNVERIFIABLE, f"message mentions '{w.group(0)}'; fee waivers/refunds need compliance (P-7.3) — needs a careful check"))
    state_blob = " ".join(str(v) for o in ctx.state.orders + ctx.state.transfers for v in o.values())
    for tok in NUM_CLAIM.findall(text):
        norm = tok.replace(" ", "")
        digits = re.sub(r"[₹,%]", "", norm)
        in_policy = kb.policy_mentions_number(norm)
        in_state = bool(digits) and (digits in state_blob.replace(",", "") or any(
            abs(float(v) - float(digits)) < 1e-6 for o in ctx.state.orders + ctx.state.transfers for v in o.values()
            if isinstance(v, (int, float)) and not isinstance(v, bool)))
        in_user = digits in m.text.replace(",", "")
        in_obs = bool(trusted(find_in_observations(ctx, float(digits)))) if digits.replace(".", "", 1).isdigit() else False
        if not (in_policy or in_state or in_user or in_obs):
            out.append(C("claims.number", "text", S.UNVERIFIABLE, f"'{tok}' in the message is not supported by policy, the session record or the request"))
    if STATUS_CLAIM.search(text) or STATUS_RE.search(text):
        for oid in set(re.findall(r"\bORD-\d+\b", text)):
            rec_o = next((o for o in ctx.state.orders if o.get("order_id") == oid), None)
            if rec_o is None:
                out.append(C("claims.status", "text", S.FAIL, f"message refers to {oid}, which is not in the session record (P-6.4)"))
                continue
            claimed = {STATUS_WORDS[w.lower()] for w in STATUS_RE.findall(text)}
            actual = str(rec_o.get("status", "")).lower()
            if claimed and actual and actual not in claimed:
                out.append(C("claims.status", "text", S.FAIL, f"message says {oid} is {sorted(claimed)}, the session record says '{actual}' (P-6.4)"))
        claim_sents = [x for x in re.split(r"(?<=[.!?])\s+", text) if STATUS_CLAIM.search(x)]
        positive = [x for x in claim_sents if not re.search(r"\b(no|not|nothing|none|never)\b|n't\b", x, re.I)]
        if positive and not re.findall(r"\bORD-\d+\b", text) and not kb.find_instruments(text):
            claimed = {STATUS_WORDS[w.lower()] for w in STATUS_RE.findall(text)}
            is_transfer = bool(re.search(r"\btransfer", text, re.I))
            records = ctx.state.transfers if is_transfer else ctx.state.orders
            if not records:
                out.append(C("claims.status", "text", S.FAIL, "message reports a completed action, but the session record has none (P-6.4)"))
            elif claimed and not is_transfer and not any(str(o.get("status", "")).lower() in claimed for o in records):
                out.append(C("claims.status", "text", S.FAIL, f"message says an order is {sorted(claimed)}; no order in the session record has that status (P-6.4)"))
        for sym, _ in (kb.find_instruments(text) if STATUS_CLAIM.search(text) else []):
            if not any(o.get("symbol") == sym for o in ctx.state.orders):
                out.append(C("claims.status", "text", S.FAIL, f"message reports an order in {sym}, but the session record has none (P-6.4)"))
    return out


CHECKS = {"place_order": check_place_order, "transfer_funds": check_transfer,
          "cancel_order": check_cancel, "send_client_message": check_message}
