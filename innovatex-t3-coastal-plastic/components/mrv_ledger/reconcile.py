"""Independent reconciliation of a clearance claim against a volume-based sensor estimate (C11).

Basis: dry-equivalent kg. Paying on wet kg rewards soaked or silted loads, so the sensor side never uses
a weight: removed volume = fill-fraction drop x boom capacity (m3), converted with a nominal wet bulk
density and moisture fraction. The claim is converted with the same nominal moisture, so a load made
heavier with water or silt shows up as excess mass for the volume actually removed from the boom.

Score: z = (claimed - sensor) / sigma_honest, where sigma_honest is the spread expected from honest
records given fill-sensor noise, per-trip bulk-density variation and honest reporting noise.
A fixed ratio threshold (the naive baseline) ignores that small clearances have large relative error.
"""
from __future__ import annotations

import json
import math
import warnings
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Optional

from ._contracts import ClearanceRecord, Reconciliation


@dataclass(frozen=True)
class Params:
    # Every value is an ASSUMPTION (no opened source yet gave a measured figure for Mumbai boom catch);
    # evaluate.py reports sensitivity to them. Replace with field calibration (weigh + volume samples).
    wet_bulk_density_kg_m3: float = 150.0   # ASSUMPTION: loose, wet floating litter + organics
    moisture_fraction: float = 0.40         # ASSUMPTION: water share of wet mass
    sigma_fill_abs: float = 0.03            # ASSUMPTION: 1-sigma error of one fill-fraction reading
    sigma_density_rel: float = 0.25         # ASSUMPTION: trip-to-trip bulk-density variation
    sigma_claim_rel: float = 0.10           # ASSUMPTION: honest reporting / scale noise
    z_review: float = 1.645                 # N(0,1) one-sided 5% PRIOR only; DEFAULT ships the calibrated params.json value
    z_reject: float = 2.326                 # one-sided 1% under N(0,1); ASSUMPTION, not calibrated
    max_wet_density_kg_m3: float = 450.0    # ASSUMPTION: above this a load is mostly water/silt

    @property
    def dry_density_kg_m3(self) -> float:
        return self.wet_bulk_density_kg_m3 * (1.0 - self.moisture_fraction)

    def __post_init__(self):
        if self.z_review > self.z_reject:
            raise ValueError(f"z_review {self.z_review} > z_reject {self.z_reject}: the review band would be empty")

    def as_dict(self) -> dict:
        return asdict(self)


# The shipped review threshold is a versioned parameter: evaluate.py calibrates it on SYNTHETIC honest trips
# (seed, sample size and code commit recorded in params.json) and every default reconcile() call uses it.
PARAMS_FILE = Path(__file__).resolve().parent / "params.json"


def load_default(path: Path = PARAMS_FILE) -> tuple[Params, str]:
    if not path.exists():
        warnings.warn(f"{path.name} missing: reconcile() falls back to the UNCALIBRATED N(0,1) prior; "
                      "run `python3 -m mrv_ledger.evaluate`", RuntimeWarning, stacklevel=2)
        return Params(), "uncalibrated-prior"
    d = json.loads(path.read_text())
    p = replace(Params(), z_review=float(d["z_review"]))
    rest = {k: v for k, v in p.as_dict().items() if k != "z_review"}
    if d.get("calibration", {}).get("model_params") != rest:
        warnings.warn(f"{path.name} was calibrated with other model parameters; rerun mrv_ledger.evaluate",
                      RuntimeWarning, stacklevel=2)
    return p, str(path)


DEFAULT, DEFAULT_SOURCE = load_default()


def reload_default() -> Params:
    """Re-read params.json (evaluate.py calls this after re-calibrating in the same process)."""
    global DEFAULT, DEFAULT_SOURCE
    DEFAULT, DEFAULT_SOURCE = load_default()
    return DEFAULT


def sensor_dry_kg(pre_fill: float, post_fill: float, boom_capacity_m3: float, p: Optional[Params] = None) -> float:
    p = DEFAULT if p is None else p
    return max(0.0, pre_fill - post_fill) * boom_capacity_m3 * p.dry_density_kg_m3


def z_score(claimed_dry: float, sensor_dry: float, boom_capacity_m3: float, p: Optional[Params] = None) -> float:
    p = DEFAULT if p is None else p
    fill_term = boom_capacity_m3 * p.dry_density_kg_m3 * p.sigma_fill_abs * math.sqrt(2.0)
    s = max(sensor_dry, 0.0)
    sigma = math.sqrt(fill_term**2 + (s * p.sigma_density_rel) ** 2 + (s * p.sigma_claim_rel) ** 2)
    return (claimed_dry - s) / max(sigma, 1e-9)


def reconcile(record: ClearanceRecord, boom_capacity_m3: float, p: Optional[Params] = None,
              twin_cleared_wet_kg: Optional[float] = None, inflow_wet_kg: Optional[float] = None) -> Reconciliation:
    """p=None uses the shipped DEFAULT (calibrated z_review from params.json), looked up at call time.
    inflow_wet_kg: plastic that reached the boom during the clearance window (C6 flux counter, or the
    twin's captured - refloated). Removed mass = fill drop + inflow, so without it long clearances look inflated."""
    p = DEFAULT if p is None else p
    claimed_dry = record.claimed_wet_kg * (1.0 - p.moisture_fraction)
    reasons = ["basis=dry-equivalent kg (volume x ASSUMPTION density/moisture)"]
    if record.pre_fill_fraction is not None and record.post_fill_fraction is not None:
        drop = record.pre_fill_fraction - record.post_fill_fraction
        sensor = sensor_dry_kg(record.pre_fill_fraction, record.post_fill_fraction, boom_capacity_m3, p)
        reasons.append(f"fill {record.pre_fill_fraction:.2f}->{record.post_fill_fraction:.2f}, "
                       f"volume removed {max(drop, 0) * boom_capacity_m3:.2f} m3")
        if drop < 2 * math.sqrt(2) * p.sigma_fill_abs:
            reasons.append("no detectable fill drop at the boom")
        if inflow_wet_kg:  # removed = fill change + inflow; clip only the total (a rising fill cancels inflow)
            sensor = max(0.0, drop * boom_capacity_m3 * p.dry_density_kg_m3 + max(0.0, inflow_wet_kg) * (1.0 - p.moisture_fraction))
            reasons.append(f"+ inflow during clearance {max(0.0, inflow_wet_kg):.0f} wet kg (flux counter / twin)")
    elif twin_cleared_wet_kg is not None:
        sensor = twin_cleared_wet_kg * (1.0 - p.moisture_fraction)
        reasons.append("sensor side = digital-twin cleared_kg (SIMULATED)")
    else:
        return Reconciliation(sensor_estimated_kg=0.0, claimed_kg=round(claimed_dry, 3), ratio=round(claimed_dry, 3),
                              flag="review", reasons=reasons + ["no fill readings: cannot reconcile"])

    z = z_score(claimed_dry, sensor, boom_capacity_m3, p)
    ratio = claimed_dry / max(sensor, 1.0)
    flag = "reject" if z > p.z_reject else "review" if z > p.z_review else "ok"
    reasons.append(f"z={z:.2f} (review>{p.z_review:.3f}, reject>{p.z_reject:.3f})")
    if z < -p.z_reject:
        reasons.append("claim far below sensor estimate: check sensor or unreported removal")
    if record.weighbridge_wet_kg is not None:
        if record.claimed_wet_kg > 1.02 * record.weighbridge_wet_kg:
            flag = "reject"
            reasons.append("claim exceeds weighbridge slip")
        drop = (record.pre_fill_fraction or 0) - (record.post_fill_fraction or 0)
        drop_m3 = max(drop, 0) * boom_capacity_m3
        # only trust an implied density when the volume drop is well above fill-sensor noise
        if drop > 3 * math.sqrt(2) * p.sigma_fill_abs and record.weighbridge_wet_kg / drop_m3 > p.max_wet_density_kg_m3:
            reasons.append(f"implied wet density {record.weighbridge_wet_kg / drop_m3:.0f} kg/m3: water or silt suspected")
            flag = "review" if flag == "ok" else flag
    if not record.photo_sha256:
        reasons.append("no photo evidence hashes")
        flag = "review" if flag == "ok" else flag
    if record.gps_track_sha256 is None:
        reasons.append("no GPS track hash")
    reasons.append(f"payable_dry_kg={min(claimed_dry, sensor):.1f}")
    return Reconciliation(sensor_estimated_kg=round(sensor, 3), claimed_kg=round(claimed_dry, 3),
                          ratio=round(ratio, 4), flag=flag, reasons=reasons)
