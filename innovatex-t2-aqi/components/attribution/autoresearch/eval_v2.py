"""FROZEN evaluator v2 for C6 attribution (written by the lead after the independent review in ADR 001).
The autoresearch loop must never edit this file; it may only edit ../methods.py.

What changed vs v1 (all SIMULATED on REAL background PM10 (monitor 6929) + REAL ERA5 wind/RH):
  sensors   post-install co-calibrated ambient gain 0.95–1.05 (ring-wide co-location at install), a SEPARATE gain for
            coarse site dust, persistent offsets, saturation caps, fouling steps (sudden gain drops), slow drift, noise,
            humidity growth with per-node κ.
  quiet hrs night work on a share of nights (00–05 is no longer guaranteed clean).
  space     persistent node-specific background gradients; a neighbour site outside the ring on random days;
            road traffic next to a random node.
  wind      vane–plume decorrelation grows in light wind; persistent vane bias.
  baseline  `refvisit_<node>` columns: a weekly technician visit with a reference instrument gives each node's gain to
            ambient air at that hour (NaN otherwise), enabling a "co-calibrated + weekly re-fit" baseline.
  truths    truth_max = site contribution at the most-impacted node (exposure); truth_diff = site contribution at the true
            downwind-most node minus the true upwind-most node (what an ideal ring can see).
Scenarios: easy / medium / hard (parameters below), 5 seeds each.
Scalar (lower is better) = mean over the three scenarios of DEV MAE vs truth_max, abstentions scored as 0.
Also printed: selective MAE on covered hours, coverage, MAE vs truth_diff, CSI for truth_max > 50.
TEST (Jan–Sep 2026) is NOT printed by default: the lead runs `python eval_v2.py <method> --holdout` (TEST period,
unseen seeds, plus a hidden 'hard-rect' scenario with a different site geometry).

v2.1 (09:47): fixed reference visits (v2.0 required Q == 0 at Wed 11:00, a work hour, so every visit was NaN).
Run: OMP_NUM_THREADS=1 python eval_v2.py [method|all] [--holdout]
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import methods  # noqa: E402

DATA = os.path.join(HERE, "..", "..", "..", ".data")
DEV = ("2025-02-01", "2025-12-31")
TEST = ("2026-01-01", "2026-09-30")
EXCEED = 50.0
NODES = ["N", "E", "S", "W"]

SCENARIOS = {
    "easy":   dict(dust_gain=(0.8, 1.2), offset=5, cap=(1500,), fouling=0, foul_drop=(0.1, 0.1), night_work=0.0, gradient=(0, 0), neighbour=0.0, decor=10, vane_bias=0, half=(60, 60)),
    "medium": dict(dust_gain=(0.6, 1.2), offset=10, cap=(1000, 1500), fouling=1, foul_drop=(0.1, 0.2), night_work=0.1, gradient=(10, 25), neighbour=0.2, decor=30, vane_bias=15, half=(60, 60)),
    "hard":   dict(dust_gain=(0.4, 1.2), offset=10, cap=(500, 1000, 1500), fouling=2, foul_drop=(0.1, 0.3), night_work=0.3, gradient=(25, 50), neighbour=0.4, decor=60, vane_bias=30, half=(60, 60)),
}
HIDDEN = {"hard-rect": dict(SCENARIOS["hard"], half=(100, 40))}
DEV_SEEDS = [11, 12, 13, 14, 15]
HOLDOUT_SEEDS = [9101, 9102, 9103, 9104, 9105]


def load():
    bg = pd.read_parquet(os.path.join(DATA, "openaq", "station_6929.parquet"))["pm10"]
    bg = bg.where((bg > 0) & (bg < 1500)).dropna()
    met = pd.read_parquet(os.path.join(DATA, "openmeteo", "era5_28.61_77.21.parquet"))
    df = pd.DataFrame({"bg": bg}).join(met[["wind_speed_10m", "wind_direction_10m", "relative_humidity_2m"]], how="inner").dropna()
    df["ws"] = df["wind_speed_10m"] / 3.6
    return df


def sig(x):
    return 0.16 * x / np.sqrt(1 + 0.0004 * x), 0.14 * x / np.sqrt(1 + 0.0003 * x)  # Briggs urban, class D


def plume(Q, sources, receptor, ue, un, u):
    rx, ry = receptor
    c = 0.0
    for sx, sy in sources:
        dx, dy = rx - sx, ry - sy
        x = dx * ue + dy * un
        y = -dx * un + dy * ue
        xs = np.maximum(x, 1.0)
        sy_, sz_ = sig(xs)
        c = c + np.where(x > 1.0, (Q / len(sources)) / (np.pi * u * sy_ * sz_) * np.exp(-y ** 2 / (2 * sy_ ** 2)), 0.0)
    return c


def simulate(df, rng, sc):
    n, idx = len(df), df.index
    hx, hy = sc["half"]
    geom = {"N": (0.0, hy), "E": (hx, 0.0), "S": (0.0, -hy), "W": (-hx, 0.0)}
    sources = [(x, y) for x in (-hx / 2, 0, hx / 2) for y in (-hy / 2, 0, hy / 2)]
    days = idx.normalize(); uday = days.unique()
    work_day = (idx.hour >= 8) & (idx.hour < 18) & (idx.dayofweek < 6)
    night_work_days = pd.Series(rng.random(len(uday)) < sc["night_work"], index=uday).reindex(days).values
    work = work_day | (night_work_days & (idx.hour < 5))
    unc = rng.random(len(uday)) < 0.3
    qd = pd.Series(np.where(unc, rng.lognormal(np.log(0.6), 0.4, len(uday)), rng.lognormal(np.log(0.1), 0.4, len(uday))), index=uday)
    Q = np.where(work, qd.reindex(days).values * rng.lognormal(0, 0.5, n), 0.0) * 1e6
    ws = df["ws"].values
    decor = np.where(ws < 1.0, sc["decor"] * 2, sc["decor"])
    wd_true = (df["wind_direction_10m"].values + rng.normal(0, 1, n) * decor) % 360
    u = np.maximum(ws, 0.5)
    to = np.deg2rad((wd_true + 180) % 360); ue, un = np.sin(to), np.cos(to)
    site = {k: plume(Q, sources, geom[k], ue, un, u) for k in NODES}
    pool = np.where(ws < 0.5, Q / (0.5 * 2 * max(hx, hy) * 10.0) * 0.3, 0.0)
    for k in NODES:
        site[k] = site[k] + pool
    S = np.stack([site[k] for k in NODES], 1)
    proj = np.stack([geom[k][0] * ue + geom[k][1] * un for k in NODES], 1)
    rows = np.arange(n)
    truth_max = S.max(1)
    truth_diff = S[rows, proj.argmax(1)] - S[rows, proj.argmin(1)]
    # neighbour site 150–250 m away in a random direction, active on random days
    ang = rng.uniform(0, 2 * np.pi); dist = rng.uniform(150, 250)
    nb_src = [(dist * np.sin(ang), dist * np.cos(ang))]
    nb_on = pd.Series(rng.random(len(uday)) < sc["neighbour"], index=uday).reindex(days).values & work_day
    Qn = np.where(nb_on, rng.lognormal(np.log(0.6), 0.4, n), 0.0) * 1e6
    road_node = NODES[rng.integers(4)]
    traffic = np.where(np.isin(idx.hour, [8, 9, 10, 17, 18, 19, 20]), 1.0, np.where((idx.hour >= 23) | (idx.hour < 6), 0.3, 0.6))
    rh = np.clip(df["relative_humidity_2m"].values, 0, 98)
    tdays = (idx - idx[0]).total_seconds().values / 86400
    obs = pd.DataFrame(index=idx)
    week_visit = (idx.dayofweek == 2) & (idx.hour == 11)  # weekly reference visit, Wed 11:00
    for k in NODES:
        amb = df["bg"].values * (1 + rng.normal(0, 0.03, n)) + rng.uniform(*sc["gradient"]) + plume(Qn, nb_src, geom[k], ue, un, u)
        if k == road_node:
            amb = amb + 20.0 * traffic
        g_amb = rng.uniform(0.95, 1.05) * np.clip(1 + rng.normal(0, 0.10) * tdays / 365, 0.5, 1.5)
        for _ in range(sc["fouling"]):
            t0 = rng.uniform(0, tdays[-1]); g_amb = g_amb * np.where(tdays >= t0, 1 - rng.uniform(*sc["foul_drop"]), 1.0)
        g_dust = rng.uniform(*sc["dust_gain"])
        kappa = 0.05 * rng.uniform(0.8, 1.2)
        hum = 1 + kappa * rh / (100 - rh)
        clean = g_amb * amb * hum
        meas = clean + g_amb * g_dust * site[k] * hum + rng.uniform(-sc["offset"], sc["offset"]) + rng.normal(0, 1, n) * (0.05 * (amb + site[k]) + 2)
        meas = np.clip(meas, 0, rng.choice(sc["cap"]))
        obs[f"raw_{k}"] = meas
        # what a reference instrument visit would report: the node's gain to ambient air at that hour
        obs[f"refvisit_{k}"] = np.where(week_visit, meas / np.maximum(amb + site[k], 1.0), np.nan)  # v2.1: co-located reference sees the same total air
    obs["rh"] = rh
    obs["ws_meas"] = ws * (1 + rng.normal(0, 0.1, n))
    obs["wd_meas"] = (wd_true + sc["vane_bias"] + rng.normal(0, 10, n)) % 360
    return obs, truth_max, truth_diff, geom


def score(est, abstain, tmax, tdiff, mask):
    abstain = abstain | ~np.isfinite(est)
    est = np.where(np.isfinite(est), est, 0.0)
    e = np.where(abstain, 0.0, est)
    cov = mask & ~abstain
    o, f = tmax[mask] > EXCEED, e[mask] > EXCEED
    h, m, fa = (o & f).sum(), (o & ~f).sum(), (~o & f).sum()
    return dict(mae=float(np.mean(np.abs(e[mask] - tmax[mask]))),
                sel_mae=float(np.mean(np.abs(est[cov] - tmax[cov]))) if cov.any() else float("nan"),
                diff_mae=float(np.mean(np.abs(est[cov] - tdiff[cov]))) if cov.any() else float("nan"),
                coverage=float(cov.sum() / max(1, mask.sum())), csi=float(h / max(1, h + m + fa)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    holdout = "--holdout" in sys.argv
    which = args[0] if args else methods.CANDIDATE
    names = list(methods.METHODS) if which == "all" else [which]
    df = load()
    period = TEST if holdout else DEV
    seeds = HOLDOUT_SEEDS if holdout else DEV_SEEDS
    scen = dict(SCENARIOS, **HIDDEN) if holdout else SCENARIOS
    res = {(nm, s): [] for nm in names for s in scen}
    for sname, sc in scen.items():
        for seed in seeds:
            obs, tmax, tdiff, geom = simulate(df, np.random.default_rng(seed), sc)
            mask = (obs.index >= period[0]) & (obs.index <= period[1] + " 23:00")
            for nm in names:
                est, ab = methods.METHODS[nm](obs, geom)
                res[(nm, sname)].append(score(np.asarray(est, float), np.asarray(ab, bool), tmax, tdiff, mask))
    tag = "HOLDOUT(TEST, unseen seeds, +hidden scenario)" if holdout else "DEV"
    for nm in names:
        per = {s: np.mean([r["mae"] for r in res[(nm, s)]]) for s in scen}
        scalar = float(np.mean(list(per.values())))
        detail = " ".join(f"{s}={per[s]:.1f}±{np.std([r['mae'] for r in res[(nm, s)]]):.1f}" for s in scen)
        cov = np.mean([r["coverage"] for s in scen for r in res[(nm, s)]])
        sel = np.nanmean([r["sel_mae"] for s in scen for r in res[(nm, s)]])
        dif = np.nanmean([r["diff_mae"] for s in scen for r in res[(nm, s)]])
        csi = np.mean([r["csi"] for s in scen for r in res[(nm, s)]])
        print(f"{nm:18s} {tag} scalar={scalar:.2f} | {detail} | sel_MAE {sel:.1f} diff_MAE {dif:.1f} cov {cov:.2f} CSI>50 {csi:.2f}")


if __name__ == "__main__":
    main()
