# P8 demo · A tutor that finds the real reason you're stuck

One offline page plus a small local engine. It shows the pre-registered results on **real** Eedi wrong answers first, with three OpenAI models side by side, replayed from committed runs. Then a judge **plays the student**: the engine certifies their wrong answer, writes a follow-up question and seals a prediction of their next answer before they give it. Next comes a cascade **knob** (routing × model × budget). Labelled **synthetic** stress tests come last.

## Run it
```bash
perceptron-p08-misconception-tutor/demo/run.sh            # creates .venv if needed, starts http://127.0.0.1:8808/ and opens it
perceptron-p08-misconception-tutor/demo/smoke.sh          # headless check, exit 0 = pass
```
- Needs Python 3.11 and [uv](https://docs.astral.sh/uv/). If uv is missing, it falls back to `python3 -m venv` and pip.
- The first run installs `pydantic sympy numpy pandas pyarrow scikit-learn rank-bm25 requests pytest scipy`. After that the demo is offline, CPU only, and the server starts in about a second.
- Options: `--port N`, `--no-browser`, `--fetch` (below), `--local-text` (below).
- The talk track is in [SCRIPT.md](SCRIPT.md); screenshots in case live fails are in [fallback/](fallback/).

## Data notice (read this before presenting)
- Real items come from Kaggle's **"Eedi – Mining Misconceptions in Mathematics"** (2024). The licence is CC BY-NC 4.0, and competition rules §7.B forbid making the data available to anyone outside the competition.
- So **no Eedi item text** (questions, answers, distractors, or expressions parsed from them) appears in any committed file, screenshot or recording.
- `web/data.js` carries **derived outcomes only**: the item id, group (P/N/S), our pack code for the label, the engine's code, flags, each model's code per run, and tokens and cost. `smoke.sh` enforces a strict schema on it.
- Misconception names are **our own descriptions**. No Kaggle label text is shown.
- Live questions (tab 2) and the probability items (tab 3) are our own.

### Optional fetch step and local text (internal verification only)
- `run.sh --fetch` downloads the pinned public copies into the gitignored `.data/` (`eval/data/fetch.py`, checksummed):
  - the Kaggle data via the `cdtmc/eedi-ir` mirror;
  - the CC BY 4.0 Eedi Misconceptions Graph.

  The demo does **not** need them. Use them only to re-run `demo/export.py` or for local-text mode.
- `run.sh --local-text` shows item text from your local `.data/` copy and re-runs the engine live on the real items. It is **off by default**.
  - Text is read at runtime, kept in memory and never written.
  - A red banner marks the mode.
  - It is for internal verification only. **Never use it in front of judges**, in recordings or in screenshots.

## What is live and what is replayed
| Tab | What you see | Source |
|---|---|---|
| 1 · Real answers | Scoreboard, 304-square grid, marking slip, "ask it again" (runs 1–3) | Replayed: `eval/results/llm_gaps_real_negatives*.json(l)`, `llm_consistency*`, `llm_gaps_posthoc.json` |
| 2 · Predict my mistake | Certificate with step traces or no claim; ask again ×1,000; sealed sha256 prediction; set-level tracer; targeted practice; slip storm | **Live**: `demo/live.py`, built on committed components (`school_math`, `TemplateGenerator`, `SympyVerifier`, `SetBayesTracer`) |
| 3 · Cascade & budget | Cost and calls per 1,000 diagnoses, positives diagnosed, false claims; LLM unplugged; budget squeeze | Replayed per-item outcomes. Real items are **POST HOC**; on probability items routing is **guaranteed by construction** |
| 4 · Stress tests | Inversion, tracing, simulated learners, probability generation | **SYNTHETIC**, replayed from committed results |

Every headline string on screen comes from `eval/numbers.claims()` and is embedded at export. The page marks each knob value with ✓ when it equals a committed aggregate. The GATED cost is the exception: it depends on how the benchmark was built, so it is shown as "–" and left out of the budget choice.

## Files
| File | Role |
|---|---|
| `run.sh`, `smoke.sh`, `_venv.sh` | One command to run; headless smoke test; shared venv setup |
| `server.py` | Stdlib HTTP server on 127.0.0.1: static page plus a small JSON API for the live engine. Never calls an LLM |
| `live.py` | Live engine: certificate traces, follow-up generation, commit-reveal, tracer, slip storm, local-text verification |
| `export.py` | Rebuilds `web/data.js` from committed results (needs `.data/` once). Checks every aggregate before writing; `--check` compares with the committed file |
| `web/index.html`, `web/data.js` | The single page (vanilla JS and SVG, no CDN, no external libraries) and its derived-only data |
| `smoke.py` | The checks behind `smoke.sh` |
| `make_fallback.py`, `fallback/` | Offline standalone page and numbered screenshots, captured in no-text mode |

## Smoke test
`smoke.sh` starts the backend headless and checks the following.
- The data is derived-only, and its claims equal a fresh `eval.numbers.claims()`.
- The headline numbers re-derive from the per-item rows:
  - 0/152 false claims for the engine and GPT-5.5;
  - GPT-4.1-mini 24/152 (15.8%);
  - GPT-5.5 79.4% vs engine 19.1%;
  - $6.50 → $6.10 (real) and $7.32 → $5.08 (tutor-native);
  - 304/304 identical; GPT-5.5 changed 2 of 40.
- The live engine works:
  - certificates, no-claim answers, pairs;
  - 1,000 identical re-asks;
  - a sealed prediction verified by sha256, with one-time tokens;
  - a deterministic slip storm.
- `/api/real` is refused in no-text mode.
- Every $ and % number in `SCRIPT.md` and this README is a committed or live result.
- When `.data/` exists, it also runs local-text mode: the live engine on all 304 real items must equal the export (two passes identical), followed by a leak guard over every file in `demo/`.
