import os
import pandas as pd
from abc import ABC, abstractmethod
from event_trader.demo_account import DemoAccount
from event_trader.config import DATE_COL, SYMBOL_COL, CURRENT_DAYS, HISTORY_DAYS
from event_trader.utils import friendly_number
import numpy as np
import mplfinance as mpf

class BaseStrategy(ABC):
    def __init__(self, stock_data, sub_path, params, params_range, params_step, factors = []):
        self.stock_data = stock_data
        self.data = self.load_data()
        self.params_path = os.path.join('params', sub_path, f'{self.stock_data.symbol}.csv')
        self.params = params
        self.params_range = params_range
        self.params_step = params_step
        self.account = None
        self.parameters = {}
        self.factors = factors
        self.load_parameters(self.params)
        self.calculate_factors()
        self.account = self.calculate_profit()
    
    def load_data(self):
        return self.stock_data.kline

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
        try:
            account = DemoAccount(initial_cash=1000000)
            for index, row in self.data.iterrows():
                if self.buy_signal(row, index):
                    account.buy(row, index)
                elif self.sell_signal(row, index):
                    account.sell(row, index)
            return account
        except Exception as e:
            raise StrategyError(f"计算利润时发生错误: {str(e)}")
    
    def validate_parameter(self, parameters):
        """增强参数验证"""
        # 检查参数是否在有效范围内
        for param, value in parameters.items():
            if param in self.params_range:
                min_val, max_val = self.params_range[param]
                if not min_val <= value <= max_val:
                    return False
        return True
        
    def optimize_parameters(self, method='grid', **kwargs):
        """支持多种优化方法"""
        if method == 'grid':
            return self._grid_search(**kwargs)
        elif method == 'random':
            return self._random_search(**kwargs)
        elif method == 'bayesian':
            return self._bayesian_optimization(**kwargs)
    
    def get_plots(self, data):
        """增加更多可视化选项"""
        plots = []
        for factor in self.factors:
            if factor in data.columns:
                plots.append(
                    mpf.make_addplot(
                        data[factor],
                        width=0.8,
                        panel=self.get_plot_panel(factor),
                        color=self.get_plot_color(factor),
                        label=f'{factor}'
                    )
                )
        return plots
    
    
    def show(self, days = CURRENT_DAYS, **kwargs):
        if self.account is None:
            self.optimize_parameters()
        self.calculate_factors()
        stock_data_copy = self.data.copy().tail(days)
        add_plots = self.get_plots(stock_data_copy)
        self.plot_basic(days = days, add_plots = add_plots, **kwargs)

    
    def plot_basic(self, days = CURRENT_DAYS, add_plots=None, title=None, volume_width=0.5, **kwargs):
        if title is None:
            title = f"{self.stock_data.symbol} {self.__class__.__name__} Figure, profit = {friendly_number(self.account.get_profit())}"
        if add_plots is None:
            add_plots = []
        stock_data_copy = self.data.copy().tail(days)
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
        return self.after_plot(fig, axes, days = days,  **kwargs)
    
    def after_plot(self, fig, axes, days= CURRENT_DAYS, **kwargs):
        trades = self.account.transactions
        ax = axes[0]
        # Plot each trade with improved layout
        if 'transaction' not in kwargs or not kwargs['transaction']:
            for trade in trades:
                date = trade['index'] - (HISTORY_DAYS - days)
                if date < 0:
                    continue
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
        if 'profit' not in kwargs or not kwargs['profit']:
            for i in range(0, len(trades) - 1, 2):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                bi = buy_trade['index'] - (HISTORY_DAYS - days)
                si = sell_trade['index'] - (HISTORY_DAYS - days)
                if bi < 0 and si < 0:
                    continue
                price_offset = (buy_trade['price'] + buy_trade['price'])  * 0.1
                profit = (sell_trade['price'] - buy_trade['price']) * buy_trade['shares'] - (buy_trade['fee'] + sell_trade['fee'])
                
                # Plot dashed line between buy and sell
                ax.plot(
                    [bi, si],
                    [buy_trade['price'], sell_trade['price']],
                    color='blue', linestyle='--', linewidth=1, zorder=3
                )
                
                # Annotate profit in the middle of the line
                ax.text(
                    (bi + (si - bi) / 2),
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

    def status(self):
        if self.should_buy(self.data.iloc[-1]):
            return "Buy"
        if self.should_sell(self.data.iloc[-1]):
            return "Sell"
        return 'None'


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
    def buy_signal(self, row, i) -> bool:
        """Define the buy signal logic."""
        pass

    @abstractmethod
    def sell_signal(self, row, i) -> bool:
        """Define the sell signal logic."""
        pass
    
    def get_factors(self):
        row = self.data.iloc[-1]
        dic = {}
        for factor in self.factors:
            dic[factor] = friendly_number(row[factor])
        return dic

    def should_buy(self, row) -> bool:
        return False

    def should_sell(self, row) -> bool:
        return False
    
    @abstractmethod
    def calculate_factors(self):
        """Calculate the factors."""
        pass

    def show_factors(self) -> bool:
        pass

    def check_signal(self, row, i, condition_func):
        """通用的信号检查逻辑"""
        if i == 0 or any(pd.isna(row[factor]) for factor in self.factors):
            return False
        return condition_func(row, self.data.iloc[i-1])

    def calculate_metrics(self):
        """计算策略性能指标"""
        metrics = {
            'total_return': self.account.get_profit(),
            'win_rate': self.calculate_win_rate(),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'max_drawdown': self.calculate_max_drawdown()
        }
        return metrics

class StrategyError(Exception):
    """策略相关错误"""
    pass

class CompositeStrategy(BaseStrategy):
    """组合多个策略"""
    def __init__(self, strategies, combination_rule='AND'):
        self.strategies = strategies
        self.combination_rule = combination_rule
        
    def buy_signal(self, row, i):
        signals = [strategy.buy_signal(row, i) for strategy in self.strategies]
        return all(signals) if self.combination_rule == 'AND' else any(signals)