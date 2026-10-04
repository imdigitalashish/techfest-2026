"""C3/C5 — Demand nowcasting and look-ahead forecasting per zone.

All forecasters implement the DemandForecaster protocol: observe(t, counts) after each step and
forecast(t, H) -> Forecast(mean (H, Z)) for steps t..t+H-1. Seasonality: a city-level time-of-day
multiplier f(tod) LEARNED from a separate training history (scenarios.diurnal_profile); per-zone
levels live in deseasonalised units (requests/step at f = 1).
"""
from __future__ import annotations

import numpy as np

from architecture.contracts.contracts import Forecast
from components.detection.detectors import PoissonCusum


class _Seasonal:
    def __init__(self, profile: np.ndarray):
        self.profile = np.asarray(profile, dtype=float)
        self.day = self.profile.size

    def f(self, t: int | np.ndarray):
        return self.profile[np.asarray(t) % self.day]


class EWMAForecaster(_Seasonal):
    """Deseasonalised exponentially-weighted level per zone; flat (seasonal-shaped) forecast."""

    def __init__(self, profile, init_level: np.ndarray, alpha: float = 0.05):
        super().__init__(profile)
        self.alpha = float(alpha)
        self.level = np.asarray(init_level, dtype=float).copy()

    def observe(self, t: int, counts: np.ndarray) -> None:
        self.level += self.alpha * (counts / self.f(t) - self.level)

    def forecast(self, t: int, horizon: int) -> Forecast:
        f = self.f(np.arange(t, t + horizon))
        return Forecast(mean=f[:, None] * self.level[None, :])


class ChangeAwareForecaster(EWMAForecaster):
    """Slow EWMA for drift + two-sided Poisson CUSUM; on an alarm the zone's level jumps to the
    post-change MLE (restart), so abrupt shocks are absorbed in ~h/KL steps while the slow EWMA
    keeps variance low between changes (the stability-plasticity trade-off made explicit)."""

    def __init__(self, profile, init_level: np.ndarray, alpha: float = 0.01, delta: float = 1.0,
                 h: float = 8.0):
        super().__init__(profile, init_level, alpha)
        self.det = PoissonCusum(self.level.size, delta=delta, h=h)
        self.alarms: list[tuple[int, int]] = []   # (t, zone) log for detector metrics

    def observe(self, t: int, counts: np.ndarray) -> None:
        f = float(self.f(t))
        out, post = self.det.update(t, counts, self.level * f, f)
        self.level += self.alpha * (counts / f - self.level)
        if out.alarm.any():
            z = np.flatnonzero(out.alarm)
            self.level[z] = post[z]
            self.alarms += [(t, int(i)) for i in z]


class MovingAverageForecaster:
    """Rule-based demand estimate: mean arrivals over the last W steps (no seasonality)."""

    def __init__(self, n_zones: int, window: int = 30, init_level: np.ndarray | None = None):
        self.W = int(window)
        self.buf = np.zeros((self.W, n_zones))
        if init_level is not None:
            self.buf[:] = init_level
        self.i = 0

    def observe(self, t: int, counts: np.ndarray) -> None:
        self.buf[self.i % self.W] = counts
        self.i += 1

    def forecast(self, t: int, horizon: int) -> Forecast:
        return Forecast(mean=np.repeat(self.buf.mean(0, keepdims=True), horizon, axis=0))


class OracleForecaster:
    """Clairvoyant: true future rates (the reference for regret). Never available in deployment."""

    def __init__(self, rates: np.ndarray):
        self.rates = rates

    def observe(self, t: int, counts: np.ndarray) -> None:
        pass

    def forecast(self, t: int, horizon: int) -> Forecast:
        T = self.rates.shape[0]
        idx = np.minimum(np.arange(t, t + horizon), T - 1)
        return Forecast(mean=self.rates[idx])
