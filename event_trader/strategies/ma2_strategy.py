import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL
from event_trader.utils import plot_line_chart
DEFAULT_PARAMS = {
    'short_window': 5,
    'long_window': 20,
}

DEFAULT_PARAMS_RANGE = {
    'short_window': (3, 12),
    'long_window': (12, 40),
}

DEFAULT_PARAMS_STEP = {
    'short_window': 2,
    'long_window': 2,
}

class MA2Strategy(BaseStrategy):
    """
移动平均价格：计算两个不同周期的移动平均值。
当短周期的移动平均线高于长周期的移动平均线时，买入；
当短周期的移动平均线低于长周期的移动平均线时，卖出。
    """
    name = 'ma2'
    def __init__(self, stock_data: StockData, *, sub_path = None, params = None, params_range=None, params_step=None, factors=None):
        if factors is None:
            factors = ['short_mavg', 'long_mavg']
        if sub_path is None:
            sub_path = MA2Strategy.name
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        _params_step = params_step if params_step is not None else DEFAULT_PARAMS_STEP
        super().__init__(stock_data, sub_path, _params, _params_range, _params_step, factors)

    def calculate_factors(self):
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        # 计算短期和长期移动平均
        self.data['short_mavg'] = self.data[PRICE_COL].rolling(window=short_window).mean()
        self.data['long_mavg'] = self.data[PRICE_COL].rolling(window=long_window).mean()
        
       # 使用单独的变量来存储列，然后进行填充
        short_mavg_derivative = self.data['short_mavg'].diff()
        self.data['short_mavg_derivative'] = short_mavg_derivative.fillna(0)

        long_mavg_derivative = self.data['long_mavg'].diff()
        self.data['long_mavg_derivative'] = long_mavg_derivative.fillna(0)

        
    def validate_parameter(self, parameters):
        if parameters['short_window'] >= parameters['long_window']:
            return False
        return True
    
    def buy_signal(self, row, i) -> bool:
        if i < 2 or pd.isna(row['short_mavg']) or pd.isna(row['long_mavg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        return (row['short_mavg'] < row['long_mavg'] and
                row['long_mavg_derivative'] > 0 and
                row['short_mavg_derivative'] > 0 and
                last1['short_mavg_derivative'] <= 0 and
                last2['short_mavg_derivative'] < 0)

    def sell_signal(self, row, i) -> bool:
        if i < 2 or pd.isna(row['short_mavg']) or pd.isna(row['long_mavg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        return (row['short_mavg'] > row['long_mavg'] and
                row['long_mavg_derivative'] < 0 and
                row['short_mavg_derivative'] < 0 and
                last1['short_mavg_derivative'] >= 0 and
                last2['short_mavg_derivative'] > 0)
        
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['short_mavg'], width=0.8, color='blue', label=f'{self.short_window}-Day MA'),
            mpf.make_addplot(data['long_mavg'], width=0.8, color='orange', label=f'{self.long_window}-Day MA')
        ]
        
    def show_factors(self):
        plot_line_chart(
            self.data, ['short_mavg_derivative', 'long_mavg_derivative'],
            title='Moving avarage derivative',  ylabel= 'derivative')
