"""Contract tests for the C4 grid-factor service baseline."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from greenauto.db import FactorDB  # noqa: E402
from greenauto.grid import GridFactorQuery, grid_factor, states  # noqa: E402


@pytest.fixture(scope="module")
def db():
    return FactorDB.load()


def test_national_meter_matches_derived_record(db):
    g = grid_factor(db, GridFactorQuery(region="IN", period="2025-26", method="average"))
    assert g.value == pytest.approx(db["energy.electricity.in.grid_wavg_at_plug.fy2025_26"].value, abs=1e-4)
    assert len(g.record_ids) == 2


def test_busbar_is_cea_table_s(db):
    for method, v in (("average", 0.675), ("operating_margin", 0.963), ("build_margin", 0.446)):
        g = grid_factor(db, GridFactorQuery(period="2025-26", method=method, delivery="busbar"))
        assert g.value == v


def test_every_state_resolves_and_is_above_busbar(db):
    sts = states(db)
    assert len(sts) == 35
    for s in sts:
        g = grid_factor(db, GridFactorQuery(region=s, period="2025-26"))
        assert g.value > 0.675


def test_co2e_adds_partial_upstream(db):
    co2 = grid_factor(db, GridFactorQuery(gas_basis="CO2", delivery="busbar")).value
    co2e = grid_factor(db, GridFactorQuery(gas_basis="CO2e", delivery="busbar")).value
    assert 0.675 == co2 < co2e < 0.675 * 1.06      # combustion CH4/N2O + coal-mine CH4 add a few per cent
    with pytest.raises(NotImplementedError):
        grid_factor(db, GridFactorQuery(gas_basis="CO2e", method="build_margin"))
