from event_trader.stock_info import StockInfo
from china_stock_data import StockMarket
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

class StocksManager:
    def __init__(self, symbols = None, index = None, start = None, limit = None, stock_kwargs = {}):
        self.stocks: dict[str, StockInfo] = {}
        if symbols is not None:
            self.symbols = symbols
            for symbol in symbols:
                self.stocks[symbol] = StockInfo(symbol)
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
                    self.stocks[symbol] = StockInfo(symbol, **stock_kwargs)
        
        
    def get_stock_info(self, symbol):
        if symbol in self.stocks:
            return self.stocks[symbol]  
        return None
    
    def show(self, **kwargs):
        for symbol, stock in self.stocks.items():
            stock.show(**kwargs)
    
    def get_result(self):
        dataframes = []

        # 定义一个函数来获取结果并添加符号
        def fetch_result(symbol, item):
            df = item.get_result()
            df['symbol'] = symbol
            return df

        # 使用ThreadPoolExecutor来管理线程池
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 提交所有任务并收集future对象
            futures = {executor.submit(fetch_result, symbol, item): symbol for symbol, item in self.stocks.items()}

            # 处理完成的任务
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    df = future.result()
                    dataframes.append(df)
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")

        if dataframes:
            result_df = pd.concat(dataframes, ignore_index=True)
            return result_df
        else:
            print("No data to combine.")
            return pd.DataFrame()
