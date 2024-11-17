import os
import pandas as pd
from abc import ABC, abstractmethod
from event_trader.demo_account import DemoAccount
from event_trader.config import DATE_COL
import numpy as np
import mplfinance as mpf

class BaseStrategy(ABC):
    def __init__(self, stock_data, sub_path, params, params_range):
        self.stock_data = stock_data
        self.data = self.load_data()
        self.params_path = os.path.join('params', sub_path, f'{self.stock_data.code}.csv')
        self.params = params
        self.params_range = params_range
        
        self.parameters = {}
        self.load_parameters(self.params)
        self.calculate_factors()

    @abstractmethod
    def load_data(self):
        """
        Load stock data into a DataFrame.
        This method should be implemented to load the data as needed.
        """
        pass

    def check_params_exists(self):
        """检查self.params_path文件是否存在"""
        return os.path.exists(self.params_path)
    
    def load_parameters(self, default_params):
        """
        Load parameters from a CSV file. If the file does not exist, use the default parameters provided.

        :param default_params: A dictionary where keys are parameter names and values are their default values.
        """
        if os.path.isfile(self.params_path):
            df = pd.read_csv(self.params_path)
            for name in default_params.keys():
                self.parameters[name] = df[name].iloc[0]
        else:
            self.parameters.update(default_params)

    def save_parameters(self):
        os.makedirs(os.path.dirname(self.params_path), exist_ok=True)
        df = pd.DataFrame({name: [value] for name, value in self.parameters.items()})
        df.to_csv(self.params_path, index=False)

    def calculate_profit(self) -> DemoAccount:
        account = DemoAccount()
        for index, row in self.data.iterrows():
            if self.buy_signal(row):
                account.buy(row, index)
            elif self.sell_signal(row):
                account.sell(row, index)

        if account.shares > 0:
            account.sell(self.data.iloc[-1], len(self.data) - 1)

        return account
    
    def optimize_parameters(self, params_range=None, forceOptimize=False):
        if (self.check_params_exists() and not forceOptimize):
            self.account = self.calculate_profit()
            return self
        if params_range is not None:
            self.params_range = {**self.params_range, **params_range}
        
        best_profit = -np.inf
        best_parameters = self.parameters.copy()
        
        import itertools
        param_names = list(self.params_range.keys())
        param_ranges = [range(*self.params_range[param]) for param in param_names]
        
        for param_combination in itertools.product(*param_ranges):
            # 更新参数
            for i, param_name in enumerate(param_names):
                self.parameters[param_name] = param_combination[i]
            
            # 计算因子和利润
            self.calculate_factors()
            account = self.calculate_profit()
            profit = account.get_profit()
            
            # 更新最佳参数
            if profit > best_profit:
                best_profit = profit
                best_parameters = self.parameters.copy()
                self.account = account
        
        # 更新为最佳参数
        self.parameters = best_parameters
        print(f"Optimized parameters: {self.parameters}, Profit = {best_profit}")
        self.save_parameters()
        return self
    
    def plot_basic(self, add_plots=None, title=None, volume_width=0.5):
        if title is None:
            title = f"{self.stock_data.code} {self.__class__.__name__} Figure"
        if add_plots is None:
            add_plots = []
        stock_data_copy = self.data.copy()
        stock_data_copy.rename(columns={
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume'
        }, inplace=True)
        
        # Convert index to datetime
        stock_data_copy.index = pd.to_datetime(stock_data_copy[DATE_COL])
        
        # Define the style with red for up and green for down
        mc = mpf.make_marketcolors(up='red', down='green', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, base_mpf_style='yahoo')
        figsize = (16, 8)

        # Plot with mplfinance, return the figure and axes
        fig, axes = mpf.plot(stock_data_copy, type='candle', volume=True, 
                            title=title, ylabel='Price', style=s, ylabel_lower='Volume', 
                            figsize=figsize, addplot=add_plots, returnfig=True, datetime_format='%Y-%m-%d')
        
        # Customizing the volume bars width and color
        volume_ax = axes[2]  # Volume is usually plotted on the third axis
        for idx, bar in enumerate(volume_ax.patches):
            bar.set_width(volume_width)  # Set custom width for each volume bar
            # Match the color of volume bars with the candle colors
            if stock_data_copy['Close'].iloc[idx] > stock_data_copy['Open'].iloc[idx]:
                bar.set_color('red')  # Up color
            else:
                bar.set_color('green')  # Down color
        print(f"Optimized parameters: {self.parameters}, Profit = {self.account.get_profit()}")
        return self.after_plot(fig, axes)
    
    def after_plot(self, fig, axes):
        trades = self.account.transactions
        ax = axes[0]
        
        # Plot each trade with improved layout
        for trade in trades:
            date = trade['index']
            offset = 2  # Adjust the offset for better positioning
            text_offset = 3  # Extra offset for the text
            
            if trade['type'] == 'buy':
                ax.annotate(
                    f"Buy\nPrice: {trade['price']}\nShares: {trade['shares']}\nFee: {trade['fee']}",
                    xy=(date, trade['price']),
                    xytext=(date, trade['price'] + offset),
                    arrowprops=dict(facecolor='green', arrowstyle='->', lw=1),
                    fontsize=8,
                    color='green',
                    horizontalalignment='left',
                    verticalalignment='bottom'
                )
            elif trade['type'] == 'sell':
                ax.annotate(
                    f"Sell\nPrice: {trade['price']}\nShares: {trade['shares']}\nFee: {trade['fee']}",
                    xy=(date, trade['price']),
                    xytext=(date, trade['price'] - offset - text_offset),
                    arrowprops=dict(facecolor='red', arrowstyle='->', lw=1),
                    fontsize=8,
                    color='red',
                    horizontalalignment='right',
                    verticalalignment='top'
                )

        # Draw lines between buy and sell points
        for i in range(0, len(trades) - 1, 2):
            buy_trade = trades[i]
            sell_trade = trades[i + 1]
            profit = (sell_trade['price'] - buy_trade['price']) * buy_trade['shares'] - (buy_trade['fee'] + sell_trade['fee'])
            
            # Plot dashed line between buy and sell
            ax.plot(
                [buy_trade['index'], sell_trade['index']],
                [buy_trade['price'], sell_trade['price']],
                color='blue', linestyle='--', linewidth=1
            )
            
            # Annotate profit in the middle of the line
            ax.text(
                (buy_trade['index'] + (sell_trade['index'] - buy_trade['index']) / 2),
                (buy_trade['price'] + sell_trade['price']) / 2 + text_offset,
                f"Profit: {profit:.2f}",
                fontsize=8,
                color='blue',
                horizontalalignment='center',
                verticalalignment='center'
            )
        
        return fig, axes



    def notify(self, message: str):
        print(f"Notification: {message}")

    def __getitem__(self, key: str):
        if key in self.parameters:
            return self.parameters[key]
        else:
            raise KeyError(f"Key '{key}' not found in {self.__class__.__name__}")

    def __getattr__(self, key: str):
        if key in self.parameters:
            return self.parameters[key]
        else:
            raise KeyError(f"Key '{key}' not found in {self.__class__.__name__}")

    @abstractmethod
    def buy_signal(self, row) -> bool:
        """Define the buy signal logic."""
        pass

    @abstractmethod
    def sell_signal(self, row) -> bool:
        """Define the sell signal logic."""
        pass
    
    @abstractmethod
    def calculate_factors(self):
        """Calculate the factors."""
        pass
