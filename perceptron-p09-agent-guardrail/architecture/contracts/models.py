"""Typed contracts shared by every component (source of truth for architecture/contracts/).

Flow: Agent proposes a ToolCall -> Guard receives GuardRequest(call, context) -> returns Verdict.
Only Verdict.decision == ALLOW lets the tool executor run the call.
Run `python -m architecture.contracts.export_schemas` to regenerate the JSON Schemas in schemas/.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Trust(str, Enum):
    """Where a piece of context came from. Intent-bearing arguments may only be grounded in trusted sources."""

    USER = "user"            # the principal's own words
    KB = "kb"                # reference knowledge base (instrument master, accounts, limits, policy)
    TOOL_DATA = "tool_data"  # structured output of a read tool backed by the KB/simulator
    UNTRUSTED = "untrusted"  # free text from outside (emails, tickets, web): never a source of intent


class ToolCall(BaseModel):
    """An action the agent proposes. Nothing has executed yet."""

    call_id: str
    tool: str
    args: dict[str, Any]


class Observation(BaseModel):
    """Result of an earlier tool call in the same episode."""

    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    result: Any
    trust: Trust = Trust.TOOL_DATA


class Principal(BaseModel):
    """Who the agent acts for."""

    user_id: str
    name: str


class SessionState(BaseModel):
    """Side effects already committed in this episode (for idempotency / reference checks)."""

    orders: list[dict[str, Any]] = Field(default_factory=list)
    transfers: list[dict[str, Any]] = Field(default_factory=list)
    messages: list[dict[str, Any]] = Field(default_factory=list)


class Context(BaseModel):
    principal: Principal
    user_request: str
    observations: list[Observation] = Field(default_factory=list)
    state: SessionState = Field(default_factory=SessionState)


class GuardRequest(BaseModel):
    call: ToolCall
    context: Context


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"                   # contradicted by a source, or a precondition is violated
    UNVERIFIABLE = "unverifiable"   # no trusted source supports it (absence of evidence)
    NEEDS_APPROVAL = "needs_approval"  # grounded, but policy requires a human


class Evidence(BaseModel):
    source: Trust
    locator: str      # e.g. "kb:instruments/RELIANCE", "user_request[12:19]", "obs[0].result.last"
    snippet: str


class CheckResult(BaseModel):
    check_id: str     # e.g. "provenance.quantity", "pretrade.price_collar"
    arg: str | None = None
    status: CheckStatus
    message: str
    evidence: list[Evidence] = Field(default_factory=list)
    tier: int = 0


class Decision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"        # do not execute; feedback goes back to the agent so it can repair
    ESCALATE = "escalate"  # pause; ask the human (user or desk supervisor)


class Verdict(BaseModel):
    call_id: str
    decision: Decision
    risk: float = Field(ge=0.0, le=1.0)
    tiers_run: list[int]
    checks: list[CheckResult]
    feedback: str           # natural-language reason, written for the agent to self-correct
    latency_ms: float
    guard: str              # which guard produced it (baseline name or "cascade")


class SuiteItem(BaseModel):
    """One red-team / regression case: a context plus a proposed call with a ground-truth label."""

    item_id: str
    split: Literal["dev", "test"]
    family: str                  # template family (splits are by family to avoid phrasing leakage)
    context: Context
    call: ToolCall
    should_execute: bool         # ground truth: may this call run without human intervention?
    hallucination_class: str     # "none" for good actions, else the mutation class
    mutation: str | None = None  # operator that produced it
    notes: str = ""


class GuardFn:  # documentation-only protocol
    """A guard is any callable: (GuardRequest) -> Verdict. It must not mutate the request."""
