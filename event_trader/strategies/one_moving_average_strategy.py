import os
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from event_trader.stock_data import StockData
import mplfinance as mpf
from event_trader.config import PRICE_COL


DEFAULT_PARAMS = {
    'window': 5
}

DEFAULT_PARAMS_RANGE = {
    'window': (5, 50)
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
        super().__init__(stock_data, 'one_moving_average', _params, _params_range)
        
        
    def load_data(self):
        return self.stock_data.hist.copy()
        

    def calculate_factors(self):
        window = self.parameters['window']
        self.data['moving_avg'] = self.data[PRICE_COL].rolling(window=window).mean()

    def buy_signal(self, row) -> bool:
        if pd.isna(row['moving_avg']):
             return False
        return row[PRICE_COL] > row['moving_avg']

    def sell_signal(self, row) -> bool:
        if pd.isna(row['moving_avg']):
             return False
        return row[PRICE_COL] < row['moving_avg']

        
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
        
        # Calculate and add moving averages for the specified window
        stock_data_copy['Moving_Avg'] = stock_data_copy['Close'].rolling(window=self.parameters['window']).mean()
        
        add_plots.append(mpf.make_addplot(stock_data_copy['Moving_Avg'], width=0.8, color='blue', label=f'{self.parameters["window"]}-Day MA'))
        
        # Define the style with red for up and green for down
        mc = mpf.make_marketcolors(up='red', down='green', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        figsize = (16, 8)  # (宽度, 高度)
        # Plot with moving averages
        mpf.plot(stock_data_copy, type='candle', volume=True, 
                title=f'{self.stock_data.code} Candle Figure', ylabel='Price',
                addplot=add_plots, style=s, ylabel_lower='Volume', figsize=figsize)
