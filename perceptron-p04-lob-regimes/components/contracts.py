"""Typed contracts shared by every component (see architecture/contracts/README.md).

Arrays are numpy; shapes are documented per field. All timestamps are integer
microseconds since the Unix epoch, in *receive time* (Tardis `local_timestamp`):
a deployed system can only act on a message after it arrives, so every as-of join
and every label uses receive time. Exchange time is kept for diagnostics only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

TICK_SIZE = {"BTCUSDT": 0.1}  # Binance USD-M BTCUSDT PRICE_FILTER tickSize (see research/notes/datasets.md)


@dataclass(frozen=True)
class BookDay:
    """C1 Ingest -> C2 Features. Top-N order-book snapshots for one UTC day.

    recv_us, exch_us: (n,) int64 · bid_px, bid_sz, ask_px, ask_sz: (n, L) float64, level 0 = best.
    """
    symbol: str
    day: str
    recv_us: np.ndarray
    exch_us: np.ndarray
    bid_px: np.ndarray
    bid_sz: np.ndarray
    ask_px: np.ndarray
    ask_sz: np.ndarray

    def __post_init__(self) -> None:
        n = self.recv_us.shape[0]
        assert self.exch_us.shape == (n,)
        for a in (self.bid_px, self.bid_sz, self.ask_px, self.ask_sz):
            assert a.shape[0] == n and a.ndim == 2
        assert np.all(np.diff(self.recv_us) >= 0), "recv_us must be non-decreasing"


@dataclass(frozen=True)
class FeatureFrame:
    """C2 Features -> C4 Normalizer / C6 Detector. One row per grid step.

    grid_us: (T,) int64 decision times · X: (T, d) float64 causal features (row t uses only
    messages with recv_us <= grid_us[t]) · mid: (T,) mid price as-of grid_us[t] · spread_ticks: (T,).
    """
    symbol: str
    day: str
    step_us: int
    grid_us: np.ndarray
    names: tuple[str, ...]
    X: np.ndarray
    mid: np.ndarray
    spread_ticks: np.ndarray

    def col(self, name: str) -> np.ndarray:
        return self.X[:, self.names.index(name)]


@dataclass(frozen=True)
class Labels:
    """C3 Labeler -> C7 Adapter / C8 Evaluator.

    y: (T,) float64 in {0, 1} or NaN (tie or beyond the day) — 1 means mid rises over the horizon.
    avail_step: (T,) int64 first grid step at which y[t] is known (t + h_steps); online
    learners may only consume y[t] at steps >= avail_step[t].
    move_bps: (T,) signed mid move over the horizon in basis points (for cost-aware metrics).
    """
    h_steps: int
    y: np.ndarray
    avail_step: np.ndarray
    move_bps: np.ndarray


@dataclass
class Alarm:
    """C6 Shift detector -> C7 Adapter."""
    step: int
    detector: str
    statistic: float
    detail: dict = field(default_factory=dict)


@dataclass
class EpisodeResult:
    """C7 Adapter -> C8 Evaluator. Output of running one policy over one day."""
    policy: str
    day: str
    p_up: np.ndarray            # (T,) predicted P(y=1) made at step t using info <= t
    alarms: list[Alarm]
    step_ns: np.ndarray         # (T,) wall time of the online step (predict + updates), nanoseconds
    extra: dict = field(default_factory=dict)
