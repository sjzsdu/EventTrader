import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL


DEFAULT_PARAMS = {
    'short': 12,
    'long': 26,
    'middle': 9,
}

DEFAULT_PARAMS_RANGE = {
    'short': (2, 30),
    'long': (3, 60),
    'middle': (2, 30),
}


class MACDStrategy(BaseStrategy):
    """
    MACD 移动平均线收敛/发散指标（Moving Average Convergence Divergence）
    """
    name = 'macd'
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, MACDStrategy.name, _params, _params_range, None, ['DIF', 'DEA', 'MACD'])
        
    def calculate_factors(self):
        data = self.data
        # 使用pandas的向量化操作
        data['EMA_short'] = data[PRICE_COL].ewm(span=self.short, adjust=False).mean()
        data['EMA_long'] = data[PRICE_COL].ewm(span=self.long, adjust=False).mean()
        data['DIF'] = data['EMA_short'] - data['EMA_long']
        data['DEA'] = data['DIF'].ewm(span=self.middle, adjust=False).mean()
        data['MACD'] = 2 * (data['DIF'] - data['DEA'])
        
    def validate_parameter(self, parameters):
        if parameters['short'] >= parameters['long']:
            return False
        return True 
    
    def buy_signal(self, row, i) -> bool:
        if i == 0 or pd.isna(row['DIF']) or pd.isna(row['DEA']):
            return False
        last = self.data.iloc[i-1]
        # Check if DIF crosses above DEA (Golden Cross)
        if row['DIF'] > row['DEA'] and last['DIF'] <= last['DEA']:
            return True
        
        # Optionally, check if MACD histogram is turning positive from negative
        if row['MACD'] > 0 and last['MACD'] <= 0:
            return True
        
        return False

    def sell_signal(self, row, i) -> bool:
        if i == 0 or pd.isna(row['DIF']) or pd.isna(row['DEA']):
            return False
        last = self.data.iloc[i-1]
        # Check if DIF crosses below DEA (Dead Cross)
        if row['DIF'] < row['DEA'] and last['DIF'] >= last['DEA']:
            return True
        
        # Optionally, check if MACD histogram is turning negative from positive
        if row['MACD'] < 0 and last['MACD'] >= 0:
            return True
        
        return False
        
    def get_plots(self, data):
        high = data['最高'].max()
        lower = data['最低'].max()
        ratio = (high - lower) / 100
        return [
            mpf.make_addplot(data['DIF'] * ratio, color='blue', width=1, label='DIF'),
            mpf.make_addplot(data['DEA'] * ratio, color='orange', width=1, label='DEA'),
            mpf.make_addplot(data['MACD'] * ratio, color='red', width=1, label='MACD')
        ]