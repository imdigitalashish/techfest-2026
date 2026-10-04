"""Isolated metric for growth_standards: max |z_ours - z_WHO| over WHO's own published SD tables.

WHO publishes, for every age day (or 0.1 cm of length/height), the measurement at -4..+4 SD
("expanded z-score tables", cdn.who.int). Feeding those values into our engine must return
the integer z (tolerance from WHO's 3-decimal rounding). +/-4 SD exercises the restricted rule.
Run: .venv/bin/python -m components.growth_standards.validate_who
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from components.growth_standards import who

SD_DIR = who.ROOT / ".data" / "raw" / "who_sd"
CASES = [  # (file stem, lms table, kind)
    ("wfa-boys", "weianthro", "age", 1), ("wfa-girls", "weianthro", "age", 2),
    ("lhfa-boys", "lenanthro", "age", 1), ("lhfa-girls", "lenanthro", "age", 2),
    ("wfl-boys", "wflanthro", "size", 1), ("wfl-girls", "wflanthro", "size", 2),
    ("wfh-boys", "wfhanthro", "size", 1), ("wfh-girls", "wfhanthro", "size", 2),
]
SDS = {"SD4neg": -4, "SD3neg": -3, "SD2neg": -2, "SD1neg": -1, "SD0": 0, "SD1": 1, "SD2": 2, "SD3": 3, "SD4": 4}


def run() -> dict:
    worst, n, per = 0.0, 0, {}
    for stem, table, kind, sex in CASES:
        df = pd.read_excel(SD_DIR / f"{stem}-zscore-expanded.xlsx")
        key = df.iloc[:, 0].to_numpy(dtype=float)
        sexv = np.full(len(df), sex)
        lms = who.age_lms(table, sexv, key) if kind == "age" else who.size_lms(table, sexv, key)
        errs = []
        for col, zt in SDS.items():
            z = who.z_restricted(df[col].to_numpy(dtype=float), *lms)
            errs.append(np.abs(z - zt))
        e = np.concatenate(errs)
        per[stem] = round(float(np.nanmax(e)), 4)
        worst, n = max(worst, float(np.nanmax(e))), n + int(np.isfinite(e).sum())
    return {"metric": "max_abs_z_error_vs_WHO_tables", "value": round(worst, 4), "n_points": n, "per_table": per}


if __name__ == "__main__":
    print(json.dumps(run()))
