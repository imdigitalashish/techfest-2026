from datetime import timedelta

import pandas as pd

from components.cohort_simulator.simulate import SimConfig, simulate
from components.early_warning import model as ew


def test_no_look_ahead_in_v1_features():
    """Appending future records must not change features of earlier child-months (v1 path)."""
    sim = simulate(SimConfig(seed=5, n_projects=1, sectors_per_project=1, awcs_per_sector=3, window_months=8))
    meas, health = sim["measurements"], sim["health_events"]
    month_of = sim["truth_monthly"][["child_key", "measured_on", "month_index"]]
    cut = meas.measured_on.min() + timedelta(days=4 * 30)
    early = ew.features(meas[meas.measured_on <= cut], health[health.occurred_on <= cut], month_of, unit_cred=False)
    full = ew.features(meas, health, month_of, unit_cred=False)
    cols = ["event_id"] + ew.ANTHRO_V1 + ew.HEALTH
    a = early[cols].set_index("event_id").sort_index()
    b = full[cols].set_index("event_id").loc[a.index].sort_index()
    pd.testing.assert_frame_equal(ew.fill(a), ew.fill(b), check_dtype=False)
