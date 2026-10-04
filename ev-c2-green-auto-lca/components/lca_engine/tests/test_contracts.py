"""Contract tests for the LCA engine (run: python3 -m pytest components/lca_engine/tests -q from ev-c2-green-auto-lca/)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from greenauto.db import FactorDB, Pedigree  # noqa: E402
from greenauto.engine import check_scenario, load_scenarios, run_scenario  # noqa: E402


@pytest.fixture(scope="module")
def db():
    return FactorDB.load()


def test_every_record_is_cited(db):
    for r in db.records.values():
        assert r.source_id in db.sources
        assert r.locator
        assert r.status in ("verified", "derived", "assumption", "synthetic", "UNVERIFIED")
        if r.status == "verified":
            assert r.quote


def test_scenarios_resolve(db):
    for sc in load_scenarios().values():
        assert check_scenario(db, sc) == []


def test_pedigree_sigma_perfect_score_is_basic_only():
    p = Pedigree(reliability=1, completeness=1, temporal=1, geographical=1, technological=1)
    import math
    assert p.sigma() == pytest.approx(math.log(1.05) / 2)


def test_replicates_icct_table1_with_implied_inputs(db):
    res = run_scenario(db, load_scenarios()["icct2021_implied"], n=500)
    assert res["products"]["ice_scooter"]["total"] == pytest.approx(60.9, abs=0.1)
    assert res["products"]["ev_scooter"]["total"] == pytest.approx(37.5, abs=0.1)
    assert res["comparison"]["reduction_central"] == pytest.approx(0.384, abs=0.002)


def test_mc_is_deterministic_for_seed(db):
    sc = load_scenarios()["in2026_cea_average"]
    a = run_scenario(db, sc, n=300, seed=1)["comparison"]["reduction_mc"]["p50"]
    b = run_scenario(db, sc, n=300, seed=1)["comparison"]["reduction_mc"]["p50"]
    assert a == b


def test_grid_ef_matches_cea_table_s(db):
    assert db["energy.electricity.in.grid_wavg_generation.fy2025_26"].value == 0.675
    derived = db["energy.electricity.in.grid_wavg_at_plug.fy2025_26"].value
    assert derived == pytest.approx(0.675 / (1 - 0.1763), abs=1e-4)
