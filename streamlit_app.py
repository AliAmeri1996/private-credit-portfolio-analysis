import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

from utils import (
    annualized_return,
    annualized_volatility,
    sharpe_ratio,
    cumulative_returns,
    compute_drawdown_series,
    max_drawdown,
    portfolio_returns,
    summary_statistics_table,
)

st.set_page_config(page_title="Private Credit Portfolio Analysis", layout="wide")

st.title("European vs US Private Credit")
st.markdown("**Portfolio construction analysis using public market proxies (USHY / IHYG.L)**")

# --- Sidebar ---
st.sidebar.header("Parameters")

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-01-01"))

st.sidebar.markdown("---")
st.sidebar.subheader("Portfolio Weights")
us_weight = st.sidebar.slider("US Weight (%)", min_value=0, max_value=100, value=50, step=5)
eu_weight = 100 - us_weight
st.sidebar.markdown(f"European Weight: **{eu_weight}%**")

rf_rate = st.sidebar.number_input("Risk-Free Rate (%)", value=0.0, step=0.5) / 100

run = st.sidebar.button("Run Analysis", type="primary")

if run:
    with st.spinner("Downloading data and running analysis..."):
        try:
            # --- Data ---
            ushy = yf.download("USHY", start=str(start_date), end=str(end_date), auto_adjust=True, progress=False)["Close"].squeeze()
            ihyg = yf.download("IHYG.L", start=str(start_date), end=str(end_date), auto_adjust=True, progress=False)["Close"].squeeze()

            raw = pd.DataFrame({"US (USHY)": ushy, "EU (IHYG.L)": ihyg}).dropna()
            returns = raw.pct_change().dropna()

            # --- Portfolio ---
            w = {"US (USHY)": us_weight / 100, "EU (IHYG.L)": eu_weight / 100}
            port_returns = portfolio_returns(returns, w)
            port_returns.name = f"Portfolio ({us_weight}/{eu_weight})"

            all_returns = returns.copy()
            all_returns[port_returns.name] = port_returns

            # --- Metrics table ---
            st.subheader("Summary Statistics")
            stats = summary_statistics_table(all_returns, rf_annual=rf_rate)
            stats_display = pd.DataFrame({
                "Ann. Return": stats["ann_return"].map("{:.2%}".format),
                "Ann. Volatility": stats["ann_vol"].map("{:.2%}".format),
                "Sharpe Ratio": stats["sharpe_rf"].map("{:.2f}".format),
                "Max Drawdown": stats["max_dd"].map("{:.2%}".format),
                "Days": stats["n_days"].map("{:,}".format),
            })
            st.dataframe(stats_display, use_container_width=True)

            # --- Correlation ---
            st.subheader("Correlation")
            corr = returns.corr()
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(corr.style.format("{:.3f}"), use_container_width=True)
            with col2:
                corr_val = corr.iloc[0, 1]
                st.metric("US vs EU Correlation", f"{corr_val:.3f}")
                if corr_val < 0.7:
                    st.success("Correlation below 0.7 — diversification benefit likely present.")
                else:
                    st.warning("High correlation — limited diversification benefit.")

            # --- Cumulative returns chart ---
            st.subheader("Cumulative Returns")
            fig1, ax1 = plt.subplots(figsize=(14, 4))
            for col in all_returns.columns:
                cum = cumulative_returns(all_returns[col]) * 100
                ls = "--" if "Portfolio" in col else "-"
                ax1.plot(cum.index, cum, label=col, linestyle=ls, linewidth=1.5)
            ax1.axhline(0, color="black", linewidth=0.5)
            ax1.set_ylabel("Cumulative Return (%)")
            ax1.legend()
            st.pyplot(fig1)

            # --- Drawdown chart ---
            st.subheader("Drawdown")
            fig2, ax2 = plt.subplots(figsize=(14, 4))
            for col in all_returns.columns:
                dd = compute_drawdown_series(cumulative_returns(all_returns[col])) * 100
                ax2.plot(dd.index, dd, label=col, linewidth=1.2)
            ax2.fill_between(
                compute_drawdown_series(cumulative_returns(port_returns)).index,
                compute_drawdown_series(cumulative_returns(port_returns)) * 100,
                0, alpha=0.15, color="purple"
            )
            ax2.set_ylabel("Drawdown (%)")
            ax2.legend()
            st.pyplot(fig2)

            # --- Disclaimer ---
            st.markdown("---")
            st.caption(
                "⚠️ USHY and IHYG.L are public market ETFs used as regional credit proxies only. "
                "ETF performance is not private credit fund performance. "
                "Sharpe uses rf = {:.1f}%. No transaction costs or rebalancing modelled.".format(rf_rate * 100)
            )

        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("Set your parameters in the sidebar and click Run Analysis.")