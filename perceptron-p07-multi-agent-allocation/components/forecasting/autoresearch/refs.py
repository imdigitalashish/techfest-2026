"""Reference forecasters for the ratchet ledger (not edited by the loop)."""
from components.forecasting.forecasters import ChangeAwareForecaster, EWMAForecaster


def ewma_005(profile, init_level):
    return EWMAForecaster(profile, init_level, alpha=0.05)


def ewma_001(profile, init_level):
    return EWMAForecaster(profile, init_level, alpha=0.01)


def ewma_020(profile, init_level):
    return EWMAForecaster(profile, init_level, alpha=0.20)


def cusum_h6(profile, init_level):
    return ChangeAwareForecaster(profile, init_level, alpha=0.01, delta=1.0, h=6.0)


def cusum_h12(profile, init_level):
    return ChangeAwareForecaster(profile, init_level, alpha=0.01, delta=1.0, h=12.0)


def cusum_d05(profile, init_level):
    return ChangeAwareForecaster(profile, init_level, alpha=0.01, delta=0.5, h=8.0)


def cusum_a003(profile, init_level):
    return ChangeAwareForecaster(profile, init_level, alpha=0.03, delta=1.0, h=8.0)
