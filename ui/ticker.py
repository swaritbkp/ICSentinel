import streamlit as st

def render_ticker_bar(quotes: dict, last_updated: str):
    TICKER_DISPLAY = [
        ("Nifty 50",    "nifty50",      "₹"),
        ("Sensex",      "sensex",       "₹"),
        ("Bank Nifty",  "banknifty",    "₹"),
        ("S&P 500",     "sp500",        "$"),
        ("NASDAQ",      "nasdaq",       "$"),
        ("Nikkei",      "nikkei225",    "¥"),
        ("USD/INR",     "usdinr",       "₹"),
        ("DXY",         "dxy",          ""),
        ("Gold",        "gold",         "$"),
        ("Brent",       "crude_brent",  "$"),
    ]
    cols = st.columns(len(TICKER_DISPLAY))
    for i, (label, key, prefix) in enumerate(TICKER_DISPLAY):
        q = quotes.get(key, {})
        if not q or "error" in q:
            cols[i].metric(label, "N/A", "–")
            continue
        price = f"{prefix}{q['price']:,.2f}"
        delta = f"{'+' if q['pct_change'] >= 0 else ''}{q['pct_change']}%"
        cols[i].metric(label, price, delta)
    st.caption(f"Last data pull: {last_updated} · Auto-refreshes every 30 min")
    st.divider()
