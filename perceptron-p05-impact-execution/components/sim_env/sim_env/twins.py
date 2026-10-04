"""Paired counterfactual runs: the treatment and its null twin on the same seed."""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from .world import TICKER, WorldResult, ns_at, run_world


def make_factory(policy, side: str, quantity: int, start: str, end: str, n_slots: int):
    from execution_agent.abides_agent import ExecutionAgent

    def factory(agent_id, rs):
        return ExecutionAgent(agent_id, rs, policy, TICKER, side, quantity,
                              ns_at(start), ns_at(end), n_slots)
    return factory


def run_null(seed: int, side: str, start: str, end: str, n_slots: int, end_time: str,
             rng_sync: str = "naive") -> WorldResult:
    from execution_agent.policies import TwapPolicy
    return run_world(seed, make_factory(TwapPolicy(), side, 0, start, end, n_slots), end_time=end_time,
                     rng_sync=rng_sync)


def run_treatment(seed: int, policy, side: str, quantity: int, start: str, end: str, n_slots: int,
                  end_time: str, rng_sync: str = "naive") -> WorldResult:
    return run_world(seed, make_factory(policy, side, quantity, start, end, n_slots), end_time=end_time,
                     rng_sync=rng_sync)
