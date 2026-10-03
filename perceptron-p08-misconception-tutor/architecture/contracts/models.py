"""Typed contracts between P8 components.

Every component consumes and returns these models; components never pass raw
dicts across a seam. Changing a field is an architecture decision owned by the
lead: bump CONTRACT_VERSION and record it in architecture/components.md.

Glossary (see architecture/components.md):
- Misconception: a systematic, predictable error pattern (Eedi's definition).
- Bug program: an executable rule that maps an Item's parameters to the wrong
  answer a learner holding one misconception would give (None = not applicable).
- Discriminative item: every applicable bug yields a wrong answer that differs
  from the key and from every other applicable bug's answer, so one response
  identifies the misconception.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

CONTRACT_VERSION = "0.1.0"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Domain(str, Enum):
    SCHOOL_MATH = "school_math"
    PROBABILITY = "probability"
    PYTHON = "python"


class Misconception(BaseModel):
    misconception_id: str  # "eedi:<id>" or "pack:<CODE>"
    name: str
    description: str = ""
    domain: Domain
    category: Optional[str] = None  # MVP category (one of 3-5) this maps to, if any
    eedi_ids: list[int] = Field(default_factory=list)
    construct_ids: list[int] = Field(default_factory=list)
    executable: bool = False  # True when a validated bug program exists
    source: str  # provenance: URL or dataset id


class Option(BaseModel):
    label: str  # "A".."D"
    text: str
    value: Optional[str] = None  # canonical value (see Normalizer)
    misconception_id: Optional[str] = None  # misconception predicting this option; None for the key
    is_key: bool = False


class Item(BaseModel):
    item_id: str
    domain: Domain
    family: Optional[str] = None  # problem family, e.g. "frac_add"
    params: dict = Field(default_factory=dict)
    stem: str
    answer_key: str  # canonical correct value
    options: list[Option] = Field(default_factory=list)  # empty => free response
    target_misconception_id: Optional[str] = None
    provenance: Literal["template", "llm", "eedi", "hand"] = "template"
    construct: Optional[str] = None


class Response(BaseModel):
    learner_id: str
    session_id: str
    item_id: str
    answer_raw: str
    explanation: Optional[str] = None
    timestamp: datetime = Field(default_factory=utcnow)


class NormalizedAnswer(BaseModel):
    raw: str
    value: Optional[str]  # canonical string; None when parsing failed
    parse_ok: bool
    kind: Literal["number", "fraction", "expression", "option", "text", "code_output"]


class PredictedAnswer(BaseModel):
    misconception_id: str
    value: Optional[str]  # canonical wrong answer; None => bug not applicable to this item


class Hypothesis(BaseModel):
    misconception_id: str
    prob: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)  # e.g. "bug_exact", "retrieval:0.71", "rerank"


class DiagnosisRequest(BaseModel):
    item: Item
    response: Response
    predicted: list[PredictedAnswer] = Field(default_factory=list)  # from the bug library, if any
    candidates: Optional[list[str]] = None  # closed set (MVP: 3-5 categories); None => open catalogue
    top_k: int = 25


class Diagnosis(BaseModel):
    item_id: str
    is_correct: bool
    hypotheses: list[Hypothesis]  # sorted by prob, descending
    p_slip: float = Field(ge=0.0, le=1.0)  # probability the error is non-systematic / unexplained
    abstained: bool = False
    method: str
    latency_ms: float = 0.0


class VerificationReport(BaseModel):
    item_id: str
    well_formed: bool
    key_verified: bool
    key_method: Literal["sympy", "exec", "none"]
    target_fires: bool  # target bug applies and its answer differs from the key
    discriminative: bool  # applicable bug answers pairwise distinct and all differ from the key
    n_competitors_separated: int = 0
    issues: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.well_formed and self.key_verified and self.target_fires


class GenerationRequest(BaseModel):
    target_misconception_id: str
    competitor_ids: list[str] = Field(default_factory=list)  # misconceptions to separate from
    domain: Domain = Domain.SCHOOL_MATH
    family: Optional[str] = None
    n: int = 1
    seed: int = 0
    exclude_item_ids: list[str] = Field(default_factory=list)
    as_mcq: bool = True


class GeneratedItem(BaseModel):
    item: Item
    predicted: list[PredictedAnswer]
    verification: VerificationReport
    generator: str  # e.g. "template-discriminative-v0", "llm:openai/gpt-4.1-mini"


class Observation(BaseModel):
    item_id: str
    session_id: str
    correct: bool
    answer_value: Optional[str]
    matched_misconceptions: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=utcnow)


class MisconceptionBelief(BaseModel):
    misconception_id: str
    p_holds: float = Field(ge=0.0, le=1.0)
    n_evidence: int = 0
    last_updated: Optional[datetime] = None


class LearnerState(BaseModel):
    learner_id: str
    beliefs: dict[str, MisconceptionBelief] = Field(default_factory=dict)
    history: list[Observation] = Field(default_factory=list)
    sessions: list[str] = Field(default_factory=list)
    contract_version: str = CONTRACT_VERSION


class NextItemRequest(BaseModel):
    state: LearnerState
    mode: Literal["diagnose", "remediate", "auto"] = "auto"
    candidate_items: list[GeneratedItem] = Field(default_factory=list)  # empty => policy asks the generator


class NextItemDecision(BaseModel):
    item: GeneratedItem
    mode: Literal["diagnose", "remediate"]
    expected_info_gain: Optional[float] = None  # nats
    rationale: str
