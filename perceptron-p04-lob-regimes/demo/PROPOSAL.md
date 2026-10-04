# P4 demo proposal: "The alarm that cries wolf"

**Status:** proposal for lead approval (2026-10-04, IST). Nothing is built yet beyond a timing probe.

## Crazy element (recommended): the alarm dial
The judge turns one dial: the textbook KS test's significance level, log10 α from −1 down to −300, with two extra stops, "calibrated (empirical null)" and "off (α = 0)". Two views update instantly: the replay day's alarm ticks and loss, and a held-out panel showing KS→refit over 22 days at that α against the regime gate.

**What the probe found** (post-hoc probe, 2026-08-01; computed with the committed `run_episode`):
- At α = 1e-3, KS→refit fires 48 times and scores log-loss 0.593946, which equals the committed `v2_holdout.json` value.
- At α = 1e-10 it fires 44 times; at 1e-20, 37 times; at 1e-30, still 26 times. Loss worsens to 0.7086, above the coin flip's ln 2.
- The reason is that `kstwo.sf` underflows to exactly 0 at D = 1. No α > 0 switches the alarm off.

**Hypothesis:** the demo shows it only if the sweep confirms it.
- No α (and no calibrated quantile) makes detect→retrain beat conditioning on state.
- The "off" stop equals one EWMA head (`static_enorm`), which is still +0.0083 worse than the regime gate (post-hoc ablation).

## Screens (one offline HTML page, plain canvas, no libraries)
1. **Scoreboard** (shown instantly). The committed 22-day table: static, `static_enorm`, `ks_refit`, `ksc_refit`, `regime_gated`, `spike_gate`, and the registered `spike`. Each row shows Δ vs static with its 97.5% CI and the number of days better. Rows carry status chips (pre-registered primary / post-dev secondary / post-hoc).
2. **Replay, real data first.** A day picker offers:
   - 2024-05-01, labelled "dev day, illustrative" (FOMC 18:00 UTC);
   - three held-out days chosen by a stated rule on the committed `regime_by_day.rv_600s_bps_mean`: calmest 2026-08-01, lower median 2025-05-01, most volatile 2026-03-01.

   Stacked panels share a UTC axis:
   - (a) price as 10-minute OHLC candles, with the event marker;
   - (b) alarm tracks: textbook KS (triggers refit), KS audit (no action), CUSUM (triggers shrinkage);
   - (c) the active regime head, as each head's share per 10 minutes;
   - (d) log-loss per policy in 10-minute bins, plus cumulative Δ vs static.

   Per-day totals are labelled "live-computed". On held-out days a ✓ appears when the total equals the committed `per_day` value.
3. **Dial panel.** Sliding α moves:
   - the alarm ticks and the `ks_refit` curve in panel 2;
   - the 22-day sweep: Δ vs static against α, with the regime-gate line, the 48/day cooldown cap and alarms/day;
   - a "why" inset: on the 12 training days (leave-one-day-out reference, as in `calibrate_ks_null`), the share of windows the naive test rejects against nominal α, plus the share whose p-value is exactly 0.

   All dial outputs are labelled "post-hoc demo sweep, not pre-registered".
4. **Execution knob.** Fee tier (Regular / VIP 9), delay (0 / 100 ms) and taker vs maker upper bound give the net bps per signal from committed `edge`. The panel ends on "not tradable as a taker after fees".

**Optional Act 2 (stretch, only if time allows; labelled SEMI-SYNTHETIC):** splice a calm and a volatile real day at a judge-chosen time.

## Where the numbers come from
| On screen | Source | Status |
|---|---|---|
| Scoreboard, execution knob | `eval/results/v2_holdout*.json` | as committed |
| Replay curves, alarms, totals | `demo/build_replay.py`, using `run_episode` with `build_context` on the 2023 training days, into gitignored `demo/.cache/` | live-computed |
| 22-day α sweep and null-rejection inset | `demo/build_sweep.py` writes `demo/results/alarm_dial_sweep.json` (per-day log-loss, alarm counts, 22-day Δ with day-cluster CI; aggregates only) | post-hoc demo sweep |

The α override uses `dataclasses.replace(ctx, cfg=…)`; nothing in `components/` or `eval/` changes. Anchors:
- the α = 1e-3 row must reproduce committed `ks_refit` on all 22 days;
- the calibrated q = 0.999 stop with the v1 feature set must reproduce `ksc_refit`;
- the "off" stop must reproduce `static_enorm`.

## Compute budget (this Mac, CPU, `nice -n 10`, at most 3 workers)
- Context build takes about 10 s once data is cached. A `ks_refit` run takes 4–6 s per day per α.
- **Sweep** (one-off, committed): 22 days × about 18 dial stops ≈ 2,000 CPU-s, about 12 min on 3 workers.
- **Replay build** (each `run.sh` on a fresh cache): 4 days × (5 policies + 18 stops) ≈ 6 CPU-min, about 2–3 min on 3 workers.
- **First visual:** the scoreboard and sweep appear in under 5 s from committed JSON. The replay panels fill in progressively (the page polls `.cache/status.json`).

## Fresh-clone fetch plan
`run.sh` checks each needed file and fetches only the missing ones with `data/fetch_tardis.py --types book_snapshot_5 --workers 2`. These are first-of-month days, so no API key is needed. MD5s are verified against `data/manifest.csv`. Days needed:
- the 12 training days, 2023-01 … 2023-12;
- 2024-05-01, 2026-08-01, 2025-05-01 and 2026-03-01.

That is 16 files, **473 MB** (sizes from the manifest). Regenerating the sweep needs the other 19 held-out days; that is documented, not done by `run.sh`. After the fetch, the demo runs offline.

## Licence (Tardis ToS §9.2)
- Raw data, per-second series and features never leave `.data/` or `demo/.cache/`, both gitignored.
- The page draws prices only as 10-minute candles and losses in 10-minute bins. The replay cache itself holds only these 10-minute aggregates and alarm timestamps, so the fallback screenshots are safe.
- Committed outputs are per-day or 22-day aggregates and alarm counts only.

## Risks
- **The sweep could contradict the hypothesis** (some α beats the gate). The page then shows that honestly; the claim text is generated from the sweep.
- **Small effects** (about 0.01 nats) are hard to see. Mitigations: cumulative Δ curves and "days better" counts.
- **Shared Mac load:** there is a memory guard, and the replay build runs in the background behind the instant scoreboard.
- **Fresh-clone download time** (473 MB) is outside the 60-s budget. It is documented as a one-time step.
