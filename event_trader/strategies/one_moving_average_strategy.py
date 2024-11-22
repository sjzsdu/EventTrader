import pandas as pd
from .base_strategy import BaseStrategy
from event_trader.stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL


DEFAULT_PARAMS = {
    'window': 5
}

DEFAULT_PARAMS_RANGE = {
    'window': (3, 80)
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
        
    def should_buy(self, row):
        return row[PRICE_COL] >= row['moving_avg']
    
    def should_sell(self, row):
        return row[PRICE_COL] <= row['moving_avg']

    def buy_signal(self, row, i) -> bool:
        if i == 0 or pd.isna(row['moving_avg']):
            return False
        last = self.data.iloc[i-1]
        return self.should_buy(row) and self.should_sell(last)

    def sell_signal(self, row, i) -> bool:
        if i == 0 or pd.isna(row['moving_avg']):
            return False
        last = self.data.iloc[i-1]
        return self.should_sell(row) and self.should_buy(last)
    
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA')
        ]   
