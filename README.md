
# European vs US Private Credit: A Portfolio Construction Analysis Using Public Market Proxies

## Overview

This repository contains a small, reproducible research workflow that compares **US** and **European** tradable credit risk proxies, then applies a simple **portfolio construction** lens to ask whether blending regional exposures could improve **diversification** and **drawdown behavior** relative to a single-region allocation.

The analysis is intentionally lightweight: daily returns, summary risk/return statistics, correlation, drawdowns, and a handful of static weight portfolios (for example 100% US, 100% Europe, and 50/50 blends). It is written to read like a **portfolio research note**, not a production risk system.

## Motivation


Private credit data isn't publicly available, so this project uses listed high-yield ETFs as transparent proxies for regional credit risk. It asks a narrow portfolio question: does adding European exposure to a US credit allocation help?

## Research question

**Does adding European credit proxy exposure to a US-focused credit allocation improve diversification and portfolio robustness (as measured by correlation, volatility, and drawdowns on public proxies)?**

The notebook answers this in a deliberately narrow, empirical way over a user-selected historical window.

## Methodology

1. **Download** adjusted close prices for two regional high-yield corporate bond ETFs via `yfinance` (public data only).
2. **Align** trading calendars and compute **daily log or simple returns** (the notebook uses **simple daily returns** for interpretability).
3. **Describe** each proxy with annualized return, annualized volatility, **Sharpe ratio** (using a **0% annualized risk-free rate** as a simple student baseline), and **maximum drawdown**.
4. **Study** correlation and **drawdown series** side by side.
5. **Construct** static long-only portfolios with fixed weights (100% US, 100% Europe, 50/50, and optional 70/30 and 30/70 mixes).
6. **Compare** the same portfolio metrics across sleeves.

No optimization, no machine learning, and no hidden datasets—just transparent arithmetic on public prices.

Sample: 26 Oct 2017 to 3 Aug 2026 (2,160 trading days), limited by when IHYG.L price history starts.

## Data sources and proxy disclaimer

- **Data provider**: Yahoo Finance via the `yfinance` Python package.
- **Default tickers**:
  - **USHY** — US-dollar broad high-yield corporate bond exposure (used here as a **US credit risk proxy**).
  - **IHYG.L** — euro high-yield corporate bond ETF, London listing (used here as a **European credit risk proxy**). Plain IHYG failed to download on Yahoo Finance, so the notebook fell back to this ticker.

If either ticker fails to download (symbol changes, exchange restrictions, or API issues), the notebook falls back to alternatives (**HYG** / **JNK** for US high yield; **IHYG.L** for Europe). **sensible alternatives** (for example **HYG** / **JNK** for US high yield; **IHYG.L** or other UCITS listings for Europe) and you should treat any substitution as a **different experiment**—update the README ticker line to match what you actually ran.

**Critical honesty statement (read this carefully):**

These instruments are **public market** vehicles with **daily liquidity**, transparent holdings rules, and **mark-to-market** pricing. **Private credit** funds differ materially in **capital structure**, **origination**, **covenant packages**, **fee structures**, **reporting lags**, **valuation smoothing**, and **liquidity terms**. **ETF performance is not private credit fund performance.** This project uses ETFs only as a **pedagogical and empirical stand-in** to study **regional credit beta** and **portfolio blending mechanics** with data anyone can download.

## Repository structure

```text
private-credit-portfolio-analysis/
├── README.md
├── requirements.txt
├── data/                 # optional: store downloaded CSVs if you export them
├── figures/              # optional: save notebook charts for README / PDF CV
├── notebooks/
│   └── private_credit_analysis.ipynb
└── src/
    └── utils.py          # reusable return / risk / portfolio helpers
```

## Key metrics used

| Metric | Definition (daily data, ~252 trading days/year) |
|--------|---------------------------------------------------|
| Annualized return | Mean daily return × 252 (simple scaling; adequate for a student project) |
| Annualized volatility | Std dev of daily returns × √252 |
| Sharpe (baseline) | Annualized excess return / annualized volatility, with **rf = 0** |
| Cumulative return | Compounded product of (1 + daily return) − 1 |
| Drawdown series | Underwater equity curve from running peak |
| Max drawdown | Minimum of the drawdown series |



## Key findings

Results from the run in `notebooks/private_credit_analysis.ipynb` (rf = 0, 252 trading days):

| Portfolio | Ann. return | Ann. vol | Sharpe | Max drawdown |
|---|---|---|---|---|
| 100% US | 5.0% | 8.3% | 0.61 | -22.4% |
| 70/30 US/Europe | 4.4% | 7.3% | 0.60 | -22.4% |
| 50/50 | 3.9% | 7.0% | 0.57 | -22.4% |
| 30/70 US/Europe | 3.5% | 6.9% | 0.51 | -23.2% |
| 100% Europe | 2.9% | 7.2% | 0.39 | -25.6% |

- **Correlation** between the two proxies was 0.61 over the full period, positive but well below 1.
- **Blending cut volatility**: the 50/50 mix had 7.0% vs 8.3% for US-only and 7.2% for Europe-only.
- **It did not improve risk-adjusted return**: US-only had the highest return and Sharpe, and max drawdown barely changed (about 22%).
- **Stress period**: correlation rose from 0.57 outside Feb-Apr 2020 to 0.67 during it, so the diversification benefit weakened in the Covid sell-off. This is a single episode of about 42 trading days, so it's indicative, not conclusive.

## Limitations

- **Proxy mismatch**: High-yield ETFs are **not** private senior secured loans; spread drivers, default cycles, and recovery assumptions differ.
- **Currency**: European proxy exposure may embed **FX** effects versus a US allocator’s base currency unless hedged—this notebook does **not** model hedging costs.
- **Survivorship / index rules**: ETFs rebalance; private portfolios do not behave identically.
- **Risk-free rate**: Sharpe uses **rf = 0** for simplicity; institutional work typically uses **OIS/T-bills** or a full curve.
- **Static weights**: No rebalancing frictions, taxes, or transaction costs beyond what is implicitly in ETF prices.
- **Look-ahead**: All calculations are **ex post**; this is not a trading strategy evaluation.

## How to run

**Prerequisites:** Python 3.10+ recommended.

```bash
cd private-credit-portfolio-analysis
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Launch Jupyter from the **repository root** (so imports resolve cleanly):

```bash
jupyter notebook notebooks/private_credit_analysis.ipynb
```

Run **Cell → Run All**. The notebook adds the `src/` directory to `sys.path` automatically.

## Figures (optional exports)

The notebook saves the following charts to `figures/`:

- `figures/normalized_prices.png` — rebased total-return level series
- `figures/drawdowns.png` — underwater curves for each proxy
- `figures/portfolio_cumulative_returns.png` — compounded performance of static portfolios

## Possible next improvements

- Add a **short-term Treasury** proxy (for example **SHV** or **BIL**) and recompute Sharpe with a **non-zero rf**.
- Compare **rolling 126-day correlation** and **rolling vol** to show **time-varying** diversification.
- Introduce **monthly rebalancing** vs buy-and-hold weights.
- Separate **FX hedged vs unhedged** European exposure if you can source consistent hedged series.
- Write a one-page **memo PDF** summarizing methodology + one chart (common in PMG-style workflows).



*Author note: This project is designed as an honest, public-data portfolio construction exercise for recruiting conversations—not as a substitute for proprietary manager research.*

