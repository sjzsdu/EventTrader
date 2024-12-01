import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL


DEFAULT_PARAMS = {
    'window': 5
}

DEFAULT_PARAMS_RANGE = {
    'window': (5, 80)
}

class OneMovingAverageStrategy(BaseStrategy):
    """
    计算一个周期的移动平均值。
    当价格高于移动平均线时，买入；
    当价格低于移动平均线时，卖出。
    """
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, 'one_moving_average', _params, _params_range, None, ['moving_avg'])
        
    def calculate_factors(self):
        window = self.parameters['window']
        self.data['moving_avg'] = self.data[PRICE_COL].rolling(window=window).mean()
        short_mavg_derivative = self.data['moving_avg'].diff()
        self.data['mavg_derivative'] = short_mavg_derivative.fillna(0)
        
    def should_buy(self, row):
        last1 = self.data.iloc[-2]
        last2 = self.data.iloc[-3]
        last3 = self.data.iloc[-4]
        return row['mavg_derivative'] > 0 and last1['mavg_derivative'] >= 0 and last2['mavg_derivative'] <= 0 and last3['mavg_derivative'] < 0
    
    def should_sell(self, row):
        last1 = self.data.iloc[-2]
        last2 = self.data.iloc[-3]
        last3 = self.data.iloc[-4]
        return row['mavg_derivative'] < 0 and last1['mavg_derivative'] <= 0 and last2['mavg_derivative'] >= 0 and last3['mavg_derivative'] > 0

    def buy_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        last3 = self.data.iloc[i-3]
        
        return row['mavg_derivative'] > 0 and last1['mavg_derivative'] > 0 and last2['mavg_derivative'] < 0 and last3['mavg_derivative'] < 0

    def sell_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        last3 = self.data.iloc[i-3]
        return row['mavg_derivative'] < 0 and last1['mavg_derivative'] < 0 and last2['mavg_derivative'] > 0 and last3['mavg_derivative'] > 0
    
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA')
        ]   
