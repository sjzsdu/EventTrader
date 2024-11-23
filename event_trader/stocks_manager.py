from event_trader.stock_info import StockInfo
from event_trader.stock_market import StockMarket
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

class StocksManager:
    def __init__(self, symbols = None, index = None, limit = None, strategy_kwargs = {}):
        self.stocks: dict[str, StockInfo] = {}
        if symbols is not None:
            self.symbols = symbols
            for symbol in symbols:
                self.stocks[symbol] = StockInfo(symbol)
        if index is not None:
            self.stock_market = StockMarket(symbol=index)
            i = 0
            for symbol in self.stock_market['index_codes']:
                if limit is not None and i > limit:
                    break
                self.stocks[symbol] = StockInfo(symbol, **strategy_kwargs)
                i = i + 1
        
        
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
