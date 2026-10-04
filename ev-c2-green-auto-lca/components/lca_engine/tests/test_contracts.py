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


def test_car_verification_within_2p5_percent(db):
    res = run_scenario(db, load_scenarios()["car_icct2021_replication"], n=300)
    published = {"petrol": 228, "diesel": 245, "cng": 226, "bev": 185}
    for pid, pub in published.items():
        assert abs(res["products"][pid]["total"] - pub) / pub < 0.025


def test_scenario_inheritance_applies_overrides(db):
    scs = load_scenarios()
    base, om = scs["in2026_cea_average"], scs["in2026_cea_operating_margin"]
    ev_b = next(p for p in base.products if p.id == "ev_scooter")
    ev_o = next(p for p in om.products if p.id == "ev_scooter")
    assert ev_b.params["ef_gen"].endswith("grid_wavg_generation.fy2025_26")
    assert ev_o.params["ef_gen"].endswith("grid_om.fy2025_26")
    assert ev_b.params["elec"] == ev_o.params["elec"]


def test_uniform_ranges_are_honoured(db):
    import numpy as np
    rec = db["use.2w.scooter_ev.elec_kwh_per_100km.icct2021_ambiguity"]
    x = rec.sample(2000, np.random.default_rng(0))
    assert x.min() >= 3.7 and x.max() <= 4.13


def test_gas_basis_flags(db):
    scs = load_scenarios()
    assert run_scenario(db, scs["car_icct2021_replication"], n=100)["harmonized"] is True
    assert run_scenario(db, scs["in2026_cea_average"], n=100)["harmonized"] is False


def test_verified_values_appear_in_their_quotes():
    import importlib.util
    spec = importlib.util.spec_from_file_location("value_check", Path(__file__).resolve().parents[2] / "ingestion" / "value_check.py")
    vc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vc)
    n, bad, waived = vc.check()
    assert n > 50 and bad == [], bad


def test_docs_do_not_drift_from_results():
    import subprocess, sys as _s
    root = Path(__file__).resolve().parents[3]
    r = subprocess.run([_s.executable, str(root / "eval" / "check_docs.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_gpt6sol_regressions(db):
    import numpy as np
    from greenauto.engine import spearman
    scs = load_scenarios()
    car = run_scenario(db, scs["car_in2026_avg_co2e"], n=200)
    assert car["harmonized"] is True and car["gas_basis_families"] == ["GWP100-AR5"]       # finding 1
    assert run_scenario(db, scs["in2026_avg_co2e"], n=200)["harmonized"] is False
    bev = next(p for p in scs["car_in2026_avg_co2e"].products if p.id == "bev")
    assert "grid" not in bev.params                                                       # finding 3
    assert 0.75 < car["products"]["bev"]["india_footprint_share"] < 0.9                    # finding 4
    x = db["fuels.petrol.ncv.ipcc2006"].sample(200000, np.random.default_rng(1))          # finding 6
    assert np.percentile(x, 2.5) == pytest.approx(42.5, rel=0.005)
    assert np.percentile(x, 97.5) == pytest.approx(44.8, rel=0.005)
    assert spearman(np.ones(8), np.arange(8)) == 0.0                                      # finding 7


def test_eol_double_counting_is_rejected(db):
    import copy
    sc = copy.deepcopy(load_scenarios()["car_in2026_avg_co2e"])
    petrol = sc.products[0]
    petrol.stages["end_of_life"] = petrol.stages["vehicle_production"]
    assert any("EOL" in x for x in check_scenario(db, sc))
