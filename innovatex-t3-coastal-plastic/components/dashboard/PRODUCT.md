# NullahNet operations dashboard: product notes

Register: product UI (operate mode). The user asked for an actionable overview instead of a data dump (2026-10-04 17:20 IST). I inferred the rest from the brief and the components; nothing below was confirmed by an operator.

## Who opens it, and when
- **Ward storm-water-drain (SWD) engineer or boom-contract supervisor**, at about 05:30 IST when the day-ahead forecast lands, on a laptop in the ward office or on a phone at the outfall.
- **Contract auditor**, weekly, to decide which clearance claims to pay.
- **Judges and demo viewers**, who need to see in under a minute what the system decides and why, and what is real versus simulated.

## The three questions it must answer, in this order
1. **What do I do today?** A ranked list of actions: dispatch crews (with time windows and a ready-to-send crew message), sites to watch, and claims to check. Each action can be marked done.
2. **Why?** Every action opens its inputs: sensor fill, forecast rain, tide, the planner's note, what the simpler rules would have done instead, and the simulation evidence for the planner.
3. **Can I trust the numbers?** Claims that sensors don't support appear first. The chain and signature check runs in the browser. Every SIMULATED or SYNTHETIC value is labelled where it appears, and all sources are in one panel.

## Non-goals
- No live data or field hardware yet: this is a replay of the 2025 monsoon with real rain and tide and simulated sensors.
- No language model writes text. The morning brief is a rule-based template over the same numbers that appear on screen, so it cannot invent anything.
- No payment amounts in rupees, because no rate has been verified.
