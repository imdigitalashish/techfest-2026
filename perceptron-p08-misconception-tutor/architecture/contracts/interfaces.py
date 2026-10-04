"""Component interfaces (typing.Protocol). Implementations live in components/<name>/.

Call graph (who calls whom, in what shape):
  Tutor -> Normalizer.normalize(raw, item) -> NormalizedAnswer
  Tutor -> BugLibrary.predict(item) -> list[PredictedAnswer]
  Tutor -> Diagnoser.diagnose(DiagnosisRequest) -> Diagnosis
  Tutor -> LearnerModel.update(state, item, response, diagnosis, predicted) -> LearnerState
  Tutor -> Policy.next_item(NextItemRequest) -> NextItemDecision
  Policy -> Generator.generate(GenerationRequest) -> list[GeneratedItem]
  Generator -> BugLibrary.predict(item) and Verifier.verify(item, predicted) -> VerificationReport
  Eval/Simulator -> SimLearner.answer(item, predicted, rng) -> Response
"""
from __future__ import annotations

import random
from typing import Optional, Protocol, runtime_checkable

from .models import (
    Diagnosis,
    DiagnosisRequest,
    GeneratedItem,
    GenerationRequest,
    Item,
    LearnerState,
    Misconception,
    NextItemDecision,
    NextItemRequest,
    NormalizedAnswer,
    PredictedAnswer,
    Response,
    VerificationReport,
)


@runtime_checkable
class Catalogue(Protocol):
    def get(self, misconception_id: str) -> Misconception: ...
    def all(self) -> list[Misconception]: ...


@runtime_checkable
class Normalizer(Protocol):
    def normalize(self, raw: str, item: Item) -> NormalizedAnswer: ...


@runtime_checkable
class BugLibrary(Protocol):
    def misconceptions(self) -> list[Misconception]: ...
    def predict(self, item: Item) -> list[PredictedAnswer]: ...


@runtime_checkable
class ComposableBugLibrary(BugLibrary, Protocol):
    def predict_set(self, item: Item, misconception_ids: list[str]) -> Optional[str]: ...


@runtime_checkable
class Diagnoser(Protocol):
    def diagnose(self, req: DiagnosisRequest) -> Diagnosis: ...


@runtime_checkable
class Verifier(Protocol):
    def verify(self, item: Item, predicted: list[PredictedAnswer]) -> VerificationReport: ...


@runtime_checkable
class Generator(Protocol):
    def generate(self, req: GenerationRequest) -> list[GeneratedItem]: ...


@runtime_checkable
class LearnerModel(Protocol):
    def start_session(self, state: LearnerState, session_id: str) -> LearnerState: ...
    def update(
        self,
        state: LearnerState,
        item: Item,
        response: Response,
        diagnosis: Diagnosis,
        predicted: list[PredictedAnswer],
    ) -> LearnerState: ...


@runtime_checkable
class Policy(Protocol):
    def next_item(self, req: NextItemRequest) -> NextItemDecision: ...


@runtime_checkable
class SimLearner(Protocol):
    learner_id: str

    def answer(self, item: Item, predicted: list[PredictedAnswer], rng: random.Random) -> Response: ...
    def receive_feedback(self, item: Item, diagnosis: Diagnosis, targeted: bool, rng: random.Random) -> None: ...
    def holds(self) -> set[str]: ...
