# Per-component research — index

One file per component (or component group), each covering the state of the art, innovation candidates, and sources opened on 2026-10-04. Contracts: [`../../architecture/contracts/contracts.py`](../../architecture/contracts/contracts.py). Map: [`../../architecture/components.md`](../../architecture/components.md).

| Component(s) | Research file | Status (4 Oct, 16:30 IST) | Innovation candidates (short) |
|---|---|---|---|
| C1 forcing, C2 load, C3 hydraulics, C4 interceptor, C9 forecaster, C10 dispatch | [twin.md](twin.md) | written; §6 escape split, paired comparisons, fuse/pocket sensitivity (SIMULATED) | archived-forecast dispatch (Spike 1, small gain in the twin); gated-vs-open outfall logic; FWCE as the north-star metric |
| H1 barrier hardware (boom angle, one-way pocket, fail-open fuse) | [interception-hardware.md](interception-hardware.md) | written; tow-tank test plan in [prototype-plan](../../deliverables/prototype-plan.md) | angled boom below the escape velocity (≈0.35 m/s, ITOPF); ratchet pocket + fuse retrofit for existing BMC booms (Spike 2, flume-tested) |
| C5 detector, C6 flux counter | [detection.md](detection.md) | written; trained baseline in progress (see `components/detection/`) | open-vocabulary prompts for film/sachets; tiling for small items; Mumbai-water domain adaptation |
| C7 fill estimator, C8 edge telemetry | [sensing-edge-bom.md](sensing-edge-bom.md) | written (specs, NASA POWER sizing, sourced BOM) | fused camera and ultrasonic fill; duty-cycled inference to fit the July solar budget; store-and-forward 4G |
| C11 evidence ledger | [mrv-ledger.md](mrv-ledger.md) | written; code + SYNTHETIC evaluation in `components/mrv_ledger/` | dry/volume-basis reconciliation; signed records with an external hash anchor |
| C12 dashboard | [dashboard.md](dashboard.md) | written; site in `components/dashboard/site/` | provenance badges (REAL / SIMULATED / SYNTHETIC); crew phone view |
| C13 recovery and upcycling; policy and EPR | [policy-economics.md](policy-economics.md), [recovery-upcycling.md](recovery-upcycling.md) | written (EPR categories, end-of-life routes, BMC budget; drain-plastic EPR eligibility NOT FOUND) | EPR end-of-life route for low-value film; pay-per-verified-kg |
| C14 source attribution | — | **not started** (worker died); Round-2 item | ward ranking from outfall flux |
| Cross-cutting | [../landscape.md](../landscape.md), [../companies.md](../companies.md), [../mumbai-context.md](../mumbai-context.md) | all written | — |
