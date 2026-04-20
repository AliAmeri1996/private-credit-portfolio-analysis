"""
Lightweight portfolio and risk statistics helpers for daily return series.

Assumes returns are simple daily returns (not log returns), expressed as decimals
(e.g., 0.01 for +1%). Trading year defaults to 252 sessions.
"""

from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def annualized_return(returns: pd.Series, trading_days: int = TRADING_DAYS_PER_YEAR) -> float:
    """Annualized arithmetic mean return from daily simple returns."""
    r = returns.dropna()
    if r.empty:
        return float("nan")
    return float(r.mean() * trading_days)


def annualized_volatility(returns: pd.Series, trading_days: int = TRADING_DAYS_PER_YEAR) -> float:
    """Annualized volatility from daily simple returns (sample std dev)."""
    r = returns.dropna()
    if r.empty or len(r) < 2:
        return float("nan")
    return float(r.std(ddof=1) * np.sqrt(trading_days))


def sharpe_ratio(
    returns: pd.Series,
    rf_annual: float = 0.0,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """
    Sharpe-style ratio using daily returns and a flat annual risk-free rate.

    rf_annual is expressed as a decimal (e.g., 0.02 for 2%).
    """
    r = returns.dropna()
    vol = annualized_volatility(r, trading_days=trading_days)
    if vol == 0 or np.isnan(vol):
        return float("nan")
    rf_daily = (1.0 + rf_annual) ** (1.0 / trading_days) - 1.0
    excess_daily = r - rf_daily
    excess_ann = float(excess_daily.mean() * trading_days)
    return excess_ann / vol


def cumulative_returns(returns: pd.Series) -> pd.Series:
    """Cumulative simple return through time: prod(1+r) - 1."""
    r = returns.dropna()
    if r.empty:
        return pd.Series(dtype=float)
    return (1.0 + r).cumprod() - 1.0


def compute_drawdown_series(cumulative_returns: pd.Series) -> pd.Series:
    """
    Drawdown series on a cumulative return curve.

    Uses wealth W = 1 + cumulative_return, then DD = W / cummax(W) - 1.
    """
    s = cumulative_returns.dropna()
    if s.empty:
        return pd.Series(dtype=float)
    wealth = 1.0 + s
    peak = wealth.cummax()
    return wealth / peak - 1.0


def max_drawdown(returns: pd.Series) -> float:
    """Maximum drawdown from daily simple returns."""
    dd = compute_drawdown_series(cumulative_returns(returns))
    if dd.empty:
        return float("nan")
    return float(dd.min())


def portfolio_returns(asset_returns: pd.DataFrame, weights: Mapping[str, float]) -> pd.Series:
    """
    Static long-only portfolio return series from aligned asset returns.

    weights maps column name -> weight; weights should sum to ~1.0.
    """
    missing = [k for k in weights if k not in asset_returns.columns]
    if missing:
        raise KeyError(f"Unknown columns in weights: {missing}")

    w = pd.Series({k: float(v) for k, v in weights.items()}, dtype=float)
    cols = list(w.index)
    aligned = asset_returns[cols].dropna(how="any")
    if aligned.empty:
        return pd.Series(dtype=float)
    return (aligned * w).sum(axis=1)


def summary_statistics_table(
    returns: pd.Series | pd.DataFrame,
    rf_annual: float = 0.0,
    name: str | None = None,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> pd.DataFrame:
    """
    Build a one-row (Series) or multi-row (DataFrame of aligned columns) summary table.

    For a DataFrame, each column is treated as an asset/sleeve/portfolio return series.
    """
    if isinstance(returns, pd.Series):
        series_map = {name or returns.name or "series": returns}
    else:
        series_map = {col: returns[col] for col in returns.columns}

    rows: list[dict[str, float | str]] = []
    for label, s in series_map.items():
        rows.append(
            {
                "name": label,
                "ann_return": annualized_return(s, trading_days=trading_days),
                "ann_vol": annualized_volatility(s, trading_days=trading_days),
                "sharpe_rf": sharpe_ratio(s, rf_annual=rf_annual, trading_days=trading_days),
                "max_dd": max_drawdown(s),
                "n_days": int(s.dropna().shape[0]),
            }
        )
    return pd.DataFrame(rows).set_index("name")
