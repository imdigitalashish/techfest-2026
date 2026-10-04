"""Calculation engine: product systems are parameterised stage expressions over cited records.

Every product parameter is a record id in the FactorDB (no free constants), so every result traces back to a
source, locator and quote. Monte Carlo is *paired*: a record shared by several products (e.g. lifetime km) is
sampled once per draw, so comparisons are not inflated by independent noise. Stated source ranges are honoured;
otherwise each record gets a pedigree-derived lognormal.

Honest naming (after the hostile-jury review): `importance` is a normalized squared Spearman rank correlation
(a screening measure, not a variance decomposition); `dq_score` is an elasticity-weighted mean pedigree score
(a screening indicator, not a validated DQR method).
"""
from __future__ import annotations

import ast
import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .db import DATA, FactorDB

SAFE_GLOBALS: dict[str, Any] = {"__builtins__": {}}
PEDIGREE_DIMS = ("reliability", "completeness", "temporal", "geographical", "technological")


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

    def stage_params(self, stage: str) -> list[str]:
        names = {n.id for n in ast.walk(ast.parse(self.stages[stage], mode="eval")) if isinstance(n, ast.Name)}
        return [self.params[n] for n in sorted(names) if n in self.params]


@dataclass
class Scenario:
    id: str
    label: str
    description: str
    products: list[Product]
    case: str = ""
    kind: str = "decision"           # replication | decision | sensitivity
    reference: dict[str, Any] = field(default_factory=dict)


def _resolve(raw: dict[str, dict], sid: str) -> dict:
    s = raw[sid]
    if "base" not in s:
        return s
    base = copy.deepcopy(_resolve(raw, s["base"]))
    out = {**base, **{k: v for k, v in s.items() if k not in ("base", "overrides")}}
    out["products"] = copy.deepcopy(base["products"])
    for p in out["products"]:
        ov = s.get("overrides", {}).get(p["id"], {})
        p["params"].update(ov.get("params", {}))
        p["stages"].update(ov.get("stages", {}))
        for k in ("label", "notes"):
            if k in ov:
                p[k] = ov[k]
    if "reference" not in s:
        out.pop("reference", None)
    return out


def load_scenarios(path: Path | None = None) -> dict[str, Scenario]:
    raw: dict[str, dict] = {}
    files = [path] if path else sorted((DATA / "vehicles").glob("*.yaml"))
    for f in files:
        doc = yaml.safe_load(Path(f).read_text())
        for s in doc["scenarios"]:
            s.setdefault("case", doc.get("case", ""))
            raw[s["id"]] = s
    out: dict[str, Scenario] = {}
    for sid in raw:
        s = _resolve(raw, sid)
        for p in s["products"]:   # drop inherited parameters no stage uses any more (provenance + importance hygiene)
            used = {n.id for e in p["stages"].values() for n in ast.walk(ast.parse(e, mode="eval")) if isinstance(n, ast.Name)}
            p["params"] = {k: v for k, v in p["params"].items() if k in used}
        prods = [Product(**p) for p in s["products"]]
        out[sid] = Scenario(sid, s["label"], s.get("description", ""), prods, s.get("case", ""),
                            s.get("kind", "decision"), s.get("reference", {}))
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


def _ranks(x: np.ndarray) -> np.ndarray:
    from scipy.stats import rankdata
    return rankdata(x).astype(float)          # average ranks for ties; constant input -> zero variance


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = _ranks(np.asarray(x)), _ranks(np.asarray(y))
    rx -= rx.mean()
    ry -= ry.mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def _stats(a: np.ndarray) -> dict[str, float]:
    return {"mean": float(a.mean()), "p05": float(np.percentile(a, 5)), "p50": float(np.percentile(a, 50)),
            "p95": float(np.percentile(a, 95))}


def _importance(samples: dict[str, np.ndarray], target: np.ndarray, ids) -> dict[str, float]:
    r2 = {rid: spearman(samples[rid], target) ** 2 for rid in ids}
    tot = sum(r2.values()) or 1.0
    return {rid: v / tot for rid, v in sorted(r2.items(), key=lambda kv: -kv[1])}


def gas_basis_shares(db: FactorDB, p: Product, stages_c: dict[str, float]) -> dict[str, float]:
    """Share of the central total attributed to each gas-basis family (by the emission-factor records of each stage)."""
    total = sum(stages_c.values()) or 1.0
    shares: dict[str, float] = {}
    for st, v in stages_c.items():
        gwp = {db[rid].gas_family for rid in p.stage_params(st) if rid.startswith("method.gwp") and db[rid].gas_family}
        fams = gwp or {db[rid].gas_family for rid in p.stage_params(st)
                       if db[rid].quantity == "emission_factor" and db[rid].gas_family}
        fam = fams.pop() if len(fams) == 1 else ("mixed" if fams else "none")
        shares[fam] = shares.get(fam, 0.0) + v / total
    return shares


def india_footprint_share(db: FactorDB, p: Product, stages_c: dict[str, float], elast: dict[str, float]) -> float:
    """Share of the central total coming from stages whose DOMINANT emission factor (largest |elasticity| among the
    stage's emission-factor records) is Indian (geography IN*). Small global defaults inside a stage (e.g. IPCC CH4/N2O
    adders on the CEA grid factor) do not flip the stage."""
    total = sum(stages_c.values()) or 1.0
    india = 0.0
    for st, v in stages_c.items():
        efs = [rid for rid in p.stage_params(st) if db[rid].quantity == "emission_factor"]
        if efs and db[max(efs, key=lambda r: abs(elast.get(r, 0.0)))].geography.startswith("IN"):
            india += v
    return india / total


def run_scenario(db: FactorDB, sc: Scenario, n: int = 10000, seed: int = 20261004) -> dict[str, Any]:
    problems = check_scenario(db, sc)
    if problems:
        raise ValueError("; ".join(problems))
    ids = sorted({rid for p in sc.products for rid in p.params.values()})
    cen = {rid: float(db[rid].value) for rid in ids}
    rng = np.random.default_rng(seed)
    smp = {rid: db[rid].sample(n, rng) for rid in ids}
    res: dict[str, Any] = {"scenario": sc.id, "label": sc.label, "description": sc.description, "case": sc.case,
                           "kind": sc.kind, "n_iterations": n, "seed": seed, "unit": "g per vehicle-km (GHG indicator)",
                           "products": {}}
    totals_mc = {}
    families: set[str] = set()
    for p in sc.products:
        stages_c = {k: 1000 * float(v) for k, v in p.evaluate(cen).items()}
        total_c = sum(stages_c.values())
        stages_mc = {k: 1000 * np.asarray(v) * np.ones(n) for k, v in p.evaluate(smp).items()}
        total_mc = sum(stages_mc.values())
        totals_mc[p.id] = total_mc
        elast = {}
        for rid in p.params.values():
            bumped = dict(cen)
            bumped[rid] = cen[rid] * 1.01
            t = 1000 * sum(float(v) for v in p.evaluate(bumped).values())
            elast[rid] = (t - total_c) / total_c / 0.01
        w = {rid: abs(e) for rid, e in elast.items()}
        wsum = sum(w.values()) or 1.0
        dq_dims = {d: sum(w[rid] * getattr(db[rid].pedigree, d) for rid in w) / wsum for d in PEDIGREE_DIMS}
        gshares = gas_basis_shares(db, p, stages_c)
        families |= {f for f, s in gshares.items() if s > 0 and f not in ("none",)}
        res["products"][p.id] = {
            "label": p.label, "powertrain": p.powertrain, "notes": p.notes,
            "stages": stages_c, "total": total_c, "mc_total": _stats(total_mc),
            "mc_stages": {k: _stats(v) for k, v in stages_mc.items()},
            "params": dict(p.params), "elasticity": elast,
            "dq_score": sum(dq_dims.values()) / len(dq_dims), "dq_dims": dq_dims,
            "india_footprint_share": india_footprint_share(db, p, stages_c, elast),
            "gas_basis_shares": gshares,
            "importance": _importance(smp, total_mc, sorted(set(p.params.values()))),
        }
    res["gas_basis_families"] = sorted(families)
    res["harmonized"] = len(families) == 1 and "unspecified" not in families and "mixed" not in families
    ref = sc.products[0]
    res["reference_product"] = ref.id
    res["comparisons"] = {}
    for p in sc.products[1:]:
        a, b = totals_mc[ref.id], totals_mc[p.id]
        red = 1 - b / a
        res["comparisons"][p.id] = {
            "vs": ref.id, "reduction_central": 1 - res["products"][p.id]["total"] / res["products"][ref.id]["total"],
            "reduction_mc": _stats(red), "difference_mc": _stats(a - b), "p_lower": float((b < a).mean()),
            "importance": dict(list(_importance(smp, red, ids).items())[:8]),
        }
    ice = next((p for p in sc.products if p.powertrain == "ICE"), None)
    bev = next((p for p in sc.products if p.powertrain == "BEV"), None)
    if ice and bev:
        a, b = totals_mc[ice.id], totals_mc[bev.id]
        red = 1 - b / a
        res["comparison"] = {
            "ice": ice.id, "bev": bev.id,
            "reduction_central": 1 - res["products"][bev.id]["total"] / res["products"][ice.id]["total"],
            "reduction_mc": _stats(red), "difference_mc": _stats(a - b), "p_bev_lower": float((b < a).mean()),
            "importance": _importance(smp, red, ids),
        }
    return res
