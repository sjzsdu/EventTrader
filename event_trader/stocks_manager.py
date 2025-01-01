from event_trader.stock_info import StockInfo
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_stocks import BaseStocks
from .utils import generate_short_md5

def execute_in_threads(iterable, func, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(func, item): item for item in iterable}
        for future in as_completed(futures):
            item = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error processing {item}: {e}")
    return results

class StocksManager(BaseStocks):
    def __init__(self, symbols=None, index=None, start=None, limit=None, **kwargs):
        file_path = generate_short_md5(f'{str(symbols)}-{str(index)}') + '.json'
        super().__init__(symbols=symbols, file_path=file_path, index=index, start=start, limit=limit, **kwargs)
        self.stocks = {}

    def get_stock_info(self, symbol, **kwargs):
        if symbol not in self.symbols:
            self.symbols.append(symbol)
        if symbol in self.stocks:
            return self.stocks[symbol]
            
        self.stocks[symbol] = StockInfo(symbol, **kwargs)
        return  self.stocks[symbol]
    
    def show(self, **kwargs):
        def _show(symbol):
            stock = self.get_stock_info(symbol)
            stock.show(**kwargs)
        execute_in_threads(self.symbols, _show, max_workers=5)

    def merge_dataframes(self, dataframes):
        """合并多个 DataFrame"""
        if dataframes:
            return pd.concat(dataframes, ignore_index=True)
        else:
            print("No data to merge.")
            return pd.DataFrame()

    def get_result(self, **kwargs):
        dataframes = []
        def _get_result(symbol):
            stock = StockInfo(symbol)
            df = stock.get_result(**kwargs)
            df['symbol'] = symbol
            return df

        results = execute_in_threads(self.symbols, _get_result, max_workers=5)
        # 处理结果
        for df in results:
            if df is not None:
                dataframes.append(df)

        # 使用公共方法合并 DataFrame
        result_df = self.merge_dataframes(dataframes)
        return result_df
    
    def optimize(self):
        def _optimize(symbol):
            stock = self.get_stock_info(symbol)
            stock.optmize()
        execute_in_threads(self.symbols, _optimize, max_workers=5)