"""SYNTHETIC longitudinal cohort + Anganwadi measurement process (evaluation only).

Everything produced here is synthetic and labelled `synthetic=True`. The point is not
to reproduce India; it is to give every component a ground truth (true growth, true
wasting onsets, true worker behaviour) so the pipeline can be measured end to end.
Calibration targets and their sources live in `calibration.yaml`; `calibrate.py`
reports achieved vs target values.

Model (monthly steps, birth to 59 months):
- Length-for-age z (LAZ): population curve declining with age + child offset + slow AR noise.
- Weight-for-length z (WLZ): child mean + AR(1) noise + *faltering episodes*: a gradual
  decline over 1-3 months (the precursor an early-warning system can see), then partial
  monthly recovery. Episode hazard rises with low birth weight, maternal short stature,
  household risk, infancy and the lean season.
- Health-system signals (only visible if records are linked): birth weight (RCH),
  illness recorded by ASHA (more likely when an episode starts), overdue vaccines (U-WIN).
- Measurement at the AWC by one of three worker behaviours: `good`, `noisy` (error,
  heaping, wrong position) or `fabricating` (real measurement only some months; other
  months copy-forward a smoothly increasing value — which hides faltering).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
import pandas as pd

from components.growth_standards import who


@dataclass
class SimConfig:
    seed: int = 7
    n_projects: int = 4
    sectors_per_project: int = 5
    awcs_per_sector: int = 6
    births_per_awc_month: float = 0.85  # ~50 under-5 children per AWC at steady state
    window_start: date = date(2024, 10, 1)
    window_months: int = 24
    p_worker_type: dict = field(default_factory=lambda: {"good": 0.6, "noisy": 0.25, "fabricating": 0.15})
    p_lbw: float = 0.18
    p_maternal_short: float = 0.10
    p_migrant: float = 0.08
    # WLZ level and episode dynamics (tuned by calibrate.py; see calibration.yaml)
    wlz_mean: float = -1.05
    wlz_child_sd: float = 0.55
    wlz_ar_sd: float = 0.32
    wlz_ar_phi: float = 0.6
    lbw_wlz_shift: float = -1.45
    birth_extra_sd: float = 0.62
    episode_base_hazard: float = 0.05
    episode_depth: tuple = (0.7, 1.9)
    recovery_keep: float = 0.72  # fraction of deficit kept each recovery month
    laz_mean_birth: float = -0.55
    laz_decline: float = 1.25
    laz_child_sd: float = 0.95
    # fabricating-worker pattern (defaults = frozen-eval world; vary for anti-gaming checks)
    fab_real_p: float = 0.33
    fab_dw: tuple = (0.05, 0.25)
    fab_dl: tuple = (0.3, 1.0)


SEASON = np.array([1.0, 1.0, 1.0, 1.0, 1.1, 1.25, 1.5, 1.6, 1.4, 1.1, 1.0, 1.0])  # Jan..Dec hazard multiplier (assumption)


def _geo(cfg: SimConfig) -> pd.DataFrame:
    rows = []
    for p in range(cfg.n_projects):
        for s in range(cfg.sectors_per_project):
            for a in range(cfg.awcs_per_sector):
                rows.append(
                    dict(state_code="SYN", district_code="SYN-D01", project_code=f"P{p+1}",
                         sector_code=f"P{p+1}S{s+1}", awc_code=f"P{p+1}S{s+1}A{a+1:02d}")
                )
    return pd.DataFrame(rows)


def _add_months(d: date, k: int) -> date:
    y, m = divmod(d.month - 1 + k, 12)
    return date(d.year + y, m + 1, min(d.day, 28))


def simulate(cfg: SimConfig | None = None) -> dict[str, pd.DataFrame]:
    cfg = cfg or SimConfig()
    rng = np.random.default_rng(cfg.seed)
    geo = _geo(cfg)
    n_awc = len(geo)
    types = list(cfg.p_worker_type)
    geo["worker_type"] = rng.choice(types, size=n_awc, p=[cfg.p_worker_type[t] for t in types])
    geo["worker_id"] = [f"W{i:04d}" for i in range(n_awc)]
    geo["gm_day"] = rng.integers(5, 26, size=n_awc)

    # ---------------------------------------------------------------- children
    birth_months = 59 + cfg.window_months  # cohorts alive at some point in the window
    counts = rng.poisson(cfg.births_per_awc_month * birth_months, size=n_awc)
    awc_idx = np.repeat(np.arange(n_awc), counts)
    n = len(awc_idx)
    first_birth = _add_months(cfg.window_start, -59)
    birth_offset_days = rng.integers(0, birth_months * 30, size=n)
    dob = np.array([first_birth + timedelta(days=int(x)) for x in birth_offset_days])
    sex = rng.choice(["M", "F"], size=n)
    lbw = rng.random(n) < cfg.p_lbw
    mshort = rng.random(n) < cfg.p_maternal_short
    migrant = rng.random(n) < cfg.p_migrant
    hh_risk = rng.normal(0, 1, n) + 0.6 * migrant
    child_key = np.array([f"C{i:06d}" for i in range(n)])

    # ---------------------------------------------------------------- latent growth (N x 60)
    A = 60
    age_m = np.arange(A)
    cal_month = np.array([[(d.month - 1 + a) % 12 for a in age_m] for d in dob])
    laz_pop = cfg.laz_mean_birth - cfg.laz_decline * (1 - np.exp(-age_m / 14.0))
    laz_child = rng.normal(0, cfg.laz_child_sd, n) - 0.45 * lbw - 0.35 * mshort - 0.15 * hh_risk
    laz_noise = np.cumsum(rng.normal(0, 0.06, (n, A)), axis=1)
    laz = laz_pop[None, :] + laz_child[:, None] + laz_noise

    wlz_child = cfg.wlz_mean + rng.normal(0, cfg.wlz_child_sd, n) - 0.1 * hh_risk
    ar = np.zeros((n, A))
    ar[:, 0] = rng.normal(0, cfg.birth_extra_sd, n) + cfg.lbw_wlz_shift * lbw
    for a in range(1, A):
        ar[:, a] = cfg.wlz_ar_phi * ar[:, a - 1] + rng.normal(0, cfg.wlz_ar_sd, n)

    offset = np.zeros((n, A))
    in_ep = np.zeros((n, A), bool)
    illness = np.zeros((n, A), bool)
    ep_start = np.zeros((n, A), bool)
    decline_left = np.zeros(n, int)
    step = np.zeros(n)
    cur = np.zeros(n)
    risk_lin = 0.55 * lbw + 0.35 * mshort + 0.35 * hh_risk
    age_mult = np.where(age_m < 6, 1.5, np.where(age_m < 24, 1.3, 0.55))
    for a in range(1, A):
        haz = cfg.episode_base_hazard * age_mult[a] * SEASON[cal_month[:, a]] * np.exp(risk_lin)
        start = (decline_left == 0) & (cur > -0.15) & (rng.random(n) < haz)
        k = rng.integers(1, 4, n)  # decline over 1-3 months (precursor window)
        depth = rng.uniform(*cfg.episode_depth, n)
        decline_left = np.where(start, k, decline_left)
        step = np.where(start, depth / k, step)
        ep_start[:, a] = start
        declining = decline_left > 0
        cur = np.where(declining, cur - step, cur * cfg.recovery_keep)
        decline_left = np.maximum(decline_left - declining, 0)
        offset[:, a] = cur
        in_ep[:, a] = cur < -0.3
        illness[:, a] = rng.random(n) < np.where(start, 0.45, 0.06)
    wlz = wlz_child[:, None] + ar + offset

    # true sizes
    age_days = np.rint(age_m[None, :] * who.DAYS_PER_MONTH).astype(int) + np.zeros((n, 1), int)
    sex_mat = np.repeat(sex[:, None], A, axis=1)
    length = who.length_from_z(laz.ravel(), sex_mat.ravel(), age_days.ravel()).reshape(n, A)
    weight = who.weight_from_wlz(wlz.ravel(), sex_mat.ravel(), length.ravel(), age_days.ravel()).reshape(n, A)
    muacz = 0.75 * wlz + rng.normal(0, 0.5, (n, A))
    muac = who.value_from_z(muacz.ravel(), *who.age_lms("acanthro", who.sex_code(sex_mat.ravel()), age_days.ravel())).reshape(n, A)

    # ---------------------------------------------------------------- calendar window
    win_months = [_add_months(cfg.window_start, k) for k in range(cfg.window_months)]
    rows = []
    for k, m0 in enumerate(win_months):
        gm_dates = np.array([date(m0.year, m0.month, int(geo.gm_day[i])) for i in range(n_awc)])
        meas = gm_dates[awc_idx]
        ad = np.array([(meas[i] - dob[i]).days for i in range(n)])
        a_m = np.floor(ad / who.DAYS_PER_MONTH).astype(int)
        alive = (ad >= 0) & (a_m < A)
        idx = np.nonzero(alive)[0]
        rows.append(pd.DataFrame(dict(child_idx=idx, month_index=k, measured_on=meas[idx], age_days=ad[idx], age_m=a_m[idx])))
    cm = pd.concat(rows, ignore_index=True)
    ci, am = cm.child_idx.to_numpy(), cm.age_m.to_numpy()
    cm["child_key"] = child_key[ci]
    cm["true_laz"], cm["true_wlz"] = laz[ci, am], wlz[ci, am]
    cm["true_length"], cm["true_weight"], cm["true_muac"] = length[ci, am], weight[ci, am], muac[ci, am]
    cm["true_in_episode"], cm["true_episode_start"], cm["illness"] = in_ep[ci, am], ep_start[ci, am], illness[ci, am]
    cm["awc_i"] = awc_idx[ci]

    # ---------------------------------------------------------------- observation process
    wt = geo.worker_type.to_numpy()[cm.awc_i]
    m = len(cm)
    p_meas = np.where(migrant[ci], 0.6, 0.88)
    measured = rng.random(m) < p_meas
    w_sd = np.select([wt == "good", wt == "noisy"], [0.05, 0.15], 0.08)
    l_sd = np.select([wt == "good", wt == "noisy"], [0.5, 1.4], 0.8)
    w_obs = cm.true_weight.to_numpy() + rng.normal(0, w_sd)
    l_obs = cm.true_length.to_numpy() + rng.normal(0, l_sd)
    heap_w = (wt == "noisy") & (rng.random(m) < 0.35)
    heap_l = (wt != "good") & (rng.random(m) < 0.45)
    w_obs = np.where(heap_w, np.round(w_obs * 2) / 2, np.round(w_obs, 1))
    l_obs = np.where(heap_l, np.round(l_obs), np.round(l_obs, 1))
    position = np.where(cm.age_days.to_numpy() < 731, "recumbent", "standing")
    wrong_pos = (wt == "noisy") & (rng.random(m) < 0.15)
    position = np.where(wrong_pos, np.where(position == "recumbent", "standing", "recumbent"), position)
    gross = rng.random(m) < 0.004
    w_obs = np.where(gross & (rng.random(m) < 0.5), w_obs * 10, w_obs)
    muac_obs = np.where((cm.age_m >= 6) & (rng.random(m) < 0.35), np.round(cm.true_muac + rng.normal(0, 0.3, m), 1), np.nan)

    cm["recorded"] = measured
    cm["weight_kg"], cm["length_height_cm"], cm["measure_position"], cm["muac_cm"] = w_obs, l_obs, position, muac_obs
    cm["copied"] = False
    # fabricating workers: real measurement only in ~1 of 3 months, otherwise copy forward with smooth gains
    cm = cm.sort_values(["child_key", "month_index"]).reset_index(drop=True)
    fab = geo.worker_type.to_numpy()[cm.awc_i] == "fabricating"
    real_month = rng.random(len(cm)) < cfg.fab_real_p
    last_w, last_l, last_key = np.nan, np.nan, None
    W, L, K = cm.weight_kg.to_numpy(copy=True), cm.length_height_cm.to_numpy(copy=True), cm.child_key.to_numpy()
    rec, cop = cm.recorded.to_numpy(copy=True), cm.copied.to_numpy(copy=True)
    for i in range(len(cm)):
        if K[i] != last_key:
            last_w, last_l, last_key = np.nan, np.nan, K[i]
        if fab[i]:
            rec[i] = True
            if not real_month[i] and np.isfinite(last_w):
                W[i] = np.round(last_w + rng.uniform(*cfg.fab_dw), 1)
                L[i] = np.round(last_l + rng.uniform(*cfg.fab_dl), 1)
                cop[i] = True
        if rec[i]:
            last_w, last_l = W[i], L[i]
    cm["weight_kg"], cm["length_height_cm"], cm["recorded"], cm["copied"] = W, L, rec, cop

    # recorded DOB (age heaping: some DOBs recorded as the 1st of the month or 1 January)
    dob_rec = dob.copy()
    wt_child = geo.worker_type.to_numpy()[awc_idx]
    heap = rng.random(n) < np.select([wt_child == "good", wt_child == "noisy"], [0.03, 0.3], 0.4)
    jan = rng.random(n) < 0.3
    dob_rec = np.array([
        (date(d.year, 1, 1) if j else date(d.year, d.month, 1)) if h else d for d, h, j in zip(dob, heap, jan)
    ])

    g = geo.iloc[cm.awc_i.to_numpy()].reset_index(drop=True)
    obs = cm[cm.recorded].copy()
    gobs = g[cm.recorded.to_numpy()]
    child_pos = {k: i for i, k in enumerate(child_key)}
    cidx = obs.child_key.map(child_pos).to_numpy()
    measurements = pd.DataFrame(dict(
        event_id=[f"E{i:08d}" for i in range(len(obs))],
        child_key=obs.child_key.to_numpy(),
        state_code=gobs.state_code.to_numpy(), district_code=gobs.district_code.to_numpy(),
        project_code=gobs.project_code.to_numpy(), sector_code=gobs.sector_code.to_numpy(),
        awc_code=gobs.awc_code.to_numpy(),
        sex=sex[cidx], dob=pd.to_datetime(dob_rec[cidx]), measured_on=pd.to_datetime(obs.measured_on.to_numpy()),
        weight_kg=obs.weight_kg.to_numpy(), length_height_cm=obs.length_height_cm.to_numpy(),
        measure_position=obs.measure_position.to_numpy(), muac_cm=obs.muac_cm.to_numpy(), oedema=False,
        measured_by=gobs.worker_id.to_numpy(), source="simulator", synthetic=True,
    ))

    truth_monthly = cm[["child_key", "month_index", "measured_on", "age_days", "true_laz", "true_wlz", "true_weight",
                        "true_length", "true_in_episode", "true_episode_start", "illness", "recorded", "copied"]].copy()
    truth_monthly["measured_on"] = pd.to_datetime(truth_monthly.measured_on)
    truth_monthly["awc_code"] = g.awc_code.to_numpy()
    children = pd.DataFrame(dict(child_key=child_key, awc_code=geo.awc_code.to_numpy()[awc_idx], sex=sex,
                                 dob_true=pd.to_datetime(dob), dob_recorded=pd.to_datetime(dob_rec), lbw=lbw,
                                 maternal_short=mshort, migrant=migrant, hh_risk=hh_risk,
                                 birth_weight_kg=np.round(weight[:, 0], 2), synthetic=True))

    # health-system events (would arrive via linkage: RCH birth weight, ASHA illness, U-WIN overdue doses)
    h = []
    bw_known = rng.random(n) < 0.8
    for i in np.nonzero(bw_known)[0]:
        h.append((child_key[i], dob[i], "birth_weight", float(np.round(weight[i, 0], 2)), "rch"))
    ill = truth_monthly[truth_monthly.illness & (rng.random(len(truth_monthly)) < 0.6)]
    for r in ill.itertuples():
        h.append((r.child_key, r.measured_on.date() - timedelta(days=int(rng.integers(3, 25))), "illness_diarrhoea", None, "rch"))
    miss_p = 1 / (1 + np.exp(-(-2.6 + 0.8 * hh_risk + 0.9 * migrant)))
    for r in truth_monthly[(truth_monthly.age_days < 730)].itertuples():
        if rng.random() < miss_p[child_pos[r.child_key]] * 0.25:
            h.append((r.child_key, r.measured_on.date(), "immunisation_missed", None, "uwin"))
    health = pd.DataFrame(h, columns=["child_key", "occurred_on", "kind", "value", "source"])
    health["occurred_on"] = pd.to_datetime(health.occurred_on)
    health["synthetic"] = True
    return dict(geo=geo, children=children, truth_monthly=truth_monthly, measurements=measurements, health_events=health)


if __name__ == "__main__":
    out = simulate()
    for k, v in out.items():
        print(k, v.shape)
