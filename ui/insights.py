import streamlit as st
import requests
import json
import os
import time
from dotenv import load_dotenv
from data.cache import cache_get, cache_set, cache_age_minutes
from data.config import OPENROUTER_MODEL

load_dotenv()
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")

def _build_market_snapshot(quotes: dict, factors: list, us_yields: dict) -> str:
    """Serialises live data into a compact string for the LLM prompt."""
    snap = {}
    for name in ["nifty50","sensex","banknifty","sp500","nasdaq","usdinr","dxy","gold","crude_brent","indiavix","us10y"]:
        q = quotes.get(name, {})
        if q and "error" not in q:
            snap[name] = {"price": q.get("price"), "pct_change": q.get("pct_change")}
    snap["market_factors"] = [{"factor": f["factor"], "signal": f["signal"]} for f in factors]
    snap["us_yields"] = {k: v for k, v in us_yields.items() if v is not None}
    return json.dumps(snap, indent=2)


def _call_openrouter(system_prompt: str, user_content: str) -> str:
    if not OPENROUTER_KEY:
        return "⚠️ OpenRouter API key not configured in .env file."
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/bilota-ai/ic-sentinel",
        "X-Title": "IC Sentinel",
    }
    body = {
        "model": OPENROUTER_MODEL,
        "max_tokens": 400,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                          headers=headers, json=body, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return "⚠️ LLM request timed out. Will retry on next refresh."
    except Exception as e:
        return f"⚠️ LLM error: {str(e)[:80]}"


def render_insights_panel(quotes: dict, factors: list, us_yields: dict):
    st.subheader("🤖 AI Market Insight Engine")
    st.caption(f"Model: `{OPENROUTER_MODEL}` via OpenRouter · Refreshes with dashboard (30 min)")

    cache_key = "llm_insights"
    age = cache_age_minutes(cache_key)
    cached = cache_get(cache_key)

    col_btn, col_age = st.columns([1, 3])
    with col_btn:
        manual_refresh = st.button("↻ Refresh AI Insights", key="llm_refresh")
    with col_age:
        if cached:
            st.caption(f"Last AI update: {age:.0f} min ago")

    if cached and not manual_refresh:
        insights = cached
    else:
        snapshot = _build_market_snapshot(quotes, factors, us_yields)

        SYSTEM = (
            "You are a senior Indian wealth management analyst. "
            "You write crisp, fact-based market commentary for Investment Counsellors. "
            "No speculation. No generic advice. Always grounded in the specific data provided. "
            "Respond ONLY with the requested format — no preamble."
        )

        prompts = {
            "briefing": (
                f"Market data snapshot:\n{snapshot}\n\n"
                "Write exactly 3 bullet points summarising today's market narrative for an Indian IC. "
                "Format: start each bullet with a relevant emoji, one sharp sentence. "
                "Cover: 1) Indian equity direction, 2) Currency/global macro signal, 3) Key risk or opportunity."
            ),
            "talking_points": (
                f"Market data:\n{snapshot}\n\n"
                "Give 2 client-ready talking points an Investment Counsellor can use with HNI clients or MFD partners today. "
                "Each point should mention a specific implication for equity/debt/gold allocation. "
                "Be concrete, not generic. Format: numbered list."
            ),
            "risk_alerts": (
                f"Market data:\n{snapshot}\n\n"
                "Scan for genuine risk signals only — VIX spike, yield curve inversion, FII selloff, sharp rupee move, crude surge. "
                "If no real alerts exist, respond with exactly: 'No significant alerts today.' "
                "Max 3 lines. No filler."
            ),
        }

        insights = {}
        with st.spinner("Generating AI insights..."):
            for key, prompt in prompts.items():
                result = _call_openrouter(SYSTEM, prompt)
                insights[key] = result
                time.sleep(1.5)  # avoid rate limiting on free tier

        cache_set(cache_key, insights, ttl=1800)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**📋 Market Briefing**")
        st.markdown(insights.get("briefing", "Loading..."))
    with c2:
        st.markdown("**💼 IC Talking Points**")
        st.markdown(insights.get("talking_points", "Loading..."))
    with c3:
        st.markdown("**⚠️ Risk Alerts**")
        alert_text = insights.get("risk_alerts", "Loading...")
        if "No significant" in alert_text:
            st.success(alert_text)
        else:
            st.warning(alert_text)
