"""C4 Grid-factor service (spike B) — baseline.

Returns a cited electricity emission factor for (region, period, method, delivery). Baseline logic: India runs one
integrated national grid (CEA v22 User Guide: all regional grids integrated in Dec 2013), so the generation mix is
national; the state-specific part is the T&D loss between busbar and the consumer meter.
    EF_meter(state) = EF_generation(national, method) / (1 - T&D_loss(state))
State-resolved generation mixes, lifetime averages and prospective factors are the spike's next steps.
"""
from __future__ import annotations

import sys
from pathlib import Path

from .db import FactorDB

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "architecture" / "contracts"))
from contracts import GridFactor, GridFactorQuery  # noqa: E402

METHOD_RECORD = {
    "average": "energy.electricity.in.grid_wavg_generation.{fy}",
    "operating_margin": "energy.electricity.in.grid_om.{fy}",
    "build_margin": "energy.electricity.in.grid_bm.{fy}",
}
NATIONAL_TD = "energy.electricity.in.td_loss_share.fy2023_24"


def _fy_key(period: str) -> str:
    return "fy" + period.replace("-", "_")


def td_record_id(region: str) -> str:
    if region == "IN":
        return NATIONAL_TD
    return f"energy.electricity.in_{region.removeprefix('IN-')}.td_loss_share.fy2023_24"


def states(db: FactorDB) -> list[str]:
    return sorted(r.geography for r in db.records.values()
                  if r.id.endswith(".td_loss_share.fy2023_24") and r.geography.startswith("IN-"))


def grid_factor(db: FactorDB, q: GridFactorQuery) -> GridFactor:
    if q.method not in METHOD_RECORD:
        raise NotImplementedError(f"method {q.method} not in the baseline service yet")
    if q.gas_basis != "CO2":
        raise NotImplementedError("CO2e (upstream + non-CO2) needs coal-upstream records — data gap")
    ef_id = METHOD_RECORD[q.method].format(fy=_fy_key(q.period))
    if ef_id not in db.records:
        raise KeyError(f"no CEA record for period {q.period}: {ef_id}")
    ef = float(db[ef_id].value)
    if q.delivery == "busbar":
        return GridFactor(value=ef, query=q, record_ids=[ef_id], derivation=f"{ef_id} (busbar, CO2 only)")
    td_id = td_record_id(q.region)
    if td_id not in db.records:
        raise KeyError(f"no T&D record for region {q.region}: {td_id}")
    td = float(db[td_id].value)
    return GridFactor(value=ef / (1 - td), query=q, record_ids=[ef_id, td_id],
                      derivation=f"{ef_id} / (1 - {td_id}) = {ef} / (1 - {td}) = {ef / (1 - td):.4f}")
