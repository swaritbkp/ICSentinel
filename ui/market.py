import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date
from data.config import RBI_MPC_DATES_FY26, FED_FOMC_DATES_2025_26, FII_DII_MANUAL

def render_market_panel(quotes: dict, rbi_feed: list, ohlcv_nifty: dict, ohlcv_sp500: dict):
    col_india, col_global, col_calendar = st.columns([1.2, 1.2, 0.9])

    with col_india:
        st.subheader("🇮🇳 Indian Markets")
        vix = quotes.get("indiavix", {}).get("price", 0)
        if vix:
            vix_color = "green" if vix < 15 else ("orange" if vix < 20 else "red")
            vix_label = "Low" if vix < 15 else ("Moderate" if vix < 20 else "High Fear")
            st.metric("India VIX", vix, delta=vix_label, delta_color=("normal" if vix < 20 else "inverse"))

        for key, label, prefix in [("nifty50","Nifty 50","₹"), ("sensex","Sensex","₹"), ("banknifty","Bank Nifty","₹")]:
            q = quotes.get(key, {})
            if q and "error" not in q:
                st.metric(label, f"{prefix}{q['price']:,.2f}", f"{'+' if q['pct_change']>=0 else ''}{q['pct_change']}%")

        st.markdown("**FII / DII (manual)**")
        fii = FII_DII_MANUAL["fii_net_crore"]
        dii = FII_DII_MANUAL["dii_net_crore"]
        c1, c2 = st.columns(2)
        c1.metric("FII Net (Cr)", f"₹{fii:,}", delta="Sell" if fii < 0 else "Buy", delta_color="inverse" if fii < 0 else "normal")
        c2.metric("DII Net (Cr)", f"₹{dii:,}", delta="Buy" if dii > 0 else "Sell", delta_color="normal" if dii > 0 else "inverse")
        st.caption(f"As of {FII_DII_MANUAL['last_updated']} · {FII_DII_MANUAL['source']}")

        if ohlcv_nifty and "error" not in ohlcv_nifty:
            fig = go.Figure(go.Candlestick(
                x=ohlcv_nifty["dates"][-20:],
                open=ohlcv_nifty["open"][-20:], high=ohlcv_nifty["high"][-20:],
                low=ohlcv_nifty["low"][-20:], close=ohlcv_nifty["close"][-20:],
                name="Nifty 5D"
            ))
            fig.update_layout(height=180, margin=dict(l=0,r=0,t=20,b=0),
                              xaxis_rangeslider_visible=False, showlegend=False,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with col_global:
        st.subheader("🌍 Global Macro")
        for key, label, prefix in [
            ("sp500","S&P 500","$"), ("nasdaq","NASDAQ","$"),
            ("us10y","US 10Y Yield","%"), ("dxy","DXY",""),
            ("crude_brent","Brent Crude","$"), ("gold","Gold","$")
        ]:
            q = quotes.get(key, {})
            if q and "error" not in q:
                st.metric(label, f"{prefix}{q['price']:,.2f}", f"{'+' if q['pct_change']>=0 else ''}{q['pct_change']}%")

        if ohlcv_sp500 and "error" not in ohlcv_sp500:
            fig = go.Figure(go.Scatter(
                x=ohlcv_sp500["dates"][-20:], y=ohlcv_sp500["close"][-20:],
                mode="lines", line=dict(width=2)
            ))
            fig.update_layout(height=120, margin=dict(l=0,r=0,t=10,b=0),
                              showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with col_calendar:
        st.subheader("📅 Event Radar")
        today = date.today()

        rbi_upcoming = sorted([d for d in RBI_MPC_DATES_FY26 if d >= str(today)])
        fed_upcoming = sorted([d for d in FED_FOMC_DATES_2025_26 if d >= str(today)])

        if rbi_upcoming:
            next_rbi = rbi_upcoming[0]
            days = (date.fromisoformat(next_rbi) - today).days
            st.metric("Next RBI MPC", next_rbi, delta=f"{days} days away")
        if fed_upcoming:
            next_fed = fed_upcoming[0]
            days_fed = (date.fromisoformat(next_fed) - today).days
            st.metric("Next Fed FOMC", next_fed, delta=f"{days_fed} days away")

        month = today.month
        if month in [1, 4, 7, 10]:
            season = "Results Season Active"
        elif month in [2, 5, 8, 11]:
            season = "Results Season Winding Down"
        else:
            season = "Between Earnings Seasons"
        st.info(f"📊 {season}")

        if rbi_feed:
            st.markdown("**RBI Latest**")
            for item in rbi_feed[:4]:
                st.markdown(f"• [{item['title'][:55]}...]({item['link']})", unsafe_allow_html=False)
                st.markdown(f"[→ {item['title'][:55]}...]({item['link']})")
