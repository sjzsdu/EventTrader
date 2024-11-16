from abc import ABC, abstractmethod
import pandas as pd

class TradingStrategy(ABC):
    def __init__(self, stock_data: pd.DataFrame):
        self.stock_data = stock_data

    @abstractmethod
    def calculate_factors(self):
        pass

    @abstractmethod
    def buy_signal(self) -> bool:
        pass

    @abstractmethod
    def sell_signal(self) -> bool:
        pass

    @abstractmethod
    def calculate_profit(self) -> float:
        pass

    @abstractmethod
    def notify(self, message: str):
        pass

    @abstractmethod
    def optimize_parameters(self):
        pass
