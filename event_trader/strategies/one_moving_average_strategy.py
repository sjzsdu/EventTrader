import os
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from event_trader.stock_data import StockData
import mplfinance as mpf
import matplotlib.pyplot as plt


PRICE_COL = "收盘"
DEFAULT_PARAMS = {
    'window': 5
}

class OneMovingAverageStrategy(BaseStrategy):
    """
    计算一个周期的移动平均值。
    当价格高于移动平均线时，买入；
    当价格低于移动平均线时，卖出。
    """
    def __init__(self, stock_data: StockData, params = None):
        super().__init__(stock_data, 'one_moving_average')
        if params is not None:
            self.default_params = { **DEFAULT_PARAMS, **params }
        else:
            self.default_params = DEFAULT_PARAMS
        self.load_parameters(self.default_params)
        self.data: pd.DataFrame = stock_data.hist.copy()
        

    def calculate_factors(self):
        window = self.parameters['window']
        self.data['moving_avg'] = self.data[PRICE_COL].rolling(window=window).mean()

    def buy_signal(self, row) -> bool:
        return row[PRICE_COL] > row['moving_avg']

    def sell_signal(self, row) -> bool:
        return row[PRICE_COL] < row['moving_avg']

    def calculate_profit(self) -> float:
        initial_investment = 1000000
        cash = initial_investment
        shares = 0

        for index, row in self.data.iterrows():
            if pd.isna(row['moving_avg']):
                continue

            current_price = row[PRICE_COL]

            if self.buy_signal(row) and cash > 0:
                max_shares_to_buy = cash // current_price
                shares_to_buy = (max_shares_to_buy // 100) * 100
                shares += shares_to_buy
                cash -= shares_to_buy * current_price
            elif self.sell_signal(row) and shares > 0:
                cash += shares * current_price
                shares = 0

        if shares > 0:
            final_price = self.data[PRICE_COL].iloc[-1]
            cash += shares * final_price
        profit = (cash - initial_investment) / initial_investment * 100
        return profit

    def optimize_parameters(self, window_range=(5, 50)):
        best_profit = -np.inf
        best_window = self.parameters['window']
        for window in range(*window_range):
            self.parameters['window'] = window
            self.calculate_factors()
            profit = self.calculate_profit()
            if profit > best_profit:
                best_profit = profit
                best_window = window
        self.parameters['window'] = best_window
        print(f"Optimized parameter: Window = {self.parameters['window']}, Profit = {best_profit}")
        self.save_parameters()
        return self
        
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
