import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL
from event_trader.utils import is_continuous_growth

DEFAULT_PARAMS = {
    'window': 5
}

DEFAULT_PARAMS_RANGE = {
    'window': (3, 50)
}

class VMAStrategy(BaseStrategy):
    """
    成交量或者换手率指标。
    成交量大于移动平均线的2倍;
    当价格低于移动平均线时，卖出。
    """
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, 'volume_moving_average', _params, _params_range, None, ['moving_avg'])
        
    def calculate_factors(self):
        window = self.parameters['window']
        self.data['moving_avg'] = self.data['成交量'].rolling(window=window).mean()
        
    def should_buy(self, row):
        return self.buy_signal(row, self.data.index.get_loc(row.name))
    
    def should_sell(self, row):
        return self.sell_signal(row, self.data.index.get_loc(row.name))

    def buy_signal(self, row, i) -> bool:
        if i < self.window or pd.isna(row['moving_avg']):
            return False
        return row['成交量'] > 2 * row['moving_avg']

    def sell_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
    
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA')
        ]   
