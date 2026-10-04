# Landscape — state of the art for monitoring, intercepting and verifying nullah/creek plastic (Mumbai) — InnovateX T3

Owner: T3 research worker (tech + companies). Synthesis of sources opened **2026-10-04**; details and exact quotes live in the linked files. *(claim)* = vendor/operator figure. Detection-model papers and policy/EPR rules are covered by the sibling research threads (detection + flux; Mumbai + policy) and are not repeated here.

Linked research: [companies.md](companies.md) · [components/interception-hardware.md](components/interception-hardware.md) · [components/sensing-edge-bom.md](components/sensing-edge-bom.md)

## 1. The Mumbai situation (what is already happening)
- **The brief's "5 million kg" comes from The Ocean Cleanup's Smart Rivers Survey**: "the metropolitan region releases an estimated 5 million kilograms of plastic waste into the Arabian Sea and Indian Ocean every year" (press release, 10 Feb 2026, https://theoceancleanup.com/press/press-releases/the-ocean-cleanup-enters-india/). The survey used "drones, AI-enhanced remote-sensing cameras, GPS drifters, and global data registries".
- **The two outfalls the brief names are taken.** TOC holds MCGM Storm Water Drain permits for **Trombay Creek and Malad Creek**, signed an MoU with MPCB, and Plastic Fischer will run on-ground operations (30 Apr 2026, https://theoceancleanup.com/press/press-releases/the-ocean-cleanup-deploys-mumbai-interceptors/); expected 61–92 t/yr from the initial systems *(claim)*.
- **BMC already operates trash booms at nullah mouths**: nine steel-net booms with conveyors since ~2022 (NGT-directed), 14 more planned (→ 23), ≈ ₹1 crore each, 1.5 t/day per boom in the dry season and 2.5–3 t/day in the monsoon; highest volumes at ML Complex nullah (Dahisar) and Gazdhar Bandh (Santacruz West) (Hindustan Times, https://www.hindustantimes.com/cities/mumbai-news/bmc-to-install-14-more-trash-booms-to-stop-garbage-from-flowing-into-arabian-sea-thane-creek-101746212815731.html). O&M for six western-suburb sites: ₹14.5 crore for two years, awarded to Virgo Specialties (FPJ, 30 Jul 2026, https://www.freepressjournal.in/mumbai/mumbai-bmc-approves-145-crore-contract-to-maintain-trash-boom-systems-across-6-rivers-and-nullahs).
- **Implication:** the incumbent is *un-instrumented booms paid by contract*, plus one global NGO at two creeks. Nobody publicly reports per-outfall plastic flux, boom fill, verified kg, or tide/forecast-aware clearance. That gap is our product.

## 2. Interception (state of the art)
- Families: fixed solar Interceptors with conveyors (TOC), low-tech TrashBooms with manual clearing (Plastic Fischer), steel-net booms + conveyor (BMC), trash wheels (Baltimore, "500 tons ... each year" *(claim)*), bubble curtains (Amsterdam: ~190,000 pieces ≈ 1 t/yr; 86% *expected*), and mobile mop-up robots (WasteShark+, Clearbot). Evidence: [interception-hardware.md §1](components/interception-hardware.md).
- **Physics limit:** floating booms lose their catch above an escape velocity — for oil booms "around 0.35 ms-1 (0.7 knots) irrespective of skirt depth" (ITOPF TIP 3). The answer is to angle the boom (normal velocity below escape) — a testable flume rule for plastics (θ ≤ ~20° at 1 m/s, inference).
- **Gaps in published practice:** no opened source documents flood-stage release or tidal-reversal handling for any of these systems, and plastic-specific flume efficiencies could not be opened (UNVERIFIED). Flood safety (never become a dam) and tide awareness are open design space.

## 3. Sensing and edge AI
- Fill sensing + operator alerts already exist inside TOC's Interceptor Original ("Using sensor data, the containers are filled equally", "automatically sends a text message to the local operators" — https://theoceancleanup.com/rivers/interceptor-original/) → "a sensor that texts when full" is **not** novel.
- Commodity edge AI is now cheap enough per outfall: Raspberry Pi AI HAT+ 13/26 TOPS (Hailo-8L/-8; list $70/$110), Raspberry Pi AI Camera (Sony IMX500, on-sensor inference, 12.3 MP), Jetson Orin Nano Super (67 sparse TOPS, $249). Indian street prices: AI HAT+ 13 TOPS ₹6,854; AI Camera ₹8,339; Pi 5 8GB ₹21,199.99; Jetson Super kit ₹54,999.99. [sensing-edge-bom.md §2, §5](components/sensing-edge-bom.md).
- **Power is the binding constraint in the monsoon**: NASA POWER gives Mumbai **3.79 kWh/m²/day in July vs 7.09 in May** (annual 5.29). A 24 h-inference node (~8 W, ASSUMPTION) needs ~78 W of panel and ~720 Wh of battery for 3 days of autonomy; duty-cycling cuts this to ~29 W / ~270 Wh. BOM A (pilot node, priced items) ≈ ₹82,282; BOM B (student flume) ≈ ₹33,958 — both from Indian retailer pages opened today.
- Connectivity: 4G for event images; LoRaWAN (Tata Communications' network was piloted in Mumbai, Delhi and Bengaluru from 2016 per Kerlink) or NB-IoT for telemetry; current Mumbai coverage at specific outfalls is UNVERIFIED.

## 4. MRV, credits and EPR
- **Verified kg is already a product**: Plastic Fischer's river-plastic credits are "tracked and verified by third-party software (Inclusiv by ASM)" and sold via Pinwheel (https://www.pinwheel.earth/projects/plastic-recovery-and-recycling-india-and-indonesia); CleanHub sells "TÜV SÜD-verified collection" (https://cleanhub.com/). Credit prices: NOT FOUND.
- Indian EPR/recycling rails exist (Saahas "EPR compliance", Banyan "traceable rPE" for brands' EPR obligations; Recykal/ReCircle platforms — details NOT FOUND).
- **Gap we can fill:** current verification proves *collected* kg via chain-of-custody. Nobody publicly pairs it with *independent in-water evidence at the outfall* (camera flux count + fill + tide/flow context) that a tampered weighbridge record would contradict. That is the defensible MRV spike.

## 5. Practitioner critique to pre-empt
- Experts and HN commenters argue that high-profile cleanup tech distracts from collection and source reduction (The Revelator, Aug 2026, https://therevelator.org/why-ocean-cleanup-has-not-solved-plastic-pollution/; HN discussion https://news.ycombinator.com/item?id=49374036). Pitch interception as the *measured last line of defence* that feeds ward-level source reduction, not as the solution.

## What companies ship today
Full table with evidence and "borrow / beat" per company: **[companies.md](companies.md#what-companies-ship-today--summary-table)**. In one line each:
- **The Ocean Cleanup** — solar Interceptors + survey; **in Mumbai (Trombay, Malad) in 2026**. Borrow survey-first siting; beat on many-small-outfall coverage, dispatch and independent verification.
- **BMC + Virgo Specialties** — 9→23 conveyor trash booms, ₹1 cr each, ₹14.5 cr/2 yr O&M. The incumbent we instrument (cheapest path to adoption: retrofit, not replace).
- **Plastic Fischer** — TrashBooms, 3.2 Mkg, verified credits, 7 Indian cities; TOC's Mumbai operator. Partner, and the registry our ledger should feed.
- **Clearwater Mills / Trash Wheel**, **Great Bubble Barrier** — proven but site-specific, costly structures; tidal Mumbai is a poor fit without redesign.
- **Clearbot** (JNPA Mumbai), **RanMarine**, **Seabin** — mobile/marina collectors; Seabin's pivot to data dashboards validates "data as the product".
- **Greyparrot**, **AMP** — AI vision in sorting plants proves that waste-vision is bankable; we move the camera upstream to the outfall.
- **CleanHub**, **Saahas**, **Banyan Nation**, **Recykal**, **ReCircle**, **Skrap** — verification, EPR and off-take rails for the verified kg we produce.

## Where our design borrows and where it beats the field
| Layer | Borrow (best practice) | Beat (our claim, to be proven by the prototype/twin) |
|---|---|---|
| Barrier | Angled floating boom with skirt + conveyor/bins (BMC, TOC) | Flood-safe release + tide-aware geometry; retrofit kit for existing BMC booms |
| Sensing | Fill sensor + SMS (TOC) | Camera flux counts (items/min by class) + fill + level, solar-sized for July insolation |
| Dispatch | Daily clearing by contract (BMC) | Clear before forecast rain peaks and at low water; fewer overflow events per crew-hour |
| MRV | Chain-of-custody kg (Inclusiv/ASM, TÜV SÜD) | Independent in-water evidence reconciled against weighbridge kg (anti-fraud) |
| Source reduction | Awareness campaigns, wall nets (BMC) | Ward hotspot feedback from per-outfall flux |

## UNVERIFIED / NOT FOUND (carry into Q&A prep)
- Credit prices (Pinwheel/CleanHub); Clearwater Mills and Great Bubble Barrier company sites unreachable; Recykal/ReCircle/Sampurn(e)arth details; smart-bin vendors not researched; plastic-specific boom efficiencies vs velocity (papers not opened); flood/tide handling of any commercial system; Mumbai LoRaWAN/NB-IoT coverage today; UK EA trash-screen head-loss guidance (404).
