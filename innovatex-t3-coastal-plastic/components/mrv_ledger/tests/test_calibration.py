"""Review issue 1: the quoted operating point must be the one the shipped default reconcile() path uses."""
import inspect
import json

import pytest

from mrv_ledger import evaluate as ev
from mrv_ledger import reconcile as rc
from mrv_ledger.synth import make_trips

PARAMS = json.loads(rc.PARAMS_FILE.read_text())
METRICS = json.loads((ev.OUT / "metrics.json").read_text())


def test_shipped_default_loads_the_persisted_threshold():
    assert rc.DEFAULT_SOURCE == str(rc.PARAMS_FILE)
    assert rc.DEFAULT.z_review == PARAMS["z_review"] != rc.Params().z_review
    assert inspect.signature(rc.reconcile).parameters["p"].default is None  # resolved to DEFAULT at call time
    assert METRICS["z_review_shipped"] == PARAMS["z_review"]


def test_persisted_threshold_reproduces_from_its_recorded_seed():
    c = PARAMS["calibration"]
    assert c["model_params"] == {k: v for k, v in rc.DEFAULT.as_dict().items() if k != "z_review"}
    cal = ev.calibrate(rc.DEFAULT, n_cal=c["n_cal"], seed=c["seed_cal"])
    assert cal["z_review"] == PARAMS["z_review"]


@pytest.fixture(scope="module")
def heldout():
    trips = make_trips(ev.TEST_COUNTS, seed=ev.SEED_TEST, p=rc.DEFAULT)
    flags = [rc.reconcile(t.record, t.capacity_m3).flag != "ok" for t in trips]  # the shipped default path
    return trips, flags


def test_default_path_flags_at_most_5pct_of_heldout_honest(heldout):
    trips, flags = heldout
    honest = [f for t, f in zip(trips, flags) if t.kind == "honest"]
    assert len(honest) == ev.TEST_COUNTS["honest"]
    assert sum(honest) / len(honest) <= 0.05


def test_quoted_metrics_come_from_the_default_path(heldout):
    trips, flags = heldout
    honest = [f for t, f in zip(trips, flags) if t.kind == "honest"]
    fraud = [f for t, f in zip(trips, flags) if t.kind != "honest"]
    inflated = [f for t, f in zip(trips, flags) if t.kind == "inflated"]
    tpr, fpr = sum(fraud) / len(fraud), sum(honest) / len(honest)

    def precision(prev):
        return prev * tpr / (prev * tpr + (1 - prev) * fpr)

    assert METRICS["false_flag_rate_test"] == round(fpr, 4)
    assert METRICS["recall_fraud_at_5pct_false_flags"] == round(tpr, 4)
    assert METRICS["recall_inflated_x1.2-3"] == round(sum(inflated) / len(inflated), 4)
    assert METRICS["precision_at_5pct_prevalence"] == round(precision(0.05), 4)
    assert METRICS["precision_at_10pct_prevalence"] == round(precision(0.10), 4)
