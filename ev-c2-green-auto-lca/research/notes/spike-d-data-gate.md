# Spike D — data gate (opened 4 Oct 2026; decision due 7 Oct)

**Question:** can we build one Indian material/component route comparison end to end from public, product-relevant
Indian data — without using corporate intensity ratios as product inventories?

## Opened so far
- **Ministry of Steel, Taxonomy for Green Steel for India** (Gazette notification, 23 Dec 2024; `data/sources/sources_materials.yaml`):
  - green steel < 2.2 t CO2e per tonne of finished steel; five-star < 1.6; four-star 1.6–2.0; three-star 2.0–2.2;
  - scope = scope 1 + 2 + limited scope 3 up to finished steel (agglomeration, beneficiation, purchased intermediates; excludes mining, downstream, transport);
  - NISST is the MRV and certification agency, using BEE's CCTS procedure (July 2024);
  - certificates state plant name, embodied emissions at finished-steel level, greenness %, star rating and quantity (clause 7).

  → This is a **government-defined product-level boundary**, which is exactly what spike D needs. Three threshold records are in `data/factors/materials_steel.yaml`, labelled as thresholds, not intensities.

## Gate criteria (go if all true by 7 Oct)
1. At least one public source of Indian **product- or plant-level** steel (or aluminium) intensities on a stated boundary: NISST certificates or registry, producer EPDs, or BRSR disclosures whose boundary can be mapped to the taxonomy scope.
2. A component bill of materials for one vehicle part with a public source (e.g. steel mass of a 2W frame or car body-in-white) — TERI 2026 uses A2MAC1 (commercial), so we need a public alternative or a clearly labelled assumption.
3. Route-level differentiation (BF-BOF vs coal-DRI-EAF vs scrap-EAF) available from Indian sources (Ministry of Steel roadmap, JPC, producer reports) with locators.

## Leads not yet opened (UNVERIFIED)
- Ministry of Steel "Greening the Steel Sector in India: Roadmap and Action Plan" (2024).
- NISST green-steel certification pages (nisst.org).
- Producers' BRSR (Tata Steel, JSW, SAIL, JSPL), Hindalco/Vedanta/NALCO (aluminium).
- Indian EPDs.

## Fallback (if no-go)
Harmonized national grid foundation, plus the steel taxonomy bands as illustrative sensitivities on a labelled assumed component mass. No invented supplier detail.
