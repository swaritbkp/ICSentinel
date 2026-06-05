import yfinance as yf
import requests
import feedparser
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from data.cache import cache_set, cache_get, cache_get_stale
from data.config import YFINANCE_TICKERS, NIFTY50_CONSTITUENTS, NIFTY_SECTORS, AV_CALLS_PER_REFRESH

load_dotenv()
AV_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")
FINNHUB_KEY = os.getenv("FINNHUB_KEY", "")

# ── 1. BATCH QUOTE FETCH (yfinance) ─────────────────────────────────────────
def fetch_quotes() -> dict:
    """Returns dict of {symbol_name: {price, change, pct_change, high, low}} for all tickers."""
    cached = cache_get("quotes")
    if cached:
        return cached

    result = {}
    all_tickers = list(YFINANCE_TICKERS.values())
    try:
        data = yf.download(
            tickers=all_tickers,
            period="2d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        for name, symbol in YFINANCE_TICKERS.items():
            try:
                if len(all_tickers) == 1:
                    close_series = data["Close"]
                else:
                    close_series = data[symbol]["Close"]
                if isinstance(close_series, pd.DataFrame):
                    close_series = close_series.iloc[:, 0]
                close_series = close_series.dropna()
                if len(close_series) < 2:
                    continue
                prev = float(close_series.iloc[-2])
                curr = float(close_series.iloc[-1])
                result[name] = {
                    "price": round(curr, 2),
                    "change": round(curr - prev, 2),
                    "pct_change": round((curr - prev) / prev * 100, 2),
                    "symbol": symbol,
                }
            except Exception:
                continue
        cache_set("quotes", result)
        return result
    except Exception as e:
        stale = cache_get_stale("quotes")
        return stale if stale else {"error": str(e), "stale": True}

# ── 2. OHLCV CHART DATA (yfinance) ──────────────────────────────────────────
def fetch_ohlcv(symbol: str, period: str = "1mo", interval: str = "1d") -> dict:
    """Returns OHLCV as dict with lists for date, open, high, low, close, volume."""
    cache_key = f"ohlcv_{symbol}{period}{interval}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    try:
        df = yf.download(symbol, period=period, interval=interval,
                         auto_adjust=True, progress=False)
        if df.empty:
            raise ValueError(f"No data returned for symbol {symbol}")
        df = df.dropna()
        
        open_series = df["Open"]
        high_series = df["High"]
        low_series = df["Low"]
        close_series = df["Close"]
        volume_series = df["Volume"]
        
        if isinstance(open_series, pd.DataFrame):
            open_series = open_series.iloc[:, 0]
        if isinstance(high_series, pd.DataFrame):
            high_series = high_series.iloc[:, 0]
        if isinstance(low_series, pd.DataFrame):
            low_series = low_series.iloc[:, 0]
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]
        if isinstance(volume_series, pd.DataFrame):
            volume_series = volume_series.iloc[:, 0]

        result = {
            "dates":  [str(d.date()) if hasattr(d, 'date') else str(d) for d in df.index],
            "open":   [round(float(v), 2) for v in open_series],
            "high":   [round(float(v), 2) for v in high_series],
            "low":    [round(float(v), 2) for v in low_series],
            "close":  [round(float(v), 2) for v in close_series],
            "volume": [int(v) for v in volume_series],
        }
        cache_set(cache_key, result, ttl=900)
        return result
    except Exception as e:
        stale = cache_get_stale(cache_key)
        return stale if stale else {"error": str(e), "stale": True}

# ── 3. NIFTY TOP MOVERS ──────────────────────────────────────────────────────
def fetch_nifty_movers() -> dict:
    cached = cache_get("nifty_movers")
    if cached:
        return cached
    try:
        data = yf.download(
            NIFTY50_CONSTITUENTS, period="2d", interval="1d",
            group_by="ticker", auto_adjust=True, progress=False, threads=True
        )
        movers = []
        for sym in NIFTY50_CONSTITUENTS:
            try:
                c = data[sym]["Close"]
                if isinstance(c, pd.DataFrame):
                    c = c.iloc[:, 0]
                c = c.dropna()
                if len(c) < 2:
                    continue
                pct = round((float(c.iloc[-1]) - float(c.iloc[-2])) / float(c.iloc[-2]) * 100, 2)
                movers.append({"symbol": sym.replace(".NS", ""), "pct_change": pct})
            except Exception:
                continue
        movers.sort(key=lambda x: x["pct_change"])
        result = {"gainers": movers[-5:][::-1], "losers": movers[:5]}
        cache_set("nifty_movers", result, ttl=900)
        return result
    except Exception as e:
        stale = cache_get_stale("nifty_movers")
        return stale if stale else {"error": str(e), "stale": True}

# ── 4. SECTOR HEATMAP ────────────────────────────────────────────────────────
def fetch_sector_performance() -> list:
    cached = cache_get("sectors")
    if cached:
        return cached
    try:
        syms = list(NIFTY_SECTORS.values())
        data = yf.download(syms, period="2d", interval="1d",
                           group_by="ticker", auto_adjust=True, progress=False)
        result = []
        for name, sym in NIFTY_SECTORS.items():
            try:
                c = data[sym]["Close"]
                if isinstance(c, pd.DataFrame):
                    c = c.iloc[:, 0]
                c = c.dropna()
                if len(c) < 2:
                    continue
                pct = round((float(c.iloc[-1]) - float(c.iloc[-2])) / float(c.iloc[-2]) * 100, 2)
                result.append({"sector": name, "pct_change": pct})
            except Exception:
                result.append({"sector": name, "pct_change": 0.0})
        cache_set("sectors", result, ttl=900)
        return result
    except Exception as e:
        stale = cache_get_stale("sectors")
        return stale if stale else []

# ── 5. ALPHA VANTAGE: NEWS + SENTIMENT ──────────────────────────────────────
# Uses 1 of the 4 AV calls per refresh cycle
def fetch_market_news() -> list:
    cached = cache_get("av_news")
    if cached:
        return cached
    url = (
        f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
        f"&topics=economy_fiscal,financial_markets,earnings,ipo"
        f"&sort=LATEST&limit=15&apikey={AV_KEY}"
    )
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        feed = data.get("feed", [])
        result = []
        for item in feed:
            score = float(item.get("overall_sentiment_score", 0))
            if score > 0.2:
                sentiment = "Bullish"
            elif score < -0.2:
                sentiment = "Bearish"
            else:
                sentiment = "Neutral"
            result.append({
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                "time": item.get("time_published", "")[:12],
                "sentiment": sentiment,
                "score": round(score, 3),
            })
        if result:
            cache_set("av_news", result, ttl=1800)
            return result
        # AV quota exhausted or invalid key — fall to Finnhub, then RSS
        fh_news = _fetch_finnhub_news()
        if fh_news:
            return fh_news
        return _fetch_rss_news()
    except Exception:
        stale = cache_get_stale("av_news")
        if stale:
            return stale
        fh_news = _fetch_finnhub_news()
        if fh_news:
            return fh_news
        return _fetch_rss_news()

def _fetch_finnhub_news() -> list:
    if not FINNHUB_KEY:
        return []
    cached = cache_get("fh_news")
    if cached:
        return cached
    try:
        r = requests.get(
            f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}",
            timeout=10
        )
        items = r.json()[:12]
        result = [
            {"title": i.get("headline",""), "source": i.get("source",""),
             "url": i.get("url",""), "time": str(i.get("datetime","")),
             "sentiment": "Neutral", "score": 0.0}
            for i in items
        ]
        cache_set("fh_news", result, ttl=1800)
        return result
    except Exception:
        return []

def _fetch_rss_news() -> list:
    cached = cache_get("rss_news")
    if cached:
        return cached
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=business+economy+markets&hl=en-IN&gl=IN&ceid=IN:en")
        result = []
        for e in feed.entries[:15]:
            title = e.title
            source = "Google News"
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1]
            
            text = title.lower()
            if any(w in text for w in ["gain", "rise", "grow", "bull", "up", "rally", "positive"]):
                sentiment = "Bullish"
                score = 0.3
            elif any(w in text for w in ["fall", "drop", "decline", "bear", "down", "slump", "negative"]):
                sentiment = "Bearish"
                score = -0.3
            else:
                sentiment = "Neutral"
                score = 0.0

            result.append({
                "title": title,
                "source": source,
                "url": e.link,
                "time": e.get("published", "")[:16],
                "sentiment": sentiment,
                "score": score
            })
        if result:
            cache_set("rss_news", result, ttl=1800)
        return result
    except Exception:
        return cache_get_stale("rss_news") or []

# ── 6. ALPHA VANTAGE: US TREASURY YIELDS ────────────────────────────────────
# Uses 3 more AV calls (2y, 10y, 30y) — total 4/refresh
def fetch_us_treasury_yields() -> dict:
    cached = cache_get("us_yields")
    if cached:
        return cached
    maturities = {"2y": "2year", "10y": "10year", "30y": "30year"}
    result = {}
    for label, maturity in maturities.items():
        try:
            url = f"https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily&maturity={maturity}&apikey={AV_KEY}"
            r = requests.get(url, timeout=10)
            data = r.json().get("data", [])
            if data:
                result[label] = float(data[0]["value"])
            time.sleep(0.5)  # gentle pacing
        except Exception:
            result[label] = None
    # 5y from yfinance as complement
    try:
        t = yf.Ticker("^FVX")
        hist = t.history(period="2d")
        result["5y"] = round(float(hist["Close"].iloc[-1]), 2)
    except Exception:
        result["5y"] = None
    if any(v is not None for v in result.values()):
        cache_set("us_yields", result, ttl=3600)
        return result
    stale = cache_get_stale("us_yields")
    return stale if stale else result

# ── 7. RBI RSS FEED ──────────────────────────────────────────────────────────
def fetch_rbi_feed() -> list:
    cached = cache_get("rbi_feed")
    if cached:
        return cached
    try:
        feed = feedparser.parse("https://www.rbi.org.in/pressreleases_rss.xml")
        result = [
            {"title": e.title, "link": e.link,
             "date": e.get("published", "")[:16]}
            for e in feed.entries[:6]
        ]
        cache_set("rbi_feed", result, ttl=3600)
        return result
    except Exception:
        return cache_get_stale("rbi_feed") or []

# ── 8. COMPUTED MARKET FACTORS ───────────────────────────────────────────────
def compute_market_factors(quotes: dict) -> list:
    """Derives interpretive signals from quotes dict. No API calls."""
    factors = []

    # Crude oil impact on India
    brent = quotes.get("crude_brent", {}).get("price", 0)
    if brent:
        signal = "Negative — CAD pressure" if brent > 90 else ("Neutral" if brent > 75 else "Positive — Fiscal relief")
        factors.append({"factor": "Brent Crude", "value": f"${brent}", "signal": signal})

    # DXY pressure on rupee
    dxy = quotes.get("dxy", {}).get("price", 0)
    dxy_chg = quotes.get("dxy", {}).get("pct_change", 0)
    if dxy:
        signal = "Rupee under pressure" if dxy_chg > 0.5 else ("Rupee stable" if abs(dxy_chg) < 0.3 else "Rupee slight relief")
        factors.append({"factor": "DXY (Dollar Index)", "value": f"{dxy} ({'+' if dxy_chg>=0 else ''}{dxy_chg}%)", "signal": signal})

    # Gold — flight to safety
    gold = quotes.get("gold", {}).get("price", 0)
    gold_chg = quotes.get("gold", {}).get("pct_change", 0)
    if gold:
        signal = "Risk-off — safety buying" if gold_chg > 1.0 else ("Stable" if abs(gold_chg) < 0.5 else "Mild caution")
        factors.append({"factor": "Gold", "value": f"${gold} ({'+' if gold_chg>=0 else ''}{gold_chg}%)", "signal": signal})

    # India VIX
    vix = quotes.get("indiavix", {}).get("price", 0)
    if vix:
        if vix < 15:
            signal = "Low fear — markets complacent"
        elif vix < 20:
            signal = "Moderate caution"
        else:
            signal = "High fear — volatility spike"
        factors.append({"factor": "India VIX", "value": str(vix), "signal": signal})

    # Global risk-off composite
    sp500_chg = quotes.get("sp500", {}).get("pct_change", 0)
    if sp500_chg and dxy_chg and gold_chg:
        risk_off = (sp500_chg < -1.0) and (dxy_chg > 0.5) and (gold_chg > 0.8)
        factors.append({"factor": "Global Risk Signal", "value": "RISK OFF" if risk_off else "RISK ON", "signal": "Defensive positioning advised" if risk_off else "Normal market conditions"})

    return factors

# ── TEST RUNNER ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing fetchers...")
    q = fetch_quotes()
    print(f"Quotes: {len(q)} tickers fetched")
    n = fetch_market_news()
    print(f"News: {len(n)} items")
    rbi = fetch_rbi_feed()
    print(f"RBI feed: {len(rbi)} items")
    factors = compute_market_factors(q)
    print(f"Market factors: {len(factors)} computed")
    print("All fetchers OK.")
