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
    name = 'vma'
    def __init__(self, stock_data: StockData, params = None, params_range = None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, VMAStrategy.name, _params, _params_range, None, ['moving_avg'])
        
    def calculate_factors(self):
        window = self.parameters['window']
        self.data['moving_avg'] = self.data['成交量'].rolling(window=window).mean()
        
    def buy_signal(self, row, i) -> bool:
        if i < self.window or pd.isna(row['moving_avg']):
            return False
            
        # 量价齐升
        if i > 0:
            last = self.data.iloc[i-1]
            if row['成交量'] > last['成交量'] and row['收盘'] > last['收盘']:
                return True
                
        # 量价齐跌后的买入机会
        if i > 0:
            last = self.data.iloc[i-1]
            if row['成交量'] < last['成交量'] and row['收盘'] < last['收盘']:
                # 检查是否在重要支撑位附近
                if row['收盘'] <= row['最低'] * 1.02:  # 在最低价2%范围内
                    return True
                    
        # 价不跌量大增
        if i > 0:
            last = self.data.iloc[i-1]
            if row['成交量'] > 2 * last['成交量'] and row['收盘'] >= last['收盘']:
                return True
                
        # 成交量突破
        if row['成交量'] > 2 * row['moving_avg'] and row['收盘'] > self.data.iloc[i-self.window:i]['收盘'].max():
            return True
            
        return False

    def sell_signal(self, row, i) -> bool:
        if i < self.window + 3 or pd.isna(row['moving_avg']):
            return False
            
        # 量价背离（价格上涨但成交量减少）
        if i > 0:
            last = self.data.iloc[i-1]
            if row['成交量'] < last['成交量'] and row['收盘'] > last['收盘']:
                return True
                
        # 量价背离（价格下跌但成交量增加）
        if i > 0:
            last = self.data.iloc[i-1]
            if row['成交量'] > last['成交量'] and row['收盘'] < last['收盘']:
                return True
                
        # 在重要阻力位附近
        if row['收盘'] >= row['最高'] * 0.98:  # 在最高价2%范围内
            return True
            
        return False
    
    def get_plots(self, data):
        return [
            mpf.make_addplot(data['moving_avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA')
        ]
