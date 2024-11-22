import pandas as pd
from .base_strategy import BaseStrategy
from .simple_moving_average_strategy import SimpleMovingAverageStrategy
from event_trader.stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL

DEFAULT_PARAMS = {
    'short_window': 5,
    'long_window': 20,
    'sell_window': 5,
}

DEFAULT_PARAMS_RANGE = {
    'short_window': (2, 20),
    'long_window': (3, 80),
    'sell_window': (3, 30),
}

class UpdateSimpleMovingAverageStrategy(SimpleMovingAverageStrategy):
    """
    升级版的移动平均指标。
    """
    def __init__(self, stock_data: StockData, params = None, params_range=None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(
            stock_data, 
            sub_path='update_simple_moving_average', 
            params=_params, 
            params_range=_params_range, 
            factors=['short_mavg', 'long_mavg', 'sell_mavg']
        )

    def calculate_factors(self):
        super().calculate_factors()
        self.data['sell_mavg'] = self.data[PRICE_COL].rolling(window=self.sell_window).mean()
    
    def should_sell(self, row):
        return row[PRICE_COL] < row['sell_mavg']

    def sell_signal(self, row, i) -> bool:
        if i == 0 or pd.isna(row['sell_mavg']):
            return False
        return self.should_sell(row)
        
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['short_mavg'], width=0.8, color='blue', label=f'{self.short_window}-Day MA'),
            mpf.make_addplot(data['long_mavg'], width=0.8, color='orange', label=f'{self.long_window}-Day MA'),
            mpf.make_addplot(data['sell_mavg'], width=0.8, color='red', label=f'{self.sell_window}-Day MA')
        ]


