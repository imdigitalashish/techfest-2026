"""SYNTHETIC stand-in for components/twin_sim/results/bundle_part.json until the twin lands.

Everything here is labelled synthetic; site coordinates are approximate, hand-placed for layout only.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

SYN = {"kind": "synthetic", "source": "component:dashboard/mock_inputs.py",
       "notes": "SYNTHETIC mock for UI development; not data"}
IST = timezone(timedelta(hours=5, minutes=30))

# (site_id, name, lat, lon, waterbody, outfall_type, boom_capacity_m3) - APPROXIMATE positions, SYNTHETIC
MOCK_SITES = [
    ("MOCK-MAHIM", "Mithi mouth, Mahim (mock)", 19.0436, 72.8395, "Mahim Creek", "river_mouth", 18.0),
    ("MOCK-DHARAVI", "Dharavi nullah outfall (mock)", 19.0570, 72.8580, "Mithi River", "nullah_outfall", 8.0),
    ("MOCK-VERSOVA", "Versova creek (mock)", 19.1405, 72.8125, "Malad Creek", "creek", 12.0),
    ("MOCK-MALAD", "Malad creek, Malvani (mock)", 19.1750, 72.8150, "Malad Creek", "creek", 10.0),
    ("MOCK-MAHUL", "Mahul creek (mock)", 19.0100, 72.8880, "Mahul Creek", "creek", 9.0),
]
WET_DENSITY = 150.0  # same ASSUMPTION as mrv_ledger.reconcile.Params


def _iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def make_bundle_part(now: datetime | None = None, seed: int = 4, past_h: int = 144, ahead_h: int = 48) -> dict:
    rng = random.Random(seed)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    ts = [now - timedelta(hours=past_h - i) for i in range(past_h + ahead_h)]
    storms = [(rng.randrange(len(ts)), rng.uniform(2, 14), rng.uniform(2, 6)) for _ in range(7)]
    rain_city = [sum(a * math.exp(-0.5 * ((i - c) / w) ** 2) for c, a, w in storms) for i in range(len(ts))]
    sites, forcing, inter, fc, tel = [], [], [], [], []
    for k, (sid, name, lat, lon, wb, kind, cap) in enumerate(MOCK_SITES):
        mult = (2.1, 1.7, 1.0, 1.35, 0.6)[k]
        sites.append({"site_id": sid, "name": name, "lat": lat, "lon": lon, "waterbody": wb, "outfall_type": kind,
                      "tidal": True, "channel_width_m": round(cap * 1.6, 1), "boom_length_m": round(cap * 2.2, 1),
                      "boom_capacity_m3": cap,
                      "catchment": {"area_km2": round(rng.uniform(2, 15), 1), "population": rng.randrange(80000, 600000),
                                    "informal_settlement_fraction": round(rng.uniform(0.2, 0.6), 2),
                                    "waste_collection_coverage": round(rng.uniform(0.6, 0.95), 2),
                                    "runoff_coefficient": 0.7, "wards": [], "provenance": {"*": SYN}},
                      "provenance": {"lat": dict(SYN, notes="APPROXIMATE, hand-placed for layout; SYNTHETIC"),
                                     "boom_capacity_m3": SYN}})
        rain = [round(max(0.0, r * rng.uniform(0.6, 1.4) + rng.gauss(0, 0.3)), 2) for r in rain_city]
        hrs = [(t - ts[0]).total_seconds() / 3600 for t in ts]
        tide = [round(1.4 * math.cos(2 * math.pi * h / 12.42 + k * 0.2) + 0.45 * math.cos(2 * math.pi * h / 12.0 + 1.0), 2) for h in hrs]
        forcing.append({"site_id": sid, "t": [_iso(t) for t in ts], "rain_mm_h": rain, "tide_m": tide, "tide_datum": "MSL",
                        "rain_provenance": SYN, "tide_provenance": SYN})
        cols = {c: [] for c in ("arrived_kg", "captured_kg", "escaped_entrainment_kg", "escaped_overtopping_kg",
                                "escaped_bypass_kg", "refloated_kg", "cleared_kg", "stored_kg", "fill_fraction")}
        stored, full = 0.4 * cap * WET_DENSITY, cap * WET_DENSITY
        for i, t in enumerate(ts):
            arrived = cap * mult * (0.35 + 0.2 * rain[i])
            fill = stored / full
            over = arrived * max(0.0, fill - 0.85) * 4 if fill > 0.85 else 0.0
            entr = arrived * min(0.3, 0.02 * rain[i])
            byp = arrived * 0.05
            over = min(over, arrived - entr - byp)
            cap_kg = arrived - entr - byp - over
            refl = stored * 0.01 if tide[i] > 1.5 else 0.0
            local = t.astimezone(IST)
            clear = stored * 0.85 if (local.hour in (9, 10) and t <= now and (local.day + k) % 2 == 0) else 0.0
            stored = max(0.0, stored + cap_kg - refl - clear)
            for c, v in zip(cols, (arrived, cap_kg, entr, over, byp, refl, clear, stored, min(1.0, stored / full))):
                cols[c].append(round(v, 3 if c == "fill_fraction" else 2))
        inter.append({"site_id": sid, "t": [_iso(t) for t in ts], **cols, "provenance": SYN})
        i_now = past_h
        for hz in (24, 48):
            fut = cols["fill_fraction"][i_now:i_now + hz]
            peak = max(fut) if fut else 0
            fc.append({"site_id": sid, "issued_at": _iso(now), "horizon_h": hz,
                       "p_overflow": round(1 / (1 + math.exp(-(peak - 0.6) / 0.07)), 3),
                       "expected_arrival_kg": round(sum(cols["arrived_kg"][i_now:i_now + hz]), 1),
                       "expected_fill_fraction": round(peak, 3),
                       "drivers": {"rain_mm_next_%dh" % hz: round(sum(rain[i_now:i_now + hz]), 1),
                                   "max_tide_m": max(tide[i_now:i_now + hz])}, "provenance": SYN})
        for j in range(24):
            i = i_now - 23 + j
            tel.append({"site_id": sid, "t": _iso(ts[i]), "simulated": True, "battery_v": round(12.4 + 0.3 * math.sin(j / 4), 2),
                        "solar_w": round(max(0.0, 18 * math.sin(math.pi * ((ts[i].astimezone(IST).hour - 6) / 12))), 1),
                        "water_level_m": tide[i], "rain_mm_last_h": rain[i],
                        "fill": {"site_id": sid, "t": _iso(ts[i]), "fill_fraction": cols["fill_fraction"][i],
                                 "method": "simulated", "confidence": 0.8, "provenance": SYN},
                        "health": ["lens_dirty"] if (k == 3 and j > 18) else []})
    order = sorted(fc[::2], key=lambda f: -f["p_overflow"])
    start = now.astimezone(IST).replace(hour=8, minute=0)
    assigns = [{"crew_id": f"CREW-{n + 1}", "site_id": f["site_id"], "start": _iso(start + timedelta(hours=3 * (n // 3))),
                "end": _iso(start + timedelta(hours=3 * (n // 3) + 2)),
                "expected_cleared_kg": round(f["expected_fill_fraction"] * 0.85 * [s for s in MOCK_SITES if s[0] == f["site_id"]][0][6] * WET_DENSITY, 1),
                "reason": f"p_overflow(24h)={f['p_overflow']:.2f}"} for n, f in enumerate(order[:3])]
    plans = [{"plan_id": f"MOCK-{now.astimezone(IST):%Y%m%d}", "issued_at": _iso(now), "policy_id": "mock-greedy-risk",
              "assignments": assigns, "objective": {"expected_cleared_kg": round(sum(a["expected_cleared_kg"] for a in assigns), 1)}}]
    metrics = {"twin_sim": {"data": "SYNTHETIC mock (twin results not yet available)",
                            "reproduce": "python3 innovatex-t3-coastal-plastic/components/dashboard/build_bundle.py --mock"}}
    return {"sites": sites, "forcing": forcing, "interceptor": inter, "forecasts": fc, "plans": plans,
            "telemetry": tel, "metrics": metrics}
