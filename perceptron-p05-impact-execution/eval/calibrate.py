"""Calibrate from TRAIN seeds only: VWAP volume curve, own-impact kernel, instantaneous-cost slope.

Usage: .venv/bin/python eval/calibrate.py --exp E1_calib_train
Writes eval/results/calibration.json.
"""
import argparse, glob, json, os, pickle, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "components", "impact_model"))
from impact_model.propagator import fit_exp_propagator, r2_on  # noqa: E402

START_S = 0.0  # grid is seconds since 09:35:00


def load(exp):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, ".data", "runs", exp, "seed_*.pkl"))):
        out.append(pickle.load(open(f, "rb")))
    return out


def episodes(raws, label, start_ns):
    eps = []
    for r in raws:
        run = r["runs"][label]
        fills_s = [((t - start_ns) / 1e9, q) for t, _, q in run["fills"]]
        eps.append(dict(fills_s=fills_s, grid_s=np.arange(len(run["path"]), dtype=float), path=run["path"]))
    return eps


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", default="E1_calib_train")
    ap.add_argument("--out", default="calibration.json", help="file name under eval/results/")
    a = ap.parse_args()
    raws = load(a.exp)
    sys.path.insert(0, os.path.join(ROOT, "components", "sim_env"))
    import sim_env  # noqa
    from sim_env.world import ns_at
    start_ns = ns_at("09:35:00")
    vol = np.array([r["slot_vol"] for r in raws], float)
    prof = vol.mean(0); cum = np.cumsum(prof) / prof.sum()
    eps_probe = episodes(raws, "PROBE", start_ns)
    eps_twap = episodes(raws, "TWAP", start_ns)
    half = len(raws) // 2
    fit = fit_exp_propagator(eps_probe[:half] + eps_twap[:half])
    oos = dict(probe=r2_on(eps_probe[half:], fit, 1200), twap=r2_on(eps_twap[half:], fit, 1200))
    cal = dict(source_exp=a.exp, n_seeds=len(raws), vwap_cum_profile=[float(x) for x in cum],
               mean_slot_volume=[float(x) for x in prof], kernel=fit, kernel_fit_seeds="first half (train)",
               kernel_oos_second_half=oos, inst_cost_cents_per_share2=0.005,
               inst_cost_note="slope from PROBE vs TWAP instant-cost gap in E1 (0.130 vs 0.114 bps at ~100-share mean child)")
    out = os.path.join(ROOT, "eval", "results", a.out)
    json.dump(cal, open(out, "w"), indent=1)
    print(json.dumps({k: cal[k] for k in ("kernel", "kernel_oos_second_half")}, indent=1))
    print("vwap cum profile (every 5th slot):", np.round(cum[::5], 3))


if __name__ == "__main__":
    main()
