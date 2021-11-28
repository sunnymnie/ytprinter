import pandas as pd
import numpy as np
import math
import statsmodels.formula.api as sm

class Magic:
    def __init__(self, lookback):
        self.lookback = lookback
        
    def get_z_score(self, a, b):
        """Returns the latest zscore between dataframes a and b. IF NAN, RETURN PREVIOUS"""
        a = a.set_index("timestamp") #Do not set inplace cause reference
        b = b.set_index("timestamp")

        df = pd.to_numeric(a.open.rename("A")).to_frame()
        df["B"] = pd.to_numeric(b.open)

        df.dropna(inplace=True)

        results = sm.ols(formula="B ~ A", data=df[['B', 'A']]).fit()
        hr = results.params[1]
        spread = pd.Series((df['B'] - hr * df['A'])).rename("spread").to_frame()
        spread["mean"] = spread.spread.rolling(self.lookback).mean()
        spread["std"] = spread.spread.rolling(self.lookback).std()
        spread["zscore"] = pd.Series((spread["spread"]-spread["mean"])/spread["std"])
        return self.get_non_nan_zscore(spread)    
    
    def get_non_nan_zscore(self, spread):
        """loops through spread finding latest non-nan zscore"""
        zscore = spread.iloc[-1].zscore
        i = 2
        while math.isnan(zscore):
            zscore = spread.iloc[-i].zscore
            i += 1
        return zscore