"""C7 Adapter: run one adaptation policy over one day, test-then-train, under label delay.

At grid step t the policy (1) predicts with information <= t, then (2) receives the label of
step t-h (the first moment it is observable), updates heads / mixture weights / loss-based
detectors, (3) updates feature-based detectors, and (4) acts on alarms. Prediction latency
(`pred_ns`) and full-step latency (`step_ns`) are recorded per step.

Policies are declared as data in POLICIES so new ones (autoresearch candidates) are one dict away.
Head kinds: static | sgd(lr) | periodic(every, window) | alarm_refit(window, min_post) | regime(r)
Combiner: single | fixed_share(eta, alpha) ; detectors: ks | ph ; on_alarm: refit | boost
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from components.contracts import EpisodeResult, FeatureFrame, Labels
from components.forecaster import LogisticHead
from components.normalizer import EWMANorm, StaticNorm
from components.shift_detector import PageHinkley, RollingKS, calibrate_ks_null

POLICIES: dict[str, dict] = {
    "static_snorm":   dict(norm="static", heads=[("static",)]),
    "static_enorm":   dict(norm="ewma", heads=[("static",)]),
    "periodic_refit": dict(norm="ewma", heads=[("periodic", 3600, 3600)]),
    "online_sgd":     dict(norm="ewma", heads=[("sgd", 0.002)]),
    "ks_refit":       dict(norm="ewma", heads=[("alarm_refit", 1800, 600)], detectors=["ks"], on_alarm=["refit"]),
    "ph_refit":       dict(norm="ewma", heads=[("alarm_refit", 1800, 600)], detectors=["ph"], on_alarm=["refit"]),
    "regime_gated":   dict(norm="ewma", heads=[("regime", 0), ("regime", 1), ("regime", 2)], combine="gate"),
    "fixed_share":    dict(norm="ewma", heads=[("static",), ("sgd", 0.0005), ("sgd", 0.005), ("periodic", 900, 1800),
                                               ("regime", 0), ("regime", 1), ("regime", 2)],
                           combine="fixed_share"),
    "fs_ks_boost":    dict(norm="ewma", heads=[("static",), ("sgd", 0.0005), ("sgd", 0.005), ("periodic", 900, 1800),
                                               ("regime", 0), ("regime", 1), ("regime", 2), ("alarm_refit", 1800, 600)],
                           combine="fixed_share", detectors=["ks"], on_alarm=["refit", "boost"]),
    "ksc_refit":      dict(norm="ewma", heads=[("alarm_refit", 1800, 600)], detectors=["ksc"], on_alarm=["refit"]),
    "fs_ksc_boost":   dict(norm="ewma", heads=[("static",), ("sgd", 0.0005), ("sgd", 0.005), ("periodic", 900, 1800),
                                               ("regime", 0), ("regime", 1), ("regime", 2)],
                           combine="fixed_share", detectors=["ksc"], on_alarm=["boost"]),
}


@dataclass
class Context:
    """Everything learned on the training days (frozen before any test day is touched)."""
    names: tuple[str, ...]
    snorm: StaticNorm
    enorm: EWMANorm
    head_static: dict[str, LogisticHead]          # norm -> head
    head_regime: dict[str, list[LogisticHead]]    # norm -> heads per volatility tercile
    regime_edges: np.ndarray                      # rv_600s tercile edges from training
    ks_ref: np.ndarray
    ks_idx: list[int]
    cfg: dict = field(default_factory=dict)
    ks_thresholds: np.ndarray | None = None


def build_context(train: list[tuple[FeatureFrame, Labels]], cfg: dict) -> Context:
    names = train[0][0].names
    X = np.vstack([f.X for f, _ in train])
    y = np.concatenate([l.y for _, l in train])
    snorm = StaticNorm.fit(X)
    enorm = EWMANorm(snorm.mu, snorm.sd ** 2, cfg["ewma_halflife_steps"])
    Zs = snorm.transform(X)
    Ze = np.vstack([enorm.transform(f.X) for f, _ in train])
    rv = X[:, names.index("rv_600s_bps")]
    edges = np.quantile(rv, [1 / 3, 2 / 3])
    reg = np.digitize(rv, edges)
    heads, regime = {}, {}
    for key, Z in (("static", Zs), ("ewma", Ze)):
        heads[key] = LogisticHead(Z.shape[1], "static").fit(Z, y, C=cfg["C"])
        regime[key] = [LogisticHead(Z.shape[1], f"regime{r}").fit(Z[reg == r], y[reg == r], C=cfg["C"])
                       for r in range(3)]
    ks_names = cfg["ks_features"]
    ks_idx = [names.index(n) for n in ks_names]
    ks_ref = X[::cfg["ks_subsample"]][:, ks_idx]
    thr = None
    if cfg.get("ksc"):
        k = cfg["ks"]
        thr = calibrate_ks_null([f.X for f, _ in train], ks_idx, k["window"], k["subsample"],
                                cfg["ksc"]["stride"], cfg["ksc"]["quantile"])
    return Context(names, snorm, enorm, heads, regime, edges, ks_ref, ks_idx, cfg, thr)


def run_episode(policy: str, frame: FeatureFrame, labels: Labels, ctx: Context,
                spec: dict | None = None) -> EpisodeResult:
    spec = spec or POLICIES[policy]
    cfg = ctx.cfg
    norm = spec.get("norm", "ewma")
    Z = ctx.snorm.transform(frame.X) if norm == "static" else ctx.enorm.transform(frame.X)
    X = frame.X
    T, H, y = Z.shape[0], labels.h_steps, labels.y
    prior = ctx.head_static[norm]

    heads: list[LogisticHead] = []
    kinds = spec["heads"]
    for k in kinds:
        if k[0] == "regime":
            heads.append(ctx.head_regime[norm][k[1]].copy())
        else:
            heads.append(prior.copy(name=k[0]))
    K = len(heads)
    combine = spec.get("combine", "single")
    eta, alpha0 = cfg["fs_eta"], cfg["fs_alpha"]
    alpha_boost, boost_steps = cfg["fs_alpha_boost"], cfg["fs_boost_steps"]
    w = np.full(K, 1.0 / K)
    rv_i = ctx.names.index("rv_600s_bps")

    dets = spec.get("detectors", [])
    ks = RollingKS(ctx.ks_ref, ctx.ks_idx, list(cfg["ks_features"]), **cfg["ks"]) if "ks" in dets else None
    if "ksc" in dets:
        ks = RollingKS(ctx.ks_ref, ctx.ks_idx, list(cfg["ks_features"]), **cfg["ks"], thresholds=ctx.ks_thresholds)
    ph = PageHinkley(**cfg["ph"]) if "ph" in dets else None
    on_alarm = spec.get("on_alarm", [])
    alarm_heads = [i for i, k in enumerate(kinds) if k[0] == "alarm_refit"]

    P = np.full((T, K), 0.5)
    p = np.full(T, 0.5)
    pred_ns = np.zeros(T, dtype=np.int64)
    step_ns = np.zeros(T, dtype=np.int64)
    last_refit = [0] * K
    pending: int | None = None
    alarm_step = -1
    boost_until = -1
    alarms = []
    w_trace = np.zeros((T // 60 + 1, K))

    def fire(al):
        nonlocal pending, alarm_step, boost_until
        alarms.append(al)
        if "refit" in on_alarm and alarm_heads:
            alarm_step = al.step
            pending = al.step + H + kinds[alarm_heads[0]][2]
        if "boost" in on_alarm:
            boost_until = al.step + boost_steps

    perf = time.perf_counter_ns
    for t in range(T):
        t0 = perf()
        z = Z[t]
        if combine == "gate":
            r = int(np.searchsorted(ctx.regime_edges, X[t, rv_i], side="right"))
            P[t, r] = heads[r].predict(z)
            p[t] = P[t, r]
        else:
            for k in range(K):
                P[t, k] = heads[k].predict(z)
            p[t] = float(w @ P[t]) if combine == "fixed_share" else P[t, 0]
        t1 = perf()

        j = t - H
        if j >= 0 and not np.isnan(y[j]):
            yj = y[j]
            if combine == "fixed_share":
                lik = np.where(yj > 0.5, P[j], 1.0 - P[j])
                w = w * np.power(np.maximum(lik, 1e-12), eta)
                w /= w.sum()
                a = alpha_boost if t <= boost_until else alpha0
                w = (1.0 - a) * w + a / K
            for k, kind in enumerate(kinds):
                if kind[0] == "sgd":
                    heads[k].sgd_update(Z[j], yj, kind[1], cfg["sgd_l2"], prior)
            if ph is not None:
                pj = min(max(p[j], 1e-12), 1 - 1e-12)
                al = ph.update(t, -np.log(pj if yj > 0.5 else 1.0 - pj))
                if al is not None:
                    fire(al)
        for k, kind in enumerate(kinds):
            if kind[0] == "periodic" and t - last_refit[k] >= kind[1] and t - H >= kind[2] // 2:
                lo = max(0, t - H - kind[2] + 1)
                heads[k].refit_towards(Z[lo:t - H + 1], y[lo:t - H + 1], prior, lam=cfg["refit_lam"])
                last_refit[k] = t
        if ks is not None:
            al = ks.update(t, X)
            if al is not None:
                fire(al)
        if pending is not None and t >= pending:
            for k in alarm_heads:
                lo = max(alarm_step, t - H - kinds[k][1] + 1)
                heads[k].refit_towards(Z[lo:t - H + 1], y[lo:t - H + 1], prior, lam=cfg["refit_lam"])
            pending = None
        step_ns[t] = perf() - t0
        pred_ns[t] = t1 - t0
        if t % 60 == 0:
            w_trace[t // 60] = w
    return EpisodeResult(policy, frame.day, p, alarms, step_ns,
                         extra={"pred_ns": pred_ns, "w_trace": w_trace, "head_names": [str(k) for k in kinds]})
