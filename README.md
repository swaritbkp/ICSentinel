# IC Sentinel

### What is IC Sentinel
IC Sentinel is a free, self-hosted market intelligence dashboard built specifically for Investment Counsellors (ICs). 
It aggregates macro economic indicators, indices, commodities, yields, and news, providing a single consolidated viewport.
An integrated AI engine parses live market feeds and outputs HNI client-ready talking points and risk alert summaries.

---

### Free API Keys (get all 3 in under 5 minutes)
To access AI commentary and sentiment analysis, obtain the following free keys:
* **Alpha Vantage**: [Get Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key) — Free, requires email signup only. Provides 25 calls/day (used for news sentiment and US Treasury yields).
* **Finnhub**: [Register Finnhub Account](https://finnhub.io/register) — Free, 60 calls/minute limit. Used as a robust news aggregator fallback.
* **OpenRouter**: [Generate OpenRouter Keys](https://openrouter.ai/keys) — Free account, supports `google/gemini-2.0-flash-exp:free` for generating client briefing insights (200 requests/day).

---

### Local Setup (5 steps)
1. Clone the repository:
   ```bash
   git clone <your-repo>
   ```
2. Navigate to the project directory:
   ```bash
   cd ic_sentinel
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment file and populate it with your API keys:
   ```bash
   cp .env.example .env
   ```
5. Run the Streamlit orchestrator locally:
   ```bash
   streamlit run app.py
   ```

---

### Streamlit Cloud Deployment (free)
1. Push your cloned/forked repository to a public or private GitHub repository (verify that `.env` and `.streamlit/secrets.toml` are correctly ignored).
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in using your GitHub account.
3. Click **New app**, select your repository, specify the `main` branch, and set the entry file to `app.py`.
4. In the setup window, click **Advanced settings** -> **Secrets**.
5. Paste the contents of `.streamlit/secrets.toml` template into the text area, replacing the placeholders with your actual API keys.
6. Click **Deploy**. Streamlit will configure the virtual environment and share your dashboard URL.

---

### Manual Data Updates
Some specialized indicators are maintained statically to avoid web scraping blockers:
* **FII/DII flow**: Update the `FII_DII_MANUAL` dictionary weekly inside [data/config.py](file:///c:/Users/SwaritSharma/Desktop/Dashboard-ag/data/config.py) from the [NSE India FII/DII activity page](https://www.nseindia.com/market-data/fii-dii-activity).
* **India G-Sec yields**: Update the `INDIA_GSEC_YIELDS` dictionary weekly inside [data/config.py](file:///c:/Users/SwaritSharma/Desktop/Dashboard-ag/data/config.py) from the [RBI G-Sec page](https://www.rbi.org.in/gsec).
* **RBI MPC dates**: Already pre-populated for FY2025-26 under `RBI_MPC_DATES_FY26`.

---

### What's included

| Zone | UI Component | Description | Data Sources |
|---|---|---|---|
| **Zone 1** | Ticker Bar | Real-time horizontal bar tracking key Indian & global benchmarks, FX, gold, and Brent crude. | `yfinance` |
| **Zone 2** | Market Panel | Side-by-side overview of Indian Indices, Global Macro, manual FII/DII flows, event radar, and latest RBI RSS press releases. | `yfinance`, RBI RSS Feed, Static configs |
| **Zone 3** | Charts | Interactive candlestick & line plots with customizable periods, overlays (MAs, Bollinger), volume, and Nifty sector treemaps. | `yfinance` |
| **Zone 4** | News + Factors | Sentiment-classified economic news alongside derived composite indicator alerts (VIX fear, CAD oil impact, DXY pressures). | Alpha Vantage, Finnhub, Google News RSS |
| **Zone 5** | Debt Panel | Collapsible fixed-income section mapping yield curves (India vs US) and calculating curve spreads (Normal, Flat, Inverted). | Alpha Vantage, `yfinance`, RBI G-Sec yield config |
| **Zone 6** | AI Insights | Large Language Model panel outputting structured briefings, client-ready talking points, and warning signals. | OpenRouter (`google/gemini-2.0-flash-exp:free`) |

---

### Disclaimer
This application is for informational purposes only. It does not constitute investment or financial advice. All data is provided "as is" and may be delayed.
