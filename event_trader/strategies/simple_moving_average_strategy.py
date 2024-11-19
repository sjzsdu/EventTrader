import pandas as pd
from .base_strategy import BaseStrategy
from event_trader.stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL

DEFAULT_PARAMS = {
    'short_window': 5,
    'long_window': 20,
}

DEFAULT_PARAMS_RANGE = {
    'short_window': (2, 20),
    'long_window': (20, 80),
}

class SimpleMovingAverageStrategy(BaseStrategy):
    """
    计算两个不同周期的移动平均值。
    当短周期的移动平均线高于长周期的移动平均线时，买入；
    当短周期的移动平均线低于长周期的移动平均线时，卖出。
    """
    def __init__(self, stock_data: StockData, params = None, params_range=None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, 'simple_moving_average', _params, _params_range, None)

    def calculate_factors(self):
        short_window= self.parameters['short_window']
        long_window= self.parameters['long_window']
        self.data['short_mavg'] = self.data[PRICE_COL].rolling(window=short_window).mean()
        self.data['long_mavg'] = self.data[PRICE_COL].rolling(window=long_window).mean()

    def buy_signal(self, row, i) -> bool:
        if i > 0 and pd.isna(row['short_mavg']) or pd.isna(row['long_mavg']):
            return False
        last = self.data.iloc[i-1]
        return row['short_mavg'] >= row['long_mavg'] and last['short_mavg'] < last['long_mavg']

    def sell_signal(self, row, i) -> bool:
        if i > 0 and pd.isna(row['short_mavg']) or pd.isna(row['long_mavg']):
            return False
        last = self.data.iloc[i-1]
        return row['short_mavg'] <= row['long_mavg'] and last['short_mavg'] > last['long_mavg']
        
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['short_mavg'], width=0.8, color='blue', label=f'{self.short_window}-Day MA'),
            mpf.make_addplot(data['long_mavg'], width=0.8, color='orange', label=f'{self.long_window}-Day MA')
        ]


