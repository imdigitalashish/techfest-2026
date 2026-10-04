"""Vendor a small, aggregated extract of the Open Bandit Dataset (ZOZO, Inc.; CC BY 4.0) for the demo.

Run once, where the raw slices exist (from perceptron-p03-off-policy-eval/; needs numpy, e.g. the project .venv):
  nice -n 10 .venv/bin/python demo/make_extract.py
Raw input (gitignored): .data/obd_slice/{random,bts}/all/all.npz, written by eval/obd_zip_slice.py:
  .venv/bin/python eval/obd_zip_slice.py --member open_bandit_dataset/random/all/all.csv --budget_mb 30
  .venv/bin/python eval/obd_zip_slice.py --member open_bandit_dataset/bts/all/all.csv --budget_mb 100
Output (committed): demo/data/obd_bts_all.csv.gz, demo/data/obd_random_all.csv.gz, demo/data/extract_manifest.json.

The extract keeps every row of campaign All in [2019-11-24 00:00, 2019-11-27 12:00) UTC, aggregated to counts:
  BTS:    hour, item, position, propensity, click, count      (propensity = exact float64 as parsed, shortest repr)
  Random: hour, item, position, click, pre_t0, count          (propensity is 0.0125 = 1/80 for every row; checked)
hour = whole UTC hours since 2019-11-24 00:00 (0..83). pre_t0 = 1 for Random rows before the first BTS row
(2019-11-24 00:00:00.047846), the start of the pre-registered window W in eval/run_obd_slice.py.
User features and exact timestamps are dropped. Nothing is rounded.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / ".data" / "obd_slice"
OUT = ROOT / "demo" / "data"
RES = ROOT / "eval" / "results"
HOUR = 3_600_000_000_000
T_FLOOR = np.datetime64("2019-11-24T00:00:00", "ns").astype(np.int64)
T_END = np.datetime64("2019-11-27T12:00:00", "ns").astype(np.int64)
T0_PREREG = np.datetime64("2019-11-24T00:00:00.047846", "ns").astype(np.int64)


def load(path: Path) -> dict:
    """Same as eval/run_obd_slice.py:load (slices written before the unit fix hold microseconds)."""
    d = np.load(path)
    out = {k: d[k] for k in ("ts", "item", "pos", "click", "ps")}
    if out["ts"].max() < 10 ** 17:
        out["ts"] = out["ts"] * 1000
    return out


def gz_csv(header: str, cols: list[np.ndarray], fmt: list) -> bytes:
    buf = io.StringIO()
    buf.write(header + "\n")
    for row in zip(*[c.tolist() for c in cols]):
        buf.write(",".join(f(v) for f, v in zip(fmt, row)) + "\n")
    return gzip.compress(buf.getvalue().encode(), compresslevel=9, mtime=0)


def close(a: float, b: float, rel: float = 1e-12) -> bool:
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-300)


def main():
    if not (RAW / "bts" / "all" / "all.npz").exists():
        sys.exit(f"missing {RAW}/bts/all/all.npz — fetch it with eval/obd_zip_slice.py (see this file's header)")
    R, B = load(RAW / "random" / "all" / "all.npz"), load(RAW / "bts" / "all" / "all.npz")
    assert int(B["ts"].min()) == int(T0_PREREG), "BTS slice must start at the pre-registered W start"
    assert max(int(R["ts"].min()), int(B["ts"].min())) == int(T0_PREREG)
    assert (int(B["ts"].max()) // HOUR) * HOUR == int(T_END), "BTS slice must end in the 12:00 hour of 2019-11-27 (budget 100 MB)"
    mB = (B["ts"] >= T_FLOOR) & (B["ts"] < T_END)
    mR = (R["ts"] >= T_FLOOR) & (R["ts"] < T_END)
    B = {k: v[mB] for k, v in B.items()}
    R = {k: v[mR] for k, v in R.items()}
    assert np.all(R["ps"] == 0.0125), "Random propensity is 1/80 for every row"

    # ---- BTS: unique (hour, item, position, propensity, click) with counts ----
    hB = ((B["ts"] - T_FLOOR) // HOUR).astype(np.int64)
    ps_vals, ps_id = np.unique(B["ps"], return_inverse=True)
    keyB = np.stack([hB, B["item"].astype(np.int64), B["pos"].astype(np.int64), ps_id.astype(np.int64), B["click"].astype(np.int64)], 1)
    uB, cB = np.unique(keyB, axis=0, return_counts=True)
    ps_str = [repr(float(x)) for x in ps_vals]
    assert all(float(s) == float(x) for s, x in zip(ps_str, ps_vals)), "repr must round-trip exactly"
    bts_bytes = gz_csv("hour,item,position,propensity,click,count",
                       [uB[:, 0], uB[:, 1], uB[:, 2], uB[:, 3], uB[:, 4], cB],
                       [str, str, str, lambda i: ps_str[i], str, str])

    # ---- Random: unique (hour, item, position, click, pre_t0) with counts ----
    hR = ((R["ts"] - T_FLOOR) // HOUR).astype(np.int64)
    pre = (R["ts"] < T0_PREREG).astype(np.int64)
    keyR = np.stack([hR, R["item"].astype(np.int64), R["pos"].astype(np.int64), R["click"].astype(np.int64), pre], 1)
    uR, cR = np.unique(keyR, axis=0, return_counts=True)
    rnd_bytes = gz_csv("hour,item,position,click,pre_t0,count", [uR[:, i] for i in range(5)] + [cR], [str] * 6)

    # ---- checks 1: raw rows vs the extract (re-read from the bytes just written) ----
    def read(b: bytes) -> list[list[str]]:
        lines = gzip.decompress(b).decode().splitlines()
        return [ln.split(",") for ln in lines[1:]]

    eb, er = read(bts_bytes), read(rnd_bytes)
    H = 84
    raw_n, raw_c = np.bincount(hB, minlength=H), np.bincount(hB, weights=B["click"], minlength=H)
    raw_u = np.bincount(hB, weights=(1.0 / 80) / B["ps"], minlength=H)
    raw_uc = np.bincount(hB, weights=(1.0 / 80) / B["ps"] * B["click"], minlength=H)
    ex_n, ex_c, ex_u, ex_uc = [[0] * H for _ in range(2)] + [[[] for _ in range(H)] for _ in range(2)]
    for h, _, _, p, c, k in eb:
        h, c, k, u = int(h), int(c), int(k), (1.0 / 80) / float(p)
        ex_n[h] += k
        ex_c[h] += k * c
        ex_u[h].append(k * u)
        if c:
            ex_uc[h].append(k * u)
    chk = {
        "bts_rows": [int(mB.sum()), int(sum(int(x[5]) for x in eb))],
        "bts_hourly_rows_equal": bool(all(int(raw_n[h]) == ex_n[h] for h in range(H))),
        "bts_hourly_clicks_equal": bool(all(int(raw_c[h]) == ex_c[h] for h in range(H))),
        "bts_hourly_sum_inverse_propensity_rel_1e-12": bool(all(close(float(raw_u[h]), math.fsum(ex_u[h])) for h in range(H))),
        "bts_hourly_sum_click_over_propensity_rel_1e-12": bool(all(close(float(raw_uc[h]), math.fsum(ex_uc[h])) for h in range(H))),
        "random_rows": [int(mR.sum()), int(sum(int(x[5]) for x in er))],
        "random_pre_t0_rows": int(sum(int(x[5]) for x in er if x[4] == "1")),
        "random_hourly_rows_equal": bool(all(int(np.sum(hR == h)) == sum(int(x[5]) for x in er if int(x[0]) == h) for h in range(H))),
        "random_clicks_equal": bool(int(R["click"].sum()) == sum(int(x[5]) for x in er if x[3] == "1")),
    }

    # ---- checks 2: committed numbers recomputed from the extract alone ----
    pre_w = json.loads((RES / "obd_slice.json").read_text())

    def arm(rows, hours, rnd: bool, skip_pre=True):
        n = c = 0
        for x in rows:
            if int(x[0]) in hours and not (rnd and skip_pre and x[4] == "1"):
                k = int(x[5])
                n += k
                c += k * int(x[3] if rnd else x[4])
        p = c / n
        return n, p, math.sqrt(p * (1 - p) / (n - 1))  # = eval/run_obd_slice.py wald_mean on 0/1 clicks

    allh, h1, h2 = set(range(84)), set(range(42)), set(range(42, 84))
    nB, ctrB, _ = arm(eb, allh, False)
    nR, ctrR, _ = arm(er, allh, True)
    nRf, _, _ = arm(er, allh, True, skip_pre=False)
    cells = {"R1": arm(er, h1, True), "R2": arm(er, h2, True), "B1": arm(eb, h1, False), "B2": arm(eb, h2, False)}
    # IPW / SNIPW for the uniform policy on the BTS rows of W2 (committed halves "deploy BTS" off-policy cell)
    sw, swr = [], []
    for h, _, _, p, c, k in eb:
        if int(h) in h2:
            w = (1.0 / 80) / float(p)
            sw.append(int(k) * w)
            if c == "1":
                swr.append(int(k) * w)
    ipw = math.fsum(swr) / cells["B2"][0]
    snipw = math.fsum(swr) / math.fsum(sw)
    A = pre_w["a3_halves"]["A_deploy_BTS"]
    b2, r1, r2 = cells["B2"][1], cells["R1"][1], cells["R2"][1]
    com = {
        "n_bts_W": (nB, pre_w["window"]["n_bts"]),
        "n_random_W": (nR, pre_w["window"]["n_random"]),
        "n_random_W_floor (deviation run)": (nRf, 660907),
        "ctr_bts_W": (ctrB, pre_w["a2"]["truth"]),
        "ctr_random_W": (ctrR, pre_w["a2"]["random_ctr"]),
        **{f"halves_cell_{k}_v": (cells[k][1], pre_w["a3_halves"]["cells"][k]["v"]) for k in cells},
        **{f"halves_cell_{k}_se": (cells[k][2], pre_w["a3_halves"]["cells"][k]["se"]) for k in cells},
        "halves_naive_deploy": (b2 - r1, A["naive"]),
        "halves_reference_deploy": (b2 - r2, A["truth"]),
        "halves_deploy_IPW_effect": (b2 - ipw, A["IPW"]["policy_effect_after"]),
        "halves_deploy_SNIPW_effect": (b2 - snipw, A["SNIPW"]["policy_effect_after"]),
    }
    committed = {k: {"extract": float(a), "committed": float(b), "match_rel_1e-12": close(float(a), float(b))} for k, (a, b) in com.items()}
    ok = all(v for k, v in chk.items() if isinstance(v, bool)) and chk["bts_rows"][0] == chk["bts_rows"][1] \
        and chk["random_rows"][0] == chk["random_rows"][1] and all(v["match_rel_1e-12"] for v in committed.values())

    OUT.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, data, lines, rows in (("obd_bts_all.csv.gz", bts_bytes, len(uB), int(cB.sum())), ("obd_random_all.csv.gz", rnd_bytes, len(uR), int(cR.sum()))):
        (OUT / name).write_bytes(data)
        files[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "lines": lines, "rows": rows}
    ist = subprocess.run(["date", "+%Y-%m-%d %H:%M:%S IST"], env={"TZ": "Asia/Kolkata"}, capture_output=True, text=True).stdout.strip()
    manifest = {
        "dataset": "Open Bandit Dataset (ZOZO, Inc.), campaign 'All', policies Random and Bernoulli Thompson Sampling (BTS)",
        "licence": "CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/ (see demo/data/NOTICE.md)",
        "source_zip": "https://research.zozo.com/data_release/open_bandit_dataset.zip",
        "source_members": ["open_bandit_dataset/random/all/all.csv (full)", "open_bandit_dataset/bts/all/all.csv (time-ordered prefix, 100 MB compressed)"],
        "window_utc": {"start": "2019-11-24T00:00:00", "end_exclusive": "2019-11-27T12:00:00", "hours": 84,
                       "pre_registered_W_start": "2019-11-24T00:00:00.047846 (first BTS row; Random rows before it carry pre_t0 = 1)"},
        "columns": {"obd_bts_all.csv.gz": "hour,item,position,propensity,click,count",
                    "obd_random_all.csv.gz": "hour,item,position,click,pre_t0,count (logged propensity 0.0125 for every row)"},
        "hour": "floor((timestamp - 2019-11-24T00:00:00 UTC) / 1 h), 0..83",
        "propensity": "float64 exactly as parsed by eval/obd_zip_slice.py (pandas read_csv), written as Python's shortest round-trip repr; not rounded",
        "files": files,
        "checks_raw_vs_extract": chk,
        "checks_committed_numbers": committed,
        "all_checks_pass": bool(ok),
        "regenerate": "nice -n 10 .venv/bin/python demo/make_extract.py (needs the raw slices; see the script header)",
        "created_at": ist,
        "numpy": np.__version__,
    }
    (OUT / "extract_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({"files": files, "all_checks_pass": ok}, indent=1))
    for k, v in committed.items():
        print(f"  {k}: extract {v['extract']!r} vs committed {v['committed']!r} -> {'OK' if v['match_rel_1e-12'] else 'MISMATCH'}")
    if not ok:
        sys.exit("extract checks FAILED (see manifest)")


if __name__ == "__main__":
    main()
