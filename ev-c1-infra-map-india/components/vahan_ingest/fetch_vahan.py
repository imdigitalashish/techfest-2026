"""Fetch the VAHAN tables the walking skeleton needs, with a per-query cache.

Usage (from ev-c1-infra-map-india/):
    .venv/bin/python components/vahan_ingest/fetch_vahan.py --national --states --rto-state MH

Writes raw tables to .data/vahan/raw/<key>.csv and a tidy long table to
.data/vahan/vahan_long.csv with columns:
    scope, state_code, state_label, rto_code, rto_label, y_axis, row_label, x_axis, col_label, year, count, fetched_at
Re-running skips cached queries, so it is safe to interrupt.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from vahan_client import Vahan  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, ".data", "vahan", "raw")
os.makedirs(RAW, exist_ok=True)
LOG = os.path.join(ROOT, ".data", "vahan", "fetch.log")


def log(msg: str) -> None:
    line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def cached(key: str, meta: dict, fn) -> None:
    path = os.path.join(RAW, key + ".csv")
    if os.path.exists(path):
        return
    df = fn()
    df.to_csv(path, index=False)
    with open(os.path.join(RAW, key + ".json"), "w") as f:
        json.dump({**meta, "title": df.attrs.get("title", ""), "fetched_at": dt.datetime.now().isoformat(timespec="seconds"),
                   "rows": len(df)}, f)
    log(f"ok {key} rows={len(df)}")


def national(years: list[str]) -> None:
    v = Vahan()
    for y in years:
        cached(f"nat_state_fuel_{y}", {"scope": "national", "state_code": "-1", "rto_code": "-1", "y_axis": "State",
                                       "x_axis": "Fuel", "year": y},
               lambda: v.query("State", "Fuel", y))


def states_class(year: str) -> None:
    v = Vahan()
    for st in v.states:
        key = f"state_{st.value}_class_fuel_{year}"
        if os.path.exists(os.path.join(RAW, key + ".csv")):
            continue
        try:
            v.set_state(st.value)
            cached(key, {"scope": "state", "state_code": st.value, "state_label": st.label, "rto_code": "-1",
                         "y_axis": "Vehicle Class", "x_axis": "Fuel", "year": year},
                   lambda: v.query("Vehicle Class", "Fuel", year))
        except Exception as e:  # keep going; a re-run retries
            log(f"FAIL {key}: {e!r}")
            v = Vahan()


def rto_level(state: str, years: list[str]) -> None:
    v = Vahan()
    rtos = v.set_state(state)
    st_label = next((s.label for s in v.states if s.value == state), state)
    pd.DataFrame([{"rto_code": r.value, "rto_label": r.label} for r in rtos]).to_csv(
        os.path.join(RAW, f"rto_list_{state}.csv"), index=False)
    log(f"{state}: {len(rtos)} RTOs")
    for r in rtos:
        for y in years:
            key = f"rto_{state}_{r.value}_class_fuel_{y}"
            if os.path.exists(os.path.join(RAW, key + ".csv")):
                continue
            try:
                v.set_state(state)
                v.set_rto(r.value)
                cached(key, {"scope": "rto", "state_code": state, "state_label": st_label, "rto_code": r.value,
                             "rto_label": r.label, "y_axis": "Vehicle Class", "x_axis": "Fuel", "year": y},
                       lambda: v.query("Vehicle Class", "Fuel", y))
            except Exception as e:
                log(f"FAIL {key}: {e!r}\n{traceback.format_exc(limit=2)}")
                v = Vahan()


def build_long() -> str:
    frames = []
    for fn in sorted(os.listdir(RAW)):
        if not fn.endswith(".json"):
            continue
        meta = json.load(open(os.path.join(RAW, fn)))
        df = pd.read_csv(os.path.join(RAW, fn[:-5] + ".csv"))
        long = df.melt(id_vars=["row_label"], var_name="col_label", value_name="count")
        for k in ("scope", "state_code", "state_label", "rto_code", "rto_label", "y_axis", "x_axis", "year", "fetched_at"):
            long[k] = meta.get(k, "")
        frames.append(long)
    out = pd.concat(frames, ignore_index=True)
    path = os.path.join(ROOT, ".data", "vahan", "vahan_long.csv")
    out.to_csv(path, index=False)
    log(f"long table rows={len(out)} -> {path}")
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--national", action="store_true")
    ap.add_argument("--states", action="store_true")
    ap.add_argument("--rto-state", default=None)
    ap.add_argument("--years", default="A,2026,2025,2024,2023,2022,2021,2020")
    ap.add_argument("--rto-years", default="A,2025")
    a = ap.parse_args()
    if a.national:
        national(a.years.split(","))
    if a.states:
        states_class("A")
    if a.rto_state:
        rto_level(a.rto_state, a.rto_years.split(","))
    build_long()
