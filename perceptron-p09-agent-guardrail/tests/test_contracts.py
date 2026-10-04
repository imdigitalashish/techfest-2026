"""Contract tests: every component honours its typed interface; suite labels are self-consistent."""
from architecture.contracts.models import Context, Decision, GuardRequest, Principal, SuiteItem, ToolCall, Verdict
from components.checker.guard import make
from components.checker.provenance import extract_mentions
from components.kb.kb import ReferenceKB
from components.redteam.build_suite import build
from components.tools.desk import TOOL_SPECS, DeskSim

kb = ReferenceKB()
U1 = Principal(user_id="U1", name="Priya Sharma")


def req(text, tool, **args):
    return GuardRequest(call=ToolCall(call_id="t", tool=tool, args=args), context=Context(principal=U1, user_request=text))


def test_kb_and_aliases():
    assert kb.resolve_instrument("hdfc bank") == "HDFCBANK"
    assert kb.resolve_instrument("Larsen & Toubro") == "LT"
    assert "P-3.1" in kb.clauses and kb.search_policy("price collar")[0].clause_id == "P-3.1"


def test_number_parsing_indian_formats():
    m = extract_mentions("Transfer ₹2,50,000 from A-1001 to A-1002 and 1.5 lakh later", kb)
    assert [n.value for n in m.numbers] == [250000.0, 150000.0]
    assert [a for a, _ in m.accounts] == ["A-1001", "A-1002"]


def test_every_guard_returns_a_verdict():
    r = req("Buy 100 Infosys in A-1001 at ₹1,850 limit.", "place_order", account_id="A-1001", symbol="INFY",
            side="buy", quantity=100, order_type="limit", limit_price=1850.0)
    for g in ("none", "schema", "t0"):
        v = make(g, kb)(r)
        assert isinstance(v, Verdict) and v.call_id == "t"
    assert make("t0", kb)(r).decision == Decision.ALLOW


def test_t0_catches_hallucinated_symbol_and_side():
    base = dict(account_id="A-1001", side="buy", quantity=100, order_type="limit", limit_price=1850.0)
    v = make("t0", kb)(req("Buy 100 Infosys in A-1001 at ₹1,850 limit.", "place_order", symbol="INFOSYS", **base))
    assert v.decision == Decision.BLOCK and any(c.check_id == "pretrade.instrument_exists" for c in v.checks)
    v = make("t0", kb)(req("Buy 100 Infosys in A-1001 at ₹1,850 limit.", "place_order", symbol="INFY", **{**base, "side": "sell"}))
    assert v.decision == Decision.BLOCK


def test_simulator_executes_allowed_call():
    sim = DeskSim(kb)
    assert sim.call("place_order", dict(account_id="A-1001", symbol="INFY", side="buy", quantity=1, order_type="market"))["status"] == "open"
    assert set(TOOL_SPECS) >= {"place_order", "transfer_funds", "cancel_order", "send_client_message"}


def test_suite_labels_consistent():
    items = build()
    assert {i.split for i in items} == {"dev", "test"}
    assert not ({i.family for i in items if i.split == "dev" and i.family in
                 ("order_explicit", "order_market", "transfer_explicit", "cancel_explicit", "msg_confirm", "order_paraphrase")}
                & {i.family for i in items if i.split == "test"})
    for i in items:
        assert isinstance(i, SuiteItem)
        if i.hallucination_class == "approval_required" and i.call.tool == "place_order":
            a = i.call.args
            assert a["quantity"] * a["limit_price"] >= kb.limits["order_approval_notional"], i.item_id
        if i.hallucination_class == "approval_required" and i.call.tool == "transfer_funds":
            assert i.call.args["amount"] >= kb.limits["transfer_approval_amount"], i.item_id
