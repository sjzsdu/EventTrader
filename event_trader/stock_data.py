from datetime import datetime, timedelta
from event_trader.config import HISTORY_DAYS
from event_trader.fetchers import StockHistFetcher, StockInfoFetcher, StockChipFetcher, StockRealtimeFetcher
class StockData:
    # Class variable to cache trade dates
    trade_dates_cache = None

    def __init__(self, code, start_date=None, end_date=None, period="daily", adjust="qfq"):
        self.code = code
        self.period = period
        self.adjust = adjust
        self.start_date = start_date or (datetime.now() - timedelta(days=HISTORY_DAYS)).strftime('%Y-%m-%d')
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.fetches = {
            'stock_hist': StockHistFetcher(self),
            'stock_info': StockInfoFetcher(self),
            'stock_realtime': StockRealtimeFetcher(self),
            'stock_chip': StockChipFetcher(self)
        }
        
    def get_data(self, data_type: str):
        if data_type not in self.fetches:
            raise ValueError(f"Unknown data type: {data_type}")
        return self.fetches[data_type].fetch_and_cache_data()
    
    def __getattr__(self, name: str):
        if (name == 'hist'):
            return self.get_data('stock_hist')
        elif (name == 'chip'):
            return self.get_data('stock_chip')
        return f'{name} is not found'
    
    
    def __getitem__(self, key: str):
        fetchers = [self.fetches['stock_hist'], self.fetches['stock_info'], self.fetches['stock_realtime']]
        for fetcher in fetchers:
            try:
                return fetcher[key.strip()]
            except KeyError:
                continue 
        raise KeyError(f"Key '{key}' not found in any fetcher")

