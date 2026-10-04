"""C11 Simulator: before/after logs with exact counterfactual ground truth (SYNTHETIC data).

World: K actions, d-dim contexts. P(R=1 | x, a, period, u) = sigmoid(bias_a + x.theta_a + drift*period + 1.5*u*z_a).
- Before period: the old policy pi0 is deployed; after the switch, the new policy pi1 is deployed.
- `mix_shift` moves the after-period context mean (a different user mix); `response_drift` shifts every logit
  after the switch (seasonality or a demand shock): both move the before/after number without any policy effect.
- `hidden_confounding` = kappa > 0: an unobserved u ~ U(-1, 1) tilts the deployed new policy's actions by
  exp(kappa*u*z_a) (an unlogged manual override) while u also raises the reward of z-aligned actions; the logged
  propensities are then the nominal ones (wrong).
- `feedback` = f: the policy shapes its own audience. After the switch, users shift by f * fb_dir only because the NEW
  policy runs (fb_dir points at the context region where the new policy's favourite action pays). Had the old policy been
  kept, they would not have shifted (common random numbers give that counterfactual exactly).
- `nonlinearity` = lam: adds lam * (s_a * (x0^2 - 1) + c_a * sin(2 x1)) to every logit, which the linear-logistic
  reward model cannot represent (misspecification test).
New random draws are taken after the original ones, so worlds with feedback = nonlinearity = 0 are unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from architecture.contracts.contracts import BanditLog, GroundTruth, ScenarioConfig

U_REWARD = 1.5


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


class World:
    def __init__(self, cfg: ScenarioConfig):
        self.cfg = cfg
        rng = np.random.default_rng(cfg.world_seed)
        K, d = cfg.n_actions, cfg.dim
        self.theta = rng.normal(0, 0.6, (K, d))
        self.bias = rng.normal(-1.2, 0.3, K)
        m = rng.normal(0, 1, d)
        self.mix_dir = m / np.linalg.norm(m)
        n_old, n_new = rng.normal(0, 0.6, (K, d)), rng.normal(0, 0.6, (K, d))
        self.w_old = cfg.old_policy_quality * self.theta + (1 - cfg.old_policy_quality) * n_old
        self.w_new = cfg.new_policy_quality * self.theta + (1 - cfg.new_policy_quality) * n_new
        self.z = np.where(np.arange(K) % 2 == 0, 1.0, -1.0)
        self.s_nl, self.c_nl = rng.normal(0, 1, K), rng.normal(0, 1, K)
        fav = int(np.argmax(self.policy(rng.normal(0, 1, (4000, d)), "new").mean(0)))
        self.fb_dir = self.theta[fav] / np.linalg.norm(self.theta[fav])

    def contexts(self, n: int, period: int, rng, new_policy_running: bool = False):
        X = rng.normal(0, 1, (n, self.cfg.dim)) + self.cfg.mix_shift * period * self.mix_dir
        if new_policy_running and period == 1:
            X = X + self.cfg.feedback * self.fb_dir
        u = rng.uniform(-1, 1, n)
        return X, u

    def reward_prob(self, X, u, period: int):
        logit = X @ self.theta.T + self.bias + self.cfg.response_drift * period + U_REWARD * u[:, None] * self.z
        if self.cfg.nonlinearity and self.cfg.nonlinear_axis == "fixed":
            logit = logit + self.cfg.nonlinearity * (np.outer(X[:, 0] ** 2 - 1, self.s_nl) + np.outer(np.sin(2 * X[:, 1]), self.c_nl))
        elif self.cfg.nonlinearity:
            logit = logit + self.cfg.nonlinearity * np.outer((X @ self.mix_dir) ** 2 - 1, self.s_nl)
        return _sigmoid(logit + self.cfg.reward_offset)

    def policy(self, X, which: str):
        """Nominal policy pi(a|x): softmax of the policy's scorer mixed with epsilon-uniform exploration."""
        W = self.w_old if which == "old" else self.w_new
        s = self.cfg.temperature * (X @ W.T)
        p = np.exp(s - s.max(1, keepdims=True))
        p /= p.sum(1, keepdims=True)
        return (1 - self.cfg.epsilon) * p + self.cfg.epsilon / self.cfg.n_actions

    def deployed(self, X, u, which: str):
        """Actual behaviour: the after-period deployment carries the hidden override when kappa > 0."""
        p = self.policy(X, which)
        k = self.cfg.hidden_confounding
        if which == "new" and k > 0:
            p = p * np.exp(k * u[:, None] * self.z)
            p /= p.sum(1, keepdims=True)
        return p


def _draw(P, rng):
    return (rng.random(len(P))[:, None] > P.cumsum(1)).sum(1).clip(0, P.shape[1] - 1)


@dataclass
class SimOutput:
    before: BanditLog
    after: BanditLog
    truth: GroundTruth
    world: World


def ground_truth(world: World, n_mc: int = 400_000) -> GroundTruth:
    rng = np.random.default_rng(world.cfg.world_seed + 99)
    Xb, ub = world.contexts(n_mc, 0, rng)
    Xa, ua = world.contexts(n_mc, 1, rng, new_policy_running=True)
    Xa_cf = Xa - world.cfg.feedback * world.fb_dir  # the same users had the old policy been kept (no feedback shift)
    qb, qa, q_mix = world.reward_prob(Xb, ub, 0), world.reward_prob(Xa, ua, 1), world.reward_prob(Xa, ua, 0)
    v = lambda P, q: float((P * q).sum(1).mean())
    p_nom, p_act = world.policy(Xa, "new"), world.deployed(Xa, ua, "new")
    odds = lambda p: p / (1 - p)
    ratio = odds(p_act) / odds(p_nom)
    return GroundTruth(
        v_before_old=v(world.policy(Xb, "old"), qb),
        v_before_new=v(world.deployed(Xb, ub, "new"), qb),  # the new policy as it would actually run (incl. any override); review C6
        v_after_old=v(world.policy(Xa, "old"), qa),
        v_after_new=v(p_act, qa),
        v_mix_old=v(world.policy(Xa, "old"), q_mix),
        gamma_true=float(np.maximum(ratio, 1 / ratio).max()),
        v_after_old_cf=v(world.policy(Xa_cf, "old"), world.reward_prob(Xa_cf, ua, 1)),
    )


def simulate(cfg: ScenarioConfig, truth: GroundTruth | None = None) -> SimOutput:
    world = World(cfg)
    rng = np.random.default_rng(1_000_003 * (cfg.seed + 1))
    logs = []
    for period, which, n in ((0, "old", cfg.n_before), (1, "new", cfg.n_after)):
        X, u = world.contexts(n, period, rng, new_policy_running=(which == "new"))
        P_act = world.deployed(X, u, which)
        A = _draw(P_act, rng)
        R = (rng.random(n) < world.reward_prob(X, u, period)[np.arange(n), A]).astype(float)
        P_logged = world.policy(X, which)  # what the system logs: nominal propensities
        ps = P_logged[np.arange(n), A]
        if cfg.pscore_noise_sims:  # logged propensity = Monte-Carlo estimate (count / M), floored at 1/M
            ps = np.maximum(rng.binomial(cfg.pscore_noise_sims, ps) / cfg.pscore_noise_sims, 1.0 / cfg.pscore_noise_sims)
        logs.append(
            BanditLog(X=X, A=A, R=R, pscore=ps, period=np.full(n, period),
                      n_actions=cfg.n_actions, source=f"sim:{cfg.name}")
        )
    return SimOutput(before=logs[0], after=logs[1], truth=truth or ground_truth(world), world=world)
