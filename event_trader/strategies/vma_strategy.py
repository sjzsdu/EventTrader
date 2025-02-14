import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from china_stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL
from event_trader.utils import is_continuous_growth

DEFAULT_PARAMS = {
    'window': 10
}

DEFAULT_PARAMS_RANGE = {
    'window': (5, 50)
}

# 常量定义
RSI_PERIOD = 14
VOLUME_THRESHOLD = 2.5
PRICE_CHANGE_THRESHOLD = 0.03
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

class VMAStrategy(BaseStrategy):
    """
成交量或者换手率指标。
成交量大于移动平均线的2倍;
当价格低于移动平均线时，卖出。
    """
    name = 'vma'
    
    def __init__(self, stock_data: StockData, params=None, params_range=None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, VMAStrategy.name, _params, _params_range, None, ['volume_ma', 'price_ma', 'rsi'])
        
    def calculate_factors(self):
        window = self.parameters['window']
        self.data['volume_ma'] = self.data['成交量'].rolling(window=window).mean()
        self.data['price_ma'] = self.data[PRICE_COL].rolling(window=window).mean()
        self.calculate_rsi()
        
    def calculate_rsi(self):
        delta = self.data[PRICE_COL].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        
    def buy_signal(self, row, i) -> bool:
        if i < self.parameters['window'] or pd.isna(row['volume_ma']) or pd.isna(row['rsi']):
            return False
            
        # 成交量突破且价格处于上升趋势
        volume_breakout = row['成交量'] > VOLUME_THRESHOLD * row['volume_ma']
        price_uptrend = row[PRICE_COL] > row['price_ma'] * (1 + PRICE_CHANGE_THRESHOLD)
        
        # RSI超卖
        rsi_oversold_condition = row['rsi'] < RSI_OVERSOLD
        
        # 连续3天价格上涨
        price_continuous_up = is_continuous_growth(self.data[PRICE_COL].iloc[i-3:i+1], n=3)
        
        return volume_breakout and price_uptrend and rsi_oversold_condition and price_continuous_up


    def sell_signal(self, row, i) -> bool:
        if i < self.parameters['window'] or pd.isna(row['volume_ma']) or pd.isna(row['rsi']):
            return False
            
        # 成交量突破且价格处于下降趋势
        volume_breakout = row['成交量'] > VOLUME_THRESHOLD * row['volume_ma']
        price_downtrend = row[PRICE_COL] < row['price_ma'] * (1 - PRICE_CHANGE_THRESHOLD)
        
        # RSI超买
        rsi_overbought_condition = row['rsi'] > RSI_OVERBOUGHT
        
        # 连续3天价格下跌
        price_continuous_down = price_continuous_down = is_continuous_growth(self.data[PRICE_COL].iloc[i-3:i+1], n=3, reverse=True)
        
        return volume_breakout and price_downtrend and rsi_overbought_condition and price_continuous_down

    def get_plots(self, data):
        return [
            mpf.make_addplot(data['volume_ma'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day Volume MA'),
            mpf.make_addplot(data['price_ma'], width=0.8, color='red', label=f'{self.parameters["window"]}-Day Price MA'),
            mpf.make_addplot(data['rsi'], panel=1, color='purple', label='RSI')
        ]
