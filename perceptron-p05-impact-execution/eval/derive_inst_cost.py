"""Derivation check for the frozen inst_cost = 0.005 (¢/share²) in calibration.json.

Model: a child of x shares costs c·x² (¢) beyond the half-spread, so the quantity-weighted mean
instantaneous cost per share is c·E[x²]/E[x]. TWAP children are 100 shares; PROBE children are
100·U(0,2), so E[x²]/E[x] = 100·(4/3). Hence c = Δinstant / (100·4/3 − 100).
Usage: .venv/bin/python eval/derive_inst_cost.py
"""
import os
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, "eval", "results", "E1_calib_train.csv"))
m = df.groupby("label")["instant_bps"].mean()
arr = df["arrival"].mean()
d_cents = (m["PROBE"] - m["TWAP"]) * 1e-4 * arr
c = d_cents / (100 * 4 / 3 - 100)
print(f"instant bps: PROBE {m['PROBE']:.4f}, TWAP {m['TWAP']:.4f}; diff {d_cents:.4f} ¢/share; derived c = {c:.5f} ¢/share² (frozen value 0.005)")
