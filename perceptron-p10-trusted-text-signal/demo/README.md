# P10 demo — "Break the band"

You are the manipulator. Pick a real StockNet stock-day, write fake posts (scored live by the deployed MiniLM scorer), give them a fake account (trust via `trust_of`), and inject them. Watch the plain CQR interval break on the few days where it can, while the **certified** band provably contains the no-injection interval for any ≤ k injected posts. Then let the machine red-team the day, and replay your attack on all 16,443 test stock-days.

```bash
bash perceptron-p10-trusted-text-signal/demo/setup.sh   # once per machine (fresh clone: ~2 min, offline from uv's cache)
bash perceptron-p10-trusted-text-signal/demo/run.sh     # opens http://127.0.0.1:8710/
bash perceptron-p10-trusted-text-signal/demo/smoke.sh   # headless assertions (~2–3 min)
```

- **Fresh clone, offline, CPU only.** No StockNet fetch is needed: the committed 5.6 MB `bundle/` holds the cal+test feature rows, per-post sentiment/trust scores, the three LightGBM models as text, the sentiment head as JSON, and the showcased days.
- **Setup (`setup.sh`).** Uses `P10_PYTHON`, else the project `.venv`, else creates `demo/.venv` with `uv` from `requirements.txt` (offline wheel cache first), then pays macOS's one-time first-load scan of the new native libraries. If you skip it, `run.sh` runs it for you, and meanwhile the browser shows the clearly labelled **RECORDED** fallback screenshots (`static/setup.html`, up in about 1 s), switching to the live page by itself.
- **Timing on this M5 Mac, CPU, measured from a fresh clone.**
  - One-time setup: 106 s, of which about 15 s is the `uv` install; the rest is the macOS first-load scan.
  - First run after setup: live first visual in 14.8 s.
  - Later runs: 3.9 s (6.1 s with the project venv). The MiniLM scorer is ready about 4 s after that.
- **Scorer.** The live scorer needs `sentence-transformers/all-MiniLM-L6-v2` in the Hugging Face cache (about 90 MB; one-time `hf download sentence-transformers/all-MiniLM-L6-v2`). Without it the page uses VADER and says **FALLBACK** on screen.
- **Shared-Mac guards.** Everything runs under `nice -n 10` and waits while `kern.memorystatus_level` < 30. The memory guard runs before any native library loads. `P10_PORT` and `P10_NO_OPEN=1` are honoured.

## What is live, and what it must match
All numbers come from the committed result files, or are computed live by the committed code paths. `engine.py` uses `QuantileFusion.predict`, `cqr_offset`, `features_from_docs`, `inject_seq`, `oracle_grid`, `CertifiedCQR`, `trust_of` and `aci_from_bounds`. `scorer_worker.py` uses `MiniLMSentimentScorer.score`, or `VaderScorer`.

`smoke.sh` asserts the live values equal `eval/results/text_minilm_v2.json` within 1e-9:
- ACI 89.497%;
- the CQR offset, and clean symmetric CQR;
- certified k = 1/2/3/5 coverage and width;
- the pump: plain, certified, ACI, CR-ACI and the shift;
- the worst fixed variant, beyond-budget 4/6/10, and the 53-variant oracle.

It also checks:
- the live MiniLM score of the pump template is within 1e-4 of the committed 0.952 (it is exact on this Mac);
- 78,000 random within-budget attacks over 26 days give 0 certified containment violations;
- every endpoint, plus input validation;
- in headless Chrome, the page's own `#selftest` drives the real UI and must pass:
  - a typed post is scored and injected; one fake post breaks plain CQR while the certified band is GUARANTEED;
  - the badge turns grey past k;
  - the red-team shows 0 violations;
  - a red-team result started on one day is discarded after switching to another (regression for review M1).
- a negative control: the same page with the API unreachable must *not* pass.

## Honesty rules the page follows
- **Curated days are labelled as selected.** A day is *flippable* if a committed `oracle_grid(3)` attack flips plain CQR. That is 327 of 16,443 stock-days (2.0%), 207 of them with no real posts. The rule is in `export.py` and the population rate is always shown. The test period was inspected during development, so this is exploratory.
- Injected posts are badged **INJECTED · SYNTHETIC**.
- Grid attacks injected from the "which posts could flip" table say their sentiment was set directly, not scored.
- The certified badge claims containment of the *no-injection interval*, not coverage of the realised return.
- CR-ACI is shown only as long-run mean daily coverage. Clean and attacked ACI runs are not nested, so no per-row claim is made.
- The footer always shows that text adds no measurable forecast value (pre-registered DJIA test, p = 0.46) and that typical attacks barely move the forecast.

## Files
| File | Role |
|---|---|
| `run.sh`, `setup.sh`, `smoke.sh`, `_env.sh` | one-command launch; one-time setup; headless checks; Python and memory guards |
| `server.py` | stdlib `http.server` with JSON endpoints: `/api/{health,meta,random,day,score,trust,attack,flips,redteam,population}` |
| `engine.py` | all computation, via committed code |
| `scorer_worker.py` | live text scorer in a separate process (torch + LightGBM in one process segfaults on macOS) |
| `static/index.html` | the whole UI: one file, plain SVG, no JS libraries, no CDN |
| `static/setup.html` | recorded-screenshot gallery shown while setup runs; switches to live by itself |
| `export.py` | regenerates `bundle/` from the cached v2 data (needs the StockNet fetch); verifies bit-exact round trips |
| `bundle/` | committed data (see `bundle/ATTRIBUTION.md`: StockNet MIT, TFNS MIT, MiniLM Apache-2.0) |
| `SCRIPT.md`, `fallback/` | 3-minute talk track; screenshots of each key state |

Regenerate the bundle (only needed if the eval changes):

```bash
cd perceptron-p10-trusted-text-signal
PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python demo/export.py --src .cache
```
