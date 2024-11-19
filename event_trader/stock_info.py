from event_trader.strategies import STRATEGIES
from event_trader import StockData


class StockInfo:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock_data = StockData(symbol)
        self.strategies = {}
        for key, item in STRATEGIES.items():
            self.strategies[key] = item(self.stock_data)
            
    def __getattr__(self, key: str):
        if key in self.strategies:
            return self.strategies[key]
        raise AttributeError(f"'StockInfo' object has no attribute '{key}'")
    
    
    def show(self, **kwargs):
        for key, item in self.strategies.items():
            item.show(**kwargs)

        
        
   