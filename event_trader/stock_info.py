from event_trader.strategies import BaseStrategy, STRATEGIES
from china_stock_data import StockData
from event_trader.utils import get_first_line
import pandas as pd

class StockInfo:
    def __init__(self, symbol: str, stock_kwargs = {}, strategies = None):
        self.symbol = symbol
        self.stock_data = StockData(symbol, **stock_kwargs)
        self.strategies: dict[str, BaseStrategy] = {}
        strategies = strategies if strategies is not None else STRATEGIES
        for strategy_class in strategies:
            self.strategies[strategy_class.name] = strategy_class(self.stock_data)
            
    def __getattr__(self, key: str):
        if key in self.strategies:
            return self.strategies[key]
        raise AttributeError(f"'StockInfo' object has no attribute '{key}'")
    
    
    def show(self, **kwargs):
        results = []
        for key, item in self.strategies.items():
            result = item.show(**kwargs)
            results.append({
                "name": key,
                "result": result
            })
        return results
            
    def get_result(self, **opt_kwargs):
        arr = []
        for key, item in self.strategies.items():
            item.optimize_parameters(**opt_kwargs)
            profit = item.calculate_profit()
            factors = item.get_factors()
            
            arr.append({
                "name": key,
                "description": get_first_line(item.__doc__),
                "parameters": item.parameters,
                'status': item.status(),
                'profit': item.account.get_profit(),
                'data': factors,
                'calculated_profit': profit
            })
        return pd.DataFrame(arr)

        
        
   