import yfinance as yf
from data.config import YFINANCE_TICKERS

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
            close_series = close_series.dropna()
            if len(close_series) < 2:
                print(f"{name} ({symbol}): series length < 2")
                continue
            prev = float(close_series.iloc[-2])
            curr = float(close_series.iloc[-1])
            print(f"{name} ({symbol}): prev={prev}, curr={curr}, change={curr-prev:.2f}")
        except Exception as e:
            print(f"Error processing {name} ({symbol}): {e}")
except Exception as e:
    print("Download failed with exception:", e)
