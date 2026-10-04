# ADR 001 — Spike: certified manipulation-robust conformal intervals (CR-ACI)

- **Status:** accepted (lead, 4 Oct 2026 07:30 IST). Revisit at the 12 Oct selection gate.
- **Context:** the brief asks for a fusion signal with a *meaningful* confidence bound, and names robustness to manipulated text and real calibration as stretch goals. Most teams will ship FinBERT + MAPIE split CP and report one coverage number. Overnight lean mode meant no independent rubber-duck agent; the antithesis below is lead-written and must be re-run by an independent reviewer before 12 Oct.

## Candidates (scored 1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasible by 15 Dec | Scalar metric | Demo | Total |
|---|---|---|---|---|---|---|
| **A. CR-ACI** — interval valid for every attack injecting ≤ k documents, + ACI for drift (C10) | 5 | 4 — closest prior: Zargarbashi et al. ICML 2024 bound worst-case conformity-score change; VRCP handles regression; none found for document budgets on text→time-series ([landscape](../../research/landscape.md) §2) | 5 — runs tonight | 5 — width at certified coverage | 5 — slide k, toggle an attack, watch the band | **24** |
| B. Learned manipulation / bot detector (C4) | 3 | 2 — well-trodden | 4 | 4 — AUROC | 3 | 16 |
| C. Text-driven width + regime-conditional conformal (C7/C8) | 4 | 3 — conditional CP exists (MAPIE 1.5) | 4 | 5 | 3 | 19 |
| D. LLM text scorer (C3) | 2 — literature shows little gain; look-ahead risk | 1 | 3 | 4 | 3 | 13 |

**Decision:** A is the spike. C is the secondary track and the first ratchet target (shrink CR-ACI width while keeping certification). B and D stay best-practice and swappable behind the contracts.

## How CR-ACI works (one paragraph)
The defender sees the observed documents D′ of a ticker-day. If an adversary injected at most k of them, the clean set is D′ minus ≤ k documents, so the clean text-feature vector lies in the *deletion box* B_k(D′). Each feature's exact range over B_k is cheap because the aggregator is order-statistic based (trimmed mean, mean, std via contiguous/prefix-suffix subsets, count, trust mean). We bound each LightGBM quantile model over the box by propagating intervals through every tree, and output `[LB − q_t, UB + q_t]`, where q_t is the CQR correction updated online by ACI. **Guarantee:** for any attack within budget, the certified interval contains the interval the clean model would have produced, so it covers whenever the clean CQR/ACI interval covers; ACI adds long-run coverage under drift. Prices are assumed unmanipulated; editing a document (delete + insert) is the next extension.

## Six Thinking Hats
- **White (facts, committed run `eval/results/baseline_v0.json`):** see the numbers table in [`eval/results/baseline_v0.md`](../../eval/results/baseline_v0.md). Split CP under-covers in the H2-2015 / Q1-2016 test period and worst in the high-volatility tercile; ACI restores marginal coverage; text adds ~nothing to point accuracy; the oracle attack lowers vanilla CQR coverage while the certified interval keeps it at or above the clean level for a few percent more width.
- **Red (gut, judges):** Optiver quants respect explicit threat models and a "price of robustness" curve; it reads as rigorous rather than buzzy, and the live demo is visceral.
- **Black (risks):** (1) threat model covers injection only, not edits, deletions/suppression or true-but-misleading news; (2) the certificate is relative to the clean interval, which itself breaks under regime shift — hence ACI; (3) per-feature boxes ignore coupling and can be loose as features grow; (4) when the model hardly uses text, robustness is cheap and a judge may say "so drop the text"; (5) tree propagation is model-specific (neural fusion would need IBP/CROWN); (6) pooled Kupiec/Christoffersen p-values ignore same-day correlation.
- **Yellow (benefits):** exact, millisecond certificates; composes with any conformal method; turns "robust" into one number k; explains which documents could flip the forecast; maps straight onto both stretch goals.
- **Green (alternatives):** edit budgets (replace ≤ k documents with any value in [−1, 1]); a two-tier budget (k_any for metadata-mimicking attackers, larger k for low-trust accounts only); certify the trading decision ("interval excludes 0") instead of the interval; monotone constraints on text features for tighter bounds; regime-conditional calibration (MAPIE `ConditionalSplitConformalRegressor`).
- **Blue (process):** ratchet metric = mean CR-ACI width at k = 3 on a pre-test validation window, penalised if clean or attacked coverage < 0.895 (`components/robust_conformal/autoresearch/eval.py`, frozen); the lead re-checks kept changes on the untouched test period.

## Thesis → antithesis → synthesis
- **Thesis:** robustness and calibration are usually two separate experiments; making robustness a *coverage guarantee under a stated attack budget* unifies both stretch goals and gives "meaningful" an operational definition.
- **Antithesis (lead-written; independent review pending):** the attacker need not respect k; a model that ignores text is trivially robust ("you certified a model that ignores its input"); ACI already guarantees long-run coverage on arbitrary — even adversarial — sequences, so why certify; k looks arbitrary.
- **Synthesis:** report coverage as a curve over the attacker's *actual* budget, including beyond k (graceful degradation); the price-of-robustness curve is the honest measure of what the text channel is worth versus its attack surface, and the ratchet tries to make text more useful (better scorer, attention → volatility) without widening the certified band; ACI's guarantee is a long-run average that an attacker can concentrate on the days they trade, while the certificate is per prediction — hence CR-ACI combines them; choose k from data (e.g. the 95th percentile of daily copy-paste cluster size) and always show the k = 0…5 curve.

## First principles
The bottleneck is not sentiment accuracy. Conformal validity is a statement about the *calibration distribution*; an attacker controls the *test input*. The minimal fix that restores validity is to make the interval a function of the set of inputs that could have been the clean one, not of the observed input. Better scorers and trust weights can shrink that set or the width, but cannot by themselves restore validity.

## Consequences
- C5 aggregators and C7 features must each come with an exact deletion-range rule (enforced in `certify.py`).
- C7 stays a tree ensemble (or monotone/linear) until a neural verifier is added.
- The eval harness reports clean, pump and oracle coverage for every method, plus width at k = 0…5.

## Update — 4 Oct 2026, ~13:05 IST (v1)
- **Independent antithesis done** (rubber-duck review, saved with per-item decisions in `research/notes/review-adr001-rubber-duck.md`). Its three blocking findings are fixed and tested:
  - trust is now computed from each post's own metadata (deletion- and injection-stable);
  - the ACI loop now matches Gibbs & Candès (no clipping, whole line at α_t ≤ 0, empty set at α_t ≥ 1, long-run bound tested on adversarial sequences);
  - the claim is restated as interval containment: an attacker within budget cannot add misses, i.e. certified coverage under attack ≥ the clean coverage.
- **Its evaluation critiques are addressed:**
  - a 53-variant oracle grid (mixed and intermediate attacks) plus the guaranteed floor;
  - burst attacks on pre-specified days;
  - day-clustered confidence intervals;
  - ratchet splits moved inside 2014.
- **"Drop the text" was tested, pre-registered, on unseen data** (Kaggle DJIA news; `eval/preregistration/2026-10-04-text-utility-djia.md`). Result: no evidence that text adds value (Winkler +0.1%, p = 0.46).
- **Consequence for the decision:** CR-ACI stays the spike, but the framing changes from "robust text alpha" to "trust and coverage guarantees for an untrusted text channel". The price-of-robustness curve plus the text-utility test form a *text gate*: admit text only if it earns its certified width, with dropping text as the k = ∞ end. On current data the insurance is cheap (+0.3% width with ACI on StockNet/MiniLM) because the exposure is small.
- Cross-model reviews (PLAYBOOK §10) are in `reviews/`, with decisions in `reviews/ledger.tsv`.
