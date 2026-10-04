"""The ONLY file the C4+C5 ratchet loop edits. `make(profile, init_level)` returns a DemandForecaster.

Iteration 1 hypothesis: after a CUSUM alarm, the level should be the running post-change MLE
(alpha_eff = max(alpha, 1/n_since_onset)) instead of a one-shot jump followed by a slow EWMA —
the jump estimate uses only the few steps before the alarm and then goes stale.
"""
import numpy as np

from components.detection.detectors import PoissonCusum
from components.forecasting.forecasters import EWMAForecaster


class RestartMeanForecaster(EWMAForecaster):
    def __init__(self, profile, init_level, alpha=0.01, delta=1.0, h=8.0):
        super().__init__(profile, init_level, alpha)
        self.det = PoissonCusum(self.level.size, delta=delta, h=h)
        self.n = np.full(self.level.size, 1e9)   # steps of evidence behind the current level
        self.alarms = []

    def observe(self, t, counts):
        f = float(self.f(t))
        out, post = self.det.update(t, counts, self.level * f, f)
        self.n += 1
        a = np.maximum(self.alpha, 1.0 / self.n)
        self.level += a * (counts / f - self.level)
        if out.alarm.any():
            z = np.flatnonzero(out.alarm)
            self.level[z] = post[z]
            self.n[z] = np.maximum(1, t - out.change_start[z] + 1)
            self.alarms += [(t, int(i)) for i in z]


def make(profile, init_level):
    return RestartMeanForecaster(profile, init_level, alpha=0.01, delta=1.0, h=8.0)
