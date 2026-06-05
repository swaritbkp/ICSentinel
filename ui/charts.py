import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from data.config import YFINANCE_TICKERS, NIFTY_SECTORS
from data.fetchers import fetch_ohlcv, fetch_sector_performance

CHART_OPTIONS = {
    "Nifty 50": "^NSEI", "Sensex": "^BSESN", "Bank Nifty": "^NSEBANK",
    "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Gold": "GC=F",
    "Brent Crude": "BZ=F", "USD/INR": "USDINR=X",
}
PERIOD_MAP = {"1D":"1d","5D":"5d","1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}
INTERVAL_MAP = {"1D":"5m","5D":"60m","1M":"1d","3M":"1d","6M":"1wk","1Y":"1wk"}

def render_charts_panel():
    st.subheader("📈 Interactive Charts")
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        selected = st.selectbox("Index / Asset", list(CHART_OPTIONS.keys()), key="chart_sel")
    with c2:
        period_label = st.selectbox("Period", list(PERIOD_MAP.keys()), index=2, key="period_sel")
    with c3:
        overlays = st.multiselect("Overlays", ["20-MA","50-MA","200-MA","Bollinger"], default=["20-MA"], key="overlay_sel")

    symbol = CHART_OPTIONS[selected]
    period = PERIOD_MAP[period_label]
    interval = INTERVAL_MAP[period_label]

    with st.spinner("Loading chart..."):
        data = fetch_ohlcv(symbol, period, interval)

    if not data or "error" in data:
        st.warning(f"Chart data unavailable: {data.get('error','unknown error')}")
    else:
        closes = np.array(data["close"])
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.75, 0.25], vertical_spacing=0.02)

        fig.add_trace(go.Candlestick(
            x=data["dates"], open=data["open"], high=data["high"],
            low=data["low"], close=data["close"], name=selected,
            increasing_line_color="#22c55e", decreasing_line_color="#ef4444"
        ), row=1, col=1)

        for ov in overlays:
            if ov == "20-MA" and len(closes) >= 20:
                ma = np.convolve(closes, np.ones(20)/20, mode="valid")
                fig.add_trace(go.Scatter(x=data["dates"][19:], y=ma.tolist(), name="20MA",
                    line=dict(color="#60a5fa", width=1.2)), row=1, col=1)
            elif ov == "50-MA" and len(closes) >= 50:
                ma = np.convolve(closes, np.ones(50)/50, mode="valid")
                fig.add_trace(go.Scatter(x=data["dates"][49:], y=ma.tolist(), name="50MA",
                    line=dict(color="#f59e0b", width=1.2)), row=1, col=1)
            elif ov == "200-MA" and len(closes) >= 200:
                ma = np.convolve(closes, np.ones(200)/200, mode="valid")
                fig.add_trace(go.Scatter(x=data["dates"][199:], y=ma.tolist(), name="200MA",
                    line=dict(color="#a78bfa", width=1.2)), row=1, col=1)
            elif ov == "Bollinger" and len(closes) >= 20:
                ma20 = np.convolve(closes, np.ones(20)/20, mode="valid")
                std20 = [np.std(closes[i:i+20]) for i in range(len(closes)-19)]
                upper = [m + 2*s for m, s in zip(ma20, std20)]
                lower = [m - 2*s for m, s in zip(ma20, std20)]
                fig.add_trace(go.Scatter(x=data["dates"][19:], y=upper, name="BB Upper",
                    line=dict(color="#94a3b8", width=1, dash="dot")), row=1, col=1)
                fig.add_trace(go.Scatter(x=data["dates"][19:], y=lower, name="BB Lower",
                    line=dict(color="#94a3b8", width=1, dash="dot"),
                    fill="tonexty", fillcolor="rgba(148,163,184,0.08)"), row=1, col=1)

        # RSI
        if len(closes) >= 15:
            delta = np.diff(closes)
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            avg_gain = np.convolve(gain, np.ones(14)/14, mode="valid")
            avg_loss = np.convolve(loss, np.ones(14)/14, mode="valid")
            rs = np.where(avg_loss == 0, 100, avg_gain / avg_loss)
            rsi = 100 - (100 / (1 + rs))
            rsi_dates = data["dates"][14+13:]
            rsi_vals = rsi[13:].tolist() if len(rsi) > 13 else rsi.tolist()
            if rsi_dates and rsi_vals:
                fig.add_trace(go.Scatter(x=rsi_dates, y=rsi_vals[:len(rsi_dates)],
                    name="RSI(14)", line=dict(color="#f472b6", width=1.5)), row=2, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        fig.add_trace(go.Bar(x=data["dates"], y=data["volume"], name="Volume",
            marker_color="rgba(99,102,241,0.35)"), row=2, col=1)

        fig.update_layout(
            height=500, xaxis_rangeslider_visible=False, showlegend=True,
            legend=dict(orientation="h", y=1.02),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Sector heatmap
    st.subheader("🔥 Nifty Sector Heatmap")
    sectors = fetch_sector_performance()
    if sectors:
        labels = [s["sector"] for s in sectors]
        values = [abs(s["pct_change"]) + 0.1 for s in sectors]
        colors = [s["pct_change"] for s in sectors]
        text = [f"{s['sector']}<br>{'+' if s['pct_change']>=0 else ''}{s['pct_change']}%" for s in sectors]
        fig2 = go.Figure(go.Treemap(
            labels=labels, parents=[""] * len(labels),
            values=values, text=text, textinfo="text",
            marker=dict(colors=colors, colorscale=[[0,"#ef4444"],[0.5,"#f1f5f9"],[1,"#22c55e"]],
                        cmid=0, showscale=True, colorbar=dict(title="%")),
        ))
        fig2.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
                           paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
