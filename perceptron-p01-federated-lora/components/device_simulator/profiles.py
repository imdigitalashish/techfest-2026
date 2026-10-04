"""C2 Device simulator: heterogeneous device profiles and a seeded availability process.

The schedule depends only on (profiles, rounds, seed, scenario), never on the strategy, so every
strategy sees exactly the same dropouts and the comparison is paired.

Scenario "clean": every device is online every round (heterogeneous data, rank and steps only).
Scenario "dropout": whole-round offline events (p_offline), deadline cut-offs that leave a device
with 25–75 % of its planned steps (p_cutoff), and a forced mid-run outage (outage_rounds).
The budgets below are simulation assumptions, not measurements of real devices.
"""
from __future__ import annotations

import numpy as np

from components.contracts import DeviceProfile

# One dominant domain per device; c0 is data-rich and strong (8x the data of any other device).
DEFAULT_PROFILES: list[DeviceProfile] = [
    DeviceProfile(client_id="c0", device_class="workstation", domain="wiki", n_train_blocks=2400,
                  rank=16, local_steps=16, p_offline=0.0, p_cutoff=0.0),
    DeviceProfile(client_id="c1", device_class="laptop", domain="pycode", n_train_blocks=300,
                  rank=8, local_steps=8, p_offline=0.1, p_cutoff=0.1),
    DeviceProfile(client_id="c2", device_class="phone", domain="cheaders", n_train_blocks=300,
                  rank=4, local_steps=4, p_offline=0.2, p_cutoff=0.3),
    DeviceProfile(client_id="c3", device_class="raspberry-pi", domain="readmes", n_train_blocks=300,
                  rank=2, local_steps=2, p_offline=0.2, p_cutoff=0.3),
    DeviceProfile(client_id="c4", device_class="tablet", domain="manpages", n_train_blocks=300,
                  rank=4, local_steps=4, p_offline=0.2, p_cutoff=0.3, outage_rounds=list(range(4, 9))),
]

WEAK_CLIENTS = ["c2", "c3", "c4"]


def availability_schedule(profiles: list[DeviceProfile], rounds: int, seed: int,
                          scenario: str) -> dict[tuple[int, str], int]:
    """Return allowed_steps[(round, client_id)]: 0 = offline; < planned = cut off by the deadline."""
    if scenario not in ("clean", "dropout"):
        raise ValueError(f"unknown scenario {scenario}")
    rng = np.random.default_rng(10_000 + seed)
    sched: dict[tuple[int, str], int] = {}
    for t in range(rounds):
        for p in DEFAULT_PROFILES:  # draw for every default device so schedules align under exclusions
            u_off, u_cut, u_frac = rng.random(3)
            if p.client_id not in {q.client_id for q in profiles}:
                continue
            planned = p.local_steps
            if scenario == "clean":
                sched[(t, p.client_id)] = planned
            elif t in p.outage_rounds or u_off < p.p_offline:
                sched[(t, p.client_id)] = 0
            elif u_cut < p.p_cutoff:
                sched[(t, p.client_id)] = max(1, int(planned * (0.25 + 0.5 * u_frac)))
            else:
                sched[(t, p.client_id)] = planned
    return sched
