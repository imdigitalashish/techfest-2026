# ADR 001 review — first principles (independent agent)

> Verbatim output of an independent `First Principles` agent, run 05:15–05:55 IST on 4 Oct 2026, with no web access. **[V]** marks premises the agent itself flagged for verification; the numbers are illustrative reasoning, not citations. Synthesis: [001-spike.md](../../architecture/adr/001-spike.md).

**Reframe.** [V] means "premise to verify". If 5,000 t/yr [V] is right, that's about 14 t/day, roughly 0.2% of Mumbai's municipal solid waste [V]. So hauling and disposal capacity isn't the constraint. The hard part is catching a flow of plastic that is spread out, arrives in pulses and is partly underwater, and then paying honestly for catching it. Also, "tonnes to sea" can't be observed: much escaped plastic gets stuck in mangroves or washes back ashore on monsoon winds [V]. **Kg removed is not the same as kg prevented.**

### 1. Chain and binding constraints

Think of it as a **stock that builds up and then flushes**, not a steady pipe. Dry-season dumping builds a stock in drains and on banks. The first heavy rains wash it out, then it moves through transport → barrier → clearance → disposal.

$$\text{kg}_{\text{sea}}=\sum_{\text{events}}A_e\left(1-\eta_{\text{capture}}(u,h)\,\eta_{\text{retain}}(V,\text{tide},\text{release})\right)$$

Here $A_e$ is the plastic arriving in each rain event, $u$ is flow velocity, $h$ is water depth and $V$ is boom-pocket storage.

**Two binding constraints:**

1. **Physical: plastic flux peaks exactly when barriers fail.** Heavy rain brings high velocity and high plastic flux. That's also when plastic is dragged under the boom's skirt, films are mixed below it, pockets overflow, and flood-safety rules force booms open. So capture weighted by plastic flow is far below capture averaged over time. No clearance schedule lifts that ceiling.
2. **Institutional: money follows claimed wet tonnes, not kg prevented** (cf. the 2025 desilting allegations [V]). The strongest existing lever is removing the dry-season stock before the June rains. That is precisely the work whose output is hardest to verify.

**Where the leverage is, provisionally:**

1. Measurement and verification: cheap, and it unlocks everything else.
2. Timing: remove stock before the monsoon, and empty pockets before surges.
3. Source collection along nullah banks: the only lever that still works during peaks, but slow.
4. Capture hardware: worth it only at a few large sites.
5. Financing: follows verification; money isn't scarce at this tonnage [V].

**Counterpoint:** stormwater practice finds that most annual water *volume* passes in frequent moderate flows, which barriers handle well [V]. **Synthesis:** the answer depends on each outfall's load–duration curve, i.e. how much plastic arrives at each flow rate. Is plastic limited by the stock available, or by how much the flow can carry? That can be measured, and it decides the strategy.

### 2. Barrier physics

- **Velocity across the boom:** floating barriers lose material under the skirt above roughly 0.35–0.5 m/s (oil-boom experience [V]). With storm flows of 1–3 m/s [V], the boom must be angled so that $u\sin\theta \lesssim 0.4$ m/s. That means a boom 2.5–7.5× the channel width.
- **Submerged fraction:** set by how fast an item rises ($w_r$) versus turbulence ($u_*$). Wet films and sachets rise slowly, so storms mix them through the water column. A skirt reaching depth $d$ in water of depth $h$ then sees only about $d/h$ of them. Bottles and thermocol stay catchable.
- **Storage:** time to overflow is $T=V/q$, where $q$ is the debris arrival rate. With an illustrative ~20 m³ pocket and storm arrivals of tens of m³/h, $T\approx 1$ h. Big outfalls are limited by removal throughput and need mechanical removal; small ones are limited by clearance scheduling.
- **Load:** force on the boom grows as $F\propto u^2\times$ mat area. Hyacinth and other organics fill storage, snap anchors and dominate the wet tonnage.
- **Tide:** behind closed (tide-locked) flap gates, water is still and debris floats up and gathers. That is the *best* window for capture and clearance. The surge as the tide falls after a rainy high tide is the *worst*. At outfalls without gates, the reversing tide re-floats stranded debris and pushes marine litter onto booms, inflating "capture".

**Implication:** intercept where and when velocity is low: behind closed gates, in wide stretches, at full-depth screens in pumping stations [V], and during the first flush with empty pockets. Outfall mouths during the outgoing surge are the worst place.

### 3. Minimal measurements

1. **Per outfall:** one fixed infrared camera viewing the boom pocket and a painted depth gauge.
2. **Per clearance:** GPS-stamped load → weighbridge → random sort to find the dry-plastic fraction.
3. **At 5–10 sample outfalls:** measure escape by releasing tagged items and counting how many are recaptured, or with a downstream audit net.
4. **Free inputs:** tide tables (fully predictable) and short-term rain forecasts.

**The single reading: how full the pocket is (%).** Its trend gives time until overflow. The same camera also gives water level, flow direction and before/after proof of clearance.

### 4. Innovations

| | Mechanism | Upper bound | Assumption that could kill it |
|---|---|---|---|
| **A** Dispatch | Empty pockets before forecast surges; clear while gates are tide-locked and debris is concentrated; move crews to the highest-load outfalls | Only escapes caused by overflow, plus more kg per crew-hour | Escapes are caused by full pockets, not velocity; crews can reach sites safely within the forecast lead time |
| **B** Verification + pay/kg + EPR | Pay for evidenced dry kg, not claimed wet tonnes; producer fees fund low-value films | Cost per tonne falls by today's overclaiming factor; moves no plastic itself | Kg removed ≈ kg prevented, yet pay-per-kg rewards *bringing in* plastic from elsewhere (cobra effect); no EPR double-counting [V] |
| **C** Camera counting | Time-resolved flux index that calibrates A, B and E | Information only; surface items in lit, clear conditions | Surface counts track total flux, but cameras are blind at night, in rain and to submerged films (i.e. at peaks); converting item counts to mass is unreliable |
| **D** Ratchet + fuse | One-way pocket holds the catch when the tide reverses; with the pocket at the bank and the fuse mid-channel, the catch stays when the fuse opens | Losses from tidal reversal and boom breakage, at ungated sites only | Reversal losses matter (gated outfalls have none); flaps keep working through hyacinth, rags, silt and barnacles. The fuse opens at peaks by design |
| **E** Attribution | Targets collection and producer responsibility at the biggest sources | Zero tonnes directly; value depends on how unequal the sources are | The signal survives mixing (wards ≠ drainage catchments; stock is re-washed); and lack of information, not of collection in informal settlements, is the bottleneck |

### 5. Spikes

Start now: dry-season tides allow calibration before the June 2027 first flush.

1. **Load and escape spike** at 3–5 contrasting outfalls: one gated, one open-tidal like the lower Mithi, one pumped. Use camera, gauge, weigh-and-sort, and tagged-item releases across tide and flow conditions. Decision rule: if most plastic arrives below the velocity at which booms fail, fund A plus angled booms. Otherwise, move money to pre-monsoon stock removal and nullah-bank collection.
2. **A+B paired trial:** matched outfalls with equal crew-hours, every clearance evidenced and checked against contractor claims.

**The one number: flux-weighted capture efficiency.** That is verified plastic kg removed ÷ plastic kg arriving, over a monsoon. It turns "removed" into "prevented", and it caps what any outfall intervention can achieve.
