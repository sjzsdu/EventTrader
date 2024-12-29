from event_trader.stock_info import StockInfo
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_stocks import BaseStocks
from .utils import generate_short_md5
class StocksManager(BaseStocks):
    def __init__(self, symbols=None, index=None, start=None, limit=None, **kwargs):
        file_path =  generate_short_md5(f'{str(symbols)}-{str(index)}')
        super().__init__(symbols=symbols, file_path=file_path, index=index, start=start, limit=limit, **kwargs)
        self.stocks: dict[str, StockInfo] = {}
        # 这里不再需要处理 symbols 和 index 的逻辑
    def create_stock_instance(self, symbol, **kwargs):
        return StockInfo(symbol, **kwargs)

    def get_stock_info(self, symbol, **kwargs):
        if symbol in self.symbols:
            return self.create_stock_instance(symbol, **kwargs)
        return None
    
    def show(self, symbols=None, **kwargs):
        for symbol, stock in self.stocks.items():
            if symbols is not None and symbol not in symbols:
                continue
            stock.show(**kwargs)
    
    def get_result(self, opt_kwargs={}):
        dataframes = []

        # 定义一个函数来获取结果并添加符号
        def fetch_result(symbol, item):
            df = item.get_result(opt_kwargs=opt_kwargs)
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
