from .trading_strategy import TradingStrategy
import pandas as pd

class SimpleMovingAverageStrategy(TradingStrategy):
    def __init__(self, stock_data: pd.DataFrame, short_window: int, long_window: int):
        super().__init__(stock_data)
        self.short_window = short_window
        self.long_window = long_window

    def calculate_factors(self):
        self.stock_data['short_mavg'] = self.stock_data['close'].rolling(window=self.short_window).mean()
        self.stock_data['long_mavg'] = self.stock_data['close'].rolling(window=self.long_window).mean()

    def buy_signal(self) -> bool:
        return self.stock_data['short_mavg'].iloc[-1] > self.stock_data['long_mavg'].iloc[-1]

    def sell_signal(self) -> bool:
        return self.stock_data['short_mavg'].iloc[-1] < self.stock_data['long_mavg'].iloc[-1]

    def calculate_profit(self) -> float:
        return (self.stock_data['close'].iloc[-1] - self.stock_data['close'].iloc[0]) / self.stock_data['close'].iloc[0]

    def notify(self, message: str):
        print(f"Notification: {message}")

    def optimize_parameters(self):
        best_profit = 0
        best_params = (self.short_window, self.long_window)
        for short in range(5, 20):
            for long in range(25, 50):
                self.short_window = short
                self.long_window = long
                self.calculate_factors()
                profit = self.calculate_profit()
                if profit > best_profit:
                    best_profit = profit
                    best_params = (short, long)
        self.short_window, self.long_window = best_params
        print(f"Optimized parameters: Short window = {self.short_window}, Long window = {self.long_window}, Profit = {best_profit}")
