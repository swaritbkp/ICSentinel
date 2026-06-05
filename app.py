import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="IC Sentinel | Bilota AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Auto-refresh every 30 minutes
st_autorefresh(interval=1800 * 1000, key="auto_refresh")

# ── Imports ──────────────────────────────────────────────────────────────────
from data.fetchers import (
    fetch_quotes, fetch_ohlcv, fetch_nifty_movers,
    fetch_market_news, fetch_rbi_feed,
    fetch_us_treasury_yields, compute_market_factors
)
from data.config import YFINANCE_TICKERS
from ui.ticker import render_ticker_bar
from ui.market import render_market_panel
from ui.charts import render_charts_panel
from ui.news import render_news_panel
from ui.debt import render_debt_panel
from ui.insights import render_insights_panel

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("IC Sentinel")
    st.caption("Bilota AI · Investment Counsellor Dashboard")
    st.divider()
    if st.button("🔄 Manual Refresh All Data"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.markdown("**API Status**")
    av_key = st.secrets.get("ALPHA_VANTAGE_KEY", os.getenv("ALPHA_VANTAGE_KEY", ""))
    fh_key = st.secrets.get("FINNHUB_KEY", os.getenv("FINNHUB_KEY", ""))
    or_key = st.secrets.get("OPENROUTER_KEY", os.getenv("OPENROUTER_KEY", ""))
  
    st.markdown(f"Alpha Vantage: {'✅' if av_key and av_key != 'demo' else '⚠️ Set key in .env'}")
    st.markdown(f"Finnhub: {'✅' if fh_key else '⚠️ Set key in .env'}")
    st.markdown(f"OpenRouter: {'✅' if or_key else '⚠️ Set key in .env'}")
    st.divider()
    st.markdown("**Data Sources**")
    st.caption("• yfinance (indices, FX, commodities)")
    st.caption("• Alpha Vantage (news, yields)")
    st.caption("• Finnhub (news fallback)")
    st.caption("• RBI RSS (press releases)")
    st.caption("• OpenRouter (AI insights)")

# ── Data Fetching (all cached, runs once per refresh cycle) ───────────────────
with st.spinner("Loading market data..."):
    quotes      = fetch_quotes()
    news        = fetch_market_news()
    rbi_feed    = fetch_rbi_feed()
    us_yields   = fetch_us_treasury_yields()
    factors     = compute_market_factors(quotes)

    ohlcv_nifty = fetch_ohlcv("^NSEI",  period="5d", interval="60m")
    ohlcv_sp500 = fetch_ohlcv("^GSPC",  period="5d", interval="60m")

last_updated = datetime.now().strftime("%d %b %Y %H:%M")

# ── Render Zones ─────────────────────────────────────────────────────────────

# Zone 1 — Ticker Bar
render_ticker_bar(quotes, last_updated)

# Zone 2 — Market Panel
render_market_panel(quotes, rbi_feed, ohlcv_nifty, ohlcv_sp500)

st.divider()

# Zone 3 — Charts
render_charts_panel()

st.divider()

# Zone 4 — News + Factors
render_news_panel(news, factors)

st.divider()

# Zone 5 — Debt (collapsible)
render_debt_panel(us_yields)

st.divider()

# Zone 6 — AI Insights
render_insights_panel(quotes, factors, us_yields)

st.caption("IC Sentinel · Bilota AI · Data for informational purposes only. Not financial advice.")
