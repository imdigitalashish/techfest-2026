# Per-component research — index

One file per component (or component group), each covering the state of the art, innovation candidates, and sources opened on 2026-10-04. Contracts: [`../../architecture/contracts/contracts.py`](../../architecture/contracts/contracts.py). Map: [`../../architecture/components.md`](../../architecture/components.md).

| Component(s) | Research file | Status (4 Oct, 07:35 IST) | Innovation candidates (short) |
|---|---|---|---|
| C1 forcing, C2 load, C3 hydraulics, C4 interceptor, C9 forecaster, C10 dispatch | [twin.md](twin.md) | written by the twin session; parameter table with sources/ASSUMPTIONs | archived-forecast dispatch (Spike 1, small gain in the twin); gated-vs-open outfall logic; FWCE as the north-star metric |
| H1 barrier hardware (boom, ratchet pocket, fail-open fuse) | [interception-hardware.md](interception-hardware.md) | written | angled boom below the escape velocity (≈0.35 m/s, ITOPF); ratchet pocket + fuse retrofit for existing BMC booms (Spike 2, flume-tested) |
| C5 detector, C6 flux counter | `detection.md` (detection session) | **pending**; component README at [`../../components/detection/README.md`](../../components/detection/README.md) | open-vocabulary prompts for film/sachets; tiling for small items; Mumbai-water domain adaptation |
| C7 fill estimator, C8 edge telemetry | [sensing-edge-bom.md](sensing-edge-bom.md) | written (specs, NASA POWER sizing, sourced BOM) | fused camera and ultrasonic fill; duty-cycled inference to fit the July solar budget; store-and-forward 4G |
| C11 evidence ledger | `mrv-ledger.md` (dashboard + MRV session) | **pending**; code and metrics at [`../../components/mrv_ledger/`](../../components/mrv_ledger/) | dry/volume-basis reconciliation; signed records with an external hash anchor |
| C12 dashboard | `dashboard.md` (dashboard + MRV session) | **pending**; site at [`../../components/dashboard/`](../../components/dashboard/) | provenance badges (REAL / SIMULATED / SYNTHETIC); crew phone view |
| C13 recovery and upcycling; policy and EPR | [policy-economics.md](policy-economics.md), [recovery-upcycling.md](recovery-upcycling.md) | written (EPR categories, end-of-life routes, BMC budget; drain-plastic EPR eligibility NOT FOUND) | EPR end-of-life route for low-value film; pay-per-verified-kg |
| C14 source attribution | — | **not started** (worker died); Round-2 item | ward ranking from outfall flux |
| Cross-cutting | [../landscape.md](../landscape.md), [../companies.md](../companies.md), [../mumbai-context.md](../mumbai-context.md) | all written | — |
