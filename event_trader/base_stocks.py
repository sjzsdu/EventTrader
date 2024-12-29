from abc import ABC, abstractmethod
from china_stock_data import StockMarket, PersistentDict
from .utils import is_a_share
import json
import os
from datetime import datetime

class BaseStocks(ABC):
    def __init__(self, symbols=None, file_path = 'base_stocks.json', index=None, start=None, limit=None, **kwargs):
        self.kwargs = kwargs
        self.cached = PersistentDict(file_path)
        self.symbols = []
        if symbols is not None:
            self.symbols = symbols
        elif index:
            self.stock_market = StockMarket(index)
            codes = self.stock_market['index_codes']
            
            if start is None:
                start = 0
            if limit is None:
                limit = len(codes)

            actual_limit = min(start + limit, len(codes))

            for i in range(start, actual_limit):
                symbol = codes[i]
                if is_a_share(symbol):
                    self.symbols.append(symbol)

    
    @abstractmethod
    def create_stock_instance(self, symbol, **kwargs):
        """创建股票实例，子类需要实现这个方法"""
        pass

