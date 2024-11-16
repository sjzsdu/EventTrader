import os
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from event_trader.stock_data import StockData
import mplfinance as mpf

S_W = 'short_window'
L_W = 'long_window'
PRICE_COL = "收盘"

class SimpleMovingAverageStrategy(BaseStrategy):
    def __init__(self, stock_data: StockData, short_window: int = 10, long_window: int = 30):
        super().__init__(stock_data)
        self.short_window, self.long_window = self.load_parameters(short_window, long_window)
        self.data: pd.DataFrame = stock_data.hist.copy()
        self.data.dropna(subset=[PRICE_COL], inplace=True)  # Remove rows with NaN in PRICE_COL
        self.calculate_factors()  # 预先计算移动平均值

    def load_parameters(self, default_short: int, default_long: int):
        params_path = os.path.join('params', 'simple_moving_average', f'{self.stock_data.code}.csv')
        if os.path.isfile(params_path):
            df = pd.read_csv(params_path)
            return df[S_W].iloc[0], df[L_W].iloc[0]
        return default_short, default_long

    def save_parameters(self):
        params_path = os.path.join('params', 'simple_moving_average', f'{self.stock_data.code}.csv')
        os.makedirs(os.path.dirname(params_path), exist_ok=True)
        df = pd.DataFrame({S_W: [self.short_window], L_W: [self.long_window]})
        df.to_csv(params_path, index=False)

    def calculate_factors(self):
        self.data['short_mavg'] = self.data[PRICE_COL].rolling(window=self.short_window).mean()
        self.data['long_mavg'] = self.data[PRICE_COL].rolling(window=self.long_window).mean()

    def buy_signal(self, row) -> bool:
        return row['short_mavg'] > row['long_mavg']

    def sell_signal(self, row) -> bool:
        return row['short_mavg'] < row['long_mavg']

    def calculate_profit(self) -> float:
        initial_investment = 1000000
        cash = initial_investment
        shares = 0

        for index, row in self.data.iterrows():
            if pd.isna(row['short_mavg']) or pd.isna(row['long_mavg']):
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

    def notify(self, message: str):
        print(f"Notification: {message}")

    def optimize_parameters(self, short_range=(5, 20), long_range=(25, 50)):
        best_profit = -np.inf
        best_params = (self.short_window, self.long_window)
        for short in range(*short_range):
            for long in range(*long_range):
                self.short_window = short
                self.long_window = long
                self.calculate_factors()  # 更新因子计算
                profit = self.calculate_profit()
                if profit > best_profit:
                    best_profit = profit
                    best_params = (short, long)
        self.short_window, self.long_window = best_params
        print(f"Optimized parameters: Short window = {self.short_window}, Long window = {self.long_window}, Profit = {best_profit}")
        self.save_parameters()
        
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
        
        # Plot with moving averages
        mpf.plot(stock_data_copy, type='candle', volume=True, 
                title=f'{self.stock_data.code} Candle Figure', ylabel='Price',
                addplot=add_plots, style=s, ylabel_lower='Volume')
