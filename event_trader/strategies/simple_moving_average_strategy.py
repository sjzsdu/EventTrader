import os
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from event_trader.stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL

DEFAULT_PARAMS = {
    'short_window': 5,
    'long_window': 20,
}

DEFAULT_PARAMS_RANGE = {
    'short_window': (2, 20),
    'long_window': (25, 80),
}

class SimpleMovingAverageStrategy(BaseStrategy):
    """
    计算两个不同周期的移动平均值。
    当短周期的移动平均线高于长周期的移动平均线时，买入；
    当短周期的移动平均线低于长周期的移动平均线时，卖出。
    """
    def __init__(self, stock_data: StockData, params = None, params_range=None):
        _params = params if params is not None else DEFAULT_PARAMS
        _params_range = params_range if params_range is not None else DEFAULT_PARAMS_RANGE
        super().__init__(stock_data, 'simple_moving_average', _params, _params_range)
    
    def load_data(self):
        return self.stock_data.hist.copy()

    def calculate_factors(self):
        short_window= self.parameters['short_window']
        long_window= self.parameters['long_window']
        self.data['short_mavg'] = self.data[PRICE_COL].rolling(window=short_window).mean()
        self.data['long_mavg'] = self.data[PRICE_COL].rolling(window=long_window).mean()

    def buy_signal(self, row) -> bool:
        if pd.isna(row['short_mavg']) or pd.isna(row['long_mavg']):
             return False
        return row['short_mavg'] > row['long_mavg']

    def sell_signal(self, row) -> bool:
        if pd.isna(row['short_mavg']) or pd.isna(row['long_mavg']):
             return False
        return row['short_mavg'] < row['long_mavg']
        
    def show(self):
        stock_data_copy = self.data.copy()
        stock_data_copy.rename(columns={
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume'
        }, inplace=True)
        
        # Convert index to datetime
        stock_data_copy.index = pd.to_datetime(stock_data_copy.index)
        
        # Prepare a list for addplot
        add_plots = []
        
        # Calculate and add moving averages for short_window and long_window
        stock_data_copy['Short_MA'] = stock_data_copy['Close'].rolling(window=self.short_window).mean()
        stock_data_copy['Long_MA'] = stock_data_copy['Close'].rolling(window=self.long_window).mean()
        
        add_plots.append(mpf.make_addplot(stock_data_copy['Short_MA'], width=0.8, color='blue', label=f'{self.short_window}-Day MA'))
        add_plots.append(mpf.make_addplot(stock_data_copy['Long_MA'], width=0.8, color='orange', label=f'{self.long_window}-Day MA'))
        
        # Define the style with red for up and green for down
        mc = mpf.make_marketcolors(up='red', down='green', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        figsize = (16, 8)  # (宽度, 高度)
        # Plot with moving averages
        mpf.plot(stock_data_copy, type='candle', volume=True, 
                title=f'{self.stock_data.code} Candle Figure', ylabel='Price',
                addplot=add_plots, style=s, ylabel_lower='Volume', figsize=figsize)


