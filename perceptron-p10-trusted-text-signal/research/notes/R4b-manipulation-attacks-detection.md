# R4b — Manipulation, Adversarial Attacks & Detection for Text-Driven Stock Signals

Status: IN PROGRESS (skeleton created, appending findings after every 2 sources)
Accessed date for all sources below: 2026-10-04 (IST)
Research window: Techfest 2026 Perceptron P10 "Trusting a Signal Extracted from Messy, Manipulated Text"

## TL;DR
(to be filled last)

## Attacks on text-driven predictors

### Xie et al., NAACL 2022 — "A Word is Worth A Thousand Dollars: Adversarial Attack on Tweets Fools Stock Prediction"
- **Citation**: Yong Xie, Dakuo Wang, Pin-Yu Chen, Jinjun Xiong, Sijia Liu, Oluwasanmi Koyejo. NAACL 2022, pp. 587–599. DOI 10.18653/v1/2022.naacl-main.43.
- **Sources opened**: ACL Anthology landing page https://aclanthology.org/2022.naacl-main.43/ (accessed 2026-10-04); arXiv abstract page https://arxiv.org/abs/2205.01094 (arXiv:2205.01094, accessed 2026-10-04); official code repo README https://github.com/yonxie/AdvFinTweet (accessed 2026-10-04, commit visible SHA 5d232e5).
- **Threat model (verified, ACL Anthology abstract + GitHub README)**: a "tweet concatenation attack" that "retweets" (appends) a *perturbed but semantically similar* tweet to the real tweet stream — i.e., the attacker does not edit real tweets, just adds adversarially-crafted ones. Adversarial generation is posed as combinatorial optimization under **semantic similarity + perturbation-budget constraints** (joint optimization over "concatenation attack with perturbation of replacement").
- **Victim models (verified, GitHub README `attack.sh` args)**: four models are attacked — `han`, `stocknet`, `tweetgru`, `tweetlstm`. **Confirms StockNet is one of the four victim models**, directly relevant to our skeleton's StockNet base.
- **Exact numbers (verified, GitHub README "Highlighted Results" section)**:
  - Attack Success Rate (ASR) is reported as a function of attack budget (figure `budget_effect.png`); exact ASR percentages are in the figure/paper tables, not reproduced as text in the README (so I cite the artifact's existence, not a single ASR number — see gap below).
  - **P&L impact (exact, quotable)**: "trading simulation with initial value $10000 shows our attack causes additional loss of $3200 (32%) over two years." This is the single cleanest number to cite for simulated trading loss.
- **Gap**: the ACL Anthology/arXiv abstract pages only state "consistent success rates and cause significant monetary loss" qualitatively — they do not expose numeric ASR tables in HTML (would require opening the PDF, which is disallowed by operating constraints). The $3200/32% figure from the GitHub README is the verified quantitative anchor for this paper.

### 2023–2026 follow-ups (verified via arXiv /abs/ pages, HTML metadata, accessed 2026-10-04)
1. **Rizvani, Apruzzese, Laskov — "Adversarial News and Lost Profits: Manipulating Headlines in LLM-Driven Algorithmic Trading"**, arXiv:2601.13082 (submitted 2026-01-19), accepted at **IEEE SaTML 2026** (DOI 10.1109/SaTML68715.2026.00053). URL: https://arxiv.org/abs/2601.13082.
   - **Threat model**: attacker has no direct ATS access but can alter stock-related news headlines for a single day, using two human-imperceptible manipulations: (a) Unicode homoglyph substitutions that misroute stock-name entity recognition, (b) hidden-text clauses that alter headline sentiment invisibly to human readers but visible to the LLM.
   - **System under test**: realistic ATS built in Backtrader fusing an LSTM price forecast with LLM-derived sentiment from FinBERT, FinGPT, FinLLaMA + six general-purpose LLMs.
   - **Exact number (verified, og:description meta + abstract text)**: "manipulating a one-day attack over 14 months can reliably mislead LLMs and **reduce annual returns by up to 17.7 percentage points**."
   - Real-world feasibility confirmed via survey of **27 FinTech practitioners** and inspection of scraping libraries/trading platforms; authors state they **notified trading platform owners** of the issue.
2. **"Market Signal Injection: Adversarial Context Manipulation of LLM Pricing Agents"**, arXiv:2609.18357. URL: https://arxiv.org/abs/2609.18357.
   - Attack ("MSI") manipulates *how* market data is presented (numerical formatting, competitor ordering, qualitative commentary) without explicit instructions, across 9 open-weight + 3 proprietary LLM pricing agents in simulated Bertrand duopoly/triopoly markets.
   - **Exact number (verified, abstract)**: sentiment-based framing attacks produce the largest behavioral shifts; probes separating attacked vs. baseline activations reach **linear-probe AUC = 1.00, MLP AUC 0.93–0.99** across all 11 re-evaluated model–condition pairs. Larger models are **not** consistently more robust.
3. **"Contagion on the Trading Floor: How Adversarial Signals Spread in Multi-Agent Trading Systems"**, arXiv:2609.19789. URL: https://arxiv.org/abs/2609.19789.
   - Introduces **GMATS** (Generic Multi-Agent Trading System) framework; studies black-box, input-only poisoning attacks that inject budget-constrained, "plausibly benign" social-media content into an analyst agent's evidence stream (no system access needed, only public social feeds).
   - Defines "contagion metrics" (belief-shift scores at analyst/coordinator layers, attack-clean deltas on backtest metrics). Abstract (verified): "even simple input-only attackers can materially degrade risk-return profile[s]" on a safe offline benchmark with historical market+social data. (Numeric contagion-metric values require the full paper; second fetch attempt for more abstract detail hit a transport error — flagged as partial.)
- **Direct relevance to our threat model**: all three 2026 papers generalize Xie et al.'s 2022 "add adversarial text, don't touch the real signal" threat model to LLM-sentiment-fusion pipelines — exactly our P10 architecture (text + price fusion). This is strong evidence our conformal-bound signal needs to be stress-tested against (a) imperceptible/homoglyph text perturbation and (b) framing-only (no-new-fact) manipulation.

## Incidents

### 1. Hacked AP Twitter account — fake White House explosion tweet (23 Apr 2013)
- **Source**: CNBC, "False Rumor of Explosion at White House Causes Stocks to Briefly Plunge, AP Confirms its Twitter Feed Was Hacked," 2013-04-23. URL: https://www.cnbc.com/2013/04/23/false-rumor-of-explosion-at-white-house-causes-stocks-to-briefly-plunge-ap-confirms-its-twitter-feed-was-hacked.html (accessed 2026-10-04).
- **Exact claim/numbers (verified, direct quote from article)**: At ~1:07pm ET, @AP tweeted "Breaking: Two Explosions in the White House and Barack Obama is Injured." "The Dow plunged more than 140 points and bond yields fell. Within six minutes, the Dow recovered its losses... Reuters estimated that the temporary loss of market cap in the S&P 500 alone totaled **$136.5 billion**." USD/JPY also briefly plunged to ~98.60. Syrian Electronic Army claimed responsibility. FBI, Secret Service, and SEC opened investigations. Quote from trader Kenny Polcari: "that goes to show you how algorithms read headlines and create these automatic orders."
- **Relevance**: canonical real-world proof that algorithmic/automated trading reacting to unverified social text (no price corroboration lag) can move indices within *minutes*, directly motivating a conformal/confidence-gated fusion signal rather than naive text-triggered trades.

### 2. Hacked SEC (@SECGov) X account — fake Bitcoin spot-ETF approval post (9 Jan 2024)
- **Source**: TechCrunch, "SEC's X account hacked, sharing 'unauthorized tweet' regarding spot bitcoin ETF," 2024-01-09. URL: https://techcrunch.com/2024/01/09/sec-account-hacked-sharing-unauthorized-tweet-regarding-bitcoin-spot-etf/ (accessed 2026-10-04).
- **Note**: sec.gov itself (including the Gensler statement page `sec.gov/newsroom/speeches-statements/gensler-x-account` and press-release paths) returned **HTTP 403 to every fetch attempt from this environment** (verified via web_fetch and via `curl` with a standard browser User-Agent on both the specific URL and the bare `sec.gov` root — all 403). Using TechCrunch as the verified secondary source instead; it directly quotes the SEC spokesperson and Chair Gensler.
- **Exact claim/numbers (verified, direct quote from article)**: Fake post was up for "about 30 minutes." "Bitcoin's price spiked near **$48,000** but has since fallen to around **$45,700**." SEC spokesperson: "The SEC's @SECGov X/Twitter account has been compromised. The unauthorized tweet regarding bitcoin ETFs was not made by the SEC or its staff." Gensler (quoted tweet, 2024-01-09): "The @SECGov twitter account was compromised, and an unauthorized tweet was posted. The SEC has not approved the listing and trading of spot bitcoin exchange-traded products." SEC + FBI + SEC Office of Inspector General investigated.
- **Relevance**: shows the attack surface is not just "fake news site" but a trusted, officially-verified regulator account — i.e., source authentication alone is an insufficient trust signal for a fusion model; content-level consistency checks (e.g., cross-check against price/options-market reaction, other regulator channels) are also needed.

## Detection
(pending)

## Tooling
(pending)

## Implications for our threat model
(pending)

## Source table
| # | Title | Authors/Org | Date | URL | Key claim used |
|---|-------|-------------|------|-----|----------------|
(pending)

## Leads not verified (UNVERIFIED)
(pending)
