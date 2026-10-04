"""C1 — PettingZoo ParallelEnv wrapper around DispatchCore (the public multi-agent API).

Each resource unit is an agent "unit_i". Action = Discrete(Z): the zone to head to (ignored unless
the unit is IDLE; choosing the current zone = stay). Observation = own zone one-hot, own status
one-hot, own eta, then city-wide queue / idle / last-arrival vectors and time-of-day (sin, cos).
Reward = shared team reward / K (cooperative). The evaluation harness drives DispatchCore directly
for speed; tests/test_simulator.py checks that both paths produce identical trajectories.
"""
from __future__ import annotations

import functools

import numpy as np
from gymnasium import spaces
from pettingzoo import ParallelEnv

from components.scenarios.scenarios import SCENARIOS, ScenarioConfig, build_trace
from components.simulator.core import DispatchCore


class DispatchParallelEnv(ParallelEnv):
    metadata = {"name": "p7_dispatch_v0", "render_modes": []}

    def __init__(self, scenario: str | ScenarioConfig = "shock+drift", n_agents: int = 40,
                 patience: int = 10, horizon: int | None = None):
        cfg = SCENARIOS[scenario] if isinstance(scenario, str) else scenario
        if horizon is not None:
            from dataclasses import replace
            cfg = replace(cfg, horizon=horizon)
        self.cfg, self.n_units, self.patience = cfg, n_agents, patience
        self.Z = cfg.grid ** 2
        self.possible_agents = [f"unit_{i}" for i in range(n_agents)]
        self.agents: list[str] = []
        self.core: DispatchCore | None = None
        self._obs_dim = self.Z + 3 + 1 + 3 * self.Z + 2

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return spaces.Box(low=0.0, high=np.inf, shape=(self._obs_dim,), dtype=np.float32)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return spaces.Discrete(self.Z)

    def _obs(self):
        st = self.core.state()
        tod = 2 * np.pi * (st.t % self.cfg.day) / self.cfg.day
        shared = np.concatenate([st.queue_len, st.idle_count, st.last_arrivals, [np.sin(tod) + 1, np.cos(tod) + 1]])
        out = {}
        for i, a in enumerate(self.agents):
            own = np.zeros(self.Z + 4, dtype=np.float32)
            own[st.agent_zone[i]] = 1.0
            own[self.Z + st.agent_status[i]] = 1.0
            own[self.Z + 3] = st.agent_eta[i]
            out[a] = np.concatenate([own, shared]).astype(np.float32)
        return out

    def reset(self, seed=None, options=None):
        seed = 0 if seed is None else int(seed)
        trace = build_trace(self.cfg, seed)
        self.core = DispatchCore(trace, n_agents=self.n_units, patience=self.patience, init_seed=seed)
        self.agents = self.possible_agents[:]
        return self._obs(), {a: {} for a in self.agents}

    def step(self, actions):
        targets = self.core.zone.copy()
        for i, a in enumerate(self.possible_agents):
            if a in actions:
                targets[i] = int(actions[a])
        info = self.core.step(targets)
        r = info.reward / self.n_units
        done = self.core.done
        obs = self._obs()
        rewards = {a: r for a in self.agents}
        terms = {a: False for a in self.agents}
        truncs = {a: done for a in self.agents}
        infos = {a: {"served": int(info.served.sum()), "lost": int(info.lost.sum())} for a in self.agents}
        if done:
            self.agents = []
        return obs, rewards, terms, truncs, infos
