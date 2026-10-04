"""Desk tools: specs (JSON Schema, for the agent and for schema validation) + a deterministic simulator.

Write tools have side effects in the simulator; the guard must run before them.
"""
from __future__ import annotations

import copy
import itertools
from typing import Any

from components.kb.kb import ReferenceKB

READ, WRITE = "read", "write"

TOOL_SPECS: dict[str, dict[str, Any]] = {
    "lookup_instrument": {
        "kind": READ, "description": "Find an instrument in the instrument master by name or symbol.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
    "get_quote": {
        "kind": READ, "description": "Latest quote (last, bid, ask) for a symbol.",
        "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]},
    },
    "get_account": {
        "kind": READ, "description": "Account summary: status, cash, positions.",
        "parameters": {"type": "object", "properties": {"account_id": {"type": "string"}}, "required": ["account_id"]},
    },
    "search_policy": {
        "kind": READ, "description": "Search the desk policy.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
    "read_inbox": {
        "kind": READ, "description": "Read the client's latest emails (untrusted external text).",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    "place_order": {
        "kind": WRITE, "description": "Submit an equity order to the exchange.",
        "parameters": {"type": "object", "properties": {
            "account_id": {"type": "string", "pattern": "^A-\\d{4}$"},
            "symbol": {"type": "string"},
            "side": {"type": "string", "enum": ["buy", "sell"]},
            "quantity": {"type": "integer", "minimum": 1},
            "order_type": {"type": "string", "enum": ["market", "limit"]},
            "limit_price": {"type": ["number", "null"]},
        }, "required": ["account_id", "symbol", "side", "quantity", "order_type"]},
    },
    "cancel_order": {
        "kind": WRITE, "description": "Cancel an open order.",
        "parameters": {"type": "object", "properties": {"order_id": {"type": "string", "pattern": "^ORD-\\d+$"}},
                       "required": ["order_id"]},
    },
    "transfer_funds": {
        "kind": WRITE, "description": "Move cash between accounts.",
        "parameters": {"type": "object", "properties": {
            "from_account": {"type": "string", "pattern": "^A-\\d{4}$"},
            "to_account": {"type": "string", "pattern": "^A-\\d{4}$"},
            "amount": {"type": "number", "exclusiveMinimum": 0},
        }, "required": ["from_account", "to_account", "amount"]},
    },
    "send_client_message": {
        "kind": WRITE, "description": "Send a message to the client who owns the account.",
        "parameters": {"type": "object", "properties": {
            "account_id": {"type": "string", "pattern": "^A-\\d{4}$"},
            "text": {"type": "string", "minLength": 1},
        }, "required": ["account_id", "text"]},
    },
}


def openai_tools() -> list[dict[str, Any]]:
    return [{"type": "function", "function": {"name": n, "description": s["description"], "parameters": s["parameters"]}}
            for n, s in TOOL_SPECS.items()]


class DeskSim:
    """In-memory exchange + OMS. Deterministic; quotes are the KB reference price ± one tick."""

    def __init__(self, kb: ReferenceKB, inbox: list[str] | None = None):
        self.kb = kb
        self.accounts = copy.deepcopy(kb.accounts)
        self.orders: list[dict[str, Any]] = []
        self.transfers: list[dict[str, Any]] = []
        self.messages: list[dict[str, Any]] = []
        self.inbox = inbox or []
        self._ids = itertools.count(1)

    def call(self, tool: str, args: dict[str, Any]) -> Any:
        return getattr(self, tool)(**args)

    # read tools
    def lookup_instrument(self, query: str):
        sym = self.kb.resolve_instrument(query)
        return self.kb.instruments[sym] if sym else {"error": f"no instrument matches '{query}'"}

    def get_quote(self, symbol: str):
        r = self.kb.instruments.get(symbol.upper())
        if not r:
            return {"error": f"unknown symbol {symbol}"}
        p, t = r["ref_price"], r["tick_size"]
        return {"symbol": r["symbol"], "last": p, "bid": round(p - t, 2), "ask": round(p + t, 2)}

    def get_account(self, account_id: str):
        a = self.accounts.get(account_id)
        return {k: a[k] for k in ("account_id", "status", "cash_available", "positions")} if a else {"error": "not found"}

    def search_policy(self, query: str):
        return [{"clause_id": c.clause_id, "text": c.text} for c in self.kb.search_policy(query)]

    def read_inbox(self):
        return [{"from": "external", "body": b} for b in self.inbox]

    # write tools
    def place_order(self, account_id, symbol, side, quantity, order_type, limit_price=None):
        oid = f"ORD-{next(self._ids)}"
        o = dict(order_id=oid, account_id=account_id, symbol=symbol, side=side, quantity=quantity,
                 order_type=order_type, limit_price=limit_price, status="open")
        self.orders.append(o)
        return {"order_id": oid, "status": "open"}

    def cancel_order(self, order_id):
        for o in self.orders:
            if o["order_id"] == order_id:
                o["status"] = "cancelled"
                return {"order_id": order_id, "status": "cancelled"}
        return {"error": f"order {order_id} not found"}

    def transfer_funds(self, from_account, to_account, amount):
        self.transfers.append(dict(from_account=from_account, to_account=to_account, amount=amount))
        return {"status": "done"}

    def send_client_message(self, account_id, text):
        self.messages.append(dict(account_id=account_id, text=text))
        return {"status": "sent"}
