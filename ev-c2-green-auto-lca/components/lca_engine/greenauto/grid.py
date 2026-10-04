"""C4 Grid-factor service (spike B) — baseline.

Returns a cited electricity emission factor for (region, period, method, delivery). Baseline logic: India runs one
integrated national grid (CEA v22 User Guide: all regional grids integrated in Dec 2013), so the generation mix is
national; the state-specific part is the T&D loss between busbar and the consumer meter.
    EF_meter(state) = EF_generation(national, method) / (1 - T&D_loss(state))
gas_basis="CO2e" adds combustion CH4/N2O (IPCC 2006 Tier 1) and coal-mine methane (India BUR-4) at AR6 GWP100 —
a PARTIAL life-cycle factor (no mining energy, coal transport, gas supply chain or infrastructure).
Output is a "national generation factor with state loss adjustment", not a state generation mix. State-resolved mixes,
lifetime averages and prospective factors are the spike's next steps.
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
# CO2e adders (same records and formula as the CO2e scenarios in data/vehicles/*.yaml)
CO2E_RECORDS = {
    "ch4c": "energy.upstream.stationary_combustion.coal.ch4.ipcc2006.energy_industries",
    "n2oc": "energy.upstream.stationary_combustion.coal.n2o.ipcc2006.energy_industries",
    "co2c": "fuels.coal.in.co2_per_energy_ncv.cea_v22",
    "hr": "energy.upstream.coal_power.net_heat_rate.coal.cea_v22_default",
    "gcv": "energy.upstream.coal_power.gcv.coal.cea_v22_default",
    "cmm": "energy.upstream.coal_mining.ch4_weighted.in.bur4_2020",
    "dens": "energy.upstream.coal_mining.ch4_density.ipcc2006",
    "gwp_ch4": "method.gwp100.ch4_fossil.ipcc_ar6",
    "gwp_n2o": "method.gwp100.n2o.ipcc_ar6",
}
COAL_SHARE = {"average": "energy.electricity.in.coal_lignite_share_net_generation.fy2025_26",
              "operating_margin": "energy.electricity.in.coal_lignite_share_fossil_generation.fy2025_26"}


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
    ef_id = METHOD_RECORD[q.method].format(fy=_fy_key(q.period))
    if ef_id not in db.records:
        raise KeyError(f"no CEA record for period {q.period}: {ef_id}")
    ef = float(db[ef_id].value)
    extra_ids: list[str] = []
    if q.gas_basis == "CO2e":
        if q.method == "build_margin":
            raise NotImplementedError("CO2e build margin needs the BM fuel mix (incl. RE) — data gap")
        recs = dict(CO2E_RECORDS)
        if q.gwp == "AR5":
            recs.update(gwp_ch4="method.gwp100.ch4_fossil.no_ccfb.ipcc_ar5", gwp_n2o="method.gwp100.n2o.no_ccfb.ipcc_ar5")
        v = {k: float(db[r].value) for k, r in recs.items()}
        share = float(db[COAL_SHARE[q.method]].value)
        nonco2 = (v["ch4c"] * v["gwp_ch4"] + v["n2oc"] * v["gwp_n2o"]) / (v["co2c"] * 1000)
        cmm = share * v["hr"] / v["gcv"] * v["cmm"] / 1000 * v["dens"] * v["gwp_ch4"]
        ef = ef * (1 + nonco2) + cmm
        extra_ids = list(recs.values()) + [COAL_SHARE[q.method]]
    basis = f"CO2e {q.gwp} GWP100, partial upstream" if q.gas_basis == "CO2e" else "CO2 only"
    if q.delivery == "busbar":
        return GridFactor(value=ef, unit=f"kg {q.gas_basis}/kWh", query=q, record_ids=[ef_id] + extra_ids,
                          derivation=f"{ef_id} at busbar ({basis})")
    td_id = td_record_id(q.region)
    if td_id not in db.records:
        raise KeyError(f"no T&D record for region {q.region}: {td_id}")
    td = float(db[td_id].value)
    return GridFactor(value=ef / (1 - td), unit=f"kg {q.gas_basis}/kWh", query=q, record_ids=[ef_id, td_id] + extra_ids,
                      derivation=f"({basis}) {ef:.4f} at busbar / (1 - {td_id} = {td}) = {ef / (1 - td):.4f}")
