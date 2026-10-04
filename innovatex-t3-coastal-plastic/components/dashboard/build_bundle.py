#!/usr/bin/env python3
"""Merge the twin bundle part, detection results and the C11 evidence records into the dashboard bundle.

Writes site/dashboard_bundle.json (validated by contracts.DashboardBundle), site/aux.json (anchor,
signatures, key registry, synthetic ground truth, detection samples) and site/data.js (same data for
file:// use). Falls back to the SYNTHETIC mock (mock_inputs.py) while the twin's output is absent.

Reproduce: python3 innovatex-t3-coastal-plastic/components/dashboard/build_bundle.py [--mock]
"""
from __future__ import annotations

import argparse
import copy
import dataclasses
import json
import math
import random
import shutil
import statistics
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPONENTS = HERE.parent
for p in (COMPONENTS, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mock_inputs  # noqa: E402
from mrv_ledger import chain  # noqa: E402
from mrv_ledger._contracts import ClearanceRecord, DashboardBundle, InterceptorSeries  # noqa: E402
from mrv_ledger import reconcile as rc  # noqa: E402
from mrv_ledger.synth import _h, twin_clearance_events  # noqa: E402

TWIN = COMPONENTS / "twin_sim" / "results" / "bundle_part.json"
DET = COMPONENTS / "detection" / "results"
MRV_METRICS = COMPONENTS / "mrv_ledger" / "results" / "metrics.json"
REPRODUCE = "python3 innovatex-t3-coastal-plastic/components/dashboard/build_bundle.py"
PART_KEYS = ("sites", "forcing", "interceptor", "forecasts", "plans", "telemetry", "metrics")


def _dt(s) -> datetime:
    return s if isinstance(s, datetime) else datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def flatten(d: dict, prefix: str = "") -> dict[str, float | str]:
    out: dict[str, float | str] = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, key + "."))
        elif isinstance(v, bool):
            out[key] = float(v)
        elif isinstance(v, (int, float)):
            out[key] = float(v) if math.isfinite(v) else str(v)
        elif v is None:
            out[key] = "null"
        else:
            out[key] = v if isinstance(v, str) else json.dumps(v)[:200]
    return out


def replay_window(part: dict) -> tuple[datetime, datetime] | None:
    """The twin's published replay window (metrics['twin_sim.window'] start_utc/end_utc), if any."""
    w = (part.get("metrics") or {}).get("twin_sim.window") or {}
    try:
        return _dt(w["start_utc"]), _dt(w["end_utc"])
    except (KeyError, TypeError, ValueError):
        return None


def _cut_series(part: dict, lo: datetime, hi: datetime) -> None:
    for key in ("forcing", "interceptor"):
        for s in part.get(key, []):
            n = len(s["t"])
            idx = [i for i, t in enumerate(s["t"]) if lo <= _dt(t) <= hi]
            for f, v in list(s.items()):
                if isinstance(v, list) and len(v) == n:
                    s[f] = [v[i] for i in idx]


def trim(part: dict, past_h: int, ahead_h: int = 48, tel_per_site: int = 24, plans_kept: int = 3,
         window: tuple[datetime, datetime] | None = None, now: datetime | None = None) -> dict:
    """Keep a dashboard-sized slice. With `window`, keep every series hour, forecast, plan and telemetry
    reading inside it (the multi-day replay); otherwise keep `past_h` hours around 'now' (default: latest
    forecast issue time, else series end) with only the latest forecasts and plans."""
    if window is not None:
        lo, hi = window
        _cut_series(part, lo, hi)
        part["forecasts"] = [f for f in part.get("forecasts", []) if lo <= _dt(f["issued_at"]) <= hi]
        part["plans"] = sorted((p for p in part.get("plans", []) if lo <= _dt(p["issued_at"]) <= hi),
                               key=lambda p: (_dt(p["issued_at"]), p["policy_id"]))
        part["telemetry"] = sorted((m for m in part.get("telemetry", []) if lo <= _dt(m["t"]) <= hi),
                                   key=lambda m: (m["site_id"], _dt(m["t"])))
        return part
    issued = [_dt(f["issued_at"]) for f in part.get("forecasts", [])]
    ends = [_dt(s["t"][-1]) for s in part.get("forcing", []) if s.get("t")]
    if not issued and not ends:
        return part
    now = now or (max(issued) if issued else max(ends))
    lo, hi = now - timedelta(hours=past_h), now + timedelta(hours=ahead_h)
    _cut_series(part, lo, hi)
    latest: dict = {}
    for f in part.get("forecasts", []):
        k = (f["site_id"], f["horizon_h"])
        if k not in latest or _dt(f["issued_at"]) > _dt(latest[k]["issued_at"]):
            latest[k] = f
    part["forecasts"] = list(latest.values())
    part["plans"] = sorted(part.get("plans", []), key=lambda p: _dt(p["issued_at"]))[-plans_kept:]
    tel = sorted(part.get("telemetry", []), key=lambda m: _dt(m["t"]))
    keep = {}
    for m in tel:
        keep.setdefault(m["site_id"], []).append(m)
    part["telemetry"] = [m for ms in keep.values() for m in ms[-tel_per_site:]]
    return part


def implied_wet_density(series: InterceptorSeries, cap: float) -> float | None:
    vals = [s / (f * cap) for s, f in zip(series.stored_kg, series.fill_fraction) if f > 0.05 and cap > 0]
    return statistics.median(vals) if vals else None


def build_ledger(part: dict, seed: int = 2026, fraud_share: float = 0.2) -> tuple[list, dict]:
    """SYNTHETIC claims on top of the twin's clearance events; ~20% injected inflation / phantom trips."""
    rng = random.Random(seed)
    caps = {s["site_id"]: s["boom_capacity_m3"] for s in part["sites"]}
    events, params = [], {}
    for raw in part.get("interceptor", []):
        s = InterceptorSeries.model_validate(raw)
        cap = caps.get(s.site_id, 0)
        if cap <= 0:
            continue
        rho = implied_wet_density(s, cap)
        # site density from the twin; z_review stays the calibrated value shipped in mrv_ledger/params.json
        params[s.site_id] = rc.DEFAULT if rho is None else dataclasses.replace(rc.DEFAULT, wet_bulk_density_kg_m3=rho)
        events += twin_clearance_events(s, cap)
    events.sort(key=lambda e: e["t_start"])
    entries, truth = [], []
    crews = sorted({a["crew_id"] for p in part.get("plans", []) for a in p["assignments"]}) or ["CREW-1", "CREW-2"]
    for n, ev in enumerate(events):
        p = params[ev["site_id"]]
        kind, factor = "honest", 1.0
        u = rng.random()
        if u < fraud_share * 0.75:
            kind, factor = "inflated", rng.uniform(1.2, 3.0)
        elif u < fraud_share:
            kind = "phantom"
        pre, post = ev["pre"], ev["post"]
        true_kg = ev["true_wet_kg"]
        if kind == "phantom":  # nothing removed: the boom keeps filling with the inflow
            post = min(1.0, pre + max(0.0, ev["inflow_wet_kg"]) / (ev["capacity_m3"] * p.wet_bulk_density_kg_m3))
        claimed = true_kg * math.exp(rng.gauss(0, p.sigma_claim_rel)) * factor
        meas = [min(1.0, max(0.0, f + rng.gauss(0, p.sigma_fill_abs))) for f in (pre, post)]
        rec = ClearanceRecord(site_id=ev["site_id"], crew_id=crews[n % len(crews)], t_start=ev["t_start"], t_end=ev["t_end"],
                              claimed_wet_kg=round(claimed, 1), pre_fill_fraction=round(meas[0], 3),
                              post_fill_fraction=round(meas[1], 3),
                              photo_sha256=[_h(f"synthetic-photo-{n}-{j}") for j in range(2)],
                              gps_track_sha256=_h(f"synthetic-gps-{n}"))
        e = chain.append(entries, rec, rc.reconcile(rec, ev["capacity_m3"], p, inflow_wet_kg=ev["inflow_wet_kg"]))
        truth.append({"seq": e.seq, "kind": kind, "factor": round(factor, 2), "true_wet_kg": round(true_kg, 1)})
    keys = {c: chain.demo_key(c) for c in crews}
    aux = {"anchor": chain.anchor(entries),
           "signatures": [chain.sign_entry(e, e.record.crew_id, keys[e.record.crew_id]) for e in entries],
           "key_registry": {c: chain.public_hex(k) for c, k in keys.items()},
           "delegations": {},  # crew_id -> signer_ids allowed to sign for that crew; none in the demo
           "reconcile_z_review": sorted({q.z_review for q in params.values()}) or [rc.DEFAULT.z_review],
           "reconcile_params_source": str(Path(rc.DEFAULT_SOURCE).relative_to(COMPONENTS.parent.parent))
           if rc.DEFAULT_SOURCE == str(rc.PARAMS_FILE) else rc.DEFAULT_SOURCE,
           "synthetic_truth": truth,
           "density_calibration_kg_m3": {k: round(v.wet_bulk_density_kg_m3, 1) for k, v in params.items()},
           "notes": "Claims are SYNTHETIC (honest, inflated x1.2-3, phantom) on top of twin clearance events. "
                    "Demo signing keys derive from public seeds: DEMO ONLY."}
    return entries, aux


def detection_samples(out_site: Path, max_n: int = 4) -> list[dict]:
    f = DET / "sample_detections.json"
    if not f.exists():
        return []
    data = json.loads(f.read_text())
    frames = data if isinstance(data, list) else data.get("frames", [])
    images = {p.stem: p for p in DET.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")}
    out, dest = [], out_site / "assets" / "detection"
    for fr in frames:
        stem = Path(str(fr.get("frame_id", ""))).stem
        img = images.get(stem) or next((p for s, p in images.items() if stem and stem in s), None)
        if img is None or img.stat().st_size > 400_000:
            continue
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img, dest / img.name)
        out.append({**fr, "image": f"assets/detection/{img.name}"})
        if len(out) >= max_n:
            break
    return out


def detection_metrics_file() -> Path | None:
    """metrics.json per the brief; until it exists, the newest other results JSON (e.g. a zero-shot eval)."""
    if (DET / "metrics.json").exists():
        return DET / "metrics.json"
    cands = sorted((p for p in DET.glob("*.json") if p.name != "sample_detections.json"), key=lambda p: p.stat().st_mtime)
    return cands[-1] if cands else None


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=HERE,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def build(mock: bool = False, out_site: Path = HERE / "site", past_h: int = 144, now: datetime | None = None,
          ledger_days: int = 30) -> dict:
    use_twin = TWIN.exists() and not mock
    raw = json.loads(TWIN.read_text()) if use_twin else mock_inputs.make_bundle_part(now=now)
    raw = {k: raw.get(k, []) if k != "metrics" else raw.get(k, {}) for k in PART_KEYS}
    win = replay_window(raw)
    # ledger: the `ledger_days` before the end of the replay window (else before the latest forecast)
    entries, aux = build_ledger(trim(copy.deepcopy(raw), ledger_days * 24, ahead_h=0, now=win[1] if win else None))
    part = trim(raw, past_h, window=win)
    assert chain.verify(entries, aux["anchor"]).ok
    assert chain.verify_signatures(entries, aux["signatures"], aux["key_registry"], aux["delegations"]).ok
    metrics = {k: flatten(v) for k, v in (part.get("metrics") or {}).items()}
    det = detection_metrics_file()
    if det is not None:
        metrics["detection"] = {"source_file": f"components/detection/results/{det.name}",
                                **flatten(json.loads(det.read_text()))}
    if MRV_METRICS.exists():
        metrics["mrv_ledger"] = flatten(json.loads(MRV_METRICS.read_text()))
    disclaimers = [
        "Values marked SIMULATED come from the digital twin, not from field hardware.",
        "Clearance claims in the evidence-records table are SYNTHETIC (honest + injected inflation/phantom trips).",
        "Reconciliation densities and moisture are ASSUMPTIONS until calibrated against weighed samples.",
    ]
    if not use_twin:
        disclaimers.insert(0, "SYNTHETIC MOCK: twin results not yet available; every series, site position and plan "
                              "on this page is synthetic test data.")
    bundle = DashboardBundle.model_validate({
        "generated_at": datetime.now(timezone.utc), "git_sha": git_sha(), **{k: part[k] for k in PART_KEYS if k != "metrics"},
        "ledger": [e.model_dump(mode="json") for e in entries], "metrics": metrics, "disclaimers": disclaimers})
    aux["inputs"] = {"twin": "components/twin_sim/results/bundle_part.json" if use_twin else "SYNTHETIC mock (mock_inputs.py)",
                     "detection": None if det is None else f"components/detection/results/{det.name}",
                     "reproduce": REPRODUCE + ("" if use_twin else " --mock")}
    aux["detection_samples"] = detection_samples(out_site)
    out_site.mkdir(parents=True, exist_ok=True)
    js = bundle.model_dump_json()
    (out_site / "dashboard_bundle.json").write_text(js)
    (out_site / "aux.json").write_text(json.dumps(aux))
    (out_site / "data.js").write_text(f"window.DASHBOARD_BUNDLE={js};\nwindow.DASHBOARD_AUX={json.dumps(aux)};\n")
    return {"bundle": bundle, "aux": aux, "twin": use_twin}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mock", action="store_true", help="ignore twin output and use the SYNTHETIC mock")
    ap.add_argument("--past-h", type=int, default=144, help="hours of history to keep (default 144)")
    a = ap.parse_args()
    r = build(mock=a.mock, past_h=a.past_h)
    b = r["bundle"]
    flags = [e.reconciliation.flag for e in b.ledger]
    print(f"twin={'yes' if r['twin'] else 'MOCK'} sites={len(b.sites)} ledger={len(b.ledger)} "
          f"flags={ {f: flags.count(f) for f in ('ok', 'review', 'reject')} } metrics={sorted(b.metrics)} "
          f"head={r['aux']['anchor']['head_hash'][:12]}")
