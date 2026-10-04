"""FROZEN evaluator for the C6 shift-monitor ratchet. The loop never edits this file.

    cd perceptron-p04-lob-regimes && python components/shift_detector/autoresearch/eval.py <candidate.json>

Runs the candidate detector alone (no forecaster) over the DEV days from eval/config.py and prints
one scalar on the last line:

    SCORE = mean false alarms per dev day + 10 * fraction of verified dev events missed   (lower is better)

An alarm is a hit if it lands in [event, event + 30 min]; every other alarm is a false alarm.
A detector that never fires scores 10 (one verified dev event, FOMC 2023-11-01, missed).
The holdout days are never read here; the lead re-checks kept candidates on holdout separately.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from config import CFG, SPLIT, STEP_S  # noqa: E402

from components.features import build_features  # noqa: E402
from components.ingest import load_book_day  # noqa: E402
from components.shift_detector import RollingKS, calibrate_ks_null  # noqa: E402

TOL_S = 1800
MISS_PENALTY = 10.0


def events_by_day() -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    with open(ROOT / "data" / "events.csv") as fh:
        for r in csv.DictReader(fh):
            if r["verified"].startswith("yes"):
                ts = datetime.fromisoformat(f"{r['date']}T{r['utc_time']}:00+00:00").timestamp()
                out.setdefault(r["date"], []).append(int(ts * 1e6))
    return out


def main(cand_path: str) -> float:
    cand = json.loads(Path(cand_path).read_text())
    feats = cand.get("features", CFG["ks_features"])
    ks_cfg = {**CFG["ks"], **cand.get("ks", {})}
    train = [build_features(load_book_day(d), step_s=STEP_S) for d in SPLIT["train"]]
    names = train[0].names
    idx = [names.index(n) for n in feats]
    ref = np.vstack([f.X for f in train])[::ks_cfg["subsample"]][:, idx]
    thr = None
    if cand.get("mode") == "calibrated":
        c = cand.get("ksc", CFG["ksc"])
        thr = calibrate_ks_null([f.X for f in train], idx, ks_cfg["window"], ks_cfg["subsample"],
                                c["stride"], c["quantile"])
    ev = events_by_day()
    false_per_day, n_ev, n_hit, delays = [], 0, 0, []
    for day in SPLIT["dev"]:
        f = build_features(load_book_day(day), step_s=STEP_S)
        Xd = f.X[:, idx]
        det = RollingKS(ref, list(range(len(idx))), feats, **ks_cfg, thresholds=thr)
        alarms = [a.step for t in range(Xd.shape[0]) if (a := det.update(t, Xd)) is not None]
        a_us = f.grid_us[alarms] if alarms else np.array([], dtype=np.int64)
        hit = np.zeros(len(a_us), bool)
        for e in ev.get(day, []):
            n_ev += 1
            inw = (a_us >= e) & (a_us <= e + TOL_S * 1_000_000)
            hit |= inw
            if inw.any():
                n_hit += 1
                delays.append(float((a_us[inw].min() - e) / 1e6))
        false_per_day.append(int((~hit).sum()))
        print(f"{day}: alarms={len(alarms)} false={int((~hit).sum())}", flush=True)
    miss = (n_ev - n_hit) / n_ev if n_ev else 0.0
    score = float(np.mean(false_per_day) + MISS_PENALTY * miss)
    print(json.dumps({"false_per_day": false_per_day, "events": n_ev, "detected": n_hit, "delays_s": delays,
                      "thresholds": None if thr is None else [round(float(x), 4) for x in thr]}))
    print(f"SCORE {score:.4f}")
    return score


if __name__ == "__main__":
    main(sys.argv[1])
