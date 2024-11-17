import os
import pandas as pd
from abc import ABC, abstractmethod
from event_trader.demo_account import DemoAccount
from event_trader.config import DATE_COL, SYMBOL_COL
import numpy as np
import mplfinance as mpf

class BaseStrategy(ABC):
    def __init__(self, stock_data, sub_path, params, params_range, params_step):
        self.stock_data = stock_data
        self.data = self.load_data()
        self.params_path = os.path.join('params', sub_path, f'{self.stock_data.code}.csv')
        self.params = params
        self.params_range = params_range
        self.params_step = params_step
        
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
        account = DemoAccount(initial_cash=1000000)  # 初始化DemoAccount实例
        for index, row in self.data.iterrows():
            if self.buy_signal(row):
                account.buy(row, index, position=1.0)  # 假设默认全仓买入
            elif self.sell_signal(row):
                account.sell(row, index, position=1.0)  # 假设默认全仓卖出

        # 检查是否还有未卖出的股票
        for symbol, shares in account.holdings.items():
            if shares > 0:
                # 在最后一个数据行处卖出所有持有的股票
                last_index = len(self.data) - 1
                last_row = self.data.iloc[last_index]
                if last_row.get(SYMBOL_COL) == symbol:  # 确保符号匹配
                    account.sell(last_row, last_index, position=1.0)

        return account
    
    def optimize_parameters(self, params_range=None, params_step=None, forceOptimize=False):
        if (self.check_params_exists() and not forceOptimize):
            self.account = self.calculate_profit()
            return self
        
        if params_range is not None:
            self.params_range = {**self.params_range, **params_range}
        if params_step is not None:
            self.params_step = {**self.params_step, **params_step}
        else:
            self.params_step = {param: 1 for param in self.params_range}  # 默认步长为 1
        
        best_profit = -np.inf
        best_parameters = self.parameters.copy()
        
        import itertools
        param_names = list(self.params_range.keys())
        param_ranges = [
            np.arange(self.params_range[param][0], 
                    self.params_range[param][1], 
                    self.params_step.get(param, 1))  # 使用 np.arange 来支持浮点数
            for param in param_names
        ]
        
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

    
    def plot_basic(self, add_plots=None, title=None, volume_width=0.5, **kwargs):
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
        return self.after_plot(fig, axes, **kwargs)
    
    def after_plot(self, fig, axes, **kwargs):
        trades = self.account.transactions
        ax = axes[0]
        volume_ax = axes[1]  # Reference to the volume axis
        ylim = ax.get_ylim()
        # Plot each trade with improved layout
        if 'transaction' in kwargs and kwargs['transaction']:
            for trade in trades:
                date = trade['index']
                price_offset = trade['price'] * 0.1
                if trade['type'] == 'buy':
                    ax.annotate(
                        f"B",
                        xy=(date, trade['price']),
                        xytext=(date, trade['price'] + price_offset),
                        arrowprops=dict(edgecolor='green', arrowstyle='->', lw=1),
                        fontsize=12,
                        color='green',
                        horizontalalignment='left',
                        verticalalignment='bottom',
                        zorder=5  # Ensure text is above other elements
                    )
                elif trade['type'] == 'sell':
                    ax.annotate(
                        f"S",
                        xy=(date, trade['price']),
                        xytext=(date, trade['price'] - price_offset),
                        arrowprops=dict(edgecolor='red', arrowstyle='->', lw=1),
                        fontsize=12,
                        color='red',
                        horizontalalignment='right',
                        verticalalignment='top',
                        zorder=5  # Ensure text is above other elements
                    )

        # Draw lines between buy and sell points
        if 'profit' in kwargs and kwargs['profit']:
            for i in range(0, len(trades) - 1, 2):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                price_offset = (buy_trade['price'] + buy_trade['price'])  * 0.1
                profit = (sell_trade['price'] - buy_trade['price']) * buy_trade['shares'] - (buy_trade['fee'] + sell_trade['fee'])
                
                # Plot dashed line between buy and sell
                ax.plot(
                    [buy_trade['index'], sell_trade['index']],
                    [buy_trade['price'], sell_trade['price']],
                    color='blue', linestyle='--', linewidth=1, zorder=3
                )
                
                # Annotate profit in the middle of the line
                ax.text(
                    (buy_trade['index'] + (sell_trade['index'] - buy_trade['index']) / 2),
                    max(buy_trade['price'], sell_trade['price']) + price_offset,
                    f"Profit: {profit:.2f}",
                    fontsize=8,
                    color='blue',
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    zorder=5
                )
        
        # Set limits to ensure annotations stay above the volume chart
        # ax.set_ylim(ylim[0], ylim[1] + (ylim[1] - ylim[0]) * 0.1)
        
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
