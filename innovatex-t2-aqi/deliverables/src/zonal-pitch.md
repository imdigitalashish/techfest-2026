# Zonal pitch — DustLedger (InnovateX Theme 2: Rising AQI in Modern Urban Cities)

*Status, 4 Oct 2026: a fully documented **alternative** to T1 (JalSakshi), which two independent judges picked for the Delhi zonal on 10 Oct. One InnovateX theme per team; the user decides. Rendered from `deliverables/src/zonal-pitch.md`.*

**The package**
- Deck: [`zonal-deck.md`](zonal-deck.md) → [`zonal-deck.pdf`](zonal-deck.pdf) / [`zonal-deck.pptx`](zonal-deck.pptx). 10 main slides + 6 backups, timed speaker notes (9:15 route + 45 s reserve), status labels BUILT · SIMULATED · PLANNED on every claim.
- Q&A prep: [`qa-prep.md`](qa-prep.md) (22 questions, honest answers). Presenter card: [`presenter-card.pdf`](presenter-card.pdf).
- Prototype plan with a verified parts list and power budget: [`prototype-plan.md`](prototype-plan.md).
- Numbers: run numbers rendered from committed results by `eval/render_docs.py`; cited numbers bound to [`research/fact-check.md`](../research/fact-check.md); `eval/check_docs.py` fails on drift.

**The pitch in one paragraph.** Delhi restricts dust-generating construction from {{v:F1|Nov 1 – Jan 31}} and bans it from {{v:F1|Dec 10 – Jan 20}}, at every site, because a city-scale monitor can't say which site made the dust. Construction is a small slice of Delhi's PM ({{v:F9|2-5%}} of ambient PM10 in IIT Kanpur's 2016 study) handled with the bluntest tool, and the cost lands on workers. DustLedger puts four low-cost PM nodes and a wind sensor on a site's boundary: downwind minus upwind is the site's own dust, "inconclusive" when the wind is calm or confused, misting only when the site is the cause, and signed records that tell inspectors where to look. Evidence today: a forecasting benchmark on real Delhi data (city forecasting isn't the gap), and an attribution replay on real background and wind with a simulated site, stress-tested after an independent review ({{n:at_selfcal}} vs {{n:at_refcal}} µg/m³ against weekly reference visits). Parts for one site cost ₹{{n:bom_kit}}.

**What it is not.** Not a city-AQI fix, not a legal measurement (inspectors still verify), not field-validated. Exemptions for clean sites are a proposal for CAQM, not a promise.
