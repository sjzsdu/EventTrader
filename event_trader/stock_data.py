from datetime import datetime, timedelta
from event_trader.config import HISTORY_DAYS
from event_trader.fetchers import StockHistFetcher, StockInfoFetcher, StockChipFetcher, StockRealtimeFetcher
class StockData:

    def __init__(self, code, type="stock", start_date=None, end_date=None, days=None, period="daily", adjust="qfq"):
        self.code = code
        self.period = period
        self.adjust = adjust
        self.days = days or HISTORY_DAYS
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        if start_date:
            self.start_date = start_date
        else:
            end_date_obj = datetime.strptime(self.end_date, '%Y-%m-%d')
            self.start_date = (end_date_obj - timedelta(days=self.days)).strftime('%Y-%m-%d')
        self.fetches = {
            'stock_hist': StockHistFetcher(self),
            'stock_info': StockInfoFetcher(self),
            'stock_realtime': StockRealtimeFetcher(self),
            'stock_chip': StockChipFetcher(self),
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

