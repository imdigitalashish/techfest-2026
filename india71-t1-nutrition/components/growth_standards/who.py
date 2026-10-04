"""WHO 2006 Child Growth Standards z-scores (vectorised).

Own implementation of the published WHO method (LMS with the WHO "restricted
application" beyond +/-3 SD for weight-based indicators; 0.7 cm length/height
correction at 731 days; 0.1 cm linear interpolation for weight-for-length/height;
biologically-implausible flags). Rules cross-checked against WHO's `anthro`
R package (GPL-3.0, commit b776d8a) — no code copied.

Tables: WHO LMS files fetched by `fetch_who.py` into `.data/raw/who_gs/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = ROOT / ".data" / "raw" / "who_gs"
MAX_AGE_DAYS = 1856
AGE_LIMIT_MONTHS = 60.0
DAYS_PER_MONTH = 365.25 / 12

FLAGS = {"waz": (-6.0, 5.0), "lhaz": (-6.0, 6.0), "wlhz": (-5.0, 5.0), "baz": (-5.0, 5.0), "muacz": (-5.0, 5.0)}


@dataclass(frozen=True)
class AgeTable:
    lms: np.ndarray  # (3 sexes [0 unused, M=1, F=2], MAX_AGE_DAYS+1, 3); NaN where undefined


@dataclass(frozen=True)
class SizeTable:
    lms: np.ndarray  # (3, n_steps, 3) indexed by round(size*10) - offset
    offset: int
    lo: float
    hi: float


def _read(name: str) -> pd.DataFrame:
    path = TABLE_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — run `python -m components.growth_standards.fetch_who`")
    return pd.read_csv(path, sep="\t")


@lru_cache(maxsize=None)
def age_table(name: str) -> AgeTable:
    df = _read(name)
    lms = np.full((3, MAX_AGE_DAYS + 1, 3), np.nan)
    lms[df["sex"].to_numpy(), df["age"].to_numpy()] = df[["l", "m", "s"]].to_numpy()
    return AgeTable(lms)


@lru_cache(maxsize=None)
def size_table(name: str) -> SizeTable:
    df = _read(name)
    size_col = df.columns[1]
    idx = np.rint(df[size_col].to_numpy() * 10).astype(int)
    offset = int(idx.min())
    lms = np.full((3, int(idx.max()) - offset + 2, 3), np.nan)
    lms[df["sex"].to_numpy(), idx - offset] = df[["l", "m", "s"]].to_numpy()
    return SizeTable(lms, offset, float(df[size_col].min()), float(df[size_col].max()))


def sex_code(sex) -> np.ndarray:
    s = pd.Series(np.asarray(sex)).astype(str).str.upper().map({"M": 1, "1": 1, "MALE": 1, "F": 2, "2": 2, "FEMALE": 2})
    return s.fillna(0).astype(int).to_numpy()


def _z_lms(y, l, m, s):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(np.abs(l) < 1e-12, np.log(y / m) / s, ((y / m) ** l - 1) / (l * s))


def _value_at(z, l, m, s):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(np.abs(l) < 1e-12, m * np.exp(s * z), m * (1 + l * s * z) ** (1 / l))


def z_restricted(y, l, m, s):
    """WHO restricted application: beyond +/-3 SD use the fixed 2-3 SD distance."""
    y, l, m, s = (np.asarray(a, dtype=float) for a in (y, l, m, s))
    z = _z_lms(y, l, m, s)
    sd3p, sd2p = _value_at(3.0, l, m, s), _value_at(2.0, l, m, s)
    sd3n, sd2n = _value_at(-3.0, l, m, s), _value_at(-2.0, l, m, s)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = np.where(z > 3, 3 + (y - sd3p) / (sd3p - sd2p), z)
        z = np.where(z < -3, -3 + (y - sd3n) / (sd2n - sd3n), z)
    return z


def value_from_z(z, l, m, s):
    """Inverse of z_restricted (used by the simulator)."""
    z, l, m, s = (np.asarray(a, dtype=float) for a in (z, l, m, s))
    v = _value_at(np.clip(z, -3, 3), l, m, s)
    sd3p, sd2p = _value_at(3.0, l, m, s), _value_at(2.0, l, m, s)
    sd3n, sd2n = _value_at(-3.0, l, m, s), _value_at(-2.0, l, m, s)
    v = np.where(z > 3, sd3p + (z - 3) * (sd3p - sd2p), v)
    v = np.where(z < -3, sd3n + (z + 3) * (sd2n - sd3n), v)
    return v


def age_lms(name: str, sex: np.ndarray, age_days):
    t = age_table(name).lms
    a = np.asarray(age_days, dtype=float)
    ok = np.isfinite(a) & (a >= 0) & (a <= MAX_AGE_DAYS) & (sex > 0)
    ai = np.where(ok, a, 0).astype(int)
    out = t[np.where(ok, sex, 0), ai]
    out[~ok] = np.nan
    return out[:, 0], out[:, 1], out[:, 2]


def size_lms(name: str, sex: np.ndarray, size_cm):
    """LMS at a length/height with WHO 0.1 cm linear interpolation."""
    t = size_table(name)
    x = np.asarray(size_cm, dtype=float)
    ok = np.isfinite(x) & (x >= t.lo) & (x <= t.hi) & (sex > 0)
    xs = np.where(ok, x, t.lo)
    low = np.trunc(xs * 10 + 1e-9) / 10
    frac = (xs - low) / 0.1
    i_lo = np.rint(low * 10).astype(int) - t.offset
    i_hi = np.minimum(i_lo + 1, t.lms.shape[1] - 1)
    sx = np.where(ok, sex, 0)
    lo, hi = t.lms[sx, i_lo], t.lms[sx, i_hi]
    hi = np.where(np.isnan(hi), lo, hi)
    lms = lo + frac[:, None] * (hi - lo)
    lms[~ok] = np.nan
    return lms[:, 0], lms[:, 1], lms[:, 2]


def standardise_length(age_days, length_height_cm, position):
    """WHO rule: <731 d use recumbent length (+0.7 if measured standing); >=731 d standing height (-0.7 if recumbent)."""
    a = np.asarray(age_days, dtype=float)
    x = np.asarray(length_height_cm, dtype=float).copy()
    pos = pd.Series(np.asarray(position, dtype=object)).astype(str).str.lower().to_numpy()
    x = np.where((a < 731) & (pos == "standing"), x + 0.7, x)
    x = np.where((a >= 731) & (pos == "recumbent"), x - 0.7, x)
    return x


def compute(df: pd.DataFrame) -> pd.DataFrame:
    """WHO z-scores for a measurement frame.

    Input columns: sex, age_days, weight_kg, length_height_cm, [measure_position], [muac_cm], [oedema].
    Output: waz, lhaz, wlhz, baz, muacz (2 dp, as WHO Anthro), flag_* booleans, valid_age.
    """
    n = len(df)
    sex = sex_code(df["sex"])
    age = df["age_days"].to_numpy(dtype=float)
    valid_age = np.isfinite(age) & (age >= 0) & (age / DAYS_PER_MONTH < AGE_LIMIT_MONTHS)
    w = df["weight_kg"].to_numpy(dtype=float)
    w = np.where(w > 0, w, np.nan)
    pos = df["measure_position"].to_numpy() if "measure_position" in df else np.array([None] * n)
    lh = standardise_length(age, df["length_height_cm"].to_numpy(dtype=float), pos)
    lh = np.where(lh > 0, lh, np.nan)
    oedema = df["oedema"].fillna(False).astype(bool).to_numpy() if "oedema" in df else np.zeros(n, bool)

    out = pd.DataFrame(index=df.index)
    out["waz"] = z_restricted(w, *age_lms("weianthro", sex, age))
    out["lhaz"] = z_restricted(lh, *age_lms("lenanthro", sex, age))
    wfl = z_restricted(w, *size_lms("wflanthro", sex, lh))
    wfh = z_restricted(w, *size_lms("wfhanthro", sex, lh))
    out["wlhz"] = np.where(age < 731, wfl, wfh)
    bmi = w / (lh / 100.0) ** 2
    out["baz"] = z_restricted(bmi, *age_lms("bmianthro", sex, age))
    if "muac_cm" in df:
        muac = df["muac_cm"].to_numpy(dtype=float)
        out["muacz"] = np.where(age >= 91, z_restricted(muac, *age_lms("acanthro", sex, age)), np.nan)
    else:
        out["muacz"] = np.nan
    for col in ("waz", "wlhz", "baz"):  # WHO: weight-based indices are not computed when oedema is present
        out.loc[oedema, col] = np.nan
    for col, (lo, hi) in FLAGS.items():
        out.loc[~valid_age, col] = np.nan
        out[col] = out[col].round(2)
        out[f"flag_{col}"] = (out[col] < lo) | (out[col] > hi)
    out["valid_age"] = valid_age
    return out


def classify(z: pd.DataFrame, muac_cm=None, oedema=None, age_days=None) -> pd.DataFrame:
    """Status classes (WHZ/MUAC/oedema, WHO cut-offs) used for SAM/MAM identification.

    MUAC cut-offs (11.5 / 12.5 cm) are applied only to children aged 6-59 months and only when the
    MUAC-for-age z is not biologically implausible; otherwise MUAC is ignored (and should be re-measured).
    """
    n = len(z)
    muac = np.asarray(muac_cm, dtype=float) if muac_cm is not None else np.full(n, np.nan)
    if age_days is not None:
        a = np.asarray(age_days, dtype=float)
        muac = np.where((a >= 183) & (a < 1826), muac, np.nan)
    if "flag_muacz" in z:
        muac = np.where(z["flag_muacz"].to_numpy(dtype=bool), np.nan, muac)
    oed = np.asarray(oedema, dtype=bool) if oedema is not None else np.zeros(n, bool)
    whz = z["wlhz"].where(~z["flag_wlhz"]).to_numpy()
    with np.errstate(invalid="ignore"):
        sam = (whz < -3) | (muac < 11.5) | oed
        mam = ~sam & ((whz < -2) | ((muac >= 11.5) & (muac < 12.5)))
    known = np.isfinite(whz) | np.isfinite(muac) | oed
    status = np.select([sam, mam, known], ["sam", "mam", "normal"], "unknown")
    haz = z["lhaz"].where(~z["flag_lhaz"]).to_numpy()
    waz = z["waz"].where(~z["flag_waz"]).to_numpy()
    with np.errstate(invalid="ignore"):
        stunt = np.select([haz < -3, haz < -2, np.isfinite(haz)], ["severe", "moderate", "none"], "unknown")
        under = np.select([waz < -3, waz < -2, np.isfinite(waz)], ["severe", "moderate", "none"], "unknown")
    return pd.DataFrame({"nutrition_status": status, "stunting": stunt, "underweight": under}, index=z.index)


def length_from_z(z, sex, age_days):
    return value_from_z(z, *age_lms("lenanthro", sex_code(sex), age_days))


def weight_from_wlz(z, sex, length_cm, age_days):
    s = sex_code(sex)
    a = np.asarray(age_days, dtype=float)
    lh = np.asarray(length_cm, dtype=float)
    w_l = value_from_z(z, *size_lms("wflanthro", s, lh))
    w_h = value_from_z(z, *size_lms("wfhanthro", s, lh))
    return np.where(a < 731, w_l, w_h)
