import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DataProcessor:
    def __init__(self):
        self.scaler = MinMaxScaler()
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        data['H-L'] = data['high'] - data['low']
        data['H-PC'] = (data['high'] - data['close'].shift(1)).abs()
        data['L-PC'] = (data['low'] - data['close'].shift(1)).abs()
        data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr = data['TR'].rolling(window=period).mean()
        return atr
    
    def normalize_data(self, data: np.array) -> np.array:
        return self.scaler.fit_transform(data)
    
    def calculate_volatility(self, data: pd.Series, period: int = 14) -> float:
        return data.pct_change().rolling(window=period).std().iloc[-1]
