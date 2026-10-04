"""Calculation engine: product systems are parameterised stage expressions over cited records.

Every product parameter is a record id in the FactorDB (no free constants), so every result traces back to a
source, locator and quote. Monte Carlo is *paired*: a record shared by two products (e.g. lifetime km) is
sampled once per iteration, so comparisons are not inflated by independent noise.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .db import DATA, FactorDB

SAFE_GLOBALS: dict[str, Any] = {"__builtins__": {}}


@dataclass
class Product:
    id: str
    label: str
    powertrain: str
    params: dict[str, str]          # local name -> record id
    stages: dict[str, str]          # stage -> expression giving kg CO2e per vehicle-km
    notes: str = ""

    def evaluate(self, values: dict[str, Any]) -> dict[str, Any]:
        local = {name: values[rid] for name, rid in self.params.items()}
        return {stage: eval(expr, SAFE_GLOBALS, dict(local)) for stage, expr in self.stages.items()}  # noqa: S307


@dataclass
class Scenario:
    id: str
    label: str
    description: str
    products: list[Product]
    reference: dict[str, Any] = field(default_factory=dict)


def load_scenarios(path: Path | None = None) -> dict[str, Scenario]:
    out: dict[str, Scenario] = {}
    files = [path] if path else sorted((DATA / "vehicles").glob("*.yaml"))
    for f in files:
        doc = yaml.safe_load(Path(f).read_text())
        for s in doc["scenarios"]:
            prods = [Product(**p) for p in s["products"]]
            out[s["id"]] = Scenario(s["id"], s["label"], s.get("description", ""), prods, s.get("reference", {}))
    return out


def check_scenario(db: FactorDB, sc: Scenario) -> list[str]:
    """Contract check: every parameter resolves to a scalar record; returns a list of problems."""
    problems = []
    for p in sc.products:
        for name, rid in p.params.items():
            if rid not in db.records:
                problems.append(f"{sc.id}/{p.id}: param {name} -> unknown record {rid}")
            elif not db[rid].is_scalar:
                problems.append(f"{sc.id}/{p.id}: param {name} -> record {rid} is not scalar")
    return problems


def central_values(db: FactorDB, ids: set[str]) -> dict[str, float]:
    return {rid: float(db[rid].value) for rid in ids}


def sample_values(db: FactorDB, ids: set[str], n: int, rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Lognormal around the published value (as median); sigma from the stated 95% range or the pedigree."""
    out = {}
    for rid in sorted(ids):
        rec = db[rid]
        out[rid] = float(rec.value) * np.exp(rng.normal(0.0, rec.log_sigma(), n))
    return out


def _ranks(x: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(x)).astype(float)


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = _ranks(x), _ranks(y)
    rx -= rx.mean()
    ry -= ry.mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def _stats(a: np.ndarray) -> dict[str, float]:
    return {"mean": float(a.mean()), "p05": float(np.percentile(a, 5)), "p50": float(np.percentile(a, 50)),
            "p95": float(np.percentile(a, 95))}


def run_scenario(db: FactorDB, sc: Scenario, n: int = 10000, seed: int = 20261004) -> dict[str, Any]:
    problems = check_scenario(db, sc)
    if problems:
        raise ValueError("; ".join(problems))
    ids = {rid for p in sc.products for rid in p.params.values()}
    cen = central_values(db, ids)
    rng = np.random.default_rng(seed)
    smp = sample_values(db, ids, n, rng)
    res: dict[str, Any] = {"scenario": sc.id, "label": sc.label, "description": sc.description,
                           "n_iterations": n, "seed": seed, "unit": "g CO2e per vehicle-km", "products": {}}
    totals_mc = {}
    for p in sc.products:
        stages_c = {k: 1000 * float(v) for k, v in p.evaluate(cen).items()}
        total_c = sum(stages_c.values())
        stages_mc = {k: 1000 * np.asarray(v) * np.ones(n) for k, v in p.evaluate(smp).items()}
        total_mc = sum(stages_mc.values())
        totals_mc[p.id] = total_mc
        # elasticity of the total to each parameter (+1% perturbation), used for the data-quality index
        elast = {}
        for name, rid in p.params.items():
            bumped = dict(cen)
            bumped[rid] = cen[rid] * 1.01
            t = 1000 * sum(float(v) for v in p.evaluate(bumped).values())
            elast[rid] = (t - total_c) / total_c / 0.01
        w = {rid: abs(e) for rid, e in elast.items()}
        wsum = sum(w.values()) or 1.0
        dqi = sum(w[rid] * db[rid].pedigree.mean_score() for rid in w) / wsum
        india_share = sum(w[rid] for rid in w if db[rid].pedigree.geographical == 1) / wsum
        rho = {rid: spearman(smp[rid], total_mc) for rid in p.params.values()}
        r2 = {rid: r ** 2 for rid, r in rho.items()}
        r2sum = sum(r2.values()) or 1.0
        res["products"][p.id] = {
            "label": p.label, "powertrain": p.powertrain, "notes": p.notes,
            "stages": stages_c, "total": total_c, "mc_total": _stats(total_mc),
            "mc_stages": {k: _stats(v) for k, v in stages_mc.items()},
            "params": {name: rid for name, rid in p.params.items()},
            "elasticity": elast, "dqi": dqi, "india_weighted_share": india_share,
            "variance_share": {rid: v / r2sum for rid, v in sorted(r2.items(), key=lambda kv: -kv[1])},
        }
    # pairwise comparison: first ICE vs first BEV in the scenario
    ice = next((p for p in sc.products if p.powertrain == "ICE"), None)
    bev = next((p for p in sc.products if p.powertrain == "BEV"), None)
    if ice and bev:
        a, b = totals_mc[ice.id], totals_mc[bev.id]
        red = 1 - b / a
        diff = a - b
        rho = {rid: spearman(smp[rid], red) for rid in ids}
        r2 = {rid: r ** 2 for rid, r in rho.items()}
        r2sum = sum(r2.values()) or 1.0
        ci, cb = res["products"][ice.id]["total"], res["products"][bev.id]["total"]
        res["comparison"] = {
            "ice": ice.id, "bev": bev.id, "reduction_central": 1 - cb / ci,
            "reduction_mc": _stats(red), "difference_mc_g_per_km": _stats(diff),
            "p_bev_lower": float((b < a).mean()),
            "variance_share_of_reduction": {rid: v / r2sum for rid, v in sorted(r2.items(), key=lambda kv: -kv[1])},
            "spearman_with_reduction": rho,
        }
    return res
