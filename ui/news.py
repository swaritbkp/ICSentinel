import streamlit as st

SENTIMENT_STYLE = {
    "Bullish":  ("🟢", "green"),
    "Bearish":  ("🔴", "red"),
    "Neutral":  ("⚪", "gray"),
}

def render_news_panel(news: list, factors: list):
    col_news, col_factors = st.columns([1.3, 1])

    with col_news:
        st.subheader("📰 Market News")
        filter_opt = st.radio("Filter", ["All","Bullish","Bearish"], horizontal=True, key="news_filter")
        filtered = [n for n in news if filter_opt == "All" or n["sentiment"] == filter_opt]
        for item in filtered[:10]:
            icon, color = SENTIMENT_STYLE.get(item["sentiment"], ("⚪","gray"))
            st.markdown(
                f"{icon} **[{item['title'][:80]}]({item['url']})**  \n"
                f"<small style='color:gray'>{item['source']} · {item['time']}</small>",
                unsafe_allow_html=True
            )
            st.divider()

    with col_factors:
        st.subheader("⚡ Market Factors")
        if not factors:
            st.info("No factor data available.")
            return
        for f in factors:
            value = f["value"]
            signal = f["signal"]
            is_risk = any(w in signal.lower() for w in ["pressure","negative","fear","risk off","spike"])
            is_positive = any(w in signal.lower() for w in ["relief","positive","stable","on","low"])
            badge = "🔴" if is_risk else ("🟢" if is_positive else "🟡")
            with st.container():
                st.markdown(f"{badge} **{f['factor']}** — `{value}`")
                st.caption(signal)
