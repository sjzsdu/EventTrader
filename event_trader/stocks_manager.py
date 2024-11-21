from event_trader.stock_info import StockInfo

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
