import streamlit as st
import plotly.graph_objects as go
from data.config import INDIA_GSEC_YIELDS

def render_debt_panel(us_yields: dict):
    with st.expander("🏛️ Debt & Fixed Income Panel", expanded=False):
        col_india, col_us, col_signals = st.columns(3)

        india = INDIA_GSEC_YIELDS
        with col_india:
            st.subheader("India G-Sec")
            maturities_in = ["1y","2y","5y","10y","30y"]
            yields_in = [india.get(m, 0) for m in maturities_in]
            fig = go.Figure(go.Scatter(x=maturities_in, y=yields_in, mode="lines+markers",
                line=dict(color="#3b82f6", width=2), marker=dict(size=7)))
            fig.update_layout(height=200, margin=dict(l=0,r=0,t=20,b=0),
                              yaxis_title="%", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Source: {india['source']} · Updated: {india['last_updated']}")

        with col_us:
            st.subheader("US Treasuries")
            maturities_us = ["2y","5y","10y","30y"]
            yields_us = [us_yields.get(m) for m in maturities_us]
            valid = [(m, y) for m, y in zip(maturities_us, yields_us) if y is not None]
            if valid:
                fig2 = go.Figure(go.Scatter(
                    x=[v[0] for v in valid], y=[v[1] for v in valid],
                    mode="lines+markers", line=dict(color="#f59e0b", width=2), marker=dict(size=7)
                ))
                fig2.update_layout(height=200, margin=dict(l=0,r=0,t=20,b=0),
                                   yaxis_title="%", paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("US yield data loading...")

        with col_signals:
            st.subheader("Signals")
            in10 = india.get("10y", 0)
            in2 = india.get("2y", 0)
            us10 = us_yields.get("10y") or 0
            us2 = us_yields.get("2y") or 0

            # India curve shape
            if in10 and in2:
                spread_in = round(in10 - in2, 2)
                shape_in = "Normal" if spread_in > 0.2 else ("Flat" if spread_in > -0.1 else "Inverted")
                st.metric("India Curve", shape_in, delta=f"Spread: {spread_in}%")

            # US curve shape
            if us10 and us2:
                spread_us = round(us10 - us2, 2)
                shape_us = "Normal" if spread_us > 0.2 else ("Flat" if spread_us > -0.1 else "Inverted ⚠️")
                st.metric("US Curve", shape_us, delta=f"Spread: {spread_us}%")

            # India-US spread
            if in10 and us10:
                in_us_spread = round(in10 - us10, 2)
                st.metric("India-US 10Y Spread", f"{in_us_spread}%",
                          delta="Attractive for FII inflows" if in_us_spread > 2.5 else "Spread compressed")
