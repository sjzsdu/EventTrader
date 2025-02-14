import pandas as pd
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL

DEFAULT_PARAMS = {
    'window': 5
}

DEFAULT_PARAMS_RANGE = {
    'window': (5, 30)
}

class MA1Strategy(BaseStrategy):
    """
MA (Moving Average) 移动平均策略
使用移动平均值的变化率来产生交易信号：
- 当变化率由负转正时买入
- 当变化率由正转负时卖出
    """
    name = 'ma1'
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, MA1Strategy.name, _params, _params_range, None, ['moving_avg'])
        
    def calculate_factors(self):
        window = self.parameters['window']
        self.data['moving_avg'] = self.data[PRICE_COL].rolling(window=window).mean()
        self.data['mavg_derivative'] = self.data['moving_avg'].diff().fillna(0)
        
    def buy_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        return (row[PRICE_COL] < row['moving_avg'] and 
                row['mavg_derivative'] > 0 and 
                last1['mavg_derivative'] <= 0 and 
                last2['mavg_derivative'] < 0)

    def sell_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
        last1 = self.data.iloc[i-1]
        last2 = self.data.iloc[i-2]
        return (row[PRICE_COL] > row['moving_avg'] and 
                row['mavg_derivative'] < 0 and 
                last1['mavg_derivative'] >= 0 and 
                last2['mavg_derivative'] > 0)
    
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA')
        ]
