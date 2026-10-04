"""SYNTHETIC clearance trips for evaluating reconciliation (no field data exists yet).

Kinds: honest; inflated (claim x U(1.2, 3)); phantom (no clearance happened, typical claim filed);
wetted (load soaked or silted: weighbridge slip and claim x U(1.3, 2), volume unchanged).
Honest trips can also come from the digital twin's InterceptorSeries clearance events.
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ._contracts import ClearanceRecord, InterceptorSeries
from .reconcile import DEFAULT, Params

KINDS = ("honest", "inflated", "phantom", "wetted")


@dataclass
class Trip:
    record: ClearanceRecord
    capacity_m3: float
    kind: str
    factor: float
    true_wet_kg: float


def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def synthetic_sites(n: int = 6, seed: int = 7) -> list[tuple[str, float]]:
    rng = random.Random(seed)
    return [(f"SYN-{i + 1:02d}", round(rng.uniform(4.0, 20.0), 1)) for i in range(n)]


def _measure(rng: random.Random, f: float, p: Params) -> float:
    return min(1.0, max(0.0, f + rng.gauss(0.0, p.sigma_fill_abs)))


def make_trip(rng: random.Random, i: int, kind: str, site: tuple[str, float], t0: datetime, p: Params = DEFAULT,
              density_bias: float = 1.0, wb_share: float = 0.4) -> Trip:
    site_id, cap = site
    rho = p.wet_bulk_density_kg_m3 * density_bias * math.exp(rng.gauss(0.0, p.sigma_density_rel))
    if kind == "phantom":
        pre = post = rng.uniform(0.2, 0.9)
        true_wet = 0.0
        claimed = rng.uniform(0.25, 0.9) * cap * p.wet_bulk_density_kg_m3 * math.exp(rng.gauss(0, p.sigma_claim_rel))
    else:
        pre = rng.uniform(0.1, 0.95)
        post = rng.uniform(0.0, min(0.15, pre * 0.5))
        true_wet = (pre - post) * cap * rho
        claimed = true_wet * math.exp(rng.gauss(0.0, p.sigma_claim_rel))
    factor = 1.0
    weighbridge = None
    has_wb = rng.random() < wb_share
    if kind == "honest" and has_wb:
        weighbridge = claimed = true_wet * math.exp(rng.gauss(0.0, 0.02))
    elif kind == "inflated":
        factor = rng.uniform(1.2, 3.0)
        claimed *= factor
        weighbridge = claimed if has_wb else None      # forged slip or none
    elif kind == "wetted":
        factor = rng.uniform(1.3, 2.0)
        weighbridge = claimed = true_wet * factor       # genuine slip of a soaked/silted load
    elif kind == "phantom" and has_wb:
        weighbridge = claimed
    start = t0 + timedelta(minutes=47 * i)
    rec = ClearanceRecord(
        site_id=site_id, crew_id=f"SYN-crew-{i % 5 + 1}", t_start=start,
        t_end=start + timedelta(minutes=rng.choice([60, 90, 120, 180])),
        claimed_wet_kg=round(claimed, 2), weighbridge_wet_kg=None if weighbridge is None else round(weighbridge, 2),
        pre_fill_fraction=round(_measure(rng, pre, p), 3), post_fill_fraction=round(_measure(rng, post, p), 3),
        photo_sha256=[_h(f"synthetic-photo-{i}-{j}") for j in range(2)], gps_track_sha256=_h(f"synthetic-gps-{i}"),
    )
    return Trip(rec, cap, kind, factor, true_wet)


def make_trips(counts: dict[str, int], seed: int, sites: list[tuple[str, float]] | None = None, p: Params = DEFAULT,
               density_bias: float = 1.0, t0: datetime | None = None) -> list[Trip]:
    rng = random.Random(seed)
    sites = sites or synthetic_sites()
    t0 = t0 or datetime(2026, 9, 1, tzinfo=timezone.utc)
    kinds = [k for k in KINDS for _ in range(counts.get(k, 0))]
    rng.shuffle(kinds)
    return [make_trip(rng, i, k, rng.choice(sites), t0, p, density_bias) for i, k in enumerate(kinds)]


def twin_clearance_events(series: InterceptorSeries, capacity_m3: float) -> list[dict]:
    """Contiguous hours with cleared_kg > 0 -> one trip: true wet kg and true fill before/after."""
    events, i, n = [], 0, len(series.t)
    while i < n:
        if series.cleared_kg[i] > 0:
            j = i
            while j + 1 < n and series.cleared_kg[j + 1] > 0:
                j += 1
            pre = series.fill_fraction[i - 1] if i > 0 else series.fill_fraction[i]
            events.append({"site_id": series.site_id, "t_start": series.t[i], "t_end": series.t[j] + timedelta(hours=1),
                           "true_wet_kg": sum(series.cleared_kg[i:j + 1]), "pre": pre, "post": series.fill_fraction[j],
                           "capacity_m3": capacity_m3})
            i = j + 1
        else:
            i += 1
    return events
