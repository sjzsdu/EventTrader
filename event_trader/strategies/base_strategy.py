import os
import pandas as pd
from abc import ABC, abstractmethod
from event_trader.demo_account import DemoAccount
import numpy as np

class BaseStrategy(ABC):
    def __init__(self, stock_data, sub_path, params, params_range):
        self.stock_data = stock_data
        self.data = self.load_data()
        self.params_path = os.path.join('params', sub_path, f'{self.stock_data.code}.csv')
        self.params = params
        self.params_range = params_range
        
        self.parameters = {}
        self.load_parameters(self.params)

    @abstractmethod
    def load_data(self):
        """
        Load stock data into a DataFrame.
        This method should be implemented to load the data as needed.
        """
        pass

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

    def calculate_profit(self) -> float:
        account = DemoAccount()
        for _, row in self.data.iterrows():
            if self.buy_signal(row):
                account.buy(row)
            elif self.sell_signal(row):
                account.sell(row)

        if account.shares > 0:
            account.sell(self.data.iloc[-1])

        return account.get_profit()
    
    def optimize_parameters(self, params_ange=None):
        if params_ange is not None:
            self.params_range = {**self.params_range, **params_ange}
        
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
            profit = self.calculate_profit()
            
            # 更新最佳参数
            if profit > best_profit:
                best_profit = profit
                best_parameters = self.parameters.copy()
        
        # 更新为最佳参数
        self.parameters = best_parameters
        print(f"Optimized parameters: {self.parameters}, Profit = {best_profit}")
        self.save_parameters()
        return self


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
