"""Typed I/O contracts for every component of the P3 "Did-It-Work" system.

Arrays are numpy; shapes are validated at construction (contract tests call these validators).
n = logged rounds, K = actions, d = context dimension.
"""
from __future__ import annotations

from typing import Literal, Optional

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

Arr = np.ndarray


class _M(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)


# C1 LogIngest -> everyone ---------------------------------------------------------------
class BanditLog(_M):
    """Logged bandit feedback from one or two periods (before = 0, after = 1)."""

    X: Arr  # (n, d) float contexts
    A: Arr  # (n,) int actions in [0, K)
    R: Arr  # (n,) float rewards in reward_range
    pscore: Optional[Arr] = None  # (n,) logging propensity pi_b(A_i | X_i); None => unlogged
    period: Arr  # (n,) int in {0, 1}
    n_actions: int
    position: Optional[Arr] = None  # (n,) int slot, for slate data such as OBD
    reward_range: tuple[float, float] = (0.0, 1.0)
    source: str = "unknown"

    @model_validator(mode="after")
    def _check(self):
        n = len(self.A)
        assert self.X.ndim == 2 and self.X.shape[0] == n, "X must be (n, d)"
        assert self.R.shape == (n,) and self.period.shape == (n,), "R, period must be (n,)"
        assert self.A.min() >= 0 and self.A.max() < self.n_actions, "A out of range"
        lo, hi = self.reward_range
        assert self.R.min() >= lo - 1e-9 and self.R.max() <= hi + 1e-9, "R outside reward_range"
        if self.pscore is not None:
            assert self.pscore.shape == (n,) and (self.pscore > 0).all() and (self.pscore <= 1 + 1e-9).all()
        return self

    def subset(self, mask: Arr) -> "BanditLog":
        return BanditLog(
            X=self.X[mask], A=self.A[mask], R=self.R[mask],
            pscore=None if self.pscore is None else self.pscore[mask],
            period=self.period[mask], n_actions=self.n_actions,
            position=None if self.position is None else self.position[mask],
            reward_range=self.reward_range, source=self.source,
        )


# C2 PolicyAdapter -> estimators ------------------------------------------------------------
class ActionDist(_M):
    """pi(a | x_i) for every logged round i: rows sum to 1."""

    probs: Arr  # (n, K)
    policy: str

    @model_validator(mode="after")
    def _check(self):
        assert self.probs.ndim == 2 and (self.probs >= -1e-12).all()
        assert np.allclose(self.probs.sum(1), 1.0, atol=1e-6), "rows must sum to 1"
        return self


# C3 PropensityModel -> estimators, sensitivity ----------------------------------------------
class Propensity(_M):
    pscore: Arr  # (n,) pi_b(A_i | X_i)
    source: Literal["logged", "estimated"]


# C4 RewardModel -> DM/DR estimators, decomposition -----------------------------------------
class RewardModelOut(_M):
    q_hat: Arr  # (n, K) cross-fitted estimate of E[R | X_i, a]
    model: str
    heldout_logloss: Optional[float] = None


# C5 ValueEstimator / C6 DeltaEstimator -> intervals, decomposition, report ------------------------
class ValueEstimate(_M):
    estimator: str
    value: float
    influence: Arr  # (n,) per-round terms; value == influence.mean() for linear estimators
    diagnostics: dict = Field(default_factory=dict)  # ess, max_weight, clip_rate, ...


class DeltaEstimate(_M):
    estimator: str
    delta: float  # V(new) - V(old) on the same traffic
    v_new: float
    v_old: float
    influence: Arr  # (n,) per-round terms of the difference
    diagnostics: dict = Field(default_factory=dict)


# C7 Interval ------------------------------------------------------------------------------
class Interval(_M):
    method: str
    level: float
    point: float
    lo: float
    hi: float

    @model_validator(mode="after")
    def _check(self):
        assert self.lo <= self.hi, "lo must be <= hi"
        return self


# C8 Sensitivity ----------------------------------------------------------------------------
class SensitivityCurve(_M):
    gammas: list[float]
    lo: list[float]  # lower bound on the target at each Gamma (with sampling error if `joint`)
    hi: list[float]
    joint: bool  # True if bounds include sampling uncertainty
    gamma_star: Optional[float]  # smallest Gamma whose interval contains 0 (None if > max grid)


# C9 Decomposer (spike) ------------------------------------------------------------------------
class Decomposition(_M):
    """Before/after attribution: naive = policy_effect + env_change; env_change = mix_shift + response_drift."""

    naive: float
    policy_effect: Interval  # V_after(new) - V_after(old), with CI
    env_change: float
    mix_shift: float
    response_drift: float


# C10 Report ---------------------------------------------------------------------------------
class Verdict(_M):
    decision: Literal["worked", "hurt", "inconclusive"]
    headline: str
    decomposition: Decomposition
    sensitivity: Optional[SensitivityCurve] = None
    diagnostics: dict = Field(default_factory=dict)


# C11 Simulator ------------------------------------------------------------------------------
class ScenarioConfig(_M):
    name: str = "default"
    n_before: int = 20000
    n_after: int = 20000
    n_actions: int = 10
    dim: int = 5
    response_drift: float = 0.0  # logit shift of every reward after the switch (seasonality)
    mix_shift: float = 0.0  # mean shift of contexts after the switch (user mix)
    new_policy_quality: float = 1.0  # 1 = new scorer uses the true weights; 0 = random scorer
    old_policy_quality: float = 0.5
    temperature: float = 1.0  # softmax inverse temperature of both policies
    epsilon: float = 0.1  # uniform exploration mixed into both policies (overlap)
    hidden_confounding: float = 0.0  # strength of an unobserved u driving both action and reward
    seed: int = 0


class GroundTruth(_M):
    v_before_old: float
    v_before_new: float
    v_after_old: float
    v_after_new: float

    @property
    def naive_expected(self) -> float:
        return self.v_after_new - self.v_before_old

    @property
    def policy_effect_after(self) -> float:
        return self.v_after_new - self.v_after_old

    @property
    def env_change(self) -> float:
        return self.v_after_old - self.v_before_old
