import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL
from event_trader.utils import is_continuous_growth

DEFAULT_PARAMS = {
    'window': 5,
    'volume': 5
}

DEFAULT_PARAMS_RANGE = {
    'window': (3, 50),
    'volume': (3, 30)
}

class OneMovingAverageStrategy(BaseStrategy):
    """
    移动平均值的变化率，当变化率由负开始走平时买入，当变化率由正开始走平时卖出。
    当价格高于移动平均线时，买入；
    当价格低于移动平均线时，卖出。
    """
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, 'one_moving_average', _params, _params_range, None, ['moving_avg', 'moving_volume'])
        
    def calculate_factors(self):
        window = self.parameters['window']
        volume = self.parameters['volume']
        self.data['moving_avg'] = self.data[PRICE_COL].rolling(window=window).mean()
        self.data['moving_volume'] = self.data['成交量'].rolling(window=volume).mean()
        short_mavg_derivative = self.data['moving_avg'].diff()
        self.data['mavg_derivative'] = short_mavg_derivative.fillna(0)
        
    def should_buy(self, row):
        last1 = self.data.iloc[-2]
        last2 = self.data.iloc[-3]
        return row['mavg_derivative'] > 0 and last1['mavg_derivative'] <= 0 and last2['mavg_derivative'] > 0 and row['成交量'] > 1.5 * row['moving_volume']
    
    def should_sell(self, row):
        last1 = self.data.iloc[-2]
        last2 = self.data.iloc[-3]
        return row['mavg_derivative'] < 0 and last1['mavg_derivative'] >= 0 and last2['mavg_derivative'] > 0

    def buy_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        return row['mavg_derivative'] > 0 and last1['mavg_derivative'] <= 0 and last2['mavg_derivative'] < 0 and row['成交量'] > 1.5 * row['moving_volume']

    def sell_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        return row['mavg_derivative'] < 0 and last1['mavg_derivative'] >= 0 and last2['mavg_derivative'] > 0
    
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA'),
            mpf.make_addplot(data['moving_volume'], width=0.8, color='blue', label=f'{self.parameters["volume"]}-Day MA')
        ]   
