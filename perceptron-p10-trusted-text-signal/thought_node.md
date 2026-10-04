# Perceptron P10 · Trusting a signal extracted from messy, manipulated text — Thought Node

> Journal for `perceptron-p10-trusted-text-signal/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ▶ RESUMED 12:45 IST, 4 Oct (batch slot). Goal: finish to the Supervisor's definition of done, then send "DONE — slot free". The 12 Oct Perceptron pick is open between P7 (done), P9, P1 and P4; P10 enters late, so the memo must make an honest case for or against it.
- **Plan (definition of done, in order):**
  1. Finish the rubber-duck fixes with tests:
     - pump trust from `trust_of`; record ACI `stats`; richer plain-CQR oracle grid plus the guaranteed floor;
     - tests for trust deletion-stability, the ACI long-run bound and ACI boundary cases;
     - move the ratchet splits to 2014 only and re-baseline `results.tsv`.
  2. v1 reruns (`baseline_v1`, `text_minilm_v1`), committed with their commands.
  3. Answer "drop the text": pre-register a text-utility test and commit it *before* running, on data not yet looked at (candidate: the organisers' Kaggle "Daily News for Stock Market Prediction", DJIA 2008–2016, via a verified mirror). Then either show where text adds value or reframe the pitch around trust and coverage.
  4. Final Round-1 abstract rendered from committed results, a doc-drift check script, and the architecture diagram.
  5. Cross-model reviews as child sessions (PLAYBOOK §10, at most 2 at a time): `gpt-6-astra` (max) as hostile judge on the abstract and spike; `gpt-6-sol` (max) on code and eval, including reproducing the headline numbers. Record them in `reviews/` and `ledger.tsv`.
  6. Final selection memo, thought node current, everything pushed, then message the Supervisor.
- **Doing:** definition of done met, everything pushed. Only gpt-6-sol's verification of the v2 fixes, with a reproduction of `text_minilm_v2`, is still open; its file is recorded on arrival. Then "DONE — slot free" to the Supervisor.
- **Machine rules:** start heavy jobs only when `sysctl -n kern.memorystatus_level` ≥ 30 (pause below 25); always `nice -n 10`, one job at a time; CPU only; small requests; poll long jobs at ≥ 10-minute intervals; no FinBERT download (MiniLM is cached).
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section. Optional: a Kaggle API token (`~/.kaggle/kaggle.json`).
- **Risks:**
  - The "drop the text" critique: price-only matches fusion (pinball 0.3513 vs 0.3518). The pitch must not rest on alpha.
  - Threat model is injection-only.
  - The StockNet test period has been looked at several times, so the text-utility test needs unseen data.
  - Pooled Kupiec/Christoffersen p-values are optimistic.
  - Memory and uplink constraints slow the reruns.

## Key results — v2 (after the cross-model review fixes; reproduce commands in each report header)
Headline run: StockNet with the MiniLM scorer, [`eval/results/text_minilm_v2.md`](eval/results/text_minilm_v2.md); VADER: [`baseline_v2.md`](eval/results/baseline_v2.md). v1 was reproduced exactly by gpt-6-sol; the v1→v2 deltas are in [`v1_vs_v2_diff.json`](eval/results/v1_vs_v2_diff.json), and headline numbers are unchanged at reported precision. 87 tickers, 119,641 tweets, 0 tweets after the timestamp cut-off; test Jul 2015 → Mar 2016 (16,443 stock-days); α = 0.1. The abstract is rendered from these JSONs (`deliverables/render.py`, `deliverables/check_drift.py`).
- **Starter baseline is not meaningful:** MAPIE split CP covers 81.6% overall and 76.9% in high volatility (Kupiec p < 0.001). CQR 86.6%. ACI (our loop) 89.5%, day-clustered 90% CI 87.5–91.2%, width 5.22 pp. Seeds 0–2: ACI coverage sd 0.03 pp (`seed_stability_minilm.json`, v1 code).
- **Text value — none detected:**
  - StockNet (exploratory): pinball 0.3508 vs 0.3513; the text gain averaged over 3 seeds is −0.0002.
  - **Pre-registered unseen Kaggle DJIA** (registered at `dd8bcd1`): **no evidence that text adds value** (Winkler 3.524 → 3.520, +0.1%, p = 0.46). Qualification: the test conditions on the official open.
  - Exploratory pre-open variant: −0.6%, p = 0.73.
  - Positive control: detects +11.1% (p = 0.019), misses +3.9% (p = 0.11).
- **Attacks, k = 3 (symmetric CQR):**
  - The worst of 53 tested variants per row takes plain CQR to 84.7%. Certified ≥ the clean 86.7% on this test set (fixed offset).
  - Worst fixed variant: plain 85.7% vs certified 89.5%.
  - Beyond budget (10 posts): certified 86.9% vs plain 86.2%.
  - Certified width +4.8% (clean).
  - CR-ACI: 89.5% / 89.7% (clean / pump), +0.4% / +1.0% width vs plain ACI. Bursts on attacked days: plain ACI 89.5% vs CR-ACI 90.7%.
  - Per-row containment holds only at a fixed offset. Separately adapted ACI runs need not be nested (documented by a test).
- **C3 scorer** (macro-F1, 2,388 labelled financial tweets): VADER 0.489 · MiniLM+LR 0.691 · 20% / 40% flipped labels 0.662 / 0.606.
- **Soundness:**
  - 70 unit tests: brute-force box exactness; derived round-off margin with sol's 50,003-post counterexample as a regression test; tree bounds; trust stability; ACI long-run bound, boundaries and non-nesting; empty-interval scoring; scorer dispatch.
  - Clean features inside the attacked box on 100% of rows.
- **Cross-model reviews** (`reviews/`, `ledger.tsv`):
  - gpt-6-astra: 64/100 on the near-final abstract, with 5 blocking issues, all fixed.
  - gpt-6-sol: every headline number reproduced exactly; 3 blocking findings, all fixed.
  - A re-score and a fix verification are in progress.

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

**Assumptions (overnight, no user input):** A1 team = Ashish + up to two teammates TBD. A2 skeleton dataset = StockNet (tweets + prices, 88 US stocks, 2014–2015, MIT licence; its StockNet model is a victim in the published tweet-concatenation attack, Xie et al. 2022); FNSPID news (KDD 2024) as the long-history set for regime shifts later. A3 target = next-day close-to-close log return per ticker; information set = documents timestamped before that day's close (America/New_York). A4 α = 0.1 primary (also 0.05, 0.2). A5 strictly time-ordered train → calibration → test splits.

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
- 2026-10-04 — Skeleton dataset = StockNet (tweets + user metadata + prices; MIT; its StockNet model is a victim in Xie et al. 2022 — that the attack used this exact dataset is UNVERIFIED). FNSPID news for the finals (stream-filtered). Kaggle set not used (no credentials).
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
_FINAL (v3), 4 Oct 2026 ~13:50 IST. Supersedes v1 (07:50) and the v2 draft. Every number is in `eval/results/` and is checked by `deliverables/check_drift.py`. The pick is open between P7 (done), P9, P1 and P4; P10 enters late, so this is the honest case._
- **Independent score:**
  - gpt-6-astra hostile judge (official rubric), on the near-final abstract: **3.20/5 (64/100)** — "plausible reserve-list candidate, not a comfortable top-25–30 choice"; 5 blocking issues, all fixed in v2.
  - Re-score of the final abstract (v2): **3.70/5 (74/100)**. 0 former blockers unresolved; 1 new (reproduction wording), fixed.
  - For comparison (from their memos): P7 71/100, P9 62/100, P1 3.40/5 (68/100, earlier version).
- **Winnability — 3.5.**
  - For: evidence discipline. A registered null on unseen data, with a positive control showing the test's power; an exact certificate unit-tested against brute force, with a derived round-off margin; the v1 results independently reproduced (gpt-6-sol). It also shows the organisers' starter baseline is not meaningful: MAPIE split CP 81.6%, 76.9% in high volatility. Round 1 is judged on the plan, and the final abstract scores 74/100 with the hostile judge.
  - Against: the pre-registered test found **no evidence that text adds value** (Winkler +0.1%, p = 0.46; pre-open variant −0.6%). The fusion the problem asks for is a formality on our data, so the pitch rests on "trust and coverage guarantees for an untrusted channel". That caps the finals story.
- **Innovation headroom — 3.** The independent judge also gave 3. Robust conformal is specialised to document-injection budgets through tractable deletion ranges and tree propagation. Close prior art (VRCP, RCP1, Zargarbashi et al. ICML 2024) makes it a specialisation, not a new principle. The measured payoffs are small because the exposure is small: the oracle takes plain CQR to 84.7% vs a certified floor of 86.7%, and CR-ACI ≈ ACI.
- **Feasibility — 5.** Built and reproduced, with 70 tests; CPU-only, about 1–4 min per run. Data is free and hash-pinned. The edit budget and FNSPID pre-registration fit before 17 Nov.
- **Demo strength — 3.** An attack toggle and k slider are easy to build. The visible effect is ≈ 2 pp of coverage, and the honest headline ("text did not help") is not a crowd-pleaser.
- **Fit with the user's strengths — 4.** Evaluation rigour, guarantees and systems; deliberately little frontier-model work (LLM scorers risk look-ahead).
- **Overall: 3.7/5** (unweighted mean: 3.5 + 3 + 5 + 3 + 4 = 18.5).
- **Biggest risk:** "If the text doesn't help, what are we trusting?" The answer is a channel-admission audit with a guarantee, which is honest but caps the ceiling. Moving to event-driven, news-rich data (FNSPID earnings news) is where text should matter: a hope, not evidence.
- **Recommendation: a close second to P7, and the Theme-6 pick over P9.**
  - On the abstract, P10's final hostile score (74/100) is the highest of the memos I could read: P7 71, P1 68 (earlier version), P9 62. Those come from separate review runs, so gaps of a few points are within reviewer noise.
  - For the finals, P7's effect size and demo are stronger (1.4 vs 39.6 requests lost in its surge replay), whereas P10's visible effect is ≈ 2 pp of coverage plus a guarantee. So I'd still pick **P7 first**, with P10 a close second.
  - Choose P10 if the user values a rigorous, guarantee-centred Round-1 plan, and a deliberately honest negative result, over a large demo effect.
  - Either way, P10's reusable assets transfer: the pre-registration plus positive-control pattern, the render/drift tooling and the certified-interval code.
- **One-line pitch:** "A 90% band you can still trust when someone floods the feed with fake posts — certified for a stated budget, tested on unseen data, and honest that the text itself added nothing measurable."

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

### 2026-10-04 08:09–08:28 IST — Self-audit + ratchet re-check
- **Ratchet:**
  - h2 (robust-only text features) improved only −0.33% vs h1, below the threshold → not kept.
  - h3 (ACI γ = 0.005) was worse → not kept.
  - Lead test-period re-check of h1 (`eval/recheck_ratchet.py`): clean width 5.240 vs baseline 5.233. The validation gain did not transfer → reverted. Keep rule is now mean of 3 seeds, >1%.
  - Lesson: single-seed differences under ~1% are noise here.
- **Self-audit fixes (wording only; no numbers changed):**
  - Abstract: StockNet's *model* is a victim in Xie et al.; that the attack used this exact dataset is unverified.
  - Robust-CP prior art also covers poisoning and sparse edits (ICML 2024).
  - Results caveat: the 12-variant oracle is not a worst-case bound for plain CQR. The certified floor (clean CQR coverage) holds for every attack within budget.
- Added `research/components/robust_conformal.md` (exactness proofs) and `text_scorer.md`, both referenced from code.

### 2026-10-04 08:30–10:05 IST — Lean mode lifted, review, pause
- Supervisor 08:22: package accepted; next steps were FinBERT, an independent antithesis, and social signal.
  - **Social signal:** R7 agent wrote `research/notes/R7-social-signal.md`. HN skeptic takes: sentiment may lag price; LLM signals are "weaponisable"; conformal's guarantee rests on exchangeability. Reddit returned 403; `site:x.com` returned nothing.
  - **FinBERT:** the HF CDN measured ~30 KB/s (curl probe), so 440 MB was not viable. Used MiniLM-L6 (already cached locally) plus a logistic-regression head trained on Twitter Financial News Sentiment (HF zeroshot, MIT): macro-F1 0.691 vs VADER 0.489. Noisy-label stretch: 20% / 40% flipped labels → 0.662 / 0.606.
  - **Independent antithesis:** the rubber-duck review found 3 blocking issues — trust not deletion-stable, ACI clipping/reordering, the "per-prediction coverage" overclaim — plus evaluation flaws and a strong "drop the text" case. Saved with the lead's synthesis in `research/notes/review-adr001-rubber-duck.md`. Fixed in code: trust, ACI, contract, evaluator v1, vectorised box (43 tests pass). Fixed in the abstract: three overclaims. The rerun is the resume point.
- Supervisor 09:40: lean mode back on. Supervisor 09:55: **PAUSE** (user's decision). No jobs running; all results saved; exact restart commands are in *Now*.

### 2026-10-04 12:45–13:10 IST — Resumed: review fixes, v1 reruns, pre-registered text test, final abstract
- **Supervisor 12:45:** RESUMED with a definition of done. Acted on: Now rewritten; steps 1–4 done; step 5 running.
- **Fixes (59 tests pass):**
  - pump trust from `trust_of` (fresh account → 0.101), and the pump sentiment from the deployed scorer;
  - ACI `stats`; 53-variant oracle grid plus guaranteed floor plus burst attack;
  - evaluator v1 adds a day-block CI;
  - ratchet evaluator v2 (2014-only splits), re-baselined.
- **Found a macOS segfault:** a torch forward pass followed by multithreaded LightGBM (OpenMP clash; bisected with `python -u`). Fix: MiniLM encodes uncached texts in a child process whenever LightGBM is loaded.
- **v1 reruns:**
  - `baseline_v1` (VADER) and `text_minilm_v1` (MiniLM), each ~1 min now that memory has recovered.
  - The richer grid lowers plain-CQR oracle coverage (84.1% VADER / 84.7% MiniLM vs v0's 84.4% from 12 variants), as the review predicted.
- **"Drop the text":**
  - Pre-registered at `dd8bcd1` (12:55:28 IST) before any run on unseen Kaggle DJIA data (mirror verified by blob hash, Yahoo closes, label consistency).
  - Result: **no evidence that text adds value.**
  - Exploratory: the price-only IC of 0.355 comes from the overnight gap continuing into the open-to-close return (Spearman 0.40). This fits stale index opens (mechanism UNVERIFIED) and affects both arms equally.
- **Reframed the pitch** around trust and coverage guarantees plus a text gate.
- **Final abstract:** rendered from committed JSONs (813 words, tables included); `check_drift.py` passes. Architecture diagram, ADR 001 and components.md updated.
- **Step 5:** launched cross-model reviewers as child sessions: gpt-6-astra (max) as hostile judge on abstract and spike; gpt-6-sol (max) on code and eval plus reproduction.

### 2026-10-04 13:10–13:55 IST — Cross-model reviews, v2 fixes, final abstract and memo
- **gpt-6-astra** (hostile judge, max) on the near-final abstract and spike: 3.20/5 (64/100), 5 blocking issues.
- **gpt-6-sol** (code/eval, max): all 8 requested headline numbers, and every non-timing leaf of the three headline JSONs, reproduced exactly. 3 blocking findings:
  - B1: per-row containment does not survive separately adapted ACI runs;
  - B2: a 50,003-post constant-sentiment day escapes the fixed-ε box;
  - B3: the DJIA "tradeable at the open" claim conflicts with the gap features.
  - Plus 2 non-blocking (N1 empty-interval scoring, N2 FinBERT pump dispatch).
- **All 18 items accepted, none rejected** (decisions under each review; `reviews/ledger.tsv`). Fixes:
  - derived round-off margin, centred sums and a document cap in `deletion_box`;
  - fixed-offset-only containment wording, with a non-nesting test;
  - empty intervals excluded from width/Winkler and counted;
  - explicit scorer dispatch;
  - beyond-budget attacks;
  - DJIA qualified as conditional on the open, with exploratory pre-open (null) and positive-control (power) runs;
  - abstract wording (leakage, novelty, admission rule, milestones incl. 15 Oct / 30 Oct, no invented teammates);
  - 1/m in the variance proof;
  - price-only is no longer called k = ∞.
  - Tests: 70.
- **v2 reruns** (`baseline_v2`, `text_minilm_v2`): headline numbers unchanged at reported precision; v1→v2 deltas committed (no-text days got tighter because v1's margin straddled thresholds at 0). Ratchet re-baselined (SCORE 4.566). Prior-art search log completed (R2 §2.5).
- **Final abstract:** v2, 890 words, rendered and drift-checked. astra re-score **3.70/5 (74/100)**: 0 former blockers left; 1 new wording blocker, fixed.
- **Final selection memo:** P7 first, P10 a close second (best hostile abstract score among the memos read, but a weaker finals story), and the Theme-6 pick over P9.
