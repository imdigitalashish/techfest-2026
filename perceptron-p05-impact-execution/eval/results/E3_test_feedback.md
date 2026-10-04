# E3_test: feedback attribution (who absorbed / amplified our 4,000-share sell)

End-of-day (10:05) position change vs null twin, shares; mean over 60 test seeds with 95% bootstrap CI. Negative = sold more than in the twin (amplified our selling).

| policy | MomentumAgent | ValueAgent | AdaptiveMarketMaker | NoiseAgent |
|---|---|---|---|---|
| TWAP | -1302 [-3185, +636] | +5314 [+3502, +7134] | -86 [-475, +297] | +74 [-15, +163] |
| VWAP | -411 [-1886, +989] | +4595 [+3249, +6039] | -193 [-686, +317] | +9 [-76, +93] |
| IA_sched_only | -716 [-2606, +1043] | +5096 [+3410, +6813] | -401 [-1005, +191] | +21 [-51, +95] |
| IA_full | -531 [-2121, +922] | +4594 [+3204, +6167] | -102 [-599, +419] | +39 [-42, +126] |
| TWAP_touch_limit | -81 [-1740, +1509] | +4128 [+2483, +5806] | -62 [-596, +508] | +16 [-72, +107] |

Paired (touch-limit − TWAP) momentum Δpos: +1221 shares, 95% CI [-495, +2836]
Instant cost TWAP 0.1238 bps vs IA_full 0.0807 bps (-35%)
