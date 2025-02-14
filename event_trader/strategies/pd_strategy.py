import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL


DEFAULT_PARAMS = {
    'window': 5,
    'percent': 10
}

DEFAULT_PARAMS_RANGE = {
    'window': (3, 35),
    'percent': (2, 20)
}

class PriceDeviationStrategy(BaseStrategy):
    """
股价偏移过大后会回归。
股价降到移动平均价格下方的一定比例后触发回归，是买入的时机；
估计升到了移动平均价格上方一定比例后触发下调，是卖出的时机；
    """
    name = 'pd'
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, PriceDeviationStrategy.name, _params, _params_range, None, ['moving_avg'])
        
    def calculate_factors(self):
        self.data['moving_avg'] = self.data[PRICE_COL].rolling(window=self.window).mean()
        self.data['percent'] = (self.data[PRICE_COL] - self.data['moving_avg']) * 100 / self.data['moving_avg']
        
    def buy_signal(self, row, i) -> bool:
        if i < self.window + 2:
            return False
        return row['percent'] <=  -self.percent

    def sell_signal(self, row, i) -> bool:
        if i < self.window + 2:
            return False
        return row['percent'] >=  self.percent
    
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA')
        ]   
