"""The ONLY file the C4+C5 ratchet loop edits. `make(profile, init_level)` returns a DemandForecaster."""
from components.forecasting.forecasters import ChangeAwareForecaster


def make(profile, init_level):
    return ChangeAwareForecaster(profile, init_level, alpha=0.01, delta=1.0, h=8.0)
