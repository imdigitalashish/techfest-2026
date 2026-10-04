from pathlib import Path

import numpy as np
import pytest

from components.scenarios.nyc_tlc import DATA_DIR, build_nyc_trace


REQUIRED = [
    DATA_DIR / "yellow_tripdata_2025-07.parquet",
    DATA_DIR / "taxi_zone_lookup.csv",
    DATA_DIR / "taxi_zones.zip",
]


@pytest.fixture(scope="module")
def nyc_trace():
    if not all(Path(p).exists() for p in REQUIRED):
        pytest.skip("NYC TLC data files are absent")
    return build_nyc_trace(["2025-07-03", "2025-07-04"], ["2025-07-01", "2025-07-02"], seed=123)


def test_nyc_trace_contract(nyc_trace):
    trace, meta = nyc_trace
    assert trace.rates.shape == (2880, 25)
    assert trace.counts.shape == (2880, 25)
    assert trace.offsets.shape == (2880, 25)
    assert trace.od_prob.shape == (25, 25)
    assert trace.rates.dtype == np.float64
    assert trace.counts.dtype == np.int32
    assert trace.offsets.dtype == np.int64
    assert trace.req_dest.dtype == np.int16
    assert trace.counts.sum() == trace.req_dest.size
    assert trace.name == "nyc-2025-07-03"
    assert trace.change_points == []
    assert set(meta) == {
        "grid",
        "n_zones",
        "od_prob",
        "profile",
        "hist_shares",
        "init_level",
        "init_level_raw",
        "rates",
    }


def test_offsets_and_probability_contract(nyc_trace):
    trace, meta = nyc_trace
    flat = trace.counts.reshape(-1)
    expected = (np.cumsum(flat, dtype=np.int64) - flat).reshape(trace.counts.shape)
    assert np.array_equal(trace.offsets, expected)
    assert int(trace.offsets[-1, -1] + trace.counts[-1, -1]) == trace.req_dest.size
    assert np.all((trace.req_dest >= 0) & (trace.req_dest < 25))
    assert np.allclose(trace.od_prob.sum(axis=1), 1.0)
    assert np.isclose(meta["profile"].mean(), 1.0)
    assert np.isclose(meta["hist_shares"].sum(), 1.0)
    assert meta["profile"].shape == (1440,)
    assert meta["hist_shares"].shape == (25,)


def test_seed_determinism():
    if not all(Path(p).exists() for p in REQUIRED):
        pytest.skip("NYC TLC data files are absent")
    a, _ = build_nyc_trace(["2025-07-04"], ["2025-07-01", "2025-07-02"], seed=7)
    b, _ = build_nyc_trace(["2025-07-04"], ["2025-07-01", "2025-07-02"], seed=7)
    c, _ = build_nyc_trace(["2025-07-04"], ["2025-07-01", "2025-07-02"], seed=8)
    assert np.array_equal(a.counts, b.counts)
    assert np.array_equal(a.req_dest, b.req_dest)
    assert not np.array_equal(a.counts, c.counts) or not np.array_equal(a.req_dest, c.req_dest)
