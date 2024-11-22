from event_trader.stock_info import StockInfo
import pandas as pd
class StocksManager:
    def __init__(self, symbols):
        self.symbols = symbols
        self.stocks = {}
        for symbol in symbols:
            self.stocks[symbol] = StockInfo(symbol)
        
        
    def get_stock_info(self, symbol):
        if symbol in self.stocks:
            return self.stocks[symbol]  
        return None
    
    def get_result(self):
        dataframes = []

        for symbol, item in self.stocks.items():
            df = item.get_result()
            df['symbol'] = symbol
            dataframes.append(df)

        if dataframes:
            result_df = pd.concat(dataframes, ignore_index=True)
            return result_df
        else:
            print("No data to combine.")
            return pd.DataFrame()
