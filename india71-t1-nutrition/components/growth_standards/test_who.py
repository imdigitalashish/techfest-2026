import numpy as np
import pandas as pd
import pytest

from components.growth_standards import who
from components.growth_standards.validate_who import SD_DIR, run


@pytest.mark.skipif(not SD_DIR.exists(), reason="WHO validation tables not fetched")
def test_matches_who_published_sd_tables():
    r = run()
    assert r["n_points"] > 40000
    assert r["value"] < 0.01, r


def test_roundtrip_and_rules():
    z = np.array([-4.5, -3.2, -2.0, 0.0, 1.5, 3.7])
    sex = np.array([1] * 6)
    lms = who.age_lms("weianthro", sex, np.full(6, 400))
    assert np.allclose(who.z_restricted(who.value_from_z(z, *lms), *lms), z, atol=1e-9)
    df = pd.DataFrame(dict(sex=["M", "M"], age_days=[700, 700], weight_kg=[9.0, 9.0],
                           length_height_cm=[78.0, 77.3], measure_position=["recumbent", "standing"]))
    out = who.compute(df)
    assert abs(out.lhaz[0] - out.lhaz[1]) < 1e-9  # standing height +0.7 cm under 731 days


def test_flags_and_oedema():
    df = pd.DataFrame(dict(sex=["F", "F"], age_days=[365, 365], weight_kg=[30.0, 8.5],
                           length_height_cm=[74.0, 74.0], measure_position=["recumbent"] * 2, oedema=[False, True]))
    out = who.compute(df)
    assert out.flag_waz[0] and out.flag_wlhz[0]
    assert np.isnan(out.waz[1]) and np.isnan(out.wlhz[1]) and not np.isnan(out.lhaz[1])
    cls = who.classify(out, oedema=df.oedema)
    assert cls.nutrition_status[1] == "sam"
