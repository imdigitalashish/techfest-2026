# Deep LOB Forecasting: State of the Art (Regime Shift Focus)

> Research thread for Perceptron Problem 4 "Order Book Forecasting Under Regime Shifts".
> Compiled 2026-10-04. Sources ordered NEWEST FIRST. Every entry cites only opened sources.
> Tool/search failures and UNVERIFIED numbers are marked explicitly.

---

## Sources

### 1. TLOB: A Novel Transformer Model with Dual Attention for Price Trend Prediction with Limit Order Book Data
- **Authors**: Leonardo Berti, Gjergji Kasneci
- **Venue/Year**: arXiv preprint, submitted 2025-02-12 (citation_date), v3 online 2025-05-07
- **URL**: https://arxiv.org/abs/2502.15757 (accessed 2026-10-04, via raw HTML og:description meta tag — markdown-simplified fetch returned title only)
- **Key claims (numbers as stated in abstract)**:
  - Introduces TLOB, a transformer model with a **dual attention mechanism** (spatial + temporal) over LOB data, adaptively focusing on market microstructure; effective for longer-horizon predictions and volatile conditions.
  - A simple **MLP-based architecture adapted to LOB surpasses prior SoTA**, "challenging the necessity of complex architectures" (ablation finding reported in same paper).
  - Introduces a **new labeling method that removes horizon bias** present in earlier labeling schemes (direct critique of standard mid-price-change labeling used by DeepLOB-era work).
  - Evaluated on 4 horizons across **FI-2010 benchmark, a NASDAQ dataset, and a Bitcoin dataset**; TLOB "outperforms SoTA methods in every dataset and horizon" (no single consolidated metric given in abstract — per-dataset numbers are in body/tables, not fetched here, so exact F1/accuracy tables are UNVERIFIED from this pass).
  - Empirically shows **stock price predictability has declined over time: -6.68 in F1-score** (exact figure as stated in abstract), attributed to growing market efficiency.
  - Tested redefining trend labels using **average spread** (primary transaction cost proxy) instead of raw mid-price ticks — this caused a performance deterioration, underscoring the gap between trend classification and profitable trading.
- **Maturity**: Maintained code release referenced in abstract.
- **Code**: https://github.com/LeonardoBerti00/TLOB — UNVERIFIED stars/last-commit (not yet opened; to fetch next).

