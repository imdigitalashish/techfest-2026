# Methods state of the art: trading confidence against latency

Accessed 2026-10-04

Scope: Problem 6 spike: rank cross-asset mispricings by executable edge, signal confidence, and probability the edge survives our latency. I cite only sources opened during this session; items I could not open are in **UNVERIFIED leads**.

## 1) Summary table

| Area | Source opened | Maturity | Specific claim/formula taken |
|---|---|---:|---|
| Latency valuation | **OR Forum—The Cost of Latency in High-Frequency Trading** — Ciamac C. Moallemi, Mehmet Sağlam, 2013, *Operations Research*. DOI/Crossref: https://api.crossref.org/works/10.1287/opre.2013.1165 | journal paper | Latency is a trading friction; the paper models an optimal-execution problem and gives a closed-form latency cost in terms of asset parameters. Crossref abstract reports NYSE 1995–2005 median latency cost roughly tripled and implied latency fell about two orders of magnitude. |
| Shadow price / fill ratio | **The shadow price of latency: improving intraday fill ratios in foreign exchange markets** — Álvaro Cartea, Leandro Sánchez-Betancourt, 2021, *SIAM Journal on Financial Mathematics*. ORA: https://ora.ox.ac.uk/objects/uuid:7a1ff3ab-cc0b-4bc9-a4f0-2f8264c0d470 | journal paper + ORA PDF link | Liquidity takers face a moving-target problem: by the time an order reaches the exchange, quotes/quantities may have worsened or improved. They derive a latency-optimal limit-price strategy balancing walking-the-book cost vs a target fill ratio; shadow price = cost a trader would pay to reduce latency. |
| Stochastic-delay execution | **Optimal execution with stochastic delay** — Álvaro Cartea, Leandro Sánchez-Betancourt, 2022/2023, *Finance and Stochastics*. ORA: https://ora.ox.ac.uk/objects/uuid:0d0f5939-6ca2-4e14-91b9-f03361afcb31 | journal paper + ORA PDF link | Models marketable limit orders (MLOs) as impulse control with stochastic latency; trader controls send times and price limits. Impatient takers may walk the book to raise fill probability; patient takers use speculative MLOs that fill only after favorable moves. |
| Delay-aware RL | **Model-Based Reinforcement Learning under Random Observation Delays** — Armin Karamzade, Kyungmin Kim, JB Lanier, Davide Corsi, Roy Fox, 2025, arXiv. https://arxiv.org/abs/2509.20869 | paper-only | Random observation delays in POMDPs; observations can arrive out-of-sequence. Naive stacking is insufficient; model-based filtering updates a belief state from incoming observations and improves robustness to delay distribution shifts. |
| Delay-aware RL | **Reinforcement Learning from Delayed Observations via World Models** — Armin Karamzade, Kyungmin Kim, Montek Kalsi, Roy Fox, 2024, arXiv. https://arxiv.org/abs/2403.12309 | paper-only | Reduces delayed POMDPs to delayed MDPs with world models; one method outperforms a naive model-based approach by up to 250% in their experiments. |
| Delay-aware RL | **Delay-Aware Model-Based Reinforcement Learning for Continuous Control** — Baiming Chen, Mengdi Xu, Liang Li, Ding Zhao, 2020, arXiv. https://arxiv.org/abs/2005.05440; code: https://github.com/baimingc/dambrl | paper + code | Defines delay-aware MDP and states it can be transformed to a standard MDP with augmented states; incorporates multi-step action delay into learned models. |
| Delayed-observation regret | **Minimax Optimal Strategy for Delayed Observations in Online Reinforcement Learning** — Harin Lee, Kevin Jamieson, 2026, arXiv. https://arxiv.org/abs/2603.03480 | paper-only | For tabular MDPs with random delayed state observation, regret bound \(\tilde O(H\sqrt{D_{\max}SAK})\), explicitly depending on max delay. |
| CUSUM design | **NIST/SEMATECH e-Handbook, CUSUM V-mask example**. https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm | official methods docs | Given false-alarm \(\alpha\), miss \(\beta\), desired shift \(\delta\), NIST gives \(k=\delta\sigma_x/2\), \(d=2\delta^{-2}\ln((1-\beta)/\alpha)\), \(h=dk\). |
| OU optimal stopping | **Optimal Mean Reversion Trading: Mathematical Analysis and Practical Applications** — Tim Leung, Xin Li, 2016, World Scientific Books. EconPapers: https://econpapers.repec.org/RePEc:wsi:wsbook:9839 | book | Chapters cover optimal stopping/switching, stop-loss, and trading under OU, exponential OU, and CIR models. |
| Survival modeling basics | **lifelines survival analysis docs**. https://lifelines.readthedocs.io/en/latest/Survival%20analysis%20with%20lifelines.html | production OSS docs | `KaplanMeierFitter` fits survival functions from durations and event indicators; docs stress confidence intervals and censored observations. |
| Survival metrics | **scikit-survival evaluating survival models**. https://scikit-survival.readthedocs.io/en/stable/user_guide/evaluating-survival-models.html | production OSS docs | Harrell's C is biased upward under high censoring; use IPCW/Uno's C for moderate/high censoring. Time-dependent Brier score uses IPCW and evaluates discrimination + calibration; integrated Brier score gives one scalar. |
| Neural survival | **DeepSurv: Personalized Treatment Recommender System Using A Cox Proportional Hazards Deep Neural Network** — Katzman et al., 2016, arXiv; code: https://github.com/jaredleekatzman/DeepSurv | paper + code | DeepSurv is a neural generalization of Cox PH. Repo trains on `{x,t,e}` and evaluates with concordance index. |
| Competing-risk neural survival | **DeepHit code repository** — Lee, Zame, Yoon, van der Schaar. https://github.com/chl8856/DeepHit | code available | Implements DeepHit for single-risk and competing-risk data; supports evaluation times and time-dependent C-index variant. |
| Calibration metrics | **ISDEvaluation code for “Effective Ways to Build and Evaluate Individual Survival Distributions”**. https://github.com/haiderstats/ISDEvaluation | paper + code | Evaluates Kaplan–Meier, Cox PH, AFT, RSF, Cox elastic-net, MTLR across concordance, Brier/IBS, L1-loss, 1-calibration, and D-calibration. |
| Cointegration implementation | **statsmodels `coint` docs**. https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html | production OSS docs | Augmented Engle–Granger two-step test. Null: no cointegration; variables assumed I(1); p-values/critical values from MacKinnon approximations; no gaps/nans implemented. |
| Equity stat-arb classic | **Statistical arbitrage in the US equities market** — Marco Avellaneda, Jeong-Hyun Lee, 2010, *Quantitative Finance*. DOI/Crossref opened: https://api.crossref.org/works/10.1080/14697680903124632 | journal paper | Crossref verifies title/authors/venue/date. Full text not opened; keep method details as leads unless verified from paper. |
| Deep stat-arb | **Deep Learning Statistical Arbitrage** — Jorge Guijarro-Ordonez, Markus Pelger, Greg Zanotti, 2026, *Management Science*. DOI/Crossref opened: https://api.crossref.org/works/10.1287/mnsc.2022.03132; SSRN DOI metadata: https://api.crossref.org/works/10.2139/ssrn.3862004 | journal paper | Constructs arbitrage portfolios as residual portfolios from conditional latent asset-pricing factors; extracts time-series signals with a convolutional transformer; then forms an optimal constrained policy maximizing risk-adjusted returns. |
| Micro-price fair value | **The micro-price: a high-frequency estimator of future prices** — Sasha Stoikov, 2018, *Quantitative Finance*. DOI/Crossref opened: https://api.crossref.org/works/10.1080/14697688.2018.1489139; official code: https://github.com/sstoikov/microprice | journal paper + code | Repo describes micro-price as “an estimator of the fair price, given the state of the order book”; notebook/code available with sample BAC/CVX data. |

## 2) Decision-rule menu: act now vs wait

### 2.1 Latency-aware expected value for an executable edge

For opportunity \(i\) at decision time \(t\):

\[
\operatorname{EV}_{\text{act}}(i,L)
= Q_i(t)\,S_i(L\mid x_t)\,N_i\,[e_i(t)-f_i-s_i(L)-a_i(L)]
- [1-Q_i(t)]\,N_i\,\ell_i(L)
- r_i(N_i,L).
\]

Definitions:

- \(e_i(t)\): gross executable edge from current books/fair values, not mid-price edge.
- \(f_i\): explicit fees + taker/maker fees + funding/basis carry where relevant.
- \(s_i(L)\): expected slippage / walking-the-book cost for latency \(L\).
- \(a_i(L)\): adverse-selection cost conditional on our order arriving after the market moved.
- \(Q_i(t)\): confidence that the mispricing is real, not stale/noisy/locked by bad data.
- \(S_i(L\mid x_t)=P(T_i>L\mid x_t)\): survival probability that the opportunity remains open after our measured end-to-end latency.
- \(\ell_i(L)\): loss if signal is false/noisy or quote disappears unfavorably.
- \(r_i\): inventory/capital/risk penalty.

Source tie: Moallemi–Sağlam justifies treating latency as an execution friction with a measurable cost; Cartea–Sánchez-Betancourt supplies the moving-target/fill-ratio framing and the limit-price vs fill-probability trade-off; lifelines/scikit-survival provide the survival probability object \(S(t)\) and evaluation discipline.

Practical rule:

\[
\text{rank score}_i = \frac{\operatorname{EV}_{\text{act}}(i,L)}{\max(L,\epsilon)}
\quad\text{or}\quad
\operatorname{EV}_{\text{act}}(i,L)\cdot P(\text{capacity available}).
\]

Use EV per millisecond when opportunities compete for the same latency budget; use raw EV when capacity is not binding.

### 2.2 Shadow-price sizing / latency improvement

For an infrastructure change reducing latency from \(L_0\) to \(L_1\):

\[
\Pi(L)=\sum_i \lambda_i\,\operatorname{EV}_{\text{act}}(i,L),
\qquad
\text{shadow price}(L_0\to L_1)=\Pi(L_1)-\Pi(L_0).
\]

\(\lambda_i\) is opportunity arrival intensity by class/venue pair. This is the P6 analogue of Cartea–Sánchez-Betancourt’s shadow price of latency: pay for colocation/software optimization only if the expected fill/EV gain exceeds the cost.

### 2.3 Wait-vs-act as value of information against decay

Let \(\Delta\) be the time needed to collect one more quote/update. Act now if:

\[
\operatorname{EV}_{\text{act}}(t,L)
\ge
\mathbb{E}\left[
\operatorname{EV}_{\text{act}}(t+\Delta,L)
\mid \mathcal F_t,\ T>\Delta
\right]P(T>\Delta\mid\mathcal F_t)
- c_{\text{wait}}(\Delta).
\]

Approximation for implementation:

\[
\operatorname{VOI}_{\Delta}
= \mathbb{E}\left[\max(0,\operatorname{EV}_{t+\Delta})\right]S(\Delta\mid x_t)
-\max(0,
\operatorname{EV}_t),
\]

wait only when \(\operatorname{VOI}_{\Delta}>c_{\text{wait}}\) and the probability of missing the opportunity is acceptable. This is the core “confidence vs latency” knob: waiting can raise \(Q\), but it multiplies payoff by survival \(S(\Delta)\).

Source tie: Cartea–Sánchez-Betancourt’s stochastic-delay MLO paper explicitly distinguishes impatient orders that walk the book from patient speculative MLOs; delay-aware RL papers justify carrying delayed observations/actions in the state/belief rather than assuming instantaneous feedback.

### 2.4 Sequential detection / CUSUM thresholding

For a standardized spread innovation \(z_t\), a one-sided CUSUM detector can maintain:

\[
C_t^+ = \max(0, C_{t-1}^+ + z_t-k),
\quad
\text{signal when } C_t^+>h.
\]

NIST’s opened CUSUM page gives a design mapping:

\[
k=\frac{\delta\sigma_x}{2},\quad
d=\frac{2}{\delta^2}\ln\left(\frac{1-\beta}{\alpha}\right),\quad
h=dk.
\]

For P6: set \(\alpha\) as false-arbitrage tolerance, \(\beta\) as missed-opportunity tolerance, and \(\delta\) as minimum economic spread in post-fee standard-deviation units. Then still gate CUSUM signals through \(\operatorname{EV}_{\text{act}}\); a statistical detection without positive latency-aware EV should not rank.

### 2.5 Delayed-MDP framing for policy experiments

State should include: latest local book snapshots, exchange timestamps, receive timestamps, in-flight orders, last actions, and a belief/fair-value state. Delay-aware RL sources say delayed systems can be treated through augmented states or belief filters. For a hackathon, use this as evaluation framing rather than primary model: compare a myopic EV policy to a small finite-horizon policy that sees \((x_t,\text{age}_t,\text{in-flight})\).

## 3) Survival-model menu for opportunity decay

Define an opportunity birth when edge first exceeds a minimum executable threshold, and death when the edge is no longer executable after fees/slippage or when a quote update invalidates it. Right-censor opportunities still alive at data-window end or when the feed drops.

| Model | Formula / output | Best P6 use | Caveats |
|---|---|---|---|
| Kaplan–Meier | Estimate \(S(t)=P(T>t)\) from durations + event indicators. | Baseline decay curve by opportunity class: same-venue, spot/perp, cointegration spread; report median lifetime and survival at p50/p95 latency. | Non-parametric; cannot condition richly on state except stratification. Good first figure. |
| Cox proportional hazards | \(h(t\mid x)=h_0(t)\exp(\beta^\top x)\). | Interpret factors: quote age, venue pair, spread size, volatility, book imbalance, event-time intensity. | PH assumption likely fragile around news/liquidity shocks. Use time-varying covariates or stratify. |
| AFT | \(\log T=\beta^\top x+\sigma\epsilon\). | Direct “milliseconds until close” model; easy for latency-budget reporting. | Distributional misspecification can hurt tails. |
| Discrete-time hazard | \(P(T\in[t,t+\Delta)\mid T\ge t,x)=\sigma(g_t(x))\). | Best fit for millisecond tick data: bin by 1/5/10 ms; handles time-varying covariates and heavy censoring with standard classifiers. | Needs careful negative sampling and exchange-clock alignment. |
| Competing risks | Cause-specific hazards \(h_k(t\mid x)\). | Label closure cause: venue A moved, venue B moved, both moved, feed stale, cost/fee crossed threshold. DeepHit repo supports competing-risk setup. | Need reliable cause labels from event replay. |
| Gradient-boosted / random survival | Nonlinear \(S(t\mid x)\) or cumulative hazard. | Strong tabular baseline after KM/Cox; handles nonlinear venue/volatility interactions. | Calibration must be checked; latency tails matter more than average C-index. |
| DeepSurv / neural Cox | Neural risk score in Cox loss. | If many features and enough events; code exists. | Black-box; PH-like Cox loss still rank-oriented, not enough for calibrated survival. |
| DeepHit-style | Direct discrete event-time distribution with competing risks. | Natural for binned millisecond lifetimes and closure causes. | More data-hungry; evaluate calibration, not just rank. |
| Conformal survival | Wrap a survival predictor with calibrated prediction sets/intervals. | Useful for “don’t trade if survival lower bound at L is poor.” | I did not open a primary conformal-survival paper; keep as lead. |

Evaluation:

- Use IPCW/Uno’s C rather than Harrell’s C under heavy censoring: scikit-survival docs explicitly warn Harrell’s C is biased upward at high censoring.
- Use time-dependent AUC only for discrimination at specific latency horizons.
- Use Brier score / integrated Brier score because scikit-survival docs define it as discrimination + calibration; P6 needs calibrated \(S(L)\), not just ranking.
- Use D-calibration and 1-calibration once individual survival curves are emitted; ISDEvaluation repo lists D-calibration and 1-calibration among supported metrics.
- Report operational metrics: calibration of \(S(L)\) at chosen latencies, realized EV by survival decile, false-positive trade rate, and missed-opportunity rate.

For ms-scale heavy censoring, start with discrete-time hazards + KM baseline. If closure cause labels are available, add cause-specific discrete hazards or DeepHit-style competing risks.

## 4) Stat-arb / fair-value menu

### 4.1 Three opportunity tiers

1. **Same asset, multiple venues:** law-of-one-price deviation. Fair value can be a multi-venue efficient price; execution uses the latency-aware EV formula.
2. **Same underlying, different instrument:** spot/perpetual basis. Edge must include funding, borrow/carry, and liquidation/margin constraints.
3. **Correlated assets:** cointegration/OU spread. Edge is less “instant arbitrage,” more convergence trade; confidence and holding-time risk dominate.

### 4.2 Cointegration and OU spreads

- Engle–Granger implementation source: statsmodels `coint` uses augmented Engle–Granger two-step test; null is no cointegration; inputs assumed I(1); p-values and critical values use MacKinnon approximations; no gaps/nans are implemented.
- Practical P6 implication: before any pair-trading result, explicitly resample/align timestamps and handle gaps. Non-synchronous ticks can otherwise create fake cointegration/lead-lag.
- OU spread model for selected pairs:

\[
dX_t=\theta(\mu-X_t)dt+\sigma dW_t,
\qquad
\text{half-life}=\frac{\ln 2}{\theta}.
\]

Use half-life only after checking estimation error; short windows, microstructure noise, and asynchronous sampling bias \(\theta\). Leung–Li is the opened source verifying OU/optimal-stopping/stop-loss as the relevant mean-reversion trading framework.

### 4.3 Dynamic hedge ratios / fair value

Implementation menu:

- Static hedge ratio: OLS residual spread; easiest baseline.
- Rolling or exponentially weighted hedge ratio: adapts slowly.
- Kalman/state-space hedge ratio: latent \(\beta_t\) and fair value; useful when basis changes intraday.
- Multi-venue efficient price: latent efficient price observed with venue-specific noise/latency; use Kalman filtering or robust weighted mid/micro-price.

I did not open a primary multi-venue Kalman efficient-price paper in this session; treat this as a modeling recommendation, not a cited literature claim.

### 4.4 Deep stat-arb

Guijarro-Ordonez–Pelger–Zanotti (opened Crossref abstract) is already strong prior art: residual arbitrage portfolios from conditional latent asset-pricing factors + convolutional transformer signals + constrained optimal trading policy. P6 should not claim “deep stat-arb” itself as novelty. Our novelty should be latency-aware ranking/decisioning on top of simple/robust signals.

### 4.5 Micro-price / fair value under noise

Stoikov’s opened repo describes micro-price as an order-book-state fair-price estimator. P6 use:

\[
\text{microprice}_v \approx \frac{a_v q^b_v + b_v q^a_v}{q^a_v+q^b_v}
\]

where \(b,a\) are best bid/ask and \(q^b,q^a\) their queue sizes. Use it as a short-horizon fair-value baseline per venue; compare against mid-price and cross-venue latent efficient price. The exact paper text was not opened, so cite the official repo for maturity/code and verify formula before external submission.

## 5) Where P6 can be genuinely novel

What already exists:

- Latency has a mature execution-cost literature: Moallemi–Sağlam quantify latency cost; Cartea–Sánchez-Betancourt value latency through fill ratios and stochastic-delay MLOs.
- Mean-reversion optimal stopping is not new: Leung–Li covers OU/exponential OU/CIR trading with optimal stopping/switching and stop-loss.
- Deep stat-arb is not new: Guijarro-Ordonez–Pelger–Zanotti already combine latent factors, transformer signals, and optimal constrained trading.
- Survival models are standard; neural and competing-risk versions have code.

Credible novelty for P6:

1. **Unified latency-aware opportunity score** across same-asset, basis, and correlated-asset opportunities: executable edge × confidence × survival-at-latency.
2. **Decision layer, not just detector:** explicit act-now vs wait-for-more-evidence rule where waiting improves \(Q\) but decays payoff through \(S(\Delta)\).
3. **Competing-risk decay labels:** edge closed because venue A moved, venue B moved, both moved, or quote became stale. This is directly useful for routing and venue selection.
4. **Latency-budget simulator:** measured components (feed age, model time, routing, exchange ack) plugged into \(S(L)\) and shadow price. Shows which optimization matters.
5. **Calibration-first evaluation:** C-index alone is insufficient; report Brier/IBS/D-calibration and realized EV calibration at latency horizons.
6. **Robust fair-value confidence:** confidence \(Q\) should include quote age, venue health, book imbalance, micro-price vs mid disagreement, and cross-venue consistency.

Recommended framing change: make “decay-calibrated execution decisioning” the innovation, not “stat-arb model.” Keep the signal model deliberately simple in Round 1, then show the decision layer can wrap threshold, OU, and learned signals.

## 6) UNVERIFIED leads

I could not open or fully verify these primary texts during this session; do not cite them in final materials until opened.

- Moallemi–Sağlam full Operations Research paper text / formula for closed-form latency cost; Crossref abstract opened, publisher page returned 403.
- Lehalle & Mounjid latency/adverse-selection source requested by prompt; not verified.
- Lo, MacKinlay & Zhang, **Econometric Models of Limit-Order Executions**, 2002, *Journal of Financial Economics*, DOI `10.1016/S0304-405X(02)00134-4`; web search found MIT/Elsevier/SSRN links, but direct opening failed.
- Maglaras–Moallemi–Wang fill-probability/fill-time source; not verified.
- Wald SPRT / Bayesian quickest detection primary sources; I only opened a secondary SPRT page and therefore did not cite it above. Formula to verify: cumulative log-likelihood ratio \(S_n=\sum_{j\le n}\log(f_1(X_j)/f_0(X_j))\), stop for \(H_1\) if \(S_n\ge \log((1-\beta)/\alpha)\), for \(H_0\) if \(S_n\le \log(\beta/(1-\alpha))\).
- Johansen original cointegration paper/book; not opened. Use statsmodels docs only for implementation details for now.
- Avellaneda–Lee full text; Crossref metadata opened, but method details (PCA/ETF residuals, Sharpe decay) need paper text verification.
- Stoikov full Quantitative Finance paper; Crossref metadata and official code repo opened, but exact micro-price derivation should be verified from paper/notebook before formal citation.
- Conformal survival primary papers; not opened.
- Online changepoint detection primary sources; not opened.
- Multi-venue efficient-price / Kalman price-discovery primary papers (e.g., Hasbrouck-style information shares/state-space variants); not opened.
