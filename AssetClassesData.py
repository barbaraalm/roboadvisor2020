import pandas as pd
import numpy as np

# Assets daily prices

close_price = pd.read_json("AssetsDailyPrices.json")
close_price.index = pd.to_datetime(close_price.index)

Assets = ['US Equity', 'Treasury Bonds', 'Real Estate', 'Commodities', 'ESG']

daily_return = close_price[Assets].pct_change(1)
monthly_return = close_price[Assets].pct_change(21)
annual_return = close_price[Assets].pct_change(252)

#Risk Free Rate
risk_free = pd.read_json("RiskFreeRate.json")
risk_free.index = pd.to_datetime(risk_free.index)

daily_rf = risk_free['rf_daily']
annual_rf = risk_free['rf_annual']



