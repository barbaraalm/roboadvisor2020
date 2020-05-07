import pandas as pd
import numpy as np
import os
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Assets daily prices
script_dir = os.path.dirname(__file__) # the cwd relative path of the script file
rel_path = "AssetsDailyPrices copy.xlsx" # the target file
rel_to_cwd_path = os.path.join(script_dir, rel_path) # the cwd-relative path of the target file
close_price = pd.read_excel(rel_to_cwd_path,  index_col= 'Date')
close_price.index = pd.to_datetime(close_price.index, format="%Y-%m-%d")

Assets = close_price.columns

daily_return = close_price[Assets].pct_change(1)
monthly_return = close_price[Assets].pct_change(21)
annual_return = close_price[Assets].pct_change(252)
cum_daily_return = np.exp(np.log1p(daily_return).cumsum())



#Risk Free Rate
rel_path = "RiskFreeRate.xlsx" 
rel_to_cwd_path = os.path.join(script_dir, rel_path)
risk_free = pd.read_excel(rel_to_cwd_path,  index_col= 'Date')
risk_free.index = pd.to_datetime(risk_free.index, format="%Y-%m-%d")

daily_rf = risk_free['rf_daily']
monthly_rf = risk_free['rf_monthly']
annual_rf = risk_free['rf_annual']



