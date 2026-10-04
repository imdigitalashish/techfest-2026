# India grid CO2e upstream factors — note (2026-10-04)

Wrote factor records for the upstream pieces needed to extend the existing CEA v22 FY2025-26 India grid factor (`energy.electricity.in.grid_wavg_generation.fy2025_26`, 0.675 kg CO2/kWh, busbar CO2-only) toward a life-cycle CO2e-at-meter factor.

## Opened sources and key values

- **IPCC 2006 Vol. 2 Ch. 2 Table 2.2** (`.data/raw/upstream/ipcc2006_v2_ch2.pdf`): energy-industries stationary-combustion defaults, NCV basis. Coal ranks: CH4 **1 kg/TJ** (0.3–3), N2O **1.5 kg/TJ** (0.5–5). Natural gas: CH4 **1 kg/TJ** (0.3–3), N2O **0.1 kg/TJ** (0.03–0.3). These are native-gas factors, not CO2e.
- **IPCC 2006 Vol. 2 Ch. 4** (`.data/raw/upstream/ipcc2006_v2_ch4.pdf`): Tier-1 coal-mine CH4 defaults, m3 CH4/t raw coal: underground mining **18** (10–25), underground post-mining **2.5** (0.9–4.0), surface mining **1.2** (0.3–2.0), surface post-mining **0.1** (0–0.2); density **0.67 kg CH4/m3**.
- **India BUR-4 / MoEFCC 2024** (`.data/raw/upstream/india_bur4.pdf`, via public Wayback copy because direct UNFCCC curl was blocked): country-specific coal-mining CH4 factors, m3/t: surface mining **1.18**, surface post-mining **0.15**; underground Degree I/II/III mining **2.91/13.08/23.64** and post-mining **0.98/2.15/3.12**. BUR-4 Table 2.14 gives 2020 production by those classes: **724.45/26.76/7.05/0.47 Mt**.
- **Coal Directory of India 2024-25 / Ministry of Coal** (`.data/raw/upstream/coal_stats_28-11-2025a-stc.pdf`): OC/UG raw coal production shares: FY2023-24 **96.56%/3.44%**; FY2024-25 **96.96%/3.04%**.
- **CEA CO2 Baseline Database v22 user guide** (`.data/raw/upstream/cea_ug_v22.pdf`): fallback default for coal stations: gross heat rate **2,500 kcal/kWh** and coal GCV **3,755 kcal/kg**, deriving **0.666 kg coal/kWh gross**. This is a CEA default assumption, not a measured all-India annual average.
- **IPCC AR6 WG1 Ch. 7 Table 7.15**: GWP100 **CH4-fossil 29.8**, **N2O 273** (AR6, with carbon-cycle responses). **IPCC AR5 WG1 Ch. 8 Table 8.7 + footnote b**: GWP100 **CH4-fossil 30** (28 + fossil adjustment 2), **N2O 265** (without climate-carbon feedbacks).

## Proposed derivation formula

Preferred AR6 busbar-to-meter build-up:

```text
grid_co2e_at_meter = (
  energy.electricity.in.grid_wavg_generation.fy2025_26
  + stationary_nonco2_co2e_per_kwh
  + coal_mine_ch4_co2e_per_kwh
  + other_upstream_fuel_chain_co2e_per_kwh
) / (1 - energy.electricity.in.td_loss_share.fy2023_24)
```

Where:

```text
stationary_nonco2_co2e_per_kwh = Σ_fuel(
  fuel_energy_TJ_per_kWh_busbar_fuel * [CH4_kg_per_TJ * method.gwp100.ch4_fossil.ipcc_ar6
  + N2O_kg_per_TJ * method.gwp100.n2o.ipcc_ar6] / 1000
)

coal_mine_ch4_co2e_per_kwh ≈ coal_kg_per_kWh * coal_mine_ch4_m3_per_t / 1000
  * energy.upstream.coal_mining.ch4_density.ipcc2006
  * method.gwp100.ch4_fossil.ipcc_ar6
```

Use BUR-4 India coal-mine factors before IPCC global defaults. For an inventory-consistent 2020 weighted coal-mine factor, weight BUR-4 Table 2.13 factors by `energy.upstream.coal_mining.production_by_gassiness.in.bur4.2020`. For a newer FY2024-25 approximation, use Coal Directory OC/UG shares, but the **UG Degree I/II/III split is missing** for 2024-25 and must be assumed or backfilled from DGMS/CIL statistics.

## Gaps

- No verified India-specific stationary-combustion CH4/N2O factors for energy industries were found in BUR-4; IPCC 2006 Tier-1 defaults are the defensible fallback.
- No measured all-India kg coal/kWh series was opened; the CEA value recorded is only a default assumption.
- No gas upstream supply methane factor and no coal rail-transport factor were opened; `other_upstream_fuel_chain_co2e_per_kwh` remains missing.
- No published India grid life-cycle CO2e cross-check was opened; leave any such benchmark UNVERIFIED until sourced.

## Erratum and implementation note (lead, 4 Oct 2026, after the gpt-6-astra ADR review)
- The "stationary_nonco2_co2e_per_kwh" formula above has a dimensional slip: TJ/kWh x kg gas/TJ x kg CO2e/kg gas is already kg CO2e/kWh, so the extra `/1000` would suppress the term 1000-fold. It was **not** used. The committed implementation (`data/vehicles/*.yaml` CO2e scenarios and `components/lca_engine/greenauto/grid.py`) applies a dimensionless ratio, CEA CO2 x (CH4_kg/TJ x GWP_CH4 + N2O_kg/TJ x GWP_N2O) / (CO2_kg/TJ), with Indian coal at 95.8 g CO2/MJ NCV (CEA Appendix B). A unit test pins the result: 0.6933 kg CO2e/kWh at busbar.
- The 0.666 kg coal/kWh above is a GROSS-generation default. The implementation uses the CEA default NET heat rate 2,717 kcal/kWh / GCV 3,755 kcal/kg = 0.724 kg coal per net kWh of coal generation, times the coal+lignite share of total net generation (0.672).
- Not yet handled: imported coal (CEA 89.5 g CO2/MJ NCV) vs domestic, lignite-specific factors, mining energy use, coal rail transport, gas supply chain and infrastructure.
