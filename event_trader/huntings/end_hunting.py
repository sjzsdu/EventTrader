from china_stock_data import StockMarket, StockData
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from event_trader.utils import is_continuous_growth
import time

class EndHunting:
    def __init__(self, symbols = None, index = None, start = None, limit = None, stock_kwargs = {}):
        self.stocks: dict[str, StockData] = {}
        if symbols is not None:
            self.symbols = symbols
            for symbol in symbols:
                self.stocks[symbol] = StockData(symbol)
        if index:
            self.stock_market = StockMarket(index)
            codes = self.stock_market['index_codes']

            # 当 start 或 limit 为 None 时的处理
            if start is None:
                start = 0
            if limit is None:
                limit = len(codes)

            # 确保 limit 不超过列表的长度
            actual_limit = min(start + limit, len(codes))

            for i in range(start, actual_limit):
                symbol = codes[i]
                if symbol not in self.stocks:
                    self.stocks[symbol] = StockData(symbol, **stock_kwargs)
    
    
    def stock_hunting(self, stock: StockData):
        if stock['量比'] <  1:
            return False
        if stock['换手'] < 5 or stock['换手'] > 10:
            return False
        
        kline_data = stock.kline
        volumn = kline_data['成交量']
        if not is_continuous_growth(volumn, 3):
            return False
        return True
        
    def get_result(self):
        stocks = []

        # 定义一个函数来获取结果并添加符号
        def fetch_result(symbol, item):
            if self.stock_hunting(item):
                return item

        # 使用ThreadPoolExecutor来管理线程池
        with ThreadPoolExecutor(max_workers=8) as executor:
            # 提交所有任务并收集future对象
            futures = {}
            for symbol, item in self.stocks.items():
                # 在每次提交任务之前进行延迟
                time.sleep(0.1)  # 延迟100毫秒，可以根据需要调整
                futures[executor.submit(fetch_result, symbol, item)] = symbol

            # 处理完成的任务
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    item = future.result()
                    if (item is not None):
                        stocks.append(item)
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                # 在每个任务执行完成后进行延迟
                time.sleep(0.1)  # 延迟100毫秒，可以根据需要调整

        return stocks
    
    def show_result(self): 
        stocks = self.get_result()
        for stock in stocks:
            print(stock.symbol)