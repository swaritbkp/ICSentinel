# All static config — no API calls here

YFINANCE_TICKERS = {
    # Indian indices
    "nifty50":     "^NSEI",
    "sensex":      "^BSESN",
    "banknifty":   "^NSEBANK",
    "niftyit":     "^CNXIT",
    "niftymid150": "^NSEMDCP50",
    "indiavix":    "^INDIAVIX",
    # Global indices
    "sp500":       "^GSPC",
    "nasdaq":      "^IXIC",
    "dowjones":    "^DJI",
    "ftse100":     "^FTSE",
    "nikkei225":   "^N225",
    "hangseng":    "^HSI",
    "dax":         "^GDAXI",
    # Currency
    "usdinr":      "USDINR=X",
    "eurinr":      "EURINR=X",
    "gbpinr":      "GBPINR=X",
    "jpyinr":      "JPYINR=X",
    "dxy":         "DX-Y.NYB",
    # Commodities
    "gold":        "GC=F",
    "silver":      "SI=F",
    "crude_wti":   "CL=F",
    "crude_brent": "BZ=F",
    "natgas":      "NG=F",
    # Bonds
    "us10y":       "^TNX",
    "us2y":        "^IRX",
    "us30y":       "^TYX",
}

NIFTY50_CONSTITUENTS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "LT.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS",
    "SUNPHARMA.NS", "NTPC.NS", "WIPRO.NS", "BAJFINANCE.NS", "ULTRACEMCO.NS",
]

NIFTY_SECTORS = {
    "IT":      "^CNXIT",
    "Bank":    "^NSEBANK",
    "Auto":    "^CNXAUTO",
    "FMCG":    "^CNXFMCG",
    "Pharma":  "^CNXPHARMA",
    "Realty":  "^CNXREALTY",
    "Metal":   "^CNXMETAL",
    "Energy":  "^CNXENERGY",
    "Infra":   "^CNXINFRA",
    "Finance": "^CNXFINANCE",
}

RBI_MPC_DATES_FY26 = [
    "2025-08-06", "2025-10-08", "2025-12-06",
    "2026-02-07", "2026-04-09", "2026-06-06",
]

FED_FOMC_DATES_2025_26 = [
    "2025-07-30", "2025-09-17", "2025-11-06",
    "2025-12-10", "2026-01-28", "2026-03-18",
    "2026-05-06", "2026-06-17",
]

# Manual FII/DII — update weekly from NSE website
FII_DII_MANUAL = {
    "fii_net_crore": -1250,
    "dii_net_crore": +2340,
    "last_updated": "2025-06-04",
    "source": "NSE India — update manually from nseindia.com/market-data/fii-dii-activity"
}

# India G-Sec yields — update weekly from RBI/CCIL
INDIA_GSEC_YIELDS = {
    "1y": 6.45, "2y": 6.52, "5y": 6.71, "10y": 6.88, "30y": 7.10,
    "last_updated": "2025-06-04",
    "source": "RBI — update from rbi.org.in/gsec"
}

OPENROUTER_MODEL = "google/gemini-2.0-flash-exp:free"
REFRESH_INTERVAL_SECONDS = 1800  # 30 minutes
CACHE_TTL_SECONDS = 1800
AV_DAILY_QUOTA = 25
AV_CALLS_PER_REFRESH = 4  # stay well within 25/day
