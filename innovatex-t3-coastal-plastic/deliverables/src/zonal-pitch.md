# Zonal pitch package — NullahNet (InnovateX Theme 3: Rising plastic pollution in coastal cities)

Status: complete as an **alternative** to the team's chosen Delhi-zonal theme (Theme 1, JalSakshi). Use it only if the team switches themes.

| File | What it is |
|---|---|
| [`zonal-deck.md`](zonal-deck.md) → [`zonal-deck.pdf`](zonal-deck.pdf) · [`zonal-deck.pptx`](zonal-deck.pptx) | 10 main slides + 4 backups. Speaker notes per slide carry timing, what to say, the line to land and what not to say. The PPTX holds the notes. |
| [`qa-prep.md`](qa-prep.md) | Twenty likely judge questions with answers; every number is bound to a source or a committed run |
| [`presenter-card.md`](presenter-card.md) → [`presenter-card.pdf`](presenter-card.pdf) | One A4 page: run of show, numbers to remember, fast answers, don't-say list |
| [`prototype-plan.md`](prototype-plan.md) | Round-2 plan: tow-tank flume, edge node, tests T1–T6, three bills of materials with URL and date per part, schedule around the exams |
| [`figures/`](figures/) | Deck figures, drawn from committed results by [`make_figures.py`](make_figures.py) |

**One-line pitch:** Mumbai's trash booms leak in fast flow, are cleared on a fixed schedule and are paid on claimed loads. NullahNet retrofits them so crews clear at the right tide, the boom keeps its catch and never raises flood levels, and contractors are paid per verified kilogram.

**Headline numbers (each bound to its source):**
- {{f:F01|5 million kg}} a year leaks from the metro region (The Ocean Cleanup survey, 2026).
- BMC is growing its boom network from {{f:F12|9}} to {{f:F12|23}} booms at {{f:F12|≈ ₹1 crore}} each.
- In our twin (SIMULATED), {{r:ent_esc}} of escaped plastic slips under or through the boom.
- Tide-aware dispatch vs clear-when-full: {{r:p2p1_med}} escaped plastic, better in {{r:p2p1_n}} of {{r:n_draws}} draws (SIMULATED).
- One sensor node costs {{f:D04|₹83,481.98}}, including the enclosure.

**How the package is built (no hand-typed numbers):**
1. `python3 innovatex-t3-coastal-plastic/eval/render_docs.py` renders `src/*.md` with committed results.
2. `python3 innovatex-t3-coastal-plastic/deliverables/make_figures.py` draws the figures.
3. `bash innovatex-t3-coastal-plastic/deliverables/build.sh` exports the PDF, PPTX and presenter card.
4. `python3 innovatex-t3-coastal-plastic/eval/check_docs.py` checks for drift, source binding, unmarked numbers and stale text. It must report 0 problems.

**On the day:**
- Present the PDF from your own laptop.
- Open the dashboard offline in a second tab.
- Fill the ‹team› placeholders on slide 1.
- Rehearse to 9:15 with the presenter card.
