# Perceptron P10 · Trusting a signal extracted from messy, manipulated text — Thought Node

> Journal for `perceptron-p10-trusted-text-signal/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** morning package delivered (Phases 0–5 v0). Next: re-verify research gaps, FinBERT scorer, edit-budget certificate, FNSPID subset.
- **Plan:** (1) 4–12 Oct: fill research gaps (social signal, SEBI/SEC, detectors, Kupiec/Christoffersen primaries) + independent rubber-duck review of ADR 001 + final selection memo by 12 Oct; (2) FinBERT/finbert-tone scorers behind the C3 contract; (3) edit-budget (replace ≤k docs) certificate; (4) FNSPID stream-filtered news subset 2018–2023 as the finals test; (5) ratchet loops on CR-ACI width.
- **Doing:** first ratchet batch on the frozen spike evaluator: h1 (drop `sent_std`) kept provisionally (SCORE 4.454 → 4.427, −0.6%); h2 (robust-only text features) and h3 (ACI γ = 0.005) running. No sub-agents (Supervisor lean mode until 08:30, then ≤ 3 concurrent).
- **Next:** log ratchet results → rubber-duck review of ADR 001 when agents are allowed again → research gap pass → FinBERT weights (~440 MB) once downloads are allowed.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section (the abstract has TBD roles). Optional: a Kaggle API token (`~/.kaggle/kaggle.json`) if we want the organisers' "Kaggle news + price" set as an extra baseline.
- **Risks:** text adds ~no point accuracy (measured: pinball 0.3518 fusion vs 0.3513 price-only) → pitch rests on trust/coverage, not alpha · threat model is injection-only (edits next) · split methods under-cover in the 2015–16 test regime (measured) · pooled Kupiec/Christoffersen p-values are optimistic · ADR 001 antithesis is lead-written (independent review pending) · research notes are partial (agents died on 408s; gaps listed in landscape §7).

## Key results (committed; reproduce: `bash eval/fetch_data.sh && PYTHONPATH=. .venv/bin/python eval/prepare.py && PYTHONPATH=. .venv/bin/python eval/run_baselines.py`)
StockNet, 87 tickers, 119,641 tweets, look-ahead leaks 0; test 2015-07-01→2016-03-31 (16,443 ticker-days); α = 0.1. Full table: [`eval/results/baseline_v0.md`](eval/results/baseline_v0.md).
- Fusion + split CP (MAPIE): coverage 81.3%, high-vol tercile 76.5%, Kupiec p < 0.001 → "present but not meaningful".
- Fusion + CQR (MAPIE): 86.3%, width 4.71 pp; + ACI: 89.4%, width 5.22 pp.
- Oracle injection attack, k = 3: plain CQR 86.3% → 84.4%; **certified CQR 88.0%** (width +4.5%). Pump attack: CQR 85.5% vs certified 88.8%.
- **CR-ACI (spike): 89.5% clean / 89.7% under pump, width 5.23 pp (+0.3% vs plain ACI).**
- Soundness: degenerate-box error 0; clean features inside the attacked box on 100% of rows; own CQR = MAPIE symmetric CQR exactly.

## Phase 0 — what the judges must be able to see (lead, 4 Oct 03:00 IST)
**The crux in our words.** Three things interact: (1) the text signal is weak and noisy, and probably says more about *how much* a price will move than *which way*; (2) daily returns are not exchangeable (volatility clustering, regime shifts), so a split-conformal interval is valid only on average and can under-cover exactly when it matters; (3) an adversary who injects or edits text moves the input at test time, which no standard conformal guarantee covers — the interval can be narrow, shifted and confidently wrong. "Meaningful" therefore has to be operationalised, not asserted.

**"Meaningful bound" — our operational definition (drives the eval harness):**
1. *Valid:* long-run coverage ≈ 1−α on a time-ordered held-out period (Kupiec unconditional-coverage test).
2. *Conditionally valid:* coverage holds within regimes (volatility tercile, text-volume tercile, attacked vs clean) and misses are not clustered in time (Christoffersen independence test).
3. *Efficient:* smallest width at that validity (mean width, Winkler interval score).
4. *Robust:* coverage degrades gracefully, and provably within a stated budget, when up to k documents per ticker-day are adversarial.
5. *Useful:* the interval changes a decision for the better (e.g. act only when the interval excludes zero) — secondary, economic sanity check.

| Criterion (weight) | Evidence we must show |
|---|---|
| Problem understanding (20%) | The three-part crux above, with citations for weak text→direction signal and non-exchangeable returns |
| Technical soundness (25%) | Named models/tools/datasets; time-ordered splits; no look-ahead (timestamp alignment test); runs on an M5 |
| Innovation (20%) | A spike beyond "FinBERT + MAPIE": manipulation-aware conformal layer (see ADR 001 once written) |
| Clarity (10%) | One diagram; every claim tied to a metric |
| Evaluation rigor (15%) | Baselines (price-only, text-only, fusion × split CP / CQR / ACI); coverage, width, Winkler, Kupiec, Christoffersen; conditional coverage; attack budgets |
| Team fit (10%) | Week-by-week plan around the 19–25 Nov exams; teammates' skills (needs user) |

**Assumptions (overnight, no user input):** A1 team = Ashish + up to two teammates TBD. A2 skeleton dataset = StockNet (tweets + prices, 88 US stocks, 2014–2015, MIT licence; the benchmark used by published tweet-injection attacks); FNSPID news (KDD 2024) as the long-history set for regime shifts later. A3 target = next-day close-to-close log return per ticker; information set = documents timestamped before that day's close (America/New_York). A4 α = 0.1 primary (also 0.05, 0.2). A5 strictly time-ordered train → calibration → test splits.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 10 — Trusting a Signal Extracted from Messy, Manipulated Text** (Theme 6: AI You Can Actually Trust — teams choose Problem 9 or 10)
- **Context:** Decisions increasingly lean on signals from unstructured text alongside numeric data, but that text is noisy and sometimes manipulated.
- **Challenge:** Fuse text and time-series data into one signal and report a confidence bound on each prediction that's meaningful.
- **Starter resources:** A public financial news + price dataset (widely available on Kaggle), plus an existing conformal prediction library (e.g. MAPIE) instead of building calibration machinery from scratch.
- **Minimum Viable:** build a fusion model combining text sentiment and time-series signal; wrap predictions with an off-the-shelf conformal prediction method for confidence bounds.
- **Stretch goals:** test robustness under one adversarial or noisy-label scenario; check whether the confidence bounds are actually well-calibrated, not just present.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: FNSPID (financial news + stock prices), Kaggle "Daily News for Stock Market Prediction".
- Text models: FinBERT, FinGPT, LLM embeddings; fusion via late fusion or temporal models (e.g. TFT).
- Conformal under distribution shift: MAPIE, EnbPI, adaptive conformal inference (ACI / AgACI), conformal PID control.
- Manipulation and noise: adversarial text perturbations (TextAttack), bot/pump text, source-credibility weighting; calibration diagnostics (coverage, interval width, conditional coverage by regime).
- What companies ship: alternative-data and news-signal products from data vendors and quant funds (public material).

## Key decisions
- 2026-10-04 — Skeleton dataset = StockNet (tweets + user metadata + prices; MIT; the benchmark attacked by Xie et al. 2022). FNSPID news for the finals (stream-filtered). Kaggle set not used (no credentials).
- 2026-10-04 — Target = next-day close-to-close log return (%); information cut-off 16:00 America/New_York; strictly time-ordered train 2014 / cal H1-2015 / test Jul-2015→Mar-2016.
- 2026-10-04 — Text scorer tonight = VADER + finance lexicon (FinBERT weights >200 MB, deferred under lean mode); scorers must not be able to recall outcomes (look-ahead bias, arXiv:2512.23847).
- 2026-10-04 — **Spike = CR-ACI** (certified manipulation-robust conformal + ACI); secondary track = text-driven width / regime-conditional conformal. [ADR 001](architecture/adr/001-spike.md).
- 2026-10-04 — Fusion model = LightGBM quantile regression (tree ensembles make the certificate exact and cheap).

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | ingest | files → DOCS, BARS | StockNet loaders | | ✅ running | rows parsed, contract pass |
| C2 | align | DOCS → ALIGNED_DOCS | 16:00 ET cut-off | | ✅ 0 leaks | look-ahead leaks (=0) |
| C3 | text_scorer | → SCORED_DOCS | VADER+lexicon; FinBERT wrapper | | ✅ VADER / ⏳ FinBERT | macro-F1 on labelled tweets; IC |
| C4 | trust_scorer | → TRUSTED_DOCS | heuristic | | ✅ | AUROC injected vs real |
| C5 | aggregator | → TEXT_FEATURES | trimmed mean etc. | | ✅ | worst-case shift under k |
| C6 | ts_features | BARS → TS_FEATURES | lags, RV, Parkinson | | ✅ | pinball (price-only) |
| C7 | fusion | → PREDICTIONS | LightGBM quantiles | | ✅ | mean pinball, IC |
| C8 | conformal | → INTERVALS | MAPIE split/CQR + ACI | | ✅ | \|cov−0.9\|, width |
| C9 | attack | DOCS → DOCS | pump, oracle (k) | | ✅ | coverage drop, median shift |
| C10 | robust_conformal | → INTERVALS | deletion box + tree propagation + ACI | **spike** | ✅ v0 + ratchet | width at certified coverage |
| C11 | eval (frozen) | INTERVALS → metrics | coverage, width, Winkler, Kupiec, Christoffersen | | ✅ | — |
| C12 | decision / demo | INTERVALS → UI | — | | ⏳ | hit rate of "interval excludes 0" |

## Selection memo
_v1, 4 Oct 07:50 IST (final by 12 Oct). Scores 1–5 with evidence._
- **Winnability: 4** — the crux (weak text + non-exchangeable returns + test-time manipulation) is precisely identified and already measured on real data; most teams will ship FinBERT + MAPIE split CP, which our own run shows under-covers (81.3%; 76.5% in high volatility). Same theme as P9, so compare those two memos directly.
- **Innovation headroom: 4** — CR-ACI certifies coverage against a budget of k injected documents (oracle attack k = 3: plain CQR 84.4% vs certified 88.0%; CR-ACI 89.5–89.7% at +0.3% width). Prior-art searches found robust conformal only for ℓp/smoothing noise on single inputs (closest: Zargarbashi et al. ICML 2024; VRCP NeurIPS 2024); independent novelty review still pending.
- **Feasibility: 5** — the full pipeline already runs end-to-end on the M5 (data prep 35 s; full evaluation incl. oracle attack 10–31 min); data on disk; MAPIE/LightGBM only. Exam window needs only automated runs.
- **Demo strength: 4** — live band per stock-day with an attack toggle and a k slider, plus "which posts could flip this forecast". Point forecasts are unimpressive (text adds ~no accuracy), so the demo must sell trust, not alpha.
- **Fit with the user's strengths: 4** — systems + frontier models map to LLM/FinBERT scorers with look-ahead tests, streaming FNSPID, verification-style bounds; needs less quant-microstructure depth than P4–P6.
- **Biggest risk:** judges may ask "why fuse text at all?" — measured fusion ≈ price-only on accuracy. Answer: the price-of-robustness curve shows what text costs and buys; finals data (FNSPID news) and FinBERT may raise its value. Second risk: injection-only threat model (edit budget planned).
- **One-line pitch:** a news-plus-price signal whose 90% band stays 90% when someone floods the feed with fake posts — and that tells you how many fake posts it can survive.

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05 IST — Phase 0 + research fan-out
Read PLAYBOOK, brief, official statement. Wrote the crux, the operational definition of "meaningful" and the evidence map (above). Launched 7 research agents (R1 conformal-TS, R2 robust CP, R3 fusion, R4 manipulation, R5 companies, R6 datasets, R7 social). Verified data access: StockNet (MIT, 68 MB repo, 664 MB on disk) cloned; FNSPID sizes read from the HF API (5.7 + 23 GB news). Disk has ~69 GB free, RAM 24 GB.

### 2026-10-04 02:57–05:04 IST — Network failures
Most agents died with "408 Timed out reading request body" and no output; relaunched R1/R2/R3/R4/R5/R6 with crash-safe incremental writing. Partial notes R1–R6 saved to `research/notes/` and committed; R7 (social signal) produced nothing.

### 2026-10-04 05:49 IST — Supervisor lean mode (Inbox via message)
Acted: no new sub-agents, small outputs, no >200 MB downloads. Stopped the FinBERT weights download (~440 MB) and switched C3 to VADER + finance lexicon. No reply needed.

### 2026-10-04 06:20–07:36 IST — Walking skeleton + eval, real numbers
Built contracts + 10 components + frozen metrics. Panel: 87 tickers, 119,641 tweets, 0 look-ahead leaks, 48,711 ticker-days. First run found one box-soundness violation of 7.5e-9 (float round-off in prefix-sum std) → widened boxes by 1e-6; rerun: 100% inside. Results in Key results above; `eval/results/baseline_v0.{json,md}`. Learned: split CP is not meaningful in the 2015–16 regime; ACI is needed; text adds ~no accuracy; the certificate costs +4.5% width alone, +0.3% when combined with ACI.

### 2026-10-04 07:10–07:50 IST — Morning package
Lead re-verified the top citations (arXiv API: 2406.16964, 2506.16553, 2601.13082 incl. "17.7 percentage points", 2512.23847, 2602.03168; AdvFinTweet README "$3200 (32%)"). Wrote `research/landscape.md`, `architecture/components.md`, `architecture/adr/001-spike.md`, `deliverables/round1-abstract.md` (831 prose words + milestone table), `deliverables/architecture.md`, ratchet scaffold (`components/robust_conformal/autoresearch/`, baseline SCORE 4.45448), selection memo v1. Supervisor 07:22 alignment message: agreed (no reply needed); no number depends on models.github.ai.

### 2026-10-04 07:50–08:05 IST — Tests, ratchet, gate message
Added `tests/` (43 pass): DST-safe 16:00 ET alignment, contract rejection, brute-force check that the deletion box is sound and exact (40 random cases, all deletions of ≤ k docs), tree-bound soundness on sampled points. Fixed a bug where `CertifiedCQR` assumed every text feature was in the model; committed results used the full feature set, so they are unaffected. Ratchet h1 (drop `sent_std`) passed the keep rule (−0.6%, coverages 90.8% / 91.2%); single seed, so the test-period re-check is pending. Supervisor 07:47 final call acted on: memo filled, Now/Log refreshed, everything pushed. Messaged the Supervisor that selection memo v1 is ready (gate deliverable).
