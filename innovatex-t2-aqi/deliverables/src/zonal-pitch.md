# Zonal pitch — DustLedger (InnovateX Theme 2: Rising AQI in Modern Urban Cities)

*Status, 4 Oct 2026: a fully documented **alternative** to T1 (JalSakshi), which two independent judges picked for the Delhi zonal on 10 Oct and which the lead also recommends. One InnovateX theme per team; the user decides. Rendered from `deliverables/src/zonal-pitch.md`; revised after two cross-model reviews (`reviews/`).*

**The package**
- Deck: [`zonal-deck.md`](zonal-deck.md) → [`zonal-deck.pdf`](zonal-deck.pdf) / [`zonal-deck.pptx`](zonal-deck.pptx). 9 main slides + 8 backups, timed speaker notes (8:45 route + 1:15 reserve), status labels BUILT · SIMULATED · PLANNED.
- Q&A prep: [`qa-prep.md`](qa-prep.md) (22 questions). Presenter card: [`presenter-card.pdf`](presenter-card.pdf).
- Offline demo: [`demo/dustledger-demo.html`](demo/dustledger-demo.html) — real Delhi background and wind, simulated sites; regulator ranking + site view ([README](demo/README.md)).
- Prototype plan with a verified parts list and a power estimate: [`prototype-plan.md`](prototype-plan.md).
- Numbers: run numbers rendered from committed results by `eval/render_docs.py`; cited numbers bound to [`research/fact-check.md`](../research/fact-check.md); `eval/check_docs.py` fails on drift (a binding gate, not fact verification).

**The pitch in one paragraph.** The reported 2026-27 Winter Action Plan restricts dust-generating construction across Delhi from {{v:F1|Nov 1 – Jan 31}} and bans it from {{v:F1|Dec 10 – Jan 20}}; rules follow the activity and the pollution stage, because a city-scale monitor can't say which site released the dust. Construction was a small slice of Delhi's PM in IIT Kanpur's 2016 study ({{v:F9|2-5%}} of ambient PM10). DustLedger puts four low-cost PM nodes and a wind sensor on a site's boundary: downwind minus upwind estimates the site's own dust, "inconclusive" when the wind is calm, misting only when the estimate says the site is adding dust, and signed records that tell inspectors where to look first. Evidence today is a simulation on real background and wind: self-calibration beats a robust reference-visit baseline over all hours ({{n:at_selfcal}} vs {{n:at_refcal14}} µg/m³) and roughly halves false alarms, but it is no better in work hours, and the test isn't blind. Parts for one site cost ₹{{n:bom_kit}}.

**What it is not.** Not a city-AQI fix, not a legal measurement (inspectors still verify), not field-validated. Exemptions for clean sites are a proposal for CAQM, not a promise.
